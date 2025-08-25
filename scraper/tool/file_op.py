import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, cast

import scraper.tool.log_op as lg
import scraper.tool.db_op as dbop

from scraper.tool.config import data_folder_path
from scraper.type.api import FileDetail, FileMetadata
from scraper.type.data import PropertyDB, PropertyDetail

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)


def get_file_metadata_list(db: Session) -> List[FileMetadata]:
   """
   input: None
   output: list of file metadata
   Scans database and return list of session (= 'file')
   """
   
   lg.log_divider('Get session list')
   
   file_list: List[FileMetadata] = []

   session_data = (
      db.query(
         PropertyDB.session_id.label('file_id'),
         PropertyDB.session_name.label('file_name'),
         func.min(PropertyDB.created_at).label('date_created'),
         func.count(PropertyDB.id).label('item_count')
      )
      .group_by(PropertyDB.session_id)
      .order_by(func.min(PropertyDB.created_at))
      .all()
   )

   for file_id, file_name, date_created, item_count in session_data:
      file_list.append(FileMetadata(
         id = str(file_id),
         file_name = file_name,
         date_created = date_created.strftime('%Y-%m-%d'),
         item_count = item_count
      ))

   return file_list



def get_file_path(file_id: int) -> Dict[str, str]:

   lg.log_divider('Get file path')

   log.info(f"Received file_id: {file_id}")

   file_metadata_list: List[FileMetadata] = get_file_metadata_list()
   file_path: str = ''
   file_name: str = ''

   for item in file_metadata_list:
      if item.id == file_id:
         file_path = item.path
         file_name = item.file_name
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



def get_file_detail(file_id: int) -> FileDetail:
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

   file_name: str = ''
   file_path: str = ''
   file_name, file_path = get_file_path(file_id)

   # make dataframe from file path
   detail_df: pd.DataFrame = csv_to_df(file_path, index='prop_code', mode=2)

   # Replace all inf/-inf, null-like (eg: NaN, None, NaT) values with None (which becomes null in JSON)
   detail_df = detail_df.replace([np.inf, -np.inf], None)
   detail_df = detail_df.where(pd.notnull(detail_df), None)

   # update all value to friendliest Python type to easily convert to JSON
   detail_df = detail_df.convert_dtypes()

   # remove 'ID' as index, so 'ID' can be included in dict
   detail_df.reset_index(inplace=True)
   
   # orient -> dictate the struc of dict
   # 'records' -> 'list of dict' structure 
   detail_dict: List[Dict[str, Any]] = cast(List[Dict[str, Any]], detail_df.to_dict(orient='records'))

   return FileDetail(
      detail = f'[file-detail api] Content for {file_name} fetched successfully',
      data = detail_dict
   )



def list_dict_to_df(list_dict: List[Dict[str, Any]] | List[PropertyDetail], index:str='prop_code') -> pd.DataFrame:
   
   if isinstance(list_dict[0], PropertyDetail):

      tempt_dict: List[Dict[str, Any]] = []
      
      for item in list_dict:
         if isinstance(item, PropertyDetail):
            # turn PropertyDetail instance to dict
            tempt_dict.append(item.model_dump())
      
      list_dict = tempt_dict
   
   df: pd.DataFrame = pd.DataFrame(list_dict)
   df.set_index(index, inplace=True)

   log.info('List_of_dict -> Dataframe successful')
   return df



def df_to_csv(df: pd.DataFrame, name: str) -> str:
   folder_name: str = data_folder_path

   # make file name
   current_time: str = datetime.now().strftime('%d%m%y')
   base_csv_name: str = f'{name}_{current_time}.csv'
   
   counter: int = 1
   csv_name: str = base_csv_name
   while os.path.exists(os.path.join(folder_name, csv_name)):
      name_without_ext: str = base_csv_name.replace('.csv', '')
      csv_name: str = f'{name_without_ext} ({counter}).csv'
      counter += 1

   full_csv_path: str = os.path.join(folder_name, csv_name)
   os.makedirs(folder_name, exist_ok=True) #crt folder if not exist
   
   # convert to csv
   try:
      df.to_csv(full_csv_path, index=True, encoding='utf-8-sig')
      log.info(f'Dataframe saved to file: {full_csv_path}')
   except Exception as e:
      lg.log_detail_error(e)

   return full_csv_path



def csv_to_df(csv_path: str, index: str, mode: int) -> pd.DataFrame:
   match mode:
      case 1:
         df: pd.DataFrame = pd.read_csv(csv_path, index_col=index, encoding='utf-8-sig')
      case 2:
         # for calculation
         df: pd.DataFrame = pd.read_csv(csv_path, index_col=index, encoding='utf-8-sig', 
               dtype={
               'this_month_booked_rate': float,
               'next_1_month_booked_rate': float,
               'next_3_month_booked_rate': float, 
               })
      # case 3:
      #    # for api json response
      #    df: pd.DataFrame = pd.read_csv(csv_path, index_col=index, encoding='utf-8-sig', 
      #          dtype={
      #          'this_month_booked_rate': str,
      #          'next_1_month_booked_rate': str,
      #          'next_3_month_booked_rate': str, 
      #          })
   
   log.info(f'Dataframe created from file: {csv_path}')
   return df



# def merge_df(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:

   merged_df: pd.DataFrame = df1.merge(df2, left_index=True, right_index=True, how='left')
   log.info(f'Successfully merge 2 Dataframe')
   
   return merged_df

