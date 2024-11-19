import sys
import os

from src.components.Data_ingestion import dataingestion
from src.components.Data_Transformation import Datatransformation
from src.components.model_trainer import Modeltrainer
from src.exceptions import CustomExceptions

class Trainingpipeline:
    def start_data_ingestion(self):
        try:
            data_ingestion = dataingestion()
            feature_store_file_path =data_ingestion.initiate_data_ingestion()
            return feature_store_file_path
        except Exception as e:
            raise CustomExceptions(e,sys)
    
    def start_data_transformation(self,feature_store_file_path):
        try:
            data_transformation = Datatransformation(feature_store_file_path=feature_store_file_path)
            train_arr,test_arr,preprocessor_path= data_transformation.initiate_data_transformation
            return train_arr,test_arr,preprocessor_path
        except Exception as e:
            raise CustomExceptions(e,sys)
    
    def start_model_training(self,train_arr,test_arr):
        try:
            model_trainer = Modeltrainer()
            model_score = model_trainer.initiate_model_trainer(
                train_arr,test_arr
            )
            return model_score
        except Exception as e:
            raise CustomExceptions(e,sys)
    
    def run_pipeline(self):
        try:
            feature_store_file_path= self.start_data_ingestion()
            train_arr,test_arr,preprocessor_path =self.start_data_transformation(feature_store_file_path)
            r2_square = self.start_model_training(train_arr,test_arr)

            print("training completed. trained model score:",r2_square)

        except Exception as e:
            CustomExceptions(e,sys)