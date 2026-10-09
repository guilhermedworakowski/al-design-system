# Radio · Usage guidelines

A radio picks **exactly one option** from a short list where every option is visible.

- **Built on:** the native `<input type="radio">`
- **Size:** one size (24px circle, 14px dot)
- **States:** unselected, selected, hover, focus, error, disabled
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#radio](https://al.guilhermedesignd.com/#radio)

## Do and don't

| Do | Don't |
|---|---|
| **Select one at the start** when there's a safe, most likely answer, and it comes first. Since a selected radio can't be unselected, "None" becomes an option. Spectrum, Polaris; Carbon for "None". | **Select nothing** when the choice has to be a conscious one: sensitive data, consent, something with a cost. Carbon, which currently recommends no preselection. The references disagree, and AL decides by context. |
| Short, only the first letter capitalized, no final period. The options share the same structure and don't overlap. Polaris. | Someone with 5 employees fits two options: the ranges overlap. And the third one breaks the pattern: a sentence with a period, no number. Polaris. |
| The error goes on the `fieldset` and lights up every option together. The form describes the error in text, and the question points to it with `aria-describedby`. Primer, Carbon, Polaris. | Only red borders and labels. That's **color only**, and WCAG requires the error to be described in text (3.3.1) and not communicated by color alone (1.4.1). |

### The error belongs to the question, and the component has no message

Carbon, Polaris and Primer put the message on the group. AL has no group component and leaves the text to the form, which is why rule 22 is mandatory, not a suggestion.

## Rules

### When to use

**1. A single option from a short, mutually exclusive list, with every option visible for comparison.**
*Precedents: Primer, Spectrum, Material.*

**2. Up to 5 or 6 options; above that, use the Select.**
*Precedents: Material (5), Primer and Spectrum (6).*

**3. Never for several choices (that's a Checkbox), and never a radio on its own: at least two.**
A standalone yes/no for consent is also a Checkbox.
*Precedents: Polaris, Carbon.*

**4. Never for an immediate action.**
That's the Switch. The choice only takes effect on submit or save, because the arrow keys change the choice while the person navigates.
*Precedents: Primer, Material.*

### The question

**5. The same `name` on every radio in the question.**
It's what makes selecting one unselect the other, and lets the arrow keys move between them. Native behavior.

**6. The application builds the `fieldset` + `legend`.**
There's no group component. Without them, the screen reader announces "Monthly, radio button" without saying what the question is.
*Precedents: Carbon, Polaris, Primer.*

**7. Vertical, one per row.**
Horizontal only with 2 or 3 short options in a tight layout, and with the space between items clearly larger than the 8px between circle and label.
*Precedent: Spectrum.*

**8. A logical order.**
Most common first, ascending, or the natural order; not alphabetical without a reason.
*Precedents: Polaris, Spectrum.*

### Initial selection

**9. Decided by context.**
Preselect when there's a safe, most likely answer, and put it first. Don't preselect when the choice has to be a conscious one (sensitive data, consent, something with a cost).
*Precedents: Spectrum and Polaris ask for a default; Carbon currently asks for none. The rule joins both by context.*

**10. A selected radio can't be unselected: if "none" is a valid answer, it becomes an option** ("None", "Other").
*Precedent: Carbon.*

### Label

**11. A visible label on the right, and clicking it selects the radio** (a wrapping `<label>`).
WCAG 2.5.8.
*Precedents: Carbon, Polaris.*

**12. Short, sentence case, no final period; options with the same structure and no overlap** ("1 to 5" / "6 to 10").
*Precedent: Polaris.*

**13. A long label wraps aligned to the top of the circle.**
In AL this comes for free: the circle and the line height both measure 24px.
*Precedent: Carbon.*

### States

**14. Selected = orange ring + dot; the shape tells them apart, not only the color.**
That's why the dot shrank to 14px.

**15. Hover only on the unselected radio.**
A selected radio doesn't unselect on click.

**16. Focus ring in every state.**

**17. The arrow keys move focus and choice together.**
Changing the option never triggers an action on its own.
*Precedent: Primer.*

**18. Disabled only when it depends on another choice on the screen; if it will never be available, hide it.**
If every option would be disabled, rethink the question.
*The same rule as the Select and the Checkbox.*

**19. Disabled sits below AA on purpose (1.19:1 to 3.64:1).**
WCAG exempts inactive controls, and raising this contrast makes the option look clickable. Don't "fix" it.
*Precedent: WCAG 1.4.3.*

**20. Selected + disabled: a gray circle with a faded dot** (`dot-disabled`).
It shows up on any locked plan, so it exists in code even without a variant in Figma.

### Error

**21. The error lights up every radio in the question at the same time, never just one.**
Red border + red label.
*Precedents: Primer, Spectrum, Carbon, Polaris.*
> **Conscious divergence:** the red label follows Material and the AL Select and Checkbox; Carbon and Polaris keep the label neutral.

**22. With no message in the component, the form MUST write the error in text next to the question** (in the `legend` or below the `fieldset`).
WCAG 3.3.1 and 1.4.1. This rule pays for the gap.
> **Conscious divergence:** Carbon, Polaris and Primer put the message on the group.

**23. Required is marked on the question, never on a radio; AL marks the optional one** ("(optional)" in the `legend`).
*Precedent: Primer, plus the Select rule.*

**24. The error shows up after submitting**, never while the person is choosing.

### Accessibility

**25. A native input with the circle painted on top; never a `div` + `role="radio"`.**
Arrow keys, a single Tab stop and "2 of 3" come for free.
*Precedent: the first rule of ARIA.*

**26. `required` on the radios; on error, `aria-invalid="true"` + `aria-describedby` on the `fieldset`, not on the radio.**
*Precedents: Carbon (ARIA doesn't allow `aria-invalid` on a radio), Polaris.*

**27. Never without a visible label.**
The reason is specific to AL. The resting border, at 1.57:1, only holds because of the label, and in dark mode the disabled circle is identical to the normal one (`#3E3E3E`). This is the rule that pays for the border decision.

## Out of scope, on purpose

| What | Why |
|---|---|
| One size only | The rule for every Tier 2 input. |
| Group component | Not now, and not on the roadmap: the question is the native `fieldset` + `legend`. |
| Help text and error message | They're not part of the component; they belong to the form. |
| Combined variants in Figma | Covered in code with the same tokens. |
| Radio card and read-only | Not opened yet. An immediate action is the Switch. |
