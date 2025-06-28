import unittest
from unittest.mock import patch, Mock
import exporter.mimir as mimir

class TestMimir(unittest.TestCase):


    @patch('exporter.mimir.requests.get')
    def test_get_tenants_failure(self, mock_get):
        mock_get.side_effect = Exception("fail")
        tenants = mimir.get_tenants("http://dummy")
        self.assertEqual(tenants, [])

    @patch('exporter.mimir.requests.get')
    def test_get_metrics_for_tenant_valid(self, mock_get):
        mock_get.return_value = Mock(
            status_code=200, 
            json=lambda: {"labels": [{"cardinality": [{"label_value": "metric"}]}]}
        )
        metrics = mimir.get_metrics_for_tenant("tenant")
        self.assertIn("metric", metrics)

    @patch('exporter.mimir.requests.get')
    def test_get_metrics_for_tenant_empty(self, mock_get):
        mock_get.return_value = Mock(status_code=200, json=lambda: {"labels": []})
        metrics = mimir.get_metrics_for_tenant("tenant")
        self.assertEqual(metrics, [])

    @patch('exporter.mimir.subprocess.run')
    def test_run_analysis_for_tenant(self, mock_run):
        mock_run.return_value = Mock(returncode=0)
        mimir.run_analysis_for_tenant("id")
        self.assertEqual(mock_run.call_count, 2)

    @patch('builtins.open')
    @patch('json.load')
    def test_get_used_metrics_success(self, mock_json, mock_open):
        mock_json.return_value = {"in_use_metric_counts": [{"metric": "a"}]}
        result = mimir.get_used_metrics()
        self.assertIn("a", result)

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_get_used_metrics_file_missing(self, mock_open):
        result = mimir.get_used_metrics()
        self.assertEqual(result, set())

if __name__ == "__main__":
    unittest.main()
