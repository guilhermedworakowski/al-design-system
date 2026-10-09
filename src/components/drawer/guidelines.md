# Drawer · Usage guidelines

A drawer is a side panel to **view or edit something without losing the page** behind it.

- **Built on:** the native `<dialog>`, opened with `showModal()`
- **Sizes:** `sm`, `md`, `lg`
- **Side:** right only
- **Closing:** X (optional), Esc always; the backdrop only when there are no fields
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#drawer](https://al.guilhermedesignd.com/#drawer)

## Do and don't

| Do | Don't |
|---|---|
| **Detail next to the list:** the person sees the data without losing the list. Primer, Evergreen. | **A confirmation in a side panel:** a decision that stops the flow is a Modal. SAP, Singapore. |
| **"Delete" opens a Modal:** the button sits in the body and opens the confirmation in a Modal, a single layer. | **Danger as the panel's main button:** one click in the footer destroys without the person stopping to confirm. |

## Rules

### When to use

**1. View or edit without losing sight of the page.**
The detail of a row, filters, settings, a quick edit next to a list. The page behind stays in view.
*Precedents: Primer, Material 3, Evergreen, Singapore Design System.*

**2. A decision that blocks, or a confirmation, is a Modal.**
The Drawer doesn't interrupt: it goes along with the page.
*Precedents: SAP, Singapore Design System.*

**3. A long flow, with several steps or its own URL, is a page.**
A short in-context edit form fits in the Drawer; past `lg` with too much scrolling, it becomes a page.
*Precedents: Primer, Evergreen, Smashing Magazine.*
> **Conscious divergence:** Primer forbids forms in side panels; Ant Design and Singapore allow them, and AL sides with them.

**4. Never a Drawer on top of another.**
People get lost in the layers.
*Precedents: Primer (the dimmed backdrop prevents two panels at once), Moon.*

**5. It only enters from the right.**
The left belongs to navigation, the Sidebar.
*Precedents: Primer, Carbon (UI shell right panel).*

### Structure and content

**6. The title is required and visible.**
It names the panel for everyone.
*Precedents: Primer, APG.*

**7. Short, in sentence case, with the name of the object or the task.**
"Filters", "Edit customer". The same rule as the Modal's title.

**8. The body is a free slot.**
The Drawer only brings the header and the actions; the content belongs to whoever uses it.

**9. No divider between the parts.**
The 24px space is what separates header, body and actions. An AL decision; if QA shows the title "disappearing" under scrolling text, it reopens.

### Size

**10. Choose by content.**
`sm` for filters and short actions, `md` for detail and short forms, `lg` for dense content. AL's criterion, mirrored from the Modal; Material only says the width is fixed.

**11. Scrolls too much? Go up a size.**
Past `lg`, it becomes a page.

**12. On mobile, the screen minus 16px of breathing room on the left.**
The gap shows the page behind, lets people tap it to close, and keeps the corner radius.
*Precedent: Material 3 (the modal version is the mobile one).*

**13. The height is always the screen's.**
Attached to the top and the bottom.
*Precedents: Primer, Material 3.*

### Closing

**14. There's always a visible way out.**
The X, or the footer with a secondary button that closes. The X can be turned off, but then the footer stays.
*Precedents: Primer (the X is required), Jellyvision.*

**15. Esc always closes it.**
With or without fields. The `<dialog>` already does it.
*Precedents: APG, Evergreen.*

**16. A click on the backdrop closes it only when there are no fields.**
> **Conscious divergence, inherited from the Modal:** Primer closes on the backdrop but blocks with unsaved changes; Material 3 and Evergreen always close. AL is stricter: any field is enough to prevent it.

**17. Closing returns focus to whatever opened it.**
*Precedents: APG, Primer, Evergreen, Workday.*

**18. A closed Drawer doesn't stay on the page.**
Not even hidden with CSS: the `<dialog>` takes care of it.

**19. X and Esc close and discard.**
A form with unsaved changes warns beforehand, in the form itself, by listening to the `cancel` event. The Drawer doesn't decide for you what counts as data loss.
*Precedent: Primer.*

### Actions

**20. Two at most, with the main one on the right.**
The same rule as the Modal.
*Precedent: Material 3 (confirm and cancel).*

**21. The buttons stretch and share the width.**
In all three sizes. The panel is narrow, and the footer lines up with the content and gives a large touch target. In the Modal, buttons are the size of their text, on the right.
*A design decision, with no market precedent.*

**22. A destructive action isn't the Drawer's main action.**
"Delete customer" opens a confirmation Modal, a single layer.
*Precedents: SAP, Singapore Design System.*

**23. A label with a verb and a noun, fixed footer.**
The same label rule as the Modal; only the body scrolls.

### Focus and screen reader

**24. `<dialog>` opened with `showModal()`.**
It traps focus, makes the rest of the page inert and closes with Esc.
*Precedents: APG, MDN.*

**25. The Drawer has a name.**
`aria-labelledby` points to the title.
*Precedents: APG, Primer.*

**26. The X has a name.**
"Close", on the button itself. It's the Icon Button rule: without a name, the button is silent.

**27. Initial focus depends on the content.**
The first field; otherwise the footer's main button; otherwise the X. APG warns against focusing the X when there's something more relevant.

**28. The dimmed backdrop is decoration.**
It doesn't receive focus and isn't announced.

**29. Only the body scrolls.**
The header and actions stay put; the page behind doesn't scroll.
*Precedent: Material 3 (vertical scrolling only).*

**30. It enters and leaves from the right, in 300ms.**
It enters from right to left and leaves from left to right; with reduced motion, without sliding.
*An AL decision, with no precedent researched beyond "a panel that slides from the edge".*

## Out of scope, on purpose

| What | Why |
|---|---|
| Other sides | Left, top and bottom. The left belongs to the Sidebar, which becomes a panel from the left on mobile. |
| Persistent Drawer, without a dimmed backdrop | Material's "standard" is a page layout, not an overlay component. |
| Resizable Drawer | The three sizes are fixed. |
| Drawer on top of a Drawer | Never. If the need comes up, the flow is a page. |
| Description under the title | The title is enough; the rest belongs to the body. |
| Dividers between the parts | Space separates; no lines. |
| Multi-step flow | It's a page. |
