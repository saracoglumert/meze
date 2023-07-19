import pandas as pd
import numpy as np
import string
import random

CONST_FREQS = ['D','W','M']

class Tools:
    @staticmethod
    def generate_test_file(start,end,freq,fill=None):
        if freq in CONST_FREQS:
            dr = pd.date_range(start=start,end=end,freq=freq).date
            df = pd.DataFrame(index=dr)
            df.name = ''.join(random.choice(string.ascii_lowercase) for i in range(4))

            if isinstance(fill,tuple) and len(fill) == 2 and isinstance(fill[0],bool) and  isinstance(fill[1],int)> 0:
                for _ in range(fill[1]):
                    temp_name = 'test_'+''.join(random.choice(string.ascii_lowercase) for i in range(4))
                    temp_val = pd.Series(np.random.randint(0,255,len(dr)))
                    df.insert(len(df.columns),temp_name,temp_val.values)

            return df

    @staticmethod
    def generate_test_folder(name,start,end,count,var):
        
        for _ in range(count):
            freq = random.choice(CONST_FREQS)
            
            temp = pd.date_range(start=start,end=end,freq=freq).date

            bot = temp[0] + np.timedelta64(var,round(len(temp)*var))
            top = temp[-1] - np.timedelta64(var,round(len(temp)*var))

            dr = pd.date_range(start=bot,end=top,freq=freq).date
            df = pd.DataFrame(index=dr)

        pass

class Container:
    class File:
        def __init__(self,path):
            self.path = path

            self.name = self.path.split("/")[-1].split(".")[0]
            self.type = path.split("/")[-1].split(".")[-1]

            if (self.type == "xlsx"):
                self.raw = pd.read_excel(path,index_col=0)
            if (self.type == "csv"):
                self.raw = pd.read_csv(path,index_col=0)
            
            self.raw.index.name = "date"

            self.features = list(self.raw.columns.values)
            self.index = self.raw.index
            self.dr = pd.to_datetime(self.index)
            self.freq = pd.infer_freq(self.index)
            self.dr_min = self.dr.values[0]
            self.dr_max = self.dr.values[-1]
    
    def __init__(self,name):
        self.name = name
        self.folder = {}
        self.keys = self.folder.keys()
        self.values = self.folder.values()

        self.dr_min = None
        self.dr_max = None

    def update(self):
        temp_min = []
        temp_max = []
        for i in self.values:
            temp_min.append(i.dr_min.astype('datetime64[D]'))
            temp_max.append(i.dr_max.astype('datetime64[D]'))
        
        self.dr_min = max(temp_min)
        self.dr_max = min(temp_max)

    def load_file(self,path):
        temp = self.File(path)
        self.folder[temp.name] = temp
        self.update()

    def report(self):
        df = pd.DataFrame()
        
        name = [] 
        type = []
        drmin = [] 
        drmax = []
        freq = []
        feature_count = []
        features = []

        for i in self.values:
            name.append(i.name)
            type.append(i.type)
            drmin.append(i.dr_min)
            drmax.append(i.dr_max)
            freq.append(i.freq)
            feature_count.append(len(i.features))
            features.append(i.features)

        df.insert(len(df.columns),'name',name)
        df.insert(len(df.columns),'type',type)
        df.insert(len(df.columns),'dr_min',drmin)
        df.insert(len(df.columns),'dr_max',drmax)
        df.insert(len(df.columns),'features_count',feature_count)
        df.insert(len(df.columns),'features',features)

        return df,self.dr_min,self.dr_max
    