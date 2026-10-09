# Tab · Usage guidelines

Tabs switch between **related content of the same level** on the same screen, or between pages in a section.

- **Types:** Line, Square
- **Uses:** panel (`role="tab"`) or navigation (links)
- **Size:** one size (Line 42px, Square 32px)
- **Behavior:** `tab.js` handles arrow keys, Home and End in the panel use
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#tab](https://al.guilhermedesignd.com/#tab)

## Do and don't

| Do | Don't |
|---|---|
| **Line outside, Square inside:** the line separates the page's sections; the tonal block chooses within them. | **Square outside, Line inside:** the inner level gets more weight than the outer one, and the hierarchy flips. |
| **Short, parallel labels:** one-word nouns, all of the same kind. | **A label that turns into a sentence:** a verb, a long phrase, a different level from its neighbors. Write "Items". |

### Tabs inside tabs: two levels at most

The first level is Line, the inner one is Square, living in the panel of the tab above. A third level calls for another pattern.

## Rules

### When to use

**1. Related content, of the same level, on the same screen.**
Tabs organize siblings, not parent and child.
*Precedents: Polaris, Carbon, Material.*

**2. Don't use them to compare.**
If the person needs to see two tabs at the same time, show them side by side.
*Precedents: Carbon, Polaris.*

**3. Don't use them for steps in a sequence.**
Tabs have no required order, and skipping a tab can't leave the task broken.
*Precedent: Polaris.*

**4. Line for pages and navbars; Square for bounded areas and the sidebar.**
The line only makes sense horizontally, which is why the sidebar is always Square.
*Precedents: Carbon Line/Contained, Material.*

**5. An item that leads to another page is a link.**
Same look, navigation markup (rule 22).
> **Conscious divergence** from Primer, which has two components for this.

### Hierarchy and combination

**6. One type per group.**
Mixing Line and Square makes the selection read in two ways.
*Precedents: Carbon, Material.*

**7. Exactly one selected.**
On opening, the first one, unless the screen remembers the last one.
*Precedents: Polaris, APG.*

**8. From 2 to 6 tabs.**
With only one, it's a heading. Above six, use side navigation.
*Precedent: Carbon.*

**9. The group fits the width.**
There's no scrolling in this version. If it doesn't fit, shorten the labels or change the pattern; never two rows of tabs.
*Precedent: Spectrum.*

### Size and layout

**10. One size.**
Square 32px and Line 42px. Don't resize: 32px already passes the WCAG 2.5.8 minimum target of 24px.

**11. Tabs side by side, with no space between them.**
The breathing room between labels comes from each tab's padding, and that's what keeps Line's line continuous.

**12. The line ends at the last tab.**
Don't complete it with a Divider: the Divider is 1px and the tab's line is 2px, and the step shows.

**13. The panel comes right below the group.**
Nothing between the tabs and the content they switch.
*Precedents: APG, Carbon.*

### Content

**14. A label of one or two words.**
A noun that says what's inside: "History", not "View history".
*Precedents: Carbon, Polaris.*

**15. Only the first letter capitalized.**
"Personal details", not "Personal Details".
*Precedent: Spectrum.*

**16. The label fits on one line.**
It doesn't wrap and doesn't get an ellipsis. If it doesn't fit, rewrite it, and count on translation stretching the text.
*Precedents: Carbon, Spectrum.*

**17. Parallel labels.**
The same kind of word and the same level of detail across the group.
*Precedent: Polaris.*

### States

**18. There's no disabled tab.**
Unavailable content leaves the group. Empty content stays, and the panel explains why it's empty.
*Precedents: Primer, Polaris.*

**19. Clicking the open tab does nothing.**
It doesn't reload, and it doesn't scroll the panel back to the top.

**20. Switching tabs doesn't erase what was typed.**
The panel that leaves is hidden, never destroyed.

### Accessibility

**21. The panel use follows the APG tabs pattern.**
A named group, one Tab stop, arrow keys, Home and End. A tab opens when it receives focus if the content is already on the page; when it loads from the network, only with Enter or Space.
*Precedents: APG, Primer.*

**22. Navigation is a list of links.**
A named `<nav>`, `aria-current="page"` on the current one, Tab goes through all of them and the arrow keys do nothing. Never `role="tab"` on a link: it promises a panel that doesn't exist.
*Precedents: Primer, APG.*

**23. Focus is the resting state plus the ring.**
The background doesn't change, and the ring only appears with the keyboard.
*Precedents: WCAG 2.4.7; the AL Button, Input and Card.*

**24. In high contrast mode, the selection stays visible.**
The selected tab's line takes the system's highlight color, and the selected Square gets an outline. The same lesson as the Divider.

### Contrast exceptions, and what pays for them

**25. The panel starts with a heading equal to the label.**
It's what pays for `selecao-tonal` (tonal selection): in dark mode, the selected Square is told apart only by hue, and the heading says where the person is. The screen reader already hears "selected" or "current page".
*Precedents: Material, Carbon.*

**26. The gray line is only a track.**
`trilho-decorativo` (decorative track): it doesn't communicate state, so don't use the color for anything else and don't darken it to "fix" it. `marca-no-hover-escuro` and `pressed-na-superficie-escura` belong to the brand, inherited from the Foundation and the Button.

## Out of scope, on purpose

| What | Why |
|---|---|
| Icon and counter | Not in this version. |
| Scrolling | The group fits the width (rule 9). |
| Vertical tabs | A vertical panel group doesn't exist. A stacked sidebar is a list of links. |
| Closing a tab | Doesn't exist. |
| A second size | One size only (rule 10). |
| Disabled | Doesn't exist (rule 18). |
| Full sidebar item | Full width with the label on the left belongs to the Sidebar: it stretches the Square. |
