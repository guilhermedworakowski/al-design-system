# Rating · Usage guidelines

A rating collects an opinion on a 1 to 5 scale, or shows an average.

- **Built on:** a `<fieldset>` with five native radios
- **Size:** one, 24px stars
- **States:** Default, Hover, Focus, Disabled, Read-only
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#rating](https://al.guilhermedesignd.com/#rating)

## Do and don't

| Do | Don't |
|---|---|
| **An opinion on a scale:** a product, a delivery, a service. | **A yes or no question:** stars say "more is better". |
| **The legend says what is rated.** | **"Rating" with no subject.** |
| **It starts empty.** | **Three stars checked in advance.** |
| **Read-only for an average, with the number next to it.** | **A disabled rating to show a score.** |
| **Five radios named "1 star" to "5 stars".** | **Five buttons with no group.** |
| **Five whole stars, brand color.** | **Half stars or an amber star.** |

### The preview is transient

The hover preview (`bg-brand-hover`) sits at 1.59:1 light and 1.15:1 dark against a checked star. It is a declared exception: the preview lasts while the pointer is there, and the checked radio carries the value.

## Rules

### When to use

**1. To collect an opinion on a 1 to 5 scale.**
A product, a service, an experience.
*Precedent: Spectrum, a sentiment scale from 0 to 5.*

**2. To show an average, use read-only with the number next to it.**
"4.3 · 128 reviews". Whole stars can't show 4.3; the number can.
*Precedent: WinUI, which recommends the read-only rating for display.*

**3. Not for unordered choices or yes or no questions.**
A star says "more is better".
*Precedent: Spectrum.*

**4. Several ratings in a group, each with its own legend.**
"Service", "Delivery".
*Precedent: eBay EVO, a group named by what it rates.*

### Content

**5. The legend says what is rated.**
"How was the delivery?", never just "Rating".
*Precedent: eBay EVO.*

**6. When the meaning of each score matters, show the chosen one next to it.**
"4 · Very good". A star does not say if 3 is good or bad.
*Precedent: MUI.*

**7. Show label only turns off when the legend is already around it.**
A card title that asks, for example. The accessible name stays.
*Precedent: Polaris, a label always present, even hidden.*

### Behavior

**8. It starts with no star checked.**
Unless the person rated before. A checked start leads the answer.
*Precedents: MUI and Spectrum.*

**9. Once checked, it does not go back to zero in v1.**
If "no rating" is a valid answer, the form offers it outside the rating.
> **Conscious divergence** from MUI and the APG, which clear the score with a click on the checked star.

**10. On hover, the stars up to the pointer turn into a preview in `bg-brand-hover`.**
The checked value stays. The preview is the declared exception, paid by the checked radio.

**11. Required and error belong to the form.**
The message goes below the group; the rating has no error state.
*Precedent: AL's Radio.*

### States

**12. Read-only is a single image, "3 out of 5 stars".**
No focus, no stars of its own: reading five stars one by one is noise.

**13. Disabled only for a rating blocked for now.**
Before the delivery, for example. To show a score, use read-only. Its contrast is exempt (WCAG 1.4.3).
*Precedent: Spectrum, which keeps disabled apart from display.*

**14. Read-only looks the same as Default.**
What changes is the behavior: no focus, no hover.
> **Conscious divergence:** MUI looks the same too; Spectrum has no read-only.

### Accessibility

**15. A radio group.**
A `<fieldset>` with a `<legend>` and five native radios, hidden on top of each star.
*Precedents: APG, MUI and eBay EVO.*

**16. Each radio has its own name, "1 star" to "5 stars".**
The drawn star is `aria-hidden`.
*Precedents: APG and eBay EVO.*

**17. The group takes a single Tab stop, and the arrows move and check.**
*Precedent: APG, roving tabindex.*

**18. The focus ring sits on the checked star.**
With nothing checked, it goes to the first one.
*Precedent: the native radio.*

**19. Color is never the only cue.**
An empty star is an outline and a full one is filled: the shape changes.
*Precedent: MUI, citing WCAG 1.4.1.*

**20. Each star is a 24px target.**
The WCAG 2.5.8 minimum. Never smaller.

### Out of scope

**21. No half stars, no sizes, no other icon.**
One scale, one drawing.
*Spectrum takes decimals; AL left them out in stage 1.*

**22. The star is brand color, not amber.**
`bg-warning` is a dark brown in light (#704F00) and does not read as a star.

## Out of scope, on purpose

| What | Status | If the need comes up |
|---|---|---|
| Half stars | Does not exist | Read-only rounds; the number says the exact value. |
| Clear back to zero | Does not exist | The form offers "no rating". |
| Sizes | Does not exist | One size, 24px. |
| Other icons | Does not exist | Back to stage 1. |
