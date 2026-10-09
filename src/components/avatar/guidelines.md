# Avatar · Usage guidelines

An avatar shows **who**: the person behind a comment, a task or a conversation.

- **Types:** Photo, Initials, Icon
- **Sizes:** `sm`, `md`, `lg`
- **Live examples, playground and contrast report:** [al.guilhermedesignd.com/#avatar](https://al.guilhermedesignd.com/#avatar)

## Do and don't

| Do | Don't |
|---|---|
| **A person's identity:** say **who**: the author of a comment, the owner of a task, a participant in a conversation. | **Decoration next to anything:** an avatar with no person behind it is an icon with a round background. If there's no identity, the right component is the **Icon**. |
| **Photo because there is a photo.** And if it fails to load, it falls back on its own to **MS** (the initials), not to an empty box. | **Icon because it's more discreet:** choosing the type by visual taste throws away information that existed. |

### The chain decides, not you

The most important rule of the component, and the one that most often disappears in a rushed implementation: the avatar's type isn't a screen preference, it's the result of how much material exists about that person. Reverse the order and the interface shows a generic icon for someone who has a photo.

## Rules

### When to use each type

**1. Photo whenever a real photo exists.**
It's the most informative of the three options; no system promotes initials or an icon when there's a photo.
*Precedents: Polaris, Material.*

**2. Initials when there's no photo but the name is known.**
Never leave the avatar empty: initials keep the structure of the interface even without an image.
*Precedent: Material, literally "never leave the avatar blank".*

**3. Icon as the last resort: no photo and no name.**
Anonymous, guest, removed user, system placeholder.
*Precedent: Polaris uses this exact pattern.*

**4. The fallback chain is fixed: Photo → Initials → Icon, with no skipped steps.**
An image that fails or takes too long falls back to Initials; a missing name falls back to Icon. In code this is a swap of the child node, with the wrapper unchanged.
*Precedent: Polaris, where the URL falls back to initials if the image fails or is slow to load.*

### Hierarchy and combination

**5. One size per group.**
A list, table or stack uses a fixed size from start to end. The size describes the context, not the importance of each person.

**6. Stack (+N) and presence indicator are left out of this version.**
If the need comes, each one is a new composition **on top of** the Avatar (a ring in the canvas color for the stack, a badge for presence), never a variant of the component.
*Precedent: Primer, in AvatarStack.*

### Size

**7. Size comes from the role on screen, never from what looks better.**
- **`sm` (32px):** inline avatar: table, list, comment. *Polaris: small when the medium is too big or the avatar matters less.*
- **`md` (48px):** the default: user card, navigation item, comment header. *Polaris (default), Material (40–48 in cards).*
- **`lg` (64px):** emphasis: profile header, account screen. *Material (64–96 in headers); Primer closes its scale at 64.*

### Content (initials)

**8. At most 2 characters, always uppercase.**
First and last name, or the first two letters if there's only one name. Never lowercase, a lone number or an emoji. If the calculation produces more than two, cut to the two relevant ones; relying on the box clipping them isn't a content rule.

### Icon

**9. The Icon type's glyph is fixed to `user`.**
It isn't a free icon slot, unlike the Button and the Icon Button. The Avatar represents a single role, "a person with no information", and no precedent treats the glyph as a free choice. Its color follows `avatar-icon` (the same value as `avatar-label`), never a brand or status color.

### Problem states

**10. A broken image, invalid URL or slow load falls back to Initials or Icon, never to an empty box.**
It's a behavior rule for whoever implements the swap: Figma only models the three final types, and this rule is what ties them together in sequence. The `avatar-bg` background is the floor while the image loads, so there's never a hole in the interface.
*Precedents: Polaris, Material.*

**11. No loading state (skeleton or shimmer) in this version.**
A consequence of the Avatar being static. Asynchronous loading is new scope to audit, not something to improvise in code.

### Accessibility

**12. Decorative versus content.**
- **Name already written next to it:** decorative. `aria-hidden="true"` on the Photo, Icon and Initials. Repeating the name doubles what the screen reader announces. *PatternFly: an icon is decorative if it can be removed without affecting the page's information. Spectrum has an explicit `is-decorative`.*
- **Avatar alone, with no visible name:** it carries information. `role="img"` + `aria-label="<name>"` (Photo and Initials). *Carbon received an accessibility issue for an avatar without a text alternative.*
- **The Icon never carries an invented name:** decorative, or a generic label ("User without a photo").
- **It never enters the tab order**, with no `tabindex` and no button role of its own. A clickable avatar is wrapped in an actionable element that already has a focus ring (an Icon Button or a link). Without this rule written down, someone puts the avatar inside a `button` and the ring simply doesn't exist.

## Out of scope, on purpose

| What | Why |
|---|---|
| Square shape | AL has no concept of organization anywhere, and creating the shape before the concept invents a state nothing uses. **Conscious divergence from Primer**, where a circle is a person and a square is an organization, team or bot. |
| Stack (+N) | A composition on top of the Avatar, not a variant of it. It needs a ring in the canvas color to separate neighboring avatars: one more token, when the time comes. |
| Presence indicator | The online/offline dot is an overlaid badge, and a positioned badge is another component. |
| Background color per person | Many systems derive a color from the name. Here there's one background only: a color derived from a string escapes the contrast gate by definition. |
| Interactive avatar | No hover, no focus, no disabled. An avatar is content; content doesn't get disabled. The same decision as the Tag. |
