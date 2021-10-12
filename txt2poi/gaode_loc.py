import requests
import pandas as pd
from .basic import compare_name, get_distance_byloc
import sys
sys.path.append(sys.path[0]+"/..")
from data_process import DataProcess
from .model.gjc2wsg import Gcj2Wgs_SimpleIteration

types = {
    '幼儿园': '141204',
    '小学': '141203',
    '中学': '141202',
    '职业技术学校': '141206'
}
regions = {
    '西湖区': '330106',
    '余杭区': '330110',
    '义乌市': '330782',
    '德清县': '330521',
    '海曙区': '330203'
}

    
type_gd = '141200 | 141201 | 141202 | 141203 | 141204 | 141206'
city_gd = '330106 | 330110 | 330782 | 330521 | 330203'

class gaode_api(object):
    def __init__(self, key):
        self.key = key
    
    def __getlocbyname(self, address):
        #内部接口
        #print(address)
        locs=pd.DataFrame(columns=['gd_point_x', 'gd_point_y'])
        addresses = pd.DataFrame(columns=['format_address1'])
        url = 'https://restapi.amap.com/v3/geocode/geo?parameters'
        params = {
            'key': self.key,
            'address': address,
            'batch': 'true'
        }
        res=requests.get(url, params)
        result = res.json()
        if result['status'] == 0:
            print("ERROR:{}".format(result['info']))
            res.close()
            return locs, addresses
        
        else:
            count = result['count']
            #print(count)
            geocodes = result['geocodes']
            #print(result)
            for index in range(0, int(count)):
                geocode = geocodes[index]
                #print("***{}".format(geocode['location']))
                if geocode['location'] == []:
                    [x,y] = [120,30]
                else:
                    [x,y] = geocode['location'].split(',')
                series_loc = pd.Series({'gd_point_x': float(x), 'gd_point_y': float(y)})
                series_add = pd.Series({'format_address1': geocode['formatted_address']})
                addresses = addresses.append(series_add, ignore_index=True)
                locs=locs.append(series_loc, ignore_index=True)
                #print(geocode['location'], locs)
        res.close()
        return locs, addresses

    def getlocbyname(self, name):
        address = ''
        name = name.reset_index()
        locs = pd.DataFrame(columns=['gd_point_x', 'gd_point_y'])
        addresses = pd.DataFrame(columns=['format_address1'])
        for i, row in name.iterrows():
            address += row['name'] + '|'
            if (i + 1) % 10 == 0:
                address = address[:-1]
                _locs, _addresses = self.__getlocbyname(address)
                address = ''
                locs = locs.append(_locs, ignore_index=True)
                addresses = addresses.append(_addresses, ignore_index=True)
        address = address[:-1]
        _locs, _addresses = self.__getlocbyname(address)
        locs = locs.append(_locs, ignore_index=True)
        addresses = addresses.append(_addresses, ignore_index=True)
        locs = pd.concat([name, locs], axis=1)
        return locs, addresses

    def __getaddressbyloc(self, loc):
        #内部接口
        addresses=pd.DataFrame(columns=['format_address2'])
        url = 'https://restapi.amap.com/v3/geocode/regeo?parameters'
        params = {
            'key': self.key,
            'location': loc,
            'batch': 'true'
        }
        res=requests.get(url, params)
        result = res.json()
        if result['status'] == 0:
            print("ERROR:{}".format(result['info']))
            res.close()
            return addresses
        
        else:
            #print(params, result['status'])
            regeocodes = result['regeocodes']
            count = len(regeocodes)
            for i in range(0, int(count)):
                regeocode = regeocodes[i]
                series = pd.Series({'format_address2': regeocode['formatted_address']})
                addresses=addresses.append(series, ignore_index=True)
        res.close()
        return addresses

    def getaddressbyloc(self, loc):
        addresses=pd.DataFrame(columns=['format_address2'])
        locs = ''
        for i, row in loc.iterrows():
            locs += str(row['gd_point_x']) + ',' + str(row['gd_point_y']) + '|'
            if (i + 1) % 20 == 0:
                locs = locs[:-1]
                __addresses = self.__getaddressbyloc(locs)
                addresses = addresses.append(__addresses, ignore_index=True)
                locs = ''
        locs = locs[:-1]
        __addresses = self.__getaddressbyloc(locs)
        addresses = addresses.append(__addresses, ignore_index=True)

        return addresses

    def displaybyloc(self, loc, file="gaode.png", zoom=15):
        url = 'https://restapi.amap.com/v3/staticmap?parameters'
        params = {
            'key': self.key,
            'zoom': str(zoom),
            'markers': 'mid,0xFF0000,A:'+str(loc[0])+','+str(loc[1])
        }
        res=requests.get(url, params)
        with open(file, 'wb') as f:
            f.write(res.content)
        res.close()
    
    def get_allcorrectloc(self, info):
        loc, address1 = self.getlocbyname(info)
        address2 = self.getaddressbyloc(loc)
        address = pd.concat([loc, address2], axis=1)
        self.allloc = address
        #print(loc, address1, address2)
        for i, row in address.iterrows():
            similar = compare_name(row['name'], row['format_address2'])
            #print(row['format_address1'], row['format_address2'], similar)
            if similar < 0.9:
                print(row['name'], row['format_address2'], similar)
                address = address.drop(index = i)
        self.allcorrectloc = address.reset_index()
        return self.allcorrectloc
    
    def get_allstoreloc(self):
        return self.allloc
    
    def get_poiinfo(self, type, region):
        info = pd.DataFrame(columns=['name', 'address', 'gd_point_x', 'gd_point_y','region', 'dataType'])
        url = 'https://restapi.amap.com/v5/place/text?parameters'
        page_num = 1
        while True:
            params = {
                'key': self.key,
                'types': types[type],
                'region': regions[region],
                'city_limit': 'true',
                'page_num': str(page_num),
                'page_size': '25'
            }

            res = requests.get(url, params)
            page_num +=1
            result = res.json()
            count = int(result['count'])
            if count == 0:
                break
            pois = result['pois']
            for index in range(0, count):
                poi = pois[index]
                [x, y] = poi['location'].split(',')
                series = pd.Series({'name': poi['name'], 'address': poi['cityname']+poi['adname']+poi['address'], 
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
                print("地址1：{}；地址2:{}；相似度：{}".format(name, add, similar))
                result = 0
            else:
                result = -1
        else:
            locs, _ = self.__getlocbyname(name)
            if len(locs) == 0:
                return -1, (0, 0), ''
            loc = (float(locs['gd_point_x']), float(locs['gd_point_y']))
            x, y = Gcj2Wgs_SimpleIteration(loc[0], loc[1])
            loc_v = (x, y)
            address = self.__getaddressbyloc(str(loc[0])+','+str(loc[1]))
            add = address['format_address2'][0]
            similar = compare_name(name, add)
            distance = get_distance_byloc(loc_v, loc_o)
            if distance < 60:
                result = 1
            elif similar > 0.95:
                print("地址1：{}；地址2:{}；相似度：{}".format(name, add, similar))
                result = 0
            else:
                result = -1
        return result, loc_v, add


    def getloc_byinputtips(self, keyword):
        url = 'https://restapi.amap.com/v3/assistant/inputtips?parameters'
        params = {
            'key': self.key,
            'keywords': keyword,
            'type': type_gd,
            'city': city_gd,
            'citylimit': 'true'
        }
        res = requests.get(url, params)
        result = res.json()
        count = result['count']
        if count == '0':
            res.close()
            return -1, (0, 0), ''
        else:
            tip = result['tips'][0]
            [x,y] = tip['location'].split(',')
            add = tip['name']
            loc_v = (float(x), float(y))
            res.close()
            return 1, loc_v, add