# Findings: how the reference reels move, and how ours differs

Evidence for `sop.md`. Sources: the six contact sheets in `frames/`, the eye analyses and Gemini reports in `analysis/`, ffmpeg cut detection. Numbers below are from the eye analyses (the contact sheets at 2 fps), cross-checked against Gemini 3.6-flash; where the two disagree it is noted.

## The clip inventory

21 reference clips in five reels, plus our 4.

| Reel | Clips | Lengths (s) | Total | Subject motion per clip | Camera per clip |
|------|-------|-------------|-------|-------------------------|-----------------|
| Ghost Rider (4.2M plays) | 2 | 7.2, 8.3 | 15.5 | straight, straight-away | track alongside, locked |
| Silver Surfer (457k) | 2 | 7.1, 8.1 | 15.2 | carving arc, straight diagonal | rolls with subject, track |
| Iron Man (138k) | 3 | 5.0, 5.0, 5.2 | 15.2 | straight, straight, descend-and-land | pan, track, locked |
| Rocket Raccoon (114k) | 5 | 4.5, 4.5, 4.1, 4.1, 4.2 | 21.4 | straight, still+gun, still+gun, run+gun, still+gun | track, locked, locked, track + whip, locked |
| Batman (150k) | 7 | 3.0, 3.8, 3.1, 2.5, 3.5, 2.1, 4.4 | 22.5 | still, straight-toward, still, straight, straight-away, still, still | slow orbit, lead/track, slow push, track, follow, locked, slow orbit |
| **Ours: Murciélago × Giza** | 4 | 3.1, 3.3, 3.4, 5.0 | 14.8 | straight, drift-into-lens, straight-away, **jump** | track, locked low, follow, locked wide |

## 1. One vector per clip

Every reference clip has the subject doing one thing: travel on a line (12 clips), stay put while something it holds does the work (6 clips: gun, cape, bats), one continuous carving arc (1 clip, Silver Surfer), descend and land (1), run (1). No clip combines two subject motions. No clip changes what the subject is doing halfway through.

Ours: clip 2 asks for three things in 3.3 s (slide toward the lens, sand covers the lens, car passes inside a metre). Clip 4 asks for jump + flight + landing + slide. Both are the clips Gemini scored lowest for realism (3 and 2).

## 2. The subject is pinned; the world moves

In the 12 travel clips the subject stays within roughly a third of the frame width for the whole clip in 9 of them. Speed is read from:
- the background smear (Batman 4 and 5, Rocket 1, Iron Man 1): buildings, arches and lamp posts turned into streaks for the full clip;
- the trail (Ghost Rider 1 and 2, Silver Surfer 2, Iron Man 2): fire, light or exhaust at least one subject-length long;
- growth (Batman 2): the bike grows from a speck to near full frame in ~3 s.

Where there is nothing to smear (Iron Man 2, flat pink sky), the clip reads slower than it is, and the afterburner trails are the only cue. Lesson: always put streakable structure or a trail in the frame.

Ours: clip 1 has the pyramids slide only slightly in 3 s (medium speed read); clip 3 has the storm wall but a soft car; clip 2 has no readable background at all for 1.5 s.

### 2b. Near things carry the speed; cuts are jumps

In the fast reference clips the moving layers are close: Ghost Rider 1 has the verge, the rail and the road markings passing right under the bike, Batman 4 and 5 have arches and lamp posts metres from the camera, Rocket 1 has the walls of the street. Where the only structure is distant (Iron Man 2, our Murciélago clip 1 with the pyramids far behind, our Mustang opener with the butte a kilometre back) the clip reads slower than its stated speed, whatever the prompt says. Parallax comes from proximity, not from speed numbers.

The references also cut between shots that look nothing alike: Ghost Rider goes from a side track with the bike mid-frame to a locked rear shot with the bike shrinking to a dot; Batman alternates stills, oncoming, side track, follow. Our Mustang cut 1 → 2 put two side three-quarters of the car in the lower half of the frame with a butte behind back to back, and the cut reads as a stutter. Both are now rules in `sop.md` (§3 near layers, §8 cut contrast).

## 3. Camera: four behaviours, constant angle

Camera behaviour across the 21 reference clips:

| Behaviour | Clips | Notes |
|-----------|-------|-------|
| Locked off | 8 | Rocket 2, 3, 5; Iron Man 3; Ghost Rider 2; Batman 6; Silver Surfer 1 is close to locked relative to the subject |
| Matched track alongside / parallel | 6 | Ghost Rider 1, Rocket 1 and 4, Iron Man 2, Batman 4, Silver Surfer 2 |
| Follow behind / lead in front on the subject's line | 2 | Batman 5 (follow), Batman 2 (lead/retreat) |
| Single pan from a fixed point | 1 | Iron Man 1 (plus Rocket 4's late whip) |
| Slow orbit or push on a **still** subject | 3 | Batman 1, 3, 7 (Gemini: ~15° and ~45° arcs, a slow push) |
| Fast orbit around a moving subject | **0** | |
| Two moves combined in one clip | **0** | (Rocket 4's track + whip is the only candidate) |

In every one of the 18 moving-subject clips, the camera's **angle on the subject stays the same** for the whole clip. The camera may travel, but parallel to the subject. This is the rule, not "the camera never moves": tracking is the most common moving-subject setup after locked.

The three slow orbits are all on a still person with a cape or a suit, at energy 1–2, used as breathing room between vehicle shots. They work for a hero portrait; a slow orbit of a parked car is a car advert, which is exactly the look we never post. Hence our exception rule: a still car only with a *fast* camera, once per reel, never first or last.

Ours: the camera behaviours are fine on paper (track, locked, follow, locked), but clip 2 puts the camera inside the action (lens covered, car at <1 m), which the references never do: their closest pass is Batman 2 at roughly 2–3 m.

## 4. Every frame has an emitter

| Reel | Emitters |
|------|----------|
| Ghost Rider | flames off the rear wheel, fire trail on the road, embers toward the lens, streaming coat |
| Silver Surfer | sun bloom and spray, light trail, cloud movement |
| Iron Man | thruster flames, afterburners, landing dust, sun flare |
| Rocket | sparks under the bike, muzzle flash (1–2 Hz), shell casings, embers, city bokeh, moon halo |
| Batman | cape in wind, tyre smoke, tunnel lamps streaking, tail light, bats, city traffic lights |

Even the still portraits have something moving (cape, bats, lights). Gemini's pattern line for three of the five reels was the same idea: use flashes, sparks, smoke and trails "to mask AI motion artifacts". Emitters hide the weak spots of the generator and add energy at the same time.

Ours has strong emitters (sand explosion, sandstorm, dust on landing) but they are inconsistent between clips: the storm wall in clip 3 moves slowly, the sand in 2 and 4 explodes. Two speeds of weather read as two different days.

## 5. Fewer, longer clips win

| Reel | Clips | Mean clip | Plays |
|------|-------|-----------|-------|
| Ghost Rider | 2 | 7.7 s | 4.2M |
| Silver Surfer | 2 | 7.6 s | 457k |
| Batman | 7 | 3.2 s | 150k |
| Iron Man | 3 | 5.1 s | 138k |
| Rocket Raccoon | 5 | 4.3 s | 114k |

Five reels is not a statistic, and music and subject matter in, but the direction is clear: the two reels built from two long, simple clips are the two that travelled. Ours: four clips averaging 3.7 s, four separate ideas, none of which gets to breathe.

Gemini flagged a practical reason for the short-clip reels: "Keep clips under 4.5 seconds: cut before AI generation artifacts or morphing become noticeable" (its reading of Rocket). The alternative the top reels use is to make the clip so simple (one vector, pinned subject, big emitter, silhouette) that it holds for 8 s.

## 6. First frame

All five references open on the subject already moving (or, for Batman, already in the wind) with the emitter visible, readable within half a second. Ours does too (car rolling, pyramids big, wheels blurred). No change needed here, except that the opener should be the loudest clip, not the mildest: ours opens at energy 3–4 and peaks later; Ghost Rider and Rocket open at 5.

## 7. Realism: what the references do that ours does not

Common to all five references:
- Silhouette against one hot source (sun, moon, tunnel lamps, fire, city bokeh). Surface detail is in shadow.
- Background motion blur for the full duration of a moving shot; blurred wheels.
- Debris obeys gravity and comes from a contact point: sparks fall, casings arc, embers land and stay, dust settles.
- Weather and light are the same in every clip of a reel.
- Nobody leaves the ground unless they can fly. Vehicles stay on the road.

Ours breaks the last two: the airborne car (Gemini: "anti-gravity floating physics, erratic mid-air arc, camel scale mismatch", realism 2/5) and the two-speed sandstorm. The car's rear also goes soft in clip 3 (480p draft look), and the camels are doll-sized.

AI tells Gemini found in the references, for calibration: wheel spokes losing geometry (Batman 2, 4; Rocket 1), chassis details morphing (Rocket 1), gun barrels warping under muzzle flash (Rocket 2, 3, 5), shell casings spawning in the air (Rocket 5), tunnel arches repeating unnaturally (Batman 5), bats turning into flickering shadow shapes (Batman 6), board/suit texture swim (Silver Surfer), sparks without smoke (Ghost Rider 2), slight wheel jitter (Ghost Rider 1). All of them are hidden by speed, silhouette or an emitter; none lasts long enough on a readable surface to register at Instagram playback size. That is the standard: not zero tells, but zero tells on a readable, slow, well-lit surface.

## 8. Where Gemini and the eye disagree

- **Ghost Rider direction.** Gemini says the bike travels left; the sheet shows it facing right and gaining on the frame rightward. Eye wins.
- **Batman 2.** Gemini reads a side-on tracking shot; the sheet shows the bike growing from a speck at 3.0 s to near full frame at 6.5 s on a diagonal, which is oncoming with a retreating camera (lead). Probably both: a lead-track on a diagonal.
- **Silver Surfer clip 2 "is a repeat loop of clip 1".** ffmpeg finds no cut at 3.5 s and the sheet shows different poses at 0.5/4.5 and 1.0/5.0. Treated as one 7 s clip.
- **Batman 1 and 7 camera.** Gemini sees slow orbits (~15°, ~45°) that the 2 fps sheet only hints at (the skyline shifts). Accepted: the still portraits have slow camera moves.
- Gemini's speed labels ("real-time fast" for nearly everything) are coarser than the eye's frame-crossing estimates; the SOP uses the eye's numbers.

The reports were produced by `gemini-3.6-flash` at 8 fps sampling because the prepaid key was empty and the free-tier key cannot run `gemini-3.1-pro-preview`. Re-run `analyze.py --force` with a topped-up key for pro-level reports; the clip tables will be finer, the rules above are unlikely to change.

## 9. The rules that fall out

1. One subject motion per clip: straight and fast, or one drift arc. Never a jump.
2. Pin the car in the frame; make the background streak or the trail long.
3. One camera behaviour per clip; the angle on the car never changes. Tracking is allowed, orbits around a moving car are not.
4. At least one emitter per clip; the same weather in every clip.
5. Fewer and longer clips: our structure is now 4 clips of 5 s (the references run 2–7 clips of 2–8 s, the best is two long ones).
6. Open on the loudest clip; end on the trail outliving the car.
7. Silhouette the car against one hot light; blur the background and the wheels; keep debris under gravity.
8. Closest pass 2 m; no blocked lens over half a second; nothing unreadable for over half a second.
