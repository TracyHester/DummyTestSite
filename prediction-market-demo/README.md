# Prediction Market Demo

A self-contained simulation of a prediction market for classroom use.
No real money, no external APIs, no dependencies beyond Python 3.8+.

## Quick Start

```bash
cd prediction-market-demo
python simulation.py
```

## What You Will See

1. **Setup** -- An event is posted (e.g., a Supreme Court certiorari
   question) and the market opens at 50/50.
2. **Trading rounds** -- Five synthetic agents evaluate the market price
   against their private beliefs and trade accordingly. Every decision is
   explained in plain English.
3. **Settlement** -- The event resolves, winners are paid, and a P&L
   table is printed.

## Files

| File            | Purpose                                      |
|-----------------|----------------------------------------------|
| `CLAUDE.md`     | Persona and rules for the Market Architect   |
| `market.py`     | LMSR automated market maker engine           |
| `agents.py`     | Synthetic agent definitions and strategies   |
| `simulation.py` | Main entry point that runs the demo          |
| `README.md`     | This file                                    |

## Customization

- **Change the event**: edit `EVENT` in `simulation.py`.
- **Change the outcome**: flip `OUTCOME_YES` to `False`.
- **Add agents**: append to `DEFAULT_AGENTS` in `agents.py`.
- **Adjust liquidity**: change `LIQUIDITY_B` in `simulation.py`.
