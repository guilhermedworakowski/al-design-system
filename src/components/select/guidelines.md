# Select · Usage guidelines

A select collects **one choice** from a list, inside a form.

- **Built on:** the native `<select>`
- **Size:** one size (48px)
- **States:** default, hover, active, focus, error, disabled, placeholder
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#select](https://al.guilhermedesignd.com/#select)

## Do and don't

| Do | Don't |
|---|---|
| A visible label, always: short, in sentence case, describing **the data**. "State", not "Select the state"; the instruction to choose is already in the placeholder. The "(Optional)" mark flags the minority: a field without it is required. | Using the placeholder as the label. It disappears the moment someone picks something, and whoever comes back to the form has lost the only clue to what the field asks for. Polaris requires the label even when it's visually hidden. |
| **No error:** the help text explains the field. | **With an error:** the error **replaces** the help text, and the help text comes back once it's fixed. That's why both texts must carry the same essential information. |

### AL marks the optional field, not the required one

It's the opposite school from Polaris's asterisk, and it wins when most fields in a form are required: you mark the minority. The consequence: **there is no "required" token or style**, because the absence of the mark is what required means, and an absence can't be tokenized.

## Rules

### When to use

**1. From 4 options up.**
With 3 or fewer, use radio buttons: the Select hides the options behind a click, and below 4 the cost of hiding them is higher than the cost of showing them.
*Precedents: Polaris sets 4+; Carbon says not to use a dropdown with two options.*

**2. Never for multiple choice.**
*Precedent: Carbon separates Select (single) from Dropdown and ComboBox.*

**3. Never to trigger an action.**
It collects data in a form. A menu that runs, filters or sorts something is another component.
*Precedent: Carbon, where the dropdown is for "taking an action, filtering, or sorting".*

**4. Above ~15 options, the native select gets in the way.**
It has no search. That's not a blocker, it's a known limit: this need opens a ComboBox, it doesn't stretch the Select.
*Precedent: Carbon keeps the ComboBox separate for this reason.*

### Label and the optional mark

**5. Every Select has a visible label above it. The placeholder is never the label.**
It disappears as soon as there's a value.
*Precedents: Polaris requires the label even when hidden; Material requires a label, placeholder or external label.*

**6. Short label, sentence case, no colon.**
*Precedent: Polaris.*

**7. The label describes the data, not the action.**
"State", not "Select the state": the instruction is already in the placeholder.

**8. AL marks the OPTIONAL field, not the required one.**
"(Optional)" next to the label, in `Body/sm` and `text-secondary`; a field without the mark is required. It wins when most fields are required: you mark the minority.
> **Conscious divergence:** it's the opposite school from Polaris's asterisk.

**9. There's no "required" token or mark.**
The absence of the mark IS required, and an absence can't be tokenized.

### Placeholder and default option

**10. If one option serves most people, it comes preselected, with no placeholder.**
A required placeholder forces everyone into a click most of them wouldn't need.
*Precedents: NN/g, repeated by Baymard.*

**11. With no good default, the placeholder describes what to choose.**
"Select the state", not "Select…".
*Precedents: NN/g, Baymard.*

**12. The placeholder is the first `<option>`, with `value=""`, `disabled` and `selected`.**
It isn't an attribute, because `<select>` has no native placeholder. It's also what triggers the text color change (`:has(option[value=""]:checked)`).

**13. Long instructions don't fit in the placeholder.**
That's help text, which stays visible after the choice.

**14. `optgroup` can be used, as the native element offers it.**
It groups for free, and there's nothing to draw on our side.

### Help text and error

**15. Help text and error share the SAME slot.**
On error the help text is replaced, and it comes back when the error is fixed. They're not two stacked lines.
*Precedent: Spectrum documents exactly this.*

**16. So both texts carry the same essential information.**
Otherwise people lose the instruction at the moment they need it most.
*Precedent: Spectrum.*

**17. The error says how to fix it.**
Not only that it failed. "Choose a state to continue", not "Invalid field".
*Precedent: Spectrum.*

**18. Help text is optional and starts off.**
Help text on every field becomes noise nobody reads.

### States

**19. Active is the instant; focus is the state that remains.**
Active lasts while the mouse button is pressed; focus holds while the field is focused, whether it arrived by Tab or by click. Chromium matches `:focus-visible` on a `<select>` clicked with the mouse, because the platform treats it as a control that takes keyboard input once it's open, so the ring shows on click. There's no "keyboard-only focus" selector other than `:focus-visible` itself, and forcing it with JavaScript would make the focus indicator conditional, the last thing that should be.
*Precedents: Carbon, Material and Polaris use this same reading.*

**20. Disabled only when the field can't be changed NOW because of another choice on the same screen.**
If it will never be usable, hide it instead of disabling it.

**21. Disabled sits below AA on purpose (1.59:1 to 3.64:1).**
WCAG 1.4.3 exempts inactive components, and raising this contrast makes a disabled field look clickable. Don't "fix" it.
*Precedent: WCAG 1.4.3.*

**22. The error shows up after submitting, or after the user leaves the field.**
Never while they're still choosing. Marking a field red before someone has finished filling it in accuses them of a mistake they haven't made.

### Accessibility

**23. It's the native `<select>`; don't rebuild it with a `div` and `role="listbox"`.**
The native element gives you keyboard, screen reader and mobile support for free.
*Precedent: the first rule of ARIA.*

**24. `<label for>` linked to the select's `id`.**
Don't use `aria-label` when there's a visible label: the announced name has to match the text people see.
*Precedents: MDN, Level Access.*

**25. Required uses the native `required` attribute.**
Not `aria-required`, which is meant for custom widgets.

**26. On error: `aria-invalid="true"` + `aria-describedby` pointing to the message's `id`.**
When it's fixed, go back to `false` and remove the `id`, or the state and the description contradict each other. With no error, `aria-describedby` points to the help text.

**27. Never use the Select without a visible label.**
The reason is specific to AL. The resting border measures 1.57:1, below the 3:1 of WCAG 1.4.11, and that only holds because the field can be identified in other ways: the label above and the text inside. Remove the label and the exception loses its ground. This is the usage rule that pays for that decision.
*Precedent: WCAG 1.4.11.*

## Out of scope, on purpose

| What | Why |
|---|---|
| Multiple choice, search and filter | They open a ComboBox; they don't stretch the Select. |
| One size only (48px) | A declared choice, like the `lg` that was left out of the Button. |
| Leading icon and read-only | They weren't designed. A field that must be read but not edited uses `disabled` today, with the known limitation that its value can't be copied. Spectrum solves it with read-only; AL doesn't have it yet. |
| The open list | It belongs to the browser. Don't style `<option>`, item height or scroll: it varies by operating system and breaks without warning. That's the agreed price of using the native element, and what buys keyboard and mobile support at no cost. |
