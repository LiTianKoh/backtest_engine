from dataclasses import dataclass # A regular class that is designed to store data and state, automatically generating repetitive boilerplate code via the @dataclass decorator
from typing import Callable, Optional, TypeVar # Callable is a type hint for functions, Optional indicates that a value can be of a specified type or None, TypeVar is used for generic programming
import pandas as pd

@dataclass # Tells Python to automatically create a constructor (_init_) using the variables listed directly below it. Without this, you'd have to manually write def __init__(self, ...):
class Hypothesis:
    """
    name    : label shown in reports
    signal  : function(df) -> boolean Series, True on days the idea "fires".
              df has 'Close' (and 'Volume' if you supply volumes).
              Write it UNSHIFTED: use today's and past data only.
              The framework adds the 1-day execution delay for you.
    holding : hold N days after each trigger. None = hold while signal is True.
    """
    name: str
    signal: Callable[[pd.DataFrame], pd.Series]
    holding: Optional[int] = None # Declares an optional integer field holding. If you don't provide a number, it defaults to None

    def positions(self, df):
        trigger = self.signal(df).fillna(False).astype(float)
        if self.holding is None:
            pos = trigger
        else:
            # 1 if any trigger in the last N days (re-triggers extend the hold)
            pos = trigger.rolling(self.holding, min_periods=1).max()
        return pos.shift(1).fillna(0.0)  # shift for 1-day execution delay, fill initial NaN with 0