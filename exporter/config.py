import os

def required_env(name):
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

# Required Grafana config(must be passed via Helm or env)
GRAFANA_URL = required_env("GRAFANA_URL")
GRAFANA_ADMIN_USER = required_env("GRAFANA_ADMIN_USER")
GRAFANA_ADMIN_PASSWORD = required_env("GRAFANA_ADMIN_PASSWORD")

# Required Mimir endpoints(must be passed via Helm or env)
BASE_STORE_GATEWAY_URL = required_env("STORE_GATEWAY_URL")
STORE_GATEWAY_URL = f"{BASE_STORE_GATEWAY_URL}/store-gateway/tenants"
BASE_MIMIR_QUERY_URL = required_env("MIMIR_QUERY_URL")
MIMIR_CARDINALITY_URL = f"{BASE_MIMIR_QUERY_URL}/prometheus/api/v1/cardinality/label_values"
MIMIR_QUERY_URL = f"{BASE_MIMIR_QUERY_URL}/prometheus/api/v1/query_range"
MIMIR_RULER_URL = required_env("MIMIR_RULER_URL")
MIMIR_TENANT_ID = required_env("MIMIR_TENANT_ID") #Mimir tenant where the loki recording rule is added.

# Optional log query window in days (for Loki analysis)
LOKI_QUERY_LOOKBACK_DAYS = int(required_env("LOKI_QUERY_LOOKBACK_DAYS"))
LOKI_QUERY_METRIC_NAME = required_env("LOKI_QUERY_METRIC_NAME")

# Required service account config(must be passed via Helm or env)
SERVICE_ACCOUNT_NAME = required_env("SERVICE_ACCOUNT_NAME")

# Optional operational config with safe defaults
TOKEN_EXPIRY_HOURS = int(os.getenv("TOKEN_EXPIRY_HOURS", "1"))
EXPORTER_PORT = int(os.getenv("EXPORTER_PORT", "8000"))
EXPORT_INTERVAL_SECONDS = int(os.getenv("EXPORT_INTERVAL_SECONDS", "86400"))
SSL_VERIFY = os.getenv("SSL_VERIFY", "true").lower() == "true"