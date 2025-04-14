import re

from PyQt5.QtCore import Qt, pyqtSignal, QSize, center
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect, QPushButton, QLineEdit, QComboBox,
                             QHBoxLayout, QListWidget, QMessageBox, QGroupBox, QFrame, QGridLayout)

from config.config import fonas, small_windows_size, medium_windows_size
from lib.create_period import NewPeriodDialog
from lib.create_period_prices import NewPeriodPrices
from lib.customer_data import add_customer_data
from lib.dbase import Period, Prices, Session, Payments, Customer, CustomersGroup, CustomerData, Orders
from lib.meter_last_data import set_previous_kwh, get_previous_kwh_text
from lib.payments import PaymentGUI


def button_style():
    return """
        QPushButton {
            background-color: #f8f9fa;
            border: 1px solid #ced4da;
            border-radius: 7px;
            padding: 8px;
        }
        QPushButton:hover {
            background-color: #e2e6ea;
        }
    """


class CustomerView(QWidget):
    view_closed = pyqtSignal()

    def closeEvent(self, event):
        self.view_closed.emit()
        super().closeEvent(event)

    def __init__(self, group, customer):
        super().__init__()
        self.group = group
        self.customer = customer
        self.customer_name = customer.customer_name
        self.group_name = group.customers_group_name

        self.session = Session()

        # Inicializuojame atributus
        self.create_price = None
        self.create_period_price = None
        self.payment_window = None

        self.setGeometry(*medium_windows_size)  # Nustatome lango dydį
        # self.setContentsMargins(10, 10, 10, 10)
        # self.setStyleSheet(f"background-color: #fff;")

        # Nustatome lango pavadinimą
        self.setWindowTitle(
            f'Klientas: "{customer.customer_name}", Kliento ID: {customer.id}, Grupė: "{group.customers_group_name}", Grupės ID: {group.id}')

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)  # Nustatome lygiavimą viršuje
        self.setLayout(layout)

        # Sukuriame pirmą QWidget bloką (client info)
        client_info_widget = QWidget()
        client_info_widget.setObjectName("clientInfoWidget")
        client_info_widget.setStyleSheet("#clientInfoWidget {"
                                         "background-color: #fafafa;"
                                         "border: 1px solid #bbb;"
                                         "border-radius: 7px;"
                                         "}")

        client_info_layout = QVBoxLayout()
        client_info_layout.setContentsMargins(20, 10, 20, 10)
        client_info_widget.setLayout(client_info_layout)
        layout.addWidget(client_info_widget)
        """
        layout.addSpacing(10)

        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignRight)
        buttons_layout.setContentsMargins(0, 0, 0, 10)

        buttons_label_name = QLabel("Kliento duomenys")
        buttons_label_name.setStyleSheet("color: #000; background-color: transparent; font-size: 12pt;")
        buttons_label_name.setAlignment(Qt.AlignLeft)
        buttons_layout.addWidget(buttons_label_name)

        delete_button = QPushButton("Ištrinti")
        delete_button.setFixedWidth(100)
        delete_button.setStyleSheet(button_style())
        delete_button.clicked.connect(lambda _, c=customer: self.delete_customer(c))
        buttons_layout.addWidget(delete_button)

        another_button = QPushButton("Redaguoti")
        another_button.setFixedWidth(100)
        another_button.setStyleSheet(button_style())
        buttons_layout.addWidget(another_button)

        client_info_layout.addLayout(buttons_layout)
        """
        buttons_layout = QGridLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 10)

        buttons_label_name = QLabel("Kliento duomenys")
        buttons_label_name.setStyleSheet("color: #666; background-color: transparent; font-size: 12pt;")
        buttons_label_name.setAlignment(Qt.AlignLeft)
        buttons_layout.addWidget(buttons_label_name, 0, 0)  # Pridedame pavadinimą į pirmą eilutę, pirmą stulpelį

        delete_button = QPushButton("Ištrinti")
        delete_button.setFixedWidth(100)
        delete_button.setStyleSheet(button_style())
        delete_button.clicked.connect(lambda _, c=customer: self.delete_customer(c))
        buttons_layout.addWidget(delete_button, 0, 4)  # Pridedame mygtuką į pirmą eilutę, antrą stulpelį

        another_button = QPushButton("Redaguoti")
        another_button.setFixedWidth(100)
        another_button.setStyleSheet(button_style())
        buttons_layout.addWidget(another_button, 0, 5)  # Pridedame mygtuką į pirmą eilutę, trečią stulpelį

        client_info_layout.addLayout(buttons_layout)

        title0 = QLabel(
            f'<b>{customer.customer_name}</b> <span style="color: #555555; font-size: 12pt;"><sup>id: {customer.id}</span>')
        title0.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        title0.setFont(QFont("Arial", 14, QFont.Bold))
        title0.setStyleSheet("color: #408140; background-color: transparent;")
        client_info_layout.addWidget(title0)

        title1 = QLabel(
            f'<b>{group.customers_group_name}</b> <span style="color: #555555; font-size: 12pt;"><sup>id: {group.id}</span>')
        title1.setAlignment(Qt.AlignLeft)
        title1.setFont(QFont("Arial", 12, QFont.Bold))
        title1.setStyleSheet("color: #007bfc; background-color: transparent;")
        title1.setGraphicsEffect(self.create_shadow(5, QColor(255, 255, 255, 200)))
        client_info_layout.addWidget(title1)

        customer_meter_id = QLabel(f"Skaitiklio id: {customer.customer_kwh_meter_id}")
        customer_meter_id.setStyleSheet("background-color: transparent;")
        customer_meter_id.setGraphicsEffect(self.create_shadow(5, QColor(255, 255, 255, 200)))
        client_info_layout.addWidget(customer_meter_id)

        customer_meter_type = QLabel(f"Skaitiklio tipas: {customer.customer_meter_type}")
        customer_meter_type.setStyleSheet("background-color: transparent;")
        customer_meter_type.setGraphicsEffect(self.create_shadow(5, QColor(255, 255, 255, 200)))
        client_info_layout.addWidget(customer_meter_type)

        self.customer_balance = QLabel(f"Balansas: {customer.customer_balance:.2f}")
        self.customer_balance.setStyleSheet("background-color: transparent;")
        self.customer_balance.setGraphicsEffect(self.create_shadow(5, QColor(255, 255, 255, 200)))
        client_info_layout.addWidget(self.customer_balance)

        customer_email = QLabel(f"El. paštas: {customer.customer_email}")
        customer_email.setStyleSheet("color: #007bfc; background-color: transparent;")
        customer_email.setGraphicsEffect(self.create_shadow(5, QColor(255, 255, 255, 200)))
        client_info_layout.addWidget(customer_email)

        # Sukuriame antrą QWidget bloką (form layout)
        form_widget = QWidget()
        form_widget.setObjectName("form_widget")
        form_widget.setStyleSheet("#form_widget {"
                                  "background-color: #fafafa;"
                                  "border: 1px solid #bbb;"
                                  "border-radius: 7px;"
                                  "}")
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(20, 10, 20, 10)
        name = QLabel("Apskaitos duomenys")
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet("color: #666; background-color: transparent; font-size: 12pt;")
        form_layout.addWidget(name)

        kwh_layout = QHBoxLayout()
        kwh_layout.setContentsMargins(0, 10, 0, 10)
        kwh_layout.setSpacing(30)  # Nustato tarpus tarp QLineEdit laukų

        self.previous_kwh_label = QLabel(self)
        self.previous_kwh_input = QLineEdit(self)

        self.previous_kwh = self.get_previous_kwh()

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
        create_period_button.setFixedWidth(100)
        create_period_button.setStyleSheet(button_style())
        create_period_button.clicked.connect(self.create_period)
        period_layout.addWidget(create_period_button)

        period_price_button = QPushButton("Tarifai", self)
        period_price_button.setToolTip(
            f"Tarifų priskyrimas\npasirinktam periodui\ngrupei: {self.group.customers_group_name}")
        period_price_button.setFixedWidth(100)
        period_price_button.setStyleSheet(button_style())
        period_price_button.clicked.connect(self.open_period_price_window)
        period_layout.addWidget(period_price_button)

        prices_layout = QHBoxLayout()
        prices_layout.setContentsMargins(0, 20, 0, 20)

        self.period_price_label = QLabel("Kainos")
        self.period_price_label.setStyleSheet("background-color: transparent;")
        prices_layout.addWidget(self.period_price_label)

        self.summary_label = QLabel("Rezultatai")
        self.summary_label.setStyleSheet("background-color: transparent;")
        prices_layout.addWidget(self.summary_label)

        form_layout.addLayout(prices_layout)

        button_layout = QHBoxLayout()

        save_button = QPushButton("Išsaugoti duomenis", self)
        save_button.setFixedWidth(200)
        save_button.hasMouseTracking()
        save_button.setStyleSheet(button_style())
        save_button.clicked.connect(self.save_data)
        button_layout.addWidget(save_button)

        form_layout.addLayout(button_layout)
        layout.addWidget(form_widget)

        form_payments_widget = QWidget()
        # form_payments_widget.setContentsMargins(0,20,0,20)
        form_payments_widget.setObjectName("form_payments_widget")
        form_payments_widget.setStyleSheet("#form_payments_widget {"
                                           "background-color: #fafafa;"
                                           "border: 1px solid #cccccc;"
                                           "border-radius: 7px;"
                                           "}")
        form_payments_layout = QVBoxLayout(form_payments_widget)
        form_payments_layout.setContentsMargins(0, 20, 0, 20)
        payment_group_box = QGroupBox()
        name_payments = QLabel("Kliento įmokų sąrašas")
        name_payments.setStyleSheet("border: None; font-weight: bold; color: #666;")
        payment_group_box.setStyleSheet("background: #fff; border: 1px solid #bbb; border-radius: 10px; padding: 5px;")
        payment_group_box_layout = QVBoxLayout()
        payment_group_box_layout.addWidget(name_payments)
        payment_group_box.setLayout(payment_group_box_layout)

        self.payment_list_widget = QListWidget(self)
        self.payment_list_widget.setStyleSheet(
            "font-family: 'Roboto Condensed'; font-size: 12px;"
            "margin-left: 20px; background-color: transparent; border: None;")
        self.payment_list_widget.setFixedWidth(250)
        self.payment_list_widget.setMinimumHeight(120)

        # --------- Mokėjimų sąrašas ---------------------------
        payments = self.session.query(Payments).filter_by(customer_id=self.customer.id).all()[::-1]
        for payment in payments:
            self.payment_list_widget.addItem(f"Data: {payment.paid_date},   Suma: {payment.paid:.2f} €")

        payment_group_box_layout.addWidget(self.payment_list_widget)

        payment_buttons_layout = QHBoxLayout()
        payment_buttons_layout.addStretch()

        empty_space = QWidget()
        empty_space.setFixedWidth(20)

        new_payment_button = QPushButton("Nauja įmoka", self)
        new_payment_button.setStyleSheet(button_style())
        new_payment_button.setFixedSize(90, 60)
        new_payment_button.clicked.connect(self.new_payment)

        payment_buttons_layout.addWidget(new_payment_button, alignment=Qt.AlignCenter)  # Centruoti mygtuką
        payment_buttons_layout.addWidget(empty_space)
        payment_buttons_layout.addWidget(payment_group_box, alignment=Qt.AlignCenter)
        payment_buttons_layout.addWidget(empty_space)

        form_payments_layout.addLayout(payment_buttons_layout)

        # Pridedame form_layout ir form_payments_layout į pagrindinį layout
        layout.addWidget(form_widget)
        # layout.addSpacing(10)
        layout.addWidget(form_payments_widget)

        # Pridedame signalą periodų pasirinkimo keitimui
        try:
            self.connect_signals()
            self.populate_periods()
            set_previous_kwh(self.session, self.customer, self.previous_kwh_label, self.previous_kwh_input)
        except Exception as e:
            print(f"Klaida __init__ metode: {e}")

    def new_payment(self):
        self.payment_window = PaymentGUI(customer_id=self.customer.id, group_id=self.group.id)
        self.payment_window.payment_added.connect(self.update_customer_view)
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
            customer = self.session.query(Customer).filter_by(id=self.customer.id).first()
            self.customer_balance.setText(f"Balansas: {customer.customer_balance:.2f}")
        except Exception as e:
            QMessageBox.warning(self, "Klaida", f"Klaida atnaujinant balansą: {e}")

    def clear_kwh_inputs(self):
        try:
            self.previous_kwh_input.clear()
            self.new_kwh_input.clear()
            set_previous_kwh(self.session, self.customer, self.previous_kwh_label, self.previous_kwh_input)
        except Exception as e:
            QMessageBox.warning(self, "Klaida", f"Klaida atnaujinant ankstesnius kWh duomenis: {e}")

    def update_data(self):
        try:
            self.update_balance()
            self.clear_kwh_inputs()
        except Exception as e:
            QMessageBox.warning(self, "Klaida", f"Klaida atnaujinant duomenis: {e}")

    def get_previous_kwh(self):
        try:
            previous_kwh = get_previous_kwh_text(self.session, self.customer)
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
            customer_id = self.customer.id
            period_id = self.get_period_id()

            if period_id:
                add_customer_data(self.session, customer_id, period_id, previous_kwh, new_kwh, self.update_data)
            else:
                QMessageBox.warning(self, "Period Error", "Period ID not found.")
        except Exception as e:
            QMessageBox.warning(self, "Klaida", f"Klaida išsaugant duomenis: {e}")

    def populate_periods(self):
        print("get available periods")
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
                        f"<tr><td>kWh kaina:</td><td style='padding-left: 20px;'>{price.kwh_price:.2f} €</td></tr>"
                        f"<tr><td>Adminisravimo mokestis:</td><td style='padding-left: 20px;'>{price.price_service:.2f} €</td></tr>"
                        f"<tr><td>Papildomas mokestis:</td><td style='padding-left: 20px;'>{price.price_additional:.2f} €</td></tr>"
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

    def update_customer_view(self):
        """Atnaujina visą informaciją esančią CustomerView klasės lange."""
        self.customer = self.session.query(Customer).filter_by(id=self.customer.id).first()
        self.customer_balance.setText(f"Balansas: {self.customer.customer_balance:.2f}")
        self.payment_list_widget.clear()
        payments = self.session.query(Payments).filter_by(customer_id=self.customer.id).all()
        for payment in payments:
            self.payment_list_widget.addItem(f"Data: {payment.paid_date}, Suma: {payment.paid:.2f} €")

    def delete_customer(self, customer):
        try:
            # Priverstinai perkrauti grupę iš DB naudojant tą pačią sesiją
            self.group = self.session.query(CustomersGroup).filter_by(id=self.group.id).first()

            if not self.group or not hasattr(self.group, 'customers'):
                QMessageBox.critical(self, "Klaida", "Grupė neegzistuoja arba neturi 'customers' atributo")
                return

            first_reply = QMessageBox.question(self, 'Patvirtinimas',
                                               f'Ar tikrai norite ištrinti\nklientą {customer.customer_name}?',
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if first_reply == QMessageBox.Yes:
                # Suskaičiuoti įrašus, kurie bus pašalinti
                customer_data_count = self.session.query(CustomerData).filter_by(customer_id=customer.id).count()
                orders_count = self.session.query(Orders).filter_by(customer_id=customer.id).count()
                payments_count = self.session.query(Payments).filter_by(customer_id=customer.id).count()

                second_reply = QMessageBox.question(self, 'Patvirtinimas',
                                                    f'Ar esate įsitikinę,\nkad norite ištrinti\n'
                                                    f'klientą {customer.customer_name}?\n'
                                                    f'Visi duomenys, susiję su\n'
                                                    f'klientu, bus ištrinti.\n\n'
                                                    f'Iš viso bus pašalinta:\n'
                                                    f'{customer_data_count} įrašų iš "CustomerData" lentelės\n'
                                                    f'{orders_count} įrašų iš "Orders" lentelės\n'
                                                    f'{payments_count} įrašų iš "Payments" lentelės',
                                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if second_reply == QMessageBox.Yes:
                    # Pašalinti klientą tiesiogiai pagal jo objektą
                    customer_in_group = next((c for c in self.group.customers if c.id == customer.id), None)

                    if customer_in_group:
                        self.group.customers.remove(customer_in_group)

                        with self.session.no_autoflush:
                            # Ištrinti visus duomenis susijusius su klientu
                            self.session.query(CustomerData).filter_by(customer_id=customer.id).delete()
                            self.session.query(Orders).filter_by(customer_id=customer.id).delete()
                            self.session.query(Payments).filter_by(customer_id=customer.id).delete()

                            self.session.delete(customer_in_group)
                            self.session.commit()
                    else:
                        QMessageBox.critical(self, "Klaida", "Klientas nėra grupėje")
        except SQLAlchemyError as e:
            QMessageBox.critical(self, "Klaida", f"Įvyko klaida ištrinant klientą: {str(e)}")
