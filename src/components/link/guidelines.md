# Link · Usage guidelines

A link takes the person somewhere else: another page, a section of the same page, or a file.

- **Built on:** the native `<a href>`
- **Types:** one, always underlined; standalone (label-md) or inline (inherits the paragraph)
- **States:** default, hover, focus
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#link](https://al.guilhermedesignd.com/#link)

## Do and don't

| Do | Don't |
|---|---|
| **A link goes somewhere:** another page, a section, a file. | **A link that opens a modal:** the screen reader says "link" and the person expects to leave. |
| **Inline inherits the paragraph:** same size, same line height. | **An inline link bigger than the text:** it breaks the line. |
| **The label names the destination:** "View privacy policy". | **"Click here":** out of context, in a list of links, it says nothing. |
| **Standalone with the arrow:** it reinforces "go forward". | **An icon inside running text:** it misaligns the line. |
| **The underline in every state.** | **A gray "visited" link:** it reads as disabled. |
| **Focus shows the ring from the keyboard.** | **A thicker underline as the only focus cue.** |
| **On the canvas or the surface, underlined.** | **No underline to "clean up" the orange:** the link starts depending on color alone. |

### The underline is never removed

This is the rule that makes the component's contrast exception acceptable. The default orange falls below 4.5:1 in the light theme and on the dark surface, and that's only acceptable because the underline, not the color, is what separates the link from text.

## Rules

### When to use

**1. Use it to go somewhere.**
Another page, another section of the same page, or a file to download. Where the person goes is a Link; what they do is a Button.
*Precedents: Primer and Carbon.*

**2. Never for an action on the page.**
Opening a Modal, submitting a form, expanding a block: use the Ghost Button. The screen reader announces "link", and the person expects to leave.
*Precedent: Primer.*
> **Conscious divergence** from Polaris, which allows actions on a link.

**3. Never as the main action of the screen.**
It has less visual weight than any Button and carries no action hierarchy.
*Precedent: Carbon.*

### Inline and standalone

**4. Inside running text, the link inherits the paragraph's font.**
Size, line height and weight. A link bigger or smaller than the text around it breaks the line.
*Precedent: Carbon.*

**5. On its own, the link uses label-md.**
The default interface size of AL.
*Precedent: Carbon.*

**6. Few links per paragraph.**
Many links compete with each other and tire keyboard users.
*Precedent: Carbon.*

### Label

**7. The text says where the link goes.**
"View privacy policy", never "click here" or "learn more" on their own: screen reader users browse a list of links out of context.
*Precedents: Primer and WCAG 2.4.4.*

**8. The same text means the same destination.**
Two links to different places get different texts.
*Precedent: WCAG 2.4.4.*

**9. A short phrase, with no final period.**
Inside running text, the punctuation stays outside the link.
*Precedent: Carbon.*

### Icon

**10. The icon goes on the right only, and it's optional.**
It reinforces the destination: an arrow to go forward, an external-link icon. The arrow is recommended on a standalone link, not required.
*Precedent: Carbon.*

**11. No icon inside running text.**
It misaligns the line and draws too much attention. The inline modifier hides it.
*Precedent: Carbon.*

**12. The icon is decorative.**
`aria-hidden="true"`: the text already says it all. If the link opens in a new tab, that goes in the text, not in the icon alone.
*Precedent: WCAG 3.2.5.*

### States

**13. The underline is there in every state.**
1px at rest, 2px on hover and focus. It's what separates the link from text, not the color.
*Precedents: Primer and WCAG 1.4.1.*

**14. There is no visited state.**
In a product interface people come back to the same screens all the time, and marking them visited doesn't help. If a content site needs it, it comes in as an evolution of the component, with its own color that reaches 4.5:1.

**15. There is no disabled link.**
If the destination isn't available, remove the link and show plain text. A link that goes nowhere confuses the keyboard and the screen reader.
*Precedents: Primer and GOV.UK.*

### Accessibility

**16. Always a real `<a href>`.**
Never a `<span>` or a `<div>` with a click handler: without `href`, the link leaves the tab order and loses "open in new tab".
*Precedents: Primer and WCAG 4.1.2.*

**17. Focus is the Button's ring.**
2px of `bg-canvas` and 2px of `border-focus`. A thicker underline alone isn't enough as a focus indicator. In Figma the ring doesn't show because the frame has no fill; in code it works.
*Precedent: WCAG 2.4.7.*
> **Known limitation** of Figma, the same as the Ghost Button's.

**18. A new tab is the exception, not the default.**
When it happens, say so in the label: "(opens in a new tab)".
*Precedents: WCAG 3.2.5 and Carbon.*

### The contrast exception

**19. The default uses the brand orange even below 4.5:1.**
3.34:1 on the light canvas, 3.12:1 on the light surface and 4.36:1 on the dark surface. A design decision about the action color, paid for by rule 13: the underline never leaves, so the link never depends on color alone.
> **Conscious divergence** from Primer, which asks for 4.5:1.

**20. Never remove the underline to make up for the color.**
Without it, the exception in rule 19 has nothing left to stand on.
*Precedent: WCAG 1.4.1.*

**21. Only on `bg-canvas` and `bg-surface`.**
Those are the two backgrounds measured. Contrast is measured against the background, not against the text around the link: the underline already separates them.
*Precedent: WCAG 1.4.3.*

**22. Never on a dark brand background, or inside an inverted Toast or Tooltip.**
The orange disappears there.
*Precedent: WCAG 1.4.3.*

## Out of scope, on purpose

| What | Status | If the need comes up |
|---|---|---|
| Visited state | Doesn't exist | An evolution for content sites, with its own color at 4.5:1. Never gray. |
| Disabled link | Doesn't exist | An unavailable destination is plain text. |
| Separate inline and standalone types | One type | Inline only inherits the paragraph font and hides the icon. |
| Other backgrounds | Not measured | Only the canvas and the surface; a new background goes through the gate first. |
