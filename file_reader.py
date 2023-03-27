import csv
from genericpath import isdir
import os
import typing 
import collections


class FileLoader():
    def __init__(self, cpi_file_path: str, data_file_path : str, property_type : str,  pattern: list, encodings : typing.Union[str, tuple, list, None] = None):
        '''
        cpi_file_path : path of cpi file
        data_file_path : path of property data
        property_type : type of property, specified at interface.py
        pattern : keywords for identical property recognization
        encodings : encodings for data file
        
        
        This class load data files and do simple data cleaning work, 
        preparing data for xirr calculation
        
        How to use:
            return an instance containing a dict called 'data contrainer'
            Users can access the cpi data and property data with this dict
            
        '''
        self.cpi_file_path = cpi_file_path
        self.data_file_path = data_file_path
        self.pattern = pattern
        self.property_type = property_type
        
        # encoding settings
        if encodings is None:
            self.encoding_cpi_file = 'utf-8-sig'
            self.encoding_data_file = 'utf-8-sig'
        elif isinstance(encodings, str):
            self.encoding_cpi_file = encodings
            self.encoding_data_file = encodings
        else:
            self.encoding_cpi_file = encodings[0]
            self.encoding_data_file = encodings[1]
        
        # put data into data container
        self.data_container = collections.defaultdict()
        self.data_container['CPI'] = self.__loadCpiFile()
        self.data_container['Sales'] = self.__loadDataFile()
        
    def __loadCpiFile(self):
        # This method can not be accessed externally
        # Load files from given path
        yearly_cpi_in_month_dict = {}
        with open(self.cpi_file_path, encoding=self.encoding_cpi_file) as cpi_file:
            Rows = csv.DictReader(cpi_file, delimiter=',')
            for row in Rows:
                row_list = []
                year_key = list(row.keys())[0]
                months_key = list(row.keys())[1:]
                year = row[year_key]
                for month_key in months_key:
                    row_list.append(row[month_key])
                yearly_cpi_in_month_dict[int(year)] = row_list
        return yearly_cpi_in_month_dict
    
    def __loadDataFile(self):
        # This method can not be accessed externally
        # Load files from given path
        with open(self.data_file_path, encoding = self.encoding_data_file) as data_file:
            Rows = csv.DictReader(data_file, delimiter=',')
            sales_info_dict = self.__filter(Rows)
            
        return sales_info_dict

    def __geiAndAddFeatures(self, row : dict):
        '''
        select and add cols for data
        select: Property ID, Status, Type, Date, Property Name, Address, sf, Price ($), Units, Yr Built, Cap Rate, Latitude, Longtitude
        add : NOI, time_diff
        '''
        # Here we delete the cols in list 'item_to_remove'
        item_to_remove = ['Deal ID', 'Market', 'Distance', 
                          'City', 'State', 'Country', 'Postal Code', 
                          'Yr Renov', 'Est Completion', '# Bldgs', 
                          '# Floors', 'Land Area (acres)', 'Occupancy',
                          'Prop/Deal', 'Currency', '$/Units', '$/sf',
                          'Price Qualifier', 'Partial Interest', 'Partial Inv Vol ($)',
                          'Cap Rate Qualifier', 'Owner/Buyer', "Buyer's Broker", 'Seller',
                          "Seller's Broker", 'Lender', 'Comments or Notes', 
                          'MSA', 'CBSA', 'APN', 'Deed', 'Beds', 'Tenants', 'Submarket', 'County'
                          ]
        
        for key in item_to_remove:
            row.pop(key, None)
        return row 
        
    def __filter(self, Rows):
        # filter, set the rules of filering here. 
        sales_info_dict = {}
        for row in Rows:
            
            row_list = []
            
            type_ = row["Type"]
            # city = row["City"]
            # state = row["State"]
            # yearBuilt = row['Yr Built']
            # latitude = row["Latitude"]
            # longitude = row["Longitude"]
            # sf = row["sf"]
            # units = row["Units"]
            status = row["Status"]
            
            
            yearBuilt = row[self.pattern[0]]
            units = row[self.pattern[1]]
            latitude = row[self.pattern[2]]
            longitude = row[self.pattern[3]]
            
            # if sale price is not present marking it to 0
            row["Price ($)"] = row["Price ($)"].replace(",", "")
            if row["Price ($)"] == "" or row["Price ($)"] == 'n/a':
                row["Price ($)"] = "0"
                
            try:
                row["Price ($)"] = float(row["Price ($)"])
            except:
                row["Price ($)"] = 0.0
            
            row["Cap Rate"] = row["Cap Rate"].replace("%", "")
            
            try:
                row["Cap Rate"] = float(row["Cap Rate"])
            except:
                row["Cap Rate"] = 0.0
            
            if(row["Cap Rate"] < 1):
                row["Cap Rate"] = row["Cap Rate"] * 100
            
            row["Cap Rate"] = round(row["Cap Rate"], 3)
            # filtering data based on given condition
            # if type == "Apartment" and city == "Tucson" and state == "AZ" and status == 'Sale':
            
            if type_ == self.property_type and status == 'Sale':
                key = yearBuilt + "_" + units + "_" + latitude + "_" + longitude
                if sales_info_dict.get(key) is not None:
                    row_list = sales_info_dict.get(key)
                        
                row_list.append(self.__geiAndAddFeatures(row))
                sales_info_dict[key] = row_list
        return sales_info_dict
    
    
if __name__ == '__main__':
    # test case, path may need to be reset to run this test case
    import pandas as pd
    import os
    cpi_path = '../Final_Code_and_Dataset/CPI.csv'
    data_path = '../Final_Code_and_Dataset/Dataset_apartment.csv'
    encodings = ('utf-8-sig', None)
    pattern = ['Yr Built', 'Units', 'Latitude', 'Longitude']
    files = FileLoader(cpi_path, data_path, 'Apartment', pattern, encodings)
    
    cpi_data = files.data_container['CPI']
    sales_data = files.data_container['Sales']
    
    for keys, item in sales_data.items():
        print(keys)
        print(item)
    
    if not os.path.isdir('origins'):
        os.mkdir('origins')
        
    for key, item in sales_data.items():
        df = pd.DataFrame(item)
        names = set()
        for d in item:
            names.add(d['Property Name'])
        
        name = ""
        for n in names:
            name += (n + "_")
        fname = name + key
        
        df.to_csv(os.path.join('origins', fname+'.csv'))