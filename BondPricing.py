
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------------- Q1
def present_value(cash_flows, rate):
    """Present value of a list of cash flows, the first arriving in one year.
    
    present_value([10, 15, 20], 0.10) -> 36.51
    """
    # TODO
    total = 0
    for i in range(len(cash_flows)):
        year = i + 1
        cash_flow = cash_flows[i]

        value_today = cash_flow / (1+rate) ** year
        total = total + value_today
    return total
    raise NotImplementedError

print(present_value([10, 15, 20], 0.10)) 



# ---------------------------------------------------------------- Q2
def bond_price(face, coupon_rate, years, market_rate):
    """Price of a bond paying an annual coupon and repaying face at maturity.

    The final year pays the coupon AND the face value. That is the usual bug.
    bond_price(1000, 0.04, 10, 0.04) -> exactly 1000.0
    """
    # TODO
    coupon = face * coupon_rate

    cash_flows = []
    ##New array
    for year in range(years):
        cash_flows.append(coupon)
    cash_flows[-1] = cash_flows[-1] + face

    return present_value(cash_flows, market_rate)
    raise NotImplementedError
print(bond_price(1000, 0.04, 10, 0.04))


# ---------------------------------------------------------------- Q4/Q5
def annualised_return(prices):
    """Annualised return from a price series, using 252 trading days."""
    # TODO
    daily_returns = []
    for i in range(1, len(prices)):
        daily_return = prices[i]/prices[i-1]-1
        daily_returns.append(daily_return)
    average_daily_return = np.mean(daily_returns)
    return(1 + average_daily_return) ** 252 - 1

    raise NotImplementedError


def annualised_volatility(prices):
    """Annualised standard deviation of daily returns."""
    # TODO
    daily_returns = []
    for i in range(1, len(prices)):
        daily_return = prices[i] / prices[i-1]-1
        daily_returns.append(daily_return)

    return np.std(daily_returns, ddof=1) * np.sqrt(252)
    raise NotImplementedError


def beta(stock_prices, market_prices):
    """Beta of a stock against the market.

    Covariance of the two RETURN series divided by the variance of the market's.
    Computing this on prices instead of returns is a common and silent error.
    beta(spy, spy) -> 1.0
    """
    # TODO
    stock_returns = []
    market_returns = [] 
    for i in range(1,len(stock_prices)):
        stock_return = stock_prices[i] / stock_prices[i-1]-1
        market_return = market_prices[i] / market_prices[i-1]-1
        stock_returns.append(stock_return)
        market_returns.append(market_return)

    #covariance
    covariance = np.cov(stock_returns, market_returns)[0][1]
    #variance of market
    market_variance = np.var(market_returns)
    #beta = cov / var

    beta = covariance / market_variance

    return beta
    raise NotImplementedError


# ---------------------------------------------------------------- your answers
def main():
    """Everything the assignment asks you to print goes here."""
    print("Q1  present_value([10, 15, 20], 0.10) =", present_value([10, 15, 20], 0.10))
    # TODO: Q3 — three bond prices, then the price-vs-rate plot
    price_2 = bond_price(1000, 0.04, 10, 0.02,)
    price_4 = bond_price(1000, 0.04, 10, 0.04)
    price_496 = bond_price(1000, 0.04, 10, 0.0496)

    print("2% market rate", price_2)
    print("4% market rate", price_4)
    print("4.96% market rate", price_496)

    rates = []
    prices = []

    for i in range(101):
        rate = i/100
        rates.append(rate)
        prices.append(bond_price(1000,0.04,10,rate))

    ##Plot it out plt.
    plt.plot(rates,prices)
    plt.xlabel("Market Rate")
    plt.ylabel("Bond Price")
    plt.title("Bond Price vs Market Rate")
    plt.show()
    # TODO: Q4 — download your three tickers and SPY, print trading days for each
    tickers = ["AAPL","JPM","XOM","SPY"]
    data = yf.download(tickers,period ="5y",interval = "1d",auto_adjust = False)

    prices = data["Close"]
    for ticker in tickers:
        print(ticker, len(prices[ticker].dropna()))

    # TODO: Q5 — the table of return, volatility and beta
    returns = prices.pct_change().dropna()
    spy_returns = returns["SPY"]
    results = []

    for ticker in tickers:
        stock_returns = returns[ticker]
        annual_return = stock_returns.mean()*252
        annualised_volatility = stock_returns.std() * np.sqrt(252)
        beta = stock_returns.cov(spy_returns)/spy_returns.var()
        results.append([ticker,annual_return, annualised_volatility, beta])

    table = pd.DataFrame(
        results, columns=["Ticker","Return","Volatility","Beta"]
    )
    print(table)
 
    # TODO: Q6 — both rankings
    print("\n Rank by Volatility:")
    print(table.sort_values("Volatility", ascending=False)[["Ticker","Volatility"]])

    print("\n Rank by beta:")
    print(table.sort_values("Beta", ascending=False)[["Ticker","Beta"]])
    #Note: Need double brackets here.

if __name__ == "__main__":
    main()
