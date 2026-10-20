"""The Server pulse charts have to work without a hover state.

The overview tab used to tell people to hover a day for exact counts, which a
phone can never do. Both charts now select a day on pointer down, keep the
counts in a live readout, and scrub while a finger drags across the plot.
These checks keep that wiring and the touch-friendly CSS from regressing back
to a hover-only tooltip.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "web" / "src" / "components" / "dashboard" / "ServerStatsCard.tsx"
STYLES = ROOT / "web" / "src" / "styles" / "server-stats.css"


class ServerPulseTouchTests(unittest.TestCase):
    def setUp(self):
        self.card = CARD.read_text(encoding="utf-8")
        self.styles = STYLES.read_text(encoding="utf-8")

    def test_both_charts_select_a_day_from_a_pointer(self):
        # The message line and the member columns share the same scrub wiring.
        self.assertEqual(
            self.card.count(
                "onPointerDown={(event) => { capturePointer(event); pick(event.clientX); }}"
            ),
            2,
        )
        self.assertEqual(
            self.card.count(
                "onPointerMove={(event) => { if (event.pointerType === \"mouse\" || event.buttons) pick(event.clientX); }}"
            ),
            2,
        )
        # A touch pointer never reports "mouse", so leaving must not wipe the
        # selection a tap just made.
        self.assertEqual(
            self.card.count(
                "onPointerLeave={(event) => { if (event.pointerType === \"mouse\" && !event.buttons) clear(); }}"
            ),
            2,
        )

    def test_the_selected_day_is_announced_and_highlighted(self):
        # The two chart readouts are the card's only live regions: the refresh
        # itself is passive and no longer announces a sync badge or timestamp.
        self.assertEqual(self.card.count('aria-live="polite"'), 2)
        self.assertEqual(self.card.count('server-chart-readout'), 2)
        self.assertIn("server-chart-readout", self.card)
        self.assertIn("is-selected", self.card)
        self.assertIn("server-chart-guide", self.card)
        self.assertIn("Tap or hover a day for exact counts", self.card)
        self.assertNotIn("Hover a day for exact counts", self.card)

    def test_keyboards_and_screen_readers_can_step_through_days(self):
        self.assertEqual(self.card.count("tabIndex={0}"), 2)
        self.assertEqual(self.card.count("onKeyDown={(event) => handleDayKeyDown(event, move)}"), 2)
        # Only the chart itself is in the tab order; every member column still
        # carries a readable label for assistive technology.
        self.assertIn('tabIndex={-1}', self.card)
        self.assertIn("joined, ${formatNumber(day.leaves)} left`", self.card)

    def test_touch_scrolling_stays_available(self):
        self.assertGreaterEqual(self.styles.count("touch-action: pan-y"), 2)
        self.assertIn(".dashboard-layout .server-chart-readout", self.styles)
        self.assertIn(".dashboard-layout .server-chart-point.is-selected", self.styles)


if __name__ == "__main__":
    unittest.main()
