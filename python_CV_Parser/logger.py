import pandas as pd
import os
from datetime import datetime


class Logger:
    def __init__(self, log_path = "system_log.csv"):
        self.log_path = log_path
        self.newlog = {}
        if os.path.exists(self.log_path):
            self.log_df = pd.read_csv(self.log_path)
        else:
            # If no existing file, create a new empty DataFrame
            self.log_df = pd.DataFrame(columns=["timestamp", "success", "detection_time", "solve_time", "cubesize"])
            #self.log_df.to_csv(self.log_path, index=False)
    def add_data(self, success=0, detection_time=-1, solve_time=-1, cubesize=-1) -> None:
        self.newlog["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.newlog["success"] = success
        self.newlog["detection_time"] = detection_time
        self.newlog["solve_time"] = solve_time
        self.newlog["cubesize"] = cubesize

    def save(self) -> None:
        if not self.newlog:
            return  # Nothing new to save
        self.log_df = pd.concat([self.log_df, pd.DataFrame([self.newlog])], ignore_index=True)    
        self.log_df.to_csv(self.log_path, index=False)
        self.newlog = {}

if __name__ == "__main__":
    logger = Logger(log_path='logger_test.csv')
    
    logger.add_data(detection_time=35)
    logger.add_data(success=1,solve_time=50,cubesize=3)
    logger.save()
    logger.add_data(success=0)
    logger.save()