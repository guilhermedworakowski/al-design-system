# Button · Usage guidelines

A button triggers an action.

- **Variants:** Primary, Secondary, Ghost, Danger
- **Sizes:** `sm`, `md` (default)
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#button](https://al.guilhermedesignd.com/#button)

## Do and don't

| Do | Don't |
|---|---|
| One main action, **at the end of the group**. | Two Primary buttons cancel each other out. If both are the main action, neither is. |
| Verb first, then the noun that says what it acts on. | "OK" doesn't say what it confirms. All caps slows reading down. |

## Rules

### Hierarchy

**1. One Primary per screen.**
It's the most unanimous rule in button documentation: Carbon, Primer and Red Hat all say the same. Need two actions with the same weight? Both become Secondary.
*Precedents: Carbon, Primer, Red Hat.*

**2. The Primary closes the group.**
In a row, from the lowest to the highest emphasis. In a column, common on mobile, the Primary goes on top, because there reading flows downward.

**3. Danger away from the exit.**
Keep the destructive action apart from the rest. A wrong click on "Delete" is expensive, and distance is the cheapest protection.

### The label

**4. Sentence case, never all caps.**
"Save changes", not "Save Changes" or "SAVE CHANGES". It's Material 3's standard for every label, and Primer explicitly forbids all caps.
*Precedents: Material 3, Primer.*

**5. Short, and never on two lines.**
One to three words. A fully rounded pill falls apart with a two-line label. If it doesn't fit, the problem is the text.

### Accessibility

**6. Loading: `aria-busy`, not `disabled`.**
Set `aria-busy="true"` and `aria-disabled="true"`, and block the handler in JS. The `disabled` attribute would remove the button from the focus order in the middle of the interaction, without announcing anything. Announce progress through a live region (`role="status"`, `aria-live="polite"`) and hold the state for a minimum of ~400ms.

**7. Disabled is the exception.**
A disabled button doesn't explain why it's disabled. In a form, keep it enabled and show the error when the user tries to submit. When it's really needed, use `aria-disabled`: the button stays focusable and a tooltip can say why.

**8. The low contrast of disabled is intentional.**
1.59:1 in the light theme. WCAG exempts inactive components from criterion 1.4.3: it's not a failure, it's a signal. Raising that contrast makes a disabled button look clickable.
*Precedent: WCAG 1.4.3.*

**9. Touch target.**
Both sizes meet the WCAG 2.5.8 minimum (24×24px). Only `md`, at 48px, reaches what Apple and Google recommend for touch. That's why it's the default, and `sm` needs a density reason.
*Precedent: WCAG 2.5.8.*

**10. System high contrast.**
High contrast mode drops `box-shadow`, and the focus ring would disappear with it. The component brings focus back as a native `outline` inside `@media (forced-colors: active)`.

## Out of scope, on purpose

| What | Status | If the need comes up |
|---|---|---|
| Full width | Doesn't exist | It becomes a property, not a variant. |
| Outlined Danger | Doesn't exist | Secondary with a label that states the consequence. |
| `lg` size | Doesn't exist | Closed at two sizes. |
| Icon only | Sibling set | `Icon Button`, with a required accessible name. |
