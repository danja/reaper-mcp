import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from reaper_mcp import render_tools


class RenderSettingsTests(unittest.TestCase):
    def test_reaper_render_bound_constants_match_api(self):
        self.assertEqual(render_tools.RENDER_BOUNDS_ENTIRE_PROJECT, 1)
        self.assertEqual(render_tools.RENDER_BOUNDS_TIME_SELECTION, 2)

    def test_sets_entire_project_bounds_for_project_render(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "test.wav"
            with patch.object(
                render_tools.RPR, "GetSetProjectInfo_String", create=True
            ):
                with patch.object(
                    render_tools.RPR, "GetSetProjectInfo", create=True
                ) as project_info:
                    render_tools._set_render_settings(
                        str(output),
                        "wav",
                        48000,
                        24,
                        2,
                        render_tools.RENDER_BOUNDS_ENTIRE_PROJECT,
                    )

        project_info.assert_any_call(0, "RENDER_BOUNDSFLAG", 1.0, True)

    def test_sets_time_selection_bounds_for_range_render(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "test.wav"
            with patch.object(
                render_tools.RPR, "GetSetProjectInfo_String", create=True
            ):
                with patch.object(
                    render_tools.RPR, "GetSetProjectInfo", create=True
                ) as project_info:
                    render_tools._set_render_settings(
                        str(output),
                        "wav",
                        48000,
                        24,
                        2,
                        render_tools.RENDER_BOUNDS_TIME_SELECTION,
                    )

        project_info.assert_any_call(0, "RENDER_BOUNDSFLAG", 2.0, True)


if __name__ == "__main__":
    unittest.main()
