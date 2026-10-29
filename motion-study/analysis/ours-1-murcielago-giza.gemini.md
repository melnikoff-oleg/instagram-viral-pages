<!-- model gemini-3.6-flash, 8.0 fps sampling, generated 2026-10-29 07:52 -->
<!-- source ours-1-murcielago-giza.mp4: {'width': 1080, 'height': 1920, 'fps': 24.0, 'duration': 14.792} ; ffmpeg cut hints [3.08, 6.42, 9.75] -->

# ours 1 murcielago giza

## 1. Overview
- **Subject:** Gold Lamborghini Murciélago.
- **Setting:** Giza Pyramids and open desert, Egypt.
- **Time/Weather:** Golden hour / sunset, dusty sandstorm conditions.
- **Mood:** Cinematic, intense, surreal action.
- **Colour Palette:** Warm gold, ochre, burnt orange, muted sky.
- **Clips:** 4 clips.
- **Average Clip Length:** ~3.65 s.
- **Rhythm:** Hard cuts aligned with music beat hits and rising dramatic action.

---

## 2. Clip by clip

### Clip 1 — 00:00.000 to 00:03.000 (3.0 s)
- **Frame:** Low side-profile wide shot of supercar on desert asphalt with Pyramids in background.
- **Subject motion:** Linear travel; left→right; real-time fast (wheel blur, trailing road streaks).
- **Camera motion:** Tracking (parallel with subject); medium speed.
- **Camera–subject relationship:** Camera matches car speed, holding car steady in frame while background slides.
- **Dynamism sources:** Dust plume behind rear tires, wheel motion blur, warm sun flare. Energy: 3.
- **Realism cues:** Vintage film grain, soft lens flare, realistic ground reflections. AI tells: wheel rim spoke deformation, background distortion. Realism: 3.
- **Would a video model get this right?** Simple: "Gold Lamborghini driving fast past Giza pyramids tracking shot".

### Clip 2 — 00:03.000 to 00:06.250 (3.25 s)
- **Frame:** Ground-level close-up of car drifting off-road near pyramid base.
- **Subject motion:** Turn / drift; right→left; real-time fast.
- **Camera motion:** Tracking low angle, tilting up into dust cloud.
- **Camera–subject relationship:** Camera stays near ground as car whips around and engulfs screen in sand.
- **Dynamism sources:** Massive exploding sand cloud, sunset lens flare, swirling dirt. Energy: 4.
- **Realism cues:** Realistic particle density in sand cloud. AI tells: rear bumper morphs into sand texture. Realism: 3.
- **Would a video model get this right?** Moderate: "Lamborghini drifting in desert dirt throwing up giant sand cloud".

### Clip 3 — 00:06.250 to 00:09.625 (3.375 s)
- **Frame:** Low-angle rear tracking shot of car driving along desert highway alongside a wall of dust.
- **Subject motion:** Linear travel; diagonal away from camera; real-time fast.
- **Camera motion:** Follow / parallel tracking; medium speed.
- **Camera–subject relationship:** Camera follows car as it drives parallel to a towering haboob.
- **Dynamism sources:** Massive dark sandstorm wall, tail light glow, asphalt tire kick-up. Energy: 4.
- **Realism cues:** Strong atmospheric haze and tail light bloom. AI tells: texture swim inside dust storm wall. Realism: 3.
- **Would a video model get this right?** Simple: "Supercar driving down highway beside a massive dust storm wall".

### Clip 4 — 00:09.625 to 00:14.625 (5.0 s)
- **Frame:** Extreme wide shot of car airborne high above desert dunes and camel caravan.
- **Subject motion:** Action (jumping/crashing); high left→right arc into dune impact; real-time fast.
- **Camera motion:** Pan wide shot; slow tracking move following crash.
- **Camera–subject relationship:** Camera watches car fly through air and plunge nose-first into dune crest.
- **Dynamism sources:** Exhaust smoke trail in air, massive sand explosion upon dune crash. Energy: 5.
- **Realism cues:** Sand displacement explosion on impact. AI tells: anti-gravity floating physics, erratic mid-air arc, camel scale mismatch. Realism: 2.
- **Would a video model get this right?** Complex: Requires multi-stage prompt (flying levitation into high-impact desert crash).

---

## 3. Structure and rhythm
- **Clip durations:** 3.0s, 3.25s, 3.375s, 5.0s.
- **Hook:** Immediate high-speed action with iconic pyramid silhouette establishes environment in frame 1.
- **Screen direction:** Predominantly left-to-right motion, maintaining visual continuity across cuts.
- **Energy curve:** Escalates steadily from high-speed driving to close-range drifting, massive storm chasing, and a climactic stunt crash.

---

## 4. Patterns
1. **Establish world instantly** with unmistakable iconic background elements in shot 1.
2. **Use ground-level camera angles** to exaggerate vehicle speed and motion visual weight.
3. **Incorporate high-volume visual FX** (sand clouds, smoke) to mask AI geometry artifacts.
4. **Keep lighting consistent** across generated clips using warm sunset backlighting.
5. **End on extreme peak action** featuring high kinetic energy and destruction.

---

## 5. Clip table (JSON)

```json
[
  {
    "n": 1,
    "start": 0.0,
    "end": 3.0,
    "subject_motion": "linear travel",
    "direction": "left->right",
    "subject_speed": "real-time fast",
    "camera_motion": "tracking",
    "camera_speed": "medium",
    "relationship": "camera tracks parallel keeping subject centered",
    "dynamism": ["dust plume", "wheel motion blur", "lens flare"],
    "energy": 3,
    "realism": 3,
    "ai_tells": ["wheel rim morphing", "background distortion"]
  },
  {
    "n": 2,
    "start": 3.0,
    "end": 6.25,
    "subject_motion": "turn",
    "direction": "right->left",
    "subject_speed": "real-time fast",
    "camera_motion": "tracking",
    "camera_speed": "medium",
    "relationship": "low camera stays close as car turns and kicks sand at lens",
    "dynamism": ["sand cloud explosion", "sun flare", "swirling dust"],
    "energy": 4,
    "realism": 3,
    "ai_tells": ["car body morphs into sand storm blur"]
  },
  {
    "n": 3,
    "start": 6.25,
    "end": 9.625,
    "subject_motion": "linear travel",
    "direction": "diagonal away",
    "subject_speed": "real-time fast",
    "camera_motion": "follow",
    "camera_speed": "medium",
    "relationship": "camera tracks behind car parallel to giant dust wall",
    "dynamism": ["massive rolling haboob wall", "tail light bloom"],
    "energy": 4,
    "realism": 3,
    "ai_tells": ["texture swim in dust storm cloud"]
  },
  {
    "n": 4,
    "start": 9.625,
    "end": 14.625,
    "subject_motion": "action",
    "direction": "left->right downward",
    "subject_speed": "real-time fast",
    "camera_motion": "pan",
    "camera_speed": "slow",
    "relationship": "camera captures full trajectory of car jump and dune crash",
    "dynamism": ["smoke trail", "massive sand displacement explosion"],
    "energy": 5,
    "realism": 2,
    "ai_tells": ["unrealistic floaty flight physics", "scale incongruity with camels"]
  }
]
```