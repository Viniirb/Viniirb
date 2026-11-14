"""Render the static terminal-themed SVGs used by the profile README.

Run manually after editing the data below: `python scripts/render_static_assets.py`.
Output goes to `assets/`. No network access, no dependencies.
"""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

OUT_DIR = Path(__file__).resolve().parents[1] / "assets"

BG = "#0d1117"
PANEL = "#161b22"
BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
PURPLE = "#a855f7"
PURPLE_DARK = "#8A2BE2"
GREEN = "#3fb950"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
CHAR_W = 7.8  # advance width of one glyph at 13px


def _window(width: int, height: int, title: str) -> list[str]:
    return [
        f'<rect width="{width}" height="{height}" rx="12" fill="{BG}"/>',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="none" stroke="{BORDER}"/>',
        f'<path d="M0 12a12 12 0 0 1 12-12h{width - 24}a12 12 0 0 1 12 12v24H0z" fill="{PANEL}"/>',
        f'<line x1="0" y1="36" x2="{width}" y2="36" stroke="{BORDER}"/>',
        '<circle cx="22" cy="18" r="6" fill="#ff5f56"/>',
        '<circle cx="42" cy="18" r="6" fill="#ffbd2e"/>',
        '<circle cx="62" cy="18" r="6" fill="#27c93f"/>',
        f'<text x="{width // 2}" y="23" text-anchor="middle" fill="{MUTED}" font-size="12">{escape(title)}</text>',
    ]


def _svg(width: int, height: int, body: list[str], extra_css: str = "", title: str = "") -> str:
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
            f"<title>{escape(title)}</title>",
            f"<style>text{{font-family:{FONT};font-size:13px}}{extra_css}</style>",
            *body,
            "</svg>",
        ]
    )


def header() -> str:
    width, height = 900, 270
    lines = [
        ("cmd", "whoami", 0.4),
        ("out", "vinicius-rolim-barbosa  ·  Senior Software Engineer", 1.2),
        ("cmd", "cat stack.txt", 2.6),
        ("out", ".NET  ·  arquitetura distribuída  ·  IA aplicada  ·  DevOps", 3.4),
        ("cmd", "echo $LOCATION", 4.9),
        ("out", "Joinville, SC — Brasil", 5.7),
    ]
    css = (
        "@keyframes type{from{width:0}to{width:100%}}"
        "@keyframes blink{50%{opacity:0}}"
        ".cur{animation:blink 1s steps(1) infinite}"
    )
    body = _window(width, height, "vinicius@joinville: ~")
    y = 70
    for i, (kind, text, delay) in enumerate(lines):
        clip_w = int(len(text) * CHAR_W + 30)
        steps = max(len(text), 1)
        dur = 0.05 * steps if kind == "cmd" else 0.025 * steps
        body.append(
            f'<clipPath id="c{i}"><rect x="24" y="{y - 16}" width="{clip_w}" height="22" '
            f'style="animation:type {dur:.2f}s steps({steps}) {delay}s both"/></clipPath>'
        )
        if kind == "cmd":
            body.append(
                f'<g clip-path="url(#c{i})"><text x="24" y="{y}" fill="{GREEN}">❯</text>'
                f'<text x="46" y="{y}" fill="{TEXT}">{escape(text)}</text></g>'
            )
            y += 24
        else:
            color = PURPLE if i == 1 else TEXT
            weight = "700" if i == 1 else "400"
            body.append(
                f'<g clip-path="url(#c{i})"><text x="46" y="{y}" fill="{color}" font-weight="{weight}">{escape(text)}</text></g>'
            )
            y += 34
    body.append(f'<text x="24" y="{y}" fill="{GREEN}">❯</text>')
    body.append(f'<rect class="cur" x="46" y="{y - 12}" width="8" height="16" fill="{PURPLE}"/>')
    return _svg(width, height, body, css, "Terminal: Vinicius Rolim Barbosa, Senior Software Engineer, Joinville SC")


def highlights() -> str:
    width, height = 900, 190
    cards = [
        ("6+", "anos", "produtos digitais e\nsistemas críticos"),
        ("-70%", "tempo", "relatórios e consultas\nSQL Server (EOS)"),
        ("100%", "automático", "pedidos, faturamento\ne estoque (Blump)"),
        ("h → min", "deploy", "CI/CD no\nAzure DevOps"),
    ]
    body = _window(width, height, "stats --summary")
    gap, left = 14, 24
    card_w = (width - 2 * left - gap * (len(cards) - 1)) / len(cards)
    for i, (big, unit, desc) in enumerate(cards):
        x = left + i * (card_w + gap)
        body.append(f'<rect x="{x:.1f}" y="56" width="{card_w:.1f}" height="112" rx="8" fill="{PANEL}" stroke="{BORDER}"/>')
        body.append(f'<rect x="{x:.1f}" y="56" width="3" height="112" rx="1.5" fill="{PURPLE_DARK}"/>')
        body.append(f'<text x="{x + 18:.1f}" y="92" fill="{PURPLE}" font-size="26" font-weight="700">{escape(big)}</text>')
        body.append(f'<text x="{x + 18:.1f}" y="112" fill="{GREEN}" font-size="12">{escape(unit)}</text>')
        for j, line in enumerate(desc.split("\n")):
            body.append(f'<text x="{x + 18:.1f}" y="{136 + j * 16}" fill="{MUTED}" font-size="12">{escape(line)}</text>')
    return _svg(width, height, body, title="Destaques: 6+ anos, -70% tempo de relatórios, 100% automação de pedidos, deploy de horas para minutos")


def stack() -> str:
    width = 900
    groups = [
        ("backend", [".NET", "C#", "ASP.NET Core", "EF Core", "Node.js", "REST", "GraphQL", "Python"]),
        ("frontend", ["Angular", "React", "Next.js", "Vue.js", "TypeScript", "Solid.js", "Tailwind", "PrimeNG"]),
        ("mobile", ["Ionic", ".NET MAUI", "Capacitor", "React Native"]),
        ("dados-ia", ["SQL Server", "PostgreSQL", "Supabase", "ML", "RAG", "agentes IA"]),
        ("integracoes", ["RabbitMQ", "n8n", "webhooks", "Tiny", "Benner", "idempotência"]),
        ("devops", ["Azure DevOps", "Docker", "Git", "Linux", "CI/CD", "Sonar"]),
    ]
    body: list[str] = []
    y = 62
    label_w = 128
    for name, items in groups:
        body.append(f'<text x="24" y="{y + 14}" fill="{GREEN}">{name}/</text>')
        x = 24 + label_w
        row_y = y
        for item in items:
            w = len(item) * CHAR_W + 18
            if x + w > width - 24:
                x = 24 + label_w
                row_y += 30
            body.append(f'<rect x="{x:.1f}" y="{row_y}" width="{w:.1f}" height="22" rx="11" fill="{PANEL}" stroke="{BORDER}"/>')
            body.append(f'<text x="{x + w / 2:.1f}" y="{row_y + 15}" text-anchor="middle" fill="{TEXT}" font-size="12">{escape(item)}</text>')
            x += w + 8
        y = row_y + 38
    height = y + 10
    return _svg(width, height, _window(width, height, "tree ./stack") + body, title="Stack técnica: backend, frontend, mobile, dados e IA, integrações e DevOps")


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    for name, render in (("header", header), ("highlights", highlights), ("stack", stack)):
        path = OUT_DIR / f"{name}.svg"
        path.write_text(render(), encoding="utf-8")
        print(f"wrote {path.relative_to(OUT_DIR.parent)} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
