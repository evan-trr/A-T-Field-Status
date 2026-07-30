from __future__ import annotations

import argparse
import sys

from atfield.generator import DEFAULT_THEME, GridConfig, Theme, generate


def hex_color(value: str) -> str:
    if value == "none":
        return value
    if not value.startswith("#") or len(value) not in (4, 7):
        raise ValueError(f"invalid hex color: {value}")
    return value


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="atfield",
        description="Generate animated hexagonal progress SVG (A.T. Field style)"
    )
    p.add_argument("progress", type=int, help="Progress percentage (0-100)")
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.add_argument("--count", type=int, default=100, help="Number of hexagons")
    p.add_argument("--radius", type=float, default=13, help="Hexagon radius")
    p.add_argument("--gap", type=float, default=0.08, help="Extra spacing between hexagons")
    p.add_argument("--bg", type=hex_color, default=DEFAULT_THEME.background, help="Background color")
    p.add_argument("--filled", type=hex_color, default=DEFAULT_THEME.filled, help="Filled hexagon color")
    p.add_argument("--charging", type=hex_color, default=DEFAULT_THEME.charging, help="Charging hexagon color")
    p.add_argument("--empty", type=hex_color, default=DEFAULT_THEME.empty, help="Empty hexagon color")
    p.add_argument("--stroke", type=hex_color, default=DEFAULT_THEME.stroke, help="Stroke color")
    p.add_argument("--stroke-width", type=float, default=DEFAULT_THEME.stroke_width, help="Stroke width")
    p.add_argument("--no-glow", action="store_false", dest="glow", help="Disable glow")
    p.add_argument("--seed", type=int, default=1, help="Seed for filling pattern")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not 0 <= args.progress <= 100:
        print("error: progress must be between 0 and 100", file=sys.stderr)
        return 1

    cfg = GridConfig(
        hex_count=args.count,
        hex_radius=args.radius,
        gap=args.gap,
        seed=args.seed,
    )

    theme = Theme(
        background=args.bg,
        filled=args.filled,
        charging=args.charging,
        empty=args.empty,
        stroke=args.stroke,
        stroke_width=args.stroke_width,
        glow=args.glow,
    )

    svg = generate(cfg, theme, args.progress)

    if args.output:
        with open(args.output, "w") as f:
            f.write(svg)
    else:
        print(svg)

    return 0


if __name__ == "__main__":
    sys.exit(main())
