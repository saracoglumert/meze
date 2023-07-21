import meze as mz
from statsmodels.tsa.seasonal import seasonal_decompose
import numpy as np
import scipy.special as sc

sc.seterr(singular='raise')

if __name__ == "__main__":
       cont = mz.Container('deneme')


       cont.load_file('data/interests.xls')
       cont.load_file('data/WB.xlsx')
       
       cont.load_folder('data/SP500')
       
       a = cont.data.keys()
       b = [['price'] for _ in range(len(a))]
       filter_all = dict(zip(a,b))

       filter =  {#'interests':['FED','ECB'],
                 #'WB':[],
                 'AAPL':['price'],
                 'GOOG':['price'],
                 'NVDA':['price'],
                 'TSLA':['price'],
                 'MSFT':['price'],
                 'META':['price'],
                 'AMZN':['price'],
                 'ADBE':['price'],
                 'ADSK':['price'],
                 'AVGO':['price'],
                 'ANSS':['price'],
                 'CSCO':['price'],
                 'HPE':['price'],
                 'HPQ':['price'],
                 'INTC':['price'],
                 'IBM':['price'],
                 'KEYS':['price'],
                 'MCHP':['price'],
                 'ORCL':['price'],
                 'PANW':['price'],
                 'QCOM':['price'],
                 'CRM':['price'],
                 'STX':['price'],
                 'TXN':['price'],
                 'VRSN':['price'],
                 'WDC':['price']}

       res = cont.build(filter,'D',3)

       prob = mz.Problems.Clustering.kMeans(res,3)
       #prob = mz.Problems.Clustering.