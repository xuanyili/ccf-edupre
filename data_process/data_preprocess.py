import pandas as pd
import numpy as np

class DataProcess(object):
    def __init__(self):
        self.origin_data = pd.read_csv("../../data/schoolinfo.csv", encoding='gbk')
    
    def get_allschoolname(self, type=None, area=None):
        data = self.origin_data
        if area != None:
            data = data.groupby(['qxmc']).get_group(area)
        if type != None:
            data = data.groupby(['dj']).get_group(type)
        return data[['name']]

    def get_allschooladdress(self, type=None, area=None):
        data = self.origin_data
        if area != None:
            data = data.groupby(['qxmc']).get_group(area)
        if type != None:
            data = data.groupby(['dj']).get_group(type)
        return data[['address']]

    def get_schoolpointbyname(self, name):
        data = self.origin_data
        point_x = data[data['name']==name]['point_x']
        point_y = data[data['name']==name]['point_y']
        return (point_x, point_y)