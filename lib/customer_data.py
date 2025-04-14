from PyQt5.QtWidgets import QMessageBox
from lib.dbase import CustomerData, Orders, Customer, Prices, Session
from datetime import date


def add_customer_data(session: Session, customer_id: int, period_id: int, previous_kwh: int, new_kwh: int,
                      update_callback):
    try:
        # Sukuriame naują CustomerData objektą
        customer_data = CustomerData(
            customer_id=customer_id,
            period_id=period_id,
            customer_previos_kwh_data=previous_kwh,
            customer_new_kwh_data=new_kwh
        )

        # Pridedame objektą į sesiją
        session.add(customer_data)

        # Išsaugome pakeitimus duomenų bazėje
        session.commit()

        print("Duomenys sėkmingai išsaugoti.")

        # Užpildome orders lentelę
        add_order_data(session, customer_id, period_id, previous_kwh, new_kwh, update_callback)

    except Exception as e:
        session.rollback()
        print(f"Klaida įrašant duomenis: {e}")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"Klaida įrašant duomenis: {e}")
        msg.setWindowTitle("Klaida")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(lambda: update_callback())
        msg.exec_()


def add_order_data(session: Session, customer_id: int, period_id: int, previous_kwh: int, new_kwh: int,
                   update_callback):
    try:
        # Gauti kliento ir grupės duomenis
        customer = session.query(Customer).filter_by(id=customer_id).first()
        group = customer.group

        # Gauti periodo kainas
        price = session.query(Prices).filter_by(customers_group_id=group.id, period_id=period_id).first()

        # Apskaičiuoti reikšmes
        customers_count = len(group.customers)
        kwh_difference = new_kwh - previous_kwh
        total_kwh_price = kwh_difference * price.kwh_price
        price_service = price.price_service / customers_count
        price_additional = price.price_additional / customers_count
        total_price = total_kwh_price + price_service + price_additional
        pay = total_price - customer.customer_balance
        creation_date = date.today()

        # Sukurti naują Orders objektą
        new_order = Orders(
            customers_group_id=group.id,
            customers_group_size=customers_count,
            customer_id=customer_id,
            period_id=period_id,
            previos_kwh_data=previous_kwh,
            new_kwh_data=new_kwh,
            kwh_difference=kwh_difference,
            kwh_price=price.kwh_price,
            total_kwh_price=total_kwh_price,
            price_service=price_service,
            price_additional=price_additional,
            total_price=total_price,
            balance=customer.customer_balance,
            pay=pay,
            creation_date=creation_date
        )

        # Pridėti objektą į sesiją
        session.add(new_order)

        # Atnaujinti kliento balansą
        customer.customer_balance -= total_price

        # Išsaugoti pakeitimus duomenų bazėje
        session.commit()

        update_callback()  # geriau kviesti čia, nei per `buttonClicked`

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Orders lentelė ir kliento balansas sėkmingai atnaujinti.")
        msg.setWindowTitle("Informacija")
        msg.setStandardButtons(QMessageBox.Ok)
        # msg.buttonClicked.connect(lambda: update_callback())
        msg.exec_()

    except Exception as e:
        session.rollback()
        print(f"Klaida įrašant duomenis į orders lentelę: {e}")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"Klaida įrašant duomenis į orders lentelę: {e}")
        msg.setWindowTitle("Klaida")
        msg.setStandardButtons(QMessageBox.Ok)
        # msg.buttonClicked.connect(lambda: update_callback())
        msg.exec_()
