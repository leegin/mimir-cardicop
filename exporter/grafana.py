import requests
import logging
import time
import subprocess
from exporter.config import GRAFANA_URL, GRAFANA_ADMIN_USER, GRAFANA_ADMIN_PASSWORD, SERVICE_ACCOUNT_NAME, TOKEN_EXPIRY_HOURS, SSL_VERIFY
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

def get_all_orgs():
    """Fetch all organizations using the Grafana admin API."""
    response = requests.get(f"{GRAFANA_URL}/api/orgs", auth=(GRAFANA_ADMIN_USER, GRAFANA_ADMIN_PASSWORD),verify=SSL_VERIFY)
    if response.status_code != 200:
        logger.info(f"Failed to get Grafana orgs: {response.text}")
    return response.json() if response.status_code == 200 else []

def switch_org(org_id):
    """Switch active organization to the given org_id."""
    response = requests.post(f"{GRAFANA_URL}/api/user/using/{org_id}", auth=(GRAFANA_ADMIN_USER, GRAFANA_ADMIN_PASSWORD),verify=SSL_VERIFY)
    if response.status_code == 200:
        logger.info(f"Switched to Org ID {org_id}")
        return True
    else:
        logger.info(f"Failed to switch to Org ID {org_id}: {response.text}")
        return False

def get_or_create_service_account():
    """Fetch the service account for the current org if it exists."""
    response = requests.get(f"{GRAFANA_URL}/api/serviceaccounts/search", auth=(GRAFANA_ADMIN_USER, GRAFANA_ADMIN_PASSWORD),verify=SSL_VERIFY)
    if response.status_code == 200:
        for account in response.json().get('serviceAccounts', []):
            if account["name"] == SERVICE_ACCOUNT_NAME:
                logger.info(f"Service account '{SERVICE_ACCOUNT_NAME}' exists in this org.")
                return account["id"]
    else:
        logger.info(f"Error fetching service accounts: {response.text}")

    payload = {"name": SERVICE_ACCOUNT_NAME, "role": "Admin"}
    response = requests.post(f"{GRAFANA_URL}/api/serviceaccounts", json=payload, auth=(GRAFANA_ADMIN_USER, GRAFANA_ADMIN_PASSWORD),verify=SSL_VERIFY)
    if response.status_code == 200:
        logger.info(f"Created service account: {account_info}")
        return response.json()["id"]
    else:
        logger.info(f"Failed to create service account: {response.text}")
    return None

def generate_service_account_token(account_id):
    """Generate a temporary token for the current organization's service account."""
    payload = {
        "name": f"mimirtool-token-{int(time.time())}",
        "role": "Admin",
        "ttl": TOKEN_EXPIRY_HOURS * 3600
    }
    response = requests.post(f"{GRAFANA_URL}/api/serviceaccounts/{account_id}/tokens", json=payload, auth=(GRAFANA_ADMIN_USER, GRAFANA_ADMIN_PASSWORD), verify=SSL_VERIFY)
    if response.status_code == 200:
        token_info = response.json()
        return token_info["key"], token_info["id"] 
    else:
        logger.info(f"Failed to generate service account token: {response.text}")
        return None, None

def delete_token(account_id, token_id):
    """Delete a service account token after use."""
    response = requests.delete(f"{GRAFANA_URL}/api/serviceaccounts/{account_id}/tokens/{token_id}",auth=(GRAFANA_ADMIN_USER, GRAFANA_ADMIN_PASSWORD), verify=SSL_VERIFY)
    if response.status_code == 200:
        logger.info(f"Deleted service account token ID {token_id}")
    else:
        logger.info(f"Failed to delete token ID {token_id}: {response.text}")

def run_grafana_analysis_for_org(org_name, api_token):
    """Run mimirtool analysis for Grafana metrics in a specific org."""

    logger.info(f"Running Grafana analysis for org: {org_name}")
    result = subprocess.run(
        ["mimirtool", "analyze", "grafana", "--address", GRAFANA_URL, f"--key={api_token}", f"--output=metrics-in-{org_name}-grafana.json"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        logger.info(f"Successfully analyzed org {org_name}")
    else:
        logger.warning(f"Failed to analyze org {org_name}: {result.stderr}")