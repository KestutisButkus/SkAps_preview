from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

from config.config import small_windows_size
from lib.dbase import CustomersGroup, session


class NewGroupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nauja Grupė")
        self.setGeometry(*small_windows_size)
        self.setStyleSheet("background-color: #f4f7fa; border-radius: 10px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        self.name_label, self.name_input = self.create_input_field("Grupės pavadinimas:", "Įveskite grupės pavadinimą")
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.meter_id_label, self.meter_id_input = self.create_input_field("Pagrindinio skaitiklio ID:",
                                                                           "Įveskite skaitiklio ID")
        layout.addWidget(self.meter_id_label)
        layout.addWidget(self.meter_id_input)
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.meter_type_label, self.meter_type_input = self.create_input_field("Pagrindinio skaitiklio tipas:",
                                                                               "Įveskite skaitiklio tipą")
        layout.addWidget(self.meter_type_label)
        layout.addWidget(self.meter_type_input)
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.balance_label, self.balance_input = self.create_input_field("Grupės sąskaitos likutis:",
                                                                         "Įveskite sąskaitos likutį")
        layout.addWidget(self.balance_label)
        layout.addWidget(self.balance_input)
        layout.addItem(QSpacerItem(30, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.create_button = QPushButton("Sukurti")
        self.create_button.setStyleSheet("""
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
        self.create_button.clicked.connect(self.create_group)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def create_input_field(self, label_text, placeholder_text):
        label = QLabel(label_text)
        label.setFont(QFont("Arial", 9, QFont.Bold))
        label.setStyleSheet("color: #343a40;")

        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder_text)
        input_field.setStyleSheet("padding: 5px; font-size: 11px; border-radius: 5px;")
        self.apply_shadow_effect(input_field)

        return label, input_field

    def apply_shadow_effect(self, widget):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)

    def create_group(self):
        group_details = {
            "customers_group_name": self.name_input.text(),
            "customers_group_kwh_meter_id": self.meter_id_input.text(),
            "customers_group_meter_type": self.meter_type_input.text(),
            "customers_group_balance": float(self.balance_input.text())
        }

        ui_new_group(group_details)
        self.accept()


def ui_new_group(group_details):
    new_group = CustomersGroup(
        customers_group_name=group_details["customers_group_name"],
        customers_group_kwh_meter_id=group_details["customers_group_kwh_meter_id"],
        customers_group_meter_type=group_details["customers_group_meter_type"],
        customers_group_balance=group_details["customers_group_balance"]
    )
    try:
        session.add(new_group)
        session.commit()
        print(f"Nauja grupė '{group_details['customers_group_name']}' sukurta sėkmingai.")
    except Exception as e:
        print(f"Klaida įrašant duomenis į duomenų bazę: {e}")
    finally:
        session.close()
