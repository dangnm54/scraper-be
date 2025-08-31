import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime
import pytz
from typing import Dict, List, Any, cast
import uuid

import scraper.tool.log_op as lg
import scraper.tool.db_op as dbop

from scraper.tool.config import data_folder_path
from scraper.type.api import FileDetail, FileMetadata
from scraper.type.data import PropertyDB, PropertyDetail

from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.orm import load_only

# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)


def get_file_list(db: Session) -> List[FileMetadata]:
   """
   input: None
   output: list of file metadata | None
   operation:
      - query from db
      - convert to list FileMetadata
   """
   
   lg.log_divider('Get session list')

   session_data = (
      db.query(
         PropertyDB.session_id.label('file_id'),
         PropertyDB.session_name.label('file_name'),
         func.min(PropertyDB.created_at).label('date_created'),
         func.count(PropertyDB.id).label('item_count')
      )
      .group_by(PropertyDB.session_id, PropertyDB.session_name)
      .order_by(func.min(PropertyDB.created_at).desc())
      .all()
   )


   file_list: List[FileMetadata] = []
   vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

   for file_id, file_name, date_created, item_count in session_data:

      local_date_created = date_created.astimezone(vietnam_tz)

      file_list.append(FileMetadata(
         id = str(file_id),
         file_name = file_name,
         date_created = local_date_created.strftime('%Y-%m-%d'),
         item_count = item_count
      ))

   return file_list



def get_file_detail(file_id: str, db: Session) -> FileDetail:
   """
   input: file_id
   output: file data (list of dict) | None
   operation:
      - query from db
      - convert to FileDetail
   """

   excluded_col_names: List[str] = [
      "session_id",
      "session_name",
      "created_at"
   ]

   included_col_names = [col for col in PropertyDB.__table__.columns.keys()
                        if col not in excluded_col_names]

   session_data = (
      db.query(PropertyDB)
      .options(load_only(*included_col_names))
      .filter_by(session_id=uuid.UUID(file_id))
      .all()
   )

   file_data: List[Dict[str, Any]] = []

   for value in session_data:
      file_data.append(value.model_dump())

   file_name: str = db.query(PropertyDB.session_name).filter_by(session_id=uuid.UUID(file_id)).scalar()

   return FileDetail(
      file_name = file_name,
      file_data = file_data
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

