# Architecture

The generator is organized around three main pieces.

## 1. Grid layout

- The layout is built in `_compute_layout`.
- Hexagons are positioned around a central hole and filtered by distance.

## 2. State assignment

- `_assign_states` distributes hexagons into filled, charging, and empty states.
- The order is determined by a pseudo-random noise function and a configurable seed.

## 3. SVG generation

- `generate()` assembles the final SVG document.
- `build_polygon_markup()` centralizes polygon markup creation so rendering stays easier to maintain and less repetitive.

## Implementation notes

- The current structure favors deterministic output.
- The SVG is designed to be self-contained, so it can be embedded without extra runtime dependencies.
