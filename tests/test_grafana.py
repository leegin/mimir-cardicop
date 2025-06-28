import unittest
from unittest.mock import patch, Mock
import exporter.grafana as grafana

class TestGrafana(unittest.TestCase):

    @patch('exporter.grafana.requests.get')
    def test_get_all_grafana_orgs_success(self, mock_get):
        mock_get.return_value = Mock(status_code=200, json=lambda: [{"id": 1}])
        result = grafana.get_all_orgs()
        self.assertEqual(result, [{"id": 1}])

    @patch('exporter.grafana.requests.get')
    def test_get_all_grafana_orgs_failure(self, mock_get):
        mock_get.return_value = Mock(status_code=500, text="fail")
        result = grafana.get_all_orgs()
        self.assertEqual(result, [])

    @patch('exporter.grafana.requests.post')
    def test_switch_org_success(self, mock_post):
        mock_post.return_value = Mock(status_code=200)
        self.assertTrue(grafana.switch_org(1))

    @patch('exporter.grafana.requests.post')
    def test_switch_org_failure(self, mock_post):
        mock_post.return_value = Mock(status_code=400, text="fail")
        self.assertFalse(grafana.switch_org(1))

    @patch('exporter.grafana.subprocess.run')
    def test_run_analysis_for_org(self, mock_run):
        mock_run.return_value = Mock(returncode=0, stdout="ok")
        grafana.run_grafana_analysis_for_org("token", "orgname")
        mock_run.assert_called_once()

if __name__ == "__main__":
    unittest.main()
