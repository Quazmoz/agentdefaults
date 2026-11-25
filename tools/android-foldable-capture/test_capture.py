import unittest

from capture import active_display


class ActiveDisplayTest(unittest.TestCase):
    def fake_adb(self, state):
        resources = {
            ("shell", "dumpsys", "device_state"):
                f"  mCommittedState=Optional[DeviceState{{identifier=0, name='{state}'}}]",
            ("shell", "dumpsys", "SurfaceFlinger", "--display-id"):
                "Display 123\nDisplay 456",
            ("shell", "dumpsys", "display"):
                'DisplayDeviceInfo{uniqueId="local:123", state OFF}\n'
                'DisplayDeviceInfo{uniqueId="local:456", state ON}',
        }
        return lambda *args: resources[args].encode()

    def test_cover_requires_closed_state(self):
        self.assertIsNone(active_display(self.fake_adb("DEFAULT"), 1, "fold"))
        self.assertEqual("456", active_display(self.fake_adb("CLOSED"), 1, "fold"))

    def test_powered_off_panel_is_unavailable(self):
        self.assertIsNone(active_display(self.fake_adb("OPENED"), 0, "unfold"))


if __name__ == "__main__":
    unittest.main()
