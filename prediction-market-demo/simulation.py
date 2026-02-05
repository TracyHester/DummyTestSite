"""
simulation.py - Main Entry Point for the Prediction Market Demo
================================================================

PLAIN-ENGLISH EXPLANATION
-------------------------
This script runs a complete prediction-market demonstration in your terminal.
It proceeds in the following stages:

  Round 0 -- SETUP
    We define the event being traded and set the opening odds at 50/50.

  Rounds 1 through N -- TRADING
    Each synthetic agent looks at the current market price, compares it to
    their private belief, and decides whether to buy YES shares, buy NO
    shares, or hold.  Every decision is printed with a plain-English
    justification so the class can follow the reasoning.

  SETTLEMENT
    We reveal the true outcome.  Agents who bet correctly receive $1 per
    share; agents who bet incorrectly receive nothing.  We print the
    profit-and-loss table.

Run with:
    python simulation.py

NO EXTERNAL DEPENDENCIES -- uses only the Python standard library.
"""

import copy
import random

from market import Market
from agents import DEFAULT_AGENTS

# ---- Configuration ------------------------------------------------------

EVENT = (
    "The U.S. Supreme Court will grant certiorari in at least 80 cases "
    "during its next term."
)
NUM_ROUNDS = 5
LIQUIDITY_B = 100.0          # LMSR liquidity depth
OUTCOME_YES = True            # ground truth for settlement (True = event happened)
SEED = 42                     # reproducible randomness


# ---- Helpers -------------------------------------------------------------

def banner(text: str) -> None:
    width = 72
    print()
    print("=" * width)
    print(f"  {text}")
    print("=" * width)


def print_trade(trade) -> None:
    print(f"\n  [{trade.agent_name}]")
    print(f"  Action   : {trade.direction}")
    if trade.shares:
        print(f"  Shares   : {trade.shares:.1f}")
        print(f"  Cost     : ${trade.cost:.2f}")
    print(f"  Price    : {trade.price_before:.1%} -> {trade.price_after:.1%}")
    print(f"  Reasoning: {trade.reasoning}")


# ---- Main ----------------------------------------------------------------

def main() -> None:
    random.seed(SEED)

    # --- Round 0: Setup ---------------------------------------------------
    banner("ROUND 0 -- MARKET SETUP")
    market = Market(event=EVENT, b=LIQUIDITY_B)

    print(f"\n  Event: \"{market.event}\"")
    print(f"  Market maker type    : Logarithmic Market Scoring Rule (LMSR)")
    print(f"  Liquidity parameter b: {market.b}")
    print(f"  Opening probability  : {market.implied_probability():.1%}")
    print()

    # Deep-copy so each run is independent
    agents = copy.deepcopy(DEFAULT_AGENTS)

    print("  Agents in this market:")
    for a in agents:
        print(f"    - {a.name:20s} | {a.profile}")
        print(f"      Belief: {a.belief:.0%}  Bankroll: ${a.bankroll:.0f}  "
              f"Threshold: {a.threshold:.0%}  Bet fraction: {a.bet_fraction:.0%}")

    # --- Rounds 1-N: Trading ----------------------------------------------
    for rnd in range(1, NUM_ROUNDS + 1):
        banner(f"ROUND {rnd} -- TRADING")

        # Shuffle order each round to avoid first-mover bias
        random.shuffle(agents)

        for agent in agents:
            price = market.implied_probability()
            direction, shares, reasoning = agent.decide(price)

            if direction == "BUY_YES":
                trade = market.buy_yes(shares, agent.name, rnd, reasoning)
            elif direction == "BUY_NO":
                trade = market.buy_no(shares, agent.name, rnd, reasoning)
            else:
                trade = market.hold(agent.name, rnd, reasoning)

            print_trade(trade)

        print(f"\n  >> Market price after round {rnd}: "
              f"{market.implied_probability():.1%}")

    # --- Settlement -------------------------------------------------------
    banner("SETTLEMENT")
    outcome_str = "YES -- the event occurred" if OUTCOME_YES else "NO -- the event did not occur"
    print(f"\n  True outcome: {outcome_str}")

    pnl = market.settle(OUTCOME_YES)

    print("\n  Profit & Loss")
    print("  " + "-" * 40)
    for agent_name, profit in sorted(pnl.items(), key=lambda x: -x[1]):
        marker = "+" if profit >= 0 else ""
        print(f"    {agent_name:20s}  {marker}${profit:.2f}")
    print("  " + "-" * 40)

    # Summary stats
    total_trades = sum(1 for t in market.trade_log if t.direction != "HOLD")
    total_holds = sum(1 for t in market.trade_log if t.direction == "HOLD")
    print(f"\n  Total trades executed : {total_trades}")
    print(f"  Total holds           : {total_holds}")
    print(f"  Final market price    : {market.implied_probability():.1%}")
    print(f"  Opening price was     : 50.0%")
    print()


if __name__ == "__main__":
    main()
