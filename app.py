import meze as mz
from statsmodels.tsa.seasonal import seasonal_decompose
import numpy as np

if __name__ == "__main__":
    t = mz.Tools
    f = mz.FileIO
    
    cont = mz.Container('deneme')

    cont.load_file('data/WB.xlsx')
    cont.load_file('data/stocks/AAPL.xlsx')
    cont.load_file('data/stocks/NVDA.xlsx')

    inp = {'WB':['USA_NY.GDP.MKTP.CD','EUU_NY.GDP.MKTP.CD'],
           'AAPL':['price'],
           'NVDA':['price']}

    res = cont.build(inp,'1/1/2005','1/1/2023', 'D', 3)
