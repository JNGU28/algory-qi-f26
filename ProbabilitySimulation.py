"""Homework 3 starter — Algory QI Education, Fall 2026

Fill in every function marked TODO. Keep the names: the checker looks for them.
Run `python check_hw03.py` as you go.
"""
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import random 

# ---------------------------------------------------------------- Q1
def simulate_dice(trials):
    """Pick a 4-sided or 6-sided die at random, roll it, repeat.
    Return the estimated P(picked the 4-sided die | rolled a 1).
    The exact answer is 0.6. Take a seed so your result is reproducible.
    """
    # TODO
    random.seed(1223)
    rolledones = 0
    four_sided_and_one = 0
    for i in range(trials):
        die = random.choice([4,6])
        roll = random.randint(1,die)

        if roll == 1:
            rolledones += 1
            if die == 4:
                four_sided_and_one += 1
    return "Q1", four_sided_and_one/rolledones

    raise NotImplementedError
print(simulate_dice(1000))

# ---------------------------------------------------------------- Q2
def simulate_coins(trials):
    """Flip three fair coins, get paid (heads x tails). Return the mean payout.
    
    The exact answer is 1.5.
    """
    # TODO
    random.seed(1227)
    total = 0
    for i in range(trials):
        heads = 0
        for j in range(3):
            if random.choice(["H","T"]) == "H":
                heads += 1
        tails = 3 - heads
        total += heads * tails
    return total/trials
    raise NotImplementedError

#lets plot 100,1000,10,000,100,000 trials.
#q3 here.
plottrials = [100,1000,10000,100000]
estimates = []

for trial in plottrials:
    estimate = simulate_coins(trial) #note seed is set to 1227.
    estimates.append(estimate)
    print(trial,"trials:", estimate)

plt.plot(plottrials, estimates, marker = "o", label = "Simulated")
plt.axhline(1.5, color = "red", linestyle = "--", label = '1.5')
plt.xscale("log")
plt.xlabel("Number of trials")
plt.ylabel("Estimated payout")
plt.title("Simulated Expected Payout")
plt.legend()
plt.show()

#q4


# ---------------------------------------------------------------- Q5/Q6
def p_down(returns):
    """Fraction of days with a negative return. Count them yourself."""
    # TODO
    down_days = 0
    for r in returns:
        if r < 0:
            down_days += 1
    return down_days/len(returns)

    raise NotImplementedError


def p_down_given_down(returns):
    """P(tomorrow is down | today was down), counted directly from the series."""
    # TODO
    down_today = 0
    down_tommorow = 0
    for i in range(len(returns)-1):
        if returns.iloc[i] < 0:
            down_today += 1
            if returns.iloc[i+1]<0:
                down_tommorow +=1
    return down_tommorow / down_today, down_today
    raise NotImplementedError


def p_down_given_big_drop(returns, threshold=-0.02):
    """P(tomorrow is down | today fell more than the threshold).

    Also report how many days the estimate uses. A handful of days is a much
    weaker claim than thousands, and the count is what tells a reader which of
    the two this is.
    """
    # TODO
    big_drop_days = 0
    down_tommorow = 0
    for i in range(len(returns)-1):
        if returns.iloc[i] < threshold:
            big_drop_days += 1
            if returns.iloc[i+1]<0:
                down_tommorow += 1

    probability = down_tommorow/big_drop_days
    return probability, big_drop_days
    raise NotImplementedError


# ---------------------------------------------------------------- Q7
def expected_present_value(cash_flows, rate, survival_prob):
    """Present value where the company survives EACH year with survival_prob.

    Year 1 is certain. Year 2 arrives with probability survival_prob, year 3
    with survival_prob squared, and so on. This is a yearly hazard rate.

    Note this is deliberately more general than the Session 3 slide, which had a
    single shutdown event after year 1 and came to 16.98. A yearly 50% survival
    is a harsher assumption and gives 15.10. Getting 16.98 here means you applied
    the probability once instead of compounding it.
    """
    # TODO
    total = 0
    for i in range(len(cash_flows)):
        survival = survival_prob ** i 
        total += cash_flows[i] * survival / ((1+rate)**(i+1))
    return total
    raise NotImplementedError


def main():
    print("Q1  P(4-sided | rolled a 1) =", simulate_dice(100_000))
    print("Q2  expected three-coin payout =", simulate_coins(100_000))

    # TODO: Q3 — four trial counts, plot the estimate against trials
        #q3 after q2, above
    # TODO: Q4 — ten years of SPY, print trading days and mean daily return
    spy = yf.download("SPY", period="10y", interval="1d", auto_adjust=True)
    returns = spy["Close"]["SPY"].pct_change().dropna()
    print("Q4  trading days =", len(returns))
    print("Q4  mean daily return =", returns.mean())
    # TODO: Q5, Q6 — the conditional probabilities, each with its count
    #q5
    probability = p_down(returns)
    print("Q5  P(down) =", probability)

    probability, count = p_down_given_down(returns)
    print("Q5  P(down tomorrow | today down) =", probability)
    print("Q5  count =", count)

    #q6
    probability, count = p_down_given_big_drop(returns)
    print("Q6  P(down tomorrow | today down > 2%) =", probability)
    print("Q6  count =", count)
    #q7
    print("Q7  EPV =", expected_present_value([10, 10, 10], 0.10, 0.5))
    print(returns)


if __name__ == "__main__":
    main()
