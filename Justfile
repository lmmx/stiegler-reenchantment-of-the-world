# The docs toolchain, pinned as in .github/workflows/site.yml (change both together).
docs_with := "--with zensical==0.0.71"
cards_with := "--with playwright==1.48.0 --with pyyaml"

# Build the site, serve it and rebuild on change
docs-serve:
   uv run --no-project -p 3.13 {{docs_with}} zensical serve

# A clean, strict build into site/
docs-build:
   uv run --no-project -p 3.13 {{docs_with}} zensical build --clean --strict

# Each page's social card, into the built site (Chromium: playwright install chromium)
docs-cards: docs-build
   uv run --no-project -p 3.13 {{cards_with}} python website/social_cards.py

# The build and its cards, then the nav, link, card and llms.txt checks
docs-check: docs-cards
   uv run --no-project -p 3.13 --with pyyaml python website/check_site.py
