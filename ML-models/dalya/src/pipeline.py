from src.extract_transform import ExtractorTransformer
import numpy as np
from sklearn.model_selection import train_test_split
class Pipeline:
    def __init__(self, target_column:str, id_column:str, test_size:float):
        #dataset
        self.data = None
        self.X_train = None
        self.X_test = None
        self.y_test = None
        self.y_train = None
        self.X = None
        self.y = None
        #split
        self.target_column = target_column
        self.id_column = id_column
        self.test_size = test_size
        
        
        
    def run(self):
        self.extract_transform()
        self.splitting()
        
        
        
    def extract_transform(self):
        self.data = ExtractorTransformer().load()
        
    def splitting(self):
        features = np.setdiff1d(self.data.columns, [self.target_column, self.id_column])
        self.X = self.data[features]
        self.y = self.data[self.target_column]
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size = self.test_size)