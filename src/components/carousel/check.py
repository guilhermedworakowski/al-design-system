"""
CSS gate for the Carousel.

The rule is the same for every component and lives in tools/cssgate.py: no
literal values (color, length, weight, duration), no orphan tokens and no
invented tokens. Only what is specific to the Carousel stays here.

Run: python3 check.py (or the full build: python3 build.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from cssgate import gate  # noqa: E402

# What this gate does NOT reach: markup only exists in the rendered output.
# a11y.py enforces these rules on the HTML the site emits.
OUTSIDE_CSS = [
    'a <section> with aria-roledescription="carousel" named by its visible title (rule 19)',
    'each slide role="group" + aria-roledescription="slide" + aria-label "n of total" (rule 19)',
    'arrows are native <button type="button"> named "Previous slide" / "Next slide" (rule 20)',
    'the dots wrapper is aria-hidden - no focus, no click (rule 22)',
    'one .al-carousel__live with aria-live="polite" (rule 21)',
]


if __name__ == '__main__':
    sys.exit(gate('carousel', outside_css=OUTSIDE_CSS))
