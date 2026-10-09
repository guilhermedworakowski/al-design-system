# Modal · Usage guidelines

A modal interrupts the page for a **short task that needs an answer**.

- **Built on:** the native `<dialog>`, opened with `showModal()`
- **Sizes:** `sm`, `md`, `lg`
- **Closing:** Esc always; the backdrop only when there are no fields; no X button
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#modal](https://al.guilhermedesignd.com/#modal)

## Do and don't

| Do | Don't |
|---|---|
| **A title and a button with the same action:** the person knows what will happen before clicking. Polaris, Carbon. | **A vague title and "OK":** "OK" to what? Someone who only reads the button doesn't know they're deleting something. |
| **The way out is a footer button:** there's always a button to go back. | **An X in the corner and three actions:** AL has no X, and three actions crowd the footer on mobile. |

## Rules

### When to use

**1. A short task that asks for an answer.**
A confirmation, a quick edit, a choice. The Modal blocks the page: the person only gets back to the flow after resolving or dismissing it.
*Precedents: Carbon, Polaris.*

**2. Never for what needs to stay in view.**
It's temporary. Information or actions the person checks all the time live on the page.
*Precedent: Polaris.*

**3. A long form isn't a Modal.**
If it goes past the `lg` size and still scrolls too much, it's a page (or a Drawer, when the page behind needs to stay in view).
*Precedents: Carbon, Polaris.*

**4. Never a Modal inside another.**
One at a time.
*An AL rule, with Bootstrap as the only precedent found on nesting.*

### Structure and content

**5. The title is required and visible.**
It names the Modal for screen readers and tells the person where they are.
*Precedents: Primer, Spectrum.*

**6. Verb and noun, or a short question.**
"Edit email", "Delete customer?". No long sentence and no vague title like "Attention".
*Precedent: Polaris.*

**7. Sentence case, short texts.**
Title, text and labels in sentence case.
*Precedent: Carbon.*

**8. State the consequence, don't ask.**
"This can't be undone", not "Are you sure?".
*Precedents: Polaris, Spectrum.*

**9. The body is a free slot.**
The Modal only brings the title and the actions; the content belongs to whoever uses it.

**10. No divider between the parts.**
The 24px space is what separates title, body and actions. An AL decision.

### Size

**11. Choose by content.**
`sm` for a short confirmation, `md` for a short form, `lg` for denser content. Never "whatever looks better".
*Precedent: Carbon.*

**12. Scrolls too much? Go up a size.**
Before accepting the scroll, try the size above.
*Precedent: Carbon.*

**13. On mobile, the screen minus 16px on each side.**
The 320px `sm` on a 375px screen doesn't touch the edge. An AL decision.

### Closing

**14. A click on the backdrop closes it only when there are no fields.**
With a form, an accidental click would lose what was typed.
> **Conscious divergence:** Polaris and Carbon say never, Primer says always. AL sits in the middle.

**15. Esc always closes it.**
With or without fields. The `<dialog>` already does it.
*Precedents: Carbon, Primer, Polaris.*

**16. There's no X button.**
Every Modal has at least one footer button, and the secondary one ("Back", "Cancel", "Close") is the visible way out. An AL rule.

**17. Closing returns focus.**
To the element that opened the Modal.
*Precedents: Carbon, Primer.*

**18. A closed Modal doesn't stay on the page.**
Not even hidden with CSS: the `<dialog>` takes care of it.

### Actions

**19. Two at most, with the main one on the right.**
More than that muddles the hierarchy and crowds the footer on mobile.
*Precedents: Polaris, Agriculture AU.*

**20. Primary for what confirms, Danger for what destroys.**
Never a Primary to delete.
*Precedents: Carbon (danger variant), Spectrum (red button).*

**21. A label with a verb and a noun.**
The same as the title: "Delete customer", not "OK".
*Precedents: Polaris, Carbon.*

**22. No actions only when there's another obvious way out.**
The footer can be turned off, but by the button rule it's the exception. When in doubt, keep the secondary.

**23. In a destructive Modal, Enter doesn't destroy.**
Whoever confirms the deletion makes a deliberate click or Tab.
*Weak precedent: only the Adobe XD documentation.*

### Focus and screen reader

**24. `<dialog>` opened with `showModal()`.**
It traps focus, makes the rest of the page inert and closes with Esc.
*Precedent: MDN.*

**25. The Modal has a name.**
`aria-labelledby` points to the title: the `<dialog>` doesn't name itself.
*Precedents: APG, MDN.*

**26. Initial focus depends on the content.**
With fields, the first field; without fields, the main button.
*Precedent: Carbon.*

**27. The dimmed backdrop is decoration.**
It doesn't receive focus and isn't announced.

**28. Only the body scrolls.**
The title and actions stay put; the page behind doesn't scroll.
*Precedent: Bootstrap (only the body scrolls).*

**29. Destructive Modal: focus starts on "Cancel".**
When the main action is Danger, initial focus goes to the secondary one, so Enter isn't one keystroke away from deleting.
*AL's own rule, with no confirmed precedent.*

## Out of scope, on purpose

| What | Why |
|---|---|
| X close button | AL requires at least one footer button (rule 16). |
| Dividers between the parts | Space separates; no lines. |
| Multi-step Modal | Carbon's "previous and next". If the need comes up, it's a new component. |
| Entering from the side | That's the Drawer, which has its own page. |
| Outline in dark mode | The card gets lighter against the dimmed backdrop, with no outline. |
