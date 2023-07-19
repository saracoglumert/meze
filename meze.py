import pandas as pd
import numpy as np
import string
import random
import datetime
import pickle

CONST_FREQS         = ['D','W','M']
CONST_SAMPLE_RANGE1  = range(0,255)
CONST_SAMPLE_RANGE2 = range(0,8)
CONST_SAMPLE_NAME   = 4
CONST_SAMPLE_VAR    = 0.15

class Tools:
    @staticmethod
    def test_DF(start,end,freq,fill=None):
        if freq in CONST_FREQS:
            dr = pd.date_range(start=start,end=end,freq=freq).date
            df = pd.DataFrame(index=dr)
            df.name = ''.join(random.choice(string.ascii_lowercase) for i in range(4))

            if isinstance(fill,tuple) and len(fill) == 2 and isinstance(fill[0],bool) and  isinstance(fill[1],int)> 0:
                for _ in range(fill[1]):
                    temp_name = 'test_'+''.join(random.choice(string.ascii_lowercase) for i in range(CONST_SAMPLE_NAME))
                    temp_val = pd.Series(np.random.randint(CONST_SAMPLE_RANGE1[0],CONST_SAMPLE_RANGE1[-1],len(dr)))
                    df.insert(len(df.columns),temp_name,temp_val.values)

            return DF(df)

    @staticmethod
    def test_Container(name,start,end,count):
        result = Container(name)

        for _ in range(0,count):
            freq = random.choice(CONST_FREQS)
            
            #bot = temp[0] + np.timedelta64(random.choice(range(0,8)),freq)
            #top = temp[-1] - np.timedelta64(random.choice(range(0,8)),freq)

            bot = datetime.datetime.strptime(start,'%d/%m/%Y')
            top = datetime.datetime.strptime(end,'%d/%m/%Y')

            dr = pd.date_range(start=bot,end=top,freq=freq).date
            df = pd.DataFrame(index=dr)

            for _ in range(0,random.choice(CONST_SAMPLE_RANGE2)+1):
                temp_name = 'test_'+''.join(random.choice(string.ascii_lowercase) for i in range(CONST_SAMPLE_NAME))
                temp_val = pd.Series(np.random.randint(CONST_SAMPLE_RANGE1[0],CONST_SAMPLE_RANGE1[-1],len(dr)))

                df.insert(len(df.columns),temp_name,temp_val.values)

            temp_name = 'test_'+''.join(random.choice(string.ascii_lowercase) for i in range(CONST_SAMPLE_NAME))
            result.load_DF(DF(df,temp_name))
        
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
            if (self.type == "csv"):
                self.data = pd.read_csv(self.path,index_col=0)
            

        if isinstance(input,pd.DataFrame) and input is not None:
            self.data = input
            self.name = name
            self.type = "DF"

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
        self.folder = {}

        self.dr_min = None
        self.dr_max = None

    def update(self):
        self.keys = [i for i in self.folder.keys()]
        self.values = [i for i in self.folder.values()]

        temp_min = []
        temp_max = []
        for i in self.values:
            temp_min.append(i.dr_min.astype('datetime64[D]'))
            temp_max.append(i.dr_max.astype('datetime64[D]'))
        
        self.dr_min = max(temp_min)
        self.dr_max = min(temp_max)

    def load_file(self,path):
        temp = DF(path)
        self.folder[temp.name] = temp
        self.update()

    def load_DF(self,input):
        self.folder[input.name] = input
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