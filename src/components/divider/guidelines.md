# Divider · Usage guidelines

A divider is a line that separates **groups** of content.

- **Built on:** the native `<hr>` (announced by default)
- **Orientation:** horizontal (default), vertical
- **Style:** one color (`border-default`) and one thickness (1px)
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#divider](https://al.guilhermedesignd.com/#divider)

## Do and don't

| Do | Don't |
|---|---|
| **Heading and space also separate:** someone who can't see the line still sees two blocks with two headings. | **Only the line separates:** without the line, four identical items. With it, two groups that only the line reveals. |

### The line is never the only cue

This is the rule that makes the component's contrast exception acceptable. The line falls below the 3:1 of criterion 1.4.11 on every surface, and that's only acceptable because the criterion applies to what is **needed** to understand the screen. If the grouping depends on the line alone, the exception no longer holds.

## Rules

**1. Space before a line.**
Use a divider only when space and alignment aren't enough. Not every block needs a line.
*Precedent: Material, "use dividers sparingly".*

**2. Groups, not items.**
No line between every item in a list or menu: it goes between one group and the next.
*Precedents: Material and Primer's ActionList.*

**3. It doesn't replace a container's border.**
Cards, fields and modals have their own border, with their own token.
*Precedents: Carbon and Primer, where each component uses its border token, not a divider.*

**4. No divider at the start or the end, and never two in a row.**
Right against the container's edge, it becomes a double line; at the ends, it separates nothing. The markup gate rejects all three cases.
*Precedent: Primer, which only places dividers between groups.*

**5. Horizontal between stacked blocks, vertical between side-by-side items.**
Sections, menu groups and a card footer on one side; actions in a toolbar and metadata on the same line on the other.
*Precedents: Spectrum and Material.*

**6. The length comes from the container.**
Don't set a width or height. The vertical one needs a flex or grid parent to get its height, and it only exists between side-by-side items.

**7. One color and one thickness, always.**
`border-default` and 1px. Don't swap it for `border-subtle`, `border-strong` or the brand color "for emphasis": hierarchy comes from headings and space.
*Precedent: Polaris.*
> **Conscious divergence** from Spectrum, which has three thicknesses.

**8. The line is never the only cue for the grouping.**
Space, a heading or the structure also show the separation. It's what makes the contrast exception acceptable.
*Precedent: WCAG 1.4.11.*

**9. The same space on both sides.**
Always from the `space-*` scale. Uneven space "sticks" the line to one of the groups. How much space is the layout's decision: AL doesn't set a value.

**10. Indentation is a margin, not a variant.**
In a list with an icon or avatar, the line can start aligned with the text.
*Precedent: Material's inset divider, done here with a margin.*

**11. No text inside the divider.**
To name the group, use a section heading above it.
*Precedent: Material, which pairs the divider with a subheader.*

**12. The default is `<hr>`, announced.**
The screen reader says "separator". Use it when the line marks a change of subject or section.
*Precedents: HTML's thematic break and WAI-ARIA's `separator` role.*

**13. A decorative divider gets `aria-hidden="true"`.**
When the structure already separates: between buttons, in a card with headings, between groups that are already lists. Hearing "separator" there is noise.
*Precedents: Queensland Design System and Sara Soueidan.*

**14. An announced vertical divider states its orientation.**
`aria-orientation="vertical"`: the separator is horizontal by default.
*Precedent: WAI-ARIA.*

**15. In a list, the line is an item too.**
`<li role="separator">`, never a loose `<hr>` inside a `<ul>`: invalid HTML breaks the item count the screen reader announces.
*Precedents: the WAI-ARIA menu pattern and Primer.*

**16. Never focusable or clickable.**
A focusable separator in ARIA is something else: the splitter that resizes panels.
*Precedent: the WAI-ARIA Window Splitter pattern.*

**17. What doesn't exist, and what to do if the need comes up.**
See below.

## Out of scope, on purpose

| What | Why |
|---|---|
| Extra thicknesses and colors | Emphasis comes from headings and space, not from a thicker or orange line. |
| Text in the middle | The "or" between two options is a section heading, not a divider. |
| Indentation as a variant | It's a layout margin. |
| Draggable divider | Resizing panels is another component, with its own focus and keyboard behavior, to discuss when the need comes. |
