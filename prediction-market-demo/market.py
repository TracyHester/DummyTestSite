"""
market.py - Automated Market Maker for the Prediction Market Demo
=================================================================

PLAIN-ENGLISH EXPLANATION
-------------------------
A prediction market lets people trade contracts that pay out if a future event
happens. Think of it like a wager, but the *price* of the contract tells you
what the crowd believes the probability of the event is.

This module implements a **Cost-Function Market Maker (CFMM)** based on the
Logarithmic Market Scoring Rule (LMSR), invented by Robin Hanson. The idea:

- The market maker holds two virtual pools: YES shares and NO shares.
- A liquidity parameter *b* controls how sensitive the price is to trades.
  Larger b -> price moves less per trade (deeper liquidity).
- The cost function is:  C = b * ln(e^(q_yes/b) + e^(q_no/b))
  where q_yes and q_no are the outstanding quantities of each type of share.
- The current implied probability of YES is:
      p(YES) = e^(q_yes/b) / (e^(q_yes/b) + e^(q_no/b))

When an agent buys YES shares, q_yes increases, which pushes p(YES) up --
just as demand raises a price in a regular market.

NO EXTERNAL DEPENDENCIES -- uses only the Python standard library.
"""

import math
from dataclasses import dataclass, field
from typing import List


@dataclass
class Trade:
    """Record of a single trade."""
    round_num: int
    agent_name: str
    direction: str          # "BUY_YES", "BUY_NO", or "HOLD"
    shares: float
    cost: float             # how much the agent paid (or received)
    price_before: float     # implied YES probability before the trade
    price_after: float      # implied YES probability after the trade
    reasoning: str          # plain-English explanation from the agent


@dataclass
class Market:
    """
    LMSR-based automated market maker for a single binary event.

    Attributes
    ----------
    event : str
        Human-readable description of the event being traded.
    b : float
        Liquidity parameter. Higher = deeper book, smaller price impact.
    q_yes : float
        Outstanding quantity of YES shares.
    q_no : float
        Outstanding quantity of NO shares.
    trade_log : list[Trade]
        Full audit trail of every trade.
    """
    event: str
    b: float = 100.0
    q_yes: float = 0.0
    q_no: float = 0.0
    trade_log: List[Trade] = field(default_factory=list)

    # -- Pricing ----------------------------------------------------------

    def _cost(self, q_yes: float, q_no: float) -> float:
        """Hanson's LMSR cost function: b * ln(e^(q_yes/b) + e^(q_no/b))."""
        return self.b * math.log(math.exp(q_yes / self.b) + math.exp(q_no / self.b))

    def implied_probability(self) -> float:
        """
        Current market-implied probability of YES.

        Formula: p = e^(q_yes/b) / (e^(q_yes/b) + e^(q_no/b))
        """
        exp_yes = math.exp(self.q_yes / self.b)
        exp_no = math.exp(self.q_no / self.b)
        return exp_yes / (exp_yes + exp_no)

    # -- Trading -----------------------------------------------------------

    def price_for_yes_shares(self, shares: float) -> float:
        """Cost to buy `shares` YES shares at current state."""
        return self._cost(self.q_yes + shares, self.q_no) - self._cost(self.q_yes, self.q_no)

    def price_for_no_shares(self, shares: float) -> float:
        """Cost to buy `shares` NO shares at current state."""
        return self._cost(self.q_yes, self.q_no + shares) - self._cost(self.q_yes, self.q_no)

    def buy_yes(self, shares: float, agent_name: str, round_num: int, reasoning: str) -> Trade:
        """Execute a YES purchase and log it."""
        price_before = self.implied_probability()
        cost = self.price_for_yes_shares(shares)
        self.q_yes += shares
        price_after = self.implied_probability()

        trade = Trade(
            round_num=round_num,
            agent_name=agent_name,
            direction="BUY_YES",
            shares=shares,
            cost=cost,
            price_before=price_before,
            price_after=price_after,
            reasoning=reasoning,
        )
        self.trade_log.append(trade)
        return trade

    def buy_no(self, shares: float, agent_name: str, round_num: int, reasoning: str) -> Trade:
        """Execute a NO purchase and log it."""
        price_before = self.implied_probability()
        cost = self.price_for_no_shares(shares)
        self.q_no += shares
        price_after = self.implied_probability()

        trade = Trade(
            round_num=round_num,
            agent_name=agent_name,
            direction="BUY_NO",
            shares=shares,
            cost=cost,
            price_before=price_before,
            price_after=price_after,
            reasoning=reasoning,
        )
        self.trade_log.append(trade)
        return trade

    def hold(self, agent_name: str, round_num: int, reasoning: str) -> Trade:
        """Record that an agent chose not to trade this round."""
        p = self.implied_probability()
        trade = Trade(
            round_num=round_num,
            agent_name=agent_name,
            direction="HOLD",
            shares=0.0,
            cost=0.0,
            price_before=p,
            price_after=p,
            reasoning=reasoning,
        )
        self.trade_log.append(trade)
        return trade

    # -- Settlement --------------------------------------------------------

    def settle(self, outcome_yes: bool) -> dict:
        """
        Resolve the market.  Returns a dict mapping agent_name -> net P&L.

        If outcome is YES, each YES share pays $1 and each NO share pays $0.
        If outcome is NO, the reverse.
        """
        positions: dict = {}  # agent -> {"yes": shares, "no": shares, "cost": total}
        for t in self.trade_log:
            if t.direction == "HOLD":
                continue
            entry = positions.setdefault(t.agent_name, {"yes": 0.0, "no": 0.0, "cost": 0.0})
            if t.direction == "BUY_YES":
                entry["yes"] += t.shares
            elif t.direction == "BUY_NO":
                entry["no"] += t.shares
            entry["cost"] += t.cost

        pnl: dict = {}
        for agent, pos in positions.items():
            payout = pos["yes"] if outcome_yes else pos["no"]
            pnl[agent] = round(payout - pos["cost"], 2)
        return pnl
