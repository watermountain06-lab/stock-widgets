#!/usr/bin/env python3
"""Regenerate index.html from templates/index.template.html + data/manifest.json
+ data/macro.json.

The JSON is inlined directly into index.html (not fetched at runtime) so the
page also works opened straight from the filesystem (file://) without a
local server, and to sidestep CORS on a bare fetch().

Usage: python3 build_index.py [repo_dir]
"""
import json
import os
import re
import sys

STOCKS_PLACEHOLDER = re.compile(
    r"/\*STOCKS_JSON_START\*/.*?/\*STOCKS_JSON_END\*/", re.DOTALL
)
MACRO_PLACEHOLDER = re.compile(
    r"/\*MACRO_JSON_START\*/.*?/\*MACRO_JSON_END\*/", re.DOTALL
)


def build(repo_dir):
    template_path = os.path.join(repo_dir, "templates", "index.template.html")
    manifest_path = os.path.join(repo_dir, "data", "manifest.json")
    macro_path = os.path.join(repo_dir, "data", "macro.json")
    out_path = os.path.join(repo_dir, "index.html")

    with open(template_path) as f:
        template = f.read()
    with open(manifest_path) as f:
        manifest = json.load(f)

    manifest_sorted = sorted(manifest, key=lambda s: s["rank"])
    stocks_blob = json.dumps(manifest_sorted, ensure_ascii=False, indent=2)
    stocks_replacement = f"/*STOCKS_JSON_START*/{stocks_blob}/*STOCKS_JSON_END*/"

    if not STOCKS_PLACEHOLDER.search(template):
        print("error: STOCKS_JSON placeholder not found in template", file=sys.stderr)
        sys.exit(1)

    out = STOCKS_PLACEHOLDER.sub(lambda _: stocks_replacement, template, count=1)

    if os.path.exists(macro_path):
        with open(macro_path) as f:
            macro = json.load(f)
        macro_blob = json.dumps(macro, ensure_ascii=False, indent=2)
        macro_replacement = f"/*MACRO_JSON_START*/{macro_blob}/*MACRO_JSON_END*/"
        if MACRO_PLACEHOLDER.search(out):
            out = MACRO_PLACEHOLDER.sub(lambda _: macro_replacement, out, count=1)

    with open(out_path, "w") as f:
        f.write(out)
    print(f"Wrote {out_path} ({len(manifest_sorted)} stocks)")


if __name__ == "__main__":
    repo_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    build(repo_dir)
