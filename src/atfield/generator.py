"""
Générateur d'SVG hexagonal style A.T. Field (Evangelion).

Produit une barre de progression animée composée de 100 hexagones :
- Les premiers X sont verts (chargés)
- Les 10 suivants sont orange et pulsent (en train de charger)
- Le reste est noir (non chargés)
- Un grand hexagone central affiche le pourcentage en police Orbitron
"""

from __future__ import annotations

import math
from dataclasses import dataclass

SQRT3 = math.sqrt(3)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class Theme:
    background: str  = "#0a0a0f"
    filled: str      = "#b5e050"   # Vert des hexagones chargés
    charging: str    = "#FF8C00"   # Orange de ceux en train de charger
    empty: str       = "#0c0c0a"   # Noir des hexagones vides
    stroke: str      = "#FF8C00"   # Bordure de l'hexagone central
    stroke_width: float = 1.5
    padding: int     = 30
    glow: bool       = True


DEFAULT_THEME = Theme()


@dataclass
class GridConfig:
    hex_count: int     = 100
    hex_radius: float  = 13
    gap: float         = 0.08
    rows: int          = 5
    seed: int          = 1
    center_radius: float = 38
    charge_band: int   = 15


# ---------------------------------------------------------------------------
# Géométrie
# ---------------------------------------------------------------------------

def hexagon_points(cx: float, cy: float, r: float) -> str:
    """Retourne les 6 sommets d'un hexagone flat-top centré en (cx, cy)."""
    vertices = []
    for i in range(6):
        angle = math.radians(60 * i)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        vertices.append(f"{x:.2f},{y:.2f}")
    return " ".join(vertices)


def _noise_val(col: int, row: int, seed: int) -> float:
    """Valeur pseudo-aléatoire entre 0 et 1 pour un placement organique."""
    raw = (math.sin(col * 0.85 + seed * 0.1) +
           math.sin(row * 0.65 + seed * 1.3) +
           math.sin((col + row) * 0.35 + seed * 0.7) +
           math.sin(col * 1.20 - row * 0.80 + seed * 0.5))
    return (raw + 4.0) / 8.0


# ---------------------------------------------------------------------------
# Placement des hexagones
# ---------------------------------------------------------------------------

def _compute_layout(cfg: GridConfig, theme: Theme):
    """
    Construit la grille d'hexagones autour du centre.
    Les hexagones trop proches du centre sont supprimés,
    puis on garde les cfg.hex_count plus proches du centre.
    """
    big_r = cfg.center_radius
    spacing = 1.0 + cfg.gap
    h_spacing = 1.5 * cfg.hex_radius * spacing
    v_spacing = SQRT3 * cfg.hex_radius * spacing

    hidden_est = max(6, int(math.pi * big_r ** 2 / (h_spacing * v_spacing)))
    cols = math.ceil((cfg.hex_count + hidden_est) / cfg.rows)

    grid_w = (cols - 1) * h_spacing + 2.0 * cfg.hex_radius
    grid_h = (cfg.rows - 1) * v_spacing + SQRT3 * cfg.hex_radius
    big_cx = theme.padding + grid_w / 2.0
    big_cy = theme.padding + grid_h / 2.0
    svg_w = grid_w + 2.0 * theme.padding
    svg_h = grid_h + 2.0 * theme.padding

    candidates = []
    for row in range(cfg.rows):
        for col in range(cols):
            cx = theme.padding + col * h_spacing + cfg.hex_radius
            cy = theme.padding + row * v_spacing + SQRT3 / 2.0 * cfg.hex_radius
            if col % 2 == 1:
                cy += v_spacing / 2.0
            d = math.hypot(cx - big_cx, cy - big_cy)
            if d < big_r - cfg.hex_radius:
                continue
            candidates.append((d, cx, cy, col, row))

    candidates.sort(key=lambda x: x[0])
    hex_data = [(cx, cy, col, row) for _, cx, cy, col, row in candidates[:cfg.hex_count]]
    return hex_data, big_cx, big_cy, svg_w, svg_h


# ---------------------------------------------------------------------------
# Filtre neon glow
# ---------------------------------------------------------------------------

def _write_glow_filter(lines: list[str]):
    lines.append("  <defs>")
    lines.append("    <filter id=\"g\">")
    lines.append("      <feGaussianBlur stdDeviation=\"2.5\" result=\"blur\"/>")
    lines.append("      <feMerge>")
    lines.append("        <feMergeNode in=\"blur\"/>")
    lines.append("        <feMergeNode in=\"SourceGraphic\"/>")
    lines.append("      </feMerge>")
    lines.append("    </filter>")
    lines.append("  </defs>")


def build_polygon_markup(points: str, fill: str, *, border: str | None = None,
                         glow: bool = False, extra_attrs: str = "") -> str:
    """Construit le markup d’un polygone SVG de manière réutilisable et compacte."""
    attrs = [f'fill="{fill}"']
    border_attr = border or 'stroke="rgba(0,0,0,0.35)" stroke-width="1"'
    if border_attr:
        attrs.append(border_attr)
    if glow:
        attrs.append('filter="url(#g)"')
    if extra_attrs:
        attrs.append(extra_attrs)
    return f'  <polygon points="{points}" {" ".join(attrs)}/>'


# ---------------------------------------------------------------------------
# Hexagone central
# ---------------------------------------------------------------------------

def _write_center_hex(big_cx: float, big_cy: float, big_r: float,
                      theme: Theme, lines: list[str], text: str):
    big_pts = hexagon_points(big_cx, big_cy, big_r)
    border_attr = f'stroke="{theme.stroke}" stroke-width="1.5"'
    lines.append(build_polygon_markup(big_pts, "#000000", border=border_attr))
    if theme.glow:
        lines.append(build_polygon_markup(big_pts, "#000000", border=border_attr,
                                          glow=True, extra_attrs='opacity="0.5"'))

    font_size = max(int(big_r * 0.5), 14)
    text_attrs = (f"x=\"{big_cx:.0f}\" y=\"{big_cy:.0f}\" "
                  f"text-anchor=\"middle\" dominant-baseline=\"central\" "
                  f"fill=\"#ffb84d\" font-size=\"{font_size}\" "
                  f"font-family=\"'Orbitron','Arial Black',sans-serif\" "
                  f"font-weight=\"900\"")
    if theme.glow:
        lines.append(f"  <text {text_attrs} filter=\"url(#g)\" opacity=\"0.8\">{text}</text>")
    lines.append(f"  <text {text_attrs}>{text}</text>")


# ---------------------------------------------------------------------------
# Attribution des états
# ---------------------------------------------------------------------------

def _assign_states(hex_data: list, cfg: GridConfig, progress: int):
    """
    Trie les hexagones par bruit, puis attribue :
    - 'filled' pour les 'progress' premiers
    - 'charging' pour les 'charge_band' suivants
    - 'empty' pour le reste
    """
    indexed = [(noise_val(col, row, cfg.seed), cx, cy, col, row)
               for cx, cy, col, row in hex_data]
    indexed.sort(key=lambda x: x[0])

    band = min(cfg.charge_band, cfg.hex_count - progress)
    result = []
    for i, (_, cx, cy, col, row) in enumerate(indexed):
        if i < progress:
            state = "filled"
        elif i < progress + band:
            state = "charging"
        else:
            state = "empty"
        result.append((cx, cy, col, row, state))
    return result

# Alias local
noise_val = _noise_val


# ---------------------------------------------------------------------------
# Génération SVG animée
# ---------------------------------------------------------------------------

def generate(cfg: GridConfig | None = None,
             theme: Theme | None = None,
             progress: int = 0) -> str:
    """
    Génère une SVG hexagonale animée.

    Paramètres
    ----------
    cfg : GridConfig
        Configuration de la grille
    theme : Theme
        Couleurs et réglages visuels
    progress : int
        Pourcentage de charge (0 à 100)

    Retourne
    -------
    str
        Code SVG complet
    """
    if cfg is None:
        cfg = GridConfig()
    if theme is None:
        theme = DEFAULT_THEME

    hex_data, big_cx, big_cy, svg_w, svg_h = _compute_layout(cfg, theme)
    states = _assign_states(hex_data, cfg, progress)

    rate = 5.0
    lines = []

    # En-tête
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                 f'viewBox="0 0 {svg_w:.0f} {svg_h:.0f}">')
    lines.append('  <style>')
    lines.append('    @font-face {')
    lines.append('      font-family: Orbitron;')
    lines.append('      font-weight: 900;')
    lines.append('      src: url("https://fonts.gstatic.com/s/orbitron/v35/'
                 'yMJMMIlzdpvBhQQL_SC3X9yhF25-T1nysimBoWgz.woff2") '
                 'format("woff2");')
    lines.append('    }')
    lines.append(f'    @keyframes charge {{')
    lines.append(f'      0%, 100% {{ fill: {theme.empty}; }}')
    lines.append(f'      50%      {{ fill: {theme.charging}; }}')
    lines.append(f'    }}')
    lines.append('  </style>')

    if theme.glow:
        _write_glow_filter(lines)

    border = 'stroke="rgba(0,0,0,0.35)" stroke-width="1"'
    charge_idx = 0
    filled_fill = theme.filled
    empty_fill = theme.empty
    glow_enabled = theme.glow

    for cx, cy, _, _, state in states:
        pts = hexagon_points(cx, cy, cfg.hex_radius)

        if state == "filled":
            lines.append(build_polygon_markup(pts, filled_fill, border=border,
                                              glow=glow_enabled))

        elif state == "charging":
            delay = (charge_idx / cfg.charge_band) * rate
            lines.append(f'  <polygon points="{pts}" fill="{empty_fill}" {border} '
                         f'style="animation: charge {rate}s ease-in-out '
                         f'infinite; animation-delay: {delay:.3f}s;"/>')
            charge_idx += 1

        else:
            lines.append(build_polygon_markup(pts, empty_fill, border=border))

    _write_center_hex(big_cx, big_cy, cfg.center_radius,
                      theme, lines, f"{progress}%")
    lines.append("</svg>")
    return "\n".join(lines)
