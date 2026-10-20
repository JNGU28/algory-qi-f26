"""Homework 4 starter — Algory QI Education, Fall 2026

The backtester is the piece worth getting right. Everything after it in the
semester assumes it works.
"""
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd


LOOKBACK = 60


# ---------------------------------------------------------------- Q1
def load_and_split(split_date="2011-09-09", prices=None, warmup=LOOKBACK):
    """Split ^SP500TR since 1990 into training and test at `split_date`.

    Training ends on the split date's close. Test begins `warmup` trading days
    BEFORE it, so the 60-day window is already full on the first day traded out
    of sample. Those overlapping days are history the strategy reads, never days
    it earns a return on. Cut the series at one date with no overlap and the
    first 60 days of the test set have no window, so the out-of-sample period
    silently starts three months late.

    September 9, 2011 is a Friday. A split date has to be a trading day, or
    "ends on that close" names a close that does not exist.

    Pass `prices` to split a series you already have, which is how the checker
    tests this without a download. Return (training, test).
    """
    # TODO
    #don't redownload
    if prices is None:
        data = yf.download("^SP500TR", 
                           start = "1990-01-01", 
                           end = "2026-10-12", 
                           interval = "1d",
                           auto_adjust= False, 
                           progress = False
                           )

    if data.empty:
        raise ValueError("No data downloaded")
    prices = data["Close"]

    if isinstance(prices, pd.DataFrame):
        prices = prices.iloc[:,0]

    prices = prices.dropna().sort_index()
    split_date =   pd.Timestamp(split_date)

    training = prices.loc[prices.index <= split_date]
    test = prices.loc[prices.index >= split_date]

    print("Training Set")
    print("Number of days:",len(training))
    print("Mean price:",round(training.mean(),2))

    print("\nTest Set")
    print("Number of days:", len(test))
    print("Mean price:", round(test.mean(),2))
    return training, test

    raise NotImplementedError


# ---------------------------------------------------------------- Q2, Q4, Q5
def always_hold(window):
    """Always invest. The control case, and the one that proves the backtester."""
    return True


def always_cash(window):
    """Never invest. Must produce exactly 0% return."""
    return False


def make_random_hold(p=0.7, seed=0):
    """Return a strategy that invests with probability p each day.

    A factory, not a plain function, because the generator has to live somewhere
    and a default argument is the wrong place: `rng=np.random.default_rng(0)` in
    a signature is evaluated once when the module loads, so every backtest in the
    session shares one advancing generator and the same backtest returns a
    different number each time you run it. Building the generator here gives one
    per strategy, so `backtest(train, make_random_hold())` is reproducible.
    """
    rng = np.random.default_rng(seed)

    def random_hold(window):
        return bool(rng.random() < p)

    return random_hold


def five_day_reversal(window):
    """The rule from class: hold unless the last 5 days were positive.

    Measure that return from the close 5 days before today to today's close,
    both of which are inside the window.
    """
    # TODO
    five_day_return = window[-1] / window[-6] - 1
    return five_day_return <= 0
    raise NotImplementedError


def my_strategy(window):
    """Your own rule. It sees only `window`, the previous LOOKBACK closes.

    It must never look at anything after that. That is the whole assignment.
    """
    # TODO
    return True
    raise NotImplementedError


# ---------------------------------------------------------------- Q3
def backtest(prices, strategy, lookback=LOOKBACK):
    """Walk forward one day at a time and apply the strategy's decision.

    The convention, stated exactly, because everything else depends on it:

        on day i, the strategy is handed prices[i - lookback + 1 : i + 1],
        the `lookback` closes ENDING WITH today's, today's included;
        if it says hold you earn prices[i + 1] / prices[i] - 1, otherwise zero.

    So i runs from lookback - 1 to len(prices) - 2. The first decision is made on
    the 60th close and the first return earned runs from the 60th close to the
    61st. Today's close is known when you decide, so withholding it throws away a
    day of information for nothing; tomorrow's close is what you are predicting,
    so reading it is the bug this whole session is about.

    Return a dict with at least:
        total_return, annualised_return, max_drawdown, fraction_invested

    Annualise by trading days, 252 a year, compounded: value ** (252 / days) - 1.

    Sanity checks before you trust it:
        always_hold  must match buy-and-hold over the days actually traded,
                     prices[-1] / prices[lookback - 1] - 1, not over the
                     whole file
        always_cash  must return exactly 0.0
    If either fails you have an off-by-one, and every number after it is fiction.
    """
    # TODO
    prices = np.asarray(prices, dtype = float)

    strategy_returns = []
    index_returns = []
    positions = []

    for i in range(lookback - 1, len(prices) - 1):
        #Strat only latest 60 closes, including today's
        window = prices[i - lookback + 1 : i + 1]
        hold = strategy(window)
        positions.append(hold)

        #calculate return from today from todays close to tommorows close.
        next_return = prices[i+1] / prices[i] - 1

        strategy_returns.append(next_return if hold else 0.0)

        index_returns.append(next_return)
    strategy_returns = np.array(strategy_returns)
    index_returns = np.array(index_returns)

    #compounding
    strategy_value = np.cumprod(1 + strategy_returns)
    index_value = np.cumprod(1 + index_returns)

    strategy_total = strategy_value[-1] - 1
    index_total = index_value[-1] - 1

    days = len(strategy_returns)

    strategy_annual = strategy_value[-1] ** (252/days) - 1
    index_annual = index_value[-1] ** (252/days) - 1

    #maximum drawdown
    equity = np.concatenate(([1.0], strategy_value))
    peaks = np.maximum.accumulate(equity)
    drawdowns = equity / peaks - 1
    max_drawdown = drawdowns.min()

    fraction_invested = np.mean(positions)

    print(f"Strategy total return: {strategy_total:.2%}")
    print(f"Strategy annualised return: {strategy_annual:.2%}")
    print(f"Index total return: {index_total:.2%}")
    print(f"Index annualised return: {index_annual:.2%}")

    #Plotting
    plt.figure(figsize=(12,6))
    plt.plot(np.concatenate(([1.0],strategy_value)), label = "Strategy")
    plt.plot(np.concatenate(([1.0],index_value)),label = "Index(buy or hold)")
    plt.xlabel("Trading days")
    plt.ylabel("Portfolio Value")
    plt.title("Strategy vs Index")
    plt.legend()
    plt.grid(True, alpha = 0.3)
    plt.tight_layout()
    plt.show()
    return{
        "total_return": float(strategy_total),
        "annualised_return": float(strategy_annual),
        "max_drawdown": float(max_drawdown),
        "fraction_invested": float(fraction_invested) 
    }
    raise NotImplementedError

def momentum_15(window):
    "invest when price is above its price 15 intervals ago"
    return bool(window[-1] > window[-16])

def momentum_30(window):
    return bool(window[-1] > window[-31])

def above_moving_average(window):
    #invest when price is above its 20 day moving average
    return bool(window[-1] > np.mean(window[-20:]))

def positive_trend_slope(window):
    #invest when fitted line through 60 closes has positive slope
    #this is the chosen one lebron james
    x = np.arange(len(window))
    slope = np.polyfit(x,window ,1)[0]
    return bool(slope > 0)

def combined_trend(window):
    "Invest when price is above its 20 day moving average + 30 day momentum == positive"
    short_average = np.mean(window[-20:])
    momentum = window[-1] / window[-31] - 1

    return bool(window[-1] > short_average and momentum > 0)

def compare_strategies(train):
    variants = [("15 day momentum", momentum_15),("30 day momentum",momentum_30),("Above moving average",above_moving_average),("60 day slope",positive_trend_slope),("Combined",combined_trend)]
    print("\n Training set comparisons")

    for name,strategy in variants:
        result = backtest(train, strategy)

        print(
            f"{name:<20}"
            f"Annualised return: {result['annualised_return']:+.2%}"
        )

# strategies = [("Always hold", always_hold),("Always cash", always_cash),("Random 70%", make_random_hold(0.7, seed=0))]
def main():
    train, test = load_and_split()
    for name, strat in [("always hold", always_hold),
                        ("always cash", always_cash),
                        ("random 70%", make_random_hold(0.7, seed=0)),
                        ("5-day reversal", five_day_reversal)]:
        r = backtest(train, strat)
        print(f"{name:<16} total {r['total_return']:+.1%}   annual {r['annualised_return']:+.2%}")
    # TODO: Q6 — print EVERY variant you try, not just the one you keep
    #Momentum, moving averages, Trend slopes, combined signaling.
    compare_strategies(train)
    #7 chosen strat : 60 day slope.
    # TODO: Q8 — run my_strategy on the test set. Once.
    train, test = load_and_split()

    result = backtest(test, positive_trend_slope)
    print("\nQ8: test set")
    print(f"Strategy total:  {result['total_return']:+.2%}")
    print(f"Strategy annual: {result['annualised_return']:+.2%}")
    print(f"Strategy maxDD:  {result['max_drawdown']:.2%}")
    print(f"Fraction invested: {result['fraction_invested']:.2%}")

    #max drawdown
    prices = np.asarray(test, dtype=float)
    index_returns = prices[LOOKBACK:] / prices[LOOKBACK-1:-1] - 1
    index_equity = np.cumprod(1 + index_returns)
    index_dd = index_equity / np.maximum.accumulate(index_equity) - 1
    print(f"Index maxDD: {index_dd.min():.2%}")

    prices = np.asarray(test, dtype=float)
    index_returns = prices[LOOKBACK:] / prices[LOOKBACK-1:-1] - 1
    index_equity  = np.cumprod(1 + index_returns)

    index_total  = index_equity[-1] - 1
    index_annual = index_equity[-1] ** (252 / len(index_returns)) - 1

    print(f"Index total:  {index_total:+.2%}")
    print(f"Index annual: {index_annual:+.2%}")
    print(f"Index maxDD:  {index_dd.min():.2%}")

    # TODO: Q9 — what does your rule say to do today?

    full = yf.download("^SP500TR", start="1990-01-01", end="2026-10-12",interval="1d", auto_adjust=False, progress=False)["Close"]
    full = full.dropna().sort_index()

    today_window = full.iloc[-LOOKBACK:]
    signal = positive_trend_slope(today_window) #the chosen strat.

    print("\nQ9: today")
    print(f"Last close date: {full.index[-1].date()}")
    print(f"Signal: {'HOLD' if signal else 'CASH'}")
    #The output is hold. 


if __name__ == "__main__":
    main()
