# Toast · Usage guidelines

A toast confirms **something that just happened**, in the corner of the screen, without interrupting.

- **Status:** Success, Info, Warning, Error
- **Position:** bottom right, one at a time, in a queue
- **Behavior:** `toast.js`; Success and Info leave after 6s, Warning and Error stay until closed
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#toast](https://al.guilhermedesignd.com/#toast)

## Do and don't

| Do | Don't |
|---|---|
| **Short and concrete:** it can be read at a glance, before it disappears. | **A celebration:** long, and it doesn't say what was saved. |
| **An error with a way out:** what failed and what to do. It stays until the person closes it. | **A form error:** that's the field's message, next to the field. |

## Rules

### When to use each status

**1. Success confirms what the person just did.**
"Product saved".
*Precedents: Spectrum, Polaris.*

**2. Info announces a process that continues without them.**
"Export started".
*Precedent: Spectrum.*

**3. Warning: done, with a caveat.**
"Saved without the image".
*Precedent: Carbon.*

**4. Error only for a non-critical failure, in one sentence.**
If the person needs to decide something, it's a Modal.
*Precedents: Polaris, Carbon.*

**5. It responds to something that just happened.**
It never appears on its own when the page loads.
*Precedent: Carbon.*

### When not to use

**6. A form error stays in the field.**
In the field's own message, never in a toast.
*Precedents: Carbon, Polaris.*

**7. What's essential can't disappear.**
Either it's also on the page, or it's a Warning or an Error, which stay.
*Precedent: W3C, the WCAG 2.2.1 example.*

**8. Don't repeat what the screen already shows.**
Unless the person may have missed the change.
*Precedent: Polaris.*

### Content

**9. A short title: the thing, and what happened to it.**
"Order sent", up to about four words.
*Precedent: Polaris (three; in Portuguese the article adds weight).*

**10. Only the first letter capitalized, no period on the title.**
*Precedents: Nord, Polaris.*

**11. An optional description, one sentence, with a period.**
If it needs more, it isn't a toast.
*Precedent: Primer.*

**12. An error says what failed and what to do.**
No "Oops!" and no error code.
*Precedents: Polaris, Carbon.*

### Icon

**13. Required and fixed per status.**
A circle with a check, a triangle, a circle with an exclamation mark, and an "i": the cue that doesn't depend on color.
*Precedent: Spectrum.*

**14. Announced with the status name.**
`role="img"` and `aria-label`: "Error".
*The AL Icon contract.*

### Behavior

**15. One at a time, in a queue.**
One that arrives while another is on screen waits for it to leave.
*Precedent: Material.*

**16. Bottom right corner.**
16px from the edges; on mobile, the screen width minus 16px on each side.

**17. Success and Info leave after 6s.**
The timer pauses with the pointer over it or focus inside, and resumes where it stopped.
*Precedent: Spectrum.*

**18. Warning and Error stay until closed.**
And they hold the queue.

**19. The X always closes it; so does Esc.**
Esc with focus inside the toast.
*Precedent: Carbon.*

**20. It rises with a fade and leaves with a fade.**
In 200ms; no movement with reduced motion.
*The Foundation's motion.*

### Accessibility

**21. It never steals focus.**
It's announced, not focused.
*Precedent: Carbon.*

**22. An error interrupts, the rest waits.**
Error in `role="alert"`; Success, Info and Warning in `role="status"`.
*Precedent: Carbon.*

**23. The region exists before the message.**
A live region created together with the text isn't announced.

**24. The X is a real button.**
"Close notification", reachable with Tab.
*Precedent: Carbon.*

### Out of scope

**25. No action button.**
"Undo" and the like go in a Modal or on the screen itself.
*Precedents: Carbon, and Primer's critique.*

**26. No neutral status.**
Info covers it.

**27. No stack of toasts.**
One at a time.
