# Realistic Image Prompt Template

## Camera → Tone → Lighting → Texture (CTLT)

Use this guide to turn your idea into a photograph-like image, even when the scene is surreal.

Source: https://docs.google.com/document/d/1ZFozAy-EtTMvBGM5YwGizuYlzmnYXOUu8qonyqlNXX8/edit

---

## 1. Blank template – CTLT formula

Fill in the empty right-hand cells. Optional details can be left out.

| Part | What to think about | Your sentence |
| :-- | :-- | :-- |
| **Camera** | Lock down the camera settings, such as the lens size (e.g., 35 mm lens) and framing (e.g., waist up). | |
| **Tone** | Set the mood, atmosphere and emotional energy first. Then describe who is in the image, what they are doing and where it happens. | |
| **Lighting** | Define the lighting direction and quality (e.g., warm sunset from camera right). | |
| **Texture** | Specify physical details and materials that interact with the environment (e.g., silk catching motion, stray hair across the face). | |

**Your final prompt**

Combine the completed rows in order: Camera → Tone → Lighting → Texture.

---

## 2. Filled-in demo

The same template, completed for the skeleton chase example.

| Part | What to think about | Your sentence |
| :-- | :-- | :-- |
| **Camera** | Lock down the camera settings, such as the lens size (e.g., 35 mm lens) and framing (e.g., waist up). | 35mm film photograph, 12mm fisheye lens, slightly elevated side view, full-body framing, crooked composition and slight motion blur. |
| **Tone** | Set the mood, atmosphere and emotional energy first. Then describe who is in the image, what they are doing and where it happens. | Frantic, absurd and darkly comic, like an unexpected chase caught by a passerby. A skeleton wearing a dress made of raw meat sprints down a Los Angeles street at night, with three dogs chasing close behind the skeleton. |
| **Lighting** | Define the lighting direction and quality (e.g., warm sunset from camera right). | Harsh direct flash, hard shadows on the road, bright foreground and dark background. |
| **Texture** | Specify physical details and materials that interact with the environment (e.g., silk catching motion, stray hair across the face). | Matte bones, glossy marbled meat, visible fat, meat flapping with movement, coarse dog fur, rough asphalt and film grain. |

**Ready-to-paste prompt**

> Candid 35mm film photograph with a 12mm fisheye lens, slightly elevated side view, wide full-body framing, tilted horizon and slight motion blur.
>
> Frantic, absurd and darkly comic, like an unexpected chase caught by a passerby. A skeleton wearing a dress made of raw meat sprints down a Los Angeles street at night, with three dogs chasing close behind the skeleton.
>
> Harsh direct on-camera flash lights the skeleton and nearby dogs, casting hard shadows across the asphalt while the parked cars and street behind them fall into darkness.
>
> Matte ivory bones, glossy marbled meat with visible fat and uneven edges flapping with each stride, coarse dog fur, rough asphalt and visible film grain.

---

## 3. Optional: let an LLM tidy up your idea

Copy the text below into your preferred LLM, replace the final placeholder with your idea, then paste the resulting image prompt into your image generator.

```text
Turn my idea into an image-generation prompt that feels like a real moment caught by a photographer.

Use the CTLT structure in this exact order:

1. Camera: photographic style, lens, shot size, viewpoint and framing. Keep the camera choices coherent.
2. Tone: start with the mood, atmosphere and emotional energy. Then describe the subject, action and setting within the same paragraph.
3. Lighting: light source, direction and quality, and how the light falls on the subject and surroundings.
4. Texture: physical details, materials and surfaces, and how they interact with the environment. Include two or three visible qualities that support realism.

Preserve my idea. Add only what helps the image; don't invent extra subjects, props or elaborate backstories.

Use grain, flash, motion blur or imperfect framing only when they suit the scene and photographic style. Avoid generic claims like "masterpiece" or "8K."

Don't add reference-image tags unless I supplied reference images. If I supplied references, preserve their actual @image1, @image2 labels and state what each reference contributes.

Return one ready-to-paste prompt in four short paragraphs: Camera → Tone → Lighting → Texture. Keep the subject, action and setting inside Tone, with no separate Scene paragraph. Do not include headings inside the prompt.

Then add a brief Camera / Tone / Lighting / Texture breakdown.

My idea: [PASTE YOUR IDEA]
```
