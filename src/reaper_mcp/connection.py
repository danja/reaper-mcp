import logging
import reapy
from reapy import reascript_api as RPR

logger = logging.getLogger("reaper_mcp.connection")

_connected = False


def ensure_connected() -> None:
    global _connected
    if _connected and hasattr(RPR, "EnumProjects"):
        return
    try:
        if hasattr(RPR, "EnumProjects"):
            reapy.connect()
        else:
            reapy.reconnect()
        if not hasattr(RPR, "EnumProjects"):
            raise RuntimeError("REAPER connected without exposing EnumProjects")
        _connected = True
        logger.info("Connected to REAPER")
    except Exception as e:
        raise RuntimeError(
            f"Cannot connect to REAPER: {e}. "
            "Make sure REAPER is running and the distant API is enabled. "
            "To enable it: run the setup script (scripts/enable_reapy.py) or "
            "in REAPER go to Actions > Run ReaScript, then run: "
            "import reapy; reapy.config.enable_dist_api()"
        ) from e


def get_project() -> reapy.Project:
    ensure_connected()
    return reapy.Project()
