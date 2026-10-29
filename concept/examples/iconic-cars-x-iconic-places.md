# Concept: Iconic Cars × Iconic Places

## The idea in one line
Iconic cars in iconic places, shot like stolen frames from a feature film: analog, moody, physical, and always moving.

## What the account is
Short vertical series (4 frames → 4 clips of 5 seconds each, stitched into one reel of about 20 s). Each series pairs **one legendary car** with **one place anyone recognizes in under a second**, then plays with that place through weather, angles and a small storyline that ends on a funny beat.

The feeling we want: *"this looks like a real behind-the-scenes still from a big-budget film that never existed."*

## The three pillars

### 1. Instant recognition
- The viewer must know **what car** and **where** within the first second of the first clip.
- The landmark is visible from frame 0 of clip 1, never revealed later.
- The car's most iconic features must read clearly, even when blurred: the G-Wagon's box and round headlights, the 911's rounded fastback, the Murciélago's wedge.

### 2. Cinematic analog look
- Vertical **9:16**, always.
- It should feel like an **unpublished set still from a feature film**: shot on motion-picture stock by someone standing far away with a long lens, catching the moment slightly imperfectly.
- **Nothing tack sharp.** Real photos are imperfect; crisp digital detail is what makes AI images look fake.
- The full breakdown is in "The look, in detail" below.

## The look, in detail

### Sky
- **Cloudless, smooth twilight gradient**: cool blue or lavender at the top fading to dusty rose, salmon or peach near the horizon. No clouds, no visible sun. The sun has *just* set (civil twilight).
- The sky is **50–70% of the frame**. It's negative space that makes the subject feel small, lonely and mythic.
- Grain is **most visible in the sky**: coarse, chromatic speckle (blue, magenta and yellow dots) over the smooth gradient. This is the single strongest "real film" signal.
- Variations keep the same logic: grey snowy dusk, storm haze or blue hour, but always a smooth, bright, low-detail backdrop against which the subject reads dark.

### Horizon and ground
- **Low horizon.** The subject sits on or just above it, usually in the lower or middle third, and its silhouette breaks the horizon line.
- The **ground is dark**, warm brown to near-black, and takes the bottom 30–40% of the frame. It's soft, out of focus or streaked with motion.
- Distant terrain (mountains, skylines, ruins, trees) appears as **flat, hazy layers**, blue-grey or dark umber, softened by atmosphere.
- A thin **layer of haze, dust or smoke** often sits near the ground, catching warm light and adding depth.

### Subject and silhouette
- The subject reads mostly as a **dark silhouette**. Exposure is set for the bright sky, so the subject falls into shadow.
- Blacks are **crushed but warm** (brown-black, never neutral grey-black). Detail appears only where the subject is lit by its own light.
- Small **graphic silhouettes** on the horizon (a dead tree, a smokestack, a ruined wall, a tower) add story without clutter.

### The single hot light source
- Every frame has **one dominant warm light that belongs to the subject** (in our world: headlights, taillights, brake glow, sparks, a burning trail).
- It's the brightest thing in the frame: a hot orange-to-yellow core, **slightly clipped**, with **strong halation and bloom** bleeding into the air around it.
- It **casts a glow onto the ground directly beneath** the subject. That small pool of warm light anchors the subject physically.
- Everything else is cool or muted, so this light pops through contrast, not saturation.

### Color grade (the "LUT")
- **Split toning**: cool blue and lavender in the highlights (sky), warm orange in the light source, brown and umber in the mids and shadows.
- **Low overall saturation.** The only saturated color is the hot light (and the colors of an iconic landmark, slightly muted).
- Slightly **faded, milky highs** in the sky with **deep, warm shadows** on the ground.
- Reads like pushed tungsten motion-picture stock (500T-style) shot at dusk.

### Lens, distance and framing
- **Default: long telephoto (135–300mm) from far away.** The subject is small to mid-size, perspective is compressed, and the background is flattened against the subject.
- **Composition is simple**: centered or slightly off-center, with huge negative space. Often near-symmetrical when the background allows it.
- **Frames within frames** are welcome: a dark architectural mass or opening framing a window of bright sky, with the subject small at the bottom.
- Occasional **wide, low shots** for aggression, but still with lots of sky and a single light source.

### Blur and focus
- **Panning motion blur**: the background and ground streak horizontally; the subject is soft but readable by shape.
- The subject itself is **slightly soft**, with a touch of missed focus or motion smear. It's never perfectly crisp, and **no single detail is sharper than the rest**.
- The light source smears into **horizontal trails** when moving.
- Foreground ground and debris are **out of focus**.

### Mood
- **Lonely, mythic, quiet intensity**: the calm in the middle of something wild.
- Action is shown at its **peak moment** (mid-jump, mid-slide, mid-wheelie), with nothing staged or posed.
- It always feels **caught**, not composed for an advert.

### Reusable style block for prompts
Paste and adapt this into the Lighting and Texture paragraphs:

> Civil twilight just after sunset, no sun in frame, a smooth cloudless sky fading from cool lavender-blue at the top to dusty rose and peach at the horizon. Exposed for the sky, so the subject falls into a warm near-black silhouette, the only bright source its own hot warm light, slightly clipped and blooming with strong halation, casting a small glow on the ground beneath it. Coarse film grain with colored speckle most visible in the sky, muted low-saturation color with cool highlights and warm brown shadows, panning motion blur streaking the dark ground and background, the subject slightly soft with no crisp detail, a thin warm haze near the horizon, like an unpublished set still shot on motion-picture film.

### 3. Dynamics
**`motion-study/sop.md` is the full motion rulebook and overrides this section where they differ** (it allows matched tracking alongside the car, forbids jumps, and sets the structure at 4 clips of 5 s).
- Every frame has motion baked in: spray, dust, snow, a slide, a drift. The car is never standing.
- **Real-time speed, never slow motion.** The car is doing 100 mph (160 km/h) unless the beat says otherwise, and the clip must feel violently fast. Say it in the GOAL and forbid it in the EXCLUSIONS ("No slow motion, no gentle movement"). Models default to a slow cinematic glide when nobody forbids it.
- **One camera behaviour per clip, constant angle on the car.** Locked, a matched track alongside, a follow/lead on the car's line, or a single pan from a fixed spot. It never orbits a moving car, never descends, never combines two moves. The car does the moving, fast, through or across the frame; the closest pass is 2 m from the lens.
- The operator is a human, not a robot: slightly late on the action, overshoots, small reframing corrections, a horizon tilting a degree or two. Never jittery, never chaotic.
- Snow, sand, water or slush **hitting the lens** is the easiest free dynamic.
- **Physics must look real.** A drift is a car entering fast, the tail stepping out, a wide arc with the front wheels counter-steered, smoke from the rear tyres only, and an exit. A car does not rotate on the spot like a turntable. **No jumps, no airborne car**: the airborne Murciélago was the least real clip we have made.

## Series structure (4 frames → 4 clips of 5 s)

| # | Role | Typical shot (`motion-study/sop.md` shot codes) |
|---|------|--------------|
| 1 | **Iconic opener**: car and landmark instantly readable, car already at speed | Side track (A) or oncoming (C), low, landmark large behind |
| 2 | **Play**: the car having fun with the place | Drift arc past a low camera (F) or drift ride (G), smoke/sand/snow pouring off the rear tyres, tire tracks as graphics |
| 3 | **Peak**: the place's beauty and its weather at full intensity in one frame | Storm, blizzard, sandstorm, night, reflection on wet ground or ice, landmark half-veiled; follow (D) or fixed-point pan (E) |
| 4 | **Funny ending**: a simple, absurd, ground-level beat | Drive-away with the trail outliving the car (B), a nose-first plunge into a drift, a snowman smashed |

The old "atmosphere" slot (reflections, golden light, the landmark half-veiled) is folded into the peak: beauty and weather in the same frame. Five seconds per clip gives each beat room to breathe; four clips keep the reel near 20 s.

**Rules for a series**
- **Screen direction stays consistent.** If the car travels right → left in frame 1, it travels right → left in every frame (or turns on screen, never just flips between cuts).
- **Light and weather progress logically**: dusk → blue hour → storm → night, or calm → storm → calm.
- **Stay in or near the place.** The landmark (or something next to it) appears in at least 3 of 4 frames. Don't escape to unrelated locations.
- **Vary angle and background in every frame.** Never two side profiles in a row with the same backdrop. Between consecutive frames at least two of these change: the angle on the car, the car's size in the frame, the lens and camera height, the car's vector (crossing, toward, away). Otherwise the cut reads as a stutter (`motion-study/sop.md` §8).
- **Near layers in every frame.** The landmark can be big and far, but something must sit 5–30 m from the car (a wall, posts, the landmark's base, rocks) and something 1–3 m from the lens, or the clip has nothing to move: a distant landmark does not move at any speed.
- The ending should be **funny but physically simple**: one clear action, not a complex gag.

## Cars and places: endless combinations

The cars, places and pairings below are **just a few examples to spark ideas**. The real pool is effectively infinite: any car with an iconic silhouette can meet any place people recognize instantly, and every pairing can be shot in countless weathers, seasons, times of day and storylines. Treat these lists as a starting point, never a limit.

## Cars

Pick cars with a silhouette people recognize instantly, even blurred or backlit. Some ideas:

- Mercedes G-Wagon (matte black): boxy silhouette, perfect against snow and bright skies
- Lamborghini Murciélago (yellow or orange): a sharp wedge, great in desert tones
- Porsche 911 GT3 RS (silver-white with red details): rounded fastback, big wing
- Ferrari F40 (red): low, angular, iconic wing
- Lamborghini Countach (white or red): pure 80s wedge
- Porsche 911 classic 964/993 (black or Guards Red): the rounded original
- Nissan Skyline GT-R R34 (Bayside Blue): JDM icon
- Toyota Supra Mk4 (orange or white)
- Mercedes 300SL Gullwing (silver): doors-up moments
- Ford Mustang 1967 Fastback (dark green or black)
- Land Rover Defender classic (green or sand): rugged, boxy
- Lada Niva or Volga (humor and nostalgia, for Russian places)
- Bugatti Chiron (two-tone): hypercar contrast against ancient places
- Rolls-Royce Phantom (black): slow, regal, rainy-city moods

**Color rule:** pick the color that contrasts most with the place. Dark cars on snow and bright skies, bright cars in desert and dusk tones. Avoid colors that merge with the background (white car in snow, red car against red walls).

## Places

The landmark must be recognizable in under a second, even blurred. Some ideas:

- Giza pyramids, Egypt: desert, sand, dunes, sandstorm, camels, giant moon
- Red Square, Moscow: St. Basil's, the Kremlin wall, Spasskaya Tower, snow, blizzards, the frozen river
- Burj Khalifa, Dubai: night skyline, empty highways
- Eiffel Tower, Paris: riverside roads along the Seine
- Sydney Opera House: waterfront roads across the harbour
- Manhattan, New York: elevated highways, skyline across the river
- Colosseum, Rome: dusty, warm, ancient stone
- Golden Gate Bridge, San Francisco: fog rolling in, wet roads
- Big Ben and Westminster, London: rain, double puddles, night
- Taj Mahal, India: dawn haze, mist, reflections in water
- Mount Fuji and Tokyo neon: snow-capped peak, rainy Shibuya nights
- Times Square, NYC: snowy night, neon reflections
- Hollywood Sign and LA hills: dry heat, sunset, dust
- Monument Valley, USA: red rock, open roads
- Machu Picchu, Peru: mountain fog
- Petra, Jordan: canyon, pink stone
- Iceland: black sand beach, glaciers, aurora (iconic nature over a building)
- Santorini, Greece: white walls, blue domes, narrow roads

**Example pairings** (a handful out of countless possibilities)
- G-Wagon × Red Square
- Murciélago × Pyramids
- 911 × Burj Khalifa
- Ferrari F40 × Colosseum
- Skyline R34 × Tokyo neon in rain
- Mustang '67 × Monument Valley
- Countach × Miami / Hollywood at sunset
- Rolls-Royce × London in the rain
- Defender × Iceland
- Bugatti × Petra

## Weather and light palette
- **Twilight pink**: a smooth rose-to-lavender cloudless sky (our signature)
- **Grey snowy dusk**: blue-grey, falling snow, warm floodlights
- **Golden backlight**: low sun behind a landmark, glowing dust or spray
- **Blue hour moonrise**: a giant moon, crisp silhouettes
- **Storm**: sandstorm, blizzard, fog, heavy rain; one strong warm light (taillights, lamps) cutting through
- **Night with practical lights**: streetlamps, floodlit landmarks, wet-road reflections

## Shot types to rotate
- **Low telephoto side profile**: the classic, landmark compressed behind
- **Low front three-quarter**: aggressive, headlights at the lens
- **Top-down drone**: the car as a graphic shape, tire tracks as lines
- **High angle from a rooftop**: the car tiny in a vast space
- **Worm's-eye**: the camera on the ground, the car or landmark looming
- **Dutch angle**: a tilted horizon for storms and chaos
- **Rear three-quarter chase**: the car racing into something (storm, fog)
- **Reflection**: the car mirrored in wet road, ice or water
- **Extreme wide**: the car a small dark shape, the place dominates
- **Silhouette against a light source**: moon, low sun, floodlit building

Skip interior shots unless there's a real interior reference.

## Prompting rules (learned the hard way)

### Image prompts
- Structure: **Camera → Tone (mood + subject + action + setting) → Lighting → Texture**, in four short paragraphs, no headings inside the prompt.
- References: `@image1` = the car (match the exact model, shape, color and details); `@image2` and `@image3` = style references only (grain, color, blur, framing, without copying their subjects). Check the order in the generation tool.
- Always write **vertical 9:16**.
- State the blur explicitly and early: slow shutter, slightly missed focus, "nothing perfectly sharp". Otherwise models default to a crisp subject.
- Don't single out one detail as "clear", or the model renders it razor-sharp while everything else is blurred.
- **Physics must be believable.** Realistic ramp sizes and jump heights, suspension extended in the air, a shadow under airborne cars, and objects actually on the car's path. In a side profile, put things "on the same line, at the same distance from the camera".
- Keep shapes simple. Complex graphics drawn in snow or sand (smileys, letters) don't work.
- Keep outfit and gear lists short; long detail lists pull the model toward crisp rendering.
- Don't mention people in the car.
- Avoid "masterpiece", "8K" and similar filler.

### Video prompts
- Structure: **[GOAL] → [CONTINUITY] → [SHOT | timecodes] → [CAMERA] → [STYLE] → [AUDIO] → [EXCLUSIONS]**.
- Length: **5 seconds**.
- Open **exactly on the generated frame** (`@image1`) so the first second is iconic: car and landmark both readable in the first frame. Attach the frame with the media role `image` (not `start_image`, which Seedance 2.5 treats as a loose reference and redraws the opening).
- State the speed: "Real-time speed, no slow motion: the car is doing 100 mph (160 km/h) and the whole clip must feel violently fast." Repeat it in the exclusions.
- **The wheels spin.** Say "the wheels and rims visibly spinning" in every SHOT line and "No frozen wheels" in the exclusions. Video models will move the car with its rims standing still unless told, and nothing looks more fake.
- Say explicitly: *"This is not a static shot,"* and describe what moves relative to what.
- **Think the space through before the beats.** One camera spot, one line for the car, the landmark on one side: write it as a [CONTINUITY] line and keep every beat consistent with it. What the car has passed stays behind it, the landmark never jumps sides, the car's heading changes only by driving and survives a dust cloud unchanged. A beautiful clip whose geometry contradicts itself (the car enters dust tail-first and leaves nose-first) is a reject.
- **One camera position per clip.** A 24–50mm lens close to the action; the camera pans and flinches from where it stands, it does not orbit, descend or drive along. Parallax comes from the car passing close, not from the camera travelling.
- Reliable dynamic beats: the car passes close to the lens, then a late whip pan; the car launches away from a standing camera; a drift arc that sweeps past the lens; snow or spray hitting the lens.
- The camera is human: slightly late, overshoots, small bumps. Avoid "handheld struggling, doubled edges", which reads as jitter.
- Audio: raw on-location engine, wind, tires and debris. **No music, no dialogue.**
- Exclusions: no text, logos or watermark, no extra vehicles or people, no change to the car's color or shape, no CGI look.
- Don't name the car model in video prompts. The frame already defines it.

## Tone of the account
Confident, a little cheeky, beautiful but never glossy-advert. It feels like film, not CGI. Each reel should make people stop for the place, stay for the motion, and laugh at the ending.
