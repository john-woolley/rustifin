use chrono::{Datelike, NaiveDate};
use pyo3::prelude::*;
use pyo3::types::PyDate;
use pyo3::types::PyDateAccess;
use std::fmt::Formatter;
use std::borrow::Borrow;

#[pyclass]
struct Date {
    day: u8,
    month: u8,
    year: i32,
}

impl std::fmt::Display for Date {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Date(day={}, month={}, year={})", self.day, self.month, self.year)
    }
}

#[pymethods]
impl Date {
    #[new]
    fn new(day: u8, month: u8, year: i32) -> Self {
        Date { day, month, year }
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(format!("Date(day={}, month={}, year={})", self.day, self.month, self.year))
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("Date(day={}, month={}, year={})", self.day, self.month, self.year))
    }

    fn clone(&self) -> Self {
        Date { day: self.day, month: self.month, year: self.year }
    }
}

impl FromPyObject<'_> for Date {
    fn extract(ob: &PyAny) -> PyResult<Self> {
        let date = ob.downcast::<PyDate>()?;
        Ok(Date {
            day: date.get_day(),
            month: date.get_month(),
            year: date.get_year(),
        })
    }
}

#[pyclass]
struct CashFlow {
    amount: f64,
    date: Date
}

#[pymethods]
impl CashFlow {

    #[new]
    fn new(amount: f64, date: Date )-> Self {
        CashFlow { amount, date }
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(format!("CashFlow(amount={}, date={})", self.amount, self.date))
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("CashFlow(amount={}, date={})", self.amount, self.date))
    }

    fn amount(&self) -> f64 {
        self.amount
    }

    fn date(&self) -> Date {
        Date::new(self.date.day, self.date.month, self.date.year)
    }

    fn pv(&self, rate: f64, as_of: Date) -> f64 {
        let self_date = NaiveDate::from_ymd_opt(self.date.year, self.date.month.into(), self.date.day.into()).unwrap();
        let as_of_date = NaiveDate::from_ymd_opt(as_of.year, as_of.month.into(), as_of.day.into()).unwrap();

        let year_frac = (self_date - as_of_date).num_days() as f64 / 365.25;
        self.amount / (1.0 + rate).powf(year_frac)
    }
}

impl FromPyObject<'_> for CashFlow {
    fn extract(ob: &PyAny) -> PyResult<Self> {
        let amount = ob.getattr("amount")?.extract::<f64>()?;
        let date = ob.getattr("date")?.extract::<Date>()?;
        Ok(CashFlow { amount, date })
    }
}

impl std::fmt::Display for CashFlow {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "CashFlow(amount={}, date={})", self.amount, self.date)
    }
}

#[pyclass]
struct CashFlowList {
    cash_flows: Vec<CashFlow>
}

#[pymethods]
impl CashFlowList {
    #[new]
    fn new() -> Self {
        CashFlowList { cash_flows: Vec::new() }
    }

    fn add(&mut self, cash_flow: CashFlow) -> PyResult<()> {
        self.cash_flows.push(cash_flow);
        Ok(())
    }

    fn __str__(&self) -> PyResult<String> {
        let mut result = String::from("CashFlowList(");
        for cash_flow in &self.cash_flows {
            result.push_str(&format!("{}, ", cash_flow));
        }
        result.push(')');
        Ok(result)
    }

    fn __repr__(&self) -> PyResult<String> {
        let mut result = String::from("CashFlowList(");
        for cash_flow in &self.cash_flows {
            result.push_str(&format!("{}, ", cash_flow));
        }
        result.push(')');
        Ok(result)
    }

    fn npv(&self, rate: f64, asof: Date) -> f64 {
        let mut npv = 0.0;
        for cash_flow in &self.cash_flows {
            npv += cash_flow.pv(rate, asof.clone());
        }
        npv
    }
}


impl std::fmt::Display for CashFlowList {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "CashFlowList(")
    }
}

#[pyclass]
struct Bond {
    maturity: Date,
    coupon: f64,
    principal: f64
}

#[pymethods]
impl Bond {
    #[new]
    fn new(maturity: Date, coupon: f64, principal: f64) -> Self {
        Bond { maturity, coupon, principal }
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(format!("Bond(maturity={}, coupon={}, principal={})", self.maturity, self.coupon, self.principal))
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("Bond(maturity={}, coupon={}, principal={})", self.maturity, self.coupon, self.principal))
    }

    fn cash_flows(&self, as_of: Date) -> CashFlowList {
        let mut cash_flows = CashFlowList::new();
        for year in as_of.borrow().year..self.maturity.year {
            cash_flows.add(CashFlow::new(self.coupon, Date::new(1, 1, year)));
        }
        cash_flows.add(CashFlow::new(self.coupon + self.principal, self.maturity.clone()));
        cash_flows
    }

    fn price(&self, rate: f64, as_of: Date) -> f64 {
        self.cash_flows(as_of.clone()).npv(rate, as_of)
    }
}



/// A Python module implemented in Rust.
#[pymodule]
fn rustifin(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<CashFlow>()?;
    m.add_class::<Date>()?;
    m.add_class::<CashFlowList>()?;
    m.add_class::<Bond>()?;

    Ok(())
}
