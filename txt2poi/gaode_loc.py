import requests
import pandas as pd

class gaode_api(object):
    def __init__(self, key):
        self.key = key
    
    def getlocbyname(self, name):
        address = ''
        for i, row in name.iterrows():
            address += row['name'] + '|'
        address = address[:-1]
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
            return 0
        
        else:
            result = res.json()
            count = result['count']
            geocodes = result['geocodes']
            locs=pd.DataFrame(columns=['point_x', 'point_y'])
            for i in range(0, int(count)):
                geocode = geocodes[i]
                [x,y] = geocode['location'].split(',')
                series = pd.Series({'point_x': float(x), 'point_y': float(y)}, name=i)
                locs=locs.append(series)

        return locs

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