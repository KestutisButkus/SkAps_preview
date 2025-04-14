import re

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect, QPushButton, QLineEdit, QComboBox,
                             QHBoxLayout, QListWidget, QMessageBox, QGroupBox)

from config.config import fonas, small_windows_size
from lib.create_period import NewPeriodDialog
from lib.create_period_prices import NewPeriodPrices
from lib.customers_group_data import add_customers_group_data
from lib.dbase import Period, Prices, Session, Payments, CustomersGroup
from lib.meter_last_data import get_group_previous_kwh_text, set_group_previous_kwh
from lib.payments import PaymentGUI


class CustomersGroupView(QWidget):
    view_closed = pyqtSignal()

    def closeEvent(self, event):
        self.view_closed.emit()
        super().closeEvent(event)

    def __init__(self, group):
        super().__init__()
        self.group = group
        self.session = Session()

        # Inicializuojame atributus
        self.create_price = None
        self.create_period_price = None
        self.payment_window = None

        self.setGeometry(*small_windows_size)  # Nustatome lango dydį
        self.setContentsMargins(20, 20, 20, 20)
        self.setStyleSheet(f"background-color: {fonas};")

        # Nustatome lango pavadinimą
        self.setWindowTitle(
            f'Grupė: "{group.customers_group_name}", Grupės ID: {group.id}')

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)  # Nustatome lygiavimą viršuje
        self.setLayout(layout)

        # Pridėti fono spalvą layout
        group_info_widget = QWidget()
        group_info_widget.setStyleSheet("background-color: transparent;")
        group_info_layout = QVBoxLayout()
        group_info_widget.setLayout(group_info_layout)
        layout.addWidget(group_info_widget)

        title1 = QLabel(f'Grupė: "{group.customers_group_name}"')
        title1.setAlignment(Qt.AlignLeft)
        title1.setFont(QFont("Arial", 10, QFont.Bold))
        title1.setStyleSheet("color: #007bfc; background-color: transparent;")
        title1.setGraphicsEffect(self.create_shadow(5, QColor(255, 255, 255, 200)))
        group_info_layout.addWidget(title1)

        title2 = QLabel(f'ID: {group.id}')
        title2.setAlignment(Qt.AlignLeading)
        title2.setFont(QFont("Arial", 6, QFont.Bold))
        title2.setStyleSheet("color: #88a8a8; background-color: transparent;")
        title2.setGraphicsEffect(self.create_shadow(5, QColor(255, 255, 255, 200)))
        group_info_layout.addWidget(title2)

        customers_group_meter_id = QLabel(f"Skaitiklio id: {group.customers_group_kwh_meter_id}")
        customers_group_meter_id.setStyleSheet("background-color: transparent;")
        customers_group_meter_id.setGraphicsEffect(self.create_shadow(5, QColor(255, 255, 255, 200)))
        group_info_layout.addWidget(customers_group_meter_id)

        customers_group_meter_type = QLabel(f"Skaitiklio tipas: {group.customers_group_meter_type}")
        customers_group_meter_type.setStyleSheet("background-color: transparent;")
        customers_group_meter_type.setGraphicsEffect(self.create_shadow(5, QColor(255, 255, 255, 200)))
        group_info_layout.addWidget(customers_group_meter_type)

        self.customers_group_balance = QLabel(f"Balansas: {group.customers_group_balance:.2f} €")
        self.customers_group_balance.setStyleSheet("background-color: transparent;")
        self.customers_group_balance.setGraphicsEffect(self.create_shadow(5, QColor(255, 255, 255, 200)))
        group_info_layout.addWidget(self.customers_group_balance)

        # Formos kūrimas
        form_layout = QVBoxLayout()
        form_layout.addSpacing(30)  # Prideda papildomą tarpą tarp elementų

        kwh_layout = QHBoxLayout()
        kwh_layout.setSpacing(30)  # Nustato tarpus tarp QLineEdit laukų

        self.previous_kwh_label = QLabel(self)
        self.previous_kwh_input = QLineEdit(self)

        self.previous_kwh = self.get_group_previous_kwh()

        if isinstance(self.previous_kwh, int) and self.previous_kwh > 0:
            self.previous_kwh_label.setText(f"Ankstesni skaitiklio duomenys: <b>{self.previous_kwh}</b>")
            self.previous_kwh_label.setStyleSheet("background-color: transparent; border-radius: 3px;")
            self.previous_kwh_label.show()
            self.previous_kwh_input.hide()
        else:
            self.previous_kwh_input.setPlaceholderText("Ankstesni")
            self.previous_kwh_label.hide()
            self.previous_kwh_input.show()

        self.new_kwh_input = QLineEdit(self)
        self.new_kwh_input.setPlaceholderText("Įveskite naujius skaitiklio duomenis")

        kwh_layout.addWidget(self.previous_kwh_label)
        kwh_layout.addWidget(self.previous_kwh_input)
        kwh_layout.addWidget(self.new_kwh_input)

        form_layout.addLayout(kwh_layout)

        period_layout = QHBoxLayout()
        period_layout.setSpacing(20)  # Nustato tarpus tarp metų ir mėnesių pasirinkimo ir etiketės

        self.year_dropdown = QComboBox(self)
        period_layout.addWidget(self.year_dropdown)

        self.month_dropdown = QComboBox(self)
        period_layout.addWidget(self.month_dropdown)

        self.period_id_label = QLabel("Periodo ID: Nėra")
        self.period_id_label.setStyleSheet("color: #007bfc; background-color: transparent;")
        period_layout.addWidget(self.period_id_label)
        form_layout.addLayout(period_layout)

        create_period_button = QPushButton("Naujas periodas", self)
        create_period_button.setToolTip(f"Sukurti naują periodą")
        create_period_button.setStyleSheet("background-color: #00cc66; color: #000;")
        create_period_button.clicked.connect(self.create_period)
        period_layout.addWidget(create_period_button)

        period_price_button = QPushButton("Tarifai", self)
        period_price_button.setToolTip(
            f"Tarifų priskyrimas\npasirinktam periodui\ngrupei: {self.group.customers_group_name}")
        period_price_button.setStyleSheet("background-color: #ffcc00; color: #000;")
        period_price_button.clicked.connect(self.open_period_price_window)
        period_layout.addWidget(period_price_button)

        self.period_price_label = QLabel("\n\n\n")
        self.period_price_label.setStyleSheet("background-color: transparent;")
        form_layout.addWidget(self.period_price_label)

        # Sukuriame mygtukus ir pridedame juos į vieną eilutę
        button_layout = QHBoxLayout()

        save_button = QPushButton("Išsaugoti duomenis", self)
        save_button.setStyleSheet("background-color: #0066cc; color: #fff;")
        save_button.clicked.connect(self.save_data)
        button_layout.addWidget(save_button)

        form_layout.addLayout(button_layout)
        form_layout.addSpacing(30)

        # Sukuriame QGroupBox atliktų kliento mokėjimų sąrašui
        payment_group_box = QGroupBox("Kliento mokėjimų sąrašas")
        payment_group_box_layout = QVBoxLayout()
        payment_group_box.setLayout(payment_group_box_layout)

        self.payment_list_widget = QListWidget(self)
        self.payment_list_widget.setStyleSheet(
            "font-family: 'Roboto Condensed'; font-size: 12px;"
            "margin-left: 20px; background-color: transparent; border: None")
        self.payment_list_widget.setFixedWidth(250)  # Nustatyti fiksuotą plotį
        self.payment_list_widget.setMinimumHeight(120)

        payments = self.session.query(Payments).filter(
            Payments.customers_group_id == self.group.id, Payments.customer_id == None).all()[::-1]

        for payment in payments:
            self.payment_list_widget.addItem(f"Data: {payment.paid_date},   Suma: {payment.paid:.2f} €")

        # mokėjimų sąrašas su numeracija
        # payments = self.session.query(Payments).filter_by(customer_id=self.customer.id).all()[::-1]
        # for i, payment in enumerate(payments):
        #     self.payment_list_widget.addItem(f"Nr.{len(payments) - i}.   Data: {payment.paid_date},   Suma: {payment.paid:.2f} €")

        payment_group_box_layout.addWidget(self.payment_list_widget)

        # Sukuriame mygtukus ir pridedame juos į vieną eilutę su mokėjimų sąrašu
        payment_buttons_layout = QHBoxLayout()
        payment_buttons_layout.addStretch()

        empty_space = QWidget()
        empty_space.setFixedWidth(20)

        new_payment_button = QPushButton("Nauja įmoka", self)
        new_payment_button.setStyleSheet("background-color: #55cc66; color: #fff;")
        new_payment_button.setFixedSize(90, 60)  # Nustatyti fiksuotą dydį
        new_payment_button.clicked.connect(self.new_payment)

        payment_buttons_layout.addWidget(empty_space)
        payment_buttons_layout.addWidget(new_payment_button, alignment=Qt.AlignCenter)  # Centruoti mygtuką
        payment_buttons_layout.addWidget(empty_space)
        payment_buttons_layout.addWidget(payment_group_box, alignment=Qt.AlignCenter)
        payment_buttons_layout.addWidget(empty_space)

        form_layout.addLayout(payment_buttons_layout)
        layout.addLayout(form_layout)

        # Pridedame signalą periodų pasirinkimo keitimui
        try:
            self.connect_signals()
            self.populate_periods()
            set_group_previous_kwh(self.session, self.group, self.previous_kwh_label, self.previous_kwh_input)
        except Exception as e:
            print(f"Klaida __init__ metode: {e}")

    def new_payment(self):
        self.payment_window = PaymentGUI(group_id=self.group.id)
        self.payment_window.payment_added.connect(self.update_customers_group_view)
        self.payment_window.show()

    def create_shadow(self, blur_radius, color, x_offset=0, y_offset=0):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(blur_radius)
        shadow.setColor(color)
        shadow.setOffset(x_offset, y_offset)
        return shadow

    def open_period_price_window(self):
        # Funkcija atidaryti naują langą periodo kainai sukurti
        self.create_price = NewPeriodPrices(self.group.id, self.group.customers_group_name)
        self.create_price.show()

    def create_period(self):
        """Atidaro periodo langą."""
        self.create_period_price = NewPeriodDialog()
        self.create_period_price.show()

    def update_balance(self):
        try:
            group = self.session.query(CustomersGroup).filter_by(id=self.group.id).first()
            self.customers_group_balance.setText(f"Balansas: {group.customers_group_balance:.2f}")
        except Exception as e:
            QMessageBox.warning(self, "Klaida", f"Klaida atnaujinant balansą: {e}")

    def clear_kwh_inputs(self):
        try:
            self.previous_kwh_input.clear()
            self.new_kwh_input.clear()
            set_group_previous_kwh(self.session, self.group, self.previous_kwh_label, self.previous_kwh_input)
        except Exception as e:
            QMessageBox.warning(self, "Klaida", f"Klaida atnaujinant ankstesnius kWh duomenis: {e}")

    def update_data(self):
        try:
            self.update_balance()
            self.clear_kwh_inputs()
        except Exception as e:
            QMessageBox.warning(self, "Klaida", f"Klaida atnaujinant duomenis: {e}")

    def get_group_previous_kwh(self):
        try:
            previous_kwh = get_group_previous_kwh_text(self.session, self.group)
            return previous_kwh
        except Exception as e:
            print(f"Klaida gaunant ankstesnius kWh duomenis: {e}")
            return 0

    def save_data(self):
        try:
            if self.previous_kwh_label.isVisible():
                previous_kwh_data = self.previous_kwh_label.text()
                previous_kwh_data = re.findall(r'\d+', previous_kwh_data)
                if previous_kwh_data:
                    previous_kwh_data = previous_kwh_data[0]
                else:
                    QMessageBox.warning(self, "Input Error", "Invalid previous kWh value.")
                    return
            else:
                previous_kwh_data = self.previous_kwh_input.text()

            new_kwh_data = self.new_kwh_input.text()

            if not previous_kwh_data or not new_kwh_data:
                QMessageBox.warning(self, "Input Error", "Please enter both previous and new kWh values.")
                return

            if not previous_kwh_data.isdigit() or not new_kwh_data.isdigit():
                QMessageBox.warning(self, "Input Error", "kWh values must be numeric.")
                return
            previous_kwh = int(previous_kwh_data)
            new_kwh = int(new_kwh_data)
            group_id = self.group.id
            period_id = self.get_period_id()

            if period_id:
                add_customers_group_data(self.session, group_id, period_id, previous_kwh, new_kwh, self.update_data)
            else:
                QMessageBox.warning(self, "Period Error", "Period ID not found.")
        except Exception as e:
            QMessageBox.warning(self, "Klaida", f"Klaida išsaugant duomenis: {e}")

    def populate_periods(self):
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

    def update_period_price(self):
        """Atnaujina periodo kainos etiketę pagal pasirinktą periodą."""
        try:
            period_id = self.get_period_id()
            if period_id:
                price = self.session.query(Prices).filter_by(customers_group_id=self.group.id,
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
            self.populate_months_by_year(
                int(selected_year))  # Konvertuojame į int, nes pasirinktas tekstas yra string

    def update_customers_group_view(self):
        """Atnaujina visą informaciją esančią CustomerView klasės lange."""
        self.group = self.session.query(CustomersGroup).filter_by(id=self.group.id).first()
        self.customers_group_balance.setText(f"Balansas: {self.group.customers_group_balance:.2f}")
        self.payment_list_widget.clear()
        payments = self.session.query(Payments).filter(Payments.customers_group_id == self.group.id,
                                                       Payments.customer_id == None).all()[::-1]
        for payment in payments:
            self.payment_list_widget.addItem(f"Data: {payment.paid_date}, Suma: {payment.paid:.2f} €")
