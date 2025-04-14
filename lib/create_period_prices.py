from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QPushButton, QLineEdit, \
    QGraphicsDropShadowEffect
from _decimal import Decimal

from config.config import small_windows_size
from lib.create_period import NewPeriodDialog
from lib.dbase import session, Period, Prices


def show_message(title, message):
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.exec_()


class NewPeriodPrices(QDialog):
    def __init__(self, group_id, group_name):
        super().__init__()
        self.period_id = None
        self.session = session
        self.group_id = group_id
        self.group_name = group_name
        self.setWindowTitle("Naujos Kainos")
        self.setGeometry(*small_windows_size)
        self.setStyleSheet("background-color: #f4f7fa; border-radius: 10px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        # Grupės pavadinimas ir ID lango viršuje
        self.group_info_label = QLabel(f"Grupė: {self.group_name} (ID: {self.group_id})")
        self.group_info_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.group_info_label.setStyleSheet("color: #343a40;")
        layout.addWidget(self.group_info_label)

        # Periodo pasirinkimas (metai ir mėnesiai atskirai)
        period_layout = QHBoxLayout()

        self.year_dropdown = QComboBox(self)
        period_layout.addWidget(self.year_dropdown)

        self.month_dropdown = QComboBox(self)
        period_layout.addWidget(self.month_dropdown)

        self.period_id_label = QLabel("Periodo ID: Nėra")
        self.period_id_label.setFont(QFont("Arial", 9, QFont.Bold))
        self.period_id_label.setStyleSheet("color: #343a40;")
        period_layout.addWidget(self.period_id_label)

        self.create_period_button = QPushButton("Sukurti periodą")
        self.create_period_button.setStyleSheet("""
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
        self.create_period_button.clicked.connect(self.open_new_period_dialog)
        period_layout.addWidget(self.create_period_button)

        layout.addLayout(period_layout)

        self.period_price_label = QLabel("\n\n\n")
        self.period_price_label.setStyleSheet("background-color: transparent;")
        layout.addWidget(self.period_price_label)

        prices_layout = QVBoxLayout()

        self.kwh_price_label, self.kwh_price_input = self.create_input_field("kWh Kaina:", "Įveskite kWh kainą")
        prices_layout.addWidget(self.kwh_price_label)
        prices_layout.addWidget(self.kwh_price_input)

        self.service_price_label, self.service_price_input = self.create_input_field("Paslaugos Kaina:",
                                                                                     "Įveskite paslaugos kainą")
        prices_layout.addWidget(self.service_price_label)
        prices_layout.addWidget(self.service_price_input)

        self.additional_price_label, self.additional_price_input = self.create_input_field("Papildoma Kaina:",
                                                                                           "Įveskite papildomą kainą")
        prices_layout.addWidget(self.additional_price_label)
        prices_layout.addWidget(self.additional_price_input)

        layout.addLayout(prices_layout)

        self.create_button = QPushButton("Sukurti grupės periodo kainas")
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
        self.create_button.clicked.connect(self.create_prices)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

        self.year_dropdown.currentIndexChanged.connect(self.update_months_by_year)
        self.month_dropdown.currentIndexChanged.connect(self.check_and_update_period_price)

        self.connect_signals()
        self.populate_periods()

    def open_new_period_dialog(self):
        dialog = NewPeriodDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.update_period_id()  # Atnaujiname period id, po naujo periodo sukūrimo.

    def create_input_field(self, label_text, placeholder_text):
        label = QLabel(label_text)
        label.setFont(QFont("Arial", 9, QFont.Bold))
        label.setStyleSheet("color: #343a40;")

        input_field = QComboBox() if "Pasirinkite" in placeholder_text else QLineEdit()
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

    def update_period_id(self):
        year = self.year_dropdown.currentText()
        month = self.month_dropdown.currentText()
        period = self.session.query(Period).filter_by(year=year, month=month).first()
        if period:
            self.period_id = period.id
            self.period_id_label.setText(f"Periodo ID: {period.id}")
            self.update_period_price()  # Atnaujina periodo kainą
            return True
        else:
            self.period_id_label.setText("Periodo ID: Nėra")
            return False

    def create_prices(self):
        kwh_price = Decimal(self.kwh_price_input.text().replace(',', '.'))
        service_price = Decimal(self.service_price_input.text().replace(',', '.'))
        additional_price = Decimal(self.additional_price_input.text().replace(',', '.'))

        if not self.update_period_id():
            show_message("Klaida", "Periodo ID nėra nustatyta.")
            return

        try:
            existing_price = self.session.query(Prices).filter_by(customers_group_id=self.group_id,
                                                                  period_id=self.period_id).first()
            if existing_price:
                show_message("Klaida", "Kainos šiam periodui ir grupei jau egzistuoja.")
                return

            new_price = Prices(
                kwh_price=kwh_price,
                price_service=service_price,
                price_additional=additional_price,
                customers_group_id=self.group_id,
                period_id=self.period_id
            )
            self.session.add(new_price)
            self.session.commit()
            show_message("Sėkmė", "Naujos kainos sėkmingai sukurtos.")
            self.accept()
        except Exception as e:
            show_message("Klaida", f"Klaida įrašant duomenis į duomenų bazę: {e}")

    def populate_periods(self):
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

    def update_period_price(self):
        """Atnaujina periodo kainos etiketę pagal pasirinktą periodą."""
        try:
            period_id = self.get_period_id()
            if period_id:
                price = self.session.query(Prices).filter_by(customers_group_id=self.group_id,
                                                             period_id=period_id).first()
                if price:
                    self.period_price_label.setText(
                        f"<table>"
                        f"<tr><td>kWh:</td><td style='padding-left: 20px;'>{price.kwh_price:.2f} €</td></tr>"
                        f"<tr><td>Adminisravimo mokestis:</td><td style='padding-left: 20px;'>{price.price_service:.2f} €</td></tr>"
                        f"<tr><td>Papildoma:</td><td style='padding-left: 20px;'>{price.price_additional:.2f} €</td></tr>"
                        f"</table>"
                    )
                else:
                    self.period_price_label.setText("Periodo kaina: Nėra duomenų")
            else:
                self.period_price_label.setText("Periodo kaina: Nėra duomenų")
        except Exception as e:
            print(f"Klaida atnaujinant periodo kainą: {e}")

    def check_and_update_period_price(self):
        """Tikrina ir atnaujina periodo kainą, kai pasikeičia pasirinktas periodas."""
        period_id = self.get_period_id()
        if period_id is not None:
            self.period_id_label.setText(f"Periodo ID: {period_id}")
            self.update_period_price()
        else:
            self.period_id_label.setText("Periodo ID: Nėra")
            self.period_price_label.setText("Periodo kaina: Nėra duomenų")

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
