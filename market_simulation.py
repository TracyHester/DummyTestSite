"""
Prediction Market Simulator

A simple simulation where agents trade 'Yes' and 'No' shares on a question.
Prices adjust automatically based on demand using a logarithmic market scoring
rule (LMSR), and every trade is logged to transaction_log.csv.
"""

import csv
import math
import random
from dataclasses import dataclass, field
from datetime import datetime


# ---------------------------------------------------------------------------
# Market (Automated Market Maker using LMSR)
# ---------------------------------------------------------------------------

class Market:
    """A binary prediction market for a single yes/no question.

    Uses a simplified Logarithmic Market Scoring Rule (LMSR):
      - The market tracks the number of outstanding Yes and No shares.
      - The price of Yes shares is:  e^(yes_shares/b) / (e^(yes_shares/b) + e^(no_shares/b))
      - 'b' (liquidity) controls how sensitive the price is to trades.
        Smaller b → prices move faster.
    """

    def __init__(self, question: str, liquidity: float = 10.0):
        self.question = question
        self.liquidity = liquidity
        self.yes_shares_sold = 0.0
        self.no_shares_sold = 0.0
        self.trade_counter = 0

    def _cost_function(self, yes_qty: float, no_qty: float) -> float:
        """LMSR cost function: C = b * ln(e^(yes/b) + e^(no/b))"""
        b = self.liquidity
        return b * math.log(math.exp(yes_qty / b) + math.exp(no_qty / b))

    @property
    def yes_price(self) -> float:
        b = self.liquidity
        e_yes = math.exp(self.yes_shares_sold / b)
        e_no = math.exp(self.no_shares_sold / b)
        return e_yes / (e_yes + e_no)

    @property
    def no_price(self) -> float:
        return 1.0 - self.yes_price

    def cost_to_buy(self, side: str, quantity: int) -> float:
        """Return the dollar cost to buy `quantity` shares of `side`."""
        if side not in ("Yes", "No"):
            raise ValueError("side must be 'Yes' or 'No'")

        old_cost = self._cost_function(self.yes_shares_sold, self.no_shares_sold)

        if side == "Yes":
            new_cost = self._cost_function(self.yes_shares_sold + quantity, self.no_shares_sold)
        else:
            new_cost = self._cost_function(self.yes_shares_sold, self.no_shares_sold + quantity)

        return new_cost - old_cost

    def execute_buy(self, side: str, quantity: int) -> float:
        """Record a purchase and return the cost charged."""
        cost = self.cost_to_buy(side, quantity)

        if side == "Yes":
            self.yes_shares_sold += quantity
        else:
            self.no_shares_sold += quantity

        self.trade_counter += 1
        return cost


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

@dataclass
class Agent:
    name: str
    cash: float = 1000.0
    yes_shares: int = 0
    no_shares: int = 0

    def buy(self, market: Market, side: str, quantity: int) -> dict | None:
        """Attempt to buy shares. Returns a trade record dict, or None if
        the agent cannot afford the trade."""
        cost = market.cost_to_buy(side, quantity)

        if cost > self.cash:
            return None  # not enough cash

        actual_cost = market.execute_buy(side, quantity)
        self.cash -= actual_cost

        if side == "Yes":
            self.yes_shares += quantity
        else:
            self.no_shares += quantity

        return {
            "trade_id": market.trade_counter,
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "side": side,
            "quantity": quantity,
            "cost": round(actual_cost, 4),
            "yes_price_after": round(market.yes_price, 4),
            "no_price_after": round(market.no_price, 4),
            "agent_cash_remaining": round(self.cash, 4),
        }


# ---------------------------------------------------------------------------
# Transaction logger
# ---------------------------------------------------------------------------

LOG_FILE = "transaction_log.csv"
LOG_FIELDS = [
    "trade_id",
    "timestamp",
    "agent",
    "side",
    "quantity",
    "cost",
    "yes_price_after",
    "no_price_after",
    "agent_cash_remaining",
]


def write_log(trades: list[dict]) -> None:
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        writer.writeheader()
        writer.writerows(trades)


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

def run_simulation(
    question: str = "Will it rain tomorrow?",
    num_agents: int = 5,
    rounds: int = 10,
    liquidity: float = 10.0,
    seed: int | None = 42,
) -> None:
    """Run a simple prediction market simulation.

    Each round, every agent randomly decides to buy 1-3 Yes or No shares
    (with a slight bias reflecting a private 'belief').
    """
    if seed is not None:
        random.seed(seed)

    market = Market(question=question, liquidity=liquidity)
    agents = [Agent(name=f"Agent_{i+1}") for i in range(num_agents)]

    # Give each agent a private belief (probability they think Yes is correct).
    beliefs = {agent.name: random.uniform(0.2, 0.8) for agent in agents}

    all_trades: list[dict] = []

    print(f"{'='*60}")
    print(f"PREDICTION MARKET SIMULATION")
    print(f"Question : {question}")
    print(f"Agents   : {num_agents}  (each starts with $1,000)")
    print(f"Rounds   : {rounds}")
    print(f"Liquidity: {liquidity}")
    print(f"{'='*60}\n")

    print(f"Starting prices  ->  Yes: ${market.yes_price:.4f}   No: ${market.no_price:.4f}\n")

    for r in range(1, rounds + 1):
        print(f"--- Round {r} ---")
        for agent in agents:
            # Decide side based on belief vs current price
            belief = beliefs[agent.name]
            if belief > market.yes_price:
                side = "Yes"
            else:
                side = "No"

            quantity = random.randint(1, 3)
            trade = agent.buy(market, side, quantity)

            if trade:
                all_trades.append(trade)
                print(
                    f"  {agent.name} buys {quantity} {side:3s} for ${trade['cost']:.4f}  "
                    f"| Yes price: ${market.yes_price:.4f}  "
                    f"| Cash left: ${agent.cash:.2f}"
                )
            else:
                print(f"  {agent.name} cannot afford {quantity} {side} shares — skipped")

        print()

    # Final summary
    print(f"{'='*60}")
    print("FINAL STATE")
    print(f"{'='*60}")
    print(f"Yes price: ${market.yes_price:.4f}   No price: ${market.no_price:.4f}\n")

    print(f"{'Agent':<12} {'Cash':>10} {'Yes Shares':>12} {'No Shares':>11}")
    print("-" * 47)
    for agent in agents:
        print(f"{agent.name:<12} ${agent.cash:>9.2f} {agent.yes_shares:>12} {agent.no_shares:>11}")

    print(f"\nTotal trades: {len(all_trades)}")

    # Write audit log
    write_log(all_trades)
    print(f"Transaction log saved to {LOG_FILE}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_simulation()
