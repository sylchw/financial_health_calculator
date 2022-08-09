#Imports
import pandas as pd
import numpy as np
from yahooquery import Ticker
from datetime import datetime
import time
import traceback
import requests
from bs4 import BeautifulSoup
import time

def get_fcf_yoy_growth(stock):
    value = ''
    try:
        page = requests.post(f'https://www.macrotrends.net/stocks/charts/{stock}/apple/free-cash-flow')
        html = page.text
        soup = BeautifulSoup(html, 'html.parser')
        # fcf_list = soup.find_all(text='annual free cash flow for')
        website_string = soup.get_text()

        #find location of percentage
        interested_chunk = 'annual free cash flow'
        index = website_string.find(interested_chunk)

        postprocessed_chunk = website_string[index+len(interested_chunk): index+len(interested_chunk)+50]
        percentage_location = postprocessed_chunk.find('%')
        percentage = postprocessed_chunk[0:percentage_location].split(' ')
        value = percentage[len(percentage)-1]
    except:
        print(f'fcf yoy percentage for {stock} failed to retrieve')

    return value

def check_existence(stock):
    skip = False
    result = Ticker(stock).price[stock]
    if "Quote not found for ticker symbol:" in result:
        print(stock, " is not found/recognized, SKIPPING")
        skip = True
    return skip

def get_DebtToEquity_OperatingMargin(stock):
    tick = Ticker(stock)
    dTE = tick.financial_data[stock]['debtToEquity']
    OM = tick.financial_data[stock]['operatingMargins']
    result_dTE = reuslt_OM = 'No Data'
    if dTE is not None:
        result_dTE = dTE
    if OM is not None:
        result_OM = OM
    return result_dTE, result_OM

def express_in_MM(number):
    return number/1_000_000

def change_to_dictionary(data_list):
    return_dict = {}
    for i, col_name in enumerate(list_of_columns):
        return_dict[col_name] = data_list[i]
    return return_dict

def get_all_data(stock):
    company_name = stock
    debt_to_equity, operating_margin = get_DebtToEquity_OperatingMargin(stock)
    fcf_yoy_growth = get_fcf_yoy_growth(stock)
    ordered_list = [company_name, debt_to_equity, operating_margin, fcf_yoy_growth]
    return ordered_list


if __name__ == "__main__":
    try:
        #Initialize dataframe
        list_of_columns = ['Company','Debt to Equity', 'Operating Margin', 'Annual Free Cash Flow Growth %']

        df_main = pd.DataFrame(columns = list_of_columns)


        #Get input by typing or from a csv
        csv_input_option = input('Input companies via CSV?: (type only "yes" or "no")')
        if csv_input_option == 'yes':
            csv_dir = input('Paste full file path here: ')
            print("Entered directory: ", csv_dir)
            try:
                csv_list = pd.read_csv(csv_dir, header=None)
                companies_list = list(csv_list[0])
            except:
                print("File not found, please restart application")
        elif csv_input_option == 'no':
            companies_string = input('Type in companies stock ticker concatenanted by comma: ')
            companies_list = list(companies_string.split(","))
        else:
            print("Invalid input, please restart application")
            
        print("Companies to be calculated: ", companies_list)

        #Loop through original list and perform the shit
        for company in companies_list:
            if check_existence(company):
                continue
            print("Getting data for: ", company)
            company_data_dict = change_to_dictionary(get_all_data(company))
            df_result_temp = pd.DataFrame(company_data_dict, index=[0])
            df_main = pd.concat([df_main,df_result_temp], ignore_index=True)


        #replace empty strings with nan for mean calculation
        df_main = df_main.replace(r'^\s*$', np.nan, regex=True)

        # #Calculate Averages
        # print("Calculating averages")
        # list_of_columns_to_calculate_average = ['EBITDA/EBIT MARGIN (%)','EBITDA/EBIT PROJ GROWTH (%)','EV/REVENUE (x)',
        #                                             'EV/EBITDA (x)','EV/EBIT (x)','PEG 5Y Expected(x)']

        # average_row_dict = {}
        # for col_name in list_of_columns:
        #     if col_name == 'COMPANY NAME':
        #         average_row_dict[col_name] = 'Average/Median'
        #     elif col_name in list_of_columns_to_calculate_average:
        #         print(col_name)
        #         average_row_dict[col_name] = df_main[col_name].mean()
        #     else:
        #         average_row_dict[col_name] = None

        # df_result_temp = pd.DataFrame(average_row_dict, index=[0])
        # df_main = pd.concat([df_main,df_result_temp], ignore_index=True)

        # #Calculate Relative Company Value
        # df_main['Relative Fair Value'] = ((df_main.iloc[len(df_main)-1]['EV/EBIT (x)'] * df_main['EBIT ($M)'] * 1_000_000) - df_main['TOTAL DEBT ($M)'] * 1_000_000)/df_main['OUTSTANDING SHARES']
        # list_of_columns.append('Relative Fair Value')
        
        # #Convert types to float
        # for convert_type_col in list_of_columns[1:]:
        #     df_main[convert_type_col] = df_main[convert_type_col].astype(float)

        # #Change the values to 2 decimal place
        # df_main = df_main.round(2)

        print("Results preview")
        print(df_main.head())

        #save the file
        today = str(datetime.now())
        today = today.replace(":", ".")

        #Export to excel
        result_save_folder = input("Enter result save folder, or leave blank for same location: ")
        if result_save_folder == '':
            df_main.to_excel(today+".xlsx", sheet_name='Financial_Health_results')
            print("Results saved to: ", today+".xlsx")
        else:
            df_main.to_excel(result_save_folder+'//'+today+".xlsx", sheet_name='Financial_Health_results')
            print("Results saved to: ", result_save_folder+'//'+today+".xlsx")

        time.sleep(5)
    except Exception:
        print(traceback.format_exc())
        print("If you don't understand the error please show it to the developer")
        time.sleep(100)