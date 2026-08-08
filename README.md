# melvor-calc

A command-line calculator that estimates how many actions and how much real
time are needed to reach a target skill level in Melvor Idle, given your
current progress and the effective XP/time of one action.

## Requirements

- Python 3.12 or newer.

## Setup

```
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
pip install -e ".[dev]"
```

## Running

```
python -m melvor_calc
```

The tool asks a short series of questions and prints one result. It performs
one calculation per run.

### Input semantics

All entered values must already be the **effective, post-modifier** values
you actually observe in-game:

- **XP gained per completed action** — the real skill XP awarded by one
  completed action, after any equipment, mastery, or other modifiers.
- **Time per action, in seconds** — the real duration of one completed
  action, after any interval modifiers.

The calculator does not know about specific skills, actions, equipment, or
mastery — it only works with these two effective numbers plus your current
progress and target level.

### Current progress

Current XP may be entered with or without thousands-separating commas
(`13034431` or `13,034,431`); both are accepted.

You can describe your current progress two ways:

1. **Exact current XP** (recommended) — your exact cumulative skill XP.
   This gives an accurate result.
2. **Current level only** — for convenience. This assumes you have exactly
   the minimum XP for that level (0% progress into it), which is a
   conservative estimate: it can overstate remaining XP/actions/time, but
   will not understate them. The output clearly flags this assumption.

### Target level

"Reach level N" means accumulating the minimum cumulative XP shown for level
N in-game — not completing level N or reaching level N+1.

Supported levels: **1 through 120**.

### Rounding

Required actions are always rounded up to a whole number — a fractional
action still counts as a full action, and total time is based on that
rounded count (not on fractional-action time).

Displayed XP/hour, by contrast, is rounded to the nearest whole number
(half-up) rather than rounded up — it's a display figure, not an action
count, so there's no need to bias it upward.

## Example

```
$ python -m melvor_calc
Melvor Idle Training Calculator

How do you want to enter current progress?
  1. Exact current XP (recommended)
  2. Current level only
Choice: 1
Current cumulative XP: 1000
Target level (1-120): 10
XP gained per completed action: 100
Time per action in seconds: 2.5

Target XP:       1,154
Current XP:      1,000
Remaining XP:    154
XP per hour:     144,000
Actions needed:  2
Estimated time:  5 seconds
```

Invalid input (e.g. a negative XP value, an out-of-range level, or `NaN`) is
rejected with a specific message, and only that field is re-prompted — the
rest of your answers are kept. `Ctrl+C` or end-of-file cancels cleanly with
no traceback (exit code `1`).

## Testing

```
pip install -e ".[dev]"
pytest
```
