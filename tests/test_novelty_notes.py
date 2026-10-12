import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from export_batch import novelty_text


class NoveltyNotes(unittest.TestCase):
    def test_radius_comes_from_receipt_and_empty_hypotheses_are_not_screen_passes(self):
        text = novelty_text({'checked_utc': '2026-10-12T18:00:00Z',
                             'arguments': {'cone_radius_arcsec': 120}})
        self.assertIn('120-arcsecond', text)
        self.assertNotIn('300-arcsecond', text)
        self.assertIn('does not attest', text)
        self.assertIn('no direct-screen receipt', text)
