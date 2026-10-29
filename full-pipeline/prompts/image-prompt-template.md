# Image prompt template (Flux 2 pro, 2K, 9:16)

Header, then four short paragraphs, Camera → Tone → Lighting → Texture. No headings inside the prompt.
`<<<image_1>>>` is the car, `<<<image_2>>>` and `<<<image_3>>>` are the two @iamnotsrc style references.

Write "Analog 35mm film photograph", not "film frame" (that can come back as a literal film border).

```
<<<image_1>>> is the car: match its exact model, body shape, <COLOUR> color and details (<THREE OR FOUR ICONIC FEATURES>). <<<image_2>>> and <<<image_3>>> are visual style references only: match their film grain, muted color, motion blur and cinematic feel, but don't copy their subjects.

Analog 35mm film photograph, vertical 9:16, <LENS> <DISTANCE AND HEIGHT>, <SHUTTER / PANNING>, <WHERE THE CAR SITS IN THE FRAME AND WHICH WAY IT TRAVELS>, <WHERE THE LANDMARK SITS AND HOW BIG>, nothing in the frame perfectly sharp.

<MOOD IN THREE WORDS>, <ONE LINE OF STORY>. The <COLOUR> supercar from <<<image_1>>> <ACTION> <PLACE DETAIL>, <ONE DYNAMIC ELEMENT: dust, spray, smoke, snow>, <WHAT THE PLACE IS DOING>.

<TIME OF DAY AND SKY>, no sun in frame, exposed for the sky so the car falls into a warm near-black silhouette, the only bright source <THE ONE HOT LIGHT>, slightly clipped and blooming with strong halation, casting a small glow on the ground beneath it, <HOW THE LANDMARK IS LIT>.

Coarse film grain with colored speckle most visible in the sky, muted low-saturation color with cool highlights and warm brown shadows, <THE BLUR: panning streaks, rotational blur, rain streaks>, the car slightly soft with no crisp detail, <HAZE / DUST / RAIN NEAR THE LENS>, like an unpublished set still shot on motion-picture film.
```

Rules that bit us:
- The opener must show the car AND the landmark, both large, in one frame: that is the first frame of the reel. A car on a road with the landmark somewhere behind is a fail.
- Name the landmark twice in top-down and worm's-eye prompts, or it gets dropped.
- A drift frame shows the car on a wide arc with the tail out and smoke behind the rear tyres, mid-corner, not parked in the middle of a drawn circle.
- Flux copies the reference's orientation. If every candidate faces the wrong way, mirror the reference before uploading or write the whole series in that direction.
- Say "nothing perfectly sharp" in the Camera paragraph, or the car comes out crisp.
- Don't single out one detail as clear.
- Short lists. Long detail lists pull the model toward crisp rendering.
- Keep people out of the frame, and keep the landmark big: "filling the background", "rising out of the top of the frame".
- Put the near layers in the still, because the clip can only move what the still contains: something close behind the car (the base of the landmark, a wall, posts, a rail, rocks, 5–30 m) and something close to the lens (a post, grass, a rock, blurred, 1–3 m). A car alone on a road with the landmark far away makes a clip with nothing moving in it.
- The four stills must read as four different shapes: angle on the car, car size, lens and height, vector. Two consecutive stills with the car in the same place at the same angle on the same backdrop cut like a stutter (`motion-study/sop.md` §8, cut contrast).
- One hot light per frame. Floodlit arches count as accents, not as the light.
