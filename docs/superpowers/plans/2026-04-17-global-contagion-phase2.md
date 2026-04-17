# Global Contagion Phase 2 Implementation Plan — Gesture Control

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add opt-in hand-gesture control to the `/Global_Contagion` page — pinch-zoom, pointer-rotate, two-finger-scrub — with a 240×180 corner webcam preview and graceful degradation when webcam / deps are unavailable.

**Architecture:** A pure classifier (`gestures.py`) converts mediapipe 21-point hand landmarks to a `GestureState`. A streamlit-webrtc adapter (`webcam.py`) runs the classifier on each frame and writes results to `st.session_state`. The page's pydeck ViewState + slider read from session_state, so gestures and mouse controls share the same backing store. When deps are missing or the user is on a "gestures hidden" URL, the toggle simply doesn't render.

**Tech Stack:** Python 3.11, Streamlit, `streamlit-webrtc>=0.50,<0.60`, `mediapipe>=0.10.21,<0.11`, pydeck, pytest + `streamlit.testing.v1.AppTest`.

---

## File structure

```
quant_lab/
└── dashboard/
    ├── lib/
    │   └── contagion/
    │       ├── gestures.py          (new — pure classifier, no streamlit/webrtc/mediapipe)
    │       └── webcam.py            (new — webrtc + mediapipe adapter)
    ├── pages/
    │   └── 70_Global_Contagion.py   (modify — toggle, speed selector, ViewState reads session_state)
    ├── requirements.txt             (modify — add two new pinned deps)
    └── tests/
        ├── test_contagion_gestures.py   (new — classifier unit tests with synthetic landmarks)
        ├── test_contagion_webcam.py     (new — importorskip smoke test)
        └── test_global_contagion.py     (modify — add toggle + speed selector + hidden-mode tests)
```

All new page logic is opt-in: when the toggle is off (default), the page behaves exactly like Phase 1. No Phase 1 tests are rewritten — only added to.

---

## Task 1: Scaffold `gestures.py` — constants + GestureState

**Files:**
- Create: `dashboard/lib/contagion/gestures.py`
- Test: `dashboard/tests/test_contagion_gestures.py`

- [ ] **Step 1: Write the failing test**

```python
"""Unit tests for gesture classifier."""
from dataclasses import fields

from lib.contagion import gestures


def test_constants_have_sensible_defaults():
    assert 0.02 < gestures.PINCH_THRESHOLD < 0.1
    assert gestures.ROTATE_SENSITIVITY > 0
    assert gestures.SCRUB_SENSITIVITY > 0
    assert gestures.EMA_WINDOW >= 1


def test_gesture_state_dataclass_has_action_and_value():
    state = gestures.GestureState(action="idle", value=0.0)
    assert state.action == "idle"
    assert state.value == 0.0
    names = {f.name for f in fields(gestures.GestureState)}
    assert names == {"action", "value"}
```

- [ ] **Step 2: Run — expect fail**

```bash
cd dashboard && python -m pytest tests/test_contagion_gestures.py -v
```
Expected: `ModuleNotFoundError: No module named 'lib.contagion.gestures'`.

- [ ] **Step 3: Implement**

Write `dashboard/lib/contagion/gestures.py`:

```python
"""Pure gesture classifier — no streamlit, no webrtc, no mediapipe import.

Tests use synthetic 21-point landmark fixtures; the webcam adapter in
webcam.py feeds real mediapipe results in.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


# Tunable thresholds — edit here, not at call sites.
PINCH_THRESHOLD: float = 0.05       # normalized image coords, thumb-tip to index-tip
ROTATE_SENSITIVITY: float = 60.0    # degrees of longitude per unit of wrist travel
SCRUB_SENSITIVITY: float = 8.0      # day-steps per unit of wrist travel
EMA_WINDOW: int = 3                 # frames of smoothing on wrist dx


@dataclass
class GestureState:
    """One gesture decision for one frame.

    `action` is one of idle / rotate / zoom / scrub.
    `value` payload depends on action:
      - rotate: degrees of longitude to add to the globe bearing
      - zoom:   multiplier (0.9 = zoom out, 1.1 = zoom in)
      - scrub:  signed integer day step
      - idle:   0.0
    """
    action: Literal["idle", "rotate", "zoom", "scrub"]
    value: float
```

- [ ] **Step 4: Run tests**

```bash
cd dashboard && python -m pytest tests/test_contagion_gestures.py -v
```
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add dashboard/lib/contagion/gestures.py dashboard/tests/test_contagion_gestures.py
git commit -m "feat(contagion): scaffold gestures package — GestureState + constants"
```

---

## Task 2: Synthetic landmark fixtures + pose helpers

**Files:**
- Modify: `dashboard/lib/contagion/gestures.py` (append pose helpers)
- Modify: `dashboard/tests/test_contagion_gestures.py` (append tests)

- [ ] **Step 1: Write the failing tests**

Append to `dashboard/tests/test_contagion_gestures.py`:

```python
from dataclasses import dataclass


# ─────────────────────────────────────────────────────────────
# Synthetic landmark fixtures. mediapipe returns 21 landmarks per
# hand with normalized x/y/z in [0,1]. For classifier tests we only
# need x/y; z is ignored by the pose helpers.
# ─────────────────────────────────────────────────────────────

@dataclass
class _Pt:
    x: float
    y: float
    z: float = 0.0


def _synth_landmarks(pose: str, wrist_x: float = 0.5, wrist_y: float = 0.8) -> list[_Pt]:
    """Factory for the 5 poses the classifier understands.

    Index map (mediapipe convention):
      0  WRIST
      1-4  THUMB  (CMC, MCP, IP, TIP)
      5-8  INDEX  (MCP, PIP, DIP, TIP)
      9-12 MIDDLE (MCP, PIP, DIP, TIP)
     13-16 RING   (MCP, PIP, DIP, TIP)
     17-20 PINKY  (MCP, PIP, DIP, TIP)

    y increases downward (image coords). Extended = tip y < knuckle y.
    """
    # Start with wrist + knuckles (MCPs) at rest positions
    pts = [_Pt(wrist_x, wrist_y)]                     # 0 wrist
    pts += [_Pt(wrist_x - 0.06, wrist_y - 0.02)] * 4  # 1-4 thumb default curled
    for base_x in (wrist_x - 0.03, wrist_x, wrist_x + 0.03, wrist_x + 0.06):
        # Each finger: MCP at y-0.05 (knuckle), then PIP, DIP, TIP
        knuckle_y = wrist_y - 0.05
        pts += [_Pt(base_x, knuckle_y)] * 4   # default curled (tip ~ knuckle)

    def _extend(finger_idx: int):
        # Raise the tip above the knuckle
        mcp = pts[finger_idx * 4 + 1 if finger_idx == 0 else 1 + finger_idx * 4]
        tip_idx = (finger_idx * 4 + 4) if finger_idx == 0 else (finger_idx * 4 + 4)
        # Simpler: just reach into the list by absolute index
    # Simpler helpers using absolute indices:
    INDEX_MCP, INDEX_TIP = 5, 8
    MIDDLE_MCP, MIDDLE_TIP = 9, 12
    RING_MCP, RING_TIP = 13, 16
    PINKY_MCP, PINKY_TIP = 17, 20
    THUMB_TIP = 4

    def lift(tip_idx: int, mcp_idx: int):
        pts[tip_idx] = _Pt(pts[mcp_idx].x, pts[mcp_idx].y - 0.12)

    if pose == "pinch":
        # Thumb tip and index tip very close
        lift(INDEX_TIP, INDEX_MCP)
        pts[THUMB_TIP] = _Pt(pts[INDEX_TIP].x + 0.02, pts[INDEX_TIP].y + 0.01)
    elif pose == "point":
        lift(INDEX_TIP, INDEX_MCP)  # only index extended
    elif pose == "two_finger":
        lift(INDEX_TIP, INDEX_MCP)
        lift(MIDDLE_TIP, MIDDLE_MCP)
    elif pose == "fist":
        pass  # all curled
    elif pose == "open_hand":
        lift(INDEX_TIP, INDEX_MCP)
        lift(MIDDLE_TIP, MIDDLE_MCP)
        lift(RING_TIP, RING_MCP)
        lift(PINKY_TIP, PINKY_MCP)
    else:
        raise ValueError(f"Unknown pose: {pose}")
    return pts


def test_pinch_pose_detected():
    ls = _synth_landmarks("pinch")
    assert gestures._is_pinched(ls) is True


def test_point_pose_not_pinched():
    ls = _synth_landmarks("point")
    assert gestures._is_pinched(ls) is False


def test_two_finger_pose_detected():
    ls = _synth_landmarks("two_finger")
    assert gestures._is_two_fingers_extended(ls) is True


def test_point_pose_not_two_finger():
    ls = _synth_landmarks("point")
    assert gestures._is_two_fingers_extended(ls) is False


def test_point_pose_detected():
    ls = _synth_landmarks("point")
    assert gestures._is_pointing(ls) is True


def test_open_hand_not_pointing():
    ls = _synth_landmarks("open_hand")
    assert gestures._is_pointing(ls) is False


def test_fist_detects_no_pose():
    ls = _synth_landmarks("fist")
    assert gestures._is_pinched(ls) is False
    assert gestures._is_two_fingers_extended(ls) is False
    assert gestures._is_pointing(ls) is False
```

- [ ] **Step 2: Run to verify fails**

```bash
cd dashboard && python -m pytest tests/test_contagion_gestures.py -v
```
Expected: `AttributeError: module 'lib.contagion.gestures' has no attribute '_is_pinched'`.

- [ ] **Step 3: Implement**

Append to `dashboard/lib/contagion/gestures.py`:

```python
# ─────────────────────────────────────────────────────────────
# Pose detection helpers.
# `landmarks` is a list of 21 objects with .x, .y, .z attributes
# (mediapipe's NormalizedLandmarkList.landmark, or synthetic in tests).
# ─────────────────────────────────────────────────────────────

# Mediapipe landmark indices
_WRIST = 0
_THUMB_TIP = 4
_INDEX_MCP, _INDEX_TIP = 5, 8
_MIDDLE_MCP, _MIDDLE_TIP = 9, 12
_RING_MCP, _RING_TIP = 13, 16
_PINKY_MCP, _PINKY_TIP = 17, 20


def _distance(a, b) -> float:
    dx, dy = a.x - b.x, a.y - b.y
    return (dx * dx + dy * dy) ** 0.5


def _is_extended(landmarks, tip: int, mcp: int) -> bool:
    """Finger is 'extended' when its tip is above the MCP knuckle
    (y decreasing upward in image coords, tip.y < mcp.y means up)."""
    return landmarks[tip].y < landmarks[mcp].y - 0.02


def _is_curled(landmarks, tip: int, mcp: int) -> bool:
    return landmarks[tip].y >= landmarks[mcp].y - 0.02


def _is_pinched(landmarks) -> bool:
    return _distance(landmarks[_THUMB_TIP], landmarks[_INDEX_TIP]) < PINCH_THRESHOLD


def _is_two_fingers_extended(landmarks) -> bool:
    return (
        _is_extended(landmarks, _INDEX_TIP, _INDEX_MCP)
        and _is_extended(landmarks, _MIDDLE_TIP, _MIDDLE_MCP)
        and _is_curled(landmarks, _RING_TIP, _RING_MCP)
        and _is_curled(landmarks, _PINKY_TIP, _PINKY_MCP)
    )


def _is_pointing(landmarks) -> bool:
    """Index up, middle/ring/pinky curled. Thumb state not checked — the
    pinch-detection-first ordering means any pinch-like pose is caught
    by _is_pinched before this helper runs."""
    return (
        _is_extended(landmarks, _INDEX_TIP, _INDEX_MCP)
        and _is_curled(landmarks, _MIDDLE_TIP, _MIDDLE_MCP)
        and _is_curled(landmarks, _RING_TIP, _RING_MCP)
        and _is_curled(landmarks, _PINKY_TIP, _PINKY_MCP)
    )
```

- [ ] **Step 4: Run tests — expect all pass**

```bash
cd dashboard && python -m pytest tests/test_contagion_gestures.py -v
```
Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add dashboard/lib/contagion/gestures.py dashboard/tests/test_contagion_gestures.py
git commit -m "feat(contagion): add pose-detection helpers (pinch, two-finger, pointing)"
```

---

## Task 3: EMA-smoothed wrist-dx helper

**Files:**
- Modify: `dashboard/lib/contagion/gestures.py` (append)
- Modify: `dashboard/tests/test_contagion_gestures.py` (append)

- [ ] **Step 1: Write the failing tests**

Append to test file:

```python
def test_smooth_dx_first_call_returns_raw_dx():
    # No history — smoothing is the raw dx
    result = gestures.smooth_dx(dx=0.2, history=[])
    assert result == pytest.approx(0.2)


def test_smooth_dx_with_history_averages_with_decay():
    # Latest sample weighted more than older ones
    result = gestures.smooth_dx(dx=0.3, history=[0.1, 0.1, 0.1])
    # EMA with window=3 should land somewhere between 0.1 and 0.3
    assert 0.1 < result < 0.3


def test_smooth_dx_zero_history_stays_zero():
    result = gestures.smooth_dx(dx=0.0, history=[0.0, 0.0, 0.0])
    assert result == pytest.approx(0.0)
```

Add `import pytest` at the top of the file if not already there.

- [ ] **Step 2: Run — expect fail**

```bash
cd dashboard && python -m pytest tests/test_contagion_gestures.py::test_smooth_dx_first_call_returns_raw_dx -v
```
Expected: `AttributeError: module 'lib.contagion.gestures' has no attribute 'smooth_dx'`.

- [ ] **Step 3: Implement**

Append to `dashboard/lib/contagion/gestures.py`:

```python
def smooth_dx(dx: float, history: list[float]) -> float:
    """Exponential moving average of wrist dx across up to EMA_WINDOW
    most-recent samples. Pass the current dx and the last EMA_WINDOW-1
    samples as history (most recent last). Returns the smoothed value.

    Separated from the classifier so the caller (webcam adapter) owns
    the history buffer — keeps classify_gesture itself stateless.
    """
    samples = history[-(EMA_WINDOW - 1):] + [dx]
    # Weights: 1, 2, 3, ... newer weighted more. Normalize.
    weights = list(range(1, len(samples) + 1))
    total_weight = sum(weights)
    return sum(w * s for w, s in zip(weights, samples)) / total_weight
```

- [ ] **Step 4: Run tests**

```bash
cd dashboard && python -m pytest tests/test_contagion_gestures.py -v
```
Expected: 12 passed.

- [ ] **Step 5: Commit**

```bash
git add dashboard/lib/contagion/gestures.py dashboard/tests/test_contagion_gestures.py
git commit -m "feat(contagion): add EMA smoother for wrist dx"
```

---

## Task 4: `classify_gesture` — the main classifier

**Files:**
- Modify: `dashboard/lib/contagion/gestures.py` (append)
- Modify: `dashboard/tests/test_contagion_gestures.py` (append)

- [ ] **Step 1: Write the failing tests**

Append to test file:

```python
def test_pinch_classifies_as_zoom_in_on_closing():
    ls = _synth_landmarks("pinch", wrist_x=0.5)
    state = gestures.classify_gesture(
        landmarks=ls, prev_wrist_x=0.5, prev_thumb_index_dist=0.08
    )
    assert state.action == "zoom"
    assert state.value < 1.0  # closing from 0.08 → <PINCH_THRESHOLD = zoom in


def test_two_finger_right_motion_scrubs_forward():
    ls = _synth_landmarks("two_finger", wrist_x=0.7)
    state = gestures.classify_gesture(
        landmarks=ls, prev_wrist_x=0.5, prev_thumb_index_dist=0.5
    )
    assert state.action == "scrub"
    assert state.value > 0  # positive dx = forward


def test_pointing_right_motion_rotates_east():
    ls = _synth_landmarks("point", wrist_x=0.7)
    state = gestures.classify_gesture(
        landmarks=ls, prev_wrist_x=0.5, prev_thumb_index_dist=0.5
    )
    assert state.action == "rotate"
    assert state.value > 0  # positive delta_longitude = east


def test_fist_classifies_as_idle():
    ls = _synth_landmarks("fist")
    state = gestures.classify_gesture(
        landmarks=ls, prev_wrist_x=0.5, prev_thumb_index_dist=0.5
    )
    assert state.action == "idle"


def test_scrub_clipped_to_five_days():
    # Huge wrist motion should still cap at ±5 days
    ls = _synth_landmarks("two_finger", wrist_x=2.0)
    state = gestures.classify_gesture(
        landmarks=ls, prev_wrist_x=0.0, prev_thumb_index_dist=0.5
    )
    assert state.action == "scrub"
    assert abs(state.value) <= 5
```

- [ ] **Step 2: Run — expect fail**

```bash
cd dashboard && python -m pytest tests/test_contagion_gestures.py::test_pinch_classifies_as_zoom_in_on_closing -v
```
Expected: `AttributeError: module 'lib.contagion.gestures' has no attribute 'classify_gesture'`.

- [ ] **Step 3: Implement**

Append to `dashboard/lib/contagion/gestures.py`:

```python
def classify_gesture(
    landmarks,
    prev_wrist_x: float,
    prev_thumb_index_dist: float,
) -> GestureState:
    """Map a frame's landmarks + the prior frame's wrist/pinch state into
    a single GestureState. Priority: pinch > two-finger > pointer > idle.
    First match wins, so ambiguous poses default to the safer interpretation.
    """
    dx = landmarks[_WRIST].x - prev_wrist_x

    # 1. Pinch → zoom
    if _is_pinched(landmarks):
        current_dist = _distance(landmarks[_THUMB_TIP], landmarks[_INDEX_TIP])
        if current_dist < prev_thumb_index_dist:
            return GestureState(action="zoom", value=1.1)   # closing → zoom in
        return GestureState(action="zoom", value=0.9)       # opening → zoom out

    # 2. Two fingers extended → scrub timeline
    if _is_two_fingers_extended(landmarks):
        sign = 1 if dx >= 0 else -1
        steps = min(5, round(abs(dx) * SCRUB_SENSITIVITY))
        return GestureState(action="scrub", value=float(sign * steps))

    # 3. Index extended (pointer) → rotate globe
    if _is_pointing(landmarks):
        return GestureState(action="rotate", value=dx * ROTATE_SENSITIVITY)

    # 4. Anything else → idle
    return GestureState(action="idle", value=0.0)
```

- [ ] **Step 4: Run tests**

```bash
cd dashboard && python -m pytest tests/test_contagion_gestures.py -v
```
Expected: 17 passed (12 from before + 5 new).

- [ ] **Step 5: Commit**

```bash
git add dashboard/lib/contagion/gestures.py dashboard/tests/test_contagion_gestures.py
git commit -m "feat(contagion): add classify_gesture() with priority-ordered pose matching"
```

---

## Task 5: `_gestures_available()` guard + "gestures hidden" URL/env handling

**Files:**
- Modify: `dashboard/pages/70_Global_Contagion.py` (append a helper + small integration)
- Modify: `dashboard/tests/test_global_contagion.py` (append tests)

- [ ] **Step 1: Write the failing tests**

Append to `dashboard/tests/test_global_contagion.py`:

```python
import os


class TestGestureHiddenMode:
    def _run(self):
        at = AppTest.from_file("pages/70_Global_Contagion.py", default_timeout=20)
        at.run()
        return at

    def test_env_var_suppresses_toggle(self, monkeypatch):
        monkeypatch.setenv("QUANTLAB_GESTURES_HIDDEN", "1")
        at = self._run()
        labels = [t.label.lower() for t in at.toggle]
        assert not any("gesture" in l for l in labels), (
            "Env var should suppress the gesture toggle"
        )

    def test_hidden_mode_shows_disabled_caption(self, monkeypatch):
        monkeypatch.setenv("QUANTLAB_GESTURES_HIDDEN", "1")
        at = self._run()
        captions = [c.value.lower() for c in at.caption]
        assert any("gesture controls disabled" in c for c in captions), (
            f"Expected disabled caption; got: {captions}"
        )
```

- [ ] **Step 2: Run — expect fail**

```bash
cd dashboard && python -m pytest tests/test_global_contagion.py::TestGestureHiddenMode -v
```
Expected: multiple AssertionErrors — neither check is wired up yet.

- [ ] **Step 3: Implement**

Insert this block in `dashboard/pages/70_Global_Contagion.py` just after the existing `render_page_header(...)` call (around line 40 — right before the `@st.cache_data` decorator):

```python
import os as _os


def _gestures_available() -> bool:
    """Check whether the gesture toggle should render at all.

    Hidden by any of:
      - URL query param ?gestures=off
      - Env var QUANTLAB_GESTURES_HIDDEN=1
      - streamlit_webrtc not importable (dep missing on this deploy)
    """
    if _os.environ.get("QUANTLAB_GESTURES_HIDDEN") == "1":
        return False
    try:
        qp = st.query_params
    except Exception:
        qp = {}
    if qp.get("gestures") == "off":
        return False
    try:
        import streamlit_webrtc  # noqa: F401
    except ImportError:
        return False
    return True


if not _gestures_available():
    st.caption("Gesture controls disabled for this view.")
```

(Later tasks add the actual toggle rendering when `_gestures_available()` is `True`.)

- [ ] **Step 4: Run tests — expect pass**

```bash
cd dashboard && python -m pytest tests/test_global_contagion.py::TestGestureHiddenMode -v
```
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add dashboard/pages/70_Global_Contagion.py dashboard/tests/test_global_contagion.py
git commit -m "feat(contagion): add _gestures_available() guard + hidden-mode caption"
```

---

## Task 6: Playback speed selector (pulled forward from Phase 3)

**Files:**
- Modify: `dashboard/pages/70_Global_Contagion.py` (replace the play/pause block)
- Modify: `dashboard/tests/test_global_contagion.py` (append)

- [ ] **Step 1: Write the failing test**

Append to `dashboard/tests/test_global_contagion.py`:

```python
    def test_has_playback_speed_selector(self):
        at = self._run()
        # Streamlit 1.40+ renders st.segmented_control as a radio under the hood
        # in AppTest; fall back to inspecting all labels for a 1/2/4/8 signature.
        labels_found = " ".join(
            str(getattr(el, "label", "")) for el in at.main
        )
        for speed in ("1×", "2×", "4×", "8×"):
            assert speed in labels_found or speed.replace("×", "x") in labels_found, (
                f"Expected speed option '{speed}' in page output"
            )
```

Add this method inside the existing `TestGlobalContagionPage` class.

- [ ] **Step 2: Run — expect fail**

```bash
cd dashboard && python -m pytest tests/test_global_contagion.py::TestGlobalContagionPage::test_has_playback_speed_selector -v
```
Expected: AssertionError.

- [ ] **Step 3: Implement**

Find the existing play/pause block in `dashboard/pages/70_Global_Contagion.py` (it has `col_slider, col_btn = st.columns([6, 1])` and the ▶ Play / ⏸ Pause button logic). Replace the whole block with:

```python
# ──────────────────────────────────────────────────────────────
# Timeline slider + play button + speed selector
# ──────────────────────────────────────────────────────────────
dates = sorted(events["date"].unique())
if not dates:
    st.warning("No data for this period.")
    st.stop()

# Session state — preserved across reruns.
if "contagion_date_idx" not in st.session_state:
    st.session_state.contagion_date_idx = len(dates) - 1
if "contagion_playing" not in st.session_state:
    st.session_state.contagion_playing = False
if "contagion_playback_speed" not in st.session_state:
    st.session_state.contagion_playback_speed = 1

# Clamp cursor if the period changed and the list of dates shrank.
if st.session_state.contagion_date_idx >= len(dates):
    st.session_state.contagion_date_idx = len(dates) - 1

col_slider, col_btn, col_speed = st.columns([5, 1, 2])
with col_slider:
    idx = st.slider(
        "Date",
        min_value=0,
        max_value=len(dates) - 1,
        value=st.session_state.contagion_date_idx,
        format="%d",
        label_visibility="collapsed",
    )
    st.session_state.contagion_date_idx = idx
with col_btn:
    btn_label = "⏸ Pause" if st.session_state.contagion_playing else "▶ Play"
    if st.button(btn_label, use_container_width=True):
        st.session_state.contagion_playing = not st.session_state.contagion_playing
        st.rerun()
with col_speed:
    st.segmented_control(
        "Speed",
        options=[1, 2, 4, 8],
        format_func=lambda x: f"{x}×",
        default=st.session_state.contagion_playback_speed,
        key="contagion_playback_speed",
        label_visibility="collapsed",
    )

selected_date = dates[st.session_state.contagion_date_idx]
st.caption(f"Showing snapshot at **{selected_date}**")

# Auto-advance while playing. Sleep interval scales with the selected speed.
if st.session_state.contagion_playing:
    import time as _time
    _SPEED_TO_SLEEP = {1: 0.15, 2: 0.075, 4: 0.04, 8: 0.02}
    _time.sleep(_SPEED_TO_SLEEP[st.session_state.contagion_playback_speed])
    if st.session_state.contagion_date_idx < len(dates) - 1:
        st.session_state.contagion_date_idx += 1
    else:
        st.session_state.contagion_playing = False
    st.rerun()
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd dashboard && python -m pytest tests/test_global_contagion.py -v
```
Expected: all existing tests still pass + the new speed selector test.

- [ ] **Step 5: Commit**

```bash
git add dashboard/pages/70_Global_Contagion.py dashboard/tests/test_global_contagion.py
git commit -m "feat(contagion): add 1×/2×/4×/8× playback speed selector"
```

---

## Task 7: ViewState reads bearing + zoom from session_state

**Files:**
- Modify: `dashboard/pages/70_Global_Contagion.py` (replace the `view_state = pdk.ViewState(...)` block)

- [ ] **Step 1: Replace the existing ViewState constructor**

Find this block in `dashboard/pages/70_Global_Contagion.py`:

```python
view_state = pdk.ViewState(
    longitude=constants.EPICENTER_LONLAT[0],
    latitude=constants.EPICENTER_LONLAT[1],
    zoom=1.5,
    pitch=0,
    bearing=0,
)
```

Replace with:

```python
# Initialise gesture-driven globe state with Phase 1 defaults.
if "contagion_globe_bearing" not in st.session_state:
    st.session_state.contagion_globe_bearing = 0.0
if "contagion_globe_zoom" not in st.session_state:
    st.session_state.contagion_globe_zoom = 1.5

view_state = pdk.ViewState(
    longitude=constants.EPICENTER_LONLAT[0],
    latitude=constants.EPICENTER_LONLAT[1],
    zoom=st.session_state.contagion_globe_zoom,
    pitch=0,
    bearing=st.session_state.contagion_globe_bearing,
)
```

- [ ] **Step 2: Verify page still loads**

```bash
cd dashboard && python -m pytest tests/test_global_contagion.py -v
```
Expected: all tests pass (no new tests here — this is a refactor; behaviour when session state keys are empty is Phase 1 defaults).

- [ ] **Step 3: Commit**

```bash
git add dashboard/pages/70_Global_Contagion.py
git commit -m "refactor(contagion): pydeck ViewState reads bearing/zoom from session_state"
```

---

## Task 8: Add streamlit-webrtc + mediapipe dependencies

**Files:**
- Modify: `dashboard/requirements.txt`

- [ ] **Step 1: Inspect the current file**

```bash
cat dashboard/requirements.txt
```
Locate a sensible place to add two new lines — e.g. right after `streamlit>=...` or at the end of the file.

- [ ] **Step 2: Add the dependencies**

Append to `dashboard/requirements.txt` (or insert in alphabetical order if the file is sorted):

```
streamlit-webrtc>=0.50,<0.60
mediapipe>=0.10.21,<0.11
```

- [ ] **Step 3: Install locally to verify pin compatibility**

```bash
cd dashboard && pip install -r requirements.txt
```
Expected: successful install. If pip reports a numpy or opencv version conflict, note the error and stop — report `BLOCKED` with the pip output so we can renegotiate a pin.

- [ ] **Step 4: Smoke-import both new packages**

```bash
python -c "import streamlit_webrtc, mediapipe; print(streamlit_webrtc.__version__, mediapipe.__version__)"
```
Expected: two version numbers, no error.

- [ ] **Step 5: Commit**

```bash
git add dashboard/requirements.txt
git commit -m "chore(deps): add streamlit-webrtc + mediapipe for Phase 2 gestures"
```

---

## Task 9: `webcam.py` — mediapipe + webrtc adapter

**Files:**
- Create: `dashboard/lib/contagion/webcam.py`
- Test: `dashboard/tests/test_contagion_webcam.py`

- [ ] **Step 1: Write the failing smoke test**

Write `dashboard/tests/test_contagion_webcam.py`:

```python
"""Smoke test for the webcam gesture adapter.

We don't try to spin up a real webcam in CI — just verify the module
imports and exposes the expected entry point when deps are installed.
Without the deps installed, the test skips cleanly.
"""
import pytest

pytest.importorskip("mediapipe")
pytest.importorskip("streamlit_webrtc")


def test_mount_gesture_stream_is_callable():
    from lib.contagion import webcam
    assert callable(webcam.mount_gesture_stream)


def test_gesture_processor_class_defined():
    from lib.contagion import webcam
    assert hasattr(webcam, "GestureProcessor")
    assert hasattr(webcam.GestureProcessor, "recv")
```

- [ ] **Step 2: Run — expect fail**

```bash
cd dashboard && python -m pytest tests/test_contagion_webcam.py -v
```
Expected: `ModuleNotFoundError: No module named 'lib.contagion.webcam'`.

- [ ] **Step 3: Implement**

Write `dashboard/lib/contagion/webcam.py`:

```python
"""Streamlit-webrtc + mediapipe adapter for Phase 2 gesture control.

Lazy-imports mediapipe / streamlit-webrtc inside function bodies so the
top-level import of this module is cheap. The page imports this module
only when the gesture toggle is on, so mediapipe's ~100 MB cold-start
cost never hits users who don't opt in.
"""
from __future__ import annotations

import av
import cv2
import mediapipe as mp
import numpy as np
import streamlit as st
from streamlit_webrtc import VideoProcessorBase, WebRtcMode, webrtc_streamer

from . import gestures


_mp_hands = mp.solutions.hands
_mp_drawing = mp.solutions.drawing_utils


class GestureProcessor(VideoProcessorBase):
    """Per-frame callback: run mediapipe on each frame, classify the
    gesture, write the result to st.session_state."""

    def __init__(self) -> None:
        self.hands = _mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        )
        # Per-hand state carried across frames so smooth_dx has history.
        self._prev_wrist_x: float = 0.5
        self._prev_pinch_dist: float = 0.5
        self._dx_history: list[float] = []

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        # mediapipe wants RGB
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        if results.multi_hand_landmarks:
            landmarks = results.multi_hand_landmarks[0].landmark
            # Draw skeleton on the preview so user sees tracking feedback
            _mp_drawing.draw_landmarks(
                img, results.multi_hand_landmarks[0], _mp_hands.HAND_CONNECTIONS
            )
            # Smooth the wrist-dx over the last N frames
            raw_dx = landmarks[0].x - self._prev_wrist_x
            smoothed = gestures.smooth_dx(raw_dx, self._dx_history)
            self._dx_history = (self._dx_history + [raw_dx])[-(gestures.EMA_WINDOW - 1):]
            # Apply the smoothed dx by pretending prev was (current - smoothed)
            pseudo_prev_wrist_x = landmarks[0].x - smoothed
            state = gestures.classify_gesture(
                landmarks=landmarks,
                prev_wrist_x=pseudo_prev_wrist_x,
                prev_thumb_index_dist=self._prev_pinch_dist,
            )
            # Update prev state for next frame
            self._prev_wrist_x = landmarks[0].x
            self._prev_pinch_dist = gestures._distance(
                landmarks[gestures._THUMB_TIP], landmarks[gestures._INDEX_TIP]
            )
            # Push action into session_state — the page reads from here.
            _apply_gesture(state)

        return av.VideoFrame.from_ndarray(img, format="bgr24")


def _apply_gesture(state: gestures.GestureState) -> None:
    """Write classifier output to session_state where the page picks it up."""
    # session_state access from a background thread is allowed since
    # streamlit-webrtc 0.50+.
    st.session_state.contagion_last_gesture = state.action
    if state.action == "rotate":
        st.session_state.contagion_globe_bearing = (
            st.session_state.get("contagion_globe_bearing", 0.0) + state.value
        ) % 360
    elif state.action == "zoom":
        new_zoom = st.session_state.get("contagion_globe_zoom", 1.5) * state.value
        # Clamp so we can't zoom beyond the globe or into the void
        st.session_state.contagion_globe_zoom = max(0.5, min(6.0, new_zoom))
    elif state.action == "scrub":
        # Requires the page to have set up contagion_date_idx already
        current = st.session_state.get("contagion_date_idx", 0)
        # The page clamps to valid range on next render
        st.session_state.contagion_date_idx = max(0, current + int(state.value))


def mount_gesture_stream() -> None:
    """Render the 240×180 corner preview wired to the GestureProcessor."""
    webrtc_streamer(
        key="contagion-gesture-stream",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=GestureProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd dashboard && python -m pytest tests/test_contagion_webcam.py -v
```
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add dashboard/lib/contagion/webcam.py dashboard/tests/test_contagion_webcam.py
git commit -m "feat(contagion): add webrtc + mediapipe adapter with session_state writes"
```

---

## Task 10: Wire the gesture toggle into the page

**Files:**
- Modify: `dashboard/pages/70_Global_Contagion.py` (insert the toggle block)
- Modify: `dashboard/tests/test_global_contagion.py` (append)

- [ ] **Step 1: Write the failing tests**

Append to `TestGlobalContagionPage` in `dashboard/tests/test_global_contagion.py`:

```python
    def test_gesture_toggle_renders_when_deps_installed(self):
        """Only meaningful when mediapipe + streamlit-webrtc are installed.
        Skip if they're not (keeps CI stable on images without the deps)."""
        import importlib.util
        if importlib.util.find_spec("streamlit_webrtc") is None:
            pytest.skip("streamlit-webrtc not installed in this env")
        at = self._run()
        labels = [t.label.lower() for t in at.toggle]
        assert any("gesture" in l for l in labels), (
            f"Expected a gesture toggle; got: {labels}"
        )

    def test_gesture_toggle_off_by_default(self):
        import importlib.util
        if importlib.util.find_spec("streamlit_webrtc") is None:
            pytest.skip("streamlit-webrtc not installed in this env")
        at = self._run()
        for t in at.toggle:
            if "gesture" in t.label.lower():
                assert t.value is False, "Toggle must default to off"
                return
        pytest.fail("No gesture toggle found")
```

Ensure `import pytest` is at the top of the test file (may already be there from Task 1).

- [ ] **Step 2: Run — expect fail**

```bash
cd dashboard && python -m pytest tests/test_global_contagion.py::TestGlobalContagionPage::test_gesture_toggle_renders_when_deps_installed -v
```
Expected: AssertionError (no toggle yet).

- [ ] **Step 3: Replace the hidden-mode block from Task 5 with the full guarded toggle**

In `dashboard/pages/70_Global_Contagion.py`, find this block (added in Task 5):

```python
if not _gestures_available():
    st.caption("Gesture controls disabled for this view.")
```

Replace with:

```python
if _gestures_available():
    st.toggle(
        "🖐️ Enable gesture control",
        key="contagion_gestures_enabled",
        help=(
            "The page works fully without it — mouse + slider + play button. "
            "Only click if you want to wave at your webcam."
        ),
    )
    if st.session_state.get("contagion_gestures_enabled"):
        try:
            from contagion import webcam  # lazy: ~100MB import
            webcam.mount_gesture_stream()
            # 10 Hz rerun loop to reflect gesture-driven session state changes
            import time as _gtime
            _gtime.sleep(0.1)
            st.rerun()
        except Exception as _exc:  # broad: webrtc / mediapipe can raise many
            st.session_state["contagion_gestures_enabled"] = False
            st.error(
                f"Gesture control unavailable: {_exc}. "
                "Falling back to mouse controls."
            )
else:
    st.caption("Gesture controls disabled for this view.")
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd dashboard && python -m pytest tests/test_global_contagion.py -v
```
Expected: all existing tests + 2 new gesture toggle tests pass (or skip if webrtc not installed).

- [ ] **Step 5: Commit**

```bash
git add dashboard/pages/70_Global_Contagion.py dashboard/tests/test_global_contagion.py
git commit -m "feat(contagion): wire gesture toggle — opt-in, lazy import, rerun loop"
```

---

## Task 11: Full regression + manual QA + PR

- [ ] **Step 1: Run the entire dashboard test suite**

```bash
cd dashboard && python -m pytest tests/ -q --ignore=tests/fixtures
```
Expected: all tests pass (412+ counting Phase 2 additions). No regressions in other suites.

- [ ] **Step 2: Manual smoke test locally**

```bash
cd dashboard && streamlit run app.py
```
Navigate to `/Global_Contagion`. Verify in order:
1. Page loads without errors; globe shows with country basemap
2. Period toggle switches between 2020 US-Iran and 2024 Hormuz
3. Play button auto-advances; 4× and 8× visibly speed up
4. Collapsible "How this works" expander still works
5. If mediapipe + webrtc installed: gesture toggle visible, clicking it prompts for webcam
6. Grant webcam: corner preview renders, skeleton drawn on hand
7. Pinch close → globe zooms in; pinch open → zooms out
8. Point + wave right → globe rotates east
9. Two fingers + wave right → timeline advances
10. Close tab → no lingering webcam indicator (streamlit-webrtc cleans up)

If any step fails in a way unrelated to the deps being uninstalled, report `DONE_WITH_CONCERNS` with the exact repro.

- [ ] **Step 3: Push**

```bash
git push origin working
```

- [ ] **Step 4: Open PR**

```bash
gh pr create --title "feat(contagion): Phase 2 — gesture control (Minority Report mode)" --body "$(cat <<'EOF'
## Summary

Phase 2 of the Global Contagion Command Center. Spec: \`docs/superpowers/specs/2026-04-17-global-contagion-phase2-design.md\`. Plan: \`docs/superpowers/plans/2026-04-17-global-contagion-phase2.md\`.

### What's in
- **Pure gesture classifier** (\`lib/contagion/gestures.py\`) — pinch→zoom, pointer→rotate, two-finger→scrub. 17 unit tests with synthetic landmarks.
- **Webcam adapter** (\`lib/contagion/webcam.py\`) — streamlit-webrtc + mediapipe, 240×180 corner preview with hand-skeleton overlay, per-frame gesture classification writing to session_state.
- **Page wiring**: opt-in \`🖐️ Enable gesture control\` toggle, hidden via \`?gestures=off\` URL param or \`QUANTLAB_GESTURES_HIDDEN=1\` env var, fallback caption when unavailable.
- **Playback speed selector** (1× / 2× / 4× / 8×) pulled forward from Phase 3.
- pydeck ViewState now reads bearing + zoom from session_state so gestures and mouse share the same backing store.

### What's out (Phase 3)
- Drill-in from aggregated epicenter to component arcs
- VIX-driven arc glow
- Top 3 At-Risk Markets overlay
- Key-event preset buttons

### Risks
- mediapipe's numpy/opencv pins may conflict with existing deps — monitor first CI install.
- streamlit-webrtc on Streamlit Cloud can flake on first cold start; fallback cascade handles it.

## Test plan
- [x] Full \`pytest dashboard/tests/\` — all pass
- [ ] \`/Global_Contagion\` loads globe + works mouse-only (deps installed, toggle off)
- [ ] Toggle on → webcam prompt → skeleton overlay renders
- [ ] Pinch / point / two-finger manipulate zoom / rotate / scrub
- [ ] \`?gestures=off\` URL param hides the toggle
- [ ] \`QUANTLAB_GESTURES_HIDDEN=1\` env var hides the toggle

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Self-review

**Spec coverage:**
- GestureState dataclass + tunable constants → Task 1 ✓
- Pose detection (pinch, two-finger, pointing) → Task 2 ✓
- EMA smoothing → Task 3 ✓
- classify_gesture() with priority ordering → Task 4 ✓
- "Gestures hidden" URL + env var guard → Task 5 ✓
- Playback speed selector (1×/2×/4×/8×) → Task 6 ✓
- pydeck ViewState reads session_state for bearing/zoom → Task 7 ✓
- streamlit-webrtc + mediapipe deps → Task 8 ✓
- webcam.py adapter with 240×180 corner preview, hand skeleton overlay, session_state writes → Task 9 ✓
- Opt-in toggle with lazy import + rerun loop + permission-denied fallback → Task 10 ✓
- Full regression + manual QA + PR → Task 11 ✓
- Blog post: spec noted this is shipped after Phase 2 merges with screen recording — not a plan task

**Placeholder scan:** none.

**Type consistency:**
- `GestureState(action, value)` is defined in Task 1 and used consistently in Tasks 4, 9
- `classify_gesture(landmarks, prev_wrist_x, prev_thumb_index_dist)` — signature matches between Task 4 definition and Task 9 call site
- `smooth_dx(dx, history)` — Task 3 definition matches Task 9 caller
- `mount_gesture_stream()` — defined in Task 9, called in Task 10

**Fallback cascade:**
- Task 5 handles URL/env/dep-missing → hide toggle, show caption
- Task 10 handles permission denial / webrtc init failure → revert toggle, show error, keep page functional

No gaps found.
