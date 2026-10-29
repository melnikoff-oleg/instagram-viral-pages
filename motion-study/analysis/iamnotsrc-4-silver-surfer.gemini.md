<!-- model gemini-3.6-flash, 8.0 fps sampling, generated 2026-10-29 07:51 -->
<!-- source iamnotsrc-4-silver-surfer.mp4: {'width': 720, 'height': 1280, 'fps': 24.0, 'duration': 15.206} ; ffmpeg cut hints [7.08] -->

# iamnotsrc 4 silver surfer

## 1. Overview
- **Subject:** Silver Surfer performing maneuvers on a surfboard in space.
- **Setting:** Low planetary orbit above a glowing atmospheric layer.
- **Lighting & Mood:** High-contrast, cinematic sci-fi; dark space contrasted with brilliant golden-orange planetary glow.
- **Colour Palette:** Metallic silver, deep black, bright orange/gold glow.
- **Clips:** 3 clips (Clip 2 is a repeat loop of Clip 1).
- **Average Clip Length:** ~5.1 seconds.
- **Music/Cut Relationship:** Cuts align with beat drops in the soundtrack.

---

## 2. Clip by clip

### Clip 1 — 00:00.0 to 00:03.5 (3.5 s)
- **Frame:** Medium shot, side profile; wide-angle space scene with atmospheric horizon line below.
- **Subject motion:** Action/turn; surfer performs a full 360-degree rotation flip on the board; fast speed.
- **Camera motion:** Locked off relative to subject path.
- **Camera–subject relationship:** Camera maintains fixed distance while subject rotates mid-frame.
- **Dynamism sources:** Particle sparks, continuous tail jet flare, light stream behind board. Energy: 4/5.
- **Realism cues:** Metallic surface specularity, motion blur during spin. AI tells: suit texture morphs during rotation, board shape deforms slightly. Realism: 3/5.
- **Would a video model get this right?** Moderately complex prompt requiring 3D character rotation on a dynamic object.

### Clip 2 — 00:03.5 to 00:07.0 (3.5 s)
- **Frame:** Medium shot; exact duplicate loop of Clip 1.
- **Subject motion:** Action/turn; acrobatic rotation/flip on board; fast speed.
- **Camera motion:** Locked off parallel track.
- **Camera–subject relationship:** Fixed tracking framing subject maneuver.
- **Dynamism sources:** Flare tail, particle dust spray. Energy: 4/5.
- **Realism cues:** High contrast metallic reflections. AI tells: mesh flickering and board geometry warping during flip. Realism: 3/5.
- **Would a video model get this right?** Repeated clip; same generation as Clip 1.

### Clip 3 — 00:07.0 to 00:15.2 (8.2 s)
- **Frame:** Extremely wide shot; high orbital angle looking down at planetary curvature and cloud layers.
- **Subject motion:** Linear travel / drift; glides continuously left-to-right along the horizon; real-time medium speed.
- **Camera motion:** Slow tracking parallel to orbital curve.
- **Camera–subject relationship:** Camera follows from high elevation while surfer cuts across space.
- **Dynamism sources:** Engine trail, atmospheric cloud movement, starry backdrop particles. Energy: 3/5.
- **Realism cues:** Atmospheric limb curve, consistent directional sun lighting. AI tells: slight limb warping on surfer, subtle speed stuttering. Realism: 4/5.
- **Would a video model get this right?** Simple motion prompt: "Silver Surfer gliding over planet horizon with light trail."

---

## 3. Structure and rhythm
- **Clip Durations:** 3.5 s, 3.5 s, 8.2 s.
- **Hook:** Immediate visual action; subject begins mid-spin within the first frame.
- **Screen Direction:** Consistent left-to-right screen vector across all cuts.
- **Energy Curve:** Opens with dynamic, fast-paced acrobatic close-ups before releasing tension into a wide, majestic space glide.
- **Ending:** Smooth glide into the distance as ambient light fades out.

---

## 4. Patterns
1. **Maintain Screen Direction:** Keep movement vectors uniform (left-to-right) across transitions.
2. **High Contrast Framing:** Silhouette dark metallic subjects against luminous backdrops.
3. **Loop Action for Energy:** Repeat short high-impact action sequences to build audio-visual beat sync.
4. **Scale Progression:** Transition from tight action frames to expansive wide shots to emphasize environment scale.
5. **Use Light Trails:** Incorporate continuous particle or beam trails behind fast-moving objects to smooth out motion artifacts.

---

## 5. Clip table (JSON)

```json
[
  {
    "n": 1,
    "start": 0.0,
    "end": 3.5,
    "subject_motion": "action",
    "direction": "left-to-right",
    "subject_speed": "real-time fast",
    "camera_motion": "locked off",
    "camera_speed": "static",
    "relationship": "camera tracking parallel while subject spins",
    "dynamism": ["particle sparks", "tail flare", "light stream"],
    "energy": 4,
    "realism": 3,
    "ai_tells": ["suit texture morphing", "board deformation during rotation"]
  },
  {
    "n": 2,
    "start": 3.5,
    "end": 7.0,
    "subject_motion": "action",
    "direction": "left-to-right",
    "subject_speed": "real-time fast",
    "camera_motion": "locked off",
    "camera_speed": "static",
    "relationship": "fixed tracking frame during maneuver",
    "dynamism": ["flare tail", "particle dust"],
    "energy": 4,
    "realism": 3,
    "ai_tells": ["mesh flickering", "board geometry warping"]
  },
  {
    "n": 3,
    "start": 7.0,
    "end": 15.2,
    "subject_motion": "linear travel",
    "direction": "left-to-right",
    "subject_speed": "slow",
    "camera_motion": "tracking",
    "camera_speed": "slow",
    "relationship": "distant camera tracking parallel to planet curvature",
    "dynamism": ["engine trail", "cloud movement", "space dust"],
    "energy": 3,
    "realism": 4,
    "ai_tells": ["limb geometry warping", "speed stuttering"]
  }
]
```