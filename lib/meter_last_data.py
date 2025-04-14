""" Šis kodas naudojams show_customers_lis.py ir customer_view.py failuose"""
import logging

from lib.dbase import CustomerData, CustomersGroup, CustomersGroupData


def set_previous_kwh(session, customer, previous_kwh_label, previous_kwh_input):
    customer_id = customer.id
    result = session.query(CustomerData.customer_new_kwh_data).filter_by(
        customer_id=customer_id).order_by(CustomerData.id.desc()).first()

    if result and result[0] > 0:
        previous_kwh_data = result[0]
        previous_kwh_label.setText(f"Ankstesni skaitiklio duomenys: {previous_kwh_data}")
        previous_kwh_label.show()
        previous_kwh_input.hide()
    else:
        previous_kwh_label.hide()
        previous_kwh_input.setPlaceholderText("Įveskite ankstesnius skaitiklio duomenis")
        previous_kwh_input.show()


def get_previous_kwh_text(session, customer):
    try:
        logging.debug("Gaunama ankstesni skaitiklio duomenys")
        customer_id = customer.id
        logging.debug(f"customer {customer_id} , dabar bandome gauti kWh duomenis")

        result = session.query(CustomerData.customer_new_kwh_data).filter_by(
            customer_id=customer_id).order_by(CustomerData.id.desc()).first()
        logging.debug(f"gauti duomenys: {result}")

        if result:
            previous_kwh_data = result[0]
            logging.debug(f"Ankstesni skaitiklio duomenys: {previous_kwh_data}")
            return previous_kwh_data  # gražinamas int
        else:
            logging.debug("Ankstesni skaitiklio duomenys nerasti")
            return "###"
    except Exception as e:
        logging.error(f"Klaida gaunant ankstesni skaitiklio duomenys: {e}")
        return "###"
    finally:
        session.close()


def set_group_previous_kwh(session, group, previous_kwh_label, previous_kwh_input):
    group_id = group.id
    result = session.query(CustomersGroupData.customers_group_new_kwh_data).filter_by(
        customers_group_id=group_id).order_by(CustomersGroupData.id.desc()).first()

    if result and result[0] > 0:
        previous_kwh_data = result[0]
        previous_kwh_label.setText(f"Ankstesni skaitiklio duomenys: {previous_kwh_data}")
        previous_kwh_label.show()
        previous_kwh_input.hide()
    else:
        previous_kwh_label.hide()
        previous_kwh_input.setPlaceholderText("Įveskite ankstesnius skaitiklio duomenis")
        previous_kwh_input.show()


def get_group_previous_kwh_text(session, group):
    try:
        logging.debug("Gaunama ankstesni skaitiklio duomenys")
        group_id = group.id
        logging.debug(f"group id: {group_id} , dabar bandome gauti kWh duomenis")

        result = session.query(CustomersGroupData.customers_group_new_kwh_data).filter_by(
            customers_group_id=group_id).order_by(CustomersGroupData.id.desc()).first()
        logging.debug(f"gauti duomenys: {result}")

        if result:
            previous_kwh_data = result[0]
            logging.debug(f"Ankstesni skaitiklio duomenys: {previous_kwh_data}")
            return previous_kwh_data  # gražinamas int
        else:
            logging.debug("Ankstesni skaitiklio duomenys nerasti")
            return "###"
    except Exception as e:
        logging.error(f"Klaida gaunant ankstesni skaitiklio duomenys: {e}")
        return "###"
    finally:
        session.close()
