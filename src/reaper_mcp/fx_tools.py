import logging

import reapy
from reapy import reascript_api as RPR

from reaper_mcp.connection import get_project

logger = logging.getLogger("reaper_mcp.fx_tools")


def register_tools(mcp):

    @mcp.tool()
    def add_fx(track_index: int, fx_name: str) -> dict:
        """
        Add an FX plugin to a track. Works for both instruments (VSTi) and effects (VST/AU).
        Use the exact plugin name as shown in REAPER's FX browser.
        Built-in Cockos plugins: ReaEQ, ReaComp, ReaDelay, ReaVerb, ReaLimit, ReaSynth,
        ReaSamplOmatic5000, ReaTune, ReaGate, ReaFIR, ReaXcomp.
        """
        try:
            project = get_project()
            track = project.tracks[track_index]
            fx = track.add_fx(fx_name)
            fx_index = fx.index
            return {
                "success": True,
                "fx_index": fx_index,
                "name": fx.name,
                "n_params": fx.n_params,
                "track_index": track_index,
            }
        except Exception as e:
            logger.error(f"add_fx failed: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def remove_fx(track_index: int, fx_index: int) -> dict:
        """Remove an FX plugin from a track by its index."""
        try:
            project = get_project()
            track = project.tracks[track_index]
            fx_name = track.fxs[fx_index].name
            RPR.TrackFX_Delete(track.id, fx_index)
            return {"success": True, "track_index": track_index, "removed": fx_name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def set_fx_parameter(
        track_index: int, fx_index: int, param_index: int, value: float
    ) -> dict:
        """
        Set a normalized parameter value (0.0–1.0) on an FX plugin.
        Use get_fx_parameters to discover available parameters and their indices.
        """
        try:
            project = get_project()
            track = project.tracks[track_index]
            fx = track.fxs[fx_index]
            fx.params[param_index].normalized = value
            param_name = fx.params[param_index].name
            return {
                "success": True,
                "track_index": track_index,
                "fx_index": fx_index,
                "param_index": param_index,
                "param_name": param_name,
                "value": value,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def get_fx_parameters(track_index: int, fx_index: int) -> dict:
        """Get all parameters for an FX plugin, including names, indices, and current values."""
        try:
            project = get_project()
            track = project.tracks[track_index]
            fx = track.fxs[fx_index]
            params = []
            for i in range(fx.n_params):
                param = fx.params[i]
                params.append({
                    "index": i,
                    "name": param.name,
                    "normalized_value": float(param.normalized),
                    "formatted_value": param.formatted,
                })
            return {
                "success": True,
                "track_index": track_index,
                "fx_index": fx_index,
                "fx_name": fx.name,
                "parameters": params,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def get_fx_parameter(track_index: int, fx_index: int, param_index: int) -> dict:
        """Get one FX parameter without enumerating a plugin's full host parameter list."""
        try:
            project = get_project()
            track = project.tracks[track_index]
            fx = track.fxs[fx_index]
            if param_index < 0 or param_index >= fx.n_params:
                return {
                    "success": False,
                    "error": f"Parameter index {param_index} is outside 0-{fx.n_params - 1}",
                }
            param = fx.params[param_index]
            return {
                "success": True,
                "track_index": track_index,
                "fx_index": fx_index,
                "fx_name": fx.name,
                "param_index": param_index,
                "param_name": param.name,
                "normalized_value": float(param.normalized),
                "formatted_value": param.formatted,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def add_fx_parameter_automation(
        track_index: int,
        fx_index: int,
        param_index: int,
        position: float,
        value: float,
    ) -> dict:
        """Add a normalized (0.0-1.0) automation point for a track FX parameter."""
        try:
            if not 0.0 <= value <= 1.0:
                return {"success": False, "error": "value must be between 0.0 and 1.0"}
            project = get_project()
            track = project.tracks[track_index]
            fx = track.fxs[fx_index]
            param = fx.params[param_index]
            envelope = RPR.GetFXEnvelope(track.id, fx_index, param_index, True)
            if not envelope or str(envelope) in ("0", "(TrackEnvelope*)0x0000000000000000"):
                return {"success": False, "error": "FX parameter envelope could not be created"}
            RPR.DeleteEnvelopePointRange(envelope, position - 1e-6, position + 1e-6)
            RPR.InsertEnvelopePoint(envelope, position, value, 0, 0, False, True)
            RPR.Envelope_SortPoints(envelope)
            return {
                "success": True,
                "track_index": track_index,
                "fx_index": fx_index,
                "fx_name": fx.name,
                "param_index": param_index,
                "param_name": param.name,
                "position": position,
                "value": value,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def list_track_fx(track_index: int) -> dict:
        """List all FX plugins on a track."""
        try:
            project = get_project()
            track = project.tracks[track_index]
            fx_list = []
            for i in range(track.n_fxs):
                fx = track.fxs[i]
                fx_list.append({
                    "index": i,
                    "name": fx.name,
                    "enabled": fx.is_enabled,
                    "n_params": fx.n_params,
                })
            return {"success": True, "track_index": track_index, "fx": fx_list}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def bypass_fx(track_index: int, fx_index: int, bypassed: bool) -> dict:
        """Enable or bypass (disable) an FX plugin on a track."""
        try:
            project = get_project()
            track = project.tracks[track_index]
            fx = track.fxs[fx_index]
            fx.is_enabled = not bypassed
            return {
                "success": True,
                "track_index": track_index,
                "fx_index": fx_index,
                "fx_name": fx.name,
                "bypassed": bypassed,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def load_fx_preset(track_index: int, fx_index: int, preset_name: str) -> dict:
        """Load a saved preset by name for an FX plugin."""
        try:
            project = get_project()
            track = project.tracks[track_index]
            fx = track.fxs[fx_index]
            fx.preset_name = preset_name
            return {
                "success": True,
                "track_index": track_index,
                "fx_index": fx_index,
                "fx_name": fx.name,
                "preset": fx.preset_name,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
