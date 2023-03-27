from isort import file
import pandas as pd
import time
import sys, argparse, getopt
import os 
from interface import usage
import datetime

OUTPUT_DIR_PATH = ''
OUTPUT_FILES_PATH = {
    'office' : 'output_Office.csv',
    'apartment' : 'output_Apartment.csv',
}

RES_OUT_DIR = 'output'

def weighted_average(df):
    price = df['first_sale_price'] / 10000
    time_ = df['time']
    xirr = df['xirr']
    ave = (xirr * time_ * price / (price * time_).sum()).sum()
    
    return ave

def select(date, years, df):
    if(date == ''):
        date = datetime.datetime.today()
    else:
        date = datetime.datetime.strptime(date, "%Y/%m/%d")

    years = int(years)
    endyear = date.year
    startyear = endyear - years
    
    df = df[(df.first_sale_date.dt.year<=endyear) & (df.first_sale_date.dt.year>=startyear)]
    df.to_csv(os.path.join(RES_OUT_DIR, 'tmp{}.csv'.format(years)))
    
    print("weight average: ")
    print(weighted_average(df))
    return 
    
def main_run(property_type, df):
    q = True
    while(q):
        date = input("input the date(press enter for using date for today or press q to quit): \n")
        years = input("input the number of year")
        
        if(date == 'q'): break
        select(date, years, df)
        
    print('end')
    return 

def start(property_type):
    file_path = os.path.join(OUTPUT_DIR_PATH, OUTPUT_FILES_PATH[property_type])
    df = load_output(file_path)
    df['first_sale_date'] = pd.to_datetime(df['first_sale_date'])
    df['second_sale_date'] = pd.to_datetime(df['second_sale_date'])
    main_run(property_type, df) 
    

def load_output(file_path):
    return pd.read_csv(file_path)


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', ['help','apartment', 'office'])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    
    
    for o, a in opts:
        if o == '--help':
            usage()
            sys.exit()
        elif o == '--apartment':
            start('apartment')
        elif o == '--office':
            start('office')
        else:
            assert False, "unhandled option"

    
    

