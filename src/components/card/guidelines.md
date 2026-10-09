# Card · Usage guidelines

A card groups **one subject** that can be read or acted on by itself.

- **Types:** Filled, Border, Elevated
- **Padding:** Tight (8px), Default (16px), Spaced (24px)
- **Behavior:** static, or clickable with a single action
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#card](https://al.guilhermedesignd.com/#card)

## Do and don't

| Do | Don't |
|---|---|
| Filled on `bg-surface`: the gray page draws the card's edge. | Filled straight on the canvas: white on white leaves loose text. Use Border, or change the page. |
| A clickable card with one action: one target, one announced name (the title). | A clickable card with buttons inside: the button competes with the whole card for the click. Remove the card's click or remove the buttons. |

## Rules

### When to use each type

**1. One subject per card.**
A card holds a subject that reads or resolves on its own. Page sections are separated with a heading and space, not with a card.
*Precedents: Material, Carbon.*

**2. Filled only on `bg-surface`.**
On the white canvas the card measures 1.00:1 and disappears. This rule is what makes the background contrast exception acceptable.
*Precedent: Polaris.*

**3. Border on the canvas or in dense grids.**
Use it where repeated shadows become visual noise.
*Precedents: Material Outlined, Carbon.*

**4. Elevated for emphasis, sparingly.**
If every card floats, none stands out.
*Precedent: Material.*

### Combination

**5. Same type and same padding across a grid.**
Mixing types suggests a hierarchy that doesn't exist.
*Precedent: Material.*

**6. No card inside a card.**
To subdivide, use a Divider or a heading.
*Precedent: Material.*

**7. A card doesn't replace a modal, drawer, accordion or tab.**
Each one is its own component.
*Precedent: Carbon.*

### Padding and size

**8. Choose padding by density.**
Spaced (24) for a standalone or featured card; Default (16) in grids and lists; Tight (8) for small, dense cards.
*Precedents: Primer, Polaris.*

**9. Width comes from the grid, height from the content.**
In a grid, the cards in a row stretch to the same height.

### Content

**10. Title and description are guidance, not requirements.**
When there is a title, use the card's own, so every product speaks the same language. The description adds to the title instead of repeating it. The slot accepts anything else.
*Precedents: Material, Spectrum.*

**11. The title is a real heading.**
`h2`, `h3`… according to the page, never a bold paragraph: screen reader users navigate by headings.
*Precedent: Inclusive Components.*

**12. Explicit actions at the end, one primary.**
On a static card, buttons or links go at the end of the card.
*Precedents: Material, Carbon.*

### Clickable card

**13. One action only, usually navigation.**
With more than one action, the card stays static.
*Precedents: Material, Carbon.*

**14. The arrow is the cue when there is no hover.**
Touch screens have no hover. The title says where the card goes, and an arrow in the corner is recommended, not required.

**15. Nothing clickable inside a clickable card.**
No button, link or checkbox: two overlapping targets confuse touch, Tab and screen readers.
*Precedent: Carbon.*
> **Conscious divergence** from the technique that "lifts" buttons above the stretched link.

**16. The link is the title, stretched.**
A real `<a href>` in the title, never `onclick` on a `<div>` and never a link wrapping the card. The cost is that the text can no longer be selected.
*Precedents: Inclusive Components, Kitty Giraudel.*

**17. The focus ring wraps the whole card.**
One Tab stop per card. On Elevated, ring and shadow together.
*Precedents: Material, Carbon.*

**18. Orange is for focus only.**
Border's hover darkens the border. Never use the brand color to highlight or select a card.

### States

**19. There is no disabled card.**
The card is removed, or its content explains why it isn't available.
> **Conscious divergence** from Material.

**20. There is no pressed state.**
The feedback for the click is the navigation itself.

### Accessibility

**21. The border may fall below 3:1.**
Because a card is recognized by its content. That's why a card must never be empty, outlined only by its line.
*Precedent: WCAG 1.4.11.*

**22. A list of cards is a list.**
`<ul>` and `<li>`, so screen readers announce how many there are. A self-contained card can be an `<article>`.

**23. In dark mode, the background does the separating.**
Shadows barely show in dark mode. Don't compensate by darkening the page or changing the card's background.

**24. What doesn't exist, and what to do if the need comes up.**
See below.

## Out of scope, on purpose

| Need | Answer |
|---|---|
| Selectable card | Use Radio or Checkbox. |
| Expandable card | Use the Accordion. |
| Cover image and fixed actions | They go in the slot, with no variant. |
| Pressed and disabled | They don't exist (rules 19 and 20). |
| Another padding | Discuss the spacing scale, and its name, first. |
