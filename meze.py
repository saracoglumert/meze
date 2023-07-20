import config as cfg

import pandas as pd
import numpy as np
import statsmodels.api as sm
import string
import random
import datetime
import pickle

class Tools:
    @staticmethod
    def sample(length):
        x = 1
        start = x
        xposition = [start]
        probabilities = [10, 120]
        for i in range(1, length):
            x += random.choice(probabilities)
            xposition.append(x)

        return np.array(xposition)

    @staticmethod
    def rand_name():
        ''.join(random.choice(string.ascii_lowercase) for i in range(cfg.CONST_SAMPLE_NAME))

    @staticmethod
    def test_DF(start,end,freq,fill=0,name=None):
        if freq in cfg.CONST_FREQS:
            dr = pd.date_range(start=start,end=end,freq=freq).date
            df = pd.DataFrame(index=dr)
            if name is None:
                df.name = 'test_DF_'+''.join(random.choice(string.ascii_lowercase) for i in range(4))
            else:
                df.name = name

            if fill > 0:
                for i in range(fill):
                    if i == 0:
                        temp_name = "test_ft"
                    else:
                        temp_name = 'test_ft_'+''.join(random.choice(string.ascii_lowercase) for i in range(cfg.CONST_SAMPLE_NAME))
                    temp_val = Tools.sample(len(dr))
                    df.insert(len(df.columns),temp_name,temp_val)
            else:
                raise ValueError()

            return Timeseries(df)

    @staticmethod
    def test_Container(start,end,length):
        temp_name = 'test_Container_'+''.join(random.choice(string.ascii_lowercase) for i in range(cfg.CONST_SAMPLE_NAME))
        result = Container(temp_name)
        
        for i in range(0,length):
            freq = random.choice(cfg.CONST_FREQS)
            dr = pd.date_range(start=start,end=end,freq=freq).date

            if i == 0:
                temp_df_name = 'test_DF'
            else:    
                temp_df_name = None

            t_start = datetime.datetime.strptime(start,'%d/%m/%Y') + datetime.timedelta(days=len(dr) * np.random.uniform(0,cfg.CONST_SAMPLE_RANGE_CONT_VAR))
            t_end = datetime.datetime.strptime(end,'%d/%m/%Y') - datetime.timedelta(days=len(dr) * np.random.uniform(0,cfg.CONST_SAMPLE_RANGE_CONT_VAR))

            tt_start = t_start.date()
            tt_end = t_end.date()

            print(tt_start)

            for _ in range(0,random.choice(cfg.CONST_SAMPLE_RANGE_DF_COUNT)+1):
                result.load_DF(Tools.test_DF(tt_start,tt_end,freq,random.choice(cfg.CONST_SAMPLE_RANGE_FT_COUNT),temp_df_name))
        
        return result

class FileIO:
    @staticmethod
    def writeMZ(path,input):
        with open(path,'wb') as handle:
            pickle.dump(input,handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    @staticmethod
    def readMZ(path):
        with open(path,'rb') as handle:
            return pickle.load(handle)

class Timeseries:
    def __init__(self,input,name=None):
        if isinstance(input,str):
            self.path = input

            self.name = self.path.split("/")[-1].split(".")[0]
            self.type = self.path.split("/")[-1].split(".")[-1]

            if (self.type in ['xls','xlsx']):
                self.data = pd.read_excel(self.path,index_col=0)
            elif (self.type == "csv"):
                self.data = pd.read_csv(self.path,index_col=0)
            else:
                raise ValueError(cfg.ERROR_FILETYPE) 
        elif isinstance(input,pd.DataFrame):
            self.data = input
            if name is None:
                self.name = Tools.rand_name()
            else:
                self.name = name
            self.type = "pd"
        else:
            raise ValueError(cfg.ERROR_OBJTYPE)

        self.data.index.name = "date"
        self.data.index = pd.to_datetime(self.data.index)

        self.features = list(self.data.columns.values)
        self.index = self.data.index
        self.dr = pd.to_datetime(self.index)
        self.dr_min = self.dr.values[0]
        self.dr_max = self.dr.values[-1]
        self.freq = pd.infer_freq(self.index)

    def filter(self,input):
        return self.data.filter(input,axis=1)

    def sample(self,count):
        result = []
        for _ in range(0,count):
            result.append(self.data.columns.values[random.choice(range(len(self.data.columns.values)))])
        
        return result
    
    def match(self,freq,order):
        temp = self.data.resample(rule=freq).mean().interpolate(method='spline', order=order)
        self.data = temp
        self.freq = freq

    def get_match(self,freq,order):
        temp = self.data.resample(rule=freq).mean().interpolate(method='spline', order=order)
        return Timeseries(temp,name=self.name+'_matched_'+freq)
    
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
        temp = Timeseries(path)
        self.data[temp.name] = temp
        self.update()

    def load_DF(self,input):
        self.data[input.name] = input
        self.update()

    def sample(self):
        return self.data[self.keys[random.choice(range(len(self.data)))]]

    def report(self):
        df = pd.DataFrame()
        
        name = [] 
        type = []
        drmin = [] 
        drmax = []
        freq = []
        feature_count = []
        features = []

        for _,i in self.data.items():
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

        return df
    
    def build(self,input,start,end,freq,order):
        temp_df = []
        temp_index = []

        for key, value in input.items():
            # Timeseries Al
            temp_1 = self.data[key].data
            #print(temp_ts)
            # İlgili kolonları Al
            temp_2 = temp_1.filter(value)
            # İlgili Tarihleri Al
            temp_3 = temp_2.loc[start:end]
            #print(temp_3)
            # Matchini Al
            temp_4 = temp_3.resample(rule=freq).mean().interpolate(method='spline', order=order)
            # Naming convention        
            temp_dict = {}
            for i in value:
                temp_dict[i] = key+'_'+i

            temp_4 = temp_4.rename(columns=temp_dict)

            temp_df.append(temp_4)
            temp_index.append(temp_4.index.tolist())
        
        df_final = pd.concat(temp_df,axis=1).dropna()

        return Dataset(df_final)


    def save(self,path):
        f = open(path, 'wb')
        pickle.dump(self.__dict__, f, 2)
        f.close()

class Dataset:
    def __init__(self,data):
        self.data = data

        self.features = list(self.data.columns.values)

        self.freq = pd.infer_freq(self.data.index)
        #self.period = cfg.CONST_FREQ_MAP[self.freq.split("-")[0]]
        
        # Seasonal Decomposition
        #self.sd_add = sm.tsa.seasonal_decompose(np.asarray(self.data), model='additive',period=self.period)
        #self.sd_mult = sm.tsa.seasonal_decompose(np.asarray(self.data), model='multiplicative',period=self.period)
        #tmp = sm.tsa.SARIMAX(self.data, order=(2,0,0))
        #self.sarimax = tmp.fit()
        #self.analysis = {'sd_add_trend':self.sd_add.trend,
        #                 'sd_add_seasonal':self.sd_add.seasonal,
        #                 'sd_mult_trend':self.sd_mult.trend,
        #                 'sd_mult_seasonal':self.sd_mult.seasonal}