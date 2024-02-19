from datetime import date, timedelta
from timeit import timeit
from rustifin import Bond as RustBond

class CashFlow:
    def __init__(self, amount, date: date):
        self.amount = amount
        self.date = date

    def __str__(self):
        return f"CashFlow(amount={self.amount}, date={self.date})"

    def __repr__(self):
        return f"CashFlow(amount={self.amount}, date={self.date})"

    def pv(self, rate, as_of):
        year_frac = (self.date - as_of).days / 365.25
        return self.amount / (1.0 + rate) ** year_frac

class CashFlowList:
    def __init__(self):
        self.cash_flows = []

    def add(self, cash_flow):
        self.cash_flows.append(cash_flow)

    def __str__(self):
        return f"CashFlowList({', '.join(map(str, self.cash_flows))})"

    def __repr__(self):
        return f"CashFlowList({', '.join(map(str, self.cash_flows))})"

    def npv(self, rate, as_of):
        return sum(cash_flow.pv(rate, as_of) for cash_flow in self.cash_flows)

class Bond:
    def __init__(self, maturity, coupon, principal):
        self.maturity = maturity
        self.coupon = coupon
        self.principal = principal

    def __str__(self):
        return f"Bond(maturity={self.maturity}, coupon={self.coupon}, principal={self.principal})"

    def __repr__(self):
        return f"Bond(maturity={self.maturity}, coupon={self.coupon}, principal={self.principal})"

    def cash_flows(self, as_of):
        cash_flows = CashFlowList()
        for year in range(as_of.year, self.maturity.year):
            cash_flows.add(CashFlow(self.coupon, date(year, 1, 1)))
        cash_flows.add(CashFlow(self.coupon + self.principal, self.maturity))
        return cash_flows

    def price(self, rate, as_of):
        return self.cash_flows(as_of).npv(rate, as_of)
    
if __name__ == '__main__':

    bond = Bond(date(2025, 1, 1), 5, 100)
    print(bond.price(0.05, date(2020, 1, 1)))

    print(timeit('bond.price(0.05, date(2020, 1, 1))', globals=globals(), number=10000))

    rustbond = RustBond(date(2025, 1, 1), 5, 100)
    print(rustbond.price(0.05, date(2020, 1, 1)))

    print(timeit('rustbond.price(0.05, date(2020, 1, 1))', globals=globals(), number=10000))