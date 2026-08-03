# Usage

This page shows the most common command-line examples for A.T. Field Status.

## Basic generation

```bash
atfield 42 -o progress.svg
```

## Custom colors

```bash
atfield 75 \
  --filled "#00ff88" \
  --charging "#ff6600" \
  --empty "#111111"
```

## Disable glow

```bash
atfield 50 --no-glow
```

## Related notes

- The output is deterministic when the same seed is used.
- The generator is suitable for GitHub READMEs, dashboards, and static assets.
