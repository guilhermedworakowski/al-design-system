# Input · Usage guidelines

An input collects a **free, single-line answer**: a name, an email, a URL, a phone number.

- **Built on:** the native `<input>`
- **Size:** one size (48px tall)
- **States:** default, hover, focus, error, read-only, disabled, placeholder
- **Options:** prefix, suffix, help text, character counter
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#input](https://al.guilhermedesignd.com/#input)

## Do and don't

| Do | Don't |
|---|---|
| A visible label, short, describing **the data**. The placeholder is a **format example**, never the instruction. Spectrum; Carbon. | An instruction in the placeholder. It disappears when typing starts, and people who use autofill never see it. Requirements go in the help text. Spectrum. |
| **Within the limit:** the counter only appears when there's a real limit. Material 3; Carbon. | **Over the limit:** no `maxlength`. The field accepts it, the counter turns red and submitting fails with a message. Locking cuts pasted text without warning. |
| **No error:** the help text explains the field, and it's optional: it starts off. | **With an error:** the message **replaces** the help text, is required and says how to fix it. Material 3; Spectrum; Primer: "an invalid field should always have a message". |
| **Read-only:** the data has to be read and copied, and it **is submitted**. It receives Tab and doesn't react to hover. When empty, it shows "—", never a placeholder. Carbon. | **Disabled:** the field doesn't apply right now, and it **isn't submitted**. It sits below AA on purpose: 1.4.3 exempts inactive components. |

### AL marks the optional field, not the required one

The same school as the Select, the opposite of Polaris's asterisk: you mark the minority. There's no "required" style; the absence of the mark is what required means.

## Rules

### When to use

**1. A free, single-line answer** (name, email, URL, phone).
If the answer fits a known list, it's a Select (4+ options) or a Radio (up to 3).
*Precedents: Primer; Carbon separates text input from dropdown.*

**2. Several lines isn't an Input.**
It opens a Textarea; it doesn't stretch the Input.
*Precedent: Carbon separates text input from text area.*

**3. A password is the Password component.**
Number and search are out of this version.
*Precedent: Carbon, where PasswordInput, NumberInput and Search are separate components.*

### Label and optional

**4. A visible label, always; the placeholder is never the label.**
*Precedents: Carbon; Spectrum: "a field without a label is ambiguous and not accessible".*

**5. A short label, sentence case, no colon, describing the data and not the action.**
"Email", not "Enter your email".
*Precedent: Polaris; Select rules 6 and 7.*

**6. AL marks the OPTIONAL field, not the required one.**
> **Conscious divergence** inherited from the Select: the opposite school from Polaris's asterisk.

### Placeholder

**7. The placeholder is a format example** ("name@company.com"), never essential information.
It disappears when typing starts, and autofill never shows it.
*Precedents: Spectrum; Carbon.*

**8. Instructions and requirements go in the help text** ("At least 8 characters").
*Precedent: Spectrum.*

### Prefix and suffix

**9. For the fixed part of the value that the person doesn't type:** currency, unit, domain.
*Precedents: Material 3; Primer.*

**10. The affix is visual and isn't submitted.**
If the system needs the full value, the code joins them. The person never retypes what the affix shows. HTML only submits the field's content.

**11. Prefix + suffix together only when they form ONE format** ("www." + ".com"), never to stack context on both sides.
> **Partial divergence from Primer**, which recommends avoiding both. Approved because Figma draws this case.

**12. A short affix:** a symbol, unit or domain.
Explanations go in the help text.
*Precedent: Primer.*

### Counter

**13. Only with a real limit; it starts off.**
*Precedents: Material 3; Carbon.*

**14. The limit does NOT block typing (no `maxlength`).**
Past the limit, the counter turns red (`counter-error`) and submitting fails with a message. Blocking cuts pasted text without warning. If it ever blocks, `counter-error` loses its meaning and goes away.
*Precedent: GOV.UK Character count.*
> **Conscious divergence from Carbon**, which blocks.

**15. An error for any other reason → the counter stays gray.**
If the error is "required field", a red counter would point at the wrong cause.

### Help text and error

**16. Same slot: the error replaces the help text**, which comes back when it's fixed; both carry the same essential information.
*Precedents: Material 3; Spectrum.*

**17. On error, the message is required and says how to fix it.**
*Precedents: Primer: "an invalid field should always have a message"; Spectrum.*

**18. Help text is optional and starts off.**
*Inherited from the Select.*

**19. The error shows up when leaving the field or submitting, never on every keystroke.**
Only the counter updates in real time.
*Inherited from the Select.*

### States

**20. Focus ring on click AND on Tab; there's no Active state.**
That's the `:focus-visible` spec for an element that accepts typing.

**21. Read-only ≠ disabled.**
Read-only: read and copy, and it IS submitted. Disabled: doesn't apply right now, and it is NOT submitted.
*Precedents: Carbon (read-only for copying); MDN (submission).*

**22. An empty read-only field shows "—", never a placeholder.**
A placeholder on `bg-subtle` measures 4.21:1.

**23. Read-only receives focus by Tab and doesn't react to hover.**

**24. Disabled sits below AA on purpose.**
Don't "fix" it.
*Precedent: WCAG 1.4.3 exemption.*

### Size and width

**25. One size only (48px).**

**26. The width follows the expected size of the answer.**
The component takes 100% of its container, and the form decides the container: a postal code doesn't need the width of an address.
*Precedent: GOV.UK: "use appropriately-sized text inputs".*

### Accessibility

**27. A native `<input>` with the right `type` (email, url, tel) + `autocomplete`.**
*Precedent: Spectrum.*

**28. `<label for>` + native `required`; no `aria-label` when there's a visible label.**
*Select rules 24 and 25.*

**29. The affix is part of the accessible name:** `aria-labelledby` = label + prefix + suffix ("Website, www., .com").
*Precedent: Polaris.*

**30. Error: `aria-invalid="true"` + `aria-describedby` pointing to the message. The counter is only announced with focus** (`aria-live="polite"` when focused, `off` otherwise).
*Precedent: Polaris PR #1720.*

**31. Never without a visible label.**
The resting border (1.57:1) and the read-only border (1.14:1) fall below 3:1 and only hold because the label and the text identify the field. This is the rule that pays for the contrast exception.

## Out of scope, on purpose

| What | Why |
|---|---|
| Warning, leading icon, clear button | Not in this version. |
| Password, number, search and several lines | Each need opens its own component (Password, Textarea) and doesn't stretch the Input. |
| Extra sizes | One size only, as in the Select. |
