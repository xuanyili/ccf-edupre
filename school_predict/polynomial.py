import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def polynomial(df_data, col_x, col_y, predict_range):
    data = df_data

    x = data[col_x].to_list()
    y = data[col_y].to_list()
    a=np.polyfit(x,y,3)#用2次多项式拟合x，y数组
    b=np.poly1d(a)#拟合完之后用这个函数来生成多项式对象
    predict_x = [x[-1] + i for i in range(1, predict_range + 1)]
    p=b(predict_x)
    return p