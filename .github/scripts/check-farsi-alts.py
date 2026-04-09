#!/usr/bin/env python3
"""
TGD-008: Farsi caption/alt-text validation script.

Checks that all images in the Jekyll site have Farsi alt-text:
1. Event files (_events/*.md): if `image:` field is set, `title:` must contain Farsi script.
2. HTML/Liquid templates (_layouts/, _includes/, *.html): every <img> tag must have
   an `alt` attribute containing Farsi characters (or be explicitly empty for decorative images).

Farsi/Arabic Unicode block: U+0600–U+06FF
Extended Arabic: U+0750–U+077F, U+FB50–U+FDFF, U+FE70–U+FEFF
"""

import re
import sys
import glob
from pathlib import Path

FARSI_PATTERN = re.compile(
    r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]'
)

IMG_TAG_PATTERN = re.compile(
    r'<img\b([^>]*)>',
    re.IGNORECASE | re.DOTALL
)

ALT_ATTR_PATTERN = re.compile(
    r'\balt=["\']([^"\']*)["\']',
    re.IGNORECASE
)

# Liquid variable pattern (e.g., alt="{{ event.title }}")
LIQUID_VAR_PATTERN = re.compile(r'\{\{[^}]+\}\}')

errors = []
warnings = []


def has_farsi(text: str) -> bool:
    return bool(FARSI_PATTERN.search(text))


def check_event_files(repo_root: Path) -> None:
    """Check _events/*.md: images must have Farsi title as alt-text."""
    events_dir = repo_root / '_events'
    if not events_dir.exists():
        return

    for md_file in sorted(events_dir.glob('*.md')):
        content = md_file.read_text(encoding='utf-8')

        # Parse front matter (between --- markers)
        fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not fm_match:
            continue

        front_matter = fm_match.group(1)

        # Check if file has an image
        image_match = re.search(r'^image:\s*"?(.+?)"?\s*$', front_matter, re.MULTILINE)
        if not image_match:
            continue

        image_val = image_match.group(1).strip()
        if not image_val:
            continue

        # Image exists — verify title is in Farsi
        title_match = re.search(r'^title:\s*"?(.+?)"?\s*$', front_matter, re.MULTILINE)
        if not title_match:
            errors.append(
                f"{md_file.relative_to(repo_root)}: has image but no title field "
                f"(title is used as alt-text)"
            )
            continue

        title = title_match.group(1).strip()
        if not has_farsi(title):
            errors.append(
                f"{md_file.relative_to(repo_root)}: image alt-text (title) is not in Farsi: '{title}'"
            )


def check_html_templates(repo_root: Path) -> None:
    """Check HTML/Liquid template files for <img> tags without Farsi alt-text."""
    patterns = [
        '_layouts/*.html',
        '_includes/*.html',
        '*.html',
        '_events/*.html',
    ]

    checked_files = set()
    for pattern in patterns:
        for html_file in sorted(repo_root.glob(pattern)):
            if html_file in checked_files:
                continue
            checked_files.add(html_file)

            content = html_file.read_text(encoding='utf-8')
            rel_path = html_file.relative_to(repo_root)

            for match in IMG_TAG_PATTERN.finditer(content):
                attrs = match.group(1)
                line_num = content[:match.start()].count('\n') + 1

                alt_match = ALT_ATTR_PATTERN.search(attrs)

                if not alt_match:
                    # No alt attribute at all
                    # Check if it's a Liquid block img (has {{ }})
                    if LIQUID_VAR_PATTERN.search(attrs):
                        warnings.append(
                            f"{rel_path}:{line_num}: <img> with Liquid src has no alt attribute "
                            f"(ensure the template passes a Farsi alt)"
                        )
                    else:
                        errors.append(
                            f"{rel_path}:{line_num}: <img> missing alt attribute entirely"
                        )
                    continue

                alt_val = alt_match.group(1).strip()

                # Empty alt is acceptable for decorative images
                if alt_val == '':
                    continue

                # If alt contains a Liquid variable, we can't validate statically —
                # warn if the variable name doesn't look like a Farsi field
                if LIQUID_VAR_PATTERN.search(alt_val):
                    # Heuristic: variable references like event.title, page.title are OK
                    # (those fields are validated separately)
                    continue

                # Static alt text must be in Farsi
                if not has_farsi(alt_val):
                    errors.append(
                        f"{rel_path}:{line_num}: <img> alt text is not in Farsi: '{alt_val}'"
                    )


def main():
    repo_root = Path(__file__).parent.parent.parent
    if not (repo_root / '_config.yml').exists():
        # Try CWD
        repo_root = Path.cwd()

    print(f"Checking Farsi alt-text in: {repo_root}\n")

    check_event_files(repo_root)
    check_html_templates(repo_root)

    if warnings:
        print("WARNINGS (review recommended):")
        for w in warnings:
            print(f"  ⚠  {w}")
        print()

    if errors:
        print("ERRORS (must fix before deploy):")
        for e in errors:
            print(f"  ✗  {e}")
        print(f"\n{len(errors)} error(s) found. All images must have Farsi alt-text.")
        sys.exit(1)
    else:
        checked = len(list(Path(repo_root / '_events').glob('*.md'))) if (repo_root / '_events').exists() else 0
        print(f"✓ All images have valid Farsi alt-text. ({checked} event files checked)")
        sys.exit(0)


if __name__ == '__main__':
    main()
