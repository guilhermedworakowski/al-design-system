# Menu · Usage guidelines

The menu holds the actions that don't fit on screen, behind a ⋮ button, and runs the one the person picks.

- **Built on:** the Icon Button as the trigger, a `<ul role="menu">` of `<button role="menuitem">`, and the Divider between groups
- **Types:** Default, Danger
- **States:** Default, Hover, Pressed, Focus, Disabled
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#menu](https://al.guilhermedesignd.com/#menu)

## Do and don't

| Do | Don't |
|---|---|
| **Actions on an object: edit, duplicate, delete.** | **Links to other pages inside a menu of actions.** |
| **A short verb: "Edit", "Duplicate".** | **A sentence that does not fit in 200px.** |
| **Shortcuts the product really implements.** | **A value or a toggle on the right side of the item.** |
| **Danger last, after the line.** | **Danger in the middle of the list.** |
| **Disabled when the action exists but is unavailable now.** | **A disabled item that will never be available.** |

## Rules

### When to use

**1. For actions on an object or on the screen.**
Edit, duplicate, delete. An item runs an action; it does not take the person to another page. To navigate, use links, as in the Breadcrumb `…` or the Sidebar.
*Precedents: Primer ActionMenu and Carbon Overflow menu.*

**2. Never to pick a form value.**
That is the Select: native, and its value goes with the form.
*Precedents: Primer and Carbon.*

**3. Only with two or more actions that don't fit on screen.**
A single action, or the main action of the screen, is a visible Button. Hiding it costs a click and takes it out of sight.
*Precedents: Carbon Overflow menu and Material.*

### Content

**4. The label is a short verb.**
"Edit", "Duplicate", "Delete". Never a sentence.
*Precedents: Primer and Carbon.*

**5. The width is a fixed 200px, and the label fits on one line.**
If it does not fit, shorten the text. In code, a label that overflows ends in "…".
*Precedent: Carbon, which also limits the width.*

**6. Order by frequency of use, with related actions together.**
*Precedents: Carbon and Primer.*

**7. Groups are split by the line only.**
The Divider, with no group title.
*Precedents: Carbon and PatternFly.*

### Icon and shortcut

**8. The icon is optional, but it is all or none in a menu.**
So the labels line up.
*Precedent: Primer ActionList.*

**9. The icon is decorative.**
It is `aria-hidden`; the label carries the meaning, as in the Button.

**10. The shortcut sits on the right, in the person's system format.**
"⌘E" on Mac, "Ctrl+E" on Windows and Linux.
*Precedent: Primer.*

**11. The menu only shows the shortcut; the product implements the key.**
It is announced by `aria-keyshortcuts`. Never show a shortcut that does not work.
*Precedents: WAI-ARIA APG and Primer.*

**12. The right side of the item is for the shortcut only.**
No value, button or toggle there.
*Precedent: Primer.*

### Danger

**13. Danger is for destructive actions only.**
Delete, remove, revoke. Never red just to draw attention.
*Precedent: Carbon.*

**14. Danger always goes last, after the line.**
*Precedent: Carbon Overflow menu.*
> **Conscious divergence:** Primer has no position rule for Danger; this one is AL's, following Carbon.

**15. If the action cannot be undone, Danger opens a confirmation Modal.**
The menu confirms nothing.
*Precedent: Carbon.*

**16. Danger hovers on a light red and presses on a solid red with white text.**
The raised greys erased the red in dark mode (3.31:1 on hover, 2.2:1 on pressed).
*Precedent: Carbon, which uses the error color on the danger hover.*

### States

**17. Disable an item when the action exists but is unavailable right now.**
If it will never be available to that person, remove the item.
*Precedent: Primer.*

**18. Disabled sits below AA contrast on purpose (2.1:1).**
WCAG 1.4.3 exempts disabled components. Don't darken it to "fix" it.

**19. The panel is always bg-surface-raised, with the -raised hover and pressed.**
The plain hover fades on the raised surface, as found in the Modal 0.18.1 fix.

**20. The panel border is below 3:1 on purpose.**
The 3:1 of WCAG 1.4.11 applies to the outline of controls; the panel is a content box, set apart by the shadow. The same exception as the Breadcrumb menu.

### Keyboard and screen reader

**21. The trigger is an Icon Button with `aria-haspopup="menu"`, `aria-expanded` and a name.**
For example "More actions".
*Precedent: WAI-ARIA APG Menu Button.*

**22. Enter, Space or Down open the menu on the first item; Up opens it on the last.**
*Precedent: WAI-ARIA APG.*

**23. Inside, the arrows move with wrap and Home and End go to the ends.**
Esc closes and returns focus to the trigger. Tab closes the menu.
*Precedents: WAI-ARIA APG and Primer.*

**24. Choosing an action closes the menu and returns focus to the trigger.**
Unless the action opens a Modal: then focus goes to the Modal.
*Precedent: WAI-ARIA APG.*

**25. Focus is a 2px orange outline inside the item, and it drops the hover background.**
An outer ring would hit the neighbors, and on the hover background the ring would fall to 2.88:1. Disabled items take focus too and are announced as unavailable.
*Precedent: WAI-ARIA APG, for the focusable disabled item.*
> **Conscious divergence** from Primer, which skips disabled items.

### Out of this version

**26. No submenu, no checkable item, no group title and no variable width.**
To pick a value, use the Select or the Radio. For more levels, rethink the screen.

## Out of scope, on purpose

| What | Status | If the need comes up |
|---|---|---|
| Submenu | Does not exist | Rethink the screen; more levels hide actions. |
| Checkable item (check or radio) | Does not exist | The Checkbox, the Radio or the Select. |
| Group title | Does not exist | The line splits the groups. |
| Variable width | Fixed at 200px | Shorten the label. |
| Links as items | Not allowed | A navigation list, like the Breadcrumb `…`. |
