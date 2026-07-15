# Phoenix implementation progress

## Current handoff

- Latest completed project: `/home/danny/Music/phoenix/phoenix-arrangement-v04.RPP`
- Tempo/form: 130 BPM, 4/4, 164 planned bars (302.77 seconds)
- The full Up/Down lifecycle arrangement and narrative volume envelopes are present.
- A muted, empty five-minute MIDI item on `tune` now gives REAPER a concrete playback endpoint. This fixed playback stopping around 2:31.
- The user has auditioned the arrangement and reports that it sounds good.
- Rendering is intentionally left to the user.

## Industrial Ground edit: current live state

- `phoenix-arrangement-v03.RPP` was loaded successfully, then explicitly saved as `phoenix-arrangement-v04.RPP` before editing.
- `ground down` was duplicated successfully with the new name `ground down industrial`.
- Immediately after duplication, the original remains track 4 and the duplicate is track 5; all later tracks shifted by one.
- The duplicate contains the same seven FX in the same order. Basilico is FX index 2.
- The duplicate reports six sends at unity gain, matching the source send count and levels. Destination names remain unresolved because the first implementation of destination-pointer matching is incompatible with this reapy binding.
- A full `get_fx_parameters` call was stopped after it attempted to enumerate 2,115 host-exposed Basilico parameters. This is unexpectedly large and is being investigated in `/home/danny/github/downspout/plugins/basilico` before continuing.
- A focused `set_fx_parameter(track=5, fx=2, param=0, value=1.0)` call was started on the assumption that Basilico's saved DPF state places `model` first, but the call was interrupted before returning. It may or may not have applied. Treat the duplicate's current Voice Model as unknown and verify it before any further edit.
- The copied volume envelope was cleared and replaced with an Industrial-only fire envelope.
- The original `ground down` envelope was rebuilt cleanly so it remains silent before the aging scene, plays the aging scene alone, returns to silence through the ashes, and recedes during the fire crossfade.
- The completed duplicate, Industrial model envelope, and complementary crossfade are saved in `v04`.
- REAPER may still display `v03` as the live project name because `save_project` writes an explicit copy without changing the tab identity. The durable completed artifact is `v04`.

## Basilico sanity-check result

- Basilico declares exactly 30 musical/plugin parameters. Its local `ParamId::model` is index 0, ranges from raw values 0-4, is integer/restricted, and maps `4` to `Industrial`.
- The engine clamps and rounds integer parameters. Existing tests explicitly verify that a model input of 3.6 becomes 4, that every model renders audible output, and that extreme parameter values remain bounded.
- The existing Basilico core test executable passes.
- REAPER's count of 2,115 is explained by DPF's VST3 wrapper: MIDI-input plugins receive 2,080 hidden controller parameters (`130 controls x 16 channels`) before the plugin's own parameters. Basilico then contributes 30, and REAPER exposes five additional host controls.
- Focused inspection showed that REAPER prepends two controls before DPF's block: host index 2080 is `MIDI Ch. 16 CC 128`, 2081 is `MIDI Ch. 16 CC 129`, and Basilico `Model` is host index 2082. The interrupted host-index-0 write targeted a hidden MIDI control rather than Basilico's model and should not be relied upon.
- No Basilico source defect was found and no Downspout source change is recommended for this issue. The correction belongs in MCP parameter access.
- A focused `get_fx_parameter` MCP tool confirmed duplicate track 5 / FX 2 / host parameter 2082 is `Model`. A single FX-parameter envelope point at time zero sets normalized value `1.0`, verified as formatted value `Industrial`.

## Industrial Ground edit completed

- Duplicate: track 5, `ground down industrial`
- Basilico: FX index 2, host Model index 2082, verified `Industrial`
- Original `ground down` aging entrance: silence held until 73.7462 s, then active from 73.8462 s through the aging scene and silent again at 118.1538 s.
- Fire crossfade, bars 97-112:
  - Original starts at -11 dB and recedes through -14, -18, -24, and -30 dB before silence at bar 113.
  - Industrial holds silence until bar 97, rises through -20, -13, and -9 dB, then falls to -14 dB and silence at bar 113.
- The duplicate retained six unity-gain sends. Destination names remain unresolved in MCP reporting, but the native duplication retained the source routing count and levels.
- The edit cursor was left at 175.3846 s, just before bar 97, for manual audition.
- Rendering remains a manual user step.

## Completed musical change

`ground down` has been duplicated, the duplicate's Basilico Voice Model is verified as Industrial, and the original-to-Industrial fire/consumption crossfade is complete in `v04`.

Implementation record:

1. Load `phoenix-arrangement-v03.RPP` and save immediately as `phoenix-arrangement-v04.RPP`.
2. Re-run `list_tracks`; do not assume indices after duplication.
3. Call `duplicate_track` on `ground down`, naming the duplicate `ground down industrial`.
4. Call `list_track_fx` on the duplicate and locate Basilico by name (it was FX index 2 before duplication).
5. Call focused `get_fx_parameter` for Basilico host index 2082 and confirm it is `Model` (initially formatted as `Dub`).
6. Set that parameter to normalized `1.0` using its FX envelope and verify the formatted value is `Industrial`.
7. Call `delete_volume_automation_range` on the duplicate across the full project, then create an Industrial-only envelope:
   - time 0: -150 dB
   - bar 97 / 177.2308 s: -150 dB
   - bar 101 / 184.6154 s: -20 dB
   - bar 105 / 192.0000 s: -13 dB
   - bar 109 / 199.3846 s: -9 dB
   - bar 112 / 204.9231 s: -14 dB
   - bar 113 / 206.7692 s: -150 dB
8. Refine the original `ground down` fire envelope to recede against it:
   - bar 97 / 177.2308 s: -11 dB
   - bar 101 / 184.6154 s: -14 dB
   - bar 105 / 192.0000 s: -18 dB
   - bar 109 / 199.3846 s: -24 dB
   - bar 112 / 204.9231 s: -30 dB
   - bar 113 / 206.7692 s: -150 dB
9. Preserve the original `ground down` as the only one audible in the aging scene (bars 41-64). The Industrial duplicate should symbolize the pyre becoming destructive, not the bird's ordinary old age.
10. Confirm the duplicate retained the source sends using the enhanced `list_sends`, audition bars 97-113, make level adjustments if the distorted layers overaccumulate, and save `v04`.

Only the user's listening review and any resulting balance adjustment remain.

## MCP source changes awaiting restart

- Fixed project time-signature setting/reporting and `.RPP` path reporting.
- Fixed python-reapy FX parameter reads/writes (`normalized` and `formatted`).
- Replaced the incompatible reapy static parameter setter with native `TrackFX_SetParamNormalized`; restart MCP before relying on this latest setter fix.
- Added focused `get_fx_parameter` lookup to avoid enumerating thousands of hidden VST3 MIDI parameters.
- Added `duplicate_track` for exact duplication of FX, routing, items, and envelopes.
- Added `add_fx_parameter_automation` for normalized track-FX envelope points.
- Added marker/region creation and deletion.
- Added explicit time-selection control.
- Enhanced `list_sends` with destination track index/name.
- Added `delete_volume_automation_range` for safely replacing copied envelopes.

Run a source compile check before restart. After restart, smoke-test the new read-only/reporting calls before making the `v04` edit.
