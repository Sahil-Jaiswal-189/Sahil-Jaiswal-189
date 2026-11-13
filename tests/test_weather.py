import importlib.util
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

spec = importlib.util.spec_from_file_location('widget', Path(__file__).parents[1] / 'scripts/update_dashboard.py')
widget = importlib.util.module_from_spec(spec)
spec.loader.exec_module(widget)


class WeatherRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'assets').mkdir()
        self.cache = self.root / 'assets/pune-weather.json'
        self.svg = self.root / 'assets/pune-dashboard.svg'
        self.patch_root = patch.object(widget, 'ROOT', self.root)
        self.patch_cache = patch.object(widget, 'CACHE', self.cache)
        self.patch_root.start()
        self.patch_cache.start()
        self.addCleanup(self.patch_root.stop)
        self.addCleanup(self.patch_cache.stop)
        self.current = dict(temperature_2m=28, weather_code=2, is_day=1, time='2026-11-13T12:00')

    def test_success_persists_reading(self):
        with patch.object(widget, 'fetch_weather', return_value=self.current):
            widget.main()
        self.assertEqual(json.loads(self.cache.read_text())['current'], self.current)
        self.assertIn('28°', self.svg.read_text())
        ET.parse(self.svg)

    def test_outage_uses_saved_data_and_marks_it_stale(self):
        self.cache.write_text(json.dumps({'current': self.current, 'observed_at': '2026-11-13T12:00:00+05:30'}))
        with patch.object(widget, 'fetch_weather', side_effect=RuntimeError('timeout')):
            widget.main()
        output = self.svg.read_text()
        self.assertIn('28°', output)
        self.assertIn('LAST KNOWN WEATHER', output)
        self.assertIn('Refresh delayed', output)
        self.assertNotIn('CURRENT WEATHER', output)
        self.assertNotIn('unavailable', output.lower())
        ET.parse(self.svg)

    def test_first_run_outage_preserves_existing_card(self):
        self.svg.write_text('previous valid card')
        with patch.object(widget, 'fetch_weather', side_effect=RuntimeError('timeout')):
            with self.assertRaisesRegex(RuntimeError, 'preserving existing widget'):
                widget.main()
        self.assertEqual(self.svg.read_text(), 'previous valid card')

    def test_invalid_api_readings_rejected(self):
        for bad in (None, float('nan'), '28'):
            with self.assertRaises(ValueError):
                widget.validate(dict(self.current, temperature_2m=bad))

    def test_backup_provider_and_day_night(self):
        data = {'current_condition': [{'temp_C': '30', 'weatherDesc': [{'value': 'Partly cloudy'}]}],
                'weather': [{'date': '2026-11-13', 'astronomy': [{'sunrise': '06:40 AM', 'sunset': '05:58 PM'}]}]}
        current = widget.secondary_weather(data, datetime(2026, 11, 13, 16, tzinfo=ZoneInfo('Asia/Kolkata')))
        self.assertEqual(current['source'], 'wttr.in')
        self.assertEqual(current['is_day'], 1)
        self.assertEqual(current['kind'], 'partial')
        night = widget.secondary_weather(data, datetime(2026, 11, 13, 20, tzinfo=ZoneInfo('Asia/Kolkata')))
        self.assertEqual(night['is_day'], 0)
        with patch.object(widget, 'fetch_json', side_effect=[RuntimeError('connection timeout'), data]), patch.object(widget, 'secondary_weather', return_value=current) as secondary:
            self.assertEqual(widget.fetch_weather(), current)
            secondary.assert_called_once()


if __name__ == '__main__':
    unittest.main()
