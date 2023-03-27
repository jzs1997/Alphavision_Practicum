# README


## Structure of the software
```tree
├── scripts                      
|   ├── interface.py
|   ├── file_reader.py
|   ├── data_preparation.py
|   ├── Calculation.py
|   └── output.py 

├── data
|   ├── CPI
    |   └── CPI.csv
|   ├── Property Data
    |   ├──Apartment.csv
    |   └── Office.csv

├── output
|   ├── output_xirr 
    |   ├──output_Apartment.csv
    |   └── output_Office.csv
|   ├── output_noi_info
    |   ├──noi_info_apartment
    |   └──noi_info_office
```

## Interface.py

+ use command: python interface.py --readall to run the code
+ or you can use python interface.py --readone Apartment, python interface.py --readone Office. This will only do the calculation on single type of property
+ If you do not want the noi information, comment  `output.save_one_pandas(dir_path, property_name, cashFlowAdded)` in line 76

## file_reader.py


+ Cotain a `FileLoader` class 
+ Only need to initialize `FileLoader` class to create an instance
+ The instance will have a `data_contrainer` attribute which contains cpi data and property data
+ Example code:

```python
files = FileLoader(path_cpi_data, path_property_data, property_type, pattern, encodings)

cpi_data = files.data_container['CPI'] # access the cpi data
property_data = files.data_container['Sales'] # access the property data

```

### Structure of script

```tree
├──FileLoader
    ├──__init__
    |   ├── __LoadCpiFile
    |   └── __LoadDataFile
        |   └──__fileter
            |   └──__geiAndAddFeatures
```


### Intro to Functions

#### LoadCpiFile

+ open CPI.csv and transform it to a list of dicts 
+ when  accessing the cpi data, use cpi[year][month-1] to accesss the value you need
### LoadaDataFile

+ open prperty_name.csv and transform it to a list of dicts
+ output example :
```python
{1980_288_32.2252057_-110.8874267 : 
    [
    {'Property ID': '1472816', 'Date': '2015/5/28', 'Property Name': 'Arcadia Park','Price ($)': 17525000.0, 'Cap Rate': 6.1285812, }, 
    {'Property ID': '122279',  'Date': '2006/10/26', 'Property Name': 'Arcadia Park','Price ($)': 16750000.0, 'Cap Rate': 6.0},
    {'Property ID': '17155', 'Date': '2003/11/12', 'Property Name': 'Arcadia Park','Price ($)': 11125000.0, 'Cap Rate': 6.859999999999999, }
    ]}
```
### getAndAddFeatures

+ remove fields which are not needed

### filter 

+ drop sales records of which property type is not the given one
+ drop sales of which status is not 'Sale'
+ group the sales for identical property with given rule
+ return a list of dict which contains all the grouped records for sales


## data_preparation.py 

+ Prepare the data
+ Follows a procedure shown below:
  + split sales into transactions(records), for each transaction we have two sales(rows)
  + add new cols(fields) to each row
  + add new rows to fill the time gap between two sales

### Workflow

+ Filter data by number of sales, if number of sales is less than 2, drop it
+ split data, each record has two sales
+ add new cols 
+ add new rows to fill the time gap

``` python 
#input : 
{1980_288_32.2252057_-110.8874267 : 
    [
    {'Property ID': '1472816', 'Date': '2015/5/28', 'Property Name': 'Arcadia Park','Price ($)': 17525000.0, 'Cap Rate': 6.1285812, }, 
    {'Property ID': '122279',  'Date': '2006/10/26', 'Property Name': 'Arcadia Park','Price ($)': 16750000.0, 'Cap Rate': 6.0},
    {'Property ID': '17155', 'Date': '2003/11/12', 'Property Name': 'Arcadia Park','Price ($)': 11125000.0, 'Cap Rate': 6.859999999999999, }
    ]}
# after going through splitAndFilter()
[
    {
    'Arcadia Park_0 : 
        [{'Date': '2003/11/12', 'Property Name': 'Arcadia Park','Price ($)': 11125000.0, 'Cap Rate': 6.859999999999999,},
        {'Date': '2006/10/26', 'Property Name': 'Arcadia Park','Price ($)': 16750000.0, 'Cap Rate': 6.0}]
    'Arcadia Park_1 :
        [{'Date': '2006/10/26', 'Property Name': 'Arcadia Park','Price ($)': 16750000.0, 'Cap Rate': 6.0}
        {'Date': '2015/5/28', 'Property Name': 'Arcadia Park','Price ($)': 17525000.0, 'Cap Rate': 6.1285812, }],
    }
]

# then go through addFeatures
[
    {
    'Arcadia Park_0 : 
        [{'Date': '2003/11/12', 'Property Name': 'Arcadia Park','Price ($)': 11125000.0, 'Cap Rate': 6.859999999999999,
        'Noi' : 0, 'CashFlow' : 0, 'time_diff' : 0},
        {'Date': '2006/10/26', 'Property Name': 'Arcadia Park','Price ($)': 16750000.0, 'Cap Rate': 6.0,
        'Noi' : 0, 'CashFlow' : 0, 'time_diff' : 0}]
    'Arcadia Park_1 :
        [{'Date': '2006/10/26', 'Property Name': 'Arcadia Park','Price ($)': 16750000.0, 'Cap Rate': 6.0,
        'Noi' : 0, 'CashFlow' : 0, 'time_diff' : 0}
        {'Date': '2015/5/28', 'Property Name': 'Arcadia Park','Price ($)': 17525000.0, 'Cap Rate': 6.1285812,
        'Noi' : 0, 'CashFlow' : 0, 'time_diff' : 0}],
    }
]


# finally go through fillGaps()
# we only use Arcadia Park_0 here
[
    {
    'Arcadia Park_0' : 
        [{'Date': '2003/11/12', 'Property Name': 'Arcadia Park','Price ($)': 11125000.0, 'Cap Rate': 6.859999999999999,
        'Noi' : 0, 'CashFlow' : 0, 'time_diff' : 0},
        # new rows
        {'Date': '2004/11/12', 'Property Name': 'Arcadia Park','Price ($)': 11125000.0, 'Cap Rate': 6.859999999999999,
        'Noi' : 0, 'CashFlow' : 0, 'time_diff' : 0},
        {'Date': '2005/11/12', 'Property Name': 'Arcadia Park','Price ($)': 11125000.0, 'Cap Rate': 6.859999999999999,
        'Noi' : 0, 'CashFlow' : 0, 'time_diff' : 0},
        # new rows end here
        {'Date': '2006/10/26', 'Property Name': 'Arcadia Park','Price ($)': 16750000.0, 'Cap Rate': 6.0,
        'Noi' : 0, 'CashFlow' : 0, 'time_diff' : 0}]
    }
]

```

## Calculation.py

+ Calculate Time difference, noi, cashflow sequencely
+ Compute xirr
+ Tip : The format of input and output in this part is always `list(dict)`, each dict is a trasaction contrains two sales, and we use a list to contain all the transactions 
### Work flow

```python
# input
# the input and output will be always in this format
# and we will add 'time_diff', 'Noi', 'CashFlow' with 
# computeTimeDiff(), NoiCalculation(), cashFlowCalculation()
[
    {
    'Arcadia Park_0' : 
        [{'Date': '2003/11/12', 'Property Name': 'Arcadia Park','Price ($)': 11125000.0, 'Cap Rate': 6.859999999999999,
        'Noi' : 0, 'CashFlow' : 0, 'time_diff' : 0},
        # new rows
        {'Date': '2004/11/12', 'Property Name': 'Arcadia Park','Price ($)': 11125000.0, 'Cap Rate': 6.859999999999999,
        'Noi' : 0, 'CashFlow' : 0, 'time_diff' : 0},
        {'Date': '2005/11/12', 'Property Name': 'Arcadia Park','Price ($)': 11125000.0, 'Cap Rate': 6.859999999999999,
        'Noi' : 0, 'CashFlow' : 0, 'time_diff' : 0},
        # new rows end here
        {'Date': '2006/10/26', 'Property Name': 'Arcadia Park','Price ($)': 16750000.0, 'Cap Rate': 6.0,
        'Noi' : 0, 'CashFlow' : 0, 'time_diff' : 0}]
    }
]

```

### How to calculate time difference, noi and cashflow

time difference : $time\_diff = date2 - date1$

Noi :
1. for the first year, noi is 0
2. For second year, we use the sales price and cap rate for that year to compute the noi for next year. and for the year between second year and last year, the method for calculation depends on the condition of the Cap Rate 
3. for example, assume we have a sample data from 2022/1/1 to 2004/1/1:

```table
Condition 1 : we only have cap rate in the first year

Date | Sales Price | Cap Rate | Noi 
2002/1/1 | 1000    | 0.06     |
2003/1/1 | 1000    |          | 1000 * 0.06
2004/1/1 | 1000    |          | 1000 * 0.06 * (1 + cpi) 
2004/6/1 | 2000    |          | 1000 * 0.06 * (1 + cpi) * (1 + cpi) * time diffierence(0.5)
```

```table
Condition 2 : we only have cap rate in the last year

Date | Sales Price | Cap Rate | Noi 
2002/1/1 | 1000    |          |
2003/1/1 | 1000    |          | 1000 * 0.06 / (1 + cpi) / (1 + cpi) / (1 + cpi)
2004/1/1 | 1000    |          | 1000 * 0.06 / (1 + cpi) / (1 + cpi) 
2004/6/1 | 2000    | 0.06     | 1000 * 0.06 /(1 + cpi) * time diffierence(0.5)
2005/1/1 | 2000    |          | 1000 * 0.06 #start here, but this will not be inlcuded in the final result, just for helping you comprehend how the code works
```

```table
Condition 3 : we have cap rate in both first year and last year

mean_diff = (sales_price_2002 * cap_rate_2002 - sales_price_2004 * cap_rate_2004) / 3

Date | Sales Price | Cap Rate | Noi 
2002/1/1 | 1000    | 0.06     |
2003/1/1 | 1000    |          | 1000 * 0.06
2004/1/1 | 1000    |          | 1000 * 0.06 - mean_diff
2004/6/1 | 2000    | 0.05     | (1000 * 0.06 - mean_diff) * time_diff
```


## Output.py

+ Save noi info and xirr info
+ use pandas and csv

### save_one_pandas
+ Save records

### save_output
+ save xirr
+ flag = 1 means noi increases evenly, -1 mean noi decrese evenly, 0 means only have 1 cap rate so we use cpi to inflate or deflate noi

