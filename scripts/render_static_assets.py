"""Render the static terminal-themed SVGs used by the profile README.

Run manually after editing the data below: `python scripts/render_static_assets.py`.
Output goes to `assets/`. No network access, no dependencies.
"""
from __future__ import annotations

import textwrap
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
GOLD = "#e3b341"
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


def about() -> str:
    width = 900
    pt = (
        "Engenheiro de Software Sênior com 6 anos em produtos digitais e sistemas críticos. "
        "Atuo de ponta a ponta com .NET, arquitetura distribuída, integrações, dados e IA aplicada. "
        "Passei pela iBR Software modernizando o ERP, estruturando o módulo Financeiro e construindo "
        "análise de risco com machine learning."
    )
    en = (
        "Senior Software Engineer with 6 years building digital products and mission-critical systems. "
        "End-to-end work with .NET, distributed architecture, integrations, data and applied AI. "
        "At iBR Software I modernized the ERP, built the Finance module and a machine learning "
        "risk-analysis pipeline."
    )
    body: list[str] = []
    y = 66
    for tag, color, text in (("pt-BR", PURPLE, pt), ("en", GREEN, en)):
        body.append(f'<text x="24" y="{y}" fill="{color}" font-weight="700">[{tag}]</text>')
        y += 22
        for line in textwrap.wrap(text, 104):
            body.append(f'<text x="24" y="{y}" fill="{TEXT}">{escape(line)}</text>')
            y += 20
        y += 14
    height = y - 2
    return _svg(width, height, _window(width, height, "cat about.md") + body, title="Sobre: " + pt)


CAREER = [
    (
        "Abr 2026 → Nov 2026",
        "iBR Software",
        "★ Destaque do mês · Out/2026",
        "Modernização do ERP em arquitetura distribuída (.NET), novo módulo Financeiro (contas a pagar/receber, baixas, plano de contas, centros de custo), cutover com reconciliação, idempotência e feature flags, pipeline de ML para risco financeiro.",
        "ERP modernization on distributed .NET, new Finance module, cutover with reconciliation and idempotency, ML pipeline for financial risk.",
    ),
    (
        "Fev 2025 → Abr 2026",
        "N Tecnologias · Coopercargo",
        "",
        "Liderança da migração completa de ERP e da evolução de monólito para serviços .NET; agentes de IA generativa com execução segura de SQL/NoSQL; automação com n8n; app Ionic; Supabase.",
        "Led the full ERP migration and monolith-to-.NET-services evolution; generative AI agents with safe SQL/NoSQL execution; n8n; Ionic app.",
    ),
    (
        "Dez 2023 → Ago 2024",
        "EOS · Organização e Sistemas",
        "",
        "Redução de até 70% no tempo de relatórios e consultas SQL Server; apps offline-first com .NET MAUI; APIs e aplicações Web em .NET para saneamento.",
        "Up to 70% faster SQL Server reports and queries; offline-first .NET MAUI apps; .NET APIs and web apps.",
    ),
    (
        "Nov 2023 → Dez 2023",
        "Blump",
        "",
        "Full Stack (PJ). 100% do fluxo de pedidos, faturamento e estoque automatizado via ERP Tiny; deploy de horas para minutos com CI/CD no Azure DevOps; .NET, Vue.js, n8n.",
        "Full Stack contractor. Fully automated order, billing and stock flow; deploys from hours to minutes.",
    ),
    (
        "Set 2021 → Out 2023",
        "Inovvati Tecnologia",
        "",
        "React, Next.js, APIs REST e GraphQL, modernização de sistemas legados .NET.",
        "React, Next.js, REST and GraphQL APIs, legacy .NET modernization.",
    ),
]


def career() -> str:
    width = 900
    body: list[str] = []
    y = 62
    dots: list[tuple[int, str]] = []
    for period, company, badge, pt, en in CAREER:
        dots.append((y + 8, GOLD if badge else PURPLE))
        body.append(f'<text x="52" y="{y + 12}" fill="{MUTED}" font-size="12">{escape(period)}</text>')
        body.append(f'<text x="214" y="{y + 12}" fill="{PURPLE}" font-weight="700" font-size="14">{escape(company)}</text>')
        if badge:
            bx = 214 + len(company) * 8.4 + 18
            bw = len(badge) * 7.2 + 20
            body.append(f'<rect x="{bx:.1f}" y="{y - 2}" width="{bw:.1f}" height="22" rx="11" fill="#2a2208" stroke="{GOLD}"/>')
            body.append(f'<text x="{bx + bw / 2:.1f}" y="{y + 13}" text-anchor="middle" fill="{GOLD}" font-size="12" font-weight="700">{escape(badge)}</text>')
        ly = y + 36
        for line in textwrap.wrap(pt, 88):
            body.append(f'<text x="214" y="{ly}" fill="{TEXT}" font-size="12">{escape(line)}</text>')
            ly += 18
        for line in textwrap.wrap(en, 98):
            body.append(f'<text x="214" y="{ly}" fill="{MUTED}" font-size="11">{escape(line)}</text>')
            ly += 16
        y = ly + 20
    height = y
    line_top, line_bot = 70, dots[-1][0]
    rail = [f'<line x1="36" y1="{line_top}" x2="36" y2="{line_bot}" stroke="{BORDER}" stroke-width="2"/>']
    for cy, color in dots:
        rail.append(f'<circle cx="36" cy="{cy}" r="6" fill="{BG}" stroke="{color}" stroke-width="2"/>')
        rail.append(f'<circle cx="36" cy="{cy}" r="2.5" fill="{color}"/>')
    title = "Experiência: " + "; ".join(f"{c[1]} ({c[0]})" for c in CAREER)
    return _svg(width, height, _window(width, height, "git log --career") + rail + body, title=title)


CERTS = [
    ("2026", "Claude 101 e Claude Code in Action", "Anthropic"),
    ("2026", "Engenharia de Prompt e Redes Neurais", "Rocketseat"),
    ("2026", "Fundamentos de C# e Intro .NET", "Rocketseat / .NET"),
    ("2025", "Azure Big Data e Microsoft Fabric", "Udemy"),
    ("2025", "Cibersegurança e módulos DIO", "Santander / DIO"),
    ("2025", "NLW: React, RN, Node.js e Python", "Rocketseat"),
    ("2024", "SEO para Devs", "Rocketseat"),
]


def education() -> str:
    width = 900
    body = [
        f'<text x="24" y="66" fill="{GREEN}">edu/</text>',
        f'<rect x="24" y="78" width="852" height="52" rx="8" fill="{PANEL}" stroke="{BORDER}"/>',
        f'<rect x="24" y="78" width="3" height="52" rx="1.5" fill="{PURPLE_DARK}"/>',
        f'<text x="44" y="100" fill="{TEXT}" font-weight="700" font-size="14">Análise e Desenvolvimento de Sistemas</text>',
        f'<text x="44" y="119" fill="{MUTED}" font-size="12">Católica SC  ·  cursando / in progress</text>',
        f'<text x="24" y="162" fill="{GREEN}">certs/</text>',
    ]
    col_w, y0 = 426, 174
    for i, (year, name, issuer) in enumerate(CERTS):
        x = 24 + (i % 2) * (col_w + 0)
        y = y0 + (i // 2) * 52
        body.append(f'<rect x="{x}" y="{y}" width="{col_w - 12}" height="42" rx="8" fill="{PANEL}" stroke="{BORDER}"/>')
        body.append(f'<rect x="{x + 10}" y="{y + 11}" width="40" height="20" rx="10" fill="{BG}" stroke="{PURPLE_DARK}"/>')
        body.append(f'<text x="{x + 30}" y="{y + 25}" text-anchor="middle" fill="{PURPLE}" font-size="11" font-weight="700">{year}</text>')
        body.append(f'<text x="{x + 62}" y="{y + 18}" fill="{TEXT}" font-size="12">{escape(name)}</text>')
        body.append(f'<text x="{x + 62}" y="{y + 33}" fill="{MUTED}" font-size="11">{escape(issuer)}</text>')
    height = y0 + ((len(CERTS) + 1) // 2) * 52 + 10
    title = "Educação e certificações: Análise e Desenvolvimento de Sistemas (Católica SC); " + "; ".join(f"{c[0]} {c[1]}" for c in CERTS)
    return _svg(width, height, _window(width, height, "ls ./edu ./certs") + body, title=title)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    for name, render in (("header", header), ("about", about), ("highlights", highlights), ("stack", stack), ("career", career), ("education", education)):
        path = OUT_DIR / f"{name}.svg"
        path.write_text(render(), encoding="utf-8")
        print(f"wrote {path.relative_to(OUT_DIR.parent)} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
