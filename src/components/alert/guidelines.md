# Alert · Usage guidelines

An alert is a message at the top of the page about a **state that is still true**: something good, a context, a risk, or a reason for care.

- **Status:** Success, Info, Warning, Danger
- **Position:** at the top of the page, below the header, one per page
- **Behavior:** `alert.js`; only Success and Info can be dismissed
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#alert](https://al.guilhermedesignd.com/#alert)

## Do and don't

| Do | Don't |
|---|---|
| **It states the consequence:** the title is the subject; the description, what to do. The action solves it. | **A shout:** it doesn't say what's wrong or what to do. |
| **Danger is care:** it warns about something irreversible before it happens. No X: it stays as long as the risk exists. | **A click confirmation:** what just happened is a Toast, in the corner, and it goes away on its own. |

## Rules

### When to use each status

**1. Success: a good state that still holds.**
"Your store is published". It doesn't confirm a click; that's a Toast.
*Precedents: Polaris, Spectrum.*

**2. Info: a context that changes how the page is used.**
"Reports are updated every hour".
*Precedents: Spectrum, Polaris.*

**3. Warning: there will be a problem if nothing is done.**
"Your plan expires in 3 days".
*Precedents: Polaris, Carbon.*

**4. Danger: it asks for care, it isn't an error.**
An irreversible action ahead, or an active risk. In AL, an action error is a Toast and a field error belongs to the form.
*Precedent: Primer.*
> **Conscious divergence** from Polaris and Carbon, which use the color for errors.

### When not to use

**5. What just happened is a Toast.**
"Change saved" appears in the corner and goes away.
*Precedent: Carbon separates inline from toast.*

**6. A filling error stays in the field.**
In the field's own message.
*Precedents: Carbon, Polaris.*

**7. Don't point out what the screen should already make clear.**
If people need an alert to find the button, the problem is the button.
*Precedent: Polaris.*

**8. Content with no status is a Card.**
The Alert is a card with a specific subject, not a pretty frame.

### Position and quantity

**9. At the top, below the header.**
Before the page content.
*Precedents: Material, Carbon.*

**10. The content's width.**
No fixed width.
*Precedent: Material.*

**11. One per page.**
With two subjects, the most serious one shows: Danger, Warning, Info, Success.
*Precedents: Primer, Polaris, Material.*

### Content

**12. A short title that states the subject.**
Only the first letter capitalized, no final period.
*Precedent: Polaris.*

**13. A description, always, in up to two lines.**
What's happening and what to do, with a period.
*Precedents: Carbon, Polaris.*

**14. No generic title.**
"Attention!" says nothing; state the consequence.
*Precedent: Polaris.*

### Icon

**15. Fixed per status, the same as the Toast.**
A circle with a check, a triangle, a circle with an exclamation mark, and an "i".
*Precedent: Spectrum.*

**16. Announced with the status name.**
`role="img"` and `aria-label`: "Danger".
*The AL Icon contract.*

### Actions

**17. Up to two, aligned to the right.**
Ghost on the left, Primary on the right.
*Precedent: Primer.*

**18. The Alert's Primary is the screen's Primary.**
If the page already shows another Primary, the Alert uses Ghost only. The Button rule: one at a time.

**19. A verb and an object in the label.**
"Renew plan". Never "OK" or "Close": the X is what closes.
*Precedents: Polaris, Carbon.*

### Dismissing

**20. An X only on what can be ignored.**
Success and Info can have one; Warning and Danger can't, as long as the situation exists. They leave when it's resolved.
*Precedents: Primer, Polaris.*

**21. Once closed, it doesn't come back.**
The choice is saved; the same Alert doesn't reappear on the next visit.
*Precedent: Primer.*

**22. Focus moves forward.**
On closing, it goes to the next focusable element; if there's none, to the main content.
*Precedent: WCAG 2.4.3.*

### Accessibility

**23. Present on load, it's regular content.**
Read in order, with no live region.
*Precedent: Spectrum reserves alert for immediate attention.*

**24. Inserted later, it's announced.**
Danger in `role="alert"`; the others in `role="status"`.
*Precedents: Spectrum, Carbon.*

**25. It never steals focus.**
*Precedent: Carbon.*

**26. The title isn't a heading.**
It sits above the `h1` and doesn't go into the headings list. Internal precedent: the Accordion.
> **Conscious divergence** from Spectrum.

**27. The X is a real button.**
"Close alert", reachable with Tab.
*Precedent: Carbon.*

### Out of scope

**28. No neutral status, colored background, full-screen banner or sizes.**
Info covers neutral; the light background with a border is the Toast's.

**29. It doesn't disappear on its own and doesn't stack.**
That's a Toast.
*Precedent: Material: persistent until resolved or closed.*
