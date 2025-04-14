import os

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, Table
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

Base = declarative_base()

group_account_association = Table('group_account', Base.metadata,
                                  Column('customers_group_id', Integer, ForeignKey('customers_group.id')),
                                  Column('account_number_id', Integer, ForeignKey('bank_account.id'))
                                  )


class Period(Base):
    __tablename__ = 'period'
    id = Column(Integer, primary_key=True)
    year = Column(String, nullable=False)
    month = Column(String, nullable=False)


class CustomersGroup(Base):
    __tablename__ = 'customers_group'
    id = Column(Integer, primary_key=True)
    customers_group_name = Column(String, nullable=False)
    customers_group_kwh_meter_id = Column(String, nullable=False)
    customers_group_meter_type = Column(String, nullable=False)
    customers_group_balance = Column(Float, default=0)
    accounts = relationship('BankAccount', secondary=group_account_association, back_populates='customers_groups')

    # Pridedame ryšį su Customer klase
    customers = relationship("Customer", back_populates="group")


class CustomersGroupData(Base):
    __tablename__ = 'customers_group_data'
    id = Column(Integer, primary_key=True)
    customers_group_id = Column(Integer, ForeignKey('customers_group.id'), nullable=False)
    customers_group_previos_kwh_data = Column(Integer, nullable=True)
    customers_group_new_kwh_data = Column(Integer, nullable=True)
    period_id = Column(Integer, ForeignKey('period.id'), nullable=False)


class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)
    customer_name = Column(String, nullable=False)
    customer_kwh_meter_id = Column(String, nullable=False)
    customer_meter_type = Column(String, nullable=False)
    customer_balance = Column(Float, default=0)
    customers_group_id = Column(Integer, ForeignKey('customers_group.id'), nullable=False)
    customer_email = Column(String, nullable=True)

    # Pridedame ryšį su CustomersGroup klase
    group = relationship("CustomersGroup", back_populates="customers")


class CustomerData(Base):
    __tablename__ = 'customer_data'
    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey('period.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    customer_previos_kwh_data = Column(Integer, nullable=False)
    customer_new_kwh_data = Column(Integer, nullable=False)


class Prices(Base):
    __tablename__ = 'prices'
    id = Column(Integer, primary_key=True)
    kwh_price = Column(Float, nullable=False)
    price_service = Column(Float, nullable=False)
    price_additional = Column(Float, nullable=False)
    customers_group_id = Column(Integer, ForeignKey('customers_group.id'), nullable=False)
    period_id = Column(Integer, ForeignKey('period.id'), nullable=False)


class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customers_group_id = Column(Integer, ForeignKey('customers_group.id'), nullable=False)
    customers_group_size = Column(Integer, nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=True)
    period_id = Column(Integer, ForeignKey('period.id'), nullable=False)
    previos_kwh_data = Column(Integer, nullable=False)
    new_kwh_data = Column(Integer, nullable=False)
    kwh_difference = Column(Integer, nullable=False)
    kwh_price = Column(Float, nullable=False)
    total_kwh_price = Column(Float, nullable=False)
    price_service = Column(Float, nullable=False)
    price_additional = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    balance = Column(Float, nullable=True)
    pay = Column(Float, nullable=False)
    creation_date = Column(Date, nullable=False)


class Payments(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    paid = Column(Float, nullable=False)
    paid_date = Column(Date, nullable=False)
    customers_group_id = Column(Integer, ForeignKey('customers_group.id'), nullable=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=True)


class BankAccount(Base):
    __tablename__ = 'bank_account'
    id = Column(Integer, primary_key=True)
    account_number = Column(String, nullable=False, unique=True)
    customers_groups = relationship('CustomersGroup', secondary=group_account_association, back_populates='accounts')


# Duomenų bazės varikls
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Gauna absoliutų dabartinio failo kelią
DB_PATH = os.path.join(BASE_DIR, "dbase.db")  # Sukuria absoliutų SQLite kelią

engine = create_engine(f'sqlite:///{DB_PATH}')  # Naudoja absoliutų kelią

# Sesija
Session = sessionmaker(bind=engine)
session = Session()
