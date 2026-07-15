import os
import time
import logging
from pathlib import Path

import reapy
from reapy import reascript_api as RPR

from reaper_mcp.connection import get_project

logger = logging.getLogger("reaper_mcp.project_tools")


def _current_project_path(project) -> str:
    """Return the current .RPP path, not REAPER's project media directory."""
    try:
        result = RPR.EnumProjects(-1, "", 4096)
        if isinstance(result, str) and result.lower().endswith(".rpp"):
            return result
        if isinstance(result, (tuple, list)):
            for value in result:
                if isinstance(value, str) and value.lower().endswith(".rpp"):
                    return value
    except Exception:
        pass

    project_path = str(getattr(project, "path", "") or "")
    project_name = str(getattr(project, "name", "") or "")
    if project_path.lower().endswith(".rpp"):
        return project_path
    if project_name.lower().endswith(".rpp") and project_path:
        if os.path.basename(project_path).lower() == "media":
            project_path = os.path.dirname(project_path)
        return os.path.join(project_path, project_name)
    return project_path


def _time_signature(project) -> tuple[int, int]:
    """Normalize python-reapy's (tempo, numerator, denominator) tuple."""
    value = project.time_signature
    if len(value) >= 3:
        return int(value[-2]), int(value[-1])
    return int(value[0]), int(value[1])


def register_tools(mcp):

    @mcp.tool()
    def create_project(tempo: float = 120.0, time_signature: str = "4/4", name: str = "") -> dict:
        """Create a new REAPER project with the given tempo and time signature."""
        try:
            RPR.Main_OnCommand(41929, 0)  # File: New project
            project = get_project()
            if time_signature:
                num, denom = map(int, time_signature.split("/"))
                RPR.SetTempoTimeSigMarker(
                    project.id, -1, 0.0, -1, 0.0, tempo, num, denom, False
                )
            else:
                project.bpm = tempo
            return {
                "success": True,
                "name": name or f"New Project {time.strftime('%Y-%m-%d %H-%M-%S')}",
                "tempo": project.bpm,
                "time_signature": time_signature,
            }
        except Exception as e:
            logger.error(f"create_project failed: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def save_project(project_path: str = "") -> dict:
        """Save the current project. If no path is given, saves to ~/Documents/REAPER Projects."""
        try:
            project = get_project()
            if not project_path:
                project.save(force_save_as=False)
                project_path = _current_project_path(project)
            else:
                os.makedirs(os.path.dirname(os.path.abspath(project_path)), exist_ok=True)
                RPR.Main_SaveProjectEx(project.id, project_path, 0)
            return {"success": True, "project_path": project_path}
        except Exception as e:
            logger.error(f"save_project failed: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def load_project(project_path: str) -> dict:
        """Load a REAPER project (.rpp) from the given file path."""
        try:
            if not os.path.exists(project_path):
                return {"success": False, "error": f"File not found: {project_path}"}
            RPR.Main_openProject(project_path)
            project = get_project()
            numerator, denominator = _time_signature(project)
            return {
                "success": True,
                "name": project.name,
                "tempo": project.bpm,
                "time_signature": f"{numerator}/{denominator}",
                "project_path": project_path,
            }
        except Exception as e:
            logger.error(f"load_project failed: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def get_project_info() -> dict:
        """Get information about the current project: name, path, tempo, tracks, length."""
        try:
            project = get_project()
            numerator, denominator = _time_signature(project)
            markers = []
            try:
                for i in range(project.n_markers):
                    m = project.markers[i]
                    markers.append({"index": i, "name": m.name, "position": m.position})
            except Exception:
                pass

            regions = []
            try:
                for i in range(project.n_regions):
                    r = project.regions[i]
                    regions.append({"index": i, "name": r.name, "start": r.start, "end": r.end})
            except Exception:
                pass

            return {
                "success": True,
                "name": project.name,
                "path": _current_project_path(project),
                "tempo": project.bpm,
                "time_signature": f"{numerator}/{denominator}",
                "length": project.length,
                "track_count": project.n_tracks,
                "markers": markers,
                "regions": regions,
            }
        except Exception as e:
            logger.error(f"get_project_info failed: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def set_tempo(bpm: float) -> dict:
        """Set the project tempo in BPM."""
        try:
            project = get_project()
            project.bpm = bpm
            return {"success": True, "tempo": project.bpm}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def set_time_signature(numerator: int, denominator: int) -> dict:
        """Set the project time signature, e.g. 4/4, 3/4, 6/8."""
        try:
            project = get_project()
            if numerator <= 0 or denominator <= 0:
                return {"success": False, "error": "Time-signature values must be positive"}
            RPR.SetTempoTimeSigMarker(
                project.id,
                -1,
                0.0,
                -1,
                0.0,
                project.bpm,
                numerator,
                denominator,
                False,
            )
            return {"success": True, "time_signature": f"{numerator}/{denominator}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def create_marker(position: float, name: str = "", color: int = 0) -> dict:
        """Create a project marker at a position in seconds."""
        try:
            project = get_project()
            marker_index = RPR.AddProjectMarker2(
                project.id, False, position, 0.0, name, -1, color
            )
            return {
                "success": marker_index >= 0,
                "marker_index": marker_index,
                "position": position,
                "name": name,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def create_region(start: float, end: float, name: str = "", color: int = 0) -> dict:
        """Create a named project region between two positions in seconds."""
        try:
            if end <= start:
                return {"success": False, "error": "Region end must be after its start"}
            project = get_project()
            region_index = RPR.AddProjectMarker2(
                project.id, True, start, end, name, -1, color
            )
            return {
                "success": region_index >= 0,
                "region_index": region_index,
                "start": start,
                "end": end,
                "name": name,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def delete_marker_or_region(index: int, is_region: bool = False) -> dict:
        """Delete a project marker or region by its displayed index."""
        try:
            project = get_project()
            deleted = bool(RPR.DeleteProjectMarker(project.id, index, is_region))
            return {
                "success": deleted,
                "index": index,
                "is_region": is_region,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def set_time_selection(start: float, end: float) -> dict:
        """Set the project time selection in seconds; use 0, 0 to clear it."""
        try:
            if end < start:
                return {"success": False, "error": "Selection end must not precede start"}
            project = get_project()
            project.time_selection = (start, end)
            return {"success": True, "start": start, "end": end}
        except Exception as e:
            return {"success": False, "error": str(e)}
