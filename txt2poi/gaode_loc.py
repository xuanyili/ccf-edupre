import requests
import pandas as pd
from .basic import compare_name
import sys
sys.path.append(sys.path[0]+"/..")
from data_process import DataProcess

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
            return addresses
        
        else:
            #print(params, result['status'])
            regeocodes = result['regeocodes']
            count = len(regeocodes)
            for i in range(0, int(count)):
                regeocode = regeocodes[i]
                series = pd.Series({'format_address2': regeocode['formatted_address']})
                addresses=addresses.append(series, ignore_index=True)

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
    
    def get_allcorrectloc(self):
        process = DataProcess()
        name = process.get_allschoolinfo()
        loc, address1 = self.getlocbyname(name)
        address2 = self.getaddressbyloc(loc)
        address = pd.concat([loc, address2], axis=1)
        self.allloc = address
        #print(loc, address1, address2)
        for i, row in address.iterrows():
            similar = compare_name(row['name'], row['format_address2'])
            #print(row['format_address1'], row['format_address2'], similar)
            if similar < 0.8:
                print(row['name'], row['format_address2'], similar)
                address = address.drop(index = i)
        self.allcorrectloc = address.reset_index()
        return self.allcorrectloc
    
    def get_allstoreloc(self):
        return self.allloc