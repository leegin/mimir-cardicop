import unittest
from unittest.mock import patch, Mock
import exporter.loki as loki
import requests

class TestLoki(unittest.TestCase):

    @patch('exporter.loki.requests.get')
    def test_check_metric_queried_true(self, mock_get):
        mock_get.return_value = Mock(status_code=200, json=lambda: {"data": {"result": [1]}})
        self.assertTrue(loki.check_metric_queried("metric"))

    @patch('exporter.loki.requests.get')
    def test_check_metric_queried_false(self, mock_get):
        mock_get.return_value = Mock(status_code=200, json=lambda: {"data": {"result": []}})
        self.assertFalse(loki.check_metric_queried("metric"))

    @patch('exporter.loki.requests.get',side_effect=requests.RequestException('fail'))
    def test_check_metric_queried_error(self, mock_get):
        self.assertFalse(loki.check_metric_queried("metric"))

if __name__ == "__main__":
    unittest.main()
