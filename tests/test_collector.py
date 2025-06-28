import unittest
from unittest.mock import patch, mock_open, MagicMock
import exporter.collector as collector

class TestCollector(unittest.TestCase):

    @patch('exporter.collector.glob.glob')
    @patch('builtins.open', new_callable=mock_open, read_data='{"metricsUsed": ["metric1"]}')
    @patch('json.dump')
    def test_combine_metrics_files(self, mock_json_dump, mock_open_file, mock_glob):
        mock_glob.return_value = ['file1.json', 'file2.json']

        # All open calls should return valid JSON
        handle = mock_open_file.return_value.__enter__.return_value
        handle.read.return_value = '{"metricsUsed": ["metric1"]}'

        collector.combine_metrics_files()

        mock_glob.assert_called_once()
        self.assertTrue(mock_json_dump.called)

    @patch('exporter.collector.glob.glob', return_value=[])
    @patch('json.dump')
    def test_combine_metrics_files_no_files(self, mock_json_dump, mock_glob):
        collector.combine_metrics_files()
        mock_json_dump.assert_called_once_with({'metricsUsed': []}, unittest.mock.ANY, indent=4)

if __name__ == "__main__":
    unittest.main()
