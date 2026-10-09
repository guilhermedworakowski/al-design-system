# Breadcrumb · Usage guidelines

A breadcrumb shows **where the page sits in the hierarchy**, with a link to each level above it.

- **Depth:** Short, Medium, Large (5 levels or more collapse into "…")
- **Behavior:** `breadcrumb.js` opens the "…" menu
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#breadcrumb](https://al.guilhermedesignd.com/#breadcrumb)

## Do and don't

| Do | Don't |
|---|---|
| **4 levels, all visible:** it still fits, and every level is one click away. | **"…" hiding a single item:** one more click for a level that would fit on the line. |
| **The full label, the trail wraps:** on a narrow screen, onto the next line. The link and its chevron move together. | **A truncated label:** the ellipsis hides exactly the word that tells the level apart. |

### Collapse only from 5 levels

Up to 4 levels, the whole trail stays visible. The "…" only comes in with 5 levels or more (rule 5).

## Rules

### When to use

**1. A hierarchy with 3 levels or more.**
With a single level, the trail becomes noise.
*Precedent: Carbon.*

**2. Not for the progress of a linear flow.**
A multi-step sign-up needs a progress indicator.
*Precedents: GOV.UK, Carbon.*

**3. With the Sidebar, only the two levels below it.**
If the Sidebar already shows where the person is, the trail repeats it.
*Precedent: GOV.UK.*

**4. Hierarchy, not history.**
The path is the same no matter how the person got there, and it's a single model across the product.
*Precedent: Carbon.*

### Depth

**5. Short, Medium and Large are depth.**
Up to 4 levels, all visible; with 5 or more, Large.
*Precedents: Spectrum (at most 4 visible), eBay.*

**6. Large: first, second, "…" and the current page.**
The middle ones go into the menu, from highest to lowest.
> **Conscious divergence** from Carbon, which shows the first and the last two.

### Position

**7. One per page, at the top, above the title.**
On `bg-canvas` or `bg-surface`, never inside a Card, Modal or Drawer.
*Precedents: GOV.UK, Carbon.*

**8. The first item is the real root.**
"Home" or the name of the area, never the logo.
*Precedent: GOV.UK.*

**9. Nothing clickable right next to the "…".**
It measures 12×20 and only meets the WCAG 2.5.8 minimum target thanks to the 24px of space around it.

### Content

**10. The label repeats the title of the destination page.**
Short and with no punctuation.
*Precedents: GOV.UK, Carbon.*

**11. The current page is the last item.**
With the same name as the page title.
> **Conscious divergence** from GOV.UK and Carbon v10, which leave it out.

**12. No ellipsis in the trail.**
On a narrow screen it wraps onto the next line; in the menu, the width grows.
*Precedent: Terra.*
> **Conscious divergence** from Queensland, which doesn't wrap.

**13. The separator is always the chevron.**
No slash, and no icons on the items.
*Precedent: Spectrum.*

### Behavior

**14. The trail has no hover.**
Only the cursor changes: it's secondary navigation, and the context already says they're links. Carbon underlines; here it's a design decision.

**15. The current page isn't a link.**
It doesn't click and doesn't receive focus.
*Precedent: Carbon.*

**16. The "…" opens the menu.**
It closes with Esc (focus returns to the "…"), with a click outside, or when a link is chosen.
*Precedent: Carbon.*

**17. Menu items are links, not actions.**
No `role="menu"`; Tab moves through them.
*Precedent: W3C, the disclosure pattern.*

**18. No disabled or loading state.**
A page with no parent has no breadcrumb. No reference system provides these states.

### Accessibility

**19. `<nav aria-label="Breadcrumb">` with an `<ol>`.**
The order has meaning.
*Precedents: Carbon, Primer, W3C.*

**20. `aria-current="page"` on the last one.**
*Precedents: Primer, W3C.*

**21. The separator is decorative.**
Hidden from screen readers, so people don't hear "arrow" at every level.
*Precedent: W3C.*

**22. The "…" is a button with a name.**
"Show more pages", with `aria-expanded` and `aria-controls`.
*Precedent: Carbon ("more breadcrumbs").*

**23. Color is never the only cue for the current page.**
It's also the last item, it's marked for screen readers, and it isn't a link. WCAG 1.4.1.

**24. Focus ring on links and on the "…".**
The default one, with a 4px corner. Menu items use the Tab Square ring.

### Exceptions and what pays for them

**25. The menu border falls below 3:1.**
`borda-de-regiao` (region border): the menu is a content box, not a control, and it separates through its shadow. Don't darken it. The same case as the Sidebar and the Card.

**26. The menu background is always `bg-surface-raised`.**
With the `-raised` hover and pressed states. Changing the background makes the hover disappear in dark mode (Modal 0.18.1).

### Out of scope

**27. No home icon, no per-item menu, no history, no larger size.**
If the need comes up, it opens a new round at step 1. Spectrum has a per-item menu; AL doesn't.

**28. It doesn't replace the back button.**
Polaris swapped the trail for a back action. In AL, the two are separate.
