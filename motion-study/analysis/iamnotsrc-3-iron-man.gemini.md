<!-- model gemini-3.6-flash, 8.0 fps sampling, generated 2026-10-29 07:50 -->
<!-- source iamnotsrc-3-iron-man.mp4: {'width': 720, 'height': 1280, 'fps': 24.0, 'duration': 15.16} ; ffmpeg cut hints [5.0, 10.0] -->

# iamnotsrc 3 iron man

## 1. Overview
- **Subject:** Iron Man in suit.
- **Setting:** City skyline and sky at sunset/dusk.
- **Time of Day:** Sunset / Dusk.
- **Weather:** Clear with soft atmospheric haze.
- **Mood:** Cinematic superhero action.
- **Color Palette:** Warm orange, golden sunset hues, dark blue sky tones.
- **Clips:** 3 clips.
- **Average Clip Length:** ~5.05 s.
- **Music/Cut Relationship:** Hard cuts locked precisely to 5.0-second musical bar loops.

---

## 2. Clip by clip

### Clip 1 — 00:00.0 to 00:05.0 (5.0 s)
- **Frame:** Iron Man flying horizontally mid-air over city buildings. Medium-wide, eye-level, telephoto lens feel.
- **Subject motion:** linear travel; left→right; real-time fast (thrust flight across city).
- **Camera motion:** tracking (parallel with subject); medium speed.
- **Camera–subject relationship:** Camera tracks matched to suit speed, keeping Iron Man centered while skyline moves beneath.
- **Dynamism sources:** Thruster exhaust glow, passing skyscrapers. Energy: 4.
- **Realism cues:** Smooth motion blur, realistic lighting integration. AI tells: Minor suit surface texture swim. Realism: 4.
- **Would a video model get this right?** "Iron Man flying horizontally over city skyline at sunset, side tracking shot."

---

### Clip 2 — 00:05.0 to 00:10.0 (5.0 s)
- **Frame:** Iron Man flying in formation alongside military fighter jets. Wide shot, long lens, high angle.
- **Subject motion:** linear travel; left→right; very fast.
- **Camera motion:** tracking (parallel with subject); fast.
- **Camera–subject relationship:** Camera tracks alongside jet formation at equal speed against sky gradient.
- **Dynamism sources:** Jet engine afterburners, heat trails, thruster exhaust. Energy: 4.
- **Realism cues:** Jet heat distortion haze, sharp silhouettes. AI tells: Minor wing geometry morphing on jets. Realism: 3.
- **Would a video model get this right?** "Iron Man flying in formation with fighter jets at dusk, tracking shot."

---

### Clip 3 — 00:10.0 to 00:15.1 (5.1 s)
- **Frame:** Iron Man hovering vertically down toward a tall skyscraper rooftop. Medium-wide, slightly low angle.
- **Subject motion:** action; top→bottom (vertical descent to hero pose); real-time fast.
- **Camera motion:** locked off; static.
- **Camera–subject relationship:** Subject enters top of frame, descending to land at center while camera remains fixed.
- **Dynamism sources:** Rooftop exhaust smoke, repulsor light fade. Energy: 3.
- **Realism cues:** Smoke dispersal, ground contact shadow lighting. AI tells: Minor suit silhouette shift upon landing impact. Realism: 4.
- **Would a video model get this right?** "Iron Man hovering down and landing on skyscraper rooftop in superhero pose, static camera."

---

## 3. Structure and rhythm
- **Clip Durations:** [5.0 s, 5.0 s, 5.1 s].
- **Hook:** Immediate visual clarity; Iron Man is centered and moving in frame 1.
- **Screen Direction:** Consistent left-to-right horizontal travel across Clips 1 & 2, transitioning to a vertical downward descent in Clip 3.
- **Stillness:** Subject comes to rest only in Clip 3 upon landing (13.5 s); camera stays static to accentuate ground impact.
- **Energy Curve:** High-speed aerial velocity (Clips 1–2) settling into a stable hero resolution (Clip 3).
- **Ending:** Holds on Iron Man standing firmly on rooftop against the sunset silhouette.

---

## 4. Patterns
1. Maintain consistent dusk color palette across clips for edit cohesion.
2. Match tracking camera speed to fast-moving aerial subjects to keep them centered.
3. Use fixed, locked-off framing for landing sequences to highlight landing impact.
4. Cut exactly on 5.0-second intervals synchronized with soundtrack loops.
5. Utilize thruster glow and exhaust trails to mask background generation artifacts.

---

## 5. Clip table (JSON)

```json
[
  {
    "n": 1,
    "start": 0.0,
    "end": 5.0,
    "subject_motion": "linear travel",
    "direction": "left->right",
    "subject_speed": "real-time fast",
    "camera_motion": "tracking",
    "camera_speed": "medium",
    "relationship": "camera tracks at matched speed keeping subject centered",
    "dynamism": [
      "thruster exhaust",
      "passing skyline"
    ],
    "energy": 4,
    "realism": 4,
    "ai_tells": [
      "suit texture swim"
    ]
  },
  {
    "n": 2,
    "start": 5.0,
    "end": 10.0,
    "subject_motion": "linear travel",
    "direction": "left->right",
    "subject_speed": "very fast",
    "camera_motion": "tracking",
    "camera_speed": "fast",
    "relationship": "camera tracks parallel with jet formation",
    "dynamism": [
      "jet afterburners",
      "heat trails"
    ],
    "energy": 4,
    "realism": 3,
    "ai_tells": [
      "jet wing morphing",
      "thruster flicker"
    ]
  },
  {
    "n": 3,
    "start": 10.0,
    "end": 15.1,
    "subject_motion": "action",
    "direction": "top->bottom",
    "subject_speed": "real-time fast",
    "camera_motion": "locked off",
    "camera_speed": "static",
    "relationship": "subject descends and lands in stationary frame",
    "dynamism": [
      "rooftop smoke",
      "thruster glow fade"
    ],
    "energy": 3,
    "realism": 4,
    "ai_tells": [
      "suit geometry shift on impact"
    ]
  }
]
```