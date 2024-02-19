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
    
class UncertainCashFlow(CashFlow):
    def __init__(self, amount, date: date, prob):
        super().__init__(amount, date)
        self.prob = prob

    def __str__(self):
        return f"UncertainCashFlow(amount={self.amount}, date={self.date}, prob={self.prob})"

    def __repr__(self):
        return f"UncertainCashFlow(amount={self.amount}, date={self.date}, prob={self.prob})"

    def pv(self, rate, as_of):
        return self.amount * self.prob / (1.0 + rate) ** ((self.date - as_of).days / 365.25)
    

class FXCashFlow(CashFlow):
    def __init__(self, amount, date: date, fx_rate):
        super().__init__(amount, date)
        self.fx_rate = fx_rate

    def __str__(self):
        return f"FXCashFlow(amount={self.amount}, date={self.date}, fx_rate={self.fx_rate})"

    def __repr__(self):
        return f"FXCashFlow(amount={self.amount}, date={self.date}, fx_rate={self.fx_rate})"

    def pv(self, rate, as_of):
        return self.amount * self.fx_rate / (1.0 + rate) ** ((self.date - as_of).days / 365.25)    
    
class UncertainFXCashFlow(CashFlow):
    def __init__(self, amount, date: date, fx_rate, prob):
        super().__init__(amount, date)
        self.fx_rate = fx_rate
        self.prob = prob

    def __str__(self):
        return f"UncertainFXCashFlow(amount={self.amount}, date={self.date}, fx_rate={self.fx_rate}, prob={self.prob})"

    def __repr__(self):
        return f"UncertainFXCashFlow(amount={self.amount}, date={self.date}, fx_rate={self.fx_rate}, prob={self.prob})"

    def pv(self, rate, as_of):
        return self.amount * self.fx_rate * self.prob / (1.0 + rate) ** ((self.date - as_of).days / 365.25)
    
class FXBond(Bond):
    def __init__(self, maturity, coupon, principal, fx_rate):
        super().__init__(maturity, coupon, principal)
        self.fx_rate = fx_rate

    def __str__(self):
        return f"FXBond(maturity={self.maturity}, coupon={self.coupon}, principal={self.principal}, fx_rate={self.fx_rate})"

    def __repr__(self):
        return f"FXBond(maturity={self.maturity}, coupon={self.coupon}, principal={self.principal}, fx_rate={self.fx_rate})"

    def cash_flows(self, as_of):
        cash_flows = CashFlowList()
        for year in range(as_of.year, self.maturity.year):
            cash_flows.add(FXCashFlow(self.coupon, date(year, 1, 1), self.fx_rate))
        cash_flows.add(FXCashFlow(self.coupon + self.principal, self.maturity, self.fx_rate))
        return cash_flows
    
class UncertainFXBond(FXBond):
    def __init__(self, maturity, coupon, principal, fx_rate, prob):
        super().__init__(maturity, coupon, principal, fx_rate)
        self.prob = prob

    def __str__(self):
        return f"UncertainFXBond(maturity={self.maturity}, coupon={self.coupon}, principal={self.principal}, fx_rate={self.fx_rate}, prob={self.prob})"

    def __repr__(self):
        return f"UncertainFXBond(maturity={self.maturity}, coupon={self.coupon}, principal={self.principal}, fx_rate={self.fx_rate}, prob={self.prob})"

    def cash_flows(self, as_of):
        cash_flows = CashFlowList()
        for year in range(as_of.year, self.maturity.year):
            cash_flows.add(UncertainFXCashFlow(self.coupon, date(year, 1, 1), self.fx_rate, self.prob))
        cash_flows.add(UncertainFXCashFlow(self.coupon + self.principal, self.maturity, self.fx_rate, self.prob))
        return cash_flows
    
    
if __name__ == '__main__':

    bond = Bond(date(2025, 1, 1), 5, 100)
    print(bond.price(0.05, date(2020, 1, 1)))

    print(timeit('bond.price(0.05, date(2020, 1, 1))', globals=globals(), number=10000))

    rustbond = RustBond(date(2025, 1, 1), 5, 100)
    print(rustbond.price(0.05, date(2020, 1, 1)))

    print(timeit('rustbond.price(0.05, date(2020, 1, 1))', globals=globals(), number=10000))