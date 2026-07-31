import unittest
from types import SimpleNamespace
from unittest.mock import patch

from reaper_mcp import mastering_tools


class MasterVolumeTests(unittest.TestCase):
    def test_sets_native_master_volume_as_linear_gain(self):
        master = SimpleNamespace(id="master-track")
        expected_linear = 10 ** (-4.0 / 20.0)

        with patch.object(
            mastering_tools.RPR, "SetMediaTrackInfo_Value", create=True
        ) as set_value:
            with patch.object(
                mastering_tools.RPR,
                "GetMediaTrackInfo_Value",
                return_value=expected_linear,
                create=True,
            ):
                actual_db = mastering_tools._set_master_volume_db(master, -4.0)

        set_value.assert_called_once_with(master.id, "D_VOL", expected_linear)
        self.assertAlmostEqual(actual_db, -4.0)

    def test_maps_silence_to_zero_linear_gain(self):
        self.assertEqual(mastering_tools._db_to_linear(-150.0), 0.0)
        self.assertEqual(mastering_tools._linear_to_db(0.0), -150.0)

    def test_rejects_invalid_master_volume(self):
        master = SimpleNamespace(id="master-track")
        with self.assertRaisesRegex(ValueError, "between -150 and 12"):
            mastering_tools._set_master_volume_db(master, 13.0)


if __name__ == "__main__":
    unittest.main()
