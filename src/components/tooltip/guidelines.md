# Tooltip · Usage guidelines

A tooltip shows a **short, complementary text** about a focusable element, usually the name of an icon-only button.

- **Look:** inverted, always with an icon, no arrow, 280px wide at most
- **Position:** top by default, flips on its own
- **Behavior:** `tooltip.js`, on hover (after 500ms) and on focus (immediately)
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#tooltip](https://al.guilhermedesignd.com/#tooltip)

## Do and don't

| Do | Don't |
|---|---|
| **The action:** what the button does, in one word. | **The drawing:** people who can't see the icon gain nothing; people who can already knew. |
| **An optional complement:** the button works without reading the tooltip. | **A paragraph with a link:** too long, and the link can't be reached. That's text on the page. |

## Rules

### When to use

**1. To name an icon-only button.**
People who see the icon have no other way to know what it does.
*Precedents: Polaris, Primer.*

**2. Only what's short and complementary, never essential.**
Touch has no hover: on mobile, the tooltip doesn't exist.
*Precedents: Carbon, Primer, Intuit.*

**3. What's needed to finish goes in the help text.**
The field's help text, always in view.
*Precedent: Carbon.*

**4. Don't repeat what's already written.**
A "Save" button with a "Save" tooltip is just noise.
*Precedent: Polaris.*

**5. Not for errors, validation or confirmation.**
Those belong to the form message, the Toast and the Alert.
*Precedent: Spectrum.*

### Content

**6. One short sentence, two lines at most.**
Within 280px. Beyond that, it isn't a tooltip.
*Precedents: Shopify, Emarsys (100 to 150 characters).*

**7. Only the first letter capitalized, no period on a fragment.**
*Precedents: Intuit, Polaris.*

**8. Name the action, not the drawing.**
"Delete", never "Trash can icon".
*Precedents: Emarsys, Primer.*

**9. The keyboard shortcut can come along.**
"Save (Ctrl+S)".
*Precedent: Polaris.*

**10. Nothing clickable inside.**
The tooltip never receives focus: a link there can't be reached.
*Precedents: Carbon, Shopify.*

### Icon

**11. The icon is decorative.**
`aria-hidden`: the text carries the meaning.
*The Icon contract.*

**12. In the text color.**
`currentColor`, with no color of its own.
*The Icon contract.*

### Position

**13. On top by default, flips on its own.**
Below if it doesn't fit; left and right for a trigger right against the edge.
*Precedents: Spectrum, Polaris.*

**14. No arrow, 4px away.**
The same recipe as the Breadcrumb menu, with no variants in Figma.
> **Conscious divergence** from Carbon and Spectrum.

**15. It never covers the trigger.**
*Precedent: WCAG 1.4.13.*

### Behavior

**16. Hover waits 500ms, focus opens immediately.**
So it doesn't flicker when the mouse just passes over.

**17. It stays open over the trigger or over itself.**
With 100ms of slack for the pointer to cross the gap.
*Precedent: WCAG 1.4.13.*

**18. Esc closes it without moving focus.**
*Precedent: WCAG 1.4.13.*

**19. One at a time.**
Two floating texts compete to be read.

**20. It doesn't open on click or tap.**
Content that opens on click is another component, the toggletip.
*Precedent: Carbon.*

**21. It fades in and out in 200ms.**
A `motion-duration-popup` fade; no transition with reduced motion.

### Accessibility

**22. Only on focusable elements.**
A button, link or field. On plain text, the keyboard never gets there.
*Precedent: Primer.*

**23. Never on a disabled element.**
It doesn't receive focus. To explain a block, use `aria-disabled`.
*Precedent: Primer.*

**24. A name uses `aria-labelledby`, a complement uses `aria-describedby`.**
And the tooltip always has `role="tooltip"`.
*Precedents: Primer, W3C ARIA1.*

**25. Right after the trigger in the HTML.**
*Precedent: Primer.*

### Out of scope

**26. Clickable content.**
AL has no toggletip: use text on the page, a Modal or a Drawer.
*Precedent: Carbon.*

**27. Colored variants.**
Use a Toast or an Alert.
*Precedent: Spectrum.*

**28. Rich tooltip, with a title and an action.**
*Precedent: Material.*
