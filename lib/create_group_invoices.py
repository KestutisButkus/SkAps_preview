from datetime import date, timedelta

from forms.customers_group_invoices_html import save_invoice_html
from lib.dbase import Customer, Period, Orders, CustomersGroup, session, BankAccount, group_account_association


def print_group_orders_all_customers(group, period_id):
    # Pasirenkame grupę
    group_id = group

    # Gauti ir atspausdinti periodų sąrašą
    period_id = period_id

    # Filtruojame klientus pagal grupę
    customers = session.query(Customer).filter(Customer.customers_group_id == group_id).all()

    # Išsaugome visų klientų ID sąraše
    customers_ids = [customer.id for customer in customers]
    invoice_date = date.today()
    payment_due_date = invoice_date + timedelta(days=14)
    get_bank_account = session.query(BankAccount).join(group_account_association).filter(
        group_account_association.c.customers_group_id == group_id).first()
    bank_account = get_bank_account.account_number
    bank_text = "Banko sąskaita apmokėjimui:"

    # Užklausa duomenims ištraukti
    customer_data = session.query(
        Customer.customer_name,
        Customer.customer_kwh_meter_id,
        Customer.customer_meter_type,
        Orders.previos_kwh_data,
        Orders.new_kwh_data,
        CustomersGroup.customers_group_name,
        Orders.balance,
        Orders.kwh_price,
        Orders.total_kwh_price,
        Orders.price_service,
        Orders.price_additional,
        Orders.total_price,
        Orders.pay,
        Orders.id,
        Period.year,
        Period.month,
        Orders.kwh_difference
    ).join(Customer, Orders.customer_id == Customer.id
           ).join(CustomersGroup, Orders.customers_group_id == CustomersGroup.id
                  ).join(Period, Orders.period_id == Period.id
                         ).filter(
        Orders.customer_id.in_(customers_ids),
        Period.id == period_id  # Naudojame period_id filtravimui
    ).all()

    print(f"Sąskaita {customer_data[0][14]}-{customer_data[0][15]} laikotarpiui")
    print(f"{'Grupė:':<10} \"{customer_data[0][5]}\"\n")
    print(f"{'Klientai':^140}")
    print(f"{'Klientas:':<14}{'kWh NUO:':<10}{'kWh IKI:':<10}{'Viso kWh:':<10}{'kWh kaina:':<10}"
          f"{'Kaina už kWh:':<15}{'Aptarnavimas:':<15}{'Kiti mokesčiai:':<16}{'Visa kaina:':<14}"
          f"{'Sąsk. balansas:':<15}{'Mokėti:':<10}")

    if customer_data:
        data_list = []
        for data in customer_data:
            print("-" * 140)
            print(f"{data[0]:<14}{data[3]:<10}{data[4]:<10}{data[16]:<10}{data[7]:<10.2f}"
                  f"{data[8]:<15.2f}{data[9]:<15.2f}{data[10]:<16.2f}{data[11]:<14.2f}"
                  f"{data[6]:<15.2f}{data[12]:<10.2f}")

            # Paruošiame duomenis HTML failams
            invoice_data = {
                'invoice_number': data[13],
                'period': f"{customer_data[0][14]}-{customer_data[0][15]}",
                'group': customer_data[0][5],
                'customer': data[0],
                'kwh_from': data[3],
                'kwh_to': data[4],
                'kwh_total': data[16],
                'electricity_price': data[7],
                'total_kwh_price': data[8],
                'service_price': data[9],
                'additional_price': data[10],
                'total_price': data[11],
                'balance': data[6],
                'pay': data[12],
                'invoice_date': invoice_date,
                'due_date': payment_due_date,
                'bank_text': bank_text,
                'bank': bank_account
            }

            data_list.append(invoice_data)

        save_invoice_html(data_list)

        print("-" * 140)
        print("\n")
        print(f"{'Sąskaita išrašyta:':<30} {invoice_date}")
        print(f"{'Apmokėti iki:':<30} {payment_due_date}")
        print(bank_text, bank_account, "\n")

    else:
        print(f"Nerasta sąskaitos duomenų kliento ID '{customers_ids}' periodui '{period_id}'\n"
              f"gal dar nesuformavote sąskaitos?")
