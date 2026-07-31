import os
import logging
import array
import sys
import wave
from pathlib import Path

import reapy
from reapy import reascript_api as RPR

from reaper_mcp.connection import get_project

logger = logging.getLogger("reaper_mcp.render_tools")

# REAPER RENDER_FORMAT codes
FORMAT_CODES = {
    "wav":  0,
    "mp3":  3,
    "ogg":  4,
    "flac": 5,
}

# REAPER RENDER_FORMAT2 codes for WAV bit depth
BIT_DEPTH_CODES = {
    16: 0,
    24: 2,
    32: 4,
}

# Built-in Track > Render/freeze family. Resolve the installed names at runtime
# before execution; IDs outside this small native family are never considered.
TRACK_RENDER_ACTION_IDS = range(41716, 41722)

# GetSetProjectInfo RENDER_BOUNDSFLAG values from the REAPER ReaScript API.
RENDER_BOUNDS_ENTIRE_PROJECT = 1
RENDER_BOUNDS_TIME_SELECTION = 2


def _resolved_output_path(output_path: str, format: str) -> Path:
    """Return the exact file path REAPER should create for a render."""
    output = Path(output_path).expanduser().resolve()
    suffix = f".{format.lower()}"
    if output.suffix.lower() != suffix:
        output = output.with_suffix(suffix)
    return output


def _set_render_settings(
    output_path: str,
    format: str,
    sample_rate: int,
    bit_depth: int,
    channels: int,
    bounds: int,
) -> str:
    """Configure REAPER's render settings and return the exact output file path."""
    output = _resolved_output_path(output_path, format)
    fmt_code = FORMAT_CODES.get(format.lower(), 0)
    bdepth_code = BIT_DEPTH_CODES.get(bit_depth, 2)
    # RENDER_FILE is a directory and RENDER_PATTERN is the filename pattern.
    # Passing a full .wav path as RENDER_FILE makes REAPER create a directory
    # with that name and put the real render inside it.
    RPR.GetSetProjectInfo_String(0, "RENDER_FILE", str(output.parent), True)
    RPR.GetSetProjectInfo_String(0, "RENDER_PATTERN", output.stem, True)
    RPR.GetSetProjectInfo(0, "RENDER_FORMAT", fmt_code, True)
    RPR.GetSetProjectInfo(0, "RENDER_FORMAT2", bdepth_code, True)
    RPR.GetSetProjectInfo(0, "RENDER_SRATE", float(sample_rate), True)
    RPR.GetSetProjectInfo(0, "RENDER_CHANNELS", float(channels), True)
    RPR.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", float(bounds), True)
    RPR.GetSetProjectInfo(0, "RENDER_SETTINGS", 0.0, True)  # Master mix
    RPR.GetSetProjectInfo(0, "RENDER_ADDTOPROJ", 0.0, True)
    return str(output)


def _render_file_result(output_path: str) -> dict:
    """Validate that REAPER produced a regular, non-header-only audio file."""
    output = Path(output_path)
    if not output.is_file():
        return {
            "success": False,
            "error": "Render command completed but no regular output file was found",
            "output_path": str(output),
        }
    size = output.stat().st_size
    if size <= 44:
        return {
            "success": False,
            "error": "Render output contains no audio payload",
            "output_path": str(output),
            "file_size_bytes": size,
        }
    if output.suffix.lower() == ".wav":
        signal = _wav_has_signal(output)
        if signal is False:
            return {
                "success": False,
                "error": "Render output is effectively silent (peak below -80 dBFS)",
                "output_path": str(output),
                "file_size_bytes": size,
            }
    return {
        "success": True,
        "output_path": str(output),
        "file_size_bytes": size,
    }


def _wav_has_signal(output: Path, minimum_peak_db: float = -80.0) -> bool | None:
    """Return whether a PCM WAV exceeds a minimum peak, or None if unsupported."""
    try:
        with wave.open(str(output), "rb") as wav:
            width = wav.getsampwidth()
            if width not in (1, 2, 3, 4):
                return None
            threshold = int((1 << (width * 8 - 1)) * 10 ** (minimum_peak_db / 20.0))
            while True:
                data = wav.readframes(65536)
                if not data:
                    return False
                if width == 3:
                    # 24-bit PCM has no native Python array type. A -80 dBFS
                    # threshold is about 839: samples above roughly 1023 must
                    # have either a non-sign-extension high byte or a middle
                    # byte outside the four values nearest each signed limit.
                    high = data[2::3]
                    if len(high) != high.count(0) + high.count(255):
                        return True
                    middle = data[1::3]
                    quiet_middle = (0, 1, 2, 3, 252, 253, 254, 255)
                    if len(middle) != sum(middle.count(value) for value in quiet_middle):
                        return True
                    continue

                typecode = {1: "B", 2: "h", 4: "i"}[width]
                samples = array.array(typecode)
                samples.frombytes(data)
                if sys.byteorder != "little" and width > 1:
                    samples.byteswap()
                if width == 1:
                    if max(samples) - 128 > threshold or 128 - min(samples) > threshold:
                        return True
                elif max(samples) > threshold or min(samples) < -threshold:
                    return True
    except (wave.Error, OSError):
        return None


def _main_action_section():
    """Return REAPER's main action-list section handle."""
    return RPR.SectionFromUniqueID(0)


def _action_name(command_id: int, section) -> str:
    value = RPR.kbd_getTextFromCmd(command_id, section)
    if isinstance(value, (tuple, list)):
        strings = [part for part in value if isinstance(part, str)]
        return strings[-1] if strings else ""
    return value if isinstance(value, str) else ""


def render_to_temp_file(sample_rate: int = 48000) -> str:
    """
    Render the current project to a temporary WAV file and return its path.
    Used by analysis and mastering tools. Caller is responsible for deleting the file.
    """
    import tempfile
    tmp = tempfile.mktemp(suffix=".wav")
    tmp = _set_render_settings(
        tmp, "wav", sample_rate, 24, 2, bounds=RENDER_BOUNDS_ENTIRE_PROJECT
    )
    RPR.Main_OnCommand(41824, 0)
    return tmp


def register_tools(mcp):

    @mcp.tool()
    def find_reaper_actions(query: str, max_results: int = 50) -> dict:
        """Find installed native Track Render/Freeze actions by name."""
        try:
            needle = query.strip().lower()
            if not needle:
                return {"success": False, "error": "query must not be empty"}
            limit = max(1, min(int(max_results), 200))
            section = _main_action_section()
            matches = []
            for command_id in TRACK_RENDER_ACTION_IDS:
                if len(matches) >= limit:
                    break
                name = _action_name(command_id, section)
                if needle in name.lower():
                    matches.append({"command_id": command_id, "name": name})
            return {
                "success": True,
                "query": query,
                "count": len(matches),
                "actions": matches,
            }
        except Exception as e:
            logger.error(f"find_reaper_actions failed: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def run_track_render_action(
        command_id: int,
        track_indices: list[int],
        source_track_indices: list[int] = None,
    ) -> dict:
        """
        Run one installed native Track Render/Freeze action on selected tracks.

        For safety, the command's installed name must begin with "Track: Render
        tracks" or "Track: Freeze tracks". source_track_indices may contain a full
        upstream dependency closure; those tracks are temporarily unmuted while the
        native action runs and their prior mute state is restored afterward. Selected
        targets are unmuted before the action and are then left in the state chosen by
        REAPER (render-and-mute/freeze actions normally mute or freeze them).
        """
        project = None
        source_mutes = []
        try:
            RPR.Main_OnCommand(1016, 0)  # Transport: Stop
            project = get_project()
            targets = sorted(set(track_indices or []))
            sources = sorted(set(source_track_indices or []))
            invalid = [
                idx for idx in targets + sources
                if not 0 <= idx < project.n_tracks
            ]
            if invalid:
                return {"success": False, "error": f"Invalid track indices: {invalid}"}
            if not targets:
                return {"success": False, "error": "At least one target track is required"}
            overlap = sorted(set(targets) & set(sources))
            if overlap:
                return {
                    "success": False,
                    "error": f"Target tracks must not also be source tracks: {overlap}",
                }

            section = _main_action_section()
            name = _action_name(int(command_id), section)
            allowed = (
                name.lower().startswith("track: render tracks")
                or name.lower().startswith("track: freeze tracks")
            )
            if not allowed:
                return {
                    "success": False,
                    "error": "Only native Track: Render tracks/Freeze tracks actions are allowed",
                    "command_id": command_id,
                    "action_name": name,
                }

            tracks = list(project.tracks)
            before_count = project.n_tracks
            before_names = [track.name for track in tracks]
            for track in tracks:
                RPR.SetTrackSelected(track.id, False)
            for idx in sources:
                track = tracks[idx]
                source_mutes.append((track, RPR.GetMediaTrackInfo_Value(track.id, "B_MUTE")))
                RPR.SetMediaTrackInfo_Value(track.id, "B_MUTE", 0.0)
            for idx in targets:
                RPR.SetMediaTrackInfo_Value(tracks[idx].id, "B_MUTE", 0.0)
                RPR.SetTrackSelected(tracks[idx].id, True)

            RPR.Main_OnCommand(int(command_id), 0)
            refreshed = get_project()
            after_names = [track.name for track in refreshed.tracks]
            return {
                "success": True,
                "command_id": int(command_id),
                "action_name": name,
                "target_track_indices": targets,
                "source_track_indices": sources,
                "track_count_before": before_count,
                "track_count_after": refreshed.n_tracks,
                "new_tracks": [
                    {"index": idx, "name": after_names[idx]}
                    for idx in range(before_count, refreshed.n_tracks)
                ],
                "track_names_before": before_names,
            }
        except Exception as e:
            logger.error(f"run_track_render_action failed: {e}")
            return {"success": False, "error": str(e)}
        finally:
            for track, muted in source_mutes:
                try:
                    RPR.SetMediaTrackInfo_Value(track.id, "B_MUTE", muted)
                except Exception as restore_error:
                    logger.error(f"Could not restore source mute state: {restore_error}")

    @mcp.tool()
    def render_project(
        output_path: str,
        format: str = "wav",
        sample_rate: int = 48000,
        bit_depth: int = 24,
        channels: int = 2,
    ) -> dict:
        """
        Render the entire project to a file.
        format: wav, flac, mp3 (requires LAME), ogg.
        sample_rate: e.g. 44100, 48000, 96000.
        bit_depth: 16, 24, or 32 (WAV only; ignored for mp3/ogg/flac).
        channels: 1 (mono) or 2 (stereo).
        """
        try:
            output_path = str(_resolved_output_path(output_path, format))
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            output_path = _set_render_settings(
                output_path,
                format,
                sample_rate,
                bit_depth,
                channels,
                bounds=RENDER_BOUNDS_ENTIRE_PROJECT,
            )
            RPR.Main_OnCommand(41824, 0)  # File: Render project to disk (no dialog)
            result = _render_file_result(output_path)
            if not result["success"]:
                return result
            return result | {
                "format": format,
                "sample_rate": sample_rate,
                "bit_depth": bit_depth,
                "channels": channels,
            }
        except Exception as e:
            logger.error(f"render_project failed: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def render_time_selection(
        output_path: str,
        start: float,
        end: float,
        format: str = "wav",
        sample_rate: int = 48000,
        bit_depth: int = 24,
        channels: int = 2,
    ) -> dict:
        """Render a specific time range of the project to a file."""
        try:
            output_path = str(_resolved_output_path(output_path, format))
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            project = get_project()
            project.time_selection = (start, end)
            output_path = _set_render_settings(
                output_path,
                format,
                sample_rate,
                bit_depth,
                channels,
                bounds=RENDER_BOUNDS_TIME_SELECTION,
            )
            RPR.Main_OnCommand(41824, 0)
            result = _render_file_result(output_path)
            if not result["success"]:
                return result
            return result | {
                "start": start,
                "end": end,
                "format": format,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def render_stems(
        output_directory: str,
        track_indices: list = None,
        format: str = "wav",
        sample_rate: int = 48000,
        bit_depth: int = 24,
    ) -> dict:
        """
        Render each track as a separate stem file by soloing each track individually.
        track_indices: list of track indices, or null to render all tracks.
        Files are named after the track names in the output directory.
        """
        try:
            output_directory = str(Path(output_directory).expanduser().resolve())
            os.makedirs(output_directory, exist_ok=True)
            project = get_project()
            indices = track_indices if track_indices is not None else list(range(project.n_tracks))
            rendered = []

            for idx in indices:
                track = project.tracks[idx]
                track_name = track.name or f"Track_{idx}"
                # Solo this track exclusively
                for j in range(project.n_tracks):
                    project.tracks[j].solo = (j == idx)
                # Sanitize filename
                safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in track_name)
                stem_path = os.path.join(output_directory, f"{safe_name}.{format}")
                stem_path = _set_render_settings(
                    stem_path,
                    format,
                    sample_rate,
                    bit_depth,
                    2,
                    bounds=RENDER_BOUNDS_ENTIRE_PROJECT,
                )
                RPR.Main_OnCommand(41824, 0)
                result = _render_file_result(stem_path)
                rendered.append({
                    "track_index": idx,
                    "track_name": track_name,
                    "output_path": stem_path,
                    "success": result["success"],
                    "file_size_bytes": result.get("file_size_bytes"),
                    "error": result.get("error"),
                })

            # Unsolo all tracks
            for j in range(project.n_tracks):
                project.tracks[j].solo = False

            return {
                "success": True,
                "output_directory": output_directory,
                "stems": rendered,
            }
        except Exception as e:
            # Always unsolo on error
            try:
                proj = get_project()
                for j in range(proj.n_tracks):
                    proj.tracks[j].solo = False
            except Exception:
                pass
            logger.error(f"render_stems failed: {e}")
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def render_track_with_sources(
        track_index: int,
        source_track_indices: list[int],
        output_path: str,
        start: float = 0.0,
        end: float = 0.0,
        sample_rate: int = 48000,
        bit_depth: int = 24,
        channels: int = 2,
        import_to_new_track: bool = False,
        printed_track_name: str = "",
        mute_original_after_import: bool = False,
    ) -> dict:
        """
        Render one receive-driven/stateful track while its upstream sources process.

        source_track_indices must contain the complete upstream dependency closure,
        not only the target's immediate senders. The render normally starts at zero
        so stateful generators can learn/evolve before the target becomes audible.
        An end of 0 uses the project length. During rendering, unrelated tracks are
        muted and source tracks have their direct master output disabled, so only the
        target is printed. All mute, solo, main-send, cursor, and time-selection state
        is restored afterward, even if rendering fails.

        If import_to_new_track is true, the rendered file is inserted on a new track
        at the render start. The original is muted afterward only when both import and
        mute_original_after_import are true.
        """
        project = None
        tracks = []
        states = []
        cursor = None
        time_selection = None
        try:
            RPR.Main_OnCommand(1016, 0)  # Transport: Stop
            project = get_project()
            n_tracks = project.n_tracks
            if not 0 <= track_index < n_tracks:
                return {"success": False, "error": f"Invalid target track index: {track_index}"}

            sources = sorted(set(source_track_indices or []))
            invalid = [idx for idx in sources if not 0 <= idx < n_tracks]
            if invalid:
                return {"success": False, "error": f"Invalid source track indices: {invalid}"}
            if track_index in sources:
                return {"success": False, "error": "Target track must not also be a source track"}

            render_end = float(end) if end > 0 else float(project.length)
            if start < 0 or render_end <= start:
                return {
                    "success": False,
                    "error": f"Invalid render range: start={start}, end={render_end}",
                }

            output = _resolved_output_path(output_path, "wav")
            if output.exists():
                return {
                    "success": False,
                    "error": "Output path already exists; choose a new versioned filename",
                    "output_path": str(output),
                }
            output.parent.mkdir(parents=True, exist_ok=True)

            tracks = list(project.tracks)
            for track in tracks:
                states.append({
                    "mute": RPR.GetMediaTrackInfo_Value(track.id, "B_MUTE"),
                    "solo": RPR.GetMediaTrackInfo_Value(track.id, "I_SOLO"),
                    "main_send": RPR.GetMediaTrackInfo_Value(track.id, "B_MAINSEND"),
                    "selected": RPR.GetMediaTrackInfo_Value(track.id, "I_SELECTED"),
                })
            cursor = project.cursor_position
            time_selection = project.time_selection

            active = set(sources) | {track_index}
            for idx, track in enumerate(tracks):
                RPR.SetMediaTrackInfo_Value(track.id, "I_SOLO", 0.0)
                RPR.SetMediaTrackInfo_Value(track.id, "B_MUTE", 0.0 if idx in active else 1.0)
                if idx in sources:
                    RPR.SetMediaTrackInfo_Value(track.id, "B_MAINSEND", 0.0)
            RPR.SetMediaTrackInfo_Value(tracks[track_index].id, "B_MAINSEND", 1.0)

            project.cursor_position = float(start)
            project.time_selection = (float(start), render_end)
            output_path = _set_render_settings(
                str(output),
                "wav",
                sample_rate,
                bit_depth,
                channels,
                bounds=RENDER_BOUNDS_TIME_SELECTION,
            )
            RPR.Main_OnCommand(41824, 0)  # File: Render project to disk (no dialog)
            result = _render_file_result(output_path)
            if not result["success"]:
                return result

            target_name = tracks[track_index].name or f"Track {track_index}"
            source_names = [tracks[idx].name or f"Track {idx}" for idx in sources]
            result |= {
                "track_index": track_index,
                "track_name": target_name,
                "source_track_indices": sources,
                "source_track_names": source_names,
                "start": float(start),
                "end": render_end,
                "sample_rate": sample_rate,
                "bit_depth": bit_depth,
                "channels": channels,
                "imported": False,
            }
        except Exception as e:
            logger.error(f"render_track_with_sources failed: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if project is not None and states:
                try:
                    for track, state in zip(tracks, states):
                        RPR.SetMediaTrackInfo_Value(track.id, "B_MUTE", state["mute"])
                        RPR.SetMediaTrackInfo_Value(track.id, "I_SOLO", state["solo"])
                        RPR.SetMediaTrackInfo_Value(track.id, "B_MAINSEND", state["main_send"])
                        RPR.SetMediaTrackInfo_Value(track.id, "I_SELECTED", state["selected"])
                    project.cursor_position = cursor
                    project.time_selection = time_selection
                except Exception as restore_error:
                    logger.error(f"Could not fully restore track state: {restore_error}")

        if import_to_new_track:
            try:
                insert_index = project.n_tracks
                RPR.InsertTrackAtIndex(insert_index, True)
                printed_track = RPR.GetTrack(0, insert_index)
                name = printed_track_name.strip() or f"{result['track_name']} [printed]"
                RPR.GetSetMediaTrackInfo_String(printed_track, "P_NAME", name, True)
                RPR.SetOnlyTrackSelected(printed_track)
                project.cursor_position = float(start)
                RPR.InsertMedia(result["output_path"], 0)
                if mute_original_after_import:
                    RPR.SetMediaTrackInfo_Value(tracks[track_index].id, "B_MUTE", 1.0)
                project.cursor_position = cursor
                RPR.UpdateArrange()
                result |= {
                    "imported": True,
                    "printed_track_index": insert_index,
                    "printed_track_name": name,
                    "original_muted": bool(mute_original_after_import),
                }
            except Exception as e:
                logger.error(f"Rendered successfully but import failed: {e}")
                result |= {"success": False, "import_error": str(e)}

        return result
