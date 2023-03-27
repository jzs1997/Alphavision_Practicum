import os
import csv
import pandas as pd
import gc


FLAGS = {
    1 : 'Evenly Increase',
    -1 : 'Evenly Decrease',
    0 : 'Inflate/Deflate with CPI'
}

def create_dir(path, dirname)-> str:
    # create a directory given directory name and the location to put the directory
    dir_path = os.path.join(path, dirname)
    if(os.path.isdir(dir_path)):
        print('Dir {} already exists' .format(dirname))
    else:
        os.mkdir(dir_path)

    return dir_path

def save_one(dir_path, property_name, Rows):
    # save the data of transaction
    # files generated will be put in directory noi_info_property_type 
    # use package csv
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
    # same as function save_one
    # use pandas
    dir_noi_info = create_dir('', dir_path)
    name_list = property_name.split('_')
    name_ = name_list[0] + name_list[-1] + 'pd' + '.csv'
    file_name = os.path.join(dir_noi_info, name_)
    df = pd.DataFrame(Rows)
    df.to_csv(file_name, index=False)
    del df
    gc.collect()
    
def save_output(file_output, data:dict, names)->None:
    # save the xirrs of properties
    # files generated will be put in root directory
    d = {}
    d['Property_name'] = [n for n in data.keys()]
    for i in range(len(names)):
        d[names[i]] = [data[key][i] for key in data.keys()]
    
    df = pd.DataFrame(d)
    df['flag'] = df['flag'].map(FLAGS)
    df.to_csv(file_output)
    del df
    gc.collect()
    