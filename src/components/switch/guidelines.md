# Switch · Usage guidelines

A switch turns a setting **on or off, with immediate effect**.

- **Built on:** the native `<input type="checkbox" role="switch">`
- **Size:** one size (38×24px track)
- **States:** off, on, hover, focus, disabled
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#switch](https://al.guilhermedesignd.com/#switch)

## Do and don't

| Do | Don't |
|---|---|
| Name the setting. Test: read it aloud and add "on" or "off" at the end. "Email notifications, on" makes sense. NN/g, Primer. | A question isn't a label: "Do you want to receive notifications?, off" makes no sense. Don't use the state as the label either ("Notifications enabled"), because it would have to change on every click. NN/g, Carbon. |

### When the action fails

The thumb moves on click. If the system refuses the change, it goes back to the real state and the application shows an Error Toast. The switch never shows a state the system doesn't have. Primer asks to wait for the response with a loading indicator; AL has no such state, and without an indicator the person clicks and it looks like nothing happened. That's why the change is immediate and the rollback belongs to the application.

## Rules

### When to use

**1. Turning a setting on or off that applies immediately, with no "Save".**
Whoever flips a switch expects the change to have already happened.
*Precedents: Carbon, Primer, Polaris, Spectrum, Material.*

**2. If it only applies after submitting, saving or validating, it's a Checkbox.**
A switch in a form with "Submit" gives the impression it already applied, and it didn't. That's also why the switch has no error state.
*Precedents: Polaris; Primer ("never replaces a checkbox").*

**3. Only two opposite states.**
If the options aren't a simple on/off ("Daily / Weekly"), it's a Radio or a Select.
*Precedents: Polaris, Carbon.*

**4. Never for accepting terms or consent.**
Consent depends on submitting and is usually required: it's a Checkbox.
*Precedents: Primer, Polaris.*

### More than one switch

**5. A vertical list, one per row, each one independent.**
Turning one on never turns another off. If it has to, the question is single choice, and it's a Radio.
*Precedents: Material (settings), Carbon.*

**6. The group title belongs to the application.**
A section heading, or `fieldset` + `legend`. There's no group component, as with the Radio.
*Precedent: Carbon.*

### Label

**7. Visible, on the right, and clicking it toggles.**
The `<label>` wraps the control: the clickable area is the whole row, not just the 38×24 track (WCAG 2.5.8).
*Precedents: Carbon, Material.*

**8. It names the setting, not the state, and it's not a question.**
"Email notifications". Test: read it aloud and add "on" or "off".
*Precedents: NN/g, Primer.*

**9. It never changes with the state.**
The control is what shows the state.
*Precedent: Carbon.*

**10. No "On / Off" next to it or inside it.**
The switch alone is enough.
*Precedent: Material.*
> **Conscious divergence** from Primer, which shows that text (status text is out of scope).

**11. Short, sentence case, no final period.**
A long label wraps, with the track aligned to the first line (the 24px track equals the line height).
*Precedents: NN/g, Carbon.*

### Initial state

**12. The initial state is the system's real state, never a visual default.**
If notifications are active in the system, the switch starts on. Never preselect "because it's recommended": the switch doesn't propose, it shows.
*Precedent: Material ("shows the real status").*

### States

**13. On = orange track + thumb on the right; position and color change together** (WCAG 1.4.1).
Inherited exception: the off thumb measures 1.96:1 in light and 2.98:1 in dark (neutral-400 is the ceiling), supported by the orange track (3.12:1) and by rule 23.

**14. Hover on the whole row, with the signal only on the off track's border; nothing changes when on.**
*The Checkbox row rule.*

**15. Focus ring in every state, outside the track.**

**16. It applies the moment it's clicked; never ask for confirmation. A serious action isn't a switch.**
Never ask "Are you sure?" for something another click undoes.
*Precedents: Primer, Polaris, Material.*

**17. Disabled only when it depends on another setting on the screen; if it will never be available, hide it.**
*The same rule as the Select, Checkbox and Radio.*

**18. Disabled sits below AA on purpose** (label 2.10:1; thumb and border 1.19 to 2.19:1).
WCAG exempts inactive controls, and raising this contrast makes the switch look clickable. Don't "fix" it.
*Precedent: WCAG 1.4.3.*

**19. On + disabled: a gray track, thumb on the right one shade darker (`thumb-checked-disabled`), no orange.**
In code only, with no variant in Figma.

### No error, and when the action fails

**20. It never has an error and is never "required".**
If a setting must be on for the person to continue, it's consent, and that's a Checkbox.
*Precedents: Spectrum, Polaris.*

**21. It changes immediately and, if it fails, the thumb goes back to the real state and the application shows an Error Toast.**
The switch never shows a state the system doesn't have.
*Precedent: Material (real status).*
> **Conscious divergence:** Primer asks to wait with a loading indicator, which AL doesn't have. Rejected because, without an indicator, it looks like a click that didn't work.

### Accessibility

**22. A native `<input type="checkbox" role="switch">` with the track painted on top; never a `div` or `button` + ARIA.**
It announces "switch, on".
*Precedents: Carbon, Spectrum.*
> **Conscious divergence** from Primer (`button` + `aria-pressed`): the first rule of ARIA.

**23. Never without a visible label.**
It pays for both contrast exceptions (border 1.47:1 and thumb 1.96:1).
> **Conscious divergence** from Spectrum and Carbon, which accept `aria-label`.

**24. Only Space toggles, not Enter.**
That's the native checkbox behavior.
> **Conscious divergence** from Carbon, which accepts Enter.

**25. With `prefers-reduced-motion`, the thumb changes sides without sliding.**
*Precedents: WCAG 2.3.3, Material. The same rule as the Checkbox and Radio.*

## Out of scope, on purpose

| What | Why |
|---|---|
| One size only | The rule for every Tier 2 input. |
| Error, status text and read-only | The switch has immediate effect. Read-only only exists in Carbon; if it comes up, show the value as text. |
| Icon inside the thumb | Material has it; AL doesn't use it. |
| Help text below the label | Primer has it. If the need comes up, it opens a new round for the component, not something invented in the application. |
| Group component and loading state | The group belongs to the application; the wait is covered by the immediate change (rule 21). |
