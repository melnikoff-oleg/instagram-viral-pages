# SOP: how every frame and clip moves

The rulebook for generating clips that move like the @iamnotsrc reels. Built from a clip-by-clip study of the five latest @iamnotsrc reels and our Murciélago × Giza reel (`analysis/`, `findings.md`). Read it before planning a series, before writing an image prompt, before writing a video prompt, and again when judging the clips.

It sits on top of `concept/instagram-concept.md` (the look) and `full-pipeline/prompts/` (the prompt templates). Where this document and the older rules disagree, this document wins; section 10 lists the differences.

---

## 0. The rule in one paragraph

Every clip is **one subject doing one simple, fast thing, seen from one fixed angle, with one thing in the environment moving too.** The car is either going straight and fast or drifting. The car is never standing still; the only exception is a still car with the camera flying around it so fast that the scenery itself moves. The camera does exactly one thing per clip and never changes its angle on the car. Speed is shown by the background, the wheels and the trail, not by the car bouncing around the frame. Everything must look like a frame someone could have shot on film: blur, grain, weight, dust that obeys gravity. Nothing that makes a viewer think "fake".

---

## 1. Why these videos work (the findings in five lines)

1. **Simple vectors.** In 21 reference clips, the subject moves on one straight line or one continuous arc. Never two things at once. (`findings.md` §1)
2. **The world carries the speed.** The subject stays pinned near one spot in the frame; a smeared background, streaking lights or a long trail say "fast". (§2)
3. **One camera behaviour per clip:** locked, tracking alongside at matched speed, following behind, or a single pan. Zero orbits, zero combined moves, one whip pan in 21 clips. (§3)
4. **Every frame has an emitter.** Fire, sparks, muzzle flash, thruster, spray, dust, bats, a cape in the wind. Even the still portraits have something moving. (§4)
5. **Few, long clips.** The 4.2M-play reel is two shots of 7 and 8 s. Our 15 s reel had four ideas and lost the car for 1.5 s. (§5)

---

## 2. Vocabulary

Use these words in plans, prompts and judging notes so everyone (and every model) means the same thing.

### 2.1 Subject motion (the car)

| Code | Name | Definition | Allowed? |
|------|------|------------|----------|
| **S1** | **Straight and fast** | The car travels on one straight line at real-time high speed (100+ mph / 160+ km/h on tarmac, 60+ mph / 100 km/h on sand, snow, gravel). Wheels blurred, body steady, no bouncing. | Yes. The default. |
| **S2** | **Drift** | The car enters fast, the tail steps out, it holds a wide arc with the front wheels counter-steered, rear tyres shedding smoke/sand/snow, and exits. One continuous arc, the car's heading changes smoothly through 30–120°. | Yes. The second move. |
| **S3** | **Still car, flying camera** | The car does not move; the camera orbits or sweeps around it fast enough that the background sweeps across the frame at speed. | Only as an exception: at most one clip per reel, never the opener, never the last clip. See 4.3. |
| S0 | Parked / idling / rolling slowly | The car stands, creeps, "glides", "cruises". | **Forbidden.** No frame, no clip, no first frame, no last frame. |
| SX | Jumps, flips, rotations on the spot, flying, teleporting | Anything that breaks the physics of a 1.5-tonne car. | **Forbidden.** The airborne Murciélago was the least real moment in our reel. |

A drift is **S2** only while the tail is out and the car is moving. A car "drifting" at walking pace is S0.

### 2.2 Camera behaviour

| Code | Name | Definition | How often in the references |
|------|------|------------|-----------------------------|
| **C1** | **Locked** | The camera does not move at all. The car crosses, approaches, or leaves. Horizon level. | 11 of 21 clips |
| **C2** | **Matched track** | The camera moves on a line parallel to the car at (almost) the car's speed, so the car hangs in one place in the frame while the background streaks. The angle on the car does not change. | 6 of 21 clips (every vehicle side shot) |
| **C3** | **Follow / lead** | The camera is directly behind (follow) or directly in front (lead) of the car, on the car's line, at nearly matched speed. The car grows (lead, camera retreating) or holds (follow). | 2 of 21 |
| **C4** | **Single pan** | The camera stands in one spot and turns once, in one direction, to keep the car in frame as it passes. Includes the late "flinch" pan. | 2 of 21 |
| **C5** | **Whip pan** | One violent horizontal pan from a fixed spot, the frame smears for ~0.5 s, then re-finds the car. | 1 of 21 |
| **C6** | **Fast orbit** | The camera arcs around a still car, fast. The background sweeps. | 0 of 21 in the references. Allowed only with S3. |
| CX | Chase-car arcs, orbits around a moving car, crane drops, FPV dives, dolly-zooms, any two moves combined | The angle on the car changes while the car moves. | **Forbidden.** This is what broke the F40 reel. |

**The rule that unifies C1–C4: the camera's angle on the car stays constant for the whole clip.** The camera may travel (C2, C3) but only parallel to the car. A tracking shot is a fixed angle that moves.

### 2.3 Emitters (what else moves)

Every clip needs at least one. Pick from the car or the place:

- **From the car:** rooster tail of dust / sand / snow / water, tyre smoke, exhaust flames and backfire, sparks from the undertray or a scraping splitter, headlight beams raking through dust, tail lights, rain spray off the wheels, mud clods.
- **From the place:** sandstorm, blizzard, rain, fog rolling, waves breaking, steam, pigeons or crows lifting, leaves or paper blown by the car's wake, lamp posts and arches streaking past, neon flicker, fireworks, lightning.
- **From the light:** a flickering light source (backfire, lightning, a passing train's windows) adds energy at 1–2 Hz even when nothing else changes.

Trails are the cheapest emitter: a straight line with a dust or spray trail reads as fast, and the trail keeps the frame alive after the car leaves.

---

## 3. Speed: how fast, and how it is read

The viewer never sees a speedometer. They read speed from four things, in this order:

1. **Background smear.** In C2/C3 clips the background must be blurred into streaks for the whole clip. Buildings, pyramids, arches, lamp posts, fences: anything with repeating verticals streaks best. A flat sky or an empty desert gives no speed read (Iron Man clip 2's weakness). Always put something between the camera and the horizon that can streak.
   **Near things carry the motion, far things carry nothing.** A landmark a kilometre behind the car does not move at any speed: in the Mustang × Monument Valley opener the butte was far behind, so the only motion in the frame was the road texture and the clip read as a slow glide at 100 mph. The references put the moving layers close: Ghost Rider's verge, rail and road markings pass right under the bike, Batman's arches and lamp posts are metres from the camera. So every clip needs **two near layers**: something **5–30 m from the car** that streaks (the base of the landmark, a wall, posts, a rail, bushes, rocks, a dune edge) and something **1–3 m from the lens** that whips past between the camera and the car (a post, grass, a rock, the trail's own dust). The landmark may sit big and far in the still for the hook, but then the near layers must be in the same frame, and the prompt must name them: "<near things> whip past between the lens and the car, <mid things> streak right behind it".
2. **Frame-crossing time.** In C1 clips the car should cross the full frame width in **0.8–2.0 s** when passing side-on at mid distance, and grow from "small" to "full frame" in **2–3 s** when approaching. Longer than that reads as cruising.
3. **Trail length.** Dust, spray or smoke trailing at least one car length behind, more on sand and snow.
4. **Wheels visibly spinning.** The wheels and rims rotate for the whole clip, spokes turning, blurred by rotation. A moving car with frozen wheels is the worst tell we have made (Mustang × Monument Valley, 2026-10-29: the car moved, the rims stood still). "Blurred into discs" is not enough, the model reads it as a static texture: write "the wheels and rims visibly spinning" in every SHOT line and "No frozen wheels" in EXCLUSIONS, every clip, no exceptions.

Prompt numbers (state them, the models obey numbers better than adjectives):

| Surface | Straight (S1) | Drift (S2) |
|---------|---------------|------------|
| Tarmac, square, bridge | 100–120 mph (160–190 km/h) | 50–60 mph entry (80–100 km/h), tail out |
| Sand, gravel, dirt | 60–80 mph (100–130 km/h) | 40–50 mph entry, big rooster tail |
| Snow, ice | 50–60 mph (80–100 km/h) | 30–40 mph entry, long slide, snow fountain |

Always write "real-time speed, no slow motion" in GOAL and "No slow motion, no gentle movement" in EXCLUSIONS. The models default to a cinematic glide when nobody forbids it.

**Camera speed.** In C2 the camera is a touch *slower* than the car (the car gains on the frame, from the left third to the centre over the clip, like Ghost Rider clip 1). Exactly matched speed makes the car look pinned to the glass. In C3 the camera is matched (follow) or slightly slower (lead, so the car grows). In C4 the pan is late by a beat and overshoots slightly.

---

## 4. The shot menu

Eight shots. Every clip we generate is one of these. Each is one subject motion + one camera behaviour + one emitter. Reference clips in brackets.

### 4.1 Straight and fast (S1)

**A. Side track** (Ghost Rider 1, Rocket 1, Batman 4) — the house shot.
- Car side-on, low camera (hub to window height), 35–50 mm, 5–15 m away. Car in the left or right third, nose pointing into the empty side.
- C2: the camera moves alongside a touch slower than the car; the landmark and road furniture streak past behind.
- Emitter: rooster tail, sparks, exhaust flame, tail-light glow.
- Duration 5–8 s. The best opener when the landmark is behind the road.
- Prompt core: "The camera travels alongside the car at almost the same speed, slightly behind, so the car slowly gains from the left third toward the centre of the frame while <landmark> and <road furniture> streak past behind it in long horizontal blur."

**B. Drive-away, locked** (Ghost Rider 2, our clip 3) — the ending shot.
- Camera C1 on the road axis, low, behind the car. Car already moving in frame 0, shrinks to tail lights in 5–8 s.
- Emitter: the trail (dust, snow spray, flames, wet-road spray) spreading back toward the camera and outliving the car.
- The frame must stay alive after the car is gone: embers, dust settling, lights.
- Prompt core: "The camera does not move. From the first frame the car is already pulling away down the straight road, shrinking to two tail lights in about five seconds, while the <trail> it throws spreads back toward the lens and keeps moving after the car is a dot."

**C. Oncoming grow** (Batman 2) — the strongest "impact" shot.
- Camera C1 or C3-lead, low, on or near the car's line, 24–35 mm. The car starts small (far third of the road) and grows to nearly full frame in 2–3 s, then passes beside the lens (not through it).
- Emitter: headlights raking, dust/snow thrown forward by the wind, tunnel or arch lights streaking.
- Keep the car's **pass distance at 2–3 m from the lens**, never under 1 m: a car inside a metre of the lens becomes an unreadable smear (our clip 2).
- Prompt core: "The car comes straight at the camera from far down the <road/tunnel>, growing from a distant shape to nearly filling the frame in about three seconds, then tears past two metres to the side of the lens; the camera holds its spot and flinches a beat late."

**D. Follow behind** (Batman 5, Iron Man 2) — the tunnel / avenue shot.
- C3-follow, camera at the car's height, 3–8 m behind, matched speed. The car holds its place; walls, lamps, arches stream past on both sides. Slight weave of the car adds life.
- Emitter: tail lights, exhaust pops, the lights of the place streaming.
- Prompt core: "The camera follows directly behind at the same speed so the car stays the same size in the centre of the frame while the <arches/lamps/walls> stream past on both sides in hard motion blur."

**E. Fixed-point pan** (Iron Man 1, Rocket 4) — the landmark shot.
- C4 from a raised fixed spot (a wall, a roof, a slope), 50–85 mm. The car crosses the scene side-on and the camera pans once to keep it; the landmark slides through the background. The pan is slightly late.
- Emitter: dust trail, spray, birds lifting, flags.
- Only pan: no zoom, no tilt, no second move. Horizon level.
- Prompt core: "From a fixed spot the camera pans once, a beat late, to keep the car as it crosses from left to right in about two seconds; <landmark> slides across the background behind it; no zoom, no tilt, the horizon stays level."

### 4.2 Drift (S2)

**F. Drift arc past a low camera** (Silver Surfer 1, Giza clip 2 as it should have been).
- C1, camera low, 24–35 mm, placed on the **outside** of the arc, 4–6 m from the closest point. The car enters fast from one side already sideways, sweeps the arc with the tail out, passes 2–3 m from the lens, exits on the other side. The camera may flinch (C4-late) as it passes; nothing else.
- Emitter: the rear tyres throw smoke/sand/snow toward the lens; some hits the lens for a few frames (not more than 0.5 s of blocked frame).
- Physics line, every time: "tail stepped out, front wheels counter-steered, smoke only from the rear tyres, the body leaning on the outside suspension, the car never rotating on the spot."
- Prompt core: "The car is already mid-drift in the first frame, tail out, front wheels turned into the slide, sweeping a wide arc from the left toward the camera and past it on the right, two to three metres from the lens; sand pours off the rear tyres toward the camera; the camera holds its spot and pans a beat late to follow it out."

**G. Drift held, camera rolling with it** (Silver Surfer 1 again).
- C2 but on an arc: the camera moves with the car around the corner, close (3–5 m), so the car holds one angle in frame (front three-quarter, tail visible) while the landmark sweeps across the background at speed. This is the one clip where the horizon may roll a few degrees, because the move is one continuous arc.
- Use for the "play" beat: donuts around a monument, a long slide along a quay.
- Prompt core: "The camera rides the drift with the car, keeping the same front three-quarter angle the whole time while <landmark> sweeps across the background from right to left behind the smoking rear tyres."

### 4.3 The exception (S3 + C6)

**H. Still car, flying camera.**
- Allowed once per reel at most, never first, never last. The car is still (engine running: exhaust shimmer, lights on). The camera arcs around it at speed so the landmark sweeps across the frame; the background must move as fast as a C2 background. Something must still move in the scene: snow falling, dust blowing, headlight beams, a flickering light.
- If the generator renders the arc slowly, the clip is dead: a slow orbit of a parked car is exactly the "fake car commercial" look we must never post. Judge it hard. If in doubt, replace it with shot A.

---

## 5. Camera–subject rules (apply to every shot)

1. **Constant angle.** The camera's angle on the car does not change inside a clip. Tracking moves parallel to the car; pans happen from a fixed point. Never an arc around a moving car.
2. **One move per clip.** Locked, or track, or follow, or one pan. Never "tracks, then orbits", never "pans and tilts".
3. **The car is pinned or drifts slowly across the frame.** It sits near a third line and either holds there (C2/C3) or crosses once (C1/C4). It never wanders.
4. **Distance 3–30 m.** Closest pass 2 m. No car inside a metre of the lens, no lens fully blocked for more than 0.5 s.
5. **Height: low.** Hub to window height for A, C, D, F, G. Raised only for E. Never top-down drone for video (fine for a still, bad for motion: no background streak).
6. **Lens 24–85 mm.** Wide (24–35) when the car passes close, long (50–85) when the camera is far and the landmark should compress behind the car. No fisheye, no FPV.
7. **Horizon level,** except shot G, where it may roll a few degrees with the arc. Never ask for a "tilting horizon" or "dutch angle" in a video prompt: it gets rendered as a wobble.
8. **The camera is a person.** A beat late, a small overshoot, a flinch when debris hits. Never "handheld shaking", never "jitter", never "struggling".
9. **The background must be streakable, and close.** Put repeating structure or a trail between camera and horizon in every clip, with one layer 5–30 m from the car and one 1–3 m from the lens (§3). A frame whose only structure is a distant landmark has no motion in it.
10. **The first frame is the picked still.** Car and landmark readable, the car already in motion in that still (blurred wheels, trail, tail out). Attach it with role `image`.

---

## 6. Dynamism rules

- **Energy target: 4–5 on 5** for every clip except a landing/ending beat (3). Energy = subject speed + emitter + background motion. A still car with an emitter alone is a 2: not enough.
- **At least one emitter per clip, two is better.** The car's own (dust, smoke, sparks, flame, spray) plus the place's (storm, snow, birds, streaking lights).
- **An environment event lifts a whole clip.** The sandstorm in our clip 3, the fire river in Ghost Rider 2. Plan one per series, in the "peak" slot.
- **Light that changes** counts: headlights sweeping across a wall, backfire flashes, lightning, a train passing. Use it when the car has to be smaller in frame.
- **Trails outlive the car.** In B and E, write what the trail does after the car has left: spreads, settles, glows.
- **Sound is part of the energy.** Engine at full revs, tyres, debris on the mic, wind. No music in the prompt ever (added in Instagram).

---

## 7. Realism rules

The references look like film because they obey physics and the lens. Our clips must pass all of these; a clip that fails any of the first five is not posted.

### 7.1 Physics
1. **Four wheels on the ground.** No jumps, no air, no wheelies. (Our Giza clip 4 is the counter-example.)
2. **Weight.** Body roll on the outside of a drift, nose dip under braking, suspension compressing on a bump. Write "the body leaning on the outside suspension" for drifts.
3. **Debris comes from the tyres and goes where the wheels send it.** Rear tyres make the smoke in a drift, the rooster tail starts at the rear wheels, dust blows back along the car's line and then sideways with the wind. Debris obeys gravity: sparks and embers fall, dust settles, spray arcs down.
4. **Shadows and contact.** The car has a shadow under it and a dark contact patch at each wheel. Reflections of the hot light on the paint.
5. **Scale.** The landmark is landmark-sized; people, camels, lamp posts are real-sized. Doll-sized camels (our clip 4) break the frame.
6. **Weather is continuous across clips.** The same storm, the same snow, the same light direction in every clip of a series. Two storms at two speeds (our clips 2 and 3) read as two different days.
7. **The space is one real place, and the clip obeys it.** Before writing the SHOT lines, write the floor plan in one sentence: where the camera stands, the line the car travels, where the landmark and the near objects are. Then every beat is what that camera sees from that spot. What the car has passed is behind it and does not come back; the landmark stays on the side it started on and slides the way the camera move says it must; the car's heading changes only by driving, never between two frames; when a dust cloud or spray hides the car, it comes out on the same line, pointing the same way, about where it should be after that much time. The Mustang × Monument Valley reel broke this twice: the car went into its own dust tail-first and came out nose-first, and the butte was passed on one side and then appeared on the other. Both read as nonsense, however good the frames look. Write the plan into the [CONTINUITY] line of the prompt (§9.2) and reject any clip that breaks it.

### 7.2 Lens and film
7. **Motion blur** on the background in every moving shot, on the wheels always, on the debris. "Extreme motion blur on the ground and the debris" in STYLE.
8. **Backlight and silhouette.** One hot light behind or beside the car, the car falling into a warm near-black silhouette with a lit edge. Detail in shadow is detail the model cannot ruin. The references are silhouettes against sun, moon, tunnel lamps, fire, city bokeh.
9. **Grain, halation, soft highlights.** Coarse grain, blooming around the one hot light, nothing tack sharp. Flat, clean, crisp renders are the AI tell.
10. **Real lens behaviour:** flare from the hot light, lens dirt in backlight, a brief focus hunt after a debris hit, depth of field on a long lens.
11. **Exposure for the sky.** Twilight gradient, lifted blacks, the ground dark and warm. Never a bright midday sky.

### 7.3 AI tells to judge for (reject the clip if any is visible for more than a few frames)
- **Wheels that stand still while the car moves.** Reject on sight, no matter how good the rest is.
- Wheels that wobble, change spoke count, or stop blurring.
- The body morphing: a door line sliding, the roofline bending, badges or lights drifting.
- The landmark changing shape, duplicating, or gaining extra elements.
- **Spatial nonsense:** an object the car has passed coming back into frame, the landmark jumping from one side of the car to the other, the car's heading or orientation flipping behind dust, spray or a pan, the car reappearing somewhere it could not have got to. Reject on sight (§7.1 rule 7).
- The car's colour shifting between frames or between clips.
- Dust or smoke that hangs without moving, or moves against the car's direction.
- Texture swim on the road, grain that "boils" in a fixed pattern.
- A horizon that bends.
- Scale errors (giant car, tiny monument, doll-sized extras).
- A speed change inside the clip without a reason (the car suddenly slowing is the model drifting into its default glide).
- Any frame where the viewer cannot tell what they are looking at for longer than 0.5 s.

---

## 8. Series structure

The references are 2–7 clips of 2–8 s each. The best performer is two clips. Ours was four clips of 3–5 s, each one a different idea.

- **Length:** the standard structure is **4 clips of 5 s** (opener, play, peak, funny ending), about 20 s stitched after beat-snapping. The references run 2–7 clips of 2–8 s and the best of them is two long clips, so when a beat needs longer, give it 8 s and drop another beat rather than squeezing five ideas in. Never shorter than 4 s per clip.
- **Hook:** frame 0 shows the car and the landmark, the car already moving, the emitter already visible. The first clip is an S1 shot at energy 5 (A, C or D). Never open on the exception shot, never on a wide where the car is small.
- **Rhythm:** alternate the camera–subject relationship between clips. Side track → drive-away; oncoming → side track; drift → follow. Never two clips with the same shot code in a row, never two side profiles with the same backdrop in a row.
- **Cut contrast (hard rule).** Two consecutive clips must look like two different shots at their first frame. Between any cut, at least **two of these four** change: (a) the angle on the car (side / front three-quarter / head-on / rear), (b) the car's size in the frame (small / mid / filling), (c) the lens and camera height (24–35 mm on the ground vs 70–135 mm raised or far), (d) the car's vector across the frame (crossing / toward the lens / away from it). The Mustang × Monument Valley cut 1 → 2 failed this: both frames were a side three-quarter of the car in the lower half of the frame with a butte behind, so the cut read as a stutter. The references never do it: Ghost Rider cuts from a side track to a locked rear shot with the bike shrinking to a dot. Plan the four stills as four different shapes on a thumbnail before writing a prompt, and judge the contact sheet row by row against the row above it.
- **Screen direction:** keep it. If the car travels left→right in clip 1, it travels left→right (or toward / away) in every clip. It never flips between cuts; it turns on screen if it must change.
- **Energy curve:** 5, 4, 5, 3 (opener, play, peak, ending). The peak clip carries the environment event.
- **Ending:** shot B (drive-away with the trail outliving the car), or a slide-to-stop with dust rolling past the car and the car still rocking on its suspension in the last frame. The ending is the only clip that may end with the car at rest, and only in its last second, and only with the dust still moving. The funny ending from the concept doc still applies when the gag is one clear physical action; a gag that needs the car to jump is out.
- **Cuts on hits.** Cut points land on the music's hits (stitch.py handles it); plan clip lengths so the strong first frames land on the drop.

---

## 9. Prompt blocks

### 9.1 Still frame (the first frame of each clip)

The still must already contain the motion. Add to the Tone paragraph of the image prompt, every time:
- S1: "mid-pass at speed, the wheels spinning and blurred by rotation, a long <dust/spray> trail behind, the background streaked by the panning camera"
- S2: "mid-drift, the tail stepped out, the front wheels counter-steered, a wall of <smoke/sand/snow> pouring off the rear tyres, the body leaning on the outside suspension"
- Never: "parked", "stands", "waits", "poses", "rests", "sits".

Pick the still that reads as the loudest movement; a beautiful still of a parked car is a reject even if the landmark is perfect.

The still also has to contain the near layers the clip will move (§3): write them into the Camera or Tone paragraph of the image prompt ("a fence post and dry grass blurred in the foreground a metre from the lens", "the base of the butte right behind the road", "a stone wall racing past behind the car"). A still of a car alone on a road with the landmark far away is a still with nothing to move.

And the four stills must differ as shapes: lay them out side by side and apply the cut-contrast rule (§8) before generating. Same angle, same car size, same backdrop twice in a row is a reject at the planning stage.

### 9.2 Video prompt (Seedance 2.5, 5 s, 9:16, audio on)

Keep the template structure from `full-pipeline/prompts/video-prompt-template.md`. Fill it with the shot code's lines:

```
[GOAL] One continuous <N>-second shot, vertical 9:16, opening exactly on <<<image_1>>>: <car, landmark, weather, light in one sentence>. Keep the car, <landmark>, <weather>, light and film look from <<<image_1>>> throughout. Real-time speed, no slow motion: the car is doing <SPEED from §3> and the whole clip must feel violently fast. <ONE SENTENCE FROM §4: what the camera does and what the car does.>

[CONTINUITY] The camera stands <where, in words: on the verge on the near side of the road, low>. The car's line runs <from where to where across the frame>. <The landmark> is <where: behind the road on the far side, left of the car> and stays there. Nothing the car has passed comes back into the frame. The car keeps the heading it has in <<<image_1>>> and only changes it by driving; when dust or spray hides it, it comes out on the same line, pointing the same way, the same distance along. The scene is one real place seen from one spot.

[SHOT | 0-<t1>s] The first frame is exactly <<<image_1>>>, the car already <moving / mid-drift>, the wheels and rims visibly spinning. <The first beat with a time: in about half a second it ... / by one second it ...>. <What the emitter does.> <The near layers: what whips past between the lens and the car, what streaks right behind it.>

[SHOT | <t1>-<N>s] <The second beat with a time.> <What the background does: streaks, slides, sweeps.> The wheels keep spinning fast the whole way. <What the trail does after.>

[CAMERA] <C-code line from §4>. <Height, lens, distance.> The angle on the car does not change. No orbit, no zoom, no cut, no second move, no slow motion. The horizon stays level.

[STYLE] Analog 35mm film matching <<<image_1>>>: coarse grain, muted <palette>, extreme motion blur on the background, the ground and the debris, the wheels and rims spinning fast and blurred by rotation, halation around <the hot light>, the car slightly soft.

[AUDIO] Engine at full throttle, <tyres on the surface>, <debris on the mic>, wind. No music, no dialogue.

[EXCLUSIONS] No slow motion, no gentle movement, the car never stops or slows. No frozen wheels: the wheels and rims visibly spin the whole time the car moves. No jump, no airborne car. No text, logos or watermark. No other vehicles or people. No change to the car's color or shape. No CGI look.
```

Words that must appear: a speed number, "real-time", "already moving" (or "already mid-drift") in the first SHOT line, "the wheels and rims visibly spinning" in every SHOT line, a time in seconds for each beat, "the angle on the car does not change", "No slow motion", "No frozen wheels".
Words that must not appear: glide, cruise, roll, steady, smooth, gentle, slow, elegant, majestic, parked, orbit, tripod, dutch, tilting horizon, drone, FPV, handheld shaking.

### 9.3 Camera lines per shot code (copy-paste)

- **A side track:** "The camera travels alongside the car on a parallel line at almost the same speed, slightly behind, hub height, 35mm, eight metres away, so the car slowly gains from the left third toward the centre while everything behind it streaks."
- **B drive-away:** "The camera stays fixed on the road axis, low, behind the car; it does not move or pan; the car shrinks straight down the road."
- **C oncoming:** "The camera stays fixed, low, just beside the car's line, 28mm; the car grows toward it and passes two metres to the right; the camera flinches a beat late as it passes."
- **D follow:** "The camera follows directly behind the car at the same speed, at tail-light height, five metres back, 35mm; the car stays the same size in the centre while the walls and lights stream past."
- **E pan:** "The camera stands on <the raised spot>, 70mm, and pans once, a beat late, from left to right to keep the car; no zoom, no tilt."
- **F drift past:** "The camera stays fixed on the ground on the outside of the arc, 24mm; it pans a beat late as the car sweeps past three metres away; the rear tyres throw <debris> at the lens for a few frames."
- **G drift ride:** "The camera rides the arc with the car, close, keeping the same front three-quarter angle on it the whole time while <landmark> sweeps across the background."
- **H still car (exception):** "The car stands with the engine running; the camera arcs fast around it at hub height so <landmark> sweeps across the background in two seconds; <snow/dust> blows through the frame."

---

## 10. What changed vs the previous rules

- **Tracking is allowed again, and it is the main move.** The old rule "the camera does not move from its spot" came from the F40 failure, where the camera *orbited*. The references track alongside and follow behind constantly; what they never do is change the angle on the subject. The rule is now "constant angle": locked, parallel track, follow/lead, or a single pan.
- **Jumps are out.** The concept doc allowed jumps with weight; the evidence says the airborne car is our least real moment and the references never leave the ground (Iron Man flies, but he is Iron Man). The funny ending must be a ground-level gag.
- **Fewer, longer clips.** The structure is now 4 clips of 5 s (opener, play, peak, funny ending) instead of 5 clips of 4 s. The "atmosphere" slot is folded into the peak.
- **Closest pass 2 m, lens never covered for more than 0.5 s.** Our Giza clip 2 was the warning.
- **Top-down drone is a still-only shot.** It has no background streak, so it cannot read as fast in motion.
- **Still car + fast camera is formally the single exception,** once per reel, never first or last.
- **Weather continuity between clips** is now a hard check.

---

## 11. Checklists

### Before generating a clip
- [ ] Shot code chosen (A–H), one subject motion, one camera behaviour, one or two emitters named.
- [ ] Speed number in GOAL and "No slow motion, no gentle movement" in EXCLUSIONS.
- [ ] "The wheels and rims visibly spinning" in every SHOT line and "No frozen wheels" in EXCLUSIONS.
- [ ] The still shows the car already moving (blurred wheels, trail or tail out), car and landmark both readable.
- [ ] Two near layers in the still and in the prompt: something 5–30 m from the car to streak, something 1–3 m from the lens to whip past. A distant landmark alone is not motion.
- [ ] Cut contrast with the previous clip: at least two of angle / car size / lens and height / vector change (§8).
- [ ] Beats have times in seconds; the first line says the first frame is exactly the still.
- [ ] A [CONTINUITY] line with the floor plan: camera spot, the car's line, where the landmark and the near objects are; passed objects never return, heading changes only by driving, the car comes out of dust on the same line. Read the SHOT lines once more as that camera: does every beat make sense from that spot?
- [ ] "The angle on the car does not change" in CAMERA; no forbidden words (§9.2).
- [ ] Screen direction matches the previous clip.
- [ ] Not the exception shot as the opener or the ending; at most one exception per reel.
- [ ] Opener generated alone first, frame 0 checked, before the batch.

### Judging a generated clip (score each 1–5; post only if every line is 4+)
- [ ] Speed: background smeared the whole clip, car crosses/grows in the target time.
- [ ] Wheels: visibly spinning every frame the car moves. Frozen rims on a moving car is a reject, whatever the rest looks like.
- [ ] Camera: one behaviour, constant angle, level horizon, no drift into an orbit or a glide.
- [ ] Readability: car and landmark recognisable every half second; no blocked frame over 0.5 s.
- [ ] Physics: wheels on the ground, debris from the tyres, gravity, weight transfer, shadow and contact.
- [ ] Continuity: car colour and shape unchanged from the still, weather and light matching the other clips.
- [ ] Space: one place seen from one spot. Nothing passed comes back, the landmark stays on its side, the car's heading never flips (not behind dust, not across a pan), the car is where that much time at that speed would put it.
- [ ] Energy: 4–5 (3 for the ending only).
- [ ] Realism: film grain, blur, halation, silhouette; no tells from §7.3.

### Judging the stitched reel
- [ ] Frame 0: car + landmark + motion, readable in under a second.
- [ ] Shot codes alternate; no two identical in a row; screen direction holds.
- [ ] Every cut is a jump: the first frames of consecutive clips differ in at least two of angle, car size, lens/height, vector. No cut reads as a stutter.
- [ ] Every clip has visible motion in its near layers for its whole length, not only in the road texture.
- [ ] Energy curve 5-4-5-4-3 (or 5-5); the peak clip has the environment event.
- [ ] Cuts on the music's hits.
- [ ] The ending's trail or dust is still moving on the last frame.
- [ ] Total 15–22 s.
