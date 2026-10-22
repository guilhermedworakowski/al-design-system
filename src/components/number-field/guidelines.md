# Number field · Usage guidelines

The number field holds a small quantity that the person adjusts a little at a time, with a − and a + around the value.

- **Built on:** a native `<input type="number">` between two `<button>`, out of the Tab order
- **Size:** one, 48px tall; the box is 140px wide
- **States:** Default, Hover, Focus, Error, Focus + Error, Read-only, Disabled; the stepper at the limit turns off
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#number-field](https://al.guilhermedesignd.com/#number-field)

## Do and don't

| Do | Don't |
|---|---|
| **A quantity: items, guests, installments.** | **A number that is not a quantity, like a zip code.** |
| **The label says what is counted, with the unit.** | **A generic label, like "Number".** |
| **Born with a value, and the − off at the minimum.** | **An empty field, with nothing to step from.** |
| **One tab stop: the field.** | **Focus stopping on the − and the +.** |
| **An error that gives the valid range.** | **An error that only turns the field red.** |
| **Steppers of at least 24×24.** | **Small steppers, below the minimum target.** |
| **The unit in the label.** | **A unit or currency suffix inside the box.** |

## Rules

### When to use

**1. For small quantities adjusted a little at a time.**
Items in a cart, number of guests, installments. The − and the + are only worth it when the step is small compared to the range.
*Precedents: Polaris and Spectrum.*

**2. Never for a number that is not a quantity.**
Zip code, phone, card, ID or year go in the Input with `inputmode="numeric"`. Nobody steps through a zip code.
*Precedents: Carbon and Spectrum.*

**3. Not for large ranges or free values.**
Price or salary go in the Input: clicking the + a thousand times is not an adjustment.
*Precedent: Spectrum.*

**4. Not for a few fixed options.**
For 3 to 5 values, use Radio or Select.
*Precedent: Material.*

### Content

**5. The label says what is being counted.**
"Quantity", "Adults". Never just "Number".
*Precedents: Carbon and Polaris.*

**6. The unit goes in the label or in the help text.**
"Weight (kg)". There is no suffix in this version.

**7. Minimum, maximum and step go in the help text when they are not obvious.**
"From 1 to 10".
*Precedent: Spectrum.*

**8. Mark the optional field, not the required one.**
The AL pattern, the same as the Input.

### Value and limits

**9. The field is always born with a value.**
The minimum or the most common default. Never empty, and with no placeholder.
*Precedent: Polaris.*

**10. At the limit, the stepper on that side turns off.**
At the minimum the − is disabled, at the maximum the +. The other one stays active.
*Precedents: Spectrum and Polaris.*

**11. A typed value out of range is not blocked while typing.**
When the person leaves the field, the form shows the error and keeps what was typed. Blocking mid-typing makes it impossible to write "15" when the minimum is 10.
> **Conscious divergence** from Polaris, which clamps to the limit on its own. The same principle as the Input: the limit never blocks typing.

**12. The step is a whole number by default.**
For decimals, set `step` and explain it in the help text.

### Interaction

**13. The − and the + are out of the Tab order.**
The field is a single tab stop: the arrow keys change the value, and the person can also type.
*Precedent: Carbon.*
> **Conscious divergence** from Spectrum, which makes the buttons focusable. AL follows Carbon so a field never takes three tab stops.

**14. The steppers have no hover of their own.**
The hover is the field's border; the cursor becomes a pointer over the button.

**15. Clicking a stepper does not move focus.**
The value changes and focus stays where it was. One click is one step: holding the button does not repeat.

### States

**16. The error says what to fix and the valid range.**
"Choose from 1 to 10". The help text is required on error, as in the Input.

**17. Read-only shows only the value, with no steppers.**
Nothing can change there, so the buttons would only be noise.

**18. Disabled only when the person cannot act there now.**
Say why nearby. Disabled falls below contrast under the WCAG 1.4.3 exemption, a declared exception as in the Button and the Input.

**19. The border at rest below 3:1 is a conscious exception.**
The visible label and the value inside pay for it, inherited from the Input and the Select.

### Accessibility

**20. A native `<input type="number">`, announced as a spin button with its minimum and maximum.**
Never a `div` rebuilt with `role`.
*Precedents: Carbon and BFIT-Bund.*

**21. The steppers are `<button tabindex="-1">` with an `aria-label`.**
"Decrease quantity". They stay available for mouse and touch.
*Precedent: Carbon.*

**22. Each stepper has a target of at least 24×24.**
WCAG 2.5.8. The icon cannot shrink.
*Precedent: WCAG 2.5.8.*

### Outside this version

**23. Unit, suffix, currency and percent stay out.**
If the need comes up, use the Input with an affix.

**24. Extra sizes and stacked buttons stay out.**
A new size or layout goes back to stage 1.

## Out of scope, on purpose

| What | Status | If the need comes up |
|---|---|---|
| Unit or currency suffix | Does not exist | The Input with an affix. |
| Holding to repeat | Does not exist | One click is one step. |
| Clamping on blur | Does not exist | The form shows the error and keeps the value. |
| Sizes and stacked buttons | One size, side by side | A new size goes back to stage 1. |
