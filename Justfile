# The docs toolchain, pinned as in .github/workflows/site.yml (change both together).
docs_with := "--with zensical==0.0.71"

# Build the site, serve it and rebuild on change
docs-serve:
   uv run --no-project -p 3.13 {{docs_with}} zensical serve

# A clean, strict build into site/
docs-build:
   uv run --no-project -p 3.13 {{docs_with}} zensical build --clean --strict

# The build, then the nav, link and llms.txt checks
docs-check: docs-build
   uv run --no-project -p 3.13 --with pyyaml python website/check_site.py
