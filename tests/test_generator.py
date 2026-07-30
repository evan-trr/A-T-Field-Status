"""
Tests pour le générateur d'SVG hexagonal A.T. Field.
"""
import math

from atfield.generator import DEFAULT_THEME, GridConfig, Theme, generate, hexagon_points


def test_hexagon_points_returns_6_vertices():
    """Un hexagone doit avoir exactement 6 sommets."""
    pts = hexagon_points(0, 0, 10)
    assert len(pts.split(" ")) == 6


def test_hexagon_first_point_is_at_0_degrees():
    """Le premier sommet est à droite (angle 0°)."""
    pts = hexagon_points(0, 0, 10)
    first = pts.split(" ")[0]
    x, y = map(float, first.split(","))
    assert math.isclose(x, 10.0, abs_tol=0.01)
    assert math.isclose(y, 0.0, abs_tol=0.01)


def test_svg_starts_and_ends_correctly():
    """L'SVG commence par <svg et finit par </svg>."""
    svg = generate(GridConfig(hex_count=10, hex_radius=8), DEFAULT_THEME, 50)
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")


def test_exact_hexagon_count():
    """Le nombre de petits hexagones (sans le central) doit être exact."""
    svg = generate(GridConfig(hex_count=50, hex_radius=8), DEFAULT_THEME, 30)
    count = sum(1 for line in svg.split("\n")
                if "<polygon" in line and "fill=\"#000000\"" not in line)
    assert count == 50


def test_progress_0():
    """À 0%, seuls les hexagones en charge (orange) doivent être présents."""
    svg = generate(GridConfig(hex_count=10, hex_radius=8), DEFAULT_THEME, 0)
    assert DEFAULT_THEME.charging in svg
    assert DEFAULT_THEME.filled not in svg


def test_progress_100():
    """À 100%, aucun hexagone vide n'est présent."""
    svg = generate(GridConfig(hex_count=10, hex_radius=8), DEFAULT_THEME, 100)
    assert DEFAULT_THEME.filled in svg


def test_center_hexagon_has_black_fill():
    """L'hexagone central doit être noir."""
    svg = generate(GridConfig(hex_count=10, hex_radius=8), DEFAULT_THEME, 50)
    assert "fill=\"#000000\"" in svg


def test_glow_adds_filter():
    """Le SVG doit contenir un filtre de glow quand glow=True."""
    svg = generate(GridConfig(hex_count=10, hex_radius=8), DEFAULT_THEME, 50)
    assert "<filter" in svg


def test_percentage_text_present():
    """Le pourcentage doit être affiché dans le SVG."""
    svg = generate(GridConfig(hex_count=10, hex_radius=8), DEFAULT_THEME, 42)
    assert "42%" in svg


def test_text_uses_amber_color():
    """Le texte du pourcentage doit être ambré (#ffb84d)."""
    svg = generate(GridConfig(hex_count=10, hex_radius=8), DEFAULT_THEME, 50)
    assert "fill=\"#ffb84d\"" in svg


def test_no_hidden_hexagons():
    """Tous les petits hexagones doivent être visibles (aucun overlap)."""
    svg = generate(GridConfig(hex_count=100, hex_radius=13, gap=0.12), DEFAULT_THEME, 50)
    count = sum(1 for line in svg.split("\n")
                if "<polygon" in line and "fill=\"#000000\"" not in line)
    assert count == 100


def test_animated_features():
    """L'SVG animée doit contenir les animations CSS."""
    svg = generate(GridConfig(hex_count=20, hex_radius=8), DEFAULT_THEME, 50)
    assert "@keyframes charge" in svg
    assert "50%" in svg
