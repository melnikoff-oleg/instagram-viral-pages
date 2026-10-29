# Video prompt template (Seedance 2.5, 5 s, 9:16, audio on)

Pick the shot code (A–H) and its camera line from `motion-study/sop.md` §4 and §9.3 first; the SOP's rules (constant angle, tracking allowed, no jumps, closest pass 2 m, one emitter per clip) override the notes below where they differ.

The picked frame is attached with the media role **`image`** (the G-Wagon and Lamborghini runs used this; `start_image` under
`omni_reference` is treated as a loose reference and the opening gets redrawn). It is `<<<image_1>>>` in the prompt.
Never name the car model: the frame defines it. Full house examples: `reference-video-prompts.md`.

```
[GOAL] One continuous 5-second shot, vertical 9:16, opening exactly on <<<image_1>>>: <WHAT IS IN THE FRAME, IN ONE SENTENCE, CAR AND LANDMARK>. Keep the car, <THE LANDMARK>, <THE WEATHER>, light and film look from <<<image_1>>> throughout. Real-time speed, no slow motion: the car is doing 100 mph (160 km/h) and the whole clip must feel violently fast. <THE CAMERA LINE FOR THE SHOT CODE, sop.md §9.3>; the car does the moving.

[CONTINUITY] The camera stands <where, in words: on the verge on the near side of the road, low>. The car's line runs <from where to where across the frame>. <The landmark> is <where: behind the road on the far side, left of the car> and stays there. Nothing the car has passed comes back into the frame. The car keeps the heading it has in <<<image_1>>> and only changes it by driving; when dust or spray hides it, it comes out on the same line, pointing the same way, the same distance along. The scene is one real place seen from one spot.

[SHOT | 0-2s] Already at full speed from the first frame, the wheels and rims visibly spinning. <THE FIRST BEAT: the car closes on the lens / launches / the tail steps out>. <WHAT THE GROUND AND THE DEBRIS DO: pure streaks, a rooster tail, spray into the lens>. <THE NEAR LAYERS: posts, grass, a rail, rocks whipping past between the lens and the car; the wall, the base of the landmark, the dunes streaking right behind it>.

[SHOT | 2-5s] <THE SECOND BEAT: the car rips past and away, the camera whips a beat late, the landmark stays big behind it, the car shrinks to two taillights>. The wheels keep spinning fast the whole way.

[CAMERA] <HEIGHT: low, on the ground, on a tripod across the square>, <LENS 24-50mm>, fixed position: a slightly late pan to follow, a jolt when debris hits, the horizon tilting a degree or two, small overshoot and correction. No orbit, no drive-along, no zooms, no cuts, no slow motion.

[STYLE] Analog 35mm film matching <<<image_1>>>: coarse grain, muted <PALETTE OF THIS FRAME>, extreme motion blur on the ground and the debris, the wheels and rims spinning fast and blurred by rotation, halation around <THE HOT LIGHT>, the car slightly soft.

[AUDIO] An engine screaming at full throttle, <TYRES ON THE SURFACE>, <DEBRIS HITTING THE CAMERA AND MIC>, wind, the engine note fading fast as the car escapes. No music, no dialogue.

[EXCLUSIONS] No slow motion, no gentle movement. No frozen wheels: the wheels and rims visibly spin the whole time the car moves. No text, logos or watermark. No other vehicles or people. No change to the car's color or shape. No CGI look.
```

Rules:
- **The wheels spin, always.** Every SHOT line says "the wheels and rims visibly spinning" and EXCLUSIONS says "No frozen wheels". Seedance happily renders a car moving with its rims standing still (the Mustang × Monument Valley clips), and it looks terrible. "Blurred into discs" alone does not do it.
- Speed is stated twice (GOAL and EXCLUSIONS) with a number. "Glides", "rolls", "steady", "smooth", "gentle", "slow" never appear unless the beat is the still ending.
- One camera behaviour per clip and the angle on the car never changes: locked, matched track alongside, follow/lead, or one pan. It never orbits a moving car, never descends, never combines moves (`motion-study/sop.md` §5).
- The opener's first frame must contain both the car and the landmark, large. If the picked image does not, pick another image.
- **Near layers, every clip.** Something 5–30 m from the car that streaks and something 1–3 m from the lens that whips past, named in the SHOT lines. A landmark far behind the car does not move at any speed (the Mustang × Monument Valley opener: the butte a kilometre back, the clip read as a glide). The references keep rails, verges, posts and arches metres from the camera.
- **Cut contrast.** The first frames of consecutive clips must differ in at least two of: the angle on the car, the car's size in the frame, the lens and camera height, the car's vector (crossing / toward / away). Two side three-quarters in a row with the same backdrop (Mustang clips 1 → 2) is a stutter, not a cut. Check this on the contact sheet before generating the videos.
- A drift is written as physics: fast entry, the tail stepping out, a wide arc with counter-steer, smoke from the rear tyres, an exit past the lens. Never "a steady drift angle around a circle".
- **The space must make sense (sop.md §7.1 rule 7).** Write the floor plan first (camera spot, the car's line, where the landmark and near objects are) and put it in the [CONTINUITY] line, then write every beat as what that camera sees. Objects the car has passed do not come back, the landmark stays on its side, the car never changes heading except by driving, and it comes out of dust or spray on the same line pointing the same way. The Mustang reel had the car enter its dust tail-first and leave nose-first, and a butte passed on one side reappear on the other: that is a reject even when every frame is beautiful.
- The funny ending is the one clip allowed to end still: three beats (set-up, the gag, the aftermath), one clear physical action, a flinch on impact.
