import unittest
import os
import json
from main import Config, StatsHistory, NetworkMonitor, TemperatureMonitor

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        # Clean up any existing config
        if os.path.exists('config.json'):
            os.remove('config.json')

    def tearDown(self):
        if os.path.exists('config.json'):
            os.remove('config.json')

    def test_config_defaults(self):
        self.assertEqual(self.config.get('theme'), 'cyberpunk')
        self.assertEqual(self.config.get('text_color'), '#00ffcc')

    def test_config_save_load(self):
        self.config.set('theme', 'minimalist')
        self.config.save_config()
        new_config = Config()
        self.assertEqual(new_config.get('theme'), 'minimalist')

class TestStatsHistory(unittest.TestCase):
    def setUp(self):
        self.history = StatsHistory(max_points=5)

    def test_add_cpu(self):
        self.history.add_cpu(50.0)
        self.history.add_cpu(60.0)
        self.assertEqual(len(self.history.cpu_history), 2)
        self.assertAlmostEqual(self.history.get_cpu_avg(), 55.0)

    def test_max_points(self):
        for i in range(7):
            self.history.add_cpu(float(i))
        self.assertEqual(len(self.history.cpu_history), 5)
        self.assertEqual(self.history.cpu_history[0], 2.0)  # First value should be removed

class TestNetworkMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = NetworkMonitor()

    def test_get_network_stats(self):
        sent, recv = self.monitor.get_network_stats()
        self.assertIsInstance(sent, (int, float))
        self.assertIsInstance(recv, (int, float))

class TestTemperatureMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = TemperatureMonitor()

    def test_get_cpu_temp(self):
        temp = self.monitor.get_cpu_temp()
        self.assertTrue(temp is None or isinstance(temp, (int, float)))

if __name__ == '__main__':
    unittest.main()