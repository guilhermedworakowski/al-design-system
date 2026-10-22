# Pagination · Usage guidelines

Pagination splits a long list into pages, or loads it in parts, so the person can move through it.

- **Built on:** a `<nav aria-label="Pagination">`; previous, next and load more are Buttons, rows per page is the Select
- **Types:** Numbered, Simple, Load more, Range
- **States:** Default, Hover, Pressed, Focus; current page tonal
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#pagination](https://al.guilhermedesignd.com/#pagination)

## Do and don't

| Do | Don't |
|---|---|
| **A long list, 25 items or more.** | **Pages for a short list that fits on one screen.** |
| **Under the list it controls.** | **The same pagination above and below the list.** |
| **A fixed window of 7 positions.** | **A row of numbers that grows and shrinks with the page.** |
| **Previous and Next always with a label.** | **Arrows alone, with no text.** |
| **Previous disabled on the first page.** | **Previous hidden on the first page, moving Next around.** |
| **The current page marked by aria-current.** | **The current page marked by color alone, with nothing announced.** |

## Rules

### When to use

**1. For long lists, from about 25 items.**
With fewer, show everything at once.
*Precedents: Polaris and Carbon.*

**2. Never for the steps of a flow.**
Steps the person moves through use the Progress Steps type or Next and Back buttons.
*Precedent: Carbon.*

**3. Pick the type by what the person needs.**
Numbered to jump to a given page. Simple when the total is unknown or costly to count. Load more to keep the reading position, as in a feed. Range when the total of items is the point, as in a table.
*Precedents: Carbon and Polaris.*

**4. Load more before infinite scroll.**
Infinite scroll hides the footer and is hard for keyboard and screen reader users.
*Precedent: Shopify.*

### Placement

**5. Under the list it controls, aligned with it.**
*Precedents: Polaris and Carbon.*

**6. One per list.**
Don't repeat it above the list. If the list is too long, filter it better.
*Precedent: Polaris.*

**7. In a table, Range on the left and the navigation on the right.**
*Precedent: Carbon.*

**8. Only on bg-canvas or bg-surface, never on bg-surface-raised.**
The hover fades on the raised surface, as found in the Modal 0.18.1 fix. So no Pagination inside a Modal or a Drawer.
> **Conscious divergence:** an AL decision, with no precedent in the reference systems.

### Numbers

**9. A fixed window of 7 positions when there are more than 7 pages.**
Near the start: 1 2 3 4 5 … 16. In the middle: 1 … 7 8 9 … 16. Near the end: 1 … 12 13 14 15 16. The first and last pages are always there.
*Precedents: Primer and Carbon.*

**10. The ellipsis is not clickable.**
It only says there are pages in between; the neighbors take the person there.
*Precedent: Primer.*

**11. The width stays the same.**
The number of positions never changes with the current page, so Previous and Next never jump.
*Precedent: Primer.*

### Content

**12. Previous and Next always have a label, never only the arrow.**
The arrow is decorative.
*Precedent: Primer.*

**13. Load more says how many it brings: "Load 20 more".**
If fewer than 20 are left, show the real number.
*Precedent: Polaris.*

**14. Range follows "Showing 41–60 of 312".**
With an en dash, and the same format on every screen.
*Precedent: Carbon.*

**15. Rows per page offers few options.**
For example 10, 20, 50 and 100.
*Precedent: Carbon.*

### States

**16. Previous is disabled on the first page, Next on the last.**
Disabled, not hidden, so the buttons don't move. In Figma it is an instance swap to the disabled Button.
*Precedent: Polaris.*

**17. When there is nothing left, Load more leaves.**
A short text takes its place, such as "That's everything".
*Precedent: Shopify.*

**18. While it loads, Load more uses the Button's loading state.**
The list already loaded stays on screen.
*Precedent: Polaris.*

**19. The current page is tonal, not outlined.**
An outline reads as focus in AL. The bg-brand-subtle background barely shows, so the brand-colored number is what marks the current page. This pays the tonal selection exception, the same as the Tab Square.
> **Conscious divergence** from the outlined reference.

### Accessibility

**20. A `<nav>` named "Pagination", with the pages in a `<ul>`.**
*Precedents: Primer and Queensland.*

**21. The current page carries `aria-current="page"`, and every page is named "Page 3".**
*Precedents: Primer and Carbon.*

**22. Pages are links when they change the URL, buttons when they swap content in place.**
As buttons, focus moves to the start of the new content.
*Precedent: Primer.*

**23. After Load more, focus goes to the first new item.**
It does not stay on the button.
*Precedent: Primer.*

**24. The target is at least 24×24.**
AL items are 36×36.
*Precedents: Primer and WCAG 2.5.8.*

## Out of scope, on purpose

| What | Status | If the need comes up |
|---|---|---|
| First and last buttons | Does not exist | The first and last pages are already numbers. |
| A field to type the page | Does not exist | A separate Input, outside the Pagination. |
| Sizes | One size, sm | A new size goes back to stage 1. |
| Use on bg-surface-raised | Not allowed | The -raised hovers would be new tokens, back to stage 3. |
