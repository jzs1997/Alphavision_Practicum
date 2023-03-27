import os
import sys, argparse, getopt
from pathlib import Path
from typing import List
import typing 

from file_reader import FileLoader
from data_preparation import DataPreparation
import pandas as pd
import gc
import output
from collections import defaultdict
import Calculation

# Mode:
## -readone: load a data file of a certain property, must claim the type of property
## -readall : load all data files and do the calculation, output will be seperate files


# basic settings, every time a new data set is added, adding the property type, rules and path for data set here
PROPERTY_TYPE_LIST = [
    'Office',
    'Apartment',
]


PROPERTY_RECOGNIZATION_RULES = {
    'Office' : ['Yr Built', 'sf', 'Latitude', 'Longitude'],
    'Apartment' : ['Yr Built', 'Units', 'Latitude', 'Longitude']
}

DATA_PATHS = {
    'Office' : 'data/office/dataset_office.csv',
    'Apartment' : 'data/apartment/dataset_apartment.csv'
}

DEFAULT_TYPE = 'all'
DATA_FOLDER = 'data'
DATA_HOME = Path(__file__).parent.parent

# path for cpi data, usually fixed 
CPI_DATA_PATH = 'CPI.csv'


# main part of the code
def progStart(property_type):
    encodings = ('utf-8-sig', None)
    # load data 
    files = FileLoader(CPI_DATA_PATH, DATA_PATHS[property_type],property_type,PROPERTY_RECOGNIZATION_RULES[property_type],encodings)
    cpi_data = files.data_container['CPI']
    sales_data = files.data_container['Sales']
    # prepare the data 
    sales_data = DataPreparation().salesDataClean(sales_data)
    # name the output dir and file
    file_output = 'output_' + str(property_type) + '.csv'
    dir_path = 'noi_info' + str(property_type)
    name_xirr = defaultdict()
    # variable to tag the sample with descreasing xirr
    flag = 0
    
    # calculate xirr
    for property_name in list(sales_data.keys()):
        flag = 0
        # calculate time differece between two sales
        timeDiffAdded = Calculation.computeTimeDiff(sales_data[property_name])
        # calculate noi
        noiAdded, flag = Calculation.noiCalculation(timeDiffAdded, cpi_data)
        print(noiAdded)
        # calculate cashflow
        cashFlowAdded = Calculation.cashFlowCalculation(noiAdded)
        first_price, second_price, time = Calculation.getTimeandPrice(cashFlowAdded)
        rets = Calculation.getItems(cashFlowAdded)
        # save the numbers
        name_xirr[property_name] = (Calculation.xirrCalculation(cashFlowAdded), flag, first_price, second_price, time) + rets
        # output the noi info of transactions
        output.save_one_pandas(dir_path, property_name, cashFlowAdded)
    # output the xirr info
    names = ['xirr', 'flag', 'first_sale_price','second_sale_price','time', 'first_sale_date', 'second_sale_date', 'year_built', 'lat', 'long']
    output.save_output(file_output, name_xirr, names)
    for name, xirr in name_xirr.items():
        print(name)
        print(xirr)
        print('==========================================')

# start the program
def launch(property_types: typing.Union[list,str]):
    if(isinstance(property_types, str)):
        progStart(property_types)
    if(isinstance(property_types, list)):
        for property_type in property_types:
            progStart(property_type)
    print('Done!')

# build rules
# abondoned now, may be useful in the future
def constructRules(rule_list : List)->str:
    return '_'.join(rule_list)

# command line helper
def usage():
    print("\n This is the usage function\n")
    print("Usage: {} -i <file> [option]".format(sys.argv[0]))

# mode 1 : only show xirr for one property type
def readone():
    property_type = input("Please input the property type of which the Xirr will be computed\n")
    
    if property_type not in PROPERTY_TYPE_LIST:
        raise RuntimeError("property type not found")
    
    # data_path = DATA_PATHS[property_type]
    launch(property_type)

# mode 2 : show the xirr for all the property types listed in PROPERTY_TYPE_LIST
def readall():
    launch(PROPERTY_TYPE_LIST)

# main function
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', ['help','readone', 'readall'])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    for o, a in opts:
        if o == '--help':
            usage()
            sys.exit()
        elif o == '--readone':
            readone()
        elif o == '--readall':
            readall()
        else:
            assert False, "unhandled option"
        
