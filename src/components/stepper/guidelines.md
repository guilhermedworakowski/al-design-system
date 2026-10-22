# Stepper · Usage guidelines

The Stepper shows where the person is in a linear task split into steps: what is done, what is now and what is left.

- **Built on:** an `<ol>` inside a `<nav aria-label="Progress">`; the current step carries `aria-current="step"`
- **Orientations:** Horizontal, Vertical
- **States:** Completed, Current, Upcoming; not clickable
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#stepper](https://al.guilhermedesignd.com/#stepper)

## Do and don't

| Do | Don't |
|---|---|
| **A linear task of 3 to 5 steps.** | **A Stepper for a two-step form.** |
| **Vertical on a narrow screen.** | **Horizontal with long titles that wrap.** |
| **Titles of one or two words.** | **Sentences as step titles.** |
| **Every step before the current one completed.** | **A completed step after the current one.** |
| **The status spelled out and aria-current on the current step.** | **The current step marked by color alone.** |
| **Back and Continue in the form, under the step.** | **The Stepper as the only way to move between steps.** |

## Rules

### When to use

**1. For a linear task of 3 to 5 steps.**
Under 3, a heading like "Step 1 of 2" is enough. Over 5, the task probably needs to be split.
*Precedents: Carbon (3 or more steps) and Red Hat (3 to 5).*

**2. Not when the steps can be done in any order.**
The Stepper says "you are here in a sequence". Free sections use the Tab.
*Precedents: Carbon and Singapore Government Design System.*

**3. Not for the progress of an operation, like a send or an upload.**
That is the Progress.
*Precedent: Carbon, which splits Progress indicator from Progress bar.*

**4. Never the only navigation.**
Back and Continue live in the form, under the step's content.
*Precedent: Red Hat.*

### Orientation

**5. Horizontal for wide screens and short titles.**
The title sits under the circle and each step takes an equal share of the width. A long title wraps and unbalances the strip.
*Precedent: Material ("avoid long step names in horizontal steppers").*

**6. Vertical for narrow screens, or when the steps need a description.**
*Precedent: Material ("vertical steppers are designed for narrow screen sizes").*

**7. One orientation per flow at each screen width.**
It may switch from horizontal to vertical at a breakpoint, but the switch applies to the whole flow.
> **Conscious divergence:** an AL decision, the same logic as the Sidebar, which becomes a panel under 1024.

**8. On bg-canvas, bg-surface and bg-surface-raised.**
The gate measured all three and every combination passes, so the Stepper may live inside a Modal or a Drawer.

### Content

**9. Titles of one or two words, preferably a noun.**
Account, Address, Review.
*Precedent: Carbon v10 (one to two words).*

**10. The description is optional and one line long.**
It complements the title and does not repeat the step's instruction. In the horizontal Stepper, use it on every step or on none.
> **Conscious divergence:** an AL decision; a lone description unbalances the strip.

**11. The number is the step's position, never a label.**
It starts at 1 and does not skip.

**12. The last step is a review or a confirmation when the flow saves something.**
*Precedent: Material (a final review step).*

### States

**13. Three states, and only one current step.**
Completed is tonal with a check, current is solid, upcoming is outlined.

**14. Every step before the current one is completed; every step after it is upcoming.**
In a linear flow there is no completed step after the current one.

**15. One continuous line shows the path walked.**
Brand up to the current step, gray after it. The half before the first step and the half after the last one stay unpainted.

**16. Going back to a completed step does not erase its data.**
The Stepper only reflects where the person is; the form decides.
*Precedent: Material (linear steppers).*

### Accessibility

**17. An `<ol>` inside `<nav aria-label="Progress">`.**
*Precedents: Kendo (navigation landmark) and the ordered-list pattern.*

**18. The current step carries `aria-current="step"`.**
*Precedents: Trimble and Singapore Government Design System.*

**19. Each step spells its status in hidden text: "completed", "current", "upcoming".**
The check and the color say nothing to a screen reader.
*Precedent: Trimble.*

**20. Color is never the only cue.**
Completed has a check, current is filled, upcoming is only outlined: the shape tells the three apart.
*Precedent: Phoenix Group.*

**21. The gray line is decorative.**
It measures 1.98:1 in dark. Progress is carried by the circles and by `aria-current`.
> **Conscious divergence:** the same as the Divider.

**22. The white number on the brand measures 3.34:1.**
The brand exception of the Foundation, with a floor of 3:1. The number is also in the step's text, so it is never the only source.

**23. When the step changes, focus goes to the heading of the new step's content, not to the Stepper.**
> **Conscious divergence:** an AL decision, the same logic as the Pagination's Load more.

### Not in v1

**24. Steps are not clickable and there is no error state.**
Carbon and Phoenix Group have both. To jump between steps use the buttons; an error shows in the field and in the form's Alert. If the need comes, it enters as a minor version, with hover, focus and an error token.
> **Conscious divergence** from Carbon and Phoenix Group.

## Out of scope, on purpose

| What | Status | If the need comes |
|---|---|---|
| Clickable steps | Not in v1 | A minor version, with hover, focus and the target size. |
| Error state | Not in v1 | The field and the form's Alert carry the error; a token would go back to stage 3. |
| Compact Stepper for more than 5 steps | Does not exist | Split the task (rule 1). |
| Sizes | One only | A new size goes back to stage 1. |
