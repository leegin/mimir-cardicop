import subprocess
import requests
import json
import logging
from exporter.config import MIMIR_CARDINALITY_URL, MIMIR_RULER_URL, BASE_MIMIR_QUERY_URL
from bs4 import BeautifulSoup
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

def get_tenants(store_gateway_url):
    """Fetch all tenants listed in Mimir's store-gateway UI."""
    try:
        response = requests.get(store_gateway_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        tenants = [a.text for a in soup.select("tbody tr td a") if not (a.text.endswith("-dr") or "fake" in a.text.lower())]
        logger.info(f"Fetched {len(tenants)} tenants")
        return tenants
    except (requests.RequestException, Exception) as e:
        logger.info(f"Error fetching tenants: {e}")
        return []

def get_metrics_for_tenant(tenant_id):
    """Query Mimir cardinality API for all metrics of a tenant."""
    logger.info(f"Fetching metrics from Mimir for tenant: {tenant_id}")
    response = requests.get(
        f"{MIMIR_CARDINALITY_URL}?label_names[]=__name__&limit=100",
        headers={"X-Scope-OrgID": tenant_id, "Content-Type": "application/json"}
    )
    if response.ok:
        data = response.json()
        if not data.get('labels'):
            logger.info(f"[{tenant_id}] No metrics found.")
            return [] 
        cardinality=data.get('labels')[0]
        cardinality_list=cardinality.get('cardinality')
        metric_names = [item['label_value'] for item in cardinality_list]
        logger.info(f"Fetched {len(metric_names)} metrics for tenant: {tenant_id}")
        return metric_names
    logger.warning(f"Failed to fetch metrics for tenant {tenant_id}")
    return []

def run_analysis_for_tenant(tenant_id):
    """Run mimirtool analyses (ruler and prometheus) for a given tenant."""
    logger.info(f"Running mimirtool analysis for tenant {tenant_id}")
    subprocess.run(["mimirtool", "analyze", "ruler", f"--address={MIMIR_RULER_URL}", f"--id={tenant_id}"], capture_output=True, text=True)
    subprocess.run(["mimirtool", "analyze", "prometheus", f"--address={BASE_MIMIR_QUERY_URL}", f"--id={tenant_id}", "--prometheus-http-prefix=prometheus", "--grafana-metrics-file=combined_grafana.json"], capture_output=True, text=True)

def get_used_metrics(filepath='prometheus-metrics.json'):
    """Parse list of in-use metrics from mimirtool prometheus analysis output."""
    try:
        with open(filepath) as f:
            data_file = json.load(f)
            metrics_list = data_file.get("in_use_metric_counts", [])
            if not isinstance(metrics_list, list):
                logger.info("Warning: 'in_use_metric_counts' is not a list or is missing. Skipping...")
                return set()
            metrics = {m["metric"] for m in data_file.get("in_use_metric_counts", [])}
            logger.info(f"Found {len(metrics)} used metrics from analysis")
            return metrics
    except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
        logger.warning(f"Error reading used metrics file: {e}")
        return set()
