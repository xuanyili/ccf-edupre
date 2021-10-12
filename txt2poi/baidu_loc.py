import requests
import pandas as pd
from .basic import compare_name, get_distance_byloc
import sys
sys.path.append(sys.path[0]+"/..")
from data_process import DataProcess
from .model.gjc2wsg import Gcj2Wgs_SimpleIteration
import time

types = {
    '幼儿园': '幼儿园',
    '小学': '小学',
    '中学': '中学'
}
regions = {
    '西湖区': '西湖区',
    '余杭区': '余杭区',
    '义乌市': '义乌市',
    '德清县': '德清县',
    '海曙区': '海曙区'
}

regions_bd = '西湖区 | 余杭区 | 义乌市 | 德清县 | 海曙区'

class baidu_api(object):
    def __init__(self, key):
        self.key = key
    
    def __getlocbyname(self, address):
        #内部接口
        #print(address)
        locs=pd.DataFrame(columns=['bd_point_x', 'bd_point_y'])
        addresses = pd.DataFrame(columns=['format_address1'])
        url = 'https://api.map.baidu.com/geocoding/v3/?parameters'
        params = {
            'ak': self.key,
            'address': address,
            'output': 'json'
        }
        res=requests.get(url, params)
        results = res.json()
        result = results['result']
        if results['status'] != 0:
            print("ERROR:{}".format(results['status']))
            res.close()
            return locs, addresses
        
        else:
            #print(count)
            geocode = result['location']
            #print(result)
            
            x,y = geocode['lng'], geocode['lat']
            
            series_loc = pd.Series({'bd_point_x': float(x), 'bd_point_y': float(y)})
            series_add = pd.Series({'format_address1': ''})
            addresses = addresses.append(series_add, ignore_index=True)
            locs=locs.append(series_loc, ignore_index=True)
                #print(geocode['location'], locs)
        res.close()
        return locs, addresses

    def getlocbyname(self, name):
        address = ''
        name = name.reset_index()
        locs = pd.DataFrame(columns=['bd_point_x', 'bd_point_y'])
        addresses = pd.DataFrame(columns=['format_address1'])
        for i, row in name.iterrows():
            address = row['name']
            _locs, _addresses = self.__getlocbyname(address)
            locs = locs.append(_locs, ignore_index=True)
            addresses = addresses.append(_addresses, ignore_index=True)

        locs = pd.concat([name, locs], axis=1)
        return locs, addresses

    def displaybyloc(self, mid, loc, file="baidu.png", width=500, height=500, zoom=18):
        url = 'https://api.map.baidu.com/staticimage/v2?parameters'
        params = {
            'ak': self.key,
            'center': str(mid[0])+','+str(mid[1]),
            'width': str(width),
            'height': str(height),
            'zoom': str(zoom),
            'coordtype': 'wgs84ll',
            'markers': str(loc[0])+','+str(loc[1])
        }
        res=requests.get(url, params)
        with open(file, 'wb') as f:
            f.write(res.content)
    
    def get_poiinfo(self, type, region):
        info = pd.DataFrame(columns=['name', 'address', 'gd_point_x', 'gd_point_y','region', 'dataType'])
        url = 'https://api.map.baidu.com/place/v2/search?parameters'
        page_num = 0
        while True:
            params = {
                'ak': self.key,
                'tag': '教育培训',
                'query': types[type],
                'region': regions[region],
                'city_limit': 'true',
                'page_num': str(page_num),
                'page_size': '20',
                'output': 'json',
                'ret_coordtype': 'gcj02ll'
            }

            res = requests.get(url, params)
            
            result = res.json()
            if result['status'] == 401:
                time.sleep(1)
                continue
            page_num +=1
            pois = result['results']
            count = len(pois)
            if count == 0:
                break
            
            for index in range(0, count):
                poi = pois[index]
                x, y = poi['location']['lng'], poi['location']['lat']
                series = pd.Series({'name': poi['name'], 'address': poi['address'], 
                'gd_point_x': float(x), 'gd_point_y': float(y),'region': region, 'dataType': type})
                info = info.append(series, ignore_index=True)

            res.close()
        return info

    def getallpoiinfo(self):
        info = pd.DataFrame(columns=['name', 'address', 'gd_point_x', 'gd_point_y','region', 'dataType'])
        for region in regions:
            for type in types:
                _info = self.get_poiinfo(type, region)
                info = info.append(_info, ignore_index=True)
        return info
    
    def verify_loc_by_name(self, name, loc_o):
    #  1:验证成功; -1:验证失败
        result, loc_v, add = self.getloc_byinputtips(name)
        if result == 1:
            x, y = Gcj2Wgs_SimpleIteration(loc_v[0], loc_v[1])
            loc_v = (x, y)
            distance = get_distance_byloc(loc_v, loc_o)
            similar = compare_name(name, add)
            if distance < 60:
                result = 1
            elif similar > 0.95:
                print("地址1：{}-{}；地址2:{}-{}；相似度：{};距离：{}"
                .format(name, loc_o, add, loc_v, similar, distance))
                result = 0
            else:
                result = -1
        return result, loc_v, add


    def getloc_byinputtips(self, keyword):
        url = 'https://api.map.baidu.com/place/v2/suggestion?parameters'
        params = {
            'ak': self.key,
            'query': keyword,
            'region': regions_bd,
            'citylimit': 'true',
            'output': 'json',
            'ret_coordtype': 'gcj02ll'
        }
        res = requests.get(url, params)
        results = res.json()
        while results['status'] == 401:
            res.close()
            res = requests.get(url, params)
            results = res.json()
        result = results['result']
        if len(result) == 0:
            res.close()
            return -1, (0, 0), ''
        else:
            tip = result[0]
            x,y = tip['location']['lng'], tip['location']['lat']
            add = tip['name']
            loc_v = (float(x), float(y))
            res.close()
            return 1, loc_v, add