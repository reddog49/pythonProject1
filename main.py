# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import csv
from datetime import date
from optionprice import Option
import pandas as pd

from sourcedata import *

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def month_to_number(txt_month):
    num_month=0
    if txt_month.find('JAN') >= 0:
        num_month = 1
    if txt_month.find('FEB') >= 0:
        num_month = 2
    if txt_month.find('MAR') >= 0:
        num_month = 3
    if txt_month.find('APR') >= 0:
        num_month = 4
    if txt_month.find('MAY') >= 0:
        num_month = 5
    if txt_month.find('JUN') >= 0:
        num_month = 6
    if txt_month.find('JUL') >= 0:
        num_month = 7
    if txt_month.find('AUG') >= 0:
        num_month = 8
    if txt_month.find('SEP') >= 0:
        num_month = 9
    if txt_month.find('OCT') >= 0:
        num_month = 10
    if txt_month.find('NOV') >= 0:
        num_month = 11
    if txt_month.find('DEC') >= 0:
        num_month = 12

    return num_month


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# read manually created file with trading type
with open('Type.csv', 'r') as file2:
    reader = csv.reader(file2)
    type_list = []
    for row in reader:
        print(row)
        type_list.append(row)


with open('U7532648.csv', 'r') as file:
    reader = csv.reader(file)
    df = pd.DataFrame(columns=['Symbol', 'Expiry', 'Strike', 'OptionType', 'DaysRemaining', 'CostPrice', 'MarketPrice',
                               'UndPrice', 'Mult', 'Position',
                               'Exposure', 'RetExposure', 'RetMargin', 'AnnRetExposure', 'AnnRetMargin', 'BullBear',
                               'Type', 'Distance'])

    for row in reader:
        if str(row).find('Open Positions')>=0:
            if str(row).find('Summary') >= 0:
                if str(row).find('Options') >= 0:
                    line = list(row)
                    #print (line)
                    #break down the symbol to compenents i.e. 'IGAC 20JAN23 7.5 P'
                    symbol_raw = line[5]
                    #print (symbol_raw)
                    symbol_raw = symbol_raw.split()
                    #print(symbol_raw)
                    symbol = symbol_raw[0]
                    pos_type = "na"
                    for elem in type_list:
                        if elem[0] == symbol:
                            pos_type = elem[1]


                    # date work
                    date_raw = symbol_raw[1]
                    if len(date_raw)>6:
                        exp_day = date_raw[0:2]
                        exp_month = date_raw[2:5]
                        exp_num_month = month_to_number(exp_month)
                        exp_year = date_raw[5:7]
                        exp_date = date(int("20" + exp_year), exp_num_month, int(exp_day))
                    else:
                        exp_day = 15
                        exp_month = date_raw[0:3]
                        exp_num_month = month_to_number(exp_month)
                        exp_year = date_raw[3:5]
                        exp_date = date(int("20" + exp_year), exp_num_month, int(exp_day))
                    #print(exp_date)
                    days_remaining = (exp_date - date.today()).days
                    strike = float(symbol_raw[2])
                    option_type = symbol_raw[3]
                    position = int(line[6])
                    multiplier = int(line[7])
                    cost_price = float(line[8])
                    cost_basis = float(line[9])
                    close_price = float(line[10])
                    value = position * multiplier * close_price
                    exposure = strike * multiplier * abs(position)
                    return_exposure = (abs(value) / exposure) * 100
                    margin_factor = 2
                    return_margin = (abs(value) / (exposure / margin_factor)) * 100
                    ann_return_exposure = 1/(days_remaining/365)*return_exposure
                    ann_return_margin = 1/(days_remaining/365)*return_margin


                    # get the underlying price - manual workarounds hardcoded :(
                    if symbol == 'AMC1': underlying_price = float(getcurrentquote_us('AMC'))
                    elif symbol == 'CSSE1': underlying_price = float(getcurrentquote_us('CSSE'))
                    elif symbol == 'AVAN': underlying_price = float(10)
                    elif symbol == 'ES': underlying_price = float(3772)
                    elif symbol == 'CL': underlying_price = float(92)
                    elif symbol == 'HG': underlying_price = float(3.7)
                    else: #underlying_price = float(getcurrentquote_us(symbol))
                        underlying_price=float(10)

                    distance = underlying_price/strike
                    new_row = {'Symbol': symbol,
                               'Expiry': exp_date,
                               'Strike': strike,
                               'OptionType': option_type,
                               'DaysRemaining': days_remaining,
                               'CostPrice': cost_price,
                               'MarketPrice': close_price,
                               'UndPrice': underlying_price,
                               'Mult': multiplier,
                               'Position': position,
                               'Exposure': exposure,
                               'RetExposure': return_exposure,
                               'RetMargin': return_margin,
                               'AnnRetExposure': ann_return_exposure,
                               'AnnRetMargin': ann_return_margin,
                               'BullBear': "na",
                               'Type': pos_type,
                               'Distance': distance,
                               }
                    #print(symbol, exp_day, exp_month, exp_year, exp_num_month, strike, option_type, position, multiplier, cost_price,
                    #      cost_basis, close_price, value, exposure, days_remaining, return_exposure,
                     #     ann_return_exposure, ann_return_margin)
                    #print('\n')
                    df = df.append(new_row, ignore_index=True)
df["GainLoss"] = (df["CostPrice"]-df["MarketPrice"])*df["Mult"]*df['Position']*-1
df["RemainingGL"] = df["MarketPrice"]*df["Mult"]*df['Position']*-1
df["RemainingGL%"] = df["RemainingGL"]/(df["GainLoss"]+df["RemainingGL"])*100
pd.options.display.float_format = '{:.2f}'.format
df = df.round(2)
df.to_csv('out.csv')


print(df.to_string())
print(df['RemainingGL'].sum())
print(df['Exposure'].sum())
print(df.groupby('Type')['Exposure'].sum())
print(df.groupby('Type').agg(Exposure=('Exposure', 'sum'), RemainingGL=('RemainingGL', 'sum')))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
