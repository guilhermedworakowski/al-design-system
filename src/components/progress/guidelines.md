# Progress · Usage guidelines

A progress bar shows how much of a system task is done, while the person waits for it.

- **Built on:** the native `<progress value max>`
- **Types:** Label (label + percentage), Steps ("N of total"), Thin (a 4px bar alone); determinate only
- **States:** none - the bar is a passive status, it takes no focus
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#progress](https://al.guilhermedesignd.com/#progress)

## Do and don't

| Do | Don't |
|---|---|
| **A long system task:** an upload, an install, an import. | **A bar for storage used:** that is a meter, not progress. |
| **Steps for countable parts:** "File 3 of 5". | **Steps as a form wizard:** the person moves forward, not the system. |
| **The bar fills its container.** | **A fixed width that breaks the layout on a phone.** |
| **The label names the task:** "Uploading report.pdf". | **"Loading…" with no subject.** |
| **When it fails, a message says so.** | **A red bar as the only sign of an error.** |
| **The label or the percentage always next to the bar.** | **A Thin bar alone, with nothing that says what it measures.** |
| **Duration unknown: the Button's loading state.** | **A bar that loops back and forth.** |

### The bar is never the only cue

This is the rule that makes the component's contrast exception acceptable. The fill sits below 3:1 against the track (2.53:1 light, 2.2:1 dark), and that is only acceptable because a text always carries the value: the percentage, the count, or the name and value read by assistive tech.

## Rules

### When to use

**1. Only for system work that takes time and can be measured.**
An upload, an install, an import. The person only waits; the progress does not depend on them.
*Precedents: Carbon and Spectrum.*

**2. Not for operations under about 5 seconds.**
Use the Button's loading state. A bar that blinks and disappears is noise.
*Precedent: Carbon.*

**3. Not to measure a quantity.**
Storage used, a goal reached: that is a meter, which AL does not have.
*Precedent: Spectrum.*

**4. Not as a form stepper.**
A multi-step flow the person moves through needs a step indicator, which is out of scope.
*Precedent: Carbon.*

### Types

**5. Label is the default.**
Use it when the task holds the focus of the screen. The label says what is happening, the percentage says how much is left.

**6. Steps is for work split into countable system parts.**
"File 3 of 5": when the part is the unit the person understands, it says more than a percentage.
*Precedent: Primer.*

**7. Thin is for background tasks.**
Inside a card, a row or a panel, where progress is secondary. It always sits next to a text that names the task (rules 20 and 22).

**8. One bar per task.**
Several tasks, several bars, one per row. A bar never adds up different tasks.

### Size and layout

**9. The bar fills its container.**
It has no width of its own. Avoid going past 6 columns or under 48px.
*Precedent: Carbon.*

**10. Only on canvas, surface or surface-raised.**
The track was calibrated for those three. Never on brand color or on a solid feedback background.

### Content

**11. The label names the action or the object.**
"Installing", "Uploading report.pdf". Never a generic "Loading…".

**12. The percentage is a whole number.**
No decimals; secondary text on the right.

**13. Steps follows "N of total".**
With the unit when it helps: "File 3 of 5".

**14. Short text, one line.**
Details go in a support line outside the component.

### States and behavior

**15. The value only grows.**
It never goes back and does not sit at 99% for long. If the estimate gets worse, change the label, not the bar.
*Precedent: Material.*

**16. When the task ends, the bar leaves and the result takes its place.**
A Toast, an Alert or the content itself. The bar does not stay at 100%.

**17. An error is not a bar color.**
AL has no error type. The message goes in an Alert or a line of text, and the bar stops where it was.
*Precedent: Carbon.*

**18. Cancel is a button outside the component.**
Next to it, when the task can be canceled. The bar is not clickable.

### Accessibility

**19. A native `<progress>`, or `role="progressbar"`.**
With `aria-valuenow`, `aria-valuemin` and `aria-valuemax`, so the screen reader can read the value. The native element gives all three.
*Precedents: Primer and Mosaic.*

**20. Every bar has an accessible name.**
Label and Steps: the visible label, through `aria-labelledby`. Thin: `aria-label` or the text next to it.
*Precedents: Primer and Material.*

**21. The bar takes no focus.**
It is a passive status. When the task ends, a Toast or an Alert announces it; the bar gets no `aria-live` of its own.
*Precedents: Primer and Carbon.*

**22. The bar is never the only cue.**
The fill sits at 2.53:1 on the track in light and 2.2:1 in dark, below 3:1. What informs is the percentage in Label, the count in Steps, and the name with `aria-valuenow` in Thin.
> **Conscious divergence** from Primer, which asks for 3:1 between segments: AL keeps the brand color on the fill and pays for it with text that is always there.

**23. No continuous animation.**
Only the width changes, with the feedback motion duration, and it respects `prefers-reduced-motion`.

### Out of scope

**24. No indeterminate, no circular, no status color, no buffer.**
When the duration is unknown, use the Button's loading state. If the need appears, it goes back to stage 1 as a new type.

## Out of scope, on purpose

| What | Status | If the need comes up |
|---|---|---|
| Indeterminate | Does not exist | The Button's loading state or the spinner. |
| Circular | Does not exist | A new type, back to stage 1. |
| Success or error color | Does not exist | The message goes in an Alert or a Toast. |
| Meter (a quantity, not a task) | Does not exist | A component of its own, not a Progress type. |
