import requests
import pandas as pd
from .gaode_loc import gaode_api
from .basic import compare_name

specifys = {
    '西湖区': '156330106',
    '余杭区': '156330110',
    '义乌市': '156330782',
    '德清县': '156330521',
    '海曙区': '156330203'
}

dataTypes = {
    '幼儿园': '160101',
    '小学': '160102',
    '中学': '160103',
    '中专': '160104',
    '大专': '160105'
}

class tianditu_api(object):
    def __init__(self, key):
        self.key = key

    def getlocbyname(self, name):
        url = 'http://api.tianditu.gov.cn/geocoder?parameters'
        ds = {"keyWord": name}
        params = {
            'tk': self.key,
            'ds': str(ds)
        }
        res=requests.get(url, params)
        loc = res.json()['location']
        lon = loc['lon']
        lat = loc['lat']

        return (lon, lat)

    def getaddressbyloc(self, loc):
        url = 'http://api.tianditu.gov.cn/geocoder?parameters'
        postStr = {'lon': loc[0], 'lat': loc[1], 'ver':1}
        params = {
            'tk': self.key,
            'postStr': str(postStr),
            'type': 'geocode'
        }
        res=requests.get(url, params)
        result = res.json()['result']
        address = result['formatted_address']

        return address

    def displaybyloc(self, mid, loc, file="tianditu.png", width=500, height=500, zoom=15):
        url = 'http://api.tianditu.gov.cn/staticimage?parameters'
        params = {
            'tk': self.key,
            'center': str(mid[0])+','+str(mid[1]),
            'width': str(width),
            'height': str(height),
            'zoom': str(zoom),
            'layers': 'vec_c,cva_c',
            'markers': str(loc[0])+','+str(loc[1])
        }
        res=requests.get(url, params)
        with open(file, 'wb') as f:
            f.write(res.content)
    
    def getpoiinfo(self, specify, dataType):
        info = pd.DataFrame(columns=['name', 'address', 'point_x', 'point_y','specify', 'dataType'])
        url = 'http://api.tianditu.gov.cn/v2/search?parameters'

        postStr = {
            'specify': specifys[specify],
            'queryType': '13',
            'start': '0',
            'count': '1',
            'dataTypes': dataTypes[dataType]
        }
        params = {
            'tk': self.key,
            'type':'query',
            'postStr':str(postStr)
        }
        res = requests.get(url, params)
        result = res.json()
        counts = int(result['count'])
        times = int(counts/300)
        for i in range(0, times + 1):
            postStr = {
                'specify': specifys[specify],
                'queryType': '13',
                'start': str(i),
                'count': '300',
                'dataTypes': dataTypes[dataType],
                'show': '2'
            }
            params = {
            'tk': self.key,
            'type':'query',
            'postStr':str(postStr)
        }
            res = requests.get(url, params)
            result = res.json()
            pois = result['pois']
            if i == times:
                count = counts % 300
            else:
                count = 300
            for index in range(0, count):
                poi = pois[index]
                [x, y] = poi['lonlat'].split(',')
                address = poi['province'] + poi['city'] + poi['county'] + poi['address']
                series = pd.Series({'name': poi['name'], 'address': address, 
                'point_x': float(x), 'point_y': float(y),'specify': specify, 'dataType': dataType})
                info = info.append(series, ignore_index=True)
        
        return info

    def getallpoiinfo(self):
        info = pd.DataFrame(columns=['name', 'address', 'point_x', 'point_y','specify', 'dataType'])
        for specify in specifys:
            for datatype in dataTypes:
                _info = self.getpoiinfo(specify, datatype)
                info = info.append(_info, ignore_index=True)
        return info

    def getallcorrect_gaodepoiinfo(self, key):
        info1 = pd.DataFrame(columns=['name', 'address', 'point_x', 'point_y','specify', 'dataType'])
        info2 = pd.DataFrame(columns=['gd_point_x','gd_point_y'])
        self.gaode_unmatch_g = pd.DataFrame(columns=['name', 'address', 'gd_point_x', 'gd_point_y','region', 'dataType'])
        self.gaode_unmatch_t = pd.DataFrame(columns=['name', 'address', 'point_x', 'point_y','specify', 'dataType'])
        gaode = gaode_api(key)
        for specify in specifys:
            for datatype in dataTypes:
                tianditu_info = self.getpoiinfo(specify, datatype)
                if datatype == '中专' or datatype == '大专':
                    type = '职业技术学校'
                else:
                    type = datatype
                gaode_info = gaode.get_poiinfo(type, specify)
                for i, row_t in tianditu_info.iterrows():
                    for j, row_g in gaode_info.iterrows():
                        similar1 = compare_name(row_t['address'], row_g['address'])
                        similar2 = compare_name(row_t['name'], row_g['name'])
                        #print(row['format_address1'], row['format_address2'], similar)
                        if similar1 >0.99 or similar2 >0.99 or (similar1 + similar2) > 1.75:
                            print(row_t['address']+row_t['name'], row_g['address']+row_g['name'],similar1, similar2)
                            info1 = info1.append(row_t, ignore_index=True)
                            info2 = info2.append(row_g[['gd_point_x','gd_point_y']], ignore_index=True)
                            gaode_info = gaode_info.drop(index = j)
                            tianditu_info = tianditu_info.drop(index = i)
                            break
                self.gaode_unmatch_g = self.gaode_unmatch_g.append(gaode_info, ignore_index=True)
                self.gaode_unmatch_t = self.gaode_unmatch_g.append(tianditu_info, ignore_index=True)
        info = pd.concat([info1, info2], axis=1)
        return info

    def get_unmatch_info_t(self):
        return self.gaode_unmatch_t
    
    def get_unmatch_info_g(self):
        return self.gaode_unmatch_g