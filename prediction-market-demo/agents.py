"""
agents.py - Synthetic Agent Definitions
========================================

PLAIN-ENGLISH EXPLANATION
-------------------------
Each agent is a simulated market participant with:

  1. A *name* and *profile* -- a short description of their trading style,
     written so a law student can picture the person.

  2. A *private belief* -- their personal probability estimate that the event
     will happen.  This is the number they compare against the market price
     to decide whether YES contracts look cheap or expensive.

  3. A *bankroll* -- how much money they have.  They never risk more than a
     fixed fraction of their bankroll on a single trade (position sizing).

  4. A *decision rule*:
     - If the market price is significantly BELOW their belief, they BUY YES
       (they think YES is underpriced).
     - If the market price is significantly ABOVE their belief, they BUY NO
       (they think NO is underpriced, i.e., YES is overpriced).
     - If the market price is close to their belief, they HOLD.
     The word "significantly" is controlled by a *threshold* -- a minimum
     gap before the agent acts.  A cautious agent has a wide threshold; an
     aggressive one has a narrow threshold.

NO EXTERNAL DEPENDENCIES -- uses only the Python standard library.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Agent:
    """A synthetic prediction-market participant."""
    name: str
    profile: str
    belief: float           # private probability of YES (0-1)
    bankroll: float         # available cash
    threshold: float        # minimum |belief - market_price| to trade
    bet_fraction: float     # fraction of bankroll risked per trade

    def decide(self, market_price: float) -> Tuple[str, float, str]:
        """
        Decide whether to BUY_YES, BUY_NO, or HOLD.

        Returns
        -------
        direction : str
        shares : float
        reasoning : str   (plain-English explanation)
        """
        gap = self.belief - market_price

        if abs(gap) < self.threshold:
            reasoning = (
                f"{self.name} sees the market at {market_price:.1%} and privately "
                f"believes the probability is {self.belief:.1%}. The gap "
                f"({abs(gap):.1%}) is below their threshold ({self.threshold:.1%}), "
                f"so they hold -- not enough edge to justify a trade."
            )
            return ("HOLD", 0.0, reasoning)

        wager = self.bankroll * self.bet_fraction
        if wager < 0.01:
            reasoning = (
                f"{self.name} would like to trade but their bankroll "
                f"(${self.bankroll:.2f}) is too small to act."
            )
            return ("HOLD", 0.0, reasoning)

        if gap > 0:
            # Agent thinks YES is underpriced
            shares = wager  # 1 share ~= $1 at settlement
            self.bankroll -= wager
            reasoning = (
                f"{self.name} ({self.profile}) believes the true probability is "
                f"{self.belief:.1%}, but the market only prices it at "
                f"{market_price:.1%}. That is a {gap:.1%} edge. They see YES as "
                f"a bargain and spend ${wager:.2f} to buy ~{shares:.1f} YES shares."
            )
            return ("BUY_YES", shares, reasoning)
        else:
            # Agent thinks YES is overpriced -> buy NO
            shares = wager
            self.bankroll -= wager
            reasoning = (
                f"{self.name} ({self.profile}) believes the true probability is "
                f"only {self.belief:.1%}, but the market prices it at "
                f"{market_price:.1%}. That is a {abs(gap):.1%} edge toward NO. "
                f"They spend ${wager:.2f} to buy ~{shares:.1f} NO shares."
            )
            return ("BUY_NO", shares, reasoning)


# ---- Pre-built cast of characters for the classroom demo ----

DEFAULT_AGENTS = [
    Agent(
        name="Professor Caution",
        profile="risk-averse academic who insists on strong evidence",
        belief=0.60,
        bankroll=500.0,
        threshold=0.10,
        bet_fraction=0.10,
    ),
    Agent(
        name="Momentum Mo",
        profile="trend-following trader who chases the crowd",
        belief=0.55,
        bankroll=300.0,
        threshold=0.05,
        bet_fraction=0.20,
    ),
    Agent(
        name="Contrarian Carla",
        profile="journalist who bets against the consensus",
        belief=0.35,
        bankroll=400.0,
        threshold=0.08,
        bet_fraction=0.15,
    ),
    Agent(
        name="Insider Ivan",
        profile="lobbyist with a strong private signal",
        belief=0.80,
        bankroll=600.0,
        threshold=0.05,
        bet_fraction=0.25,
    ),
    Agent(
        name="Novice Nora",
        profile="first-time trader going on gut feeling",
        belief=0.50,
        bankroll=200.0,
        threshold=0.15,
        bet_fraction=0.10,
    ),
]
