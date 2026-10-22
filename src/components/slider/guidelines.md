# Slider · Usage guidelines

A slider picks a value inside a range when the position matters more than the exact number.

- **Built on:** the native `<input type="range">`
- **Size:** one, at the container's width
- **States:** Default, Hover, Active, Focus, Disabled; no error, it always holds a value
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#slider](https://al.guilhermedesignd.com/#slider)

## Do and don't

| Do | Don't |
|---|---|
| **Volume, brightness, a search radius:** adjusted by the effect. | **An exact amount:** that is the Number field. |
| **The value next to the label, with its unit.** | **A slider with no number:** the track alone carries the value. |
| **A limit that can't be passed:** min and max do the work. | **An error message on a slider:** it never leaves the range. |
| **Disabled with a reason nearby.** | **Disabled with nothing that says why.** |
| **The visible label names the control.** | **An aria-label that repeats the visible label.** |
| **One thumb, one value.** | **Two thumbs on one track:** use two Number fields. |

### The value in text pays for the track

The fill sits below 3:1 against the track (2.53:1 light, 2.2:1 dark), the same exception as the Progress. It is only acceptable because the number next to the label always says the value.

## Rules

### When to use

**1. When the position in the range matters more than the exact number.**
Volume, brightness, a search radius: the person adjusts by the effect.
*Precedent: Material (continuous slider).*

**2. When the exact number matters, use the Number field.**
Landing on an exact number by dragging is frustrating.
*Precedent: Carbon, which pairs a number input with its slider for that reason.*

**3. Only in ranges short enough for every step to be reachable.**
0 to 10,000 in 320px is 31 units per pixel.
*Precedent: Carbon.*

**4. Not for a few named options.**
Small, Medium, Large is a Radio or a Select. A slider says a continuous range, not categories.
*Precedent: Material, discrete marks only on a numeric scale.*

### Content

**5. The label is always visible and says what is adjusted.**
"Volume", never "Adjust".
*Precedent: Polaris.*

**6. The current value sits to the right of the label, with its unit.**
"60%", "15 km". It is the value in text that pays for the track below 3:1.
*Precedents: Polaris and Carbon.*

**7. Show value only turns off when the value shows somewhere else.**
A live preview of the effect, for example. Without the number, the track would be the only cue.

**8. The limits show when they are not obvious.**
Turn them off on a 0 to 100% scale everyone knows.
*Precedent: Carbon.*

**9. Limits and value share the same unit and format.**
"0 km", "50 km". A change of format makes the person convert in their head.
*Precedent: Polaris.*

### Behavior

**10. The effect is either immediate or sent with the form.**
A display setting applies at once; a filter in a form waits for Submit. Never both on the same screen.
*Precedents: AL's Switch and Polaris.*

**11. No error state.**
A slider always holds a valid value. If part of the range is not allowed, change min and max.
> **Conscious divergence** from Polaris, which validates its range slider: AL's never leaves its limits.

**12. The initial value is always a real value, never empty.**
A range control has no empty state.
*Precedent: the native range input.*

**13. The step belongs to the form and is said when it is not 1.**
"In steps of 5".
*Precedent: Polaris.*

### States

**14. Disabled only when the person understands why.**
Preferably with a line of text nearby. Its contrast is exempt (WCAG 1.4.3), as in the Switch and the Checkbox.

**15. Hover and active fall below 3:1 in dark on surface and surface-raised.**
A declared exception: they are transient, and the resting thumb passes 3:1 on all three backgrounds.

### Accessibility

**16. A native `<input type="range">`.**
Arrows move one step, Page Up and Page Down ten, Home and End go to the limits.
*Precedents: Shopify, which recommends the native range input, and Carbon.*

**17. The visible label is the control's name.**
`<label for>`, never a repeated `aria-label`.
*Precedent: Carbon.*

**18. With a unit, the announcement carries it.**
`aria-valuetext="60%"`: "60" alone does not say percent or kilometers. `slider.js` writes it from `data-unit`.
*Precedent: APG slider pattern.*

**19. The thumb has a 24px target.**
Drawn at 20px, the input row is 24px tall (WCAG 2.5.8).

**20. Focus shows an inner gap in `bg-canvas`, then the ring.**
Without the gap, the orange ring reads as a bigger thumb in light.

**21. A click on the track moves the thumb.**
Dragging is never the only way to change the value (WCAG 2.5.7).

### Out of scope

**22. No range with two thumbs.**
If the need appears, use two Number fields, minimum and maximum.
*Precedent: Polaris, which pairs text fields with its dual slider.*

**23. No tick marks, no value bubble, no vertical slider.**
The value already sits in the header.
*Precedent: Carbon has no vertical slider either.*

**24. One size, at the container's width.**
The Tier 2 rule.

## Out of scope, on purpose

| What | Status | If the need comes up |
|---|---|---|
| Range (two thumbs) | Does not exist | Two Number fields, minimum and maximum. |
| Tick marks | Does not exist | Back to stage 1 as a new type. |
| Value bubble | Does not exist | The value is in the header. |
| Vertical | Does not exist | Not planned. |
| Error state | Does not exist | Change min and max. |
