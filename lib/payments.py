from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel, QLineEdit, QWidget, QMessageBox
from datetime import date
from decimal import Decimal

from config.config import small_windows_size
from lib.dbase import CustomersGroup, Payments, session, Customer

from PyQt5.QtCore import pyqtSignal


class PaymentGUI(QWidget):
    payment_added = pyqtSignal()

    def __init__(self, customer_id=None, group_id=None):
        super().__init__()

        self.customer_id = customer_id
        self.group_id = group_id

        self.setWindowTitle("Mokėjimai")
        self.setGeometry(*small_windows_size)

        layout = QVBoxLayout()

        self.info_label = QLabel()
        layout.addWidget(self.info_label)

        self.amount_label = QLabel("Įveskite sumokėtą sumą:")
        layout.addWidget(self.amount_label)

        self.amount_input = QLineEdit()
        layout.addWidget(self.amount_input)

        self.submit_button = QPushButton("Patvirtinti")
        self.submit_button.clicked.connect(self.submit_payment)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

        self.update_info_label()

    def update_info_label(self):
        self.group = session.query(CustomersGroup).filter_by(id=self.group_id).first()
        if self.customer_id:
            self.customer = session.query(Customer).filter_by(id=self.customer_id).first()
            if self.customer:
                self.info_label.setText(
                    f"Mokėjmas bus priskitras grupės: <span style='font-size:12px; color:#3366FF; font-weight:bold;'><br>"
                    f"{self.group.customers_group_name}</span> (ID:  {self.group.id})<br>"
                    f"Klientui: <span style='font-size:16px; color:#44AA55; font-weight:bold;'><br>"
                    f"{self.customer.customer_name}</span>  (ID: {self.customer.id})")
        else:
            self.customer = None  # išvalome, jei nepasirinktas
            self.info_label.setText(
                f"Mokėjimas bus priskirtas grupei: <span style='font-size:16px; color:#3366FF; font-weight:bold;'><br>"
                f"{self.group.customers_group_name}</span> (ID:  {self.group.id})")

    def submit_payment(self):
        paid = Decimal(self.amount_input.text().replace(',', '.'))

        if paid == 0:
            print("Mokėjimo įvedimas atšauktas.")
            return

        paid_date = date.today()

        if self.customer and self.group:
            insert_payment(paid, paid_date, self.customer.id, self.group.id)
            update_customer_balance(self.customer.id, paid)
            message_text = f'Grupės "{self.group.customers_group_name}" Klientui "{self.customer.customer_name}"\nMokėjimas sėkmingai įvestas ir balansas atnaujintas!'
        elif self.group:
            insert_payment(paid, paid_date, None, self.group.id)
            update_customers_group_balance(self.group.id, paid)
            message_text = f'Grupei "{self.group.customers_group_name}"\nMokėjimas sėkmingai įvestas ir balansas atnaujintas!'
        else:
            message_text = "Nenurodytas nei kliento ID, nei grupės ID."

        # Emituojame signalą po mokėjimo pridėjimo
        self.payment_added.emit()

        msg_box = QMessageBox(QMessageBox.Information, "Sėkmė", message_text, QMessageBox.Ok, self)
        msg_box.buttonClicked.connect(self.close)
        msg_box.exec_()


def insert_payment(paid, paid_date, customer_id, customers_group_id):
    add_payment = Payments(
        paid=paid,
        paid_date=paid_date,
        customer_id=customer_id,
        customers_group_id=customers_group_id
    )
    session.add(add_payment)
    session.commit()
    print("Duomenys sėkmingai įterpti!")


def update_customer_balance(customer_id, sum_data):
    customer = session.query(Customer).filter_by(id=customer_id).first()
    if customer:
        customer_balance_decimal = Decimal(str(customer.customer_balance)) if customer.customer_balance else Decimal(
            "0")
        sum_data_decimal = Decimal(str(sum_data))
        customer.customer_balance = customer_balance_decimal + sum_data_decimal
        session.commit()
        print("Kliento balansas sėkmingai atnaujintas!")
    else:
        print("Klientas nerastas.")


def update_customers_group_balance(customers_group_id, sum_data):
    customers_group = session.query(CustomersGroup).filter_by(id=customers_group_id).first()
    if customers_group:
        customers_group_decimal = Decimal(
            str(customers_group.customers_group_balance)) if customers_group.customers_group_balance else Decimal("0")
        sum_data_decimal = Decimal(str(sum_data))
        customers_group.customers_group_balance = customers_group_decimal + sum_data_decimal
        session.commit()
        print("Grupės balansas sėkmingai atnaujintas!")
    else:
        print("Grupė nerasta.")
