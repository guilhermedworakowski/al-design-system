from color import *
from palette import SEM, PAIRS, EXCEPTIONS, HARD_FLOOR
import json, os, sys

# Path anchored on the file itself, never on the folder it runs from:
# tokens.json is the single source of truth the components read, and it lives
# in build/ (see tools/paths.py). Before this, the destination depended on the
# cwd, and running from inside foundation/ created a second copy the gates read
# without anyone noticing.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
from paths import ROOT, TOKENS_JSON, out  # noqa: E402
TOKENS_PATH = out(TOKENS_JSON)

P = build()
SHADOW_RGB = "24, 24, 24"   # achromatic neutral-950 -> gray shadow, no hue tint

TOKENS = {
  "meta": {
    # Third digit = release. An update to the foundation or to an existing
    # component goes here; the middle digit is for a new layer. 0.3.1: the
    # Button moved the icon up to the label's line height (0.1.1 -> 0.2.0).
    # 0.4.0: the Icon Button came in whole - a new component and a new layer,
    # so the middle digit. It brought its own Figma collection, 42 tokens, CSS,
    # two gates and a page on the site.
    # 0.5.0: the Tag - the first AL component to close with zero exceptions
    # while carrying text (4.5:1 floor, not the Icon Button's 3:1).
    # 0.6.0: the Avatar - a new component, middle digit. It closes Tier 1. It
    # creates no new contrast pair (zero exceptions), and it is the smallest
    # a11y gate in the system so far: the background never varies by type,
    # only by theme.
    # 0.10.0: the Switch - a new component, middle digit. The first component
    # to create a semantic in the Foundation (bg-thumb, bg-thumb-disabled), and
    # the first the site itself consumes: the theme switch in the rail.
    # 0.11.0: the Input - a new component, middle digit. The first with
    # read-only (which is NOT exempt from contrast like disabled) and with
    # affixes inside the border: the box is a wrapper, and the state reaches it
    # through :has().
    # 0.11.1: package.json - distribution; no token changes.
    # 0.13.0: the Password - a new component, middle digit. The first component
    # with its own JavaScript (password.js), which now ships in the package.
    # 0.14.0: the Divider - a new component, middle digit. The first of Tier 3
    # (structure); no Foundation token changes.
    # 0.15.0: the Card - a new component, middle digit. Second of Tier 3; no
    # Foundation token changes.
    # 0.16.0: the Tab - a new component, middle digit. Third of Tier 3 and the
    # first with its own script (tab.js); no Foundation token changes.
    # 0.17.0: the Accordion - a new component, middle digit. Fourth of Tier 3,
    # native <details>/<summary>, no script. The Foundation gains two
    # semantics, bg-hover-raised and bg-active-raised: in dark, bg-hover was the
    # same color as the raised surface and the hover disappeared.
    # 0.17.1: Motion - a Foundation update, third digit. Four tokens
    # (duration-panel/popup, easing-enter/exit) for what enters and leaves the
    # screen; no component consumes them yet, and the literal 120ms remain.
    # 0.17.2: Motion complete - a Foundation update, third digit. Four more
    # tokens (duration-feedback, duration-spinner, duration-spinner-reduced,
    # easing-spinner) and the 12 components with transitions now consume
    # motion: no literal duration or curve. The rendered value is the same,
    # except the controls' curve, which is now ease-out on enter and ease-in on
    # exit.
    # 0.18.0: Modal, fifth component of Tier 3 - middle digit, new component.
    # The Foundation gains bg-scrim, the first semantic with transparency
    # (#RRGGBBAA): the dimmed background behind a modal layer. Out of PAIRS,
    # because its contrast only exists composited over the page; the Modal's
    # gate measures it. No existing token value changes.
    # 0.18.1: a Modal fix, third digit. In dark the Modal background
    # (surface-raised) was the same as bg-hover, and the ghost and secondary
    # hover disappeared in the footer. modal.css now uses bg-hover-raised and
    # bg-active-raised on those buttons. No new token.
    # 0.18.2: a Card and Modal fix, third digit. Ghost and Secondary buttons
    # (Button and Icon Button) inside the Card, and an Icon Button anywhere in
    # the Modal, use bg-hover-raised and bg-active-raised: the background is
    # surface-raised and, in dark, the same as bg-hover. No new token.
    # 0.19.0: Drawer, sixth and last component of Tier 3 - middle digit, new
    # component. A native <dialog> docked on the right, with its own drawer.js
    # (open by attribute, backdrop click only without fields, initial focus).
    # Reuses bg-scrim and motion.duration.panel; no Foundation token changes.
    # 0.20.0: Sidebar, first component of Tier 4 - middle digit, new
    # component. An <aside> with a <nav> inside, items = Tab Square; below
    # 1024px sidebar.js moves the same <aside> into a <dialog> from the left.
    # Reuses bg-scrim, elevation-5 and motion.duration.panel; no Foundation
    # token changes.
    # From 1.0.0 on, the history of every release lives in CHANGELOG.md.
    "name": "AL Design System", "version": "1.0.1", "license": "MIT",
    "brandAnchor": "#FC5000", "colorSpace": "OKLCH", "wcag": "2.1 AA",
    "lLadder": L_LADDER, "neutralHue": NEUTRAL_HUE,
  },
  "color": {"primitive": P, "semantic": SEM, "brandHover": BRAND_HOVER},
  "type": {
    "family": {
      "sans": "'InterVariable', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      "mono": "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace",
    },
    "weight": {"regular": 400, "medium": 500, "semibold": 600, "bold": 700},
    "size":  {"xs":12,"sm":14,"md":16,"lg":18,"xl":20,"2xl":24,"3xl":30,"4xl":36,"5xl":48,"6xl":60},
    "leading": {"xs":16,"sm":20,"md":24,"lg":28,"xl":28,"2xl":32,"3xl":36,"4xl":44,"5xl":56,"6xl":68},
    "tracking": {"xs":"0.01em","sm":"0em","md":"0em","lg":"0em","xl":"-0.01em","2xl":"-0.01em",
                 "3xl":"-0.015em","4xl":"-0.02em","5xl":"-0.02em","6xl":"-0.025em"},
    "styles": [
      # name,          size, leading, weight, tracking,   use
      ("display-2xl",   60, 68, 700, "-0.025em", "hero / highlight number"),
      ("display-xl",    48, 56, 700, "-0.02em",  "marketing page title"),
      ("heading-lg",    36, 44, 600, "-0.02em",  "product H1"),
      ("heading-md",    30, 36, 600, "-0.015em", "H2"),
      ("heading-sm",    24, 32, 600, "-0.01em",  "H3 / card title"),
      ("heading-xs",    20, 28, 600, "-0.01em",  "H4 / section title"),
      ("body-lg",       18, 28, 400, "0em",      "lead / intro"),
      ("body-md",       16, 24, 400, "0em",      "the system's default body"),
      ("body-sm",       14, 20, 400, "0em",      "supporting text / table"),
      ("label-lg",      16, 24, 500, "0em",      "large button label"),
      ("label-md",      14, 20, 500, "0em",      "field / button label"),
      ("label-sm",      12, 16, 500, "0.01em",   "badge / tag / overline"),
      ("caption",       12, 16, 400, "0.01em",   "caption / helper text"),
      ("code-md",       14, 20, 400, "0em",      "inline and block code"),
    ],
  },
  "space": {str(v): v for v in [0,2,4,8,12,16,20,24,32,40,48,64,80,96]},
  "radius": {"none":0,"xs":2,"sm":4,"md":6,"lg":8,"xl":12,"2xl":16,"3xl":24,"full":9999},
  # Icon size scale. The steps are named by their own value, like spacing -
  # on purpose: t-shirt names (sm/md/lg) force a rename when a step comes in
  # between, and this is the scale that grows the most. This way a new step
  # costs one line and nothing existing changes name.
  #
  # The scale does NOT lock the Icon component. The drawing is 24 with the
  # stroke outlined into a fill, so the instance works at any size. This names
  # the recurring sizes so the decision is made once and can change in one
  # place - and so the literal CSS gate has something to validate against.
  "iconSize": {"16":16, "20":20, "24":24, "32":32},
  "border": {"width": {"0":0,"1":1,"2":2,"focus":2}, "focusOffset": 2},
  # Motion. Two axes, and the second is the consumer's choice:
  #   easing   -> the TYPE OF ACTION (enter or exit). Enter decelerates
  #               (ease-out): the element arrives and settles. Exit accelerates
  #               (ease-in): the element leaves and disappears.
  #   duration -> the SIZE of what moves, not the component's name. A
  #               component name would force a new token for every new
  #               component; size doesn't. `panel` covers what takes over the
  #               screen (Modal, Drawer), `popup` what appears small on top of
  #               it (Tooltip, Toast).
  #   `feedback` is the third step and it is about ROLE, not size: it is the
  #               control's response to the pointer, focus and selection. It
  #               came in on 2026-10-08 to absorb the 120ms that 12 components
  #               wrote by hand. It uses the same enter/exit pair as the
  #               overlays: entering a state (hover, focus, checked) is
  #               ease-out, leaving is ease-in.
  #   `spinner` and `spinner-reduced` are LOOP durations (one turn), with the
  #               `easing-spinner` curve (linear, written as 0,0,1,1 - the same
  #               motion). They came in on 2026-10-08 to remove the literal
  #               700ms/2400ms from the Button and the Icon Button.
  # Enter and exit have the same duration by design (2026-10-08); if they ever
  # diverge, the new token is `duration-panel-exit`, with no rename.
  # The curves are the CSS keywords written out in full: Figma, the JS and the
  # site's chart need the four numbers, not the nickname.
  "motion": {
    "duration": {"feedback": 120, "popup": 200, "panel": 300, "spinner": 700, "spinner-reduced": 2400},
    "easing": {"enter": [0, 0, 0.58, 1], "exit": [0.42, 0, 1, 1], "spinner": [0, 0, 1, 1]},
    "usage": {
      "duration-feedback": "Hover, pressed, focus and selection on every control (Button, Input, Switch, Tab...). Entering the state uses easing-enter, leaving uses easing-exit.",
      "duration-spinner": "One turn of the spinner (Button, Icon Button). A continuous loop: neither enter nor exit.",
      "duration-spinner-reduced": "One turn of the spinner under prefers-reduced-motion. The spinner doesn't stop, because it is the only clue that something is happening; it only slows down.",
      "duration-panel": "Modal and Drawer: what covers the screen or comes in from one of its edges. Enter and exit.",
      "duration-popup": "Tooltip and Toast: what appears small on top of the screen. Enter and exit.",
      "easing-enter": "Everything that enters (ease-out): arrives fast and settles slowly.",
      "easing-exit": "Everything that exits (ease-in): leaves slowly and speeds up until it disappears.",
      "easing-spinner": "A continuous loop (linear): constant speed, no acceleration or braking. Spinner and, in the future, skeleton.",
    },
    "_note": "Under prefers-reduced-motion the component removes the transition (transition: none). "
             "There is no zero-duration token: the absence of motion is not a scale value.",
  },
  "focusRing": {
    # Two layers in the same shadow, no offset:
    #   inner  -> spread 2, in the background color. It is the gap. It keeps
    #             the ring from touching the component's fill.
    #   outer  -> spread 4 (2 for the gap + 2 for the ring), in the focus color.
    # This way the ring only has to contrast with the screen background - and
    # the button's fill, orange or red, stops being a problem.
    "default": {
      "light": f"0 0 0 2px {SEM['bg-canvas'][0]}, 0 0 0 4px {SEM['shadow-focus-default'][0]}",
      "dark":  f"0 0 0 2px {SEM['bg-canvas'][1]}, 0 0 0 4px {SEM['shadow-focus-default'][1]}",
    },
    "error": {
      "light": f"0 0 0 2px {SEM['bg-canvas'][0]}, 0 0 0 4px {SEM['shadow-focus-error'][0]}",
      "dark":  f"0 0 0 2px {SEM['bg-canvas'][1]}, 0 0 0 4px {SEM['shadow-focus-error'][1]}",
    },
    "_note": "It is not elevation. Elevation communicates height; this communicates keyboard "
             "focus and goes through the contrast gate. It never disappears, never animates.",
  },
  "elevation": {
    "0":  {"light":"none", "dark":"none"},
    "1":  {"light":f"0 1px 2px 0 rgba({SHADOW_RGB},0.06), 0 1px 3px 0 rgba({SHADOW_RGB},0.10)",
           "dark": f"0 1px 2px 0 rgba(0,0,0,0.30), 0 1px 3px 0 rgba(0,0,0,0.40)"},
    "2":  {"light":f"0 2px 4px -1px rgba({SHADOW_RGB},0.06), 0 4px 8px -2px rgba({SHADOW_RGB},0.10)",
           "dark": f"0 2px 4px -1px rgba(0,0,0,0.32), 0 4px 8px -2px rgba(0,0,0,0.44)"},
    "3":  {"light":f"0 4px 8px -2px rgba({SHADOW_RGB},0.06), 0 8px 16px -4px rgba({SHADOW_RGB},0.12)",
           "dark": f"0 4px 8px -2px rgba(0,0,0,0.34), 0 8px 16px -4px rgba(0,0,0,0.48)"},
    "4":  {"light":f"0 8px 16px -4px rgba({SHADOW_RGB},0.08), 0 16px 32px -8px rgba({SHADOW_RGB},0.14)",
           "dark": f"0 8px 16px -4px rgba(0,0,0,0.36), 0 16px 32px -8px rgba(0,0,0,0.52)"},
    "5":  {"light":f"0 16px 32px -8px rgba({SHADOW_RGB},0.10), 0 32px 64px -16px rgba({SHADOW_RGB},0.18)",
           "dark": f"0 16px 32px -8px rgba(0,0,0,0.40), 0 32px 64px -16px rgba(0,0,0,0.56)"},
    "_note": "In dark the shadow is a secondary cue: the primary cue is the surface getting lighter (950 -> 900 -> 800).",
  },
}

# embedded contrast report (the gate becomes data, not just a log)
report = []
for i, theme in enumerate(('light','dark')):
    for fg, bg, mn, label in PAIRS:
        a, b = SEM[fg][i], SEM[bg][i]
        exc = (theme, fg, bg) in EXCEPTIONS
        floor = HARD_FLOOR if exc else mn
        report.append({"theme":theme,"label":label,"fg":fg,"bg":bg,
                       "fgHex":a,"bgHex":b,"ratio":round(cr(a,b),2),"min":floor,
                       "pass":cr(a,b)>=floor,"exception":exc})

fails = [r for r in report if not r["pass"]]
if fails:
    raise SystemExit(f"{len(fails)} pair(s) fail the contrast gate - export aborted: {fails}")

TOKENS["contrastReport"] = report

json.dump(TOKENS, open(TOKENS_PATH,'w'), indent=2, ensure_ascii=False)

# The version has a single source: meta.version, above. package.json repeats
# the number for npm, and this script rewrites it - never by hand. It comes
# after the contrast gate: an aborted export doesn't bump the package version.
PACKAGE_PATH = os.path.join(ROOT, 'package.json')
pkg = json.load(open(PACKAGE_PATH, encoding='utf-8'))
pkg['version'] = TOKENS['meta']['version']
with open(PACKAGE_PATH, 'w', encoding='utf-8') as f:
    json.dump(pkg, f, indent=2, ensure_ascii=False)
    f.write('\n')
n_prim = sum(len(v) for v in P.values()) + 1
print(f"build/tokens.json written")
print(f"package.json at version {pkg['version']}")
print(f"  color primitives  : {n_prim}  ({len(P)} families x 11 steps + orange-550)")
print(f"  color semantics   : {len(SEM)} x 2 themes = {len(SEM)*2}")
print(f"  text styles       : {len(TOKENS['type']['styles'])}")
print(f"  spacing           : {len(TOKENS['space'])}   radius: {len(TOKENS['radius'])}   icon-size: {len(TOKENS['iconSize'])}   elevation: 6")
n_exc = sum(1 for r in report if r['exception'])
print(f"  validated pairs   : {len(report)}  |  full AA: {len(report)-n_exc}  |  brand exceptions: {n_exc}  |  fail: {sum(1 for r in report if not r['pass'])}")
TOKENS['meta']['brandLabel'] = 'light'
TOKENS['meta']['exceptions'] = [{'theme':r['theme'],'label':r['label'],'ratio':r['ratio']} for r in report if r['exception']]
total = n_prim + len(SEM)*2 + len(TOKENS['type']['styles']) + len(TOKENS['space']) + len(TOKENS['radius']) + len(TOKENS['iconSize']) + 6 + 4
print(f"  TOTAL             : ~{total} tokens")
