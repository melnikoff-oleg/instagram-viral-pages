# Run notes: 1967 Ford Mustang Fastback × Monument Valley (2026-10-29)

Third run of `full-pipeline/`, the first on the 4 × 5 s structure (opener, play, peak, funny ending) with the
`motion-study/sop.md` shot codes. About 35 minutes wall clock, 99 Higgsfield credits (16 images at 1.5, 5 clips of 5 s
at 15: four shots plus one retry of the play clip), about $0.90 on Apify for the music, a few cents for Pinterest,
no Anthropic API.

## What was made

- `refs/car.jpg`: #46 of 60 screened by eye from the Pinterest `--screen` sheets (a Highland Green '67 fastback,
  front three-quarter, nose pointing right, whole car clean). #45 (`car-alt-lights.jpg`) is the same car with the
  headlights on, kept as a backup. The nose points right, so the whole series runs **left → right**.
- 16 Flux 2 pro candidates (`contact-candidates.jpg`). Every opener candidate had the car and a butte both large;
  every row was usable except the ending row, where only one candidate faced the right way. Picks in `selected/`:
  1. `12` opener: side three-quarter, headlights on, a rooster tail, the butte filling the top half.
  2. `22` play: the car sliding on the dirt with the tail out and dust behind (the first video attempt used `23`, see below).
  3. `31` peak: the car punching out of a dust wall with the Mitten and the spire readable above, room to grow.
  4. `43` ending, **mirrored**: the only moon-and-dust candidate had the nose pointing left, so it was flipped and
     uploaded as its own media (`uploads.frame_4_mirrored`). Mirroring a picked still is fine when the frame has no
     readable text; the plate is unreadable at this size.
- 5 Seedance 2.5 draft clips. The opener came out right first time (`clips/01.mp4`), clips 3 and 4 too. Clip 2 took
  two attempts (`clips/02-attempt1.mp4`, `clips/02.mp4`).
- Music finder with hand-written searches (dark phonk, drift phonk, western phonk, cowboy phonk, outlaw, desert,
  wild west, muscle car, V8 engine, Arizona, spaghetti western, midnight drive), picked from the table:
  Company Money "Drift Skunk" (1.4M reels, the main variant), 1beatProductions "Outlaw" (104K reels, plays with the
  place), Skrillex, Noisia, josh pan, Dylan Brady "Supersonic (my existence)" (the latest house track). "Wrath" and
  "Say Nothing" topped the table again but were already used on the F40 reel.
- Three reels in `reels/05-mustang-monument-valley/` (local), cut with `--clip-max 3=2.8`: the peak clip is cut right
  after the dust wall rolls over the lens, the rest keep their full length and are beat-snapped. About 17.6 s each.

| Variant | BPM | Drop in the song | Reel | Cuts |
|---------|-----|------------------|------|------|
| drift-skunk | 110 | 17.0 s | 17.6 s | 4.91, 4.91, 2.73, 5.04 |
| outlaw | 133 | 16.6 s | 17.7 s | 4.96, 4.96, 2.71, 5.04 |
| supersonic | 86 | 28.0 s | 17.5 s | 4.86, 4.86, 2.78, 5.04 |

## The clips, judged against the SOP

1. **Opener, shot A (C2 matched track).** Frame 0 is the picked still. The car holds its place while the road
   streaks under it and the dust trail hangs behind; the butte slides slowly as a telephoto track should. It is the
   first tracking opener we have made and it reads as a car at speed without the car ever leaving the frame. It is
   also the quietest clip of the four: if the reel feels slow at the top, `--clip-max 1=3` is the cheap fix.
2. **Play, shot F (C1 + late pan).** The first attempt from candidate `23` (nose toward the lens) rendered as a
   second oncoming pass with the lens blocked by dust for a full second, the same beat as clip 3. The retry from
   candidate `22` (side-on slide) with "the side of the car facing the lens the whole time", "the car never drives
   toward the lens" and "the lens is never covered for more than a moment" written in came out as a lateral pass at
   about two seconds, a late pan, and the taillights tearing away into their own dust. **Pick the drift still by
   where the nose points: a nose at the lens becomes an oncoming shot.**
3. **Peak, shot C (C1 oncoming grow).** Frame 0 is the still with the car mid-frame; it grows to full frame in two
   seconds, passes right, and the dust wall rolls over the camera. After 2.8 s the frame is only dust, hence the cut.
4. **Ending, slide to stop.** Frame 0 is the mirrored still; the car slides right, its own dust cloud catches up at
   two seconds and swallows it, and the last two seconds are two headlight glows inside the red cloud under the
   moon with the dust still moving. Exactly the gag as planned.

Weather continuity holds: dust in every clip, the storm building from the drift to the peak and settling in the
ending. Light goes civil twilight → dusk → blue hour → night with the moon.

## Lessons

- **The wheels do not spin.** The car moves but the rims stand still, which looks terrible. The prompts said "wheels blurred into discs" and the model rendered a static blurred texture. From now on every SHOT line says "the wheels and rims visibly spinning" and EXCLUSIONS says "No frozen wheels" (`motion-study/sop.md` §3, §7.3, §9.2, the video template, CLAUDE.md). This reel is kept as it is, not posted as it is.
- **Too little motion in the opener.** The butte is a kilometre behind the car, so nothing in the frame moves except the road texture, and a 100 mph tracking shot reads as a glide. The references keep rails, verges and posts metres from the camera. Rule added: two near layers in every still and every SHOT line, one 5–30 m from the car, one 1–3 m from the lens (`sop.md` §3, §5.9).
- **The space contradicts itself.** The car goes into its own dust cloud tail-first and comes out nose-first, and the butte is passed on one side of the frame and then shows up on the other. Rule added: a [CONTINUITY] line with the floor plan in every prompt, every beat written as what that camera sees from its spot, passed objects never return, headings never flip (`sop.md` §7.1 rule 7, §7.3, checklists).
- **Cut 1 → 2 is a stutter.** Both first frames are a side three-quarter of the car in the lower half with a butte behind, so the cut barely registers. Rule added: consecutive clips differ in at least two of angle, car size, lens/height, vector (`sop.md` §8, cut contrast); check the contact sheet rows against each other before generating the videos.

- Role `image` still maps to `image_references` under `omni_reference`, and "The first frame is exactly `<<<image_1>>>`"
  in the first SHOT line kept the frame in all five clips.
- The preset recommendation ("IN THE DARK", `24bae836-…`) came back on the first video submission again; resend with
  `declined_preset_id`.
- Mirroring a picked still is a legitimate fix for screen direction when the candidate row only faces one way.
- A dust-on-lens beat is strong once per reel; two in a row read as the same shot. Check the clip strips side by side
  before stitching, not one at a time.
- The forbidden-word check (`sop.md` §9.2) caught "steady" in the opener prompt; run it on every prompt.
- Finalise before posting: these are 480p drafts. `draft_job_id` finalising works until 2026-11-05. Nobody has
  listened to the three tracks yet.
