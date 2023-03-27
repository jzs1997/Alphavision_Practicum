from collections import defaultdict
from datetime import datetime
from msilib.schema import Error
import typing
from data_preparation import DataPreparation
from pyxirr import xirr 


#   def computeTimeDiff(Rows: list[dict])->list[dict]: calculate time diff for cpi calculation to use
#   def noiCalculation(Rows: list[dict])->list[dict]: calculate noi for each year, forward or backward 
#   def cashFlowCalculation(Rows: list[dict])->list[dict]: calculate cash flow, use sale price for first year, use sales price + noi - sales cost for last year
#   def xirrCalculation(Property_info: dict[str, list[dict]])->dict: calculate xirr for each property

def check(Rows : list[dict]):
    # a function that checks the format of output
    for row in Rows:
        if(isinstance(row, dict) == False):
            print('Not a dict')
            print(Rows)
            raise Error

def sort(Rows : list[dict]):
    # Sort Rows by time
    Rows = sorted(Rows, key=lambda row: datetime.strptime(row["Date"], "%Y/%m/%d"))
    return Rows

def timeDiffCalculation(date1 : str, date2: str)-> float:
    # Given date1 and date2, computes the time difference, 
    # date2 must be the date later than date1
    
    def isLeap(year : typing.Union[int, float]):
        # identify whether a year is a leap year
        is_leap = False
        if(year % 400 == 0):
            is_leap = True
        else:
            if(year % 4 == 0):
                is_leap = True
        return is_leap
    
    
    
    time_diff = 0.0
    date1 = datetime.strptime(date1, "%Y/%m/%d")
    date2 = datetime.strptime(date2, "%Y/%m/%d")
    
    year = date2.year
    days_ = 366 if isLeap(year) == True else 365
    time_diff = (date2 - date1).days / days_ 
    
    return time_diff

def computeTimeDiff(Rows: list[dict])->list[dict]:
    # Applying function 'timeDiffCalculation'
    for i in range(1, len(Rows)):
        date1, date2 = Rows[i-1]['Date'], Rows[i]['Date']
        Rows[i]['time_diff'] = timeDiffCalculation(date1, date2)
    
    return Rows


def capRateStatus(Rows: list[dict])->int:
    
    # Identify the locations and numbers of cap rate
    # Decide which method(forward or backward) to use to compute noi
    
    status = 0
    capRate1 = Rows[0]['Cap Rate']
    capRate2 = Rows[-1]['Cap Rate']
    
    # statues -1, shrink the noi from later time to former time
    if(capRate1==0 and capRate2!=0):
        status = -1
    # status 1, inflate noi from former time to later time
    if(capRate1!=0 and capRate2==0):
        status = 1
    # status 2, inflate noi from former time to later time
    if(capRate1!=0 and capRate2!=0):
        status = 2
    
    return status 

    
def noiCalculation(Rows: list[dict], cpi_data):
    # compute noi based on the status code returned by function 'CapRateStatus'
    # For the first and last row we do not need to inflate, we need to use cap rate multiples price to compute the noi
    # for others we use cpi to inflate or deflate
    flag = 0
    status = capRateStatus(Rows)
    check(Rows)
    print(Rows)
    if(status == 1):
        noiFirst = Rows[0]['Cap Rate'] * 0.01 * Rows[0]['Price ($)']
        Rows[0]['Noi'] = noiFirst
        for i in range(1, len(Rows)):
            cpi = DataPreparation().cpiCalculation(Rows[i-1]['Date'], Rows[i]['Date'], '%Y/%m/%d', cpi_data)
            Rows[i]['Noi'] = Rows[i-1]['Noi'] * (1 + cpi/100)
            
        
    elif(status == -1):
        noiLast = Rows[len(Rows)-1]['Cap Rate'] * 0.01 * Rows[len(Rows)-1]['Price ($)']
        Rows[len(Rows)-1]['Noi'] = noiLast
        for i in reversed(range(0, len(Rows)-1)):
            cpi = DataPreparation().cpiCalculation(Rows[i]['Date'], Rows[i+1]['Date'], '%Y/%m/%d', cpi_data)    
            Rows[i]['Noi'] = Rows[i+1]['Noi'] / ((1 + cpi/100))
    
    
    elif(status == 2):
        noiFirst = Rows[0]['Cap Rate'] * 0.01 * Rows[0]['Price ($)']
        noiLast_ = Rows[len(Rows)-1]['Cap Rate'] * 0.01 * Rows[len(Rows)-1]['Price ($)']
        # noiLast = Rows[len(Rows)-1]['Cap Rate'] * 0.01 * Rows[len(Rows)-1]['Price ($)']
        Rows[0]['Noi'] = noiFirst
        Rows[len(Rows)-1]['Noi'] = noiLast_
        mean_diff = (noiFirst - noiLast_)/(len(Rows) - 1)
        for i in range(1, len(Rows)):
            Rows[i]['Noi'] = Rows[i-1]['Noi'] - mean_diff
        if(noiFirst > noiLast_):
            flag = -1
        else:
            flag = 1
        
    else:
        print("Error!!!!!")

    for i in reversed(range(1, len(Rows))):
        Rows[i]['Noi'] = Rows[i-1]['Noi']
    Rows[0]['Noi'] = 0
    Rows[len(Rows)-1]['Noi'] = Rows[len(Rows)-1]['Noi'] * Rows[len(Rows)-1]['time_diff']
    return Rows, flag 

def cashFlowCalculation(Rows: list[dict]):
    # for first year cash flow = -price
    # for last year, cash flow = noi + price - sales cost
    # for the years in between: cash flow = noi
    Rows[0]['CashFlow'] = Rows[0]['Price ($)'] * (-1)
    # print(Rows)
    Rows[len(Rows)-1]['CashFlow'] = Rows[len(Rows)-1]['Price ($)'] * 0.98 + Rows[len(Rows)-1]['Noi']
    if(len(Rows) > 2):
        for i in range(1, len(Rows)-1):
            Rows[i]['CashFlow'] = Rows[i]['Noi'] 
    return Rows



def xirrCalculation(Rows: list[dict]):
    # using pyxirr to compute xirr on given cash flow
    def xirrCal(Rows: list[dict])->float:
        dates, cashFlow = [], []
        
        for row in Rows:
            dates.append(datetime.strptime(row['Date'], '%Y/%m/%d'))
            cashFlow.append(row['CashFlow'])
        
        # print(Rows[0]['Property Name'])
        # print(dates)
        # print(cashFlow)
        return xirr(dates, cashFlow)
    
    try:
        xirr_ = xirrCal(Rows)
    except:
        # print("Error on computing xirr for {}".format(property_name))
        # print(Rows)
        xirr_ = 0.0
    
    return xirr_

def getItems(Rows : list[dict]):
    first_sale_date = Rows[0]['Date']
    second_sale_date = Rows[-1]['Date']
    year_built = Rows[0]['Yr Built']
    lat = Rows[0]['Latitude']
    long = Rows[0]['Longitude']

    return (first_sale_date, second_sale_date, year_built, lat, long)

def getTimeandPrice(Rows: list[dict]):
    first_sale_price = Rows[0]['Price ($)']
    last_sale_price = Rows[-1]['Price ($)']
    time = sum([row['time_diff'] for row in Rows])
    return first_sale_price, last_sale_price, time
    
if __name__ == '__main__':
    import os 
    import csv 
    from file_reader import FileLoader
    from data_preparation import DataPreparation
    import pandas as pd
    import gc
    
    # test case, need to be improved
    def create_dir(path, dirname)-> str:
        dir_path = os.path.join(path, dirname)
        if(os.path.isdir(dir_path)):
            print('Dir {} already exists' .format(dirname))
        else:
            os.mkdir(dir_path)
    
        return dir_path
    
    def save_one(dir_path, property_name, Rows):
        dir_noi_info = create_dir('', dir_path)
        name_list = property_name.split('_')
        name_ = name_list[0] + name_list[-1] + '.csv'
        file_name = os.path.join(dir_noi_info, name_)
        fieldnames = list(Rows[0].keys())
        with open(file_name, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in Rows:
                writer.writerow(row)
                    
    def save_all(dir_path, data):
        dir_noi_info = create_dir('', dir_path)
        for name, info in data.items():
            name_list = name.split('_')
            name_ = name_list[0] + name_list[-1] + '.csv'
            file_name = os.path.join(dir_noi_info, name_)
            fieldnames = list(info[0].keys())
            with open(file_name, 'w') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in info:
                    writer.writerow(row)
                    
    def save_one_pandas(dir_path, property_name, Rows):
        dir_noi_info = create_dir('', dir_path)
        name_list = property_name.split('_')
        name_ = name_list[0] + name_list[-1] + 'pd' + '.csv'
        file_name = os.path.join(dir_noi_info, name_)
        df = pd.DataFrame(Rows)
        df.to_csv(file_name, index=False)
        del df
        gc.collect()
        
    cpi_path = '../Final_Code_and_Dataset/CPI.csv'
    data_path = '../Final_Code_and_Dataset/Dataset.csv'
    encodings = ('utf-8-sig', None)
    
    files = FileLoader(cpi_path, data_path, encodings)
    
    cpi_data = files.data_container['CPI']
    sales_data = files.data_container['Sales']
    
    sales_data = DataPreparation().salesDataClean(sales_data)
    # for key, values in sales_data.items():
    #     print(key)
    #     print(values)
    #     print('================================')
    
    file_output = 'output_office.csv'
    dir_path = 'noi_info'
    
    
    name_xirr = defaultdict()
    #ds = []
    flag = 0
    for property_name in list(sales_data.keys()):
        # check(sales_data[property_name])
        timeDiffAdded = computeTimeDiff(sales_data[property_name])
        # check(timeDiffAdded)
        noiAdded, isDeclined = noiCalculation(timeDiffAdded, cpi_data)
        if(isDeclined == True):
            flag = 1
        else:
            flag = 0
        print(noiAdded)
        cashFlowAdded = cashFlowCalculation(noiAdded)
        # tagDecliningNoi(property_name, cashFlowAdded)
        name_xirr[property_name] = (xirrCalculation(cashFlowAdded), flag)
        save_one_pandas(dir_path, property_name, cashFlowAdded)
        # print(property_name)
        # for row in cashFlowAdded:
        #     print(row)
        # if(cashFlowAdded[-1]['CashFlow'] < 0):
        #     print(cashFlowAdded)
        #     print('+++++++++++++++++++++++++++++++++++')
        # print('===========================')
        # sales_data[property_name] = cashFlowAdded

    # for name, rows in sales_data.items():
    #     print(name)
    #     print(rows)
    #     print('=++++++++++++++++++++++++=============')

    for name, xirr in name_xirr.items():
        print(name)
        print(xirr)
        print('==========================================')
    
    
    def save_output(file_output, data:dict)->None:
        name_list = [key for key in list(data.keys())]
        xirr_list = [data[key][0] for key in list(data.keys())]
        ds = [data[key][1] for key in list(data.keys())]
        df = pd.DataFrame({
            'Property_Name': name_list,
            'Xirr' : xirr_list,
            'is_Declined' : ds
        })
        
        df.to_csv(file_output)
        del df
        gc.collect()
        
    save_output(file_output, name_xirr)