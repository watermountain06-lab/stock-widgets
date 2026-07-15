#!/usr/bin/env python3
"""Wrap a design-token-dependent HTML fragment (a Claude-artifact-style
widget body that uses var(--color-background-primary) etc. but has no
:root block defining those tokens) into a standalone, self-contained page.

Without this wrapper the fragment renders with transparent card
backgrounds and 0px border-radius, because the custom properties it
references are undefined - confirmed by inspecting computed styles in a
browser (card background fell back to rgba(0,0,0,0)).

The token block below is copied from the Anthropic-artifact default
design system (light-dark() adaptive: works in both light/dark browser
themes), matching the token names these fragments actually use.

Usage: python3 wrap_fragment.py FRAGMENT.html --title "TICKER 종합 분석" --out OUT.html
"""
import argparse

TOKENS_CSS = """
:root {
    --color-background-primary: light-dark(rgba(255, 255, 255, 1), rgba(48, 48, 46, 1));
    --color-background-secondary: light-dark(rgba(245, 244, 237, 1), rgba(38, 38, 36, 1));
    --color-background-tertiary: light-dark(rgba(250, 249, 245, 1), rgba(20, 20, 19, 1));
    --color-background-inverse: light-dark(rgba(20, 20, 19, 1), rgba(250, 249, 245, 1));
    --color-background-ghost: light-dark(rgba(255, 255, 255, 0), rgba(48, 48, 46, 0));
    --color-background-info: light-dark(rgba(214, 228, 246, 1), rgba(37, 62, 95, 1));
    --color-background-danger: light-dark(rgba(247, 236, 236, 1), rgba(96, 42, 40, 1));
    --color-background-success: light-dark(rgba(233, 241, 220, 1), rgba(27, 70, 20, 1));
    --color-background-warning: light-dark(rgba(246, 238, 223, 1), rgba(72, 58, 15, 1));
    --color-background-disabled: light-dark(rgba(255, 255, 255, 0.5), rgba(48, 48, 46, 0.5));
    --color-text-primary: light-dark(rgba(20, 20, 19, 1), rgba(250, 249, 245, 1));
    --color-text-secondary: light-dark(rgba(61, 61, 58, 1), rgba(194, 192, 182, 1));
    --color-text-tertiary: light-dark(rgba(115, 114, 108, 1), rgba(156, 154, 146, 1));
    --color-text-inverse: light-dark(rgba(255, 255, 255, 1), rgba(20, 20, 19, 1));
    --color-text-info: light-dark(rgba(50, 102, 173, 1), rgba(128, 170, 221, 1));
    --color-text-danger: light-dark(rgba(127, 44, 40, 1), rgba(238, 136, 132, 1));
    --color-text-success: light-dark(rgba(38, 91, 25, 1), rgba(122, 185, 72, 1));
    --color-text-warning: light-dark(rgba(90, 72, 21, 1), rgba(209, 160, 65, 1));
    --color-text-disabled: light-dark(rgba(20, 20, 19, 0.5), rgba(250, 249, 245, 0.5));
    --color-text-ghost: light-dark(rgba(115, 114, 108, 0.5), rgba(156, 154, 146, 0.5));
    --color-border-primary: light-dark(rgba(31, 30, 29, 0.4), rgba(222, 220, 209, 0.4));
    --color-border-secondary: light-dark(rgba(31, 30, 29, 0.3), rgba(222, 220, 209, 0.3));
    --color-border-tertiary: light-dark(rgba(31, 30, 29, 0.15), rgba(222, 220, 209, 0.15));
    --color-border-inverse: light-dark(rgba(255, 255, 255, 0.3), rgba(20, 20, 19, 0.15));
    --color-border-ghost: light-dark(rgba(31, 30, 29, 0), rgba(222, 220, 209, 0));
    --color-border-info: light-dark(rgba(70, 130, 213, 1), rgba(70, 130, 213, 1));
    --color-border-danger: light-dark(rgba(167, 61, 57, 1), rgba(205, 92, 88, 1));
    --color-border-success: light-dark(rgba(67, 116, 38, 1), rgba(89, 145, 48, 1));
    --color-border-warning: light-dark(rgba(128, 92, 31, 1), rgba(168, 120, 41, 1));
    --color-border-disabled: light-dark(rgba(31, 30, 29, 0.1), rgba(222, 220, 209, 0.1));
    --color-ring-primary: light-dark(rgba(20, 20, 19, 0.7), rgba(250, 249, 245, 0.7));
    --color-ring-secondary: light-dark(rgba(61, 61, 58, 0.7), rgba(194, 192, 182, 0.7));
    --color-ring-inverse: light-dark(rgba(255, 255, 255, 0.7), rgba(20, 20, 19, 0.7));
    --color-ring-info: light-dark(rgba(50, 102, 173, 0.5), rgba(128, 170, 221, 0.5));
    --color-ring-danger: light-dark(rgba(167, 61, 57, 0.5), rgba(205, 92, 88, 0.5));
    --color-ring-success: light-dark(rgba(67, 116, 38, 0.5), rgba(89, 145, 48, 0.5));
    --color-ring-warning: light-dark(rgba(128, 92, 31, 0.5), rgba(168, 120, 41, 0.5));
    --font-sans: "Segoe UI", -apple-system, sans-serif;
    --font-mono: ui-monospace, monospace;
    --font-weight-normal: 400;
    --font-weight-medium: 500;
    --font-weight-semibold: 600;
    --font-weight-bold: 700;
    --font-text-xs-size: 12px;
    --font-text-sm-size: 14px;
    --font-text-md-size: 16px;
    --font-text-lg-size: 20px;
    --font-heading-xs-size: 12px;
    --font-heading-sm-size: 14px;
    --font-heading-md-size: 16px;
    --font-heading-lg-size: 20px;
    --font-heading-xl-size: 24px;
    --font-heading-2xl-size: 28px;
    --font-heading-3xl-size: 36px;
    --font-text-xs-line-height: 1.4;
    --font-text-sm-line-height: 1.4;
    --font-text-md-line-height: 1.4;
    --font-text-lg-line-height: 1.25;
    --font-heading-xs-line-height: 1.4;
    --font-heading-sm-line-height: 1.4;
    --font-heading-md-line-height: 1.4;
    --font-heading-lg-line-height: 1.25;
    --font-heading-xl-line-height: 1.25;
    --font-heading-2xl-line-height: 1.1;
    --font-heading-3xl-line-height: 1;
    --border-radius-xs: 4px;
    --border-radius-sm: 6px;
    --border-radius-md: 8px;
    --border-radius-lg: 10px;
    --border-radius-xl: 12px;
    --border-radius-full: 9999px;
    --border-width-regular: 0.5px;
    --shadow-hairline: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
    color-scheme: light dark;
}
body { background: var(--color-background-tertiary); color: var(--color-text-primary); margin: 0; }
.page-center { max-width: 800px; margin: 0 auto; padding: 16px; }
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{tokens_css}</style>
</head>
<body>
<div class="page-center">
{fragment_body}
</div>
</body>
</html>
"""


def wrap(fragment_path, title):
    with open(fragment_path, encoding="utf-8") as f:
        fragment_body = f.read()
    return PAGE_TEMPLATE.format(title=title, tokens_css=TOKENS_CSS, fragment_body=fragment_body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fragment")
    ap.add_argument("--title", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = wrap(args.fragment, args.title)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
