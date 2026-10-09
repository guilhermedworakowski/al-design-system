# Password · Usage guidelines

A password field for **every password someone creates or types**, with a button to show or hide it.

- **Built on:** the native `<input type="password">` + a `<button>` for the eye
- **Size:** one size (48px tall)
- **States:** default, hover, focus, error, disabled, hidden or shown
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#password](https://al.guilhermedesignd.com/#password)

## Do and don't

| Do | Don't |
|---|---|
| A visible label saying the data: "Password", "Current password", "New password". A short, generic placeholder, or none. Polaris. | A requirement in the placeholder. It disappears on the first keystroke, and the password manager never shows it. |
| Requirements **above** the field, in the form, linked with `aria-describedby`. People read them before making a mistake. Polaris. | A requirement that only appears as an error. People find out the rule after trying. |

### "Enter your password" is a conscious divergence

In the Input, the placeholder only holds a format example (Input rule 7). A password has no format to show, so the Password accepts a generic placeholder: never a requirement, never an example password. And the Password is always required: there's no "(Optional)" mark.

## Rules

### When to use

**1. Every password someone creates or types.**
Sign in, sign up, password change.
*Precedent: GOV.UK.*

**2. A one-time code (SMS) isn't a Password.**
It goes in an Input with `autocomplete="one-time-code"`. It isn't a stored secret, and hiding it only gets in the way of copying it over.
*Precedent: GOV.UK.*

**3. "Confirm password" isn't part of the component.**
The form decides, and showing the password already covers the check that field used to do.

### Label

**4. A visible label describing the data** ("Password", "Current password", "New password"); two fields → distinct labels.
*Precedents: Polaris; GOV.UK.*

**5. In AL, the Password is always required: no "(Optional)" mark.**
An optional password is a new need.

### Placeholder

**6. Short and generic ("Enter your password"), or empty; never a requirement or an example.**
*Precedent: Polaris.*
> **Conscious divergence** from Input rule 7.

### Requirements and error

**7. Requirements show up BEFORE typing**: in the form, above the field, linked with `aria-describedby`.
*Precedent: Polaris.*

**8. Error: a required message that says how to fix it.**
"The password needs at least 8 characters".
*Precedent: Primer; Input rule 17.*

**9. Sign-in never says which credential was wrong.**
"Incorrect email or password", never "Incorrect password". Saying which one was wrong helps whoever is trying to break in.
*Precedent: GOV.UK.*

**10. A failed sign-in → the field comes back empty and hidden.**
*Precedent: GOV.UK.*

**11. The error shows up when leaving the field or submitting, never on every keystroke.**
*Input rule 19.*

**12. No maximum, no `maxlength`; the minimum (8 recommended) belongs to the system, not the component.**
*Precedent: GOV.UK.*

### Show and hide

**13. It always starts hidden.**
Only the person decides to show it.
*Precedent: GOV.UK.*

**14. The icon shows the ACTION** (eye = show, eye-off = hide).
*Precedents: Material, Carbon.*

**15. Toggling doesn't clear the value or move focus off the button.**
*Precedent: GOV.UK.*

**16. On form submit, it goes back to `type=password`.**
The password doesn't stay exposed on the next screen.
*Precedent: GOV.UK.*

**17. Each field has its own eye; the accessible name tells them apart** ("Show new password").
*Precedent: GOV.UK.*

### States

**18. On error, the value stays `text-primary`; only the label, border and message turn red.**
The red points to what to fix, not to the content.

**19. The eye's focus ring goes around the eye only, round (`radius.full`), always orange, even on error.**
*Precedents: Carbon; the Tag's X.*

**20. Disabled: always hidden, with the eye faded and out of the Tab order.**

**21. Disabled sits below AA on purpose.**
Don't "fix" it.
*Precedent: WCAG 1.4.3 exemption.*

**22. No read-only.**
A password "just for reading" exposes the data with no use to the reader.

**23. The 24×24 eye is the exact WCAG 2.5.8 minimum; never shrink the icon.**

### Size

**24. One size (48px); the width comes from the form, never narrow (a good password is long).**
*Input rule 26; GOV.UK.*

### Accessibility

**25. A native `<input type="password">` + `autocomplete` `current-password` / `new-password`.**
*Precedents: GOV.UK, Polaris.*

**26. `spellcheck="false"` + `autocapitalize="none"`.**
*Precedent: GOV.UK.*

**27. Pasting is always allowed; never block password managers.**
*Precedents: WCAG 3.3.8; GOV.UK.*

**28. The eye is a `<button type="button">`, with `aria-label` toggling between "Show password" and "Hide password", `aria-controls` pointing to the field, and the icon `aria-hidden`.**
*Precedent: GOV.UK; the Icon contract.*

**29. `<label for>`; error with `aria-invalid="true"` + `aria-describedby`; no `aria-label` when there's a visible label.**
*Input rules 28 and 30.*

**30. Never without a visible label.**
The resting border, at 1.57:1, only holds because of the label. This is the rule that pays for the exception.
*Input rule 31.*

## Out of scope, on purpose

| What | Why |
|---|---|
| Strength meter and live checklist | They weigh a lot in behavior; the gain is small in this version. |
| Caps Lock warning | Left for a future version. |
| Confirm password | It belongs to the form (rule 3). |
| Read-only | A password "just for reading" exposes the data with no use to the reader. |
| Help text at rest | Requirements live in the form. |
| Copy button and extra sizes | Not in this version. |
