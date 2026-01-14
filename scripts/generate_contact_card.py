from pathlib import Path

def generate_contact_svg():
    """Generate a beautiful interactive contact card SVG"""
    
    width = 900
    height = 180
    
    contacts = [
        {
            "name": "Gmail",
            "url": "mailto:vinii.rbarbosa@gmail.com",
            "icon": "M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z",
            "color": "#EA4335",
            "x": 50
        },
        {
            "name": "ProtonMail",
            "url": "mailto:viniirb@pm.me",
            "icon": "M12 2L3 7v7c0 5.5 3.8 10.7 9 12 5.2-1.3 9-6.5 9-12V7l-9-5zm0 2.2L19 8v6c0 4.5-3.2 8.8-7 10-3.8-1.2-7-5.5-7-10V8l7-3.8z",
            "color": "#6D4AFF",
            "x": 230
        },
        {
            "name": "LinkedIn",
            "url": "https://www.linkedin.com/in/vinicius-rolim-barbosa-15b066374/",
            "icon": "M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z",
            "color": "#0A66C2",
            "x": 410
        },
        {
            "name": "GitHub",
            "url": "https://github.com/Viniirb?tab=repositories",
            "icon": "M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z",
            "color": "#181717",
            "x": 590
        },
        {
            "name": "Portfólio",
            "url": "https://myportifolio-vinicius.vercel.app/",
            "icon": "M3 3h18v18H3V3m16 16V5H5v14h14m-4-4h2v2h-2v-2m-4 0h2v2h-2v-2m-4 0h2v2H7v-2m12-4h-2v2h2v-2m-4 0h-2v2h2v-2m-4 0H7v2h2v-2m8-4h-2v2h2V7m-4 0h-2v2h2V7m-4 0H7v2h2V7z",
            "color": "#000000",
            "x": 770
        }
    ]
    
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<defs>',
        # Gradiente de fundo
        '<linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '  <stop offset="0%" style="stop-color:#667eea;stop-opacity:0.1" />',
        '  <stop offset="100%" style="stop-color:#764ba2;stop-opacity:0.1" />',
        '</linearGradient>',
    ]
    
    # Criar gradientes e filtros para cada ícone
    for i, contact in enumerate(contacts):
        svg_parts.extend([
            f'<linearGradient id="iconGrad{i}" x1="0%" y1="0%" x2="100%" y2="100%">',
            f'  <stop offset="0%" style="stop-color:{contact["color"]};stop-opacity:1" />',
            f'  <stop offset="100%" style="stop-color:#8A2BE2;stop-opacity:1" />',
            '</linearGradient>',
            f'<filter id="glow{i}">',
            f'  <feGaussianBlur stdDeviation="2" result="coloredBlur"/>',
            '  <feMerge>',
            '    <feMergeNode in="coloredBlur"/>',
            '    <feMergeNode in="SourceGraphic"/>',
            '  </feMerge>',
            '</filter>',
        ])
    
    svg_parts.extend([
        '</defs>',
        '<style>',
        '.contact-card { transition: all 0.3s ease; cursor: pointer; }',
        '.contact-card:hover .card-bg { fill: url(#bgGrad); }',
        '.contact-card:hover .icon-circle { r: 28; }',
        '.contact-card:hover .icon-path { filter: url(#glow0); }',
        '.contact-title { font: 600 11px ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial; }',
        '</style>',
        # Fundo
        f'<rect width="{width}" height="{height}" rx="16" fill="#0d1117"/>',
        f'<rect x="8" y="8" width="{width-16}" height="{height-16}" rx="12" fill="#161b22"/>',
        # Título
        '<text x="450" y="35" text-anchor="middle" fill="#c9d1d9" font-family="ui-sans-serif,system-ui" font-size="20" font-weight="700">💬 Vamos conversar?</text>',
        '<text x="450" y="55" text-anchor="middle" fill="#8b949e" font-family="ui-sans-serif,system-ui" font-size="12">Escolha seu canal preferido de contato</text>',
    ])
    
    # Adicionar cada card de contato
    for i, contact in enumerate(contacts):
        x = contact["x"]
        y = 90
        
        svg_parts.extend([
            f'<a href="{contact["url"]}" target="_blank" class="contact-card">',
            '<g>',
            # Círculo de fundo do ícone com hover
            f'  <circle class="icon-circle" cx="{x}" cy="{y}" r="24" fill="#21262d" opacity="0.8"/>',
            # Ícone SVG
            f'  <g transform="translate({x-12}, {y-12}) scale(1)">',
            f'    <path class="icon-path" d="{contact["icon"]}" fill="{contact["color"]}" opacity="0.9"/>',
            '  </g>',
            # Label
            f'  <text x="{x}" y="{y + 42}" class="contact-title" text-anchor="middle" fill="#8b949e">{contact["name"]}</text>',
            '</g>',
            '</a>',
        ])
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)


if __name__ == "__main__":
    output_dir = Path(__file__).resolve().parents[1] / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    svg_content = generate_contact_svg()
    output_path = output_dir / "contact-card.svg"
    output_path.write_text(svg_content, encoding="utf-8")
    
    print(f"✓ Generated contact card: {output_path}")
    print(f"  Size: {output_path.stat().st_size} bytes")
