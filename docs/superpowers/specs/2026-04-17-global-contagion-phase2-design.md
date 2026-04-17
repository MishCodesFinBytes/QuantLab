# Global Contagion Command Center — Phase 2 Design (Gesture Control)

**Date**: 2026-04-17
**Status**: design
**Depends on**: Phase 1 (merged, PR #203)
**Author**: brainstormed with Claude

## Purpose

Add opt-in hand-gesture control to the `/Global_Contagion` page from Phase 1. Visitors who enable the feature point their webcam at their hand and use three gestures — pinch-to-zoom, pointer-to-rotate-globe, two-finger-to-scrub-timeline — to navigate the contagion replay. The mouse-only Phase 1 experience remains first-class: gestures are strictly additive and default to off.

This is the ambitious "Minority Report" layer described in the original brief, now scoped to a single iteration with conservative fallbacks.

## Scope

### In
- `dashboard/lib/contagion/gestures.py` — pure gesture classifier (no streamlit, no webrtc, fully unit-testable)
- `dashboard/lib/contagion/webcam.py` — `streamlit-webrtc` adapter that runs mediapipe on frames and writes `GestureState` to `st.session_state`
- Opt-in `🖐️ Enable gesture control` toggle in the existing page, with 240×180 corner preview showing the 21-point hand skeleton
- Three gestures: **pinch → zoom**, **pointer → rotate**, **two-finger → scrub timeline**
- Playback speed selector (`1× / 2× / 4× / 8×`) next to the ▶ Play button — pulled forward from Phase 3 because it's cheap
- "Gestures hidden" escape hatch: URL param `?gestures=off` or env var `QUANTLAB_GESTURES_HIDDEN=1` suppresses the toggle entirely
- Graceful degradation cascade: import error → permission denial → stream timeout → all fall back to mouse-only with a clear caption
- Tech-demo blog post on FinBytes (finance-methodology post shipped in Phase 1)

### Out (Phase 3+)
- Drill-in from aggregated epicenter to 3 component arcs on click
- VIX-driven arc glow intensity
- "Top 3 At-Risk Markets" overlay panel
- Key-event preset buttons ("Soleimani strike", "Port attack")

## Architecture

```
Visitor clicks 🖐️ toggle
   │
   ▼
streamlit-webrtc mounts VideoProcessor  ◀── browser prompts for webcam
   │                                          │ denied → fall back to mouse-only,
   │  frames (≈15 fps on Streamlit Cloud)     │   show red caption
   ▼
dashboard/lib/contagion/gestures.py
   └─ classify_gesture(landmarks, prev_state) ─▶ GestureState
   │
   ▼  (writes to st.session_state)
existing page code (Phase 1):
   - session_state["contagion_date_idx"]       ← scrub gesture writes here
   - session_state["contagion_globe_bearing"]  ← rotate gesture writes here (new)
   - session_state["contagion_globe_zoom"]     ← zoom gesture writes here (new)
```

### New / modified files

| File | Purpose |
|---|---|
| `dashboard/lib/contagion/gestures.py` (new) | Pure classifier — takes a 21-point mediapipe landmark list, returns `GestureState`. No streamlit, no webrtc. |
| `dashboard/lib/contagion/webcam.py` (new) | `VideoProcessorBase` subclass running mediapipe on each frame, calling `gestures.classify_gesture`, pushing the result into session_state. Lazy-imported — never loaded if toggle is off. |
| `dashboard/pages/70_Global_Contagion.py` (modify) | Add the toggle, the playback-speed selector, the "Gestures hidden mode" guard, and make the pydeck ViewState read bearing/zoom from session_state. |
| `dashboard/requirements.txt` (modify) | Add `streamlit-webrtc>=0.50,<0.60` and `mediapipe>=0.10.21,<0.11`. |
| `dashboard/tests/test_contagion_gestures.py` (new) | Classifier unit tests using synthetic landmark fixtures. |
| `dashboard/tests/test_contagion_webcam.py` (new) | Minimal smoke test — module imports when deps available; `importorskip` when not. |
| `dashboard/tests/test_global_contagion.py` (modify) | Add gesture-toggle and playback-speed assertions. |

## Gesture classifier

```python
@dataclass
class GestureState:
    action: Literal["idle", "rotate", "zoom", "scrub"]
    # Per-action payload:
    #   rotate:  delta_longitude (degrees per frame, typically ±5..±20)
    #   zoom:    zoom_multiplier (e.g. 0.9 to zoom out, 1.1 to zoom in)
    #   scrub:   days_delta      (int, typically ±1..±5)
    value: float
```

### Classification rules (first match wins, priority top-down)

1. **Pinch (→ zoom)**: thumb-tip to index-tip Euclidean distance < `PINCH_THRESHOLD`. Pinch closing → zoom in (multiplier 1.1), pinch opening → zoom out (0.9).
2. **Two fingers extended (→ scrub)**: index and middle fingertips extended above the knuckles, ring/pinky curled. Horizontal wrist dx → `days_delta = sign(dx) * round(|dx| * SCRUB_SENSITIVITY)`, capped at ±5 days/frame.
3. **Index extended, thumb down (→ rotate)**: classic pointer pose. Horizontal wrist dx → `delta_longitude = dx * ROTATE_SENSITIVITY`.
4. **Otherwise → idle**.

### Smoothing

A 3-frame exponential moving-average on the wrist `dx` value (before classification) prevents jitter-induced oscillation. The classifier takes `prev_wrist_x` as an argument so the EMA state is threaded through by the webcam adapter.

### Tunable constants

All in `gestures.py`, with sensible defaults:
- `PINCH_THRESHOLD = 0.05` (normalized image coordinates)
- `ROTATE_SENSITIVITY = 60.0` (degrees per unit of wrist travel)
- `SCRUB_SENSITIVITY = 8.0` (day-steps per unit of wrist travel)
- `EMA_WINDOW = 3` (frames)

## Session state schema

All keys prefixed `contagion_` to avoid collisions with other pages.

| Key | Added by | Consumed by | Default |
|---|---|---|---|
| `contagion_date_idx` | Phase 1 slider + scrub gesture | slider block | `len(dates) - 1` |
| `contagion_playing` | Phase 1 play button | auto-advance block | `False` |
| `contagion_playback_speed` | **Phase 2 new** — speed selector | auto-advance sleep timer | `1` (×) |
| `contagion_gestures_enabled` | Phase 2 toggle | webcam mount + rerun loop | `False` |
| `contagion_globe_bearing` | Phase 2 rotate gesture | pydeck ViewState | `0` |
| `contagion_globe_zoom` | Phase 2 zoom gesture | pydeck ViewState | `1.5` |
| `contagion_last_gesture` | Phase 2 webcam processor | debug caption | `"idle"` |

## Page integration

### Toggle + corner preview

When `streamlit_webrtc` + `mediapipe` both import AND neither `?gestures=off` URL param nor `QUANTLAB_GESTURES_HIDDEN=1` env var is set, render the toggle:

```python
if _gestures_available():
    st.toggle(
        "🖐️ Enable gesture control",
        key="contagion_gestures_enabled",
        help="The page works fully without it — mouse + slider + play button. "
             "Only click if you want to wave at your webcam.",
    )
    if st.session_state["contagion_gestures_enabled"]:
        from contagion import webcam  # lazy
        webcam.mount_gesture_stream()  # 240×180 corner preview + processor
        # 10 Hz rerun loop while gestures active
        time.sleep(0.1); st.rerun()
else:
    st.caption("Gesture controls disabled for this view.")
```

### Playback-speed selector

Add a `st.segmented_control` next to the ▶ Play button (same row):

```python
st.segmented_control(
    "Speed", options=[1, 2, 4, 8], format_func=lambda x: f"{x}×",
    default=1, key="contagion_playback_speed", label_visibility="collapsed",
)
```

Auto-advance block maps the speed to sleep intervals:

```python
SPEED_TO_SLEEP = {1: 0.15, 2: 0.075, 4: 0.04, 8: 0.02}
time.sleep(SPEED_TO_SLEEP[st.session_state["contagion_playback_speed"]])
```

### pydeck ViewState reads from session_state

```python
view_state = pdk.ViewState(
    longitude=constants.EPICENTER_LONLAT[0],
    latitude=constants.EPICENTER_LONLAT[1],
    zoom=st.session_state.get("contagion_globe_zoom", 1.5),
    bearing=st.session_state.get("contagion_globe_bearing", 0),
    pitch=0,
)
```

When gestures are off, these keys stay at their defaults and the globe behaves identically to Phase 1.

## Fallback cascade

Each step falls through to the next on failure; the page remains fully functional throughout.

1. `streamlit_webrtc` + `mediapipe` both import → toggle renders
2. User clicks toggle → browser prompts for webcam
3. Permission denied → red caption *"Webcam permission denied — using mouse controls"*, toggle flips back to off
4. Permission granted but no frames within 5 s → same fallback caption, toggle off
5. Either dep missing → toggle never renders; `Gestures hidden mode` caption appears

## Performance guardrails

- Process every other webrtc frame (halves CPU, imperceptible to user at 15 fps input)
- Rerun loop at 10 Hz (100 ms cadence) while gestures active
- Corner preview 240×180, memory-cheap
- mediapipe's ~100 MB cold-start cost only fires when a user opts in — regular visitors get Phase 1 speeds

## Testing

### Classifier (`test_contagion_gestures.py`) — ~15 tests

Synthetic landmark fixtures (`_synth_landmarks(pose)`) for `pinch / point / two_finger / fist / open_hand`. Tests cover:
- Each gesture triggers the expected action
- Priority ordering (pinch-with-index-pointing → zoom, not rotate)
- EMA smoothing reduces jitter
- Out-of-range wrist motion clips to threshold
- Idle returned when no pose matches

### Webcam adapter (`test_contagion_webcam.py`) — 1 test

```python
mediapipe = pytest.importorskip("mediapipe")
streamlit_webrtc = pytest.importorskip("streamlit_webrtc")

def test_mount_gesture_stream_is_callable():
    from lib.contagion import webcam
    assert callable(webcam.mount_gesture_stream)
```

### Page (`test_global_contagion.py` — extends Phase 1)

- `test_gesture_toggle_renders` — a toggle with label containing "gesture" is present (only if deps installed)
- `test_gesture_toggle_off_by_default` — toggle's default value is `False`
- `test_playback_speed_selector_present` — a segmented control with 1/2/4/8 options exists
- `test_hidden_mode_suppresses_toggle` — setting env var or query param hides the toggle and shows the disabled caption

### Not tested

- Real webcam frames, real mediapipe inference, end-to-end pose classification. Requires a mock video source; out of scope for Phase 2. Manual QA checklist on the PR covers this.

## Deployment notes

### Dependencies

Add to `dashboard/requirements.txt`:
```
streamlit-webrtc>=0.50,<0.60
mediapipe>=0.10.21,<0.11
```

### Streamlit Cloud

- HTTPS provided — `getUserMedia` works out of the box
- Cold start increases by mediapipe's ~100 MB download on first-visit-with-gestures; subsequent visits cached
- If webrtc's STUN server negotiation flakes in a given session, the 5-second-no-frames fallback catches it

### Local dev

- `http://localhost` blocks `getUserMedia`. Use `streamlit run --server.sslCertFile ... --server.sslKeyFile ...` with a self-signed cert, or test against the deployed Streamlit Cloud URL.

### Browser matrix

- Chrome 120+ on desktop: full support (primary target)
- Chrome mobile: toggle visible; gestures functional but fiddly; blog post recommends desktop
- Firefox desktop: STUN quirks possible; fallback cascade handles it
- Safari desktop: same as Firefox; fallback cascade handles it

### Blog post

Tech-demo-focused. Title candidate: "Minority Report with Python: mediapipe + streamlit-webrtc + pydeck." Cross-link from the Phase 1 methodology post. Screen-recorded locally (so the gestures demo is not dependent on a live Streamlit Cloud session working when a reader opens the page). Lives in the FinBytes repo at `docs/_posts/`.

## Risks

1. **mediapipe dependency conflicts**: mediapipe pins specific numpy / opencv-python versions. If pip can't resolve against the existing `requirements.txt`, we'll need to relax one of the existing pins. Test with a fresh `pip install -r requirements.txt` before committing.
2. **streamlit-webrtc on Streamlit Cloud flakes in the wild**: the fallback cascade should catch it, but if visitors widely report broken gestures, flip `QUANTLAB_GESTURES_HIDDEN=1` on the Cloud deploy to suppress the toggle while we investigate.
3. **Gesture classifier mis-categorisation**: if in manual QA the priority order (pinch > two-finger > point > idle) produces too many false positives (e.g., pointer gets caught as two-finger during transitions), we revisit the thresholds in a follow-up. Not a blocker for shipping.
4. **Playback speed at 8× may desync the rerun loop**: 20 ms sleep between frames is right at Streamlit's rerun overhead. If 8× frames visibly drop, we cap the selector at 4×. Cheap to change.

## Out of scope reminder

These remain for Phase 3, not this plan:
- Drill-in from aggregated epicenter origin to 3 component arcs on click
- VIX-driven arc glow intensity
- "Top 3 At-Risk Markets" overlay panel
- Key-event preset buttons ("Soleimani strike", "Port attack")
- Any gesture control beyond rotate/zoom/scrub (e.g., palm-push-to-reset)
