# Carousel · Usage guidelines

A carousel shows a row of items of the same kind in a space that only fits a few, and lets the person move through them.

- **Built on:** a `<section>` with native `<button>` arrows (the Icon Button Secondary sm) and `carousel.js`
- **Size:** one; the slide width is the layout's
- **States:** the arrows' own, disabled at the ends; no auto-rotation
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#carousel](https://al.guilhermedesignd.com/#carousel)

## Do and don't

| Do | Don't |
|---|---|
| **Items of the same kind to browse:** photos, related cards. | **The page's main message in rotating banners.** |
| **The next slide cut at the edge, the arrows below.** | **Arrows over the image, slides that fit exactly.** |
| **A visible title above, each slide standing on its own.** | **"Continued on the next slide."** |
| **The arrow at the end turns off.** | **A loop back to the first slide.** |
| **Named arrows; the dots only show where you are.** | **Clickable dots as the only way to move.** |
| **The person moves it.** | **Auto-rotation.** |

### The shape pays for the dots

The current dot against the others measures 1.46:1 in light and 1.10:1 in dark. It is only acceptable because the shape carries the state (a 24px pill against an 8px dot) and the dots are decorative: `aria-hidden`, no focus, no click.

## Rules

### When to use

**1. For items of the same kind the person browses.**
Product photos, related cards, a portfolio: seeing all of them is not required.
*Precedents: Material (multi-browse) and Porsche.*

**2. Never for the page's main message or for competing banners.**
Use a static highlight. People ignore what looks like an ad, and in tests they fail even when the answer is on the first slide.
*Precedents: NN/g and Yale.*

**3. Never hide content the task needs.**
Most people never get past the first slide.
*Precedents: NN/g and Smashing.*

**4. From 3 to 10 slides.**
With 1 or 2, show them side by side; with more than 10, use a grid with the Pagination.
*Precedent: Smashing; the ceiling of 10 is AL's.*

### Composition

**5. One carousel per visible area.**
Two sets of identical arrows side by side make it unclear which one moves what.
*Precedent: Smashing.*

**6. Every slide has the same width, and the next one shows cut at the edge.**
The cut is the visual cue that there is more. The width is the layout's: `--al-carousel-slide-size`.
*Precedent: Material (uncontained).*
> **Conscious divergence** from Material's multi-browse: AL has no mixed slide sizes.

**7. The controls sit below the content, never over it.**
Dots on the left, arrows on the right. Over an image, an arrow would lose its contrast.
*Precedent: the W3C carousel tutorial asks for clearly visible controls.*

**8. The space around the carousel is the layout's.**
The same rule as the Divider and the Card.

### Content

**9. A visible title above it, which also names the region.**
`aria-labelledby` points to it: one name for sighted people and screen reader users.
*Precedent: APG carousel pattern.*

**10. Each slide stands on its own.**
No "continued on the next slide": the person may skip slides or stop at the first.
*Precedent: NN/g.*

**11. An image that informs has alt text; a decorative one has an empty alt.**
*Precedent: the W3C image tutorial, applied to its carousel tutorial.*

**12. A clickable slide uses the Card's stretched link.**
Never two links in the same slide.
*Precedent: AL's Card rules.*

### Navigation and states

**13. The arrows turn off at the ends, with no loop.**
A loop takes away the sense of a start and an end.
*Precedent: APG, whose manual carousel needs no loop.*

**14. Each arrow moves one page: as many slides as fit whole.**
The first slide that was cut becomes the first one of the new page, so no slide is ever skipped.
*Precedents: Material and Smashing.*

**15. Touch and trackpad scroll freely and snap to the nearest slide.**
*Precedent: Material.*

**16. Smooth scrolling turns off when the person asks for less motion.**
*Precedent: AL's Motion tokens and WCAG 2.3.3.*

**17. No auto-rotation, ever.**
Without a pause button it fails WCAG 2.2.2, and it hurts people with less motor control.
*Precedents: NN/g, APG and W3C.*

**18. A slide with no image, or a failed one, shows `bg-subtle`, and the alt text stays.**
*Precedent: AL's Avatar fallback.*

### Accessibility

**19. A `<section>` with `aria-roledescription="carousel"`, named by its title.**
Each slide is a `role="group"` with `aria-roledescription="slide"` and a label such as "2 of 5".
*Precedent: APG carousel pattern.*

**20. The arrows are native `<button>`s named "Previous slide" and "Next slide".**
At the ends they get `disabled`, and focus moves to the other arrow so it never falls back to the page.
*Precedents: the W3C carousel tutorial and APG.*

**21. After an arrow, a polite live region says which slides are in view.**
"Slides 3 to 4 of 5". Swipe and trackpad announce nothing.
*Precedent: the W3C carousel tutorial ("Item x of y").*

**22. The dots are decorative: `aria-hidden`, no focus, no click.**
The current one is told apart by its shape, which pays for the dot-shape exception.
> **Conscious divergence** from APG, which prefers clickable picker buttons: AL keeps the basic carousel.

**23. Focus entering a slide out of view scrolls it into view.**
Focus is never hidden (WCAG 2.4.11). The browser does it natively.

### Out of scope

**24. No auto-rotation, vertical carousel, loop, mixed sizes or thumbnail navigation.**
If the need appears, it goes back to stage 1 as a new version. The empty slide against the page is exempt from 3:1: it is content, not a control, and on surface-raised in dark the content draws its own edge.

## Out of scope, on purpose

| What | Status | If the need comes up |
|---|---|---|
| Auto-rotation | Does not exist | A static highlight (rule 2). |
| Clickable dots | Does not exist | The arrows move it (rule 22). |
| Loop | Does not exist | The arrows turn off at the ends. |
| Vertical | Does not exist | A list or a grid. |
| Thumbnails as navigation | Does not exist | Back to stage 1 as a new version. |
