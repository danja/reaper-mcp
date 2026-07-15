# Phoenix implementation progress

## Current handoff

- Latest known-good project: `/home/danny/Music/phoenix/phoenix-arrangement-v10.RPP`
- Tempo/form: 130 BPM, 4/4, 164 planned bars (302.77 seconds)
- The full Up/Down lifecycle arrangement and narrative volume envelopes are present.
- A muted, empty five-minute MIDI item on `tune` now gives REAPER a concrete playback endpoint. This fixed playback stopping around 2:31.
- The user has auditioned the arrangement and reports that it sounds good.
- Full-mix rendering is intentionally left to the user. A source-aware print of
  Counterpointer Down has been created and placed in the project.

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

## Surreal medieval timbral pass completed

The approved `v04` structure is preserved. `v05` adds motion to the existing instrumentation and effects without adding new dense layers.

- Both MelGen tracks retain their GM Reed Organ patch and now use ReaControlMIDI automation:
  - CC processing enabled throughout;
  - expression/volume breathing shaped around each audible section;
  - mirrored MIDI-pan movement between ascending and descending voices;
  - small pitch-wheel inflections for unstable, non-equal-tempered colour without turning into obvious pitch effects.
- Cadence Up/Down StereoChorus now changes speed and depth by narrative scene:
  - restrained beating in ordinary life/aging;
  - deeper, slower ritual modulation for aromatic branches and enclosure;
  - faster, wider instability during the pyre;
  - luminous but controlled movement during resurrection.
- Counterpointer delays now use asymmetric feedback, wet/dry, and tempo-division envelopes during aging and rebirth, creating antiphonal echoes rather than a fixed delay wash.
- DrumGen's Rift is host-enabled but controlled by a Bypass envelope:
  - bypassed during the main body of the arrangement;
  - active only in the wingbeat transition around bars 33-39 and the fire/consumption section around bars 97-112;
  - Density, Damage, Drift, Pitch, Mix, and Chop evolve inside those windows and reset afterward.
- Automation write results:
  - 74 ReaControlMIDI points;
  - 144 chorus/delay/Rift points;
  - no tool-reported failures.
- Saved-file inspection confirms all expected named parameter envelopes and point counts.
- Focused live verification confirms ReaControlMIDI `CC Enable` is on, Rift is bypassed before bar 33, and becomes active inside the transition.
- The edit cursor is left at 57.2308 s, just before bar 33, for manual audition.
- Rendering remains manual.

## MCP source changes active after restart

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
- Added `render_track_with_sources` for receive-driven/stateful tracks. It temporarily
  unmutes the target and an explicit complete upstream dependency list, disables the
  sources' direct master output, renders only the target from time zero (unless told
  otherwise), restores track state, and can optionally import the print to a new track.
- Corrected render output handling: `RENDER_FILE` is now the parent directory and
  `RENDER_PATTERN` is the file stem. Render success now requires a regular file with
  an audio payload rather than accepting a directory as a successful render.

## Counterpointer Down monotone: source-aware print failed; native render pending

- The user reports that `counterpointer down` currently produces a discordant
  monotone. This is consistent with Counterpointer retaining one learned pitch when
  transport begins after its input history or when receiving source tracks are muted.
- Saved `v05` routing confirms `counterpointer down` (track 12) directly receives from
  `bassgen up` (6), `bassgen down` (7), `melgen up` (9), and `melgen down` (10).
- Those four tracks themselves depend on all three ground tracks: `ground up` (3),
  `ground down` (4), and `ground down industrial` (5). The full source closure for a
  print is therefore `[3, 4, 5, 6, 7, 9, 10]`, not only the four immediate senders.
- `phoenix-arrangement-v06.RPP` was saved as a safety checkpoint before rendering.
- `render_track_with_sources` rendered target track 12 using complete source closure
  `[3, 4, 5, 6, 7, 9, 10]`, from 0 to 302.7692 seconds, without importing or muting.
- The test output is `/home/danny/Music/phoenix/counterpointer-down-v06-test.wav`:
  regular WAV, PCM 24-bit stereo at 48 kHz, 302.769229 seconds, 87,198,228 bytes.
- The print was appended at time 0 on track 23, named
  `counterpointer down [printed]`. REAPER copied its project media to
  `/home/danny/Music/phoenix/Media/counterpointer-down-v06-test.wav`.
- Live `counterpointer down` remains track 12 with its five-FX generator chain intact,
  but is statically muted. The printed track is unmuted, has one audio item, and no FX
  because pan, volume-envelope, instrument, and delay processing are baked in.
- The completed arrangement is saved as
  `/home/danny/Music/phoenix/phoenix-arrangement-v07.RPP` and independently confirmed
  as a regular RPP containing both the muted live track and appended print.
- `get_project_info` still reports the open tab as `v05`; this is the known behavior
  where explicit `save_project` writes a durable copy without changing tab identity.
  Treat `v07` as authoritative and load it explicitly in a future session if needed.
- Track count is now 24. Existing indices 0-22 are unchanged because the print was
  appended; the printed track is index 23.
- The user auditioned the printed track and found it silent. Independent FFmpeg
  analysis confirms both peak and mean at -91 dBFS across the file: it contains only
  digital silence/dither despite being a structurally valid 87 MB WAV. The earlier
  "resolved" assessment was incorrect.
- Do not use or trust `counterpointer-down-v06-test.wav` or its project-media copy.
  In the current saved `v07`, track 23 is this invalid print and track 12 is the muted
  live generator. Restore audible working state by muting/removing track 23 and
  unmuting track 12 before further audition.
- MCP source now rejects effectively silent WAV renders and adds
  `find_reaper_actions` plus constrained `run_track_render_action`. These need another
  MCP restart.
- The bad `v07` state was preserved unchanged as `phoenix-arrangement-v08.RPP`.
  The audible fallback state was then saved as `phoenix-arrangement-v09.RPP`: live
  generator track 12 is unmuted and invalid printed track 23 is muted. Track 23 has
  not been deleted, so its provenance remains inspectable until a valid native stem
  replaces it.
- After restart, search installed actions for `render tracks` and choose a native
  stereo stem/render-and-mute option from REAPER's Track menu. Run it on live target
  track 12 with source closure `[3, 4, 5, 6, 7, 9, 10]` temporarily unmuted. Verify
  the resulting stem has real signal before removing the invalid printed track.
- First post-restart testing found that the initial `find_reaper_actions` implementation
  enumerated the entire action list through thousands of distant-API round trips. Two
  parallel searches were terminated, but their underlying calls left that MCP server
  occupied; no render action or project mutation occurred. Source now checks only the
  six built-in Track Render/Freeze IDs 41716-41721 and still resolves/validates each
  installed action name at runtime. Restart MCP again before continuing.

## Native stereo stem attempt: failed offline, live load uncertain

- Focused action discovery showed IDs 41716-41721 are the six "render selected area"
  variants in REAPER 7.77, not the entire-project family. ID 40788 was then verified
  at runtime as exactly `Track: Render tracks to stereo stem tracks (and mute originals)`.
- `phoenix-arrangement-v10.RPP` was saved before executing native action 40788 on
  Counterpointer Down with source closure `[3, 4, 5, 6, 7, 9, 10]` unmuted.
- REAPER inserted `counterpointer down - stem` before the source track, shifting the
  original live generator from index 12 to 13 and the old invalid print from 23 to 24.
  The new stem was index 12, unmuted, with the original narrative volume envelope;
  the live source at 13 was muted by the native action.
- The native media file is
  `/home/danny/Music/phoenix/Media/phoenix-arrangement-v09_stems_counterpointer down.wav`:
  32-bit float stereo/48 kHz, 303.769229 seconds, 116,648,128 bytes.
- This native offline render is also invalid. `astats` measured roughly +13 dBFS RMS,
  peaks around +13.7 dBFS, DC offset up to 0.118, and raw samples around +/-4.8 full
  scale. A spectrogram of the intended audible interval showed continuous dense
  broadband energy rather than a changing melodic Counterpointer line.
- The failed native experiment was saved as `phoenix-arrangement-v11.RPP` for forensic
  inspection only. Do not use it as the arrangement checkpoint.
- A request to reload known-good `v10` timed out after 300 seconds. The subsequent
  `get_project_info` poll also remained queued and its client was terminated. The
  underlying load may still complete; inspect REAPER directly before retrying or
  changing anything. If a modal dialog is present, dismiss it, then confirm `v10` is
  loaded and re-list all tracks.
- Both custom offline rendering and REAPER's native offline stem render mishandle this
  stateful receive-driven chain. The next approach should be a true real-time print:
  either force the native render to 1x online if the track-render action honors that
  project setting, or route/record the target's stereo output onto a new track while
  playing from time 0. Preserve `v10` before that experiment.
