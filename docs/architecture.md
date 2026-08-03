# Architecture

The generator is organized around three main pieces:

1. Grid layout
   - The layout is built in the `_compute_layout` function.
   - Hexagons are positioned around a central hole and filtered by distance.

2. State assignment
   - The `_assign_states` function distributes the hexagons into filled, charging, and empty states.
   - The order is determined by a pseudo-random noise function and a configurable seed.

3. SVG generation
   - `generate()` assembles the final SVG document.
   - `build_polygon_markup()` centralizes polygon markup creation so that rendering is easier to maintain and less repetitive.
