# Checkbox · Usage guidelines

A checkbox picks **any number of options** from a list, or confirms a single statement.

- **Built on:** the native `<input type="checkbox">`
- **Size:** one size (24px box)
- **States:** unchecked, checked, indeterminate, hover, focus, error, disabled
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#checkbox](https://al.guilhermedesignd.com/#checkbox)

## Do and don't

| Do | Don't |
|---|---|
| Short, in sentence case, no final period, **affirmative**. The text is clickable too, and hover lights up the whole row. Primer, Carbon. | A negation makes people think twice about what to check, and here checking means receiving, the opposite of what the sentence seems to say. Primer. |
| The form describes the error in text (for example, a summary above) and the checkbox points to it with `aria-describedby`. | Only a red border and label. That's **color only**, and WCAG requires the error to be described in text (3.3.1) and not communicated by color alone (1.4.1). |

### The component has no error message

Carbon and Polaris put the message inside the component. AL leaves the text to the form, and that's why rule 19 is mandatory, not a suggestion: it covers the gap.

## Rules

### When to use

**1. Several options from a list, or a single option that only takes effect after confirming** (submit, save).
*Precedents: Carbon, Primer, NN/g.*

**2. Never when only one option can be chosen.**
That's a radio: with a checkbox, people have no way to know the options exclude each other.
*Precedent: Carbon.*

**3. Never for an immediate action** (dark mode, notifications).
Whoever clicks a box expects to confirm later. An immediate action needs the Switch.
*Precedents: Carbon, Primer.*

**4. A single checkbox works for consent**, with the text in the first person: "I have read and accept the terms".
*Precedent: Primer.*

### Group

**5. Options stacked vertically, one per row.**
Horizontally, it's hard to tell which box belongs to which label.
*Precedents: NN/g, Carbon.*

**6. The group title (`fieldset` + `legend`) is another component.**
Until it exists, use the native elements; without them, the screen reader announces the option without the question.

### Indeterminate

**7. Only on a parent checkbox that controls children.**
All children checked → parent checked; none → unchecked; some → indeterminate.
*Precedents: Carbon, Material.*

**8. Clicking an indeterminate parent checks all the children.**
Nobody chooses indeterminate; it's a consequence. It's set with JavaScript (`input.indeterminate = true`): there's no HTML attribute.
*Precedent: Material.*

### Label

**9. A visible label on the right, and clicking it checks the box.**
A wrapping `<label>`, or `for`. It enlarges the clickable area (WCAG 2.5.8).
*Precedent: Carbon.*

**10. Short, sentence case, no final period, affirmative.**
A negation makes people think twice.
*Precedent: Primer.*

**11. A long label wraps aligned to the top of the box**, not centered on the block.
In AL this comes for free: the box and the line height both measure 24px.
*Precedent: Carbon.*

### States

**12. Checked and indeterminate share the orange box.**
The glyph (check versus dash) tells them apart, never the color.

**13. Hover only on the unchecked box.**
That's this version's behavior; it changes if the combined variant is created.

**14. Focus ring in every state.**
It doesn't depend on the fill.

**15. Disabled only when it depends on another choice on the same screen.**
If it will never be usable, hide it.
*The same rule as the Select.*

**16. Disabled sits below AA on purpose (1.19:1 to 3.64:1).**
WCAG exempts inactive controls, and raising this contrast makes the box look clickable. Don't "fix" it.
*Precedent: WCAG 1.4.3.*

**17. Checked + disabled: a gray box with a faded check** (`icon-disabled`).
It shows up on any locked settings screen, so it exists in code even without a variant in Figma.

### Error

**18. Error = an empty box with a red border + a red label.**
The typical error is a missing choice.
> **Conscious divergence:** the red label follows Material and the AL Select; Carbon and Polaris keep the label neutral.

**19. With no message in the component, the form MUST show the error in text somewhere else** (a summary at the top, or next to the group).
A red border and label are color only: WCAG 3.3.1 and 1.4.1. This rule pays for the gap.
> **Conscious divergence:** Carbon and Polaris put the message inside the component.

**20. The error shows up after submitting**, never while the person is still choosing.

### Accessibility

**21. A native input with the box painted on top; never a `div` + `role="checkbox"`.**
Space bar, announcement and mixed state come for free.
*Precedent: the first rule of ARIA.*

**22. Native `required`; on error, `aria-invalid="true"` + `aria-describedby` pointing to the form's message.**
When it's fixed, go back to `false`.

**23. Never without a visible label.**
The reason is specific to AL. The resting border, at 1.57:1, only holds because the label identifies the control; and in dark mode the disabled box is identical to the normal one (`#3E3E3E`), so only the faded label tells them apart. This is the rule that pays for the border decision.

**24. A checkbox without a visible label is reserved for the future table component** (row selection, named with `aria-label`).
Until then, don't use it.

## Out of scope, on purpose

| What | Why |
|---|---|
| One size only | The rule for every Tier 2 input. |
| Help text and error message | They're not part of the component; they belong to the form. |
| Combined variants in Figma | Checked + hover and the like are covered in code with the same tokens; the variants come in if an update asks for them. |
| Read-only | Not opened yet. An immediate action is the Switch. |
