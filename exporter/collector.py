import glob
import json
import logging
import os
from prometheus_client import Gauge
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

# Prometheus gauge for metric usage status
metric_usage_status = Gauge('metric_usage_status', 'Metric usage status (1=used, 0=unused)', ['tenant_id', 'metric_name'])

def combine_metrics_files(output_file='combined_grafana.json', directory='./'):
    """Merge all *_grafana.json files into a single combined file."""
    all_metrics = set()
    for file_path in glob.glob(os.path.join(directory, "**grafana.json"), recursive=True):
        try:
            with open(file_path) as f:
                data = json.load(f)
                if "metricsUsed" in data and isinstance(data.get("metricsUsed"), list):
                    all_metrics.update(data["metricsUsed"])
        except Exception as e:
            logger.warning(f"Could not process {file_path}: {e}")
    with open(output_file, "w") as out:
        json.dump({"metricsUsed": sorted(all_metrics)}, out, indent=4)
        logger.info(f"Combined {len(all_metrics)} unique metrics into {output_file}")