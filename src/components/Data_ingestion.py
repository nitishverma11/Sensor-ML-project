import sys
import os
import numpy as np
import pandas as pd
from pymongo import mongoclient
from zipfile import Path
from src.constants import *
from src.exceptions import CustomExceptions
from src.logger import logging
from src.Utils.main_utils import MainUtils
from dataclasses import dataclass

@dataclass
class dataingestionconfig:
    artfacts_folder: str = os.path.join(artfacts_folder)

class dataingestion:
    def __init__(self):
        self.data_ingestion_config = dataingestionconfig()
        self.Utils = MainUtils()
    def export_collection_as_dataframe(self,collection_name,db_name):

        try:
            mongo_client = mongoclient(MONGO_DB_URL)
            collection = mongo_client[db_name][collection_name]
            df = pd.DataFrame(list(collection.find()))

            if "_id" in df.columns.to_list():
                df = df.drop(columns=['_id'],axis=1)

            df.replace({"na":np.nan},inplace=True)

            return df
        except Exception as e:
            raise CustomExceptions(e,sys)
    
    def export_data_into_feature_store_file_path(self)-> pd.DataFrame:
        try:
            logging.info(f"Exporting data from MOngoDB")
            raw_file_path = self.data_ingestion_config.artfacts_folder

            os.makedirs(raw_file_path,exist_ok=True)

            sensor_data = self.export_collection_as_dataframe(
                collection_name= MONGO_COLLECTION_NAME,
                db_name= MONGO_DATABASE_NAME
            )
            
            logging.info(f"saving exported data into feature store file path : {raw_file_path}")
            feature_store_file_path =os.path.join(raw_file_path,'wafer_fault.csv')

            sensor_data.to_csv(feature_store_file_path,index=False)
            return feature_store_file_path
        except Exception as e :
            raise CustomExceptions(e,sys)
    def initiate_data_ingestion(self) -> Path:
        logging.info("Entered initiated_data_ingestion method of data ingestion class")

        try:
            feature_store_file_path =self.export_data_into_feature_store_file_path()
            logging.info("got the data from mongodb")
            logging.info("exited initiate_data_ingestion methods of data ingestion class")

            return feature_store_file_path
        except Exception as e:
            raise CustomExceptions(e,sys) from e        
