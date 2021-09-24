import requests

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