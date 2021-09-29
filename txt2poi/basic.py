import spacy
import pandas as pd
from haversine import haversine

nlp = spacy.load('zh_core_web_sm')

def clear_name_unusedinfo(name1):
    name1 = name1.replace('浙江', '')
    name1 = name1.replace('杭州', '')
    name1 = name1.replace('市', '')
    name1 = name1.replace('省', '')
    name1 = name1.replace('金华', '')
    name1 = name1.replace('宁波', '')
    name1 = name1.replace('湖州', '')
    name1 = name1.replace('西湖区', '')
    name1 = name1.replace('余杭区', '')
    name1 = name1.replace('义乌', '')
    name1 = name1.replace('德清县', '')
    name1 = name1.replace('海曙区', '')
    return name1

def compare_name(name1, name2):
    name1 = clear_name_unusedinfo(name1)
    name2 = clear_name_unusedinfo(name2)
    if name1 == [] or name2 == [] or name1 == '' or name2 == '':
        return 0
    doc1 = nlp(name1)
    doc2 = nlp(name2)
    return  doc1.similarity(doc2)

def get_distance_byloc(loc1, loc2):
    return haversine(loc1, loc2)*1000

def get_gaodematched_poi_info(tianditu_info, gaode_info):
    _info1 = pd.DataFrame(columns=['name', 'address', 'point_x', 'point_y','specify', 'dataType'])
    _info2 = pd.DataFrame(columns=['gd_point_x','gd_point_y'])
    gaode_unmatch_g = pd.DataFrame(columns=['name', 'address', 'gd_point_x', 'gd_point_y','region', 'dataType'])
    gaode_unmatch_t = pd.DataFrame(columns=['name', 'address', 'point_x', 'point_y','specify', 'dataType'])
    for i, row_t in tianditu_info.iterrows():
        for j, row_g in gaode_info.iterrows():
            similar1 = compare_name(row_t['address'], row_g['address'])
            similar2 = compare_name(row_t['name'], row_g['name'])
            #print(row['format_address1'], row['format_address2'], similar)
            if similar1 > 0.9 and similar2 > 0.9:
                #print(row_t['address']+row_t['name'], row_g['address']+row_g['name'],similar1, similar2)
                _info1 = _info1.append(row_t, ignore_index=True)
                _info2 = _info2.append(row_g[['gd_point_x','gd_point_y']], ignore_index=True)
                gaode_info = gaode_info.drop(index = j)
                tianditu_info = tianditu_info.drop(index = i)
                break
        gaode_unmatch_g = gaode_unmatch_g.append(gaode_info, ignore_index=True)
        gaode_unmatch_t = gaode_unmatch_t.append(tianditu_info, ignore_index=True)
    info = pd.concat([_info1, _info2], axis=1)
    return info, gaode_unmatch_g, gaode_unmatch_t

import math
A_ALIS = 6378137
B_ALIS = 6356752.3142
 
E = math.sqrt(A_ALIS * A_ALIS - B_ALIS * B_ALIS) / A_ALIS
 
def transform_latlonhei2xyz(lon, lat, h):
    """ 大地坐标系 转 空间直角坐标系 """
    lon, lat, h = math.radians(float(lon)), math.radians(float(lat)), float(h)
 
    W = math.sqrt(1 - E * E * math.sin(lat) * math.sin(lat))
    N = A_ALIS / W
 
    x = (N + h) * math.cos(lat) * math.cos(lon)
    y = (N + h) * math.cos(lat) * math.sin(lon)
    z = (N * (1 - E * E) + h) * math.sin(lat)
 
    return (x, y, z)