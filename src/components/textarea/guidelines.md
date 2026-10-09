# Textarea · Usage guidelines

A textarea collects a **free answer that can run past one line**: a description, a comment, a justification.

- **Built on:** the native `<textarea>`
- **Height:** 3 lines by default (96px), which is also the minimum; resizes vertically only
- **States:** default, hover, focus, error, read-only, disabled, placeholder
- **Options:** help text, character counter
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#textarea](https://al.guilhermedesignd.com/#textarea)

## Do and don't

| Do | Don't |
|---|---|
| A visible label, short, saying **the data**. The placeholder is an example of the kind of answer; requirements go in the help text. Spectrum; Carbon. | An instruction in the placeholder. It disappears on the first keystroke, and in a long text the person loses the reference halfway through. Spectrum. |
| A long answer is expected, so the field is tall: `rows="6"`. GOV.UK; Primer; Polaris. | A 3-line field asking for a whole account says, without meaning to, "keep it short". Three lines is the default **and the minimum**. |
| **Within the limit:** the counter only appears when there's a real limit, and it starts off. Material 3; Carbon. | **Over the limit:** no `maxlength`. The field accepts it, the counter turns red and submitting fails with a message. In a Textarea this matters more: pasting long text is the common case. |
| **Read-only:** read, copy and scroll, and it **is submitted**. It receives Tab, and it has to: without focus, keyboard users can't scroll a long text. When empty, it shows "—". Carbon. | **Disabled:** doesn't apply right now, **isn't submitted**, and doesn't resize. It sits below AA on purpose: 1.4.3 exempts inactive components. |

### AL marks the optional field, not the required one

The same school as the Select and the Input, the opposite of Polaris's asterisk. The absence of the mark is what required means.

## Rules

### When to use

**1. An answer that can run past one line** (description, comment, justification).
A few words → Input.
*Precedents: Carbon; Polaris.*

**2. Never for an address, a date or any data with parts.**
Split it into several Inputs: in a free field, everyone writes in a different format.
*Precedents: Carbon and GOV.UK (free text only when the format is unpredictable).*
> **Conscious divergence** from Polaris's address example.

**3. An answer that fits a known list → Select (4+) or Radio (up to 3).**
*Precedent: Carbon.*

### Label and optional

**4. A label that's always visible; the placeholder is never the label.**
*Precedents: Carbon; Spectrum.*

**5. A short label, first letter capitalized, no colon, saying the data and not the action.**
"Description of the problem".
*Precedent: Polaris; Input rule 5.*

**6. AL marks the OPTIONAL field, not the required one.**
> **Conscious divergence** inherited from the Select and the Input (Polaris uses an asterisk).

### Placeholder

**7. The placeholder is an example of the kind of answer, never an essential instruction.**
It disappears when typing starts.
*Precedents: Spectrum; Carbon.*

**8. Instructions and requirements go in the help text.**
*Precedent: Spectrum.*

### Height and resizing

**9. 3 lines by default (96px)**, which is also the minimum.

**10. The height follows the expected size of the answer**, through `rows` (≥ 3).
A short field asking for long text signals "keep it short".
*Precedents: GOV.UK; Primer; Polaris.*

**11. Text longer than the field scrolls; the field doesn't grow on its own.**
*Precedents: Carbon; Spectrum Web Components; Polaris issue #1391 as a counterexample.*

**12. It resizes vertically only** (`resize: vertical`).
The width belongs to the form.
*Precedent: Primer.*

**13. Disabled doesn't resize (`resize: none`); read-only does.**

**14. It takes 100% of its container**; the form decides the width.
*Input rule 26; GOV.UK.*

### Counter

**15. Only with a real limit; it starts off.**
*Precedents: Material 3; Carbon.*

**16. The limit does NOT block typing (no `maxlength`).**
Past the limit → `counter-error`, and submitting fails with a message. Pasting long text is the common case.
*Precedents: GOV.UK Character count; Input rule 14.*
> **Conscious divergence from Carbon**, which blocks.

**17. An error for any other reason → the counter stays gray.**

### Help text and error

**18. Same slot: the error replaces the help text**, which comes back when the error is fixed.
*Precedents: Material 3; Spectrum.*

**19. On error, the message is required and says how to fix it.**
*Precedent: Primer.*

**20. The error shows up when leaving the field or submitting, never on every keystroke.**
Only the counter updates in real time.
*Inherited from the Select and the Input.*

### States and keyboard

**21. Enter breaks the line, it never submits.**
An optional shortcut (Ctrl+Enter) doesn't replace the visible button. A chat where Enter sends is another component.
*Precedent: native behavior (MDN).*

**22. Focus ring on click AND on Tab; there's no Active state.**
*Precedent: `:focus-visible`.*

**23. Read-only ≠ disabled.**
Read-only: read, copy and scroll, and it IS submitted. Disabled: it is NOT submitted.
*Precedents: Carbon; MDN.*

**24. Read-only receives focus by Tab** (needed to scroll long text with the keyboard), doesn't react to hover and, when empty, shows "—".
*Input rules 22 and 23; scrolling is new here.*

**25. Disabled sits below AA on purpose.**
Don't "fix" it.
*Precedent: WCAG 1.4.3 exemption.*

### Accessibility

**26. A native `<textarea>` with `rows`, never a `contenteditable` div.**
*Precedents: Primer; Carbon.*

**27. `<label for>` + native `required`; no `aria-label` when there's a visible label.**
*Select rules 24 and 25.*

**28. Error: `aria-invalid="true"` + `aria-describedby`. The counter is only announced with focus.**
*Precedents: Polaris PR #1720; Carbon issue #12071.*

**29. Never without a visible label.**
The resting border (1.57:1) and the read-only border (1.14:1) fall below 3:1. This is the rule that pays for the contrast exception.

## Out of scope, on purpose

| What | Why |
|---|---|
| Prefix and suffix | A fixed part of the value makes no sense in free, multi-line text. |
| Growing on its own | If the need comes, it comes in as an option, always with a maximum height. Polaris grows with no ceiling, and that became an issue. |
| Horizontal resizing | Width belongs to the form. |
| Rich text editor | Bold, lists: another component. |
| Warning and extra sizes | Not in this version. |
