import config as cfg

import pandas as pd
import numpy as np
import statsmodels.api as sm
import string
import random
import datetime
import pickle
import requests
from io import StringIO
import re
import dateutil.parser
import os

import pandasdmx as sdmx
import yfinance as yf
import wbgapi as wb

class Fetcher:
    class YahooFinance:
        def fetch(self,tick,start,end):
            if isinstance(tick,str):
                tmp = yf.Ticker(tick)

                start = dateutil.parser.parse(start).strftime("%Y-%m-%d")
                end = dateutil.parser.parse(end).strftime("%Y-%m-%d")

                tmp2 = tmp.history(start=start,end=end).iloc[:,3:4].rename(columns={"Close": "price", "Volume": "volume", "Dividends":"dividends"})
                tmp2.index = tmp2.index.date

                return tmp2
            elif isinstance(tick,list):
                df = pd.DataFrame()
                
                for t in tick:
                    tmp = yf.Ticker(t)

                    start = dateutil.parser.parse(start).strftime("%Y-%m-%d")
                    end = dateutil.parser.parse(end).strftime("%Y-%m-%d")

                    tmp2 = tmp.history(start=start,end=end).iloc[:,3:4].rename(columns={"Close": "price", "Volume": "volume", "Dividends":"dividends"})
                    tmp2.index = tmp2.index.date

                    df.insert(len(df.columns),t,tmp2['price'])

                return df
            else:
                raise ValueError(cfg.ERROR_OBJTYPE)
            
    class FRED:
        pass

    class ECB:
        def fetch(self,tick,region,start,end):
            tmp = sdmx.Request('ECB')
            res = tmp.data(resource_id = 'EXR', key={'CURRENCY': ['CHF', 'EUR']}, params = {'startPeriod': '2016'})
            data = res.data

            return data
    class WB:
        pass

    class IMF:
        pass

class Tools:
    @staticmethod
    def td_format(td_object):
        seconds = int(td_object.total_seconds())
        periods = [
            ('year',        60*60*24*365),
            ('month',       60*60*24*30),
            ('day',         60*60*24),
            ('hour',        60*60),
            ('minute',      60),
            ('second',      1)
        ]

        strings=[]
        for period_name, period_seconds in periods:
            if seconds > period_seconds:
                period_value , seconds = divmod(seconds, period_seconds)
                has_s = 's' if period_value > 1 else ''
                strings.append("%s %s%s" % (period_value, period_name, has_s))

        return ", ".join(strings)
    
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
        self.timedelta = pd.to_timedelta(np.diff(self.index).min())
        self.freq = cfg.CONST_FREQ_MAP[min(range(len(cfg.CONST_FREQ_MAP_SECONDS)), key=lambda i: abs(cfg.CONST_FREQ_MAP_SECONDS[i]-self.timedelta.total_seconds()))]
        self.na = self.data.isna().sum().sum()

    def sample(self,count):
        result = []
        for _ in range(0,count):
            result.append(self.data.columns.values[random.choice(range(len(self.data.columns.values)))])
        
        return result
    def filter_features(self,input):
        self.data = self.data.filter(input,axis=1)
    
    def get_filter_feautres(self,input):
        return self.data.filter(input,axis=1)

    def filter_index(self,start,end):
        self.data = self.data.loc[start:end]

    def get_filter_index(self,start,end):
        return self.data.loc[start:end]

    def match(self,freq,order):
        temp = self.data.resample(rule=freq).mean().interpolate(method='spline', order=order, s=0.1)
        self.data = temp
        self.freq = freq

    def get_match(self,freq,order):
        temp = self.data.resample(rule=freq).mean().interpolate(method='spline', order=order, s=0.1)
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

    def load_folder(self,folder,files=None):
        if files is None:
            tmp = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        else:
            tmp = files
        
        paths = [folder+'/'+i for i in tmp]

        for i in range(0,len(paths)):
            if not tmp[i][0] == '.':
                self.load_file(paths[i])

        return tmp

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
        df.insert(len(df.columns),'freq',freq)
        df.insert(len(df.columns),'features_count',feature_count)
        df.insert(len(df.columns),'features',features)

        return df
    
    def build(self,input,freq,order,start=None,end=None):
        temp_df = []
        temp_index = []

        if start is None and end is None:
            start = self.dr_min
            end = self.dr_max

        for key, value in input.items():
            print(self.data[key].freq)
            print(freq)
            # If equal, pass
            if self.data[key].freq == freq:
                break
            # Timeseries Al
            temp_1 = self.data[key]
            #print(temp_ts)
            # İlgili kolonları Al
            temp_2 = temp_1.get_filter(value)
            # İlgili Tarihleri Al
            temp_3 = temp_2.loc[start:end]
            #print(temp_3)
            # Matchini Al
            temp_4 = self.data[key].get_match(freq,order).data
            # Naming convention        
            temp_dict = {}
            for i in value:
                temp_dict[i] = key+'_'+i

            temp_4 = temp_4.rename(columns=temp_dict)

            temp_df.append(temp_4)
            temp_index.append(temp_4.index.tolist())
        
        df_final = pd.concat(temp_df,axis=1).dropna()

        return Dataset(df_final)

    def build2(self,input,freq,order,start=None,end=None):
        result = []
        
        if start is None and end is None:
            start = self.dr_min
            end = self.dr_max

        for key, value in input.items():
            obj = self.data[key]
            
            if not freq == obj.freq:
                obj.match(freq,order)
            
            obj.filter_features(value)
            obj.filter_index(start,end)
            obj.data.columns = [key+'_'+i for i in obj.data.columns]

            result.append(obj.data)

        return pd.concat(result,axis=1)

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