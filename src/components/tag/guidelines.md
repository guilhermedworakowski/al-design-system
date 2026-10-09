# Tag · Usage guidelines

A tag labels the status or the category of something.

- **Types:** Filled, Outlined
- **Status:** Neutral, Info, Success, Warning, Error
- **Sizes:** `sm`, `md`
- **Behavior:** static, or dismissible (with an X)
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#tag](https://al.guilhermedesignd.com/#tag)

## Do and don't

| Do | Don't |
|---|---|
| **Status or category:** label the status of an item, or tag it without any status meaning. | **Action:** if clicking does anything other than remove the tag itself, it's a **Button**. Precedent: Spectrum, where badges aren't interactive; if you need interaction, use a button, tag or link. |
| **The text doing the work.** Precedent: Primer, which says that if you list successes and failures, you should prefix each label instead of relying on the color scheme. | **The color doing the work:** red reading "Payment" says nothing on its own. |

### The label carries the meaning

This is the most important rule of the component, and it's the criterion that most often fails this kind of element in any system. When the difference between statuses is **purely visual**, it doesn't reach people who can't tell the colors apart, and it doesn't reach any screen reader.

## Rules

### When to use each type

**1. Filled when the tag is an item's only status indicator.**
For example, an order's status in a table row.
*Precedent: Spectrum, the only one of the five references with solid as the Badge default.*

**2. Outlined when there are three or more tags together.**
N saturated solids compete with each other.
*Precedents: Carbon, Primer and Polaris use low emphasis as the default.*

**3. Prefer Outlined for a dismissible tag.**
The border signals "this responds to interaction" before the user hovers. A preference, not a ban.
*Precedent: Carbon gives a container border to its selectable and operational variants for this reason.*

**4. Don't use a tag for an action.**
If clicking does anything other than remove the tag itself, it's a Button.
*Precedent: Spectrum, where badges aren't interactive.*

**5. Don't use a tag as a counter or notification indicator.**
That's another component, which AL doesn't have.

### Hierarchy and combination

**6. Don't mix Filled and Outlined in the same group.**
The difference in treatment becomes a hierarchy nobody meant to create: the eye reads the filled one as more important.

**7. One status tag per item.**
If an order is "Paid" and "Shipped", those are two fields, not two tags. Two tags side by side compete over which one is the real status.

**8. A tag doesn't replace a banner.**
An error that requires action needs a place with room for the explanation and the next step.
*Precedent: Polaris, which says not to use a red badge as the only way to communicate a critical status.*

### Which status

**9. Success, Warning, Error and Info only for a real semantic status.**

**10. Neutral for a category with no status meaning.**
"Draft", "Internal", "Beta".
*Precedents: Carbon gray; Polaris `info` / `read-only`.*

**11. Don't use Error for emphasis.**
*Precedent: Polaris, which says not to use "Error" if another term describes it better.*

### Size

**12. `md` is the default.**

**13. `sm` for condensed or inline spaces.**
*Precedent: Carbon.*

**14. Dismissible `sm` only in pointer interfaces.**
The `sm` X has a 16px target, against the 24px minimum in WCAG 2.5.8. In touch contexts, use `md`. It's the same family of decision as the Button's `sm` (36px against the 44px Carbon recommends), and the answer is the same: a usage rule, not geometry.
*Precedent: WCAG 2.5.8.*

### Content and label

**15. Sentence case, one word.**
Two only when the status is compound and one word isn't enough: "Partially refunded".
*Precedent: Polaris, literally this rule.*

**16. Past tense for done, present continuous for in progress.**
"Paid", "Shipped", "Canceled" versus "Processing", "Shipping".
*Precedent: Polaris.*

**17. The label carries the meaning on its own, without relying on color.**
The most important rule on the list, and the criterion that most often fails this component.
*Precedent: Primer, which says to prefix "Pass:" / "Fail:" instead of relying on the color scheme.*

**18. Use the same term the rest of the product uses.**
*Precedent: Polaris.*

**19. Fix a long label at the source, not by truncating it.**
The AL Tooltip only works on focusable elements, and the tag isn't one, so truncated text would have no way back for keyboard or touch users. The rule is the step before: shorten it before it reaches the tag.
> **Conscious divergence:** Carbon truncates and reveals the full text in a tooltip.

### The dismissible tag

**20. Only when removing has a real, reversible effect.**
An applied filter is the canonical case.
*Precedent: Carbon.*

**21. After removing, focus moves to the previous tag in the group.**
Without this, focus falls on the `body` and keyboard users get lost in the middle of the list. This is JS; CSS can't reach it.
*Precedent: Primer, in the Token accessibility guidance.*

**22. The X has no hover background, only the cursor changes.**
The consequence to accept is that touch screens have no hover at all, so the small target from rule 14 gets no reinforcement.
> **Conscious divergence:** Carbon changes the close icon's background on hover.

**23. The whole tag isn't clickable, only the X.**
*Precedent: Carbon.*

### Accessibility

**24. A read-only tag stays out of the tab order and never receives focus.**
*Precedent: Carbon, literally.*

**25. The X needs an accessible name that includes the label.**
"Remove Pending", not "Remove". Six filters with six "Remove" buttons can't be told apart by a screen reader. It inherits the Icon Button's contract.

**26. Only the X gets a focus ring, the default one.**
Never the whole tag.

## Out of scope, on purpose

| What | Why |
|---|---|
| Brand status | Brand isn't a status, and white on `bg-brand` measures 3.34:1, below the text minimum. If it comes back, it's v2, with `bg-brand-strong`. |
| Selectable · operational | A tag that filters when clicked is another component, not a variant of this one. |
| Disabled | A tag is content. Content doesn't get disabled. |
| `lg` size | Carbon has three. AL has two, the same decision as the Button. |
| Leading icon | Spectrum and Polaris have one. Here the only slot is the X, on the right. |
