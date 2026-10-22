# Empty state · Usage guidelines

The Empty state takes the place of content that is not there: it says what is empty, why, and what to do next.

- **Built on:** a `<section>` with a heading; after a search or filter it renders inside `role="status"`
- **Parts:** optional icon, title, optional description, at most one Primary button
- **Size:** one, up to 600px wide
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#empty-state](https://al.guilhermedesignd.com/#empty-state)

## Do and don't

| Do | Don't |
|---|---|
| **One Empty state in place of the list that would be there.** | **An Empty state for a failure to load.** |
| **On the canvas or on a section band.** | **Inside a Card, Modal or Drawer.** |
| **A title that names what is empty, and an icon of that object.** | **"No data" with a warning icon.** |
| **One Primary action that fixes the empty area.** | **Two buttons, or a link next to the button.** |
| **The title as a heading at the page's level.** | **The title as bold text that is not a heading.** |
| **Error goes to the Alert.** | **An error variant of the Empty state.** |

## Rules

### When to use

**1. When an area that would show data is empty.**
First use, a search or filter with no results, or after everything was deleted.
*Precedent: Carbon.*

**2. Not for a system error or a failed load.**
That is the Alert: the Empty state says "nothing here", not "something broke".
*Precedent: Carbon, which separates error from empty.*

**3. Not while loading.**
While data arrives, show the Progress or the area's skeleton. The empty state appears only when the area is known to be empty.
*Precedent: Carbon.*

**4. One per empty area, never several stacked.**
If the whole page is empty, use one, in place of the main content.
*Precedent: Polaris.*

### Where it lives

**5. Only on bg-canvas or bg-surface.**
The box is bg-surface-raised: inside a Card, Modal or Drawer it is white on white and disappears.

**6. It takes the place of the missing content.**
Same position the list or table would have; it does not float in the middle of the screen.
*Precedents: Primer and Carbon.*

**7. Up to 600px wide, centered in the space it has.**
On a narrow screen it shrinks with the space.
*Precedent: Primer (narrow).*

### Content

**8. The title names what is empty, not that it is empty.**
"No projects yet", not "No data".
*Precedent: Polaris.*

**9. The description explains why, or what to do, in one or two sentences.**
It is optional when the title is enough.
*Precedents: Lightning and Carbon.*

**10. A search with no results repeats the term and suggests changing the search or the filters.**
*Precedents: Carbon and NN/g.*

**11. A neutral tone, no blame and no jokes.**
"No results for 'X'", not "Oops! We found nothing".
*Precedent: Polaris.*

**12. No marketing copy.**
The empty state points to the next step; it does not sell a feature.
*Precedent: Polaris.*

**13. The icon is optional and decorative.**
`aria-hidden`: the title already says everything.
*Precedent: Polaris (illustration with an empty alt).*

**14. The icon is the missing object (a folder, a search, a bell), never a warning or an error.**
A warning icon makes the empty area read as a failure.
*Precedent: Carbon.*

### Action

**15. At most one action, always Primary.**
The action that fixes the empty area, like "Create project".
*Precedent: Polaris.*

**16. No action when there is nothing to do.**
For example, a list only the system fills.
*Precedent: Lightning.*

**17. The action's label is verb + object, under the Button's rules.**
*Precedent: Polaris.*

**18. No Link inside the Empty state, not even in the description.**
Figma has none, and the Link Default would fall to 3.2:1 on surface-raised in dark.
> **Conscious divergence** from Polaris, which allows a secondary link.

### Accessibility

**19. The title is always a heading, at the level the page outline asks for.**
h2, h3: the class does not pin a tag.
*Precedents: Siteimprove and Unkey.*

**20. Reading order is icon, title, description, action; focus does not jump to the button.**
After a search or filter the empty state renders inside `role="status"` and is announced once; on first load it is static.
*Precedents: Primer and ICDS.*

**21. The box border is decorative.**
It measures 1.47 to 2.42:1 against the page. WCAG 1.4.11 asks 3:1 of control outlines; the box is content, recognized by what it says. The same exemption as the Card.

### Not in v1

**22. No illustration, no compact size and no error variant.**
An empty area inside a table or a Menu is plain text in text-secondary; an error is the Alert.

**23. Never two actions.**
If a second one seems necessary, it lives outside the Empty state.
*Precedent: Polaris (one primary call to action).*

## Out of scope, on purpose

| What | Status | If the need comes |
|---|---|---|
| Illustration | Not in v1 | A new component, with its own library. |
| Compact size | Not in v1 | Plain text in text-secondary inside the table or Menu. |
| Error variant | Does not exist | The Alert. |
| Second action or Link | Does not exist | It lives outside the Empty state (rules 18 and 23). |
