# Phoenix implementation progress

## Current handoff

- Latest project: `/home/danny/Music/phoenix/phoenix-arrangement-v03.RPP`
- Tempo/form: 130 BPM, 4/4, 164 planned bars (302.77 seconds)
- The full Up/Down lifecycle arrangement and narrative volume envelopes are present.
- A muted, empty five-minute MIDI item on `tune` now gives REAPER a concrete playback endpoint. This fixed playback stopping around 2:31.
- The user has auditioned the arrangement and reports that it sounds good.
- Rendering is intentionally left to the user.

## Pending musical change

Duplicate `ground down`, change only the duplicate's Basilico `Voice Model` to `Industrial`, and crossfade from the original voice into Industrial during the fire/consumption scene.

After restarting the MCP server:

1. Load `phoenix-arrangement-v03.RPP` and save immediately as `phoenix-arrangement-v04.RPP`.
2. Re-run `list_tracks`; do not assume indices after duplication.
3. Call `duplicate_track` on `ground down`, naming the duplicate `ground down industrial`.
4. Call `list_track_fx` on the duplicate and locate Basilico by name (it was FX index 2 before duplication).
5. Call `get_fx_parameters` for Basilico and locate `Voice Model`/`model` by parameter name. Confirm its formatted values rather than assuming an index.
6. Set that parameter to the formatted `Industrial` choice. Basilico has five models and the saved source state shows `model=2`; Industrial is expected to be the final choice, commonly normalized `1.0`, but verify through the MCP response before setting it.
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

## MCP source changes awaiting restart

- Fixed project time-signature setting/reporting and `.RPP` path reporting.
- Fixed python-reapy FX parameter reads/writes (`normalized` and `formatted`).
- Added `duplicate_track` for exact duplication of FX, routing, items, and envelopes.
- Added `add_fx_parameter_automation` for normalized track-FX envelope points.
- Added marker/region creation and deletion.
- Added explicit time-selection control.
- Enhanced `list_sends` with destination track index/name.
- Added `delete_volume_automation_range` for safely replacing copied envelopes.

Run a source compile check before restart. After restart, smoke-test the new read-only/reporting calls before making the `v04` edit.
