import config

import pandas as pd
import numpy as np
import string
import random
import datetime
import pickle



class Tools:
    @staticmethod
    def sample(length):
        temp = np.linspace(0,length,length).round(2)
        result = np.sin(temp)*random.choice(CONST_SAMPLE_RANGE_MID) + np.random.normal(scale=1, size=len(temp))
        
        return np.array(result)

    def test_DF(start,end,freq,fill=0):
        if freq in CONST_FREQS:
            dr = pd.date_range(start=start,end=end,freq=freq).date
            df = pd.DataFrame(index=dr)
            df.name = ''.join(random.choice(string.ascii_lowercase) for i in range(4))

            if fill > 0:
                for _ in range(fill):
                    temp_name = 'test_ft_'+''.join(random.choice(string.ascii_lowercase) for i in range(CONST_SAMPLE_NAME))
                    temp_val = Tools.sample(len(dr))
                    df.insert(len(df.columns),temp_name,temp_val)
            else:
                raise ValueError()

            temp_name = 'test_DF_'+''.join(random.choice(string.ascii_lowercase) for i in range(CONST_SAMPLE_NAME))
            return DF(df,)

    @staticmethod
    def test_Container(start,end,length):
        temp_name = 'test_Container_'+''.join(random.choice(string.ascii_lowercase) for i in range(CONST_SAMPLE_NAME))
        result = Container(temp_name)

        for _ in range(0,length):
            freq = random.choice(CONST_FREQS)
            
            bot = datetime.datetime.strptime(start,'%d/%m/%Y')
            top = datetime.datetime.strptime(end,'%d/%m/%Y')

            for _ in range(0,random.choice(CONST_SAMPLE_RANGE_LOW)+1):
                result.load_DF(Tools.test_DF(bot,top,freq,random.choice(CONST_SAMPLE_RANGE_LOW)))
        raise ValueError(ERROR_LENGTH)
        
        return result

class FileIO:
    @staticmethod
    def saveMZ(path,input):
        with open(path,'wb') as handle:
            pickle.dump(input,handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    @staticmethod
    def loadMZ(path):
        with open(path,'rb') as handle:
            return pickle.load(handle)

class DF:
    def __init__(self,input,name=None):
        if isinstance(input,str):
            self.path = input

            self.name = self.path.split("/")[-1].split(".")[0]
            self.type = self.path.split("/")[-1].split(".")[-1]

            if (self.type == "xlsx"):
                self.data = pd.read_excel(self.path,index_col=0)
            elif (self.type == "csv"):
                self.data = pd.read_csv(self.path,index_col=0)
            else:
                raise ValueError(ERROR_FILETYPE) 
        else:
            raise ValueError(ERROR_OBJTYPE) 

        if isinstance(input,pd.DataFrame) and input is not None:
            self.data = input
            self.name = self.data.name
            self.type = "DF"
        else:
            raise ValueError(ERROR_OBJTYPE)

        self.data.index.name = "date"

        self.features = list(self.data.columns.values)
        self.index = self.data.index
        self.dr = pd.to_datetime(self.index)
        self.freq = pd.infer_freq(self.index)
        self.dr_min = self.dr.values[0]
        self.dr_max = self.dr.values[-1]

class Container:
    def __init__(self,name):
        self.name = name
        self.data = {}

        self.dr_min = None
        self.dr_max = None

    def update(self):
        self.keys = [i for i in self.data.keys()]
        self.values = [i for i in self.data.values()]

        temp_min = []
        temp_max = []
        for i in self.values:
            temp_min.append(i.dr_min.astype('datetime64[D]'))
            temp_max.append(i.dr_max.astype('datetime64[D]'))
        
        self.dr_min = max(temp_min)
        self.dr_max = min(temp_max)

    def load_file(self,path):
        temp = DF(path)
        self.data[temp.name] = temp
        self.update()

    def load_DF(self,input):
        self.data[input.name] = input
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

        return df,self.dr_min.astype(str),self.dr_max.astype(str)
    
    def save(self,path):
        f = open(path, 'wb')
        pickle.dump(self.__dict__, f, 2)
        f.close()