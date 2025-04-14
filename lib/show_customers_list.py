from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QDialog, QLabel, QVBoxLayout, QPushButton, QGridLayout, QWidget, \
    QHBoxLayout, QSizePolicy, QMessageBox

from config.config import fonas
from lib.create_customer import NewCustomerDialog
from lib.create_invoices import InvoiceGUI
from lib.customer_view import CustomerView
from lib.customers_group_view import CustomersGroupView
from lib.dbase import Session, CustomersGroup
from lib.meter_last_data import get_previous_kwh_text
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


class CustomerListWindow(QWidget):
    customer_created = pyqtSignal()

    def __init__(self, group, parent=None):
        super().__init__(parent)

        self.group = group
        self.session = Session()
        self.setContentsMargins(20, 20, 20, 20)
        self.setStyleSheet(f"QWidget {{ background-color: {fonas[1]}; border: none; }}")

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.create_ui()
        self.reload_customers()

    def create_ui(self):
        if self.group:
            title1 = QLabel(f'Klientai grupėje "{self.group.customers_group_name}"')
            title1.setAlignment(Qt.AlignHCenter)
            title1.setFont(QFont("Arial", 12, QFont.Bold))
            title1.setStyleSheet("color: #007bfc; background-color: transparent;")
            self.layout.addWidget(title1)

            title2 = QLabel(f'Grupės ID: {self.group.id}')
            title2.setAlignment(Qt.AlignHCenter)
            title2.setFont(QFont("Arial", 8, QFont.Bold))
            title2.setStyleSheet("color: #88a8a8; background-color: transparent;")
            self.layout.addWidget(title2)

            buttons_layout = QHBoxLayout()
            create_invoices_button = QPushButton("Sąskaitų formavimas")
            create_invoices_button.setFont(QFont("Arial", 10, QFont.Bold))
            create_invoices_button.setStyleSheet(button_style() + "padding: 10px;")
            create_invoices_button.clicked.connect(self.open_create_invoices_window)
            create_invoices_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            buttons_layout.addWidget(create_invoices_button)

            create_payments_button = QPushButton("Nauja įmoka")
            create_payments_button.setFont(QFont("Arial", 10, QFont.Bold))
            create_payments_button.setStyleSheet(button_style())
            create_payments_button.clicked.connect(self.new_payment)
            create_payments_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            buttons_layout.addWidget(create_payments_button)

            create_group_view_button = QPushButton("Grupės duomenys")
            create_group_view_button.setFont(QFont("Arial", 10, QFont.Bold))
            create_group_view_button.setStyleSheet(button_style())
            create_group_view_button.clicked.connect(self.customers_group_view)
            create_group_view_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            buttons_layout.addWidget(create_group_view_button)

            self.layout.addLayout(buttons_layout)

        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 30, 0, 0)
        self.grid_layout.setHorizontalSpacing(20)
        self.grid_layout.setVerticalSpacing(20)
        self.layout.addLayout(self.grid_layout)

    def new_payment(self):
        self.payment_window = PaymentGUI(group_id=self.group.id)
        self.payment_window.show()

    def open_create_invoices_window(self):
        if not self.group:
            print("Grupės duomenys nėra nustatyti!")
            return
        print(f"Atidaromas sąskaitų formavimo langas grupei: {self.group.customers_group_name}, {self.group.id}")
        self.invoice_window = InvoiceGUI(self.group)  # Perduodame grupės objektą
        self.invoice_window.show()

    def customers_group_view(self):
        self.customers_group_view_window = CustomersGroupView(group=self.group)
        self.customers_group_view_window.view_closed.connect(self.customer_created.emit)
        self.customers_group_view_window.show()

    def create_customer_button(self, customer):
        customer_button = QPushButton()
        customer_button.setFixedSize(170, 130)
        customer_button.setStyleSheet(self.get_button_style(customer.customer_balance))
        customer_button.setGraphicsEffect(self.create_shadow(15, QColor(0, 0, 0, 100), -2, -1))
        customer_layout = QVBoxLayout()

        customer_name = QLabel(
            f'<b>{customer.customer_name}</b> <span style="color: #555555; font-size: 10pt;"><sup>id: {customer.id}</span>')
        customer_name.setFont(QFont("Arial", 12, QFont.Bold))
        customer_name.setStyleSheet("color: #229955; background-color: transparent;")
        customer_name.setAlignment(Qt.AlignCenter)
        customer_layout.addWidget(customer_name)
        try:
            previous_kwh_text = get_previous_kwh_text(self.session, customer)
        except Exception as e:
            previous_kwh_text = "N/A"

        customer_meter_data = QLabel(f"Skaitiklio rodmenys: {previous_kwh_text}")
        customer_meter_data.setStyleSheet(f"background-color: transparent;")
        customer_layout.addWidget(customer_meter_data)

        customer_meter_id = QLabel(f"Skaitiklio id: {customer.customer_kwh_meter_id}")
        customer_meter_id.setStyleSheet(f"background-color: transparent;")
        customer_layout.addWidget(customer_meter_id)

        customer_meter_type = QLabel(f"Skaitiklio tipas: {customer.customer_meter_type}")
        customer_meter_type.setStyleSheet("background-color: transparent;")
        customer_layout.addWidget(customer_meter_type)

        customer_balance = QLabel(f"Balansas: {customer.customer_balance:.2f}")
        customer_balance.setStyleSheet("background-color: transparent;")
        customer_layout.addWidget(customer_balance)

        customer_email = QLabel(f"El. paštas: {customer.customer_email}")
        customer_email.setStyleSheet("color: #007bfc; background-color: transparent;")
        customer_layout.addWidget(customer_email)

        customer_button.setLayout(customer_layout)
        customer_button.clicked.connect(lambda _, c=customer: self.open_customer_view(c))
        return customer_button

    def reload_customers(self):
        # Priverstinai perkrauti grupę iš DB
        session = Session()
        self.group = session.query(CustomersGroup).filter_by(id=self.group.id).first()

        if not self.group or not hasattr(self.group, 'customers'):
            QMessageBox.critical(self, "Klaida", "Grupė neegzistuoja arba neturi 'customers' atributo")
            return

        while self.grid_layout.count():
            widget = self.grid_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        row, col = 0, 0
        for customer in self.group.customers:
            self.grid_layout.addWidget(self.create_customer_button(customer), row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

        self.grid_layout.addWidget(self.create_new_customer_button(), row, col)
        self.customer_created.emit()

    def eventFilter(self, obj, event):
        """Keičia „Naujas Klientas“ mygtuko tekstą į "+" pelės įvedimo/išvedimo metu."""
        if isinstance(obj, QPushButton) and obj == self.new_customer_button:
            label = obj.findChild(QLabel)  # Surandame QLabel mygtuko viduje
            if not label:
                return super().eventFilter(obj, event)

            if event.type() == QEvent.Enter:
                label.setText("+")
                label.setFont(QFont("Arial", 72, QFont.Bold))
                label.setStyleSheet("color: white; background-color: transparent;")  # Nustatome permatomą foną
            elif event.type() == QEvent.Leave:
                label.setText("Naujas Klientas")
                label.setFont(QFont("Arial", 14, QFont.Bold))
                label.setStyleSheet("color: white; background-color: transparent;")  # Nustatome permatomą foną

        return super().eventFilter(obj, event)

    def create_new_customer_button(self):
        """Sukuria 'Naujas Klientas' mygtuką su centruotu tekstu ir šešėliu."""
        self.new_customer_button = QPushButton()
        self.new_customer_button.setFixedSize(180, 140)
        self.new_customer_button.setGraphicsEffect(self.create_shadow(15, QColor(0, 0, 0, 100), 0, 0))
        self.new_customer_button.setStyleSheet("""
                    QPushButton {
                        background-color: #f5f5f5;
                        border-radius: 7px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #fafafa;
                    }
                """)
        self.new_customer_button.clicked.connect(lambda: self.open_new_customer_dialog())

        # Sukuriame centrinį išdėstymą mygtuko viduje
        layout = QVBoxLayout(self.new_customer_button)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        # Sukuriame QLabel, kuris bus viduje
        label = QLabel("Naujas Klientas")
        label.setFont(QFont("Arial", 14, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; background-color: transparent;")

        # Sukuriame šešėlį tekstui
        label.setGraphicsEffect(self.create_shadow(6, QColor(0, 0, 0, 150), 0, 0))
        # Pridedame įvykio filtrą animacijoms (+ simboliui)
        self.new_customer_button.installEventFilter(self)

        layout.addWidget(label)

        return self.new_customer_button

    def open_new_customer_dialog(self):
        dialog = NewCustomerDialog(self.group)
        dialog.customer_created.connect(self.reload_customers)
        if dialog.exec_() == QDialog.Accepted:
            self.reload_customers()

    def open_customer_view(self, customer):
        self.customer_view = CustomerView(self.group, customer)
        # self.customer_view.view_closed.connect(lambda: self.update_customer_button(customer))
        self.customer_view.view_closed.connect(self.reload_customers)
        self.customer_view.show()

    def create_shadow(self, blur_radius, color, x_offset=0, y_offset=0):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(blur_radius)
        shadow.setColor(color)
        shadow.setOffset(x_offset, y_offset)
        return shadow

    def get_button_style(self, balance):
        if balance < 0:
            return """
                QPushButton {
                    background-color: #faf5f5;
                    border: 0px solid #cccccc;
                    border-radius: 7px;
                }
                QPushButton:hover {
                    background-color: #fafafa;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #f5f5f5;
                    border: 0px solid #cccccc;
                    border-radius: 7px;
                }
                QPushButton:hover {
                    background-color: #fafafa;
                }
            """

    def update_customer_button(self, customer):
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text().contains(f"id: {customer.id}"):
                new_button = self.create_customer_button(customer)
                self.grid_layout.replaceWidget(widget, new_button)
                widget.deleteLater()
                break
