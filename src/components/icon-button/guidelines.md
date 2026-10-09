# Icon Button · Usage guidelines

A button whose only content is an icon.

- **Variants:** Primary, Secondary, Ghost, Danger
- **Sizes:** `sm` (36px), `md` (48px)
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#icon-button](https://al.guilhermedesignd.com/#icon-button)

## Do and don't

| Do | Don't |
|---|---|
| Search, close, more options: recognizable **without a caption**. | Filter, export, archive: the drawing doesn't explain itself. These need a Button with a label. |
| One variant for the whole group. | Three variants suggest a hierarchy that doesn't exist between three sibling actions. |
| `aria-label="Search"`: the **action**. | `aria-label="Magnifier"`: the drawing. Listeners need to know what will happen, not what's on screen. |

## Rules

### When to use

**1. Only for universally recognizable actions.**
Here the icon is the only carrier of meaning: if it isn't recognized, the action doesn't get harder, it disappears. NN/G states plainly that icons rarely replace labels, and that users only learn a drawing after repeated use.
*Precedent: NN/G.*

**2. Never for the main action on the screen.**
A primary action needs a Button with a visible label. Polaris says to provide text whenever possible and to treat the accessible label as a fallback, not the default.
*Precedent: Polaris.*

**3. Don't use it when the action depends on the label to identify its target.**
"Delete" only works when the surrounding row or card already says what. Without that, the `aria-label` would have to carry the whole target, "Delete order 4471", which is longer than a tooltip can hold, by Spectrum's definition.
*Precedent: Spectrum.*

### Hierarchy

**4. One group, one variant.**
The difference between the buttons comes from position and icon, not from the variant. That's how Primer builds its icon button groups.
*Precedent: Primer.*

**5. At most one Primary per region.**
It's counted per region, not per component: one Primary across Icon Buttons and Buttons combined.

### The accessible name

**6. The label describes the action, never the icon.**
"Search", never "Magnifier". "Close", never "X". The wording is literally Primer's.
*Precedent: Primer.*

**7. With a tooltip, the name comes from it.**
The button points to the tooltip with `aria-labelledby` and has no `aria-label`, never both. That way the text people see and the name the screen reader announces are the same text, not two copies that can drift apart. Drift breaks voice control: saying "click Search" doesn't activate a button labeled some other way. Polaris is explicit about this, and the Icon Button gate rejects the two together.
*Precedent: Polaris.*

**8. Use a tooltip on every icon-only button.**
Primer always renders one, Polaris says it should be provided, and Spectrum defines the tooltip as exactly the place to show an icon-only button's label. `aria-label` alone serves screen readers, but not sighted people who don't recognize the drawing; the tooltip serves both. It doesn't replace rule 1: it's a safety net for people who hesitate, not a license for an ambiguous icon.
*Precedents: Primer, Polaris, Spectrum.*

### Accessibility

**9. Loading: `aria-busy`, not `disabled`.**
Set `aria-busy="true"` and `aria-disabled="true"`, and block the handler in JS. The `disabled` attribute would remove the button from the focus order in the middle of the interaction, without announcing anything.

**10. Progress is announced outside the button.**
On the Button, changing the label from "Publish" to "Publishing…" already gives notice. **Here there's no label to change**, so the live region (`role="status"`, `aria-live="polite"`) stops being a complement and becomes the only channel that says something has started.

**11. The low contrast of disabled is intentional.**
WCAG exempts inactive components from 1.4.3: it's not a failure, it's a signal. Raising that contrast makes a disabled button look clickable.
*Precedent: WCAG 1.4.3.*

**12. Touch target.**
Both sizes meet the WCAG 2.5.8 minimum (24×24px): 36px for `sm` and 48px for `md`. Only `md` reaches the 44px Carbon recommends for icon targets. By a recorded decision there is no CSS hit-area expansion, and the trade-off is a usage rule: `sm` is only for high density, never in a primarily touch interface.
*Precedents: WCAG 2.5.8, Carbon.*

**13. System high contrast.**
High contrast mode drops `box-shadow`, and the focus ring would disappear with it. The component brings focus back as a native `outline` inside `@media (forced-colors: active)`.

## Out of scope, on purpose

| What | Status | If the need comes up |
|---|---|---|
| `lg` size | Doesn't exist | Closed at two sizes, like the Button. |
| Outlined Danger | Doesn't exist | The same deliberate absence as in the Button. |
| Selected / toggle | Doesn't exist | A new component, not a variant: it needs `aria-pressed` and its own state contract. Primer and Spectrum treat it separately. |
| With a visible label | Sibling set | `Button`, which already handles icons on the left and right. |
