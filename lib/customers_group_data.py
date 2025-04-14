from PyQt5.QtWidgets import QMessageBox
from lib.dbase import CustomerData, Orders, Customer, Prices, Session, CustomersGroupData, CustomersGroup
from datetime import date


def add_customers_group_data(session: Session, group_id: int, period_id: int, previous_kwh: int, new_kwh: int,
                             update_callback):
    try:
        # Sukuriame naują CustomerData objektą
        customers_group_data = CustomersGroupData(
            customers_group_id=group_id,
            period_id=period_id,
            customers_group_previos_kwh_data=previous_kwh,
            customers_group_new_kwh_data=new_kwh
        )

        # Pridedame objektą į sesiją
        session.add(customers_group_data)

        # Išsaugome pakeitimus duomenų bazėje
        session.commit()

        print("Duomenys sėkmingai išsaugoti.")

        # Užpildome orders lentelę
        add_order_data(session, group_id, period_id, previous_kwh, new_kwh, update_callback)

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


def add_order_data(session: Session, group_id: int, period_id: int, previous_kwh: int, new_kwh: int, update_callback):
    try:
        # grupės duomenis
        customers_group = session.query(CustomersGroup).filter_by(id=group_id).first()
        # group = customers_group.group

        # Gauti periodo kainas
        price = session.query(Prices).filter_by(customers_group_id=group_id, period_id=period_id).first()

        # Apskaičiuoti reikšmes
        customers_count = len(customers_group.customers)
        kwh_difference = new_kwh - previous_kwh
        total_kwh_price = kwh_difference * price.kwh_price
        price_service = price.price_service
        price_additional = price.price_additional
        total_price = total_kwh_price + price_service + price_additional
        pay = total_price - customers_group.customers_group_balance
        creation_date = date.today()

        print(f"Customers count: {customers_count}")
        print(f"kWh difference: {kwh_difference}")
        print(f"Total kWh price: {total_kwh_price}")
        print(f"Price service: {price_service}")
        print(f"Price additional: {price_additional}")
        print(f"Total price: {total_price}")
        print(f"Pay: {pay}")
        print(f"Creation date: {creation_date}")

        # Sukurti naują Orders objektą
        new_order = Orders(
            customers_group_id=group_id,
            customers_group_size=customers_count,
            period_id=period_id,
            previos_kwh_data=previous_kwh,
            new_kwh_data=new_kwh,
            kwh_difference=kwh_difference,
            kwh_price=price.kwh_price,
            total_kwh_price=total_kwh_price,
            price_service=price_service,
            price_additional=price_additional,
            total_price=total_price,
            balance=customers_group.customers_group_balance,
            pay=pay,
            creation_date=creation_date
        )

        print(f"New order: {new_order}")

        # Pridėti objektą į sesiją
        session.add(new_order)

        # Atnaujinti grupės balansą
        customers_group.customers_group_balance -= total_price

        # Išsaugoti pakeitimus duomenų bazėje
        session.commit()

        print(f"Orders lentelė ir grupės {customers_group.customers_group_name} balansas sėkmingai atnaujinti.")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Orders lentelė ir grupės {customers_group.customers_group_name} balansas sėkmingai atnaujinti.")
        msg.setWindowTitle("Informacija")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(lambda: update_callback())
        msg.exec_()

    except Exception as e:
        session.rollback()
        print(f"Klaida įrašant duomenis į orders lentelę: {e}")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"Klaida įrašant duomenis į orders lentelę: {e}")
        msg.setWindowTitle("Klaida")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(lambda: update_callback())
        msg.exec_()
