import requests
import datetime
import logging
from exporter.config import MIMIR_QUERY_URL, LOKI_QUERY_LOOKBACK_DAYS, LOKI_QUERY_METRIC_NAME, MIMIR_TENANT_ID
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

def get_unix_timestamp(days_ago):
    """Returns a Unix timestamp for X days ago."""
    return int((datetime.datetime.utcnow() - datetime.timedelta(days=days_ago)).timestamp())

def check_metric_queried(metric):
    """Check whether a metric was queried recently based on Loki logs."""
    params = {
        "query": f'{LOKI_QUERY_METRIC_NAME}{{param_query=~".*{metric}.*"}}',
        "start": get_unix_timestamp(LOKI_QUERY_LOOKBACK_DAYS),
        "end": get_unix_timestamp(0),
        "step": "1d"
    }
    try:
        response = requests.get(MIMIR_QUERY_URL, params=params, headers={"X-Scope-OrgID": MIMIR_TENANT_ID})
        if response.ok:
            queried = len(response.json().get("data", {}).get("result", [])) > 0
            logger.info(f"Metric {metric} queried in logs: {queried}")
            return queried
    except (requests.RequestException, Exception) as e:
        logger.info(f"Error checking Mimir for metric {metric}: {e}")
        return False