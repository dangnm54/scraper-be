import os
import pandas as pd
from datetime import datetime

try:
    import scraper.utils as utl
    from scraper.config import data_folder_path
except ImportError:
    import utils as utl
    from config import data_folder_path



# -----------------------------------------------------------------------------------


def get_file_metadata_list():
    """
    Scans 'data' folder and return list of file metadata
    """
    data_path = data_folder_path
    file_list = []
    file_id = 1

    if not os.path.exists(data_path):
        return []       # return empty list if directory not exist

    for file_name in os.listdir(data_path):
        if file_name.endswith(".csv") and "link" in file_name.lower():
            file_path = os.path.join(data_path, file_name)

            # get file date
            try:
                timestamp = os.path.getmtime(file_path) # get modification time
                file_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
            except Exception as e:
                utl.log_error(e)
                file_date = 'Unknown date'
                
            # get item count
            item_count = 0
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    item_count = sum(1 for line in f) - 1 # Subtract 1 for header row
                    if item_count < 0: item_count = 0
            except Exception:
                item_count = 0

            file_list.append({
                'id': file_id,
                'file_name': file_name,
                'date_created': file_date,
                'item_count': item_count,
                'path': file_path
            })
            file_id += 1

            print(f'file_path: {file_path}')
            print(f'file_list: {file_list.dict()}')
            print('-'*30)

    # Sort by date created (newest first)
        # lambda is shorthand mini function to get date_created value of each file
    file_list.sort(key=lambda file: file['date_created'], reverse=True)

    return file_list




def list_dict_to_df(list_dict, index='ID'):
    df = pd.DataFrame(list_dict)
    df.set_index(index, inplace=True)

    print('List_of_dict -> Dataframe successful')
    print('-'*30)
    return df



def merge_df(df1, df2):
    merged_df = df1.merge(df2, left_index=True, right_index=True, how='left')
    
    print(f'Successfully merge 2 Dataframe')
    print('-'*30)
    return merged_df    



def df_to_csv(df, name=None):
    folder_name = data_folder_path

    # make file name
    current_time = datetime.now().strftime('%d%m%y')
    base_csv_name = f'{name}_{current_time}.csv'
    
    counter = 1
    csv_name = base_csv_name
    while os.path.exists(os.path.join(folder_name, csv_name)):
        name_without_ext = base_csv_name.replace('.csv', '')
        csv_name = f'{name_without_ext} ({counter}).csv'
        counter += 1

    full_csv_path = os.path.join(folder_name, csv_name)
    os.makedirs(folder_name, exist_ok=True) #crt folder if not exist
    
    
    # convert to csv
    try:
        df.to_csv(full_csv_path, index=True, encoding='utf-8-sig')
        print(f'Dataframe saved to file: {full_csv_path}')
    except Exception as e:
        utl.log_error(e)

    print('-'*30)
    return full_csv_path



def csv_to_df(csv_path, index=None, mode=1):
    match mode:
        case 1:
            df = pd.read_csv(csv_path, index_col=index, encoding='utf-8-sig')
        case 2:
            df = pd.read_csv(csv_path, index_col=index, encoding='utf-8-sig', 
                dtype={
                'This_month_booked_rate': float,
                'Last_1_month_booked_rate': float,
                'Last_3_month_booked_rate': float,
                'Next_1_month_booked_rate': float,
                'Next_3_month_booked_rate': float, 
                })
    
    print(f'Dataframe created from file: {csv_path}')
    print('-'*30)
    return df


