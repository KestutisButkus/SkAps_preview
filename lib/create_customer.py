import re
from decimal import Decimal, InvalidOperation
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QSpacerItem, QSizePolicy, QMessageBox
from PyQt5.QtGui import QFont, QColor, QDoubleValidator
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

from config.config import small_windows_size
from lib.dbase import Customer, session
from PyQt5.QtCore import pyqtSignal


class NewCustomerDialog(QDialog):
    customer_created = pyqtSignal()  # Klientų sąrašo atnaujinimo signalas
    group_created = pyqtSignal()  # Grupės sąrašo atnaujinimo signalas

    def __init__(self, group, parent=None):
        super().__init__(parent)
        self.group = group
        self.setWindowTitle("Naujas Klientas")
        self.setGeometry(*small_windows_size)
        self.setStyleSheet("background-color: #f4f7fa; border-radius: 10px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        self.setLayout(layout)

        # 0 title
        title0 = QLabel(f"NAUJAS KLIENTAS GRUPEI:")
        title0.setFont(QFont("Arial", 10, QFont.Bold))
        title0.setStyleSheet("color: #555; background-color: transparent;")
        title0.setAlignment(Qt.AlignCenter)
        layout.addWidget(title0)

        # Pirmas title
        title1 = QLabel(f'"{group.customers_group_name}"')
        title1.setFont(QFont("Arial", 12, QFont.Bold))
        title1.setStyleSheet("color: #007bfc; background-color: transparent;")
        title1.setAlignment(Qt.AlignCenter)
        layout.addWidget(title1)

        # Antras title
        title2 = QLabel(f'Grupės ID: {group.id}')
        title2.setFont(QFont("Arial", 8, QFont.Bold))
        title2.setStyleSheet("color: #777; background-color: transparent;")
        title2.setAlignment(Qt.AlignCenter)
        layout.addWidget(title2)

        layout.addItem(QSpacerItem(50, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Įveskite kliento vardą")
        self.style_input(self.name_input, layout)

        self.meter_id_input = QLineEdit()
        self.meter_id_input.setPlaceholderText("Įveskite skaitiklio ID")
        self.style_input(self.meter_id_input, layout)

        self.meter_type_input = QLineEdit()
        self.meter_type_input.setPlaceholderText("Įveskite skaitiklio tipą")
        self.style_input(self.meter_type_input, layout)

        self.balance_input = QLineEdit()
        self.balance_input.setPlaceholderText("Įveskite balansą (pvz., 100.50)")
        # self.balance_input.setValidator(QDoubleValidator(-999999.99, 999999.99, 2))
        self.balance_input.setValidator(QDoubleValidator())
        self.style_input(self.balance_input, layout)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Įveskite el. paštą (nebūtina)")
        self.style_input(self.email_input, layout)

        layout.addItem(QSpacerItem(50, 50, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.create_button = QPushButton("Sukurti")
        self.create_button.setStyleSheet("""
            QPushButton {
                background-color: #408140;
                color: white;
                padding: 10px;
                font-size: 12px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #5cb85c;
            }
        """)
        self.create_button.clicked.connect(self.create_customer)
        layout.addWidget(self.create_button)

    def style_input(self, widget, layout):
        widget.setStyleSheet("padding: 5px; font-size: 11px; border-radius: 5px;")
        self.apply_shadow_effect(widget)
        layout.addWidget(widget)
        layout.addItem(QSpacerItem(30, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

    def apply_shadow_effect(self, widget):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)

    def create_customer(self):
        balance_text = self.balance_input.text().replace(",", ".").strip()

        # Patikrinkite, ar balansą galima konvertuoti į Decimal
        try:
            customer_balance = Decimal(balance_text) if balance_text else Decimal("0.00")
        except (ValueError, InvalidOperation):
            QMessageBox.warning(self, "Klaida", "Balansas turi būti teisingas skaičius.")
            return

        # Patikriname el. pašto adresą, jei jis įvestas
        if self.email_input.text().strip() and not self.is_valid_email(self.email_input.text().strip()):
            QMessageBox.warning(self, "Klaida", "Neteisingas el. pašto adresas.")
            return

        # Sukuriame naujo kliento duomenis
        customer_details = {
            "customer_name": self.name_input.text().strip() or str("Demo"),
            "customer_kwh_meter_id": self.meter_id_input.text().strip() or str("sn:###"),
            "customer_meter_type": self.meter_type_input.text().strip() or str("nežinoma"),
            "customer_balance": customer_balance or None,
            "customer_email": self.email_input.text().strip() or None,
            "customers_group_id": self.group.id
        }

        # Bandome įrašyti naują klientą į duomenų bazę
        try:
            new_customer = Customer(**customer_details)
            session.add(new_customer)
            session.commit()
            # QMessageBox.information(self, "Sėkminga",
            #                         f"Klientas {customer_details['customer_name']} sukurtas sėkmingai!")
            print(self, f'Klientas "{customer_details['customer_name']}" sukurtas sėkmingai!')
            self.customer_created.emit()
            self.group_created.emit()

        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Klaida", f"Klaida kuriant klientą:\n{str(e)}")

        finally:
            session.close()

        self.accept()

    def is_valid_email(self, email):
        return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email))
