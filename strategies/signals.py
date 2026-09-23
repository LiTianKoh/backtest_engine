import numpy as np
import pandas as pd

def sma_crossover(df, window = 200):
    """
    Hypothesis: If price closes above the N-SMA = uptrend, go long
    """
    sma = df["Close"].rolling(window).mean()
    raw = np.where(df["Close"] > sma, 1.0, 0.0) # 1.0 - Long SPY, 0.0 - Be in cash (flat)
    
    """
    .shift can only be used on pandas and not numpy, so have to use pd
    raw = array([113.33, 113.63, 113.71]), it has no pandas feature, so it'll output this [113.33, 113.63, 113.71]
    
    With pandas, you'll output this:
    Date
    2010-01-04    113.33
    2010-01-05    113.63
    2010-01-06    113.71
    Name: Close, dtype: float64
    """
    return pd.Series(raw, index = df.index).shift(1)

def rsi_mean_reversion(df, window = 14, oversold = 30, overbought = 70):
    """
    When RSI drops below 30, buy signal
    When RSI rises above 70, sell signal
    """
    # Step 1: Compute daily price changes
    delta = df["Close"].diff() # Different from .pct_change()

    """
    .clip() - Acts as a safety ceiling or a safety floor for your data
    """
    # Step 2: Separate gains and losses
    gain = delta.clip(lower = 0) # Accepts values at least 0. If a number is below 0, it'll set those values to 0
    loss = -delta.clip(upper = 0) # Accepts values at most 0. If a number is above 0, it'll set those values to 0

    # Step 3: Compute rolling average of the gains and losses
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()

    # Step 4: Relatie Strength = avg_gain / avg_loss
    rs = avg_gain / avg_loss

    # Step 5: RSI
    rsi = 100 - (100 / (1 + rs))
    
    # Step 6: Signal - Long when oversold, flat when overbought
    # We hold the position until it's overbought, not just for a day
    signal = pd.Series(0, index = df.index)
    position = 0
    for i in range(len(rsi)):
        if pd.isna(rsi.iloc[i]):
            signal.iloc[i] = 0
            continue
        if rsi.iloc[i] < oversold:
            position = 1
        elif rsi.iloc[i] > overbought:
            position = 0
        signal.iloc[i] = position

    return signal.shift(1)

def rate_of_change_momentum(df, window = 20):
    """
    Hypothesis: If price is higher than it was 20 days ago, momentum is positive

    ROC = (current_price - price_20_days_ago) / price_20_days_ago
    Positive ROC = upwards momentum -> Go long
    """
    roc = df["Close"].pct_change(periods = window)
    raw = np.where(roc > 0, 1, 0)
    return pd.Series(raw, index = df.index).shift(1)
