# REAPER MCP agent notes

## Purpose

This repository provides an MCP server for controlling a live REAPER session through `python-reapy`. Work here often spans two kinds of state:

- source changes in this repository;
- musical changes in the currently connected REAPER project, often saved outside the repository.

Keep those states distinct and report both accurately.

## Live-session safety

- Inspect `get_project_info` and `list_tracks` before editing.
- Stop transport before loading, duplicating, or making structural changes.
- Save an explicit, versioned `.RPP` safety copy before material edits. Do not overwrite the user's source project.
- Prefer explicit paths with `save_project`. A modal Save dialog in REAPER can block an MCP call indefinitely; if a call stalls, ask the user to check REAPER before retrying.
- A `load_project` call may take several minutes while generative VST3 plugins initialize. Terminating the waiting client does not prove the load failed; poll `get_project_info` afterward.
- Track indices are ephemeral. Duplication or insertion shifts every later index, so call `list_tracks` again immediately after structural edits.
- Treat tool `success` fields as authoritative, but independently validate important files and state. A bridge helper can report success while returning misleading metadata.

## Long-call discipline

- Do not enumerate every parameter of a large VST3 unless necessary. Some MIDI-input DPF VST3 plugins expose thousands of hidden host parameters.
- Use focused calls such as `get_fx_parameter` when a host parameter index is known.
- Run live REAPER writes serially. Parallel read-only inspection is usually acceptable, but parallel envelope/track edits risk inconsistent host state.
- Give REAPER time to instantiate or render plugins, while providing user updates at least once per minute.
- If an MCP wrapper is terminated, assume its underlying REAPER operation may have partially or fully completed and re-inspect before retrying.

## python-reapy compatibility findings

- `FXParam` uses `.normalized` and `.formatted`, not `.normalized_value` or `.formatted_value`.
- `Project.path` may be REAPER's media directory rather than the `.RPP` filename. Prefer `EnumProjects` and retain a fallback based on project name.
- `Project.time_signature` is inconsistent across reapy/REAPER versions. Do not assume a two-element tuple contains numerator and denominator; verify with the native ReaScript time-map API before changing this helper again.
- `Project.time_signature` has no setter in the installed binding. Set meter through a tempo/time-signature marker with the ReaScript API.
- REAPER pointer-returning APIs may not compare cleanly with `reapy` object IDs. In particular, send-destination reporting needs binding-aware pointer normalization; a matching send count does not prove the destination-name helper worked.
- New or changed MCP tools require an MCP server restart before they appear in the tool schema.

## VST3/DPF parameter indexing

DPF's VST3 wrapper prepends hidden parameters for MIDI-input plugins. With MIDI input enabled it reserves:

```text
130 controls × 16 MIDI channels = 2080 hidden host parameters
```

The plugin's own first parameter therefore commonly appears at REAPER host index `2080`, not `0`. REAPER may append additional host controls afterward.

Example: Downspout Basilico declares 30 real parameters. Its local `ParamId::model` is index 0, but its REAPER VST3 host index is expected to be 2080. Industrial is raw model value 4 and normalized value 1.0. Always verify the host parameter name with `get_fx_parameter` before writing.

Do not “fix” this by changing a plugin's parameter table. The large count is wrapper behavior. Use focused MCP parameter access instead.

## Track duplication and automation

- `duplicate_track` uses REAPER's native duplicate-track action so FX, routing, items, and envelopes are copied exactly.
- Duplication also copies the source volume envelope. If the duplicate should enter only in one scene, clear its copied points with `delete_volume_automation_range` before writing a new envelope.
- `add_volume_automation` positions are seconds and values are dB.
- REAPER envelope points interpolate linearly. A single “off” point followed much later by an “on” point creates a long fade, not a held silence. Add paired boundary points when a level must remain constant.
- Static mute is not timed automation. Once section envelopes are established, tracks generally need to remain statically unmuted so the envelopes control audibility.
- `add_fx_parameter_automation` uses normalized values from 0.0 to 1.0. Confirm discrete parameter names and formatted values first.
- A muted empty MIDI item can serve as a concrete project-duration anchor when REAPER stops at the last media item despite later envelope points.

## Rendering caveat

Rendering is currently not the preferred verification path for the Phoenix project; the user will render manually.

The render helper has previously treated an output path ending in `.wav` as a directory and allowed REAPER to create `$project.wav` inside it. It then reported the directory size as if it were the render file size. Do not claim a render is valid based only on `exists()` or a nonzero size. Confirm that the output is a regular audio file and inspect its duration/header.

## Downspout work

- Read `/home/danny/github/downspout/AGENTS.md` before touching Downspout source.
- Read `/home/danny/github/downspout/docs/summary.md` before choosing or rearranging its plugins.
- Preserve generator-before-instrument FX order.
- Downspout prohibits git operations unless the user explicitly approves them.
- Do not modify Downspout shared/framework code without explicit user approval.
- Basilico's existing core test executable is typically at `/home/danny/github/downspout/build/plugins/basilico/downspout_basilico_core_tests` and has passed during the Phoenix work.

## Phoenix project handoff

For the current Phoenix composition, read [docs/phoenix-progress.md](docs/phoenix-progress.md) completely before touching REAPER. It records:

- the latest `.RPP` checkpoint;
- current live-session uncertainty;
- shifted track indices;
- the Industrial Basilico plan;
- exact fire-scene crossfade times and levels;
- MCP source changes that require restart.

The arrangement brief and original plan are in [docs/phoenix.md](docs/phoenix.md) and [docs/phoenix-plan.md](docs/phoenix-plan.md).

## Source validation

After Python source edits, run:

```bash
python -m compileall -q src
git diff --check
```

Do not run destructive git commands or alter unrelated user changes. This worktree may already contain moved, deleted, modified, or untracked files that belong to the user.
