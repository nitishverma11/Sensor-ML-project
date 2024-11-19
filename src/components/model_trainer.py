import sys
from typing import Generator,List,Tuple
import os
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score

from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from src.constants import *
from src.exceptions import CustomExceptions
from src.logger import logging
from src.Utils.main_utils import MainUtils

from dataclasses import dataclass

@dataclass
class Modeltrainerconfig:
    artifacts_folder = os.path.join(artfacts_folder)
    trained_model_path = os.path.join(artifacts_folder)
    expected_accuracy=0.45
    model_config_file_path = os.path.join('config','model.yaml')

class Modeltrainer:
    def __inti__(self):

        self.model_trainer_config = Modeltrainerconfig()

        self.Utils = MainUtils()
        
        self.models = {
                       "XGBClassifier": XGBClassifier(),
                       "GradientBoostingClassifier": GradientBoostingClassifier(),
                       'SVC': SVC(),
                       'RandomForestClassifier': RandomForestClassifier()
                      }
    def evalute_models(self,X,y,models):
        try:
            X_train, X_test,y_train,y_test = train_test_split(
                X,y,test_size=0.2, random_state=42
            )

            report= {}

            for i in range(len(list(models))):
                model = list(models.values())[i]

                model.fit(X_train,y_train )
                y_train_pred = model.predict(X_train)
                y_test_pred = model.predict(X_test)
                train_medal_score =accuracy_score(y_train,y_train_pred)
                test_model_score = accuracy_score(y_test,y_test_pred)

                report[list(model.keys())[i]]= test_model_score
            return report
        
        except Exception as e:
            raise CustomExceptions(e,sys)
        
    def get_best_model(self,
                       x_train:np.array,
                       y_train:np.array,
                       x_test:np.array,
                       y_test:np.array):
        try:

            model_report: dict=self.evalute_models(
                x_train= x_train,
                y_train = y_train,
                x_test = x_test,
                y_test = y_test,
                models =self.models
            )

            print(model_report)

            best_model_score =max(sorted(model_report.values()))

            #to get best model
            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]

            best_model_object = self.models[best_model_name]
            return best_model_name,best_model_object,best_model_score
        except Exception as e:
            raise CustomExceptions(e,sys)
    
    def finetune_best_model(self,
                             best_model_object: object,
                             best_model_name,
                             X_train,
                             y_train,
                             ) -> object:
        try:

            model_param_grid =self.Utils.read_yaml_file(self.model_trainer_config.model_config_file_path)["model_selection"]["model"][best_model_name]["search_param_grid"]

            grid_search = GridSearchCV(
                best_model_object,param_grid=model_param_grid,cv=5,n_jobs=-1,verbose=1)
            
            grid_search.fit(X_train,y_train)

            best_params = grid_search.best_params_
            print("best params are:",best_params)

            finetuned_model = best_model_object.set_params(**best_params)

            return finetuned_model
        
        except Exception as e:
            raise CustomExceptions(e,sys)
    
    def initiate_model_trainer(self,train_array,test_array):
        try:
            logging.info(f"splitting training ad testing input and target feature")

            x_train, y_train, x_test,y_test = (
                train_array[:,:-1],
                train_array[:,:-1],
                test_array[:,:-1],
                test_array[:,:-1]
            )

            logging.info(f"Extracting model Config file path")

            model_report: dict =  self.evaluate_models(X=x_train,y=y_train,models=self.models)
            #to get best model from dict
            best_model_score= max(sorted(model_report.values()))
            
            bets_model_name= list( model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]

            best_model=self.models[bets_model_name]

            best_model = self.finetune_best_model(
                best_model_name=bets_model_name,
                best_model_object=best_model,
                X_train = x_train,
                y_train= y_train
            )
            
            best_model.fiyt(x_train,y_train)
            y_pred = best_model.predict(x_test)
            best_model_score = accuracy_score(y_test,y_pred)

            print(f"best model name{bets_model_name} and score: {best_model_score}")

            if best_model_score < 0.5:
                raise Exception ("no best model found with an accuracy greater than the threshold 0.6")
            
            logging.info(f"Best found model on both training and testing dataset")

            logging.info(
                f"saving model at path: {self.model_trainer_config.trained_model_path}"
            )
            
            os.makedirs(os.path.dirname(self.model_trainer_config.trained_model_path),exist_ok=True)

            self.Utils.save_object(
                file_path=self.model_trainer_config.trained_model_path,
                obj=best_model
            )

            return self.model_trainer_config.trained_model_path
        
        except Exception as e:
            raise CustomExceptions(e,sys)