import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from fastapi import HTTPException

try:
   import scraper.log_op as lg
   from scraper.config import data_folder_path
except ImportError:
   import log_op as lg
   from config import data_folder_path


# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)


def get_file_metadata_list():
   """
   input: None
   output: list of file metadata
   Scans 'data' folder and return list of file metadata
   """
   
   lg.log_divider('Get file metadata list')
   
   data_path = data_folder_path
   file_list = []
   file_id = 1

   if not os.path.exists(data_path):
      if not os.path.exists(data_path):
         return {
               "status": "success",
               "message": "No files found",
               "data": []
         }

   for file_name in os.listdir(data_path):
      if file_name.endswith(".csv") and "full" in file_name.lower():
         file_path = os.path.join(data_path, file_name)

         # get file date
         try:
               timestamp = os.path.getmtime(file_path) # get modification time
               file_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
         except Exception:
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

         log.info(f'file_path: {file_path}')

   # Sort by date created (newest first)
      # lambda is shorthand mini function to get date_created value of each file
   file_list.sort(key=lambda file: file['date_created'], reverse=True)

   return file_list



def get_file_path(file_id: int):

   lg.log_divider('Get file path')

   log.info(f"Received file_id: {file_id}")

   file_metadata_list = get_file_metadata_list()
   file_path = None
   file_name = None

   for item in file_metadata_list:
      if item['id'] == file_id:
         file_path = item['path']
         file_name = item['file_name']
         break
   log.info(f"Found file_path: {file_path}")
   log.info(f"Found file_name: {file_name}")

   # check if file exist in file_metadata_list
   if not file_path:   
      # file_path is None -> not None is true -> raise 404
      raise HTTPException(status_code=404, detail=f"File ID {file_id} not found.")
   
   return {
      'file_name': file_name,
      'file_path': file_path 
   }



def get_file_detail(file_id: int):
   """
   input: file_id
   output: detail of file (list of dict)
   operation:
      - check path of file
      - create dataframe from file 
      - turn dataframe to list of dict
   """

   lg.log_divider('Get file detail')

   log.info(f"Received file_id: {file_id}")

   file_name, file_path = get_file_path(file_id).values()
   
   # make dataframe from file path
   detail_df = csv_to_df(file_path, mode=2)

   # Replace all inf/-inf, null-like (eg: NaN, None, NaT) values with None (which becomes null in JSON)
   detail_df = detail_df.replace([np.inf, -np.inf], None)
   detail_df = detail_df.where(pd.notnull(detail_df), None)

   # update all value to friendliest Python type to easily convert to JSON
   detail_df = detail_df.convert_dtypes()
   
   # orient -> dictate the struc of dict
   # 'records' -> 'list of dict' structure 
   detail_dict = detail_df.to_dict(orient='records') 

   return {
      "detail": f'[file-detail api] Content for {file_name} fetched successfully',
      "data": detail_dict
   }



def list_dict_to_df(list_dict, index='ID'):
   df = pd.DataFrame(list_dict)
   df.set_index(index, inplace=True)

   log.info('List_of_dict -> Dataframe successful')
   return df



def merge_df(df1, df2):
   merged_df = df1.merge(df2, left_index=True, right_index=True, how='left')
   
   log.info(f'Successfully merge 2 Dataframe')
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
      log.info(f'Dataframe saved to file: {full_csv_path}')
   except Exception as e:
      lg.log_detail_error(e)

   return full_csv_path



def csv_to_df(csv_path, index=None, mode=1):
   match mode:
      case 1:
         df = pd.read_csv(csv_path, index_col=index, encoding='utf-8-sig')
      case 2:
         # for calculation
         df = pd.read_csv(csv_path, index_col=index, encoding='utf-8-sig', 
               dtype={
               'This_month_booked_rate': float,
               'Last_1_month_booked_rate': float,
               'Last_3_month_booked_rate': float,
               'Next_1_month_booked_rate': float,
               'Next_3_month_booked_rate': float, 
               })
      case 3:
         # for api json response
         df = pd.read_csv(csv_path, index_col=index, encoding='utf-8-sig', 
               dtype={
               'This_month_booked_rate': str,
               'Last_1_month_booked_rate': str,
               'Last_3_month_booked_rate': str,
               'Next_1_month_booked_rate': str,
               'Next_3_month_booked_rate': str, 
               })
   
   log.info(f'Dataframe created from file: {csv_path}')
   return df


