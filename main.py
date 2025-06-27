import time
import logging
import subprocess
from prometheus_client import start_http_server
import sys

from exporter.config import EXPORTER_PORT, EXPORT_INTERVAL_SECONDS, STORE_GATEWAY_URL
from exporter import grafana, mimir, loki, collector
from exporter.collector import metric_usage_status

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

def update_metrics():
    """Update Prometheus metrics based on usage checks."""
    logger.info("Fetching Grafana orgs and Mimir tenants...")
    orgs = grafana.get_all_orgs()
    tenants = mimir.get_tenants(STORE_GATEWAY_URL)

    for org in orgs:
        logger.info(f"Analyzing Grafana org: {org['name']} (ID: {org['id']})")
        if grafana.switch_org(org["id"]):
            acc_id = grafana.get_or_create_service_account()
            if acc_id:
                token, token_id = grafana.generate_service_account_token(acc_id)
                if token:
                    grafana.run_grafana_analysis_for_org(org["name"], token)
                    grafana.delete_token(acc_id, token_id)

    collector.combine_metrics_files()

    for tenant in tenants:
        logger.info(f"Analyzing tenant: {tenant}")
        mimir.run_analysis_for_tenant(tenant)
        used_metrics = mimir.get_used_metrics()
        metrics = mimir.get_metrics_for_tenant(tenant)
        for metric in metrics:
            usage = 1 if metric in used_metrics or loki.check_metric_queried(metric) else 0
            metric_usage_status.labels(tenant_id=tenant, metric_name=metric).set(usage)
            logger.debug(f"Metric {metric} for tenant {tenant} marked as {'used' if usage else 'unused'}")

if __name__ == '__main__':
    logger.info(f"Starting Prometheus exporter on port {EXPORTER_PORT}")
    start_http_server(EXPORTER_PORT)
    while True:
        logger.info("Running metric update cycle...")
        update_metrics()
        logger.info(f"Sleeping for {EXPORT_INTERVAL_SECONDS}s before next run...")
        time.sleep(EXPORT_INTERVAL_SECONDS)
