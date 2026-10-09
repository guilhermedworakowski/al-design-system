# Accordion · Usage guidelines

An accordion item shows a heading and **hides secondary content** until the person opens it.

- **Built on:** the native `<details>` and `<summary>`, with no JS
- **Size:** one size (76px closed)
- **Behavior:** several items open at once by default; one at a time with `name`
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#accordion](https://al.guilhermedesignd.com/#accordion)

## Do and don't

| Do | Don't |
|---|---|
| **On a surface:** the edge shows in both themes. | **Straight on the canvas:** white on white leaves a loose heading with an arrow. |
| **A real heading before the stack:** people who navigate by headings find the stack; the item's title is visual. | **A button inside the header:** two buttons in the same place. Does the click open it or cancel? The action goes in the content. |

### Where it lives

The item's background is the raised surface. On the light canvas it measures 1.00:1 and disappears; on `bg-surface`, the gray of the page draws the edge.

## Rules

### When to use

**1. Secondary content.**
FAQs, details, advanced settings: what not everyone needs to read.
*Precedents: Carbon, Polaris.*

**2. Never hide what's essential.**
Errors, warnings, required actions or information everyone needs stay in view. Not everyone notices the item opens.
*Precedents: GOV.UK, Polaris.*

**3. If the person is going to read everything, don't use it.**
Use the page with regular headings: every closed item is one more click.
*Precedents: Carbon, GOV.UK.*

**4. Accordion or Tab.**
In an Accordion the content stacks and several items open. To switch between content of the same level, one at a time, use the Tab.
*Precedents: Carbon, Polaris.*

**5. Never one inside another.**
Nesting hides content inside hidden content.
*Precedents: Carbon, Spectrum.*

### Combination and stacking

**6. A single item works.**
The "view details" of a summary.
*Precedents: Primer Details, Polaris Collapsible.*

**7. The same space across the whole stack.**
There's no group component: whoever builds the page chooses the space, from the scale, equal between all items.
*Precedent: Spectrum.*

**8. Several open by default.**
One at a time (`name`) only when the items are alternatives.
*Precedents: Carbon, GOV.UK, Primer.*
> **Conscious divergence** from Spectrum, which opens one at a time by default.

**9. All closed on load.**
Only the item the person was taken to, through a direct link, starts open.
*Precedents: Carbon, GOV.UK.*

### Size and layout

**10. One size only.**
76px closed. Don't reduce the padding or change the font. The whole header is the target, well above the 24px of criterion 2.5.8.

**11. The container's width.**
The 320px in Figma is the example's measurement.
*Precedent: Carbon.*

**12. A long heading wraps.**
No ellipsis: truncating hides the summary that helps the person decide whether to open it. The icons stay aligned with the first line.

**13. The chevron sits at the end.**
The heading lines up with the rest of the page's text. There's no left-side option.
*Precedent: Carbon.*

**14. Always on `bg-surface`.**
Straight on the light canvas the item measures 1.00:1 and disappears. Inside a Card, it's the same color as the card. This is the rule that makes the background contrast exception acceptable.
*Precedent: Card Filled.*

### Content

**15. The heading summarizes the content.**
Short, in sentence case. In FAQs, the heading is the question.
*Precedents: Carbon, Spectrum.*

**16. Parallel, distinct headings.**
The same structure across the stack, none repeated.
*Precedents: Polaris, GOV.UK.*

**17. Nothing clickable in the header.**
No link, button or Switch: the header is already the button. Actions go in the content.
*Precedent: APG.*

### Icon

**18. A leading icon is decorative.**
Optional, hidden from screen readers; the heading does the talking. In a stack, either all items have one or none do.

**19. The chevron is decorative too.**
Down when closed, up when open. The state reaches the screen reader through the native markup.
*Precedent: APG.*

### States

**20. There's no disabled state.**
An item with no content leaves the stack.
> **Conscious divergence** from Carbon and Spectrum, which disable the group.

**21. Only the header reacts.**
The content never changes background: it isn't clickable.
*Precedent: APG.*

**22. Focus is the resting state plus the ring.**
Keyboard only. The ring hugs the header and sits on top of the content.
*Precedent: WCAG 2.4.7.*

**23. Opening doesn't move focus.**
Focus stays on the header and the page doesn't scroll.
*Precedents: Primer, APG.*

### Accessibility

**24. Native, with no ARIA.**
`<details>` and `<summary>`: the browser announces open or closed and responds to Enter and Space.
*Precedent: MDN.*

**25. The real heading comes before the stack.**
No `<h3>` inside the `<summary>`: in some screen readers it drops out of the headings list. If the stack needs to be found by heading, put one before it.
*Precedent: APG.*

**26. Find in page doesn't open items in every browser yet.**
In Chrome and Edge, Ctrl+F opens the item that has the text; in the others, it doesn't. One more reason not to hide what's essential.

**27. High contrast mode adds an outline.**
In that mode the background disappears, and each item gets an outline in the system text color.

**28. Two declared exceptions.**
The divider falls below 3:1: it only separates, and the chevron says whether the item is open. The item barely separates from the page by its background, which is why it lives on `bg-surface`.

## Out of scope, on purpose

| What | Why |
|---|---|
| Group component | The stack is items placed together; the space belongs to the layout. |
| Another size | Only one in this version. |
| Disabled | Doesn't exist (rule 20). |
| No background, for a card or side panel | Carbon's "flush". It comes in when the need appears. |
| Open and close all | Primer and GOV.UK have it; AL doesn't yet. |
| Chevron on the left and content loaded on open | They open a new scope round. |
