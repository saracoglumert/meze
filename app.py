import meze as mz
from statsmodels.tsa.seasonal import seasonal_decompose
import numpy as np

if __name__ == "__main__":
       t = mz.Tools
       f = mz.FileIO

       cont = mz.Container('deneme')

       cont.load_file('data/interests.xls')
       cont.load_file('data/WB.xlsx')
       
       cont.load_folder('data/SP500',['AAPL.xlsx',
                                      'GOOG.xlsx',
                                      'NVDA.xlsx',
                                      'TSLA.xlsx',
                                      'MSFT.xlsx',
                                      'AMZN.xlsx',
                                      'META.xlsx'])
       

       #
       
       filter=  {'interests':['FED','ECB'],
                 'WB':[],
                 'AAPL':['price'],
                 'GOOG':['price'],
                 'NVDA':['price'],
                 'TSLA':['price'],
                 'MSFT':['price'],
                 'AMZN':['price'],
                 'META':['price']}

       res = cont.build(filter,'D',3)