# The Phoenix: REAPER MCP Production Plan

## Objective

Turn the existing `/home/danny/Music/phoenix/phoenix.RPP` sketch into an approximately five-minute instrumental narrative of the phoenix lifecycle. The paired ascending and descending Downspout generators should provide the main musical motion, separated by sparse bridges and fills. The arrangement must leave deliberate space for a later vocal and sound-effects pass.

This plan is based on a read-only REAPER MCP inspection of the loaded project on 2026-07-15, plus the Downspout capability summary.

## Current project snapshot

- Project: `phoenix.RPP`
- Tempo: 130 BPM
- Reported length: 332.31 seconds (about 5:32, or 180 bars of 4/4 at 130 BPM)
- Tracks: 22
- Markers/regions: none
- Main generator pairs:
  - `ground up` / `ground down`
  - `bassgen up` / `bassgen down`
  - `melgen up` / `melgen down`
  - `counterpointer up` / `counterpointer down`
  - `Cadence up` / `Cadence down`
- Supporting tracks: `Drumgen`, `gremlin`, `tune`, `FX`, and five muted `CV` tracks
- The `up` tracks are currently muted and the `down` tracks are active.
- The generator tracks already contain instruments and processing. Preserve their FX order because MIDI processors must remain before instruments.
- Ground and BassGen tracks have six sends each; MelGen tracks have two. The MCP response does not identify send destinations, so these existing sends must not be rebuilt or removed blindly.
- The project-info tool returned an invalid time-signature string (`130.0/4.0`). Treat this as a bridge/reporting defect and explicitly establish 4/4 before calculating or writing the arrangement.

## Musical design

- Tempo/meter: 130 BPM, 4/4
- Tonal center: retain the pitch/scale already programmed in the generator pairs unless inspection shows the pairs disagree. Prefer a dark D or E modal center if a common center still needs to be chosen.
- Target form: 164 bars, 302.77 seconds (about 5:03)
- Core contrast:
  - `up` family = youth, flight, sunlight, flame, growth, resurrection
  - `down` family = age, gravity, enclosure, consumption, ash
  - bridges/fills = aromatics, mystery, the ninth day, and space for future voice/SFX
- Recurring motif: a short three-note rising cell, answered by its falling inversion. Keep it recognizable through register, density, and timbre changes rather than introducing unrelated material in every section.
- Density ceiling: no more than three principal pitched layers plus drums at once. Counterpointer should normally replace MelGen rather than stack continuously with it.
- Vocal space: reserve broad, stable midrange openings in bars 1-8, 49-56, 81-88, 113-128, and 161-164. Avoid sustained lead activity in those windows.

## Form and narrative

At 130 BPM one bar is approximately 1.846 seconds. Times below are suitable for MCP automation positions; recalculate from the confirmed project tempo before executing.

| Bars | Time | Scene | Generator direction and texture |
|---|---:|---|---|
| 1-8 | 0:00-0:15 | Solitary bird / Arabia | Sparse bridge: `tune` or a single Cadence voice, no full drums; leave room for opening narration |
| 9-32 | 0:15-0:59 | Youth, colour, long life, flight | First ascent: Ground Up + MelGen Up; add light DrumGen after bar 16; introduce Cadence Up only near the peak |
| 33-40 | 0:59-1:14 | First wingbeat fill | Pull bass and harmony away; use a short DrumGen/Rift or Gremlin fill, then near-silence for one bar |
| 41-64 | 1:14-1:58 | Age and descent | Ground Down + MelGen Down; bring Counterpointer Down in as a restrained answer; drums become heavier but less busy |
| 65-80 | 1:58-2:28 | Gathering frankincense, myrrh, aromatic branches | Bridge: Cadence Up with a sparse high line and very light percussion; gradually widen/brighten, avoiding full bass for the first eight bars |
| 81-96 | 2:28-2:57 | Building the pyre / facing the sun | Second ascent: BassGen Up + Cadence Up; add MelGen Up only in bars 89-96; staged crescendo with space at the start for voice/SFX |
| 97-112 | 2:57-3:27 | Wingbeats, fire, consumption | Abrupt turn to the Down family. DrumGen is strongest here; controlled Rift/Gremlin gestures mark bars 104 and 111, followed by a hard collapse |
| 113-128 | 3:27-3:56 | Ashes / death / ninth day | Near-silence. No drums for bars 113-120. Use one low or frozen texture, then faint isolated high notes; this is the largest vocal/SFX window |
| 129-144 | 3:56-4:26 | Worm, growth, acquiring wings | Third ascent begins from minimal Ground Up, then adds Counterpointer Up and soft percussion in stages; increase register before density |
| 145-160 | 4:26-4:55 | Resurrection and restored form | Full but controlled Up-family climax: Ground or BassGen Up, Cadence Up, one melodic voice, and drums. Restate the opening motif in a higher register |
| 161-164 | 4:55-5:03 | Solitary bird renewed / coda | Remove drums and bass; leave one rising figure and an ambience tail, with room for the final vocal line |

The final render should end near bar 164. Do not delete existing material beyond that point during the first pass; render a 0-302.77 second time selection until the arrangement is approved.

## Track roles

Use the present track indices only as an initial map. Re-run `list_tracks` immediately before every editing pass because adding or deleting tracks changes indices.

| Current index | Track | Intended role |
|---:|---|---|
| 0 | drums | Existing drum bus/limiter; preserve and confirm routing |
| 1 | Drumgen | Main rhythmic arc; restrained except in the fire and resurrection sections |
| 2 | Bass | Existing bass bus/limiter; preserve and confirm routing |
| 3 / 4 | ground up / down | Long-form foundation; primary low-frequency narrative pair |
| 5 / 6 | bassgen up / down | More active alternative bass motion; use selectively so it does not double Ground continuously |
| 7 | Keys | Existing keys bus/limiter; preserve and confirm routing |
| 8 / 9 | melgen up / down | Main bird/flight voice, left side; silence it during major vocal windows |
| 10 / 11 | counterpointer up / down | Right-side answering voice; use for dialogue and rebirth, not constant doubling |
| 12 / 13 | Cadence up / down | Harmonic colour and ritual/faith layer; especially useful in the aromatics and resurrection scenes |
| 14 | FX | Destination for later sound effects; keep mostly empty now |
| 15 | gremlin | Brief fire, fracture, and rebirth transition gestures only |
| 16 | tune | Existing one-item reference/seed; inspect before altering |
| 17-21 | CV 1/2/4/8/16 | Existing control material; preserve muted state until routing and purpose are confirmed |

## REAPER MCP execution plan

### 1. Protect and audit the session

1. Ensure transport is stopped with `stop_transport`.
2. Confirm the loaded project with `get_project_info`; if it is not `phoenix.RPP`, use `load_project` on the stated source path.
3. Immediately make a working copy with `save_project`, for example `/home/danny/Music/phoenix/phoenix-arrangement-v01.RPP`. Never overwrite the source sketch during development.
4. Run `list_tracks`, then `get_track_info`, `list_track_fx`, and `list_sends` for every existing musical track.
5. Use `get_fx_parameters` on the first FX of every Up/Down generator pair. Record parameter names, normalized values, and formatted values before changing anything. Verify that each pair really implements opposite contours and shares key, scale, phrase length, and deterministic/random settings.
6. Inspect the `tune` item and CV routing manually in REAPER if MCP cannot reveal their MIDI contents or send destinations. This is a required checkpoint before modifying those tracks.
7. Explicitly call `set_time_signature(4, 4)`. Retain 130 BPM unless listening reveals transport-sync problems.
8. Save again after the audit.

### 2. Establish a repeatable section switch

Timed mute automation is not exposed by this MCP server, and `set_track_mute` is only static. Use `add_volume_automation` to gate each generator family by section:

- Off level: `-150 dB`
- Typical active starting levels: Ground/BassGen `-10 to -6 dB`, MelGen/Counterpointer `-14 to -9 dB`, Cadence `-16 to -10 dB`, DrumGen `-18 to -8 dB`
- Use two points around a boundary for a short crossfade, normally 0.25-1 bar. Use 2-4 bars for narrative crescendos such as the pyre and rebirth.
- Add an explicit point at time 0 on every generator track so the pre-existing static mute state does not make the envelope ambiguous.
- After envelopes are established, unmute both Up and Down tracks statically with `set_track_mute(..., false)`; their envelopes then determine when they are audible.
- Never activate both Ground and BassGen at full level together. Crossfade or choose one.

Because `add_volume_automation` creates linear envelope points, paired points are required to hold a level and make a deliberate step or fade. Verify every call's `success` field and audition each boundary.

Suggested primary gates:

- Up foundation: active bars 9-32, 81-96, and 129-160
- Down foundation: active bars 41-64 and 97-112
- MelGen: active only in selected halves of those blocks
- Counterpointer: bars 49-64 and 137-152
- Cadence: bars 25-32, 65-96, and 145-160
- DrumGen: fade in at bar 17; pull back at bars 33, 65, 113, and 161; strongest at bars 97-111 and 145-156

### 3. Tune the generators without destroying the pair concept

1. Use `get_fx_parameters` to locate musical controls by name rather than assuming parameter indices.
2. Use `set_fx_parameter` only after capturing the existing value in the session log.
3. Keep Up/Down pair settings identical except for contour/direction and any intentional register distinction.
4. Ground should provide the slow, evolving foundation; BassGen should add more explicit pulse or propulsion. Avoid running both as equally dense bass parts.
5. MelGen carries the main phoenix motif. Counterpointer supplies an answer when the arrangement needs dialogue; confirm it receives useful MIDI input before relying on it.
6. Cadence supplies ritual harmonic support. Keep its lower midrange thin during future vocal windows.
7. Prefer existing saved presets through `load_fx_preset` when suitable preset names are known. Do not invent preset names.
8. Save a new project version after parameter tuning, before automation is expanded across the full form.

### 4. Build bridges and fills

- First wingbeat fill, bars 33-40: thin all pitched generators, retain a shortened DrumGen gesture, and enable the existing Rift on `Drumgen` only for a controlled transition. `bypass_fx` can set Rift's static state, but MCP cannot automate FX bypass over time; render the gesture to audio or perform/automate it manually if it must exist only in this section.
- Aromatics, bars 65-80: use Cadence and a sparse authored high-register MIDI clip on an existing suitable instrument or a new Canticle/Floozy track. If a new track is required, call `create_track`, add the instrument with `add_fx`, then add notes in one batch with `create_midi_clip`.
- Fire, bars 97-112: use DrumGen plus brief Gremlin/Rift gestures. Keep feedback and output conservative. Render/freeze destructive or section-specific effects if static MCP bypass would affect the whole song.
- Ashes, bars 113-128: automate almost everything to `-150 dB`. A single sustained/frozen timbre may remain, but leave at least the first eight bars drumless.
- Rebirth, bars 129-144: introduce layers every four bars rather than starting them together.
- Coda, bars 161-164: remove bass and percussion and allow an ambience tail beyond the musical endpoint if needed.

Use `create_midi_clip` rather than many `add_midi_note` calls for any authored motif, seed, or fill. Times inside each clip are relative to the item start and drums use MIDI channel 9.

### 5. Mix for the later vocal and SFX passes

1. Establish conservative static balance with `set_track_volume` and keep the master below clipping; do not normalize during composition.
2. Retain the current broad MelGen-left / Counterpointer-right dialogue, but reduce the extreme near-100% pans if mono compatibility is poor.
3. Keep bass centered and high-pass non-bass textures where the existing ReaEQ permits it.
4. Use a shared ambience bus only if the current routing audit shows one is absent. Create it with `create_bus` or `create_track` + `create_send`; start sends quiet (roughly -18 dB to -12 dB).
5. Avoid high Ambo feedback, stacked delay/shimmer, uncontrolled Rift repeats, and heavy Gremlin randomization.
6. Preserve at least 6 dB of practical headroom for later vocals and sound effects. A premaster around -18 to -14 LUFS with peaks below -3 dBFS is a useful working target, not a final mastering mandate.
7. Do not apply a final mastering chain until vocals and sound effects are present.

### 6. Audition, revise, and verify

1. Save before playback and before every render.
2. Audition from several boundaries with `set_cursor_position` + `play_project`, then `stop_transport`: bars 9, 33, 41, 65, 81, 97, 113, 129, 145, and 161.
3. At every boundary check for hanging notes, generator phase resets, excessive overlap, silent routing, and abrupt ambience cuts.
4. Make section review renders with `render_time_selection`, especially:
   - 0:00-1:14 (opening and first turn)
   - 1:58-3:27 (aromatics through fire)
   - 3:27-5:03 (ashes through resurrection)
5. Render the approved instrumental time selection to `/home/danny/Music/phoenix/renders/phoenix-instrumental-v01.wav`, 48 kHz, 24-bit stereo.
6. Run `detect_clipping`, `analyze_loudness`, `analyze_dynamics`, `analyze_frequency_spectrum`, and `analyze_stereo_field`. Treat tool `success` values as authoritative; do not claim a render or analysis exists if a call times out or the file is absent.
7. Revise balance if there is clipping, extreme sub-bass accumulation, negative stereo correlation, or insufficient contrast between the ashes and resurrection sections.
8. Save the approved arrangement as a new numbered `.RPP` version and retain the unmastered render for the later vocal/SFX session.

## MCP limitations and manual checkpoints

- No tool creates markers or regions. Add the scene names manually in REAPER, or extend the MCP server before execution if fully automated region creation is desired.
- No tool exposes timed FX parameter/bypass automation. Use track-volume automation, rendered transition audio, or manual REAPER automation for section-specific Rift/Gremlin/Ambo moves.
- `list_sends` does not report destination tracks. Existing sends must be mapped in REAPER before changing them.
- Track item inspection reports only position and length, not MIDI note contents. The `tune` and CV items require manual inspection or an MCP enhancement.
- `render_project` renders the entire project. Until the old 180-bar tail is intentionally trimmed, use `render_time_selection` for the planned 164-bar version.
- Generator output may depend on live transport and random state. Capture approved performances to audio or MIDI in REAPER if exact repeatability is required; save deterministic seeds wherever the plugins expose them.

## Definition of done

- A safety-copy `.RPP` exists; the source sketch is untouched.
- The project has a clear 164-bar lifecycle form with audible Up/Down alternation and bridges between major turns.
- The ashes section is materially quieter and sparser than every other section.
- The resurrection develops recognizable earlier material rather than merely becoming louder.
- The listed vocal windows remain uncluttered in the midrange.
- No uncontrolled feedback, hanging notes, or digital clipping is present.
- A verified 48 kHz/24-bit unmastered instrumental render exists at a durable path.
- Project and render paths, analysis results, and any manual/bridge limitations are documented for the vocal/SFX handoff.
