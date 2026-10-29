<!-- model gemini-3.6-flash, 8.0 fps sampling, generated 2026-10-29 07:48 -->
<!-- source iamnotsrc-5-ghost-rider.mp4: {'width': 720, 'height': 1280, 'fps': 24.0, 'duration': 15.462} ; ffmpeg cut hints [7.17] -->

# iamnotsrc 5 ghost rider

## 1. Overview
- **Subject:** Ghost Rider riding a flaming motorcycle.
- **Setting:** Desert highway framed by distant mountains.
- **Time of day / Weather:** Dusk / sunset twilight under clear skies.
- **Mood:** Cinematic, high-octane, supernatural.
- **Colour palette:** High-contrast orange/yellow fire against dark silhouettes and muted twilight blues/pinks.
- **Clips:** 2 clips.
- **Average clip length:** ~7.6 seconds.
- **Music/Cut relationship:** Hard cut aligns with an audio drop/beat transition around 07.125 s.

---

## 2. Clip by clip

### Clip 1 — 00:00.000 to 00:07.125 (7.125 s)
- **Frame:** Medium-wide side shot at low camera height showing Ghost Rider riding leftward against dusk horizon.
- **Subject motion:** Linear travel to the left; real-time fast speed.
- **Camera motion:** Tracking parallel with subject at matched speed.
- **Camera–subject relationship:** Camera tracks matched speed, keeping subject locked in frame center while background scrolls.
- **Dynamism sources:** Flaming skull head, rear wheel ablaze, ground fire trail, streaming coat, fluttering sparks. Energy: 4/5.
- **Realism cues:** Fire illumination on chassis and road; subtle wheel blur. AI tells: rigid flame structure and slight wheel jitter. Realism: 4/5.
- **Would a video model get this right?** Yes, straightforward prompt: "Side tracking shot of Ghost Rider riding motorcycle on highway at dusk."

### Clip 2 — 00:07.125 to 00:15.250 (8.125 s)
- **Frame:** Low-angle wide rear shot centered on a straight highway with Ghost Rider receding into the distance.
- **Subject motion:** Linear travel directly away from camera; real-time fast speed.
- **Camera motion:** Locked off ground-level shot.
- **Camera–subject relationship:** Subject moves away from stationary camera, shrinking in frame while leaving a long flame trail.
- **Dynamism sources:** Flaming skull, bright continuous trail of fire on asphalt, flying embers drifting towards camera. Energy: 4/5.
- **Realism cues:** Perspective convergence, flame glow reflection on pavement. AI tells: sparks float off road texture without generating smoke. Realism: 4/5.
- **Would a video model get this right?** Yes, simple prompt: "Low angle rear shot of Ghost Rider speeding away on desert road leaving fire trail."

---

## 3. Structure and rhythm
- **Clip durations:** 7.125 s, 8.125 s.
- **Hook:** Immediate visual impact with flaming skull and tire fire active in frame 1.
- **Screen direction:** Transitions from horizontal profile motion (left) to axial receding motion away from camera.
- **Standing still:** Subject never stops; maintains high speed throughout.
- **Energy curve:** Sustained high energy throughout, fading visually as rider recedes into distant horizon.

---

## 4. Patterns
1. Pair dark silhouettes against high-luminance particle effects (fire/sparks) for strong visual impact.
2. Cut between simple, clean angles (side profile tracking to rear center axial view).
3. Align camera motion smoothly with subject vector (matched tracking or locked off).
4. Utilize twilight backlighting to maximize flame vibrancy.

---

## 5. Clip table (JSON)

```json
[
  {
    "n": 1,
    "start": 0.0,
    "end": 7.125,
    "subject_motion": "linear travel",
    "direction": "left",
    "subject_speed": "real-time fast",
    "camera_motion": "tracking",
    "camera_speed": "fast",
    "relationship": "camera tracks at matched speed keeping subject stationary in frame",
    "dynamism": ["flaming skull", "burning rear wheel", "ground sparks", "flapping coat"],
    "energy": 4,
    "realism": 4,
    "ai_tells": ["rigid flame geometry", "minor wheel jitter"]
  },
  {
    "n": 2,
    "start": 7.125,
    "end": 15.25,
    "subject_motion": "linear travel",
    "direction": "away",
    "subject_speed": "real-time fast",
    "camera_motion": "locked off",
    "camera_speed": "static",
    "relationship": "subject moves away from still camera receding into distance",
    "dynamism": ["flame trail on asphalt", "flying sparks", "glowing embers"],
    "energy": 4,
    "realism": 4,
    "ai_tells": ["lack of smoke from fire trail", "floating embers"]
  }
]
```