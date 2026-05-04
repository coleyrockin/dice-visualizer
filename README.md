# Dice Visualizer

Interactive Python visualizer for dice-sum probability spaces.

The app highlights combinations of `n` six-sided dice that add up to a target sum:

- 1 die: 1D scatter
- 2 dice: 2D grid
- 3 dice: 3D scatter
- 4+ dice: interactive 3D slice with controls for fixed remaining dice

## Requirements

- Python 3.10+
- `matplotlib`
- `numpy`

## Install locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

## Run

Open the interactive visualizer:

```bash
dice-visualizer --dice 4 --target 14
```

Print a quick probability summary without opening a GUI:

```bash
dice-visualizer --dice 4 --target 14 --summary
```

Or:

```bash
python Dice.py
```

## Test

```bash
python -m pytest
```

GitHub Actions runs tests on Python 3.10, 3.11, and 3.12, then smoke-tests the summary CLI.

## Notes

This repo was promoted from a one-file experiment into a small Python package with a CLI, validation helpers, and tests. The plotting UI is intentionally local/interactive.
