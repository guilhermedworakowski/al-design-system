# Sidebar · Usage guidelines

The sidebar is the product's **main navigation between destinations**, always visible on the left.

- **Zones:** profile at the top, groups in the middle, Help at the bottom
- **Items:** the full-width Tab Square, as links
- **Size:** one size (296px wide, the screen's height)
- **Below 1024px:** a modal panel from the left, opened by a Menu button
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#sidebar](https://al.guilhermedesignd.com/#sidebar)

## Do and don't

| Do | Don't |
|---|---|
| **Destinations, one of them current:** short nouns that lead to pages. Primer, Material. | **Actions mixed with destinations:** an action is a Button, in the content. Primer, Polaris. |
| **A short label, one line:** if it doesn't fit, the text changes. Material. | **Two current items:** the mark says where the person is: one place only. |

## Rules

### When to use

**1. Main navigation between the product's destinations.**
Visible all the time; it pays off from around 5 destinations, or when people switch areas often. With fewer, use a horizontal bar with Tab Line.
*Precedents: Carbon (side panel above 5 items), Material (drawer for 5 or more).*

**2. An item is a destination, never an action.**
"Create order" or "Sign out" go in a Button, in the content or on the account page.
*Precedents: Primer NavList, Polaris.*

**3. It doesn't switch content on the same screen.**
That's the panel Tab: different markup, different announcement.
*Precedents: Primer (NavList and UnderlinePanels are separate), Tab rule 22.*

**4. One Sidebar per screen, always on the left.**
The right belongs to the Drawer; two navigation columns compete.
*Precedents: Material, Carbon.*

### Structure and hierarchy

**5. Three zones, in this order.**
Profile at the top, groups in the middle, Help at the bottom. Only the middle scrolls.
*Precedents: Carbon, Material.*

**6. Related destinations under a group label.**
Uncategorized items go at the top, with no label; a one-item group gets no label.
*Precedents: Spectrum, Primer NavList.Group.*

**7. Most used first.**
Between groups and within each group.
*Precedent: Material.*

**8. One level only.**
Sub-pages become a Tab Line inside the page.
*Precedents: Carbon (no third level; tabs on the page); the Tab's "Tabs inside tabs".*

**9. A group label isn't clickable.**
It doesn't lead anywhere.
*Precedent: Spectrum.*

**10. Groups separated by space, with no Divider.**
> **Conscious divergence:** Primer uses a divider for unlabeled groups. In AL every group with more than one item has a label, and a label plus 24px of space already separate.

### Item

**11. Always the full-width Tab Square.**
Never the Line: the line only makes sense horizontally.
*Precedent: Tab rule 4.*

**12. At most one current item.**
The destination of the area where the person is, including its sub-pages. A page outside the destinations, like the account page, marks none.
*Precedents: Carbon, Primer.*

**13. No icon and no counter.**
In this version. The Tab doesn't have them either.

### Content

**14. A label of 1 to 3 words.**
A noun that names the destination, in sentence case, with no internal jargon: "Orders", not "Manage your orders".
*Precedents: Material; Tab rules 14 and 15.*

**15. The label on one line, with no ellipsis.**
The usable width is 248px. If it doesn't fit, the text changes.
*Precedents: Material ("don't truncate"); Tab rule 16.*

**16. No repeated labels.**
The screen reader lists every link; two "Reports" are ambiguous (WCAG 2.4.4).

**17. A group label of one or two words.**
Mono, in sentence case, never all caps: the font already sets it apart from the items.

### Profile

**18. Who is signed in: name and email.**
The Avatar follows photo, initials, icon, and here it's decorative, because the name is right next to it.
*Precedent: the Avatar rules.*

**19. The button leads to the account page.**
With a name that says so, like "Open my account".
*Precedent: the Icon Button rules.*

**20. Name and email can have an ellipsis.**
The only exception to rule 15: the text comes from the user's record, not from the product. The full text stays in the document for screen readers.
*Precedent: Primer (truncate only user text).*

### Help

**21. Optional, for what's outside day-to-day work.**
Support, documentation, feedback; up to three items, fixed at the bottom.
*Precedents: Carbon, Material.*

**22. An item that opens another site says so.**
In the label or the accessible name.
*Precedent: WCAG 3.2.5.*

### Size and layout

**23. One size only.**
296px wide and the screen's height; it doesn't scroll with the page.
*Precedent: Primer (296px panel).*

**24. Below 1024px, a modal panel from the left.**
Opened by a Menu button that the product places at the top. It also covers 200% zoom (WCAG 1.4.10).
*Precedents: Carbon (menu on small screens or at ~175% zoom), Material (modal drawer on compact screens).*

**25. In modal mode, no X.**
Focus lands on the current item; Esc closes and returns focus to Menu; choosing a destination closes it; clicking outside always closes, because there are no fields. The Menu button stays visible.
*Precedents: the AL Modal and Drawer, Material.*

### Accessibility

**26. An `<aside>` with the navigation inside.**
Groups and Help in a `<nav aria-label="Main">`; the profile stays outside, because it identifies, it doesn't navigate.
*Precedents: Carbon, Queensland.*

**27. Each group is a list named by its label.**
"Sales, list, 4 items".
*Precedents: Primer, Carbon.*

**28. Items are links, the current one with `aria-current="page"`.**
Never `role="tab"`; Tab goes through all of them and the arrow keys do nothing.
*Precedents: Tab rule 22, Carbon, Primer.*

**29. "Skip to content" before the Sidebar.**
It belongs to the product. Without it, keyboard users go through every item on every page (WCAG 2.4.1).
*Precedent: Carbon.*

**30. Focus is the Tab's ring, keyboard only.**
In high contrast mode, the current item gets an outline and the border stays visible.
*Precedent: Tab rules 23 and 24.*

### Exceptions

**31. The border is a region border.**
Between 1.47 and 2.71:1, below 3:1: the Sidebar is a region of the page, not a control. Don't darken it. The same reasoning as the Divider and the Card.

**32. The page title repeats the current item's label.**
It pays for the tonal selection inherited from the Tab (the current item's background barely separates from the canvas). On the canvas, the current item's pressed state passes 3:1.

### Out of scope

**33. What's left out, on purpose.**
Icon, counter, sub-levels, a collapsed icon-only mode, drag to resize, a Sidebar on the right, a second size, its own theme. A new need reopens the component's scope.

## Out of scope, on purpose

| What | Why |
|---|---|
| Icon and counter on items | The Tab doesn't have them; the Sidebar inherits that. |
| Expanding sub-levels | One level only; sub-pages are a Tab Line on the page. |
| Collapsed icon-only mode | Without icons on the items, it isn't even possible. |
| Drag to resize | Spectrum has it; AL has one size. |
| Sidebar on the right | The right belongs to the Drawer. |
| Its own theme | A dark Sidebar in a light product, for example. |
