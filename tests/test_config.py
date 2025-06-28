import os
import unittest
from unittest import mock

# Patch env BEFORE importing config
mock.patch.dict(os.environ, {
    "GRAFANA_URL": "http://dummy",
    "GRAFANA_ADMIN_USER": "admin",
    "GRAFANA_ADMIN_PASSWORD": "password",
    "STORE_GATEWAY_URL": "http://dummy",
    "MIMIR_QUERY_URL": "http://dummy",
    "MIMIR_RULER_URL": "http://dummy",
    "MIMIR_TENANT_ID": "tenant",
    "LOKI_QUERY_METRIC_NAME": "dummy",
    "LOKI_QUERY_LOOKBACK_DAYS": "7",
    "SERVICE_ACCOUNT_NAME": "dummy",
    "EXPORTER_PORT": "8000",
    "EXPORT_INTERVAL_SECONDS": "86400",
    "TOKEN_EXPIRY_HOURS": "1",
}).start()

import exporter.config as config

class TestConfig(unittest.TestCase):
    
    def test_required_env_present(self):
        with mock.patch.dict(os.environ, {"TEST_VAR": "value"}):
            self.assertEqual(config.required_env("TEST_VAR"), "value")

    def test_required_env_missing(self):
        with self.assertRaises(RuntimeError):
            config.required_env("MISSING_VAR")

    def test_defaults_are_ints(self):
        self.assertIsInstance(config.EXPORTER_PORT, int)
        self.assertIsInstance(config.TOKEN_EXPIRY_HOURS, int)
        self.assertIsInstance(config.EXPORT_INTERVAL_SECONDS, int)

if __name__ == "__main__":
    unittest.main()
