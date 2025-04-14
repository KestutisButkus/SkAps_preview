from datetime import date, timedelta

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QHBoxLayout
from PyQt5.QtGui import QFont

from config.config import small_windows_size
from forms.customer_html import save_invoice_html
from forms.customer_img2 import save_invoice_image
from forms.customer_txt import save_invoice_txt
from lib.create_group_invoices import print_group_orders_all_customers
from lib.dbase import Period, Session, session, Customer, Orders, CustomersGroup, BankAccount, group_account_association


class InvoiceGUI(QWidget):
    def __init__(self, group):
        super().__init__()

        self.group = group
        self.session = Session()

        self.setWindowTitle("Sąskaitų generavimas")
        self.setGeometry(*small_windows_size)
        self.setStyleSheet("background-color: #f4f7fa; border-radius: 10px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        self.group_label = QLabel(f"Grupė: {group.customers_group_name} ID: {group.id}")
        self.group_label.setStyleSheet("font-size: 14px; color: #343a40;")
        layout.addWidget(self.group_label)

        self.period_label = QLabel("Pasirinkite laikotarpį:")
        self.period_label.setFont(QFont("Arial", 9, QFont.Bold))
        self.period_label.setStyleSheet("color: #343a40;")
        layout.addWidget(self.period_label)

        period_layout = QHBoxLayout()
        period_layout.setSpacing(20)  # Nustato tarpus tarp metų, mėnesių pasirinkimo ir etiketės

        self.year_dropdown = QComboBox(self)
        period_layout.addWidget(self.year_dropdown)

        self.month_dropdown = QComboBox(self)
        period_layout.addWidget(self.month_dropdown)

        self.period_id_label = QLabel("Periodo ID: Nėra")
        self.period_id_label.setStyleSheet("color: #007bfc; background-color: transparent;")
        period_layout.addWidget(self.period_id_label)
        layout.addLayout(period_layout)

        # Pridedame signalą periodų pasirinkimo keitimui
        try:
            self.connect_signals()
            self.populate_periods()
        except Exception as e:
            print(f"Klaida __init__ metode: {e}")

        buttons_layout = QHBoxLayout()  # Inicijuojame QHBoxLayout kaip objektą

        self.generate_button1 = QPushButton("Generuoti klientų sąskaitas")
        self.generate_button1.setStyleSheet("""
            QPushButton {
                background-color: #007bfc;
                color: white;
                padding: 10px;
                font-size: 12px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.generate_button1.clicked.connect(lambda: self.generate_invoice(self.group, self.get_period_id()))
        buttons_layout.addWidget(self.generate_button1)

        self.generate_button2 = QPushButton("Generuoti sąskaitų sąrašą")
        self.generate_button2.setStyleSheet("""
            QPushButton {
                background-color: #007bfc;
                color: white;
                padding: 10px;
                font-size: 12px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.generate_button2.clicked.connect(
            lambda: print_group_orders_all_customers(self.group.id, self.get_period_id()))
        buttons_layout.addWidget(self.generate_button2)

        layout.addLayout(buttons_layout)  # Pridedame buttons_layout į pagrindinį layout

        self.setLayout(layout)

    def populate_periods(self):
        """Užpildo metų ir mėnesių pasirinkimo laukus iš duomenų bazės."""
        print("bandome ištraukti periodus")
        self.year_dropdown.clear()
        self.month_dropdown.clear()

        try:
            periods = self.session.query(Period).all()
            years = sorted(list(set(period.year for period in periods)))
            print(years)
            self.year_dropdown.addItems(map(str, years))
            self.populate_months_by_year(
                years[0] if years else None)  # Atnaujiname mėnesius su pirmais metais (jei yra)
        except Exception as e:
            print(f"Klaida gaunant periodų sąrašą: {e}")

    def populate_months_by_year(self, year):
        """Užpildo mėnesių pasirinkimo lauką pagal pasirinktus metus."""
        self.month_dropdown.clear()
        if year is not None:
            try:
                months = sorted(
                    list(set(period.month for period in self.session.query(Period).filter_by(year=year).all())))
                print(f"Mėnesiai {year} metais: {months}")
                self.month_dropdown.addItems(map(str, months))
            except Exception as e:
                print(f"Klaida gaunant mėnesių sąrašą pagal metus: {e}")

    def get_period_id(self):
        """Gauna periodo ID pagal pasirinktus metus ir mėnesį."""
        year = self.year_dropdown.currentText()
        month = self.month_dropdown.currentText()
        period = self.session.query(Period).filter_by(year=year, month=month).first()
        if period:
            return period.id
        else:
            return None

    def check_and_update_period_price(self):
        """Tikrina ir atnaujina periodo kainą, kai pasikeičia pasirinktas periodas."""
        period_id = self.get_period_id()
        if period_id is not None:
            self.period_id_label.setText(f"Periodo ID: {period_id}")
        else:
            self.period_id_label.setText("Periodo ID: Nėra")

    def connect_signals(self):
        """Prijungia signalus prie periodo pasirinkimo laukų."""
        try:
            self.year_dropdown.currentIndexChanged.connect(self.update_months_by_year)
            self.month_dropdown.currentIndexChanged.connect(self.check_and_update_period_price)
        except Exception as e:
            print(f"Klaida connect_signals metode: {e}")

    def update_months_by_year(self):
        """Atnaujina mėnesių sąrašą, kai pasikeičia pasirinkti metai."""
        selected_year = self.year_dropdown.currentText()
        if selected_year:
            self.populate_months_by_year(int(selected_year))  # Konvertuojame į int, nes pasirinktas tekstas yra string

    def generate_invoice(self, group, period_id):
        group_id = group.id

        if not period_id:
            print("Periodo ID nerastas.")
            return

        customers = session.query(Customer).filter(Customer.customers_group_id == group_id).all()
        get_bank_account = session.query(BankAccount).join(group_account_association).filter(
            group_account_association.c.customers_group_id == group_id).first()
        bank_account = get_bank_account.account_number
        bank_text = "Banko sąskaita apmokėjimui:"

        for customer in customers:
            customer_id = customer.id

            # Užklausa duomenims ištraukti
            customer_data = session.query(
                Customer.customer_name,
                Customer.customer_kwh_meter_id,
                Customer.customer_meter_type,
                Orders.previos_kwh_data,
                Orders.new_kwh_data,
                CustomersGroup.customers_group_name,
                Orders.balance,
                Orders.kwh_price,
                Orders.total_kwh_price,
                Orders.price_service,
                Orders.price_additional,
                Orders.total_price,
                Orders.pay,
                Orders.id,
                Period.year,
                Period.month,
                Orders.kwh_difference
            ).join(Customer, Orders.customer_id == Customer.id
                   ).join(CustomersGroup, Orders.customers_group_id == CustomersGroup.id
                          ).join(Period, Orders.period_id == Period.id
                                 ).filter(Orders.customer_id == customer_id, Orders.period_id == period_id).all()

            # Tikriname, ar yra duomenų
            if customer_data:
                for data in customer_data:
                    pay = data[12]
                    if pay <= 0:
                        pay = 0

                    invoice_date = date.today()
                    payment_due_date = invoice_date + timedelta(days=14)

                    # Paruošiame duomenis HTML, PNG ir TXT failams
                    invoice_data = {
                        'invoice_number': data[13],
                        'period': f"{data[14]}-{data[15]}",
                        'group': data[5],
                        'customer': data[0],
                        'meter_id': data[1],
                        'meter_type': data[2],
                        'kwh_from': data[3],
                        'kwh_to': data[4],
                        'kwh_total': data[16],
                        'electricity_price': data[7],
                        'total_kwh_price': data[8],
                        'service_price': data[9],
                        'additional_price': data[10],
                        'total_price': data[11],
                        'balance': data[6],
                        'pay': pay,
                        'invoice_date': invoice_date,
                        'due_date': payment_due_date,
                        'bank_text': bank_text,
                        'bank': bank_account
                    }

                    save_invoice_html(invoice_data)
                    save_invoice_txt(invoice_data)
                    save_invoice_image(invoice_data)
            else:
                print(f"Nerasta sąskaitos duomenų klientui {customer.customer_name}. Gal dar nesuformavote sąskaitos?")
