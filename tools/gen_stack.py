#!/usr/bin/env python3
"""Generate assets/tech-stack.svg — the tech-stack strip for the profile README.

One self-contained SVG (brand icons inlined from tools/icons.json, no external
requests) so the section can never reflow into one-item-per-line the way a row
of separate <img> badges can.

    python3 tools/gen_stack.py > assets/tech-stack.svg

Icon paths come from Simple Icons (CC0). Colours in icons.json are adjusted for
legibility on the dark #06050f background, so they are not always the official
brand hex.
"""

import json
import os

W = 1200
PAD_L = 40
LABEL_W = 250
CHIP_X = PAD_L + LABEL_W
CHIP_MAX = W - CHIP_X - PAD_L
CHIP_H = 32
CHIP_GAP = 10
ROW_GAP = 26
TOP = 34

ICON = 15
ICON_GAP = 7
CHIP_PAD = 13

PURPLE = "#7c5cff"
TEAL = "#00e7c4"
GREY = "#5a5a78"

ICONS = json.load(open(os.path.join(os.path.dirname(__file__), "icons.json")))

# (domain, level, level colour, chip accent, [(label, icon slug or None)])
ROWS = [
    ("Frontend", "Expert", PURPLE, PURPLE, [
        ("React", "react"),
        ("Next.js · RSC", "nextdotjs"),
        ("TypeScript", "typescript"),
        ("Tailwind CSS", "tailwindcss"),
        ("Three.js / GLSL", "threedotjs"),
        ("GSAP", "greensock"),
    ]),
    ("Backend", "Advanced", TEAL, TEAL, [
        ("Node.js", "nodedotjs"),
        ("NestJS", "nestjs"),
        ("gRPC", None),
        ("NATS", "natsdotio"),
        ("Dapr", "dapr"),
        ("Redis", "redis"),
        ("PostgreSQL", "postgresql"),
        ("MongoDB", "mongodb"),
        ("DynamoDB", "amazondynamodb"),
        ("Prisma", "prisma"),
    ]),
    ("AI / LLM", "Advanced", TEAL, PURPLE, [
        ("AWS Bedrock", "amazonwebservices"),
        ("Gemini", "googlegemini"),
        ("OpenAI", "openai"),
        ("MCP", "anthropic"),
        ("RAG", None),
        ("agent tooling & memory", None),
    ]),
    ("Mobile", "Advanced", TEAL, PURPLE, [
        ("Swift / SwiftUI", "swift"),
        ("React Native", "react"),
        ("Capacitor", "capacitor"),
    ]),
    ("Web3", "Proficient", GREY, TEAL, [
        ("Solidity", "solidity"),
        ("ethers", "ethereum"),
        ("wagmi", "wagmi"),
        ("Hardhat", None),
    ]),
    ("DevOps", "Proficient", GREY, TEAL, [
        ("Docker", "docker"),
        ("AWS", "amazonwebservices"),
        ("CI/CD", "githubactions"),
        ("Sentry", "sentry"),
        ("Vercel", "vercel"),
    ]),
    ("Games", "Proficient", GREY, PURPLE, [
        ("Unity (C#)", "unity"),
        ("HTML5 Canvas", "html5"),
        ("Phaser", None),
    ]),
]

# Conservative advance widths for a 12.5px Helvetica/Arial-class sans.
NARROW = set("iljtfrI().,·/ ")
WIDE = set("mwMW@")


def text_w(s, size=12.5):
    u = 0.0
    for ch in s:
        if ch in NARROW:
            u += 0.36
        elif ch in WIDE:
            u += 0.85
        elif ch.isupper():
            u += 0.68
        else:
            u += 0.56
    return u * size


def chip_w(label, icon):
    return CHIP_PAD * 2 + ICON + ICON_GAP + text_w(label) if icon else \
        CHIP_PAD * 2 + 6 + ICON_GAP + text_w(label)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def layout():
    placed = []
    y = TOP
    for label, level, level_color, accent, chips in ROWS:
        lines, cur, cur_w = [], [], 0.0
        for text, icon in chips:
            w = chip_w(text, icon)
            if cur and cur_w + w + CHIP_GAP > CHIP_MAX:
                lines.append(cur)
                cur, cur_w = [], 0.0
            cur.append((text, icon, w))
            cur_w += w + CHIP_GAP
        if cur:
            lines.append(cur)
        h = len(lines) * CHIP_H + (len(lines) - 1) * 8
        placed.append((label, level, level_color, accent, lines, y, h))
        y += h + ROW_GAP
    return placed, y - ROW_GAP + TOP


def render():
    rows, height = layout()
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" '
        f'width="{W}" height="{height}" role="img" '
        f'aria-label="Tech stack by domain and depth">',
        "  <defs>",
        '    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">',
        '      <path d="M40 0H0V40" fill="none" stroke="#ffffff" '
        'stroke-opacity="0.03" stroke-width="1"/>',
        "    </pattern>",
        "  </defs>",
        f'  <rect width="{W}" height="{height}" rx="14" fill="#06050f"/>',
        f'  <rect width="{W}" height="{height}" rx="14" fill="url(#grid)"/>',
        "  <g font-family=\"'Space Grotesk', 'Helvetica Neue', Helvetica, Arial, sans-serif\">",
    ]

    for i, (label, level, level_color, accent, lines, y, h) in enumerate(rows):
        mid = y + h / 2
        o.append(f'    <text x="{PAD_L}" y="{mid + 5:.0f}" font-size="16" '
                 f'fill="#ffffff">{esc(label)}</text>')

        pill_w = text_w(level, 10.5) + 22
        pill_x = PAD_L + 132
        o.append(f'    <rect x="{pill_x}" y="{mid - 11:.0f}" width="{pill_w:.0f}" '
                 f'height="22" rx="11" fill="{level_color}" fill-opacity="0.16" '
                 f'stroke="{level_color}" stroke-opacity="0.5"/>')
        o.append(f'    <text x="{pill_x + pill_w / 2:.0f}" y="{mid + 4:.0f}" '
                 f'font-size="10.5" letter-spacing="1" text-anchor="middle" '
                 f'fill="{level_color}">{level.upper()}</text>')

        cy = y
        for line in lines:
            cx = CHIP_X
            for text, icon, w in line:
                o.append(f'    <rect x="{cx:.0f}" y="{cy}" width="{w:.0f}" '
                         f'height="{CHIP_H}" rx="{CHIP_H // 2}" fill="{accent}" '
                         f'fill-opacity="0.10" stroke="{accent}" stroke-opacity="0.32"/>')
                if icon:
                    ic = ICONS[icon]
                    gx = cx + CHIP_PAD
                    gy = cy + (CHIP_H - ICON) / 2
                    s = ICON / 24
                    o.append(f'    <g transform="translate({gx:.1f} {gy:.1f}) '
                             f'scale({s:.4f})"><path d="{ic["path"]}" '
                             f'fill="{ic["hex"]}"/></g>')
                    tx = cx + CHIP_PAD + ICON + ICON_GAP
                else:
                    o.append(f'    <circle cx="{cx + CHIP_PAD + 3:.1f}" '
                             f'cy="{cy + CHIP_H / 2:.0f}" r="3" fill="none" '
                             f'stroke="{accent}" stroke-opacity="0.8"/>')
                    tx = cx + CHIP_PAD + 6 + ICON_GAP
                o.append(f'    <text x="{tx:.0f}" y="{cy + 20}" font-size="12.5" '
                         f'fill="#d2d2e4">{esc(text)}</text>')
                cx += w + CHIP_GAP
            cy += CHIP_H + 8

        if i < len(rows) - 1:
            ly = y + h + ROW_GAP / 2
            o.append(f'    <rect x="{PAD_L}" y="{ly:.0f}" width="{W - 2 * PAD_L}" '
                     f'height="1" fill="#ffffff" fill-opacity="0.05"/>')

    o.append("  </g>")
    o.append("</svg>")
    return "\n".join(o) + "\n"


if __name__ == "__main__":
    import sys
    sys.stdout.write(render())
