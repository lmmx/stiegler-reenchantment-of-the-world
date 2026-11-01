#!/usr/bin/env python3
"""Check the documentation site's sources and its built output.

    uv run --no-project -p 3.13 --with pyyaml python website/check_site.py [--site DIR]

- Every Markdown page of the companion (the repository's .md files, less those zensical.toml
  excludes) is in the nav of zensical.toml, and every nav entry exists.
- No page links to an excluded page by a relative path: such links go to GitHub instead.
- Every internal link, image, stylesheet and social card (og:image) in the built site
  (default: site/) resolves to a file of the build, with its #anchor present, as served under the base path of site_url
  (/stiegler-reenchantment-of-the-world/ on GitHub Pages).
- Every nav page has a front-matter description (the home page, README.md, takes the
  site_description), and is listed once in the llmstxt sections of zensical.toml with that
  same description; the built site has llms.txt, llms-full.txt and the page's Markdown copy,
  and no Markdown copy of any other page.

Adapted from lmmx/mibz2's docs/scripts/check_site.py. Exits with 1 and lists every problem.
"""

import argparse
import fnmatch
import re
import sys
import tomllib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
HOME = "README.md"


def nav_pages(nav):
    """Yield every page path in a zensical nav, at any depth."""
    for entry in nav:
        if isinstance(entry, str):
            yield entry
        elif isinstance(entry, dict):
            for value in entry.values():
                yield from nav_pages([value] if isinstance(value, str) else value)


def excluded(config, rel):
    """Whether zensical.toml's exclude_docs (gitignore-style, simplified) leaves out rel."""
    for pattern in config["project"].get("exclude_docs", "").split():
        anchored = pattern.startswith("/")
        pattern = pattern.strip("/")
        if pattern.endswith("*") or "*" in pattern:
            if fnmatch.fnmatch(rel, pattern) or (not anchored and fnmatch.fnmatch(Path(rel).name, pattern)):
                return True
        elif rel == pattern or rel.startswith(pattern + "/") or (not anchored and Path(rel).name == pattern):
            return True
    return False


def doc_pages(config):
    """The companion's pages: every .md under docs_dir that is not excluded or hidden."""
    docs = ROOT / config["project"]["docs_dir"]
    pages = set()
    for p in docs.rglob("*.md"):
        rel = p.relative_to(docs).as_posix()
        if any(part.startswith(".") for part in Path(rel).parts) or excluded(config, rel):
            continue
        pages.add(rel)
    return pages


def front_matter(text):
    """A page's YAML front matter, or {}."""
    if not text.startswith("---\n"):
        return {}
    return yaml.safe_load(text[4 : text.index("\n---\n", 4)]) or {}


class Links(HTMLParser):
    """Collect an HTML page's link targets and its element ids."""

    def __init__(self):
        super().__init__()
        self.links, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        """Record the tag's id or anchor name, and its href or src."""
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("name"):
            self.ids.add(attrs["name"])
        if tag == "meta" and attrs.get("property") == "og:image" and attrs.get("content"):
            self.links.append(attrs["content"])  # the page's social card
        for key in ("href", "src"):
            value = attrs.get(key)
            if value and not (tag == "link" and attrs.get("rel") in ("preconnect", "dns-prefetch")):
                self.links.append(value)


def check_nav(config, problems):
    """Every page is in the nav, and every nav entry exists."""
    pages = doc_pages(config)
    listed = set(nav_pages(config["project"]["nav"]))
    for page in sorted(pages - listed):
        problems.append(f"not in the nav: {page}")
    for page in sorted(listed - pages):
        problems.append(f"in the nav but missing or excluded: {page}")


def check_excluded_links(config, problems):
    """No page links by a relative path to a Markdown file the site leaves out."""
    docs = ROOT / config["project"]["docs_dir"]
    for page in sorted(doc_pages(config)):
        for target in re.findall(r"\]\(([^)\s#]+\.md)(?:#[^)]*)?\)", (docs / page).read_text()):
            if urlparse(target).scheme:
                continue
            rel = (Path(page).parent / target).as_posix()
            rel = Path(*[p for p in Path(rel).parts]).as_posix()
            parts = []
            for part in rel.split("/"):
                if part == "..":
                    parts.pop() if parts else None
                elif part != ".":
                    parts.append(part)
            rel = "/".join(parts)
            if excluded(config, rel):
                problems.append(f"{page}: links to {target}, which the site leaves out (link to GitHub)")


def check_links(config, site, problems):
    """Every internal link of the built site resolves, with its anchor."""
    base = urlparse(config["project"]["site_url"]).path
    parsed = {}
    for html in site.rglob("*.html"):
        p = Links()
        p.feed(html.read_text(errors="replace"))
        parsed[html] = p

    def target(url_path):
        if not url_path.startswith(base):
            return None
        path = site / unquote(url_path[len(base) :])
        if url_path.endswith("/") or path.is_dir():
            path = path / "index.html"
        return path

    checked = 0
    for html, p in sorted(parsed.items()):
        page_url = base + html.relative_to(site).as_posix()
        if page_url.endswith("index.html"):
            page_url = page_url[: -len("index.html")]
        for link in p.links:
            parts = urlparse(link)
            if parts.scheme and parts.netloc and not link.startswith(config["project"]["site_url"]):
                continue  # external
            if link.startswith(("mailto:", "javascript:", "data:")):
                continue
            url = urlparse(urljoin("https://host" + page_url, link))
            path = target(url.path)
            checked += 1
            where = html.relative_to(site).as_posix()
            if path is None:
                problems.append(f"{where}: {link} leaves the base path {base}")
            elif not path.exists():
                problems.append(f"{where}: {link} -> missing {path.relative_to(site)}")
            elif url.fragment and path.suffix == ".html":
                ids = parsed[path].ids if path in parsed else set()
                if url.fragment not in ids:
                    problems.append(f"{where}: {link} -> no #{url.fragment}")
    return checked


def md_copy(site, page):
    """Where the llmstxt plugin writes the Markdown copy of a page."""
    stem = page.removesuffix(".md")
    if stem == "README" or stem.endswith("/README") or stem == "index" or stem.endswith("/index"):
        return site / (stem.rsplit("/", 1)[0] + "/index.md" if "/" in stem else "index.md")
    return site / stem / "index.md"


def check_llms(config, site, problems):
    """Every nav page has a description, listed once in llmstxt, and the built llms files."""
    docs = ROOT / config["project"]["docs_dir"]
    sections = config["project"]["plugins"]["llmstxt"]["sections"]
    listed = [entry for entries in sections.values() for item in entries for entry in item.items()]
    paths = [path for path, _ in listed]
    for page in sorted({p for p in paths if paths.count(p) > 1}):
        problems.append(f"listed more than once in the llmstxt sections: {page}")
    for page in nav_pages(config["project"]["nav"]):
        if page == HOME:
            description = config["project"]["site_description"]
        else:
            text = (docs / page).read_text() if (docs / page).exists() else ""
            description = front_matter(text).get("description")
            if not description:
                problems.append(f"no front-matter description: {page}")
        if page not in paths:
            problems.append(f"not in the llmstxt sections of zensical.toml: {page}")
        elif description and dict(listed)[page] != description:
            problems.append(f"llmstxt description differs from the front matter: {page}")
    if (site / "index.html").exists():
        for name in ("llms.txt", "llms-full.txt"):
            if not (site / name).exists():
                problems.append(f"no {name} in the built site")
        for page in paths:
            md = md_copy(site, page)
            if not md.exists():
                problems.append(f"no Markdown copy of {page} at {md.relative_to(site)}")
        expected = {md_copy(site, page) for page in paths}
        for md in sorted(set(site.rglob("*.md")) - expected):
            problems.append(f"Markdown copy of a page not in the llmstxt sections: {md.relative_to(site)}")


def main():
    """Run every check and exit non-zero listing the problems found."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default=str(ROOT / "site"))
    args = parser.parse_args()
    config = tomllib.loads((ROOT / "zensical.toml").read_text())
    problems = []
    check_nav(config, problems)
    check_excluded_links(config, problems)
    site = Path(args.site)
    if (site / "index.html").exists():
        checked = check_links(config, site, problems)
        print(f"{checked} internal links checked", file=sys.stderr)
    else:
        problems.append(f"no built site at {site} (zensical build)")
    check_llms(config, site, problems)
    for problem in problems:
        print(problem)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
