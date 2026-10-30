import copy
import datetime as dt
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('analytics', ROOT/'scripts/analytics.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT/'assets/analytics/snapshot.json').read_text())

    def test_snapshot_has_complete_window_and_exclusions(self):
        a.validate(self.data)
        for r in self.data['repositories']:
            if r['name'] in a.EXCLUDED:
                self.assertEqual(r['languages'], {})

    def test_missing_calendar_day_fails_instead_of_becoming_zero(self):
        self.data['calendar'].pop(0)
        with self.assertRaises(AssertionError):
            a.validate(self.data)

    def test_reference_language_pollution_is_rejected(self):
        r = next(r for r in self.data['repositories'] if r['name']=='Zyberlane-Design-Library')
        r['languages']={'Python':9999999}
        with self.assertRaises(AssertionError):
            a.validate(self.data)

    def test_zero_activity_and_empty_languages_render_without_nan(self):
        for d in self.data['calendar']:
            d['count']=0
        for r in self.data['repositories']:
            r['commits']=[]
            r['languages']={}
            r['language']=None
            r['merged_prs']=0
        a.validate(self.data)
        for svg in a.render(self.data).values():
            ET.fromstring(svg)
            self.assertNotRegex(svg,r'\b(?:NaN|Infinity)\b')

    def test_calendar_parser_requires_numeric_tooltips_for_every_date(self):
        today=dt.date(2026,10,30)
        start=today-dt.timedelta(days=364)
        source=''.join(f'<td id="d{i}" data-date="{start+dt.timedelta(days=i)}"></td><tool-tip for="d{i}">{"No" if i==0 else "1,234"} contributions on October 1st.</tool-tip>' for i in range(365))
        days=a.parse_calendar(source,today)
        self.assertEqual(days[0]['count'],0)
        self.assertEqual(days[-1]['count'],1234)
        with self.assertRaises(ValueError):
            a.parse_calendar(source.replace('1,234 contributions','unknown contributions'),today)
        with self.assertRaises(ValueError):
            a.parse_calendar('',today)

    def test_all_rest_pages_are_consumed(self):
        with patch.object(a,'request',side_effect=[[{'x':i} for i in range(100)],[{'x':100}]]) as req:
            self.assertEqual(len(a.pages('repos/test/name/commits?author=diluxlane')),101)
            self.assertIn('&per_page=100&page=2',req.call_args.args[0])

    def test_bad_refresh_does_not_replace_last_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'analytics';out.mkdir()
            (out/'snapshot.json').write_text('previous-good-snapshot')
            self.data['calendar']=[]
            with patch.object(a,'OUT',out):
                with self.assertRaises(AssertionError):
                    a.write(self.data)
            self.assertEqual((out/'snapshot.json').read_text(),'previous-good-snapshot')

    def test_graphics_reproduce_and_contain_no_external_requests(self):
        for name,svg in a.render(self.data).items():
            ET.fromstring(svg)
            self.assertEqual(svg,(ROOT/'assets/analytics'/name).read_text())
            self.assertNotRegex(svg,r'<script|<foreignObject|href=|url\(https?')

    def test_totals_match_source_and_excluded_languages_do_not_leak(self):
        rendered=a.render(self.data)
        count=sum(d['count'] for d in self.data['calendar'])
        self.assertIn(f'{count:,}',rendered['activity.svg'])
        primary=[r['language'] for r in self.data['repositories'] if not r['language_excluded'] and r['language']]
        self.assertIn(f'{len(primary)} repos',rendered['languages-repos.svg'])
        self.assertEqual(set(self.data['language_exclusions']),a.EXCLUDED)
        self.assertEqual(set(rendered),{'activity.svg','activity-mobile.svg','languages-repos.svg','languages-bytes.svg','stats.svg','commits.svg'})

class ReadmeTests(unittest.TestCase):
    def test_local_assets_and_links_exist_and_have_alt_text(self):
        readme=(ROOT/'README.md').read_text()
        for path in re.findall(r'(?:src|srcset)="([^"]+)"',readme):
            self.assertFalse(path.startswith('http'))
            self.assertTrue((ROOT/path).is_file(),path)
        for tag in re.findall(r'<img\b[^>]+>',readme):
            self.assertRegex(tag,r'alt="[^"]+"')
        for target in re.findall(r'\]\(([^)]+)\)',readme):
            if not target.startswith('http'):
                self.assertTrue((ROOT/target).is_file(),target)

    def test_no_unrequested_widgets_or_private_contacts(self):
        readme=(ROOT/'README.md').read_text().lower()
        self.assertNotRegex(readme,r'github-profile-trophy|buymeacoffee|komarev|mailto:|tel:|random dev quote|masterjudah|sairaj')
        snapshot=(ROOT/'assets/analytics/snapshot.json').read_text()
        self.assertNotRegex(snapshot,r'@|"email"|"token"|"private"')
        self.assertLess(sum(p.stat().st_size for p in (ROOT/'assets/profile').glob('*.webp')),500_000)

    def test_svg_assets_parse(self):
        for path in (ROOT/'assets').rglob('*.svg'):
            ET.parse(path)

if __name__=='__main__':
    unittest.main()
