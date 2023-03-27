from datetime import datetime

class DataPreparation():

    '''
    Function 'salesDataClean' and function 'cpiCalculation' are main functions in this class
    call 'cpiCalculation' to calculate the cpi 
    call 'salesDataClean' to prepare the property data
    '''
    
    def __init__(self):
        self.featuresToAdd = ['Noi', 'CashFlow', 'time_diff']
        
    
    def cpiCalculation(self, date1 : str, date2 : str, date_format: str, cpi_data)-> float:
        # Give two dates and cpi data, computing the cpi
        # date2 should be the date later than date1 
        # format of data can be specified, but must be the same as the format in data file
        d1 = datetime.strptime(date1, date_format)
        d2 = datetime.strptime(date2, date_format)
        
        d1_month = d1.month; d1_year = d1.year; d2_month = d2.month; d2_year = d2.year
        
        cpi1, cpi2 = 0.0, 0.0
        

        if not cpi_data[d1_year][d1_month - 1]:
            cpi1 = 0.0
        else:
            cpi1 = float(cpi_data[d1_year][d1_month - 1])

        if d2_year in cpi_data:
            if not cpi_data[d2_year][d2_month - 1]:
                cpi2 = 0.0
            else:
                cpi2 = float(cpi_data[d2_year][d2_month - 1])

        if cpi1 == 0.0 or cpi2 == 0.0:
            return 0.0

        perCalculated = (cpi2 / cpi1 - 1) * 100

        perDefault = 4
        minPer = perCalculated if perCalculated < perDefault else perDefault
        return minPer + 1
    
    def splitAndFilter(self, Rows : dict[str, list[dict]])-> dict[str, list[dict]]:
        # drop record with only one sale
        Rows = self.filterByLength(Rows)        
        newRows = {}
        
        # if number of sales > 3, split and rename, then put it into 
        # for each record check number of cap rate
        # sort the rows by date for each record
        for key, values in Rows.items():
            if(len(values) == 2):
                newKey = values[0]['Property Name'] + '_' + key + '_' + '0'
                newRows[newKey] = sorted(values, key=lambda row: datetime.strptime(row["Date"], "%Y/%m/%d"))
        
            if(len(values) > 2):
                index = 0
                for i in range(len(values)-1):
                    values = sorted(values, key=lambda row: datetime.strptime(row["Date"], "%Y/%m/%d"))
                    newKey = values[0]['Property Name'] + '_' + key + '_' + str(i)
                    v = [values[i], values[i+1]]
                    newRows[newKey] = v
            #check valid cap rate
            
            for key in list(newRows.keys()):
                if(self.isValid(newRows[key]) == False):
                    newRows.pop(key, None)
        
        return newRows 
        
    def filterByLength(self, Rows : dict[str, list[dict]])-> dict[str, list[dict]]:
        # drop records with only one sale 
        for key in list(Rows.keys()):
            if(len(Rows[key]) < 2):
                Rows.pop(key, None)
        return Rows
    
    def isValid(self, rows_for_single_record: list[dict])-> bool:
        capCount = 0
        # Condition 2: At least two sales prices needs to be present and 1 noi or cap rate needs to be present.
        for row in rows_for_single_record:
            if row['Cap Rate'] != 0.0:
                capCount+=1
        # condition 1: current sales price is less than previous sales price and no cap rate present , then filter
        if(rows_for_single_record[1]['Price ($)'] < rows_for_single_record[0]['Price ($)'] and rows_for_single_record[1]['Cap Rate'] == 0):
            return False 
        return True if capCount >0 else False 
    
    def fillGaps(self, Rows: dict[str, list[dict]])->dict[str, list[dict]]:
        # apply 'fillGap' on all the properties
        for key, values in Rows.items():
            newValues = self.fillGap(values)
            Rows[key] = newValues
        
        return Rows
    
    def fillGap(self, values: list[dict])->list[dict]:
        '''
        As we have splitted sales into transactions, we may have transaction information like this:
        {A : [
            {date: 2000/1/1, others},
            {date: 2003/1/1, others},
        ]}
        
        by calling fillGap we insert new rows(actually the copies of the first row, but changing the date)
        between the two sales to fill the time gap. The returned object will be like this:
        
        {A : [
            {date: 2000/1/1, others},
            {date: 2001/1/1, others},
            {date: 2002/1/1, others},
            {date: 2003/1/1, others},
        ]}
        
        '''        
        
        start_time, end_time = datetime.strptime(values[0]['Date'], "%Y/%m/%d"), datetime.strptime(values[1]['Date'], "%Y/%m/%d")
        start_year, end_year = start_time.year, end_time.year
        end = (end_year - start_year) if (end_time.month == 1 and end_time.day == 1) else (end_year - start_year + 1)
        for i in range(1, end):
            newRow = values[0].copy()
            newTime = start_time.replace(year=start_year+i)
            if(newTime > end_time):
                pass
            else:
                newRow['Date'] = newTime.strftime('%Y/%m/%d')
                values.insert(-1, newRow)
        
        return values 
    
    def addFeatures(self, Rows: dict[str, list[dict]])->dict[str, list[dict]]:
        # add new cols in self.featuresToAdd : ['Noi', 'CashFlow', 'time_diff']
        # For the convenience of calculation. 
        for key in list(Rows.keys()):
            for values in Rows[key]:
                for item in self.featuresToAdd:
                    values[item] = 0.0
        
        return Rows
    def salesDataClean(self, sales_data: dict[str, list[dict]])->dict[str, list[dict]]:
        # We only need to call this in order to clean the data
        # format changing
        # sales_data = self.__salesDataInitialization(sales_data)
        for name in sales_data:
            print(name)
            print(sales_data[name])
        sales_data_splited = self.splitAndFilter(sales_data)
        sales_data_splited = self.addFeatures(sales_data_splited)
        sales_data_filled = self.fillGaps(sales_data_splited)
        
        return sales_data_filled
    
    
# test case

if __name__ == '__main__':
    from file_reader import FileLoader
    
    cpi_path = '../Final_Code_and_Dataset/CPI.csv'
    data_path = '../Final_Code_and_Dataset/Dataset_apartment.csv'
    encodings = ('utf-8-sig', None)
    
    files = FileLoader(cpi_path, data_path, encodings)
    
    cpi_data = files.data_container['CPI']
    sales_data = files.data_container['Sales']
    
    sales_data = DataPreparation().salesDataClean(sales_data)