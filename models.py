from sqlalchemy import Column, Float, String, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Companies(Base):
    __tablename__ = 'companies'

    ticker = Column(String(30), primary_key=True)
    name = Column(String(100))
    sector = Column(String(100))


class Financial(Base):
    __tablename__ = 'financial'

    ticker = Column(String(100), primary_key=True)
    ebitda = Column(Float)
    sales = Column(Float)
    net_profit = Column(Float)
    market_price = Column(Float)
    net_debt = Column(Float)
    assets = Column(Float)
    equity = Column(Float)
    cash_equivalents = Column(Float)
    liabilities = Column(Float)


INDICATORS = {
    "ND/EBITDA": func.round(Financial.net_debt / Financial.ebitda, 2),
    "ROE": func.round(Financial.net_profit / Financial.equity, 2),
    "ROA": func.round(Financial.net_profit / Financial.assets, 2)
}
