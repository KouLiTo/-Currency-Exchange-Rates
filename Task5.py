# коди по країнам я скрапив з https://www.iban.com/currency-codes

import sqlite3
from lxml import html
from urllib import request
import datetime
import sys
import json

sql_db = "exchange_db"
conn = sqlite3.connect(sql_db)
try:
    conn.execute('CREATE TABLE "currency_data"(id integer PRIMARY KEY, currency_name, currency_value, current_date)')
    conn.commit()
except Exception:
    pass


def insert_intoDB(tup):
    conn.execute(f"""INSERT INTO currency_data(currency_name, currency_value, current_date)
                     VALUES{tup}
""")
    conn.commit()


def read_codes():
    with open(cc_name, "r") as f:
        cur_codes = json.load(f)
        return cur_codes


cc_name = "currency_codes.json"

try:
    cur_codes = read_codes()
except Exception:
    print("Wait a minute. Data is being collected")
    response1 = request.urlopen("https://www.iban.com/currency-codes")
    tree = html.fromstring(response1.read())
    elements = tree.xpath("""/html/body/div/div[2]/div/div/div/div/table/tbody/tr[*]/td[3]""")
    elements_ = tree.xpath("""/html/body/div/div[2]/div/div/div/div/table/tbody/tr[*]/td[4]""")
    with open(cc_name, "w") as f:
        json.dump({k.text: v.text for k, v in zip(elements, elements_)}, f, indent=4)
    cur_codes = read_codes()



cur_codes_formated = {k: int(v) for k, v in cur_codes.items() if isinstance(v, str)}  # creates dict with codes from
                                                                                # data parsed from iban.com

try:
    response = request.urlopen("https://api.monobank.ua/bank/currency")   # sending request to monobank
except Exception:
    print("Error. Too many requests. Try again later")
    sys.exit()
else:
    data_ = eval(response.read().decode())    # getting response from Monobank, it takes upto 10 seconds


def amount_float():
    try:
        a = float(input("Enter amount to exchange: "))
    except ValueError:
        print("It must be a float number. Try again")
        return amount_float()
    return a



def codesA_B(arg):
    for k, v in cur_codes_formated.items():
        if k == arg:
            return v


while True:
    count = 0
    currency1 = input("Enter currency in the international format (ex. USD) or 'exit' to exit: ").upper()
    if currency1 == "EXIT":
        break
    else:
        currency2 = input("Enter currency to convert in: ").upper()
        amount = amount_float()
        for i in data_:
            if isinstance(i, dict):
                if i["currencyCodeA"] == codesA_B(currency1) and i["currencyCodeB"] == codesA_B(currency2):
                    print(f"Current rates: {currency1} = {i['rateBuy']} {currency2}")
                    print(f"Your amount after exchange: {round(amount * i['rateBuy'], 2)} {currency2}")
                    print(f"Date: {datetime.datetime.now()}")
                    count += 1
                    insert_intoDB((currency2, i['rateBuy'], str(datetime.datetime.now())))
                    print("Printed from sql_db:")
                    for item in conn.execute('SELECT * FROM "currency_data"').fetchall():
                        print(item)
                    break
    if count == 0:
        print("The pair is not supported. Try another one (ex. USD-UAH, EUR-UAH)")
