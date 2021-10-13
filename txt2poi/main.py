import sys
sys.path.append(sys.path[0]+"/..")
from .tianditu_loc import tianditu_api
from .basic import get_distance_byloc, compare_name
from .gaode_loc import gaode_api
from .baidu_loc import baidu_api
import pandas as pd
from .model.gjc2wsg import Gcj2Wgs_SimpleIteration

tianditukey = '2423a38b3af5569af8aa521babc5e349'
gaodekey = '6977ecc8c25093a80583a1cb5b2e6155'
baidukey = 'v4YOvobXA6CKDXzW2GjcrxAggIqByx7U'

specifys = {
    '西湖区': '156330106',
    '余杭区': '156330110',
    '义乌市': '156330782',
    '德清县': '156330521',
    '海曙区': '156330203'
}

def check_correct_origininfo(data):
    #check by tianditu api
    correct_locinfo = pd.DataFrame()
    uncorrect_locinfo = pd.DataFrame()
    notsure_locinfo = pd.DataFrame()
    correct_series = pd.DataFrame()
    uncorrect_series = pd.DataFrame()
    tianditu = tianditu_api(tianditukey)
    for i, row_t in data.iterrows():
        loc = (float(row_t['point_x']), float(row_t['point_y']))
        result, loc_v, address = tianditu.verify_loc_by_name(row_t['name'], loc)
        series = pd.Series({'verify_point_x': loc_v[0], 'verify_point_y': loc_v[1], 
                'verify_address': address, 'o_point_x': loc[0], 'o_point_y': loc[1]})
        if result == 1:
            correct_series = correct_series.append(series, ignore_index=True)
            correct_locinfo = correct_locinfo.append(row_t, ignore_index=True)
        elif result == 0:
            uncorrect_series = uncorrect_series.append(series, ignore_index=True)
            uncorrect_locinfo = uncorrect_locinfo.append(row_t, ignore_index=True)
        elif result == -1:
            notsure_locinfo = notsure_locinfo.append(row_t, ignore_index=True)
            #notsure_locinfo = notsure_locinfo.append(series, ignore_index=True)
    correct_locinfo = pd.concat([correct_locinfo, correct_series], axis=1)
    uncorrect_locinfo = pd.concat([uncorrect_locinfo, uncorrect_series], axis=1)
    return correct_locinfo, uncorrect_locinfo, notsure_locinfo

def _check_correct_infobypoi(data, poidata, type = 'tdt'):
    correct_locinfo = pd.DataFrame()
    correct_series = pd.DataFrame()
    uncorrect_locinfo = pd.DataFrame()
    uncorrect_series = pd.DataFrame()
    notsure_locinfo = pd.DataFrame()
    _similar = 0
    correct = False
    for j, row_poi in poidata.iterrows():
        similar = compare_name(data['name'], row_poi['name'])
        if similar > 0.9:
            if type == 'gd':
                x, y = float(row_poi['gd_point_x']), float(row_poi['gd_point_y'])
                lon, lat = Gcj2Wgs_SimpleIteration(x, y)
                loc2 = (lon, lat)
            elif type == 'bd':
                x, y = float(row_poi['gd_point_x']), float(row_poi['gd_point_y'])
                lon, lat = Gcj2Wgs_SimpleIteration(x, y)
                loc2 = (lon, lat)
            else:
                x, y = float(row_poi['point_x']), float(row_poi['point_y'])
                loc2 = (x, y)
            loc1 = (float(data['point_x']), float(data['point_y']))
            distance = get_distance_byloc(loc1, loc2)
            if distance < 60:
                series = pd.Series({'verify_point_x': loc2[0], 'verify_point_y': loc2[1], 
            'verify_address': row_poi['name'], 'o_point_x': x, 'o_point_y': y})
                correct_series = correct_series.append(series, ignore_index=True)
                correct_locinfo = correct_locinfo.append(data, ignore_index=True)
                correct = True
                break
            if similar > _similar:
                _similar = similar
                _distance = distance
                _name = row_poi['name']
                _x = x
                _y = y
    if _similar > 0.99 and correct == False:
        print("地址1：{}；地址2:{}；相似度：{}".format(data['name'], _name, _similar))
        series = pd.Series({'verify_point_x': loc2[0], 'verify_point_y': loc2[1],
         'verify_address': _name, 'o_point_x': _x, 'o_point_y': _y})
        uncorrect_locinfo = uncorrect_locinfo.append(data, ignore_index=True)
        uncorrect_series = uncorrect_series.append(series, ignore_index=True)
    elif correct == False:
        notsure_locinfo = notsure_locinfo.append(data, ignore_index=True)
    correct_locinfo = pd.concat([correct_locinfo, correct_series], axis=1)
    uncorrect_locinfo = pd.concat([uncorrect_locinfo, uncorrect_series], axis=1)

    #print(correct_locinfo, uncorrect_locinfo, notsure_locinfo)
    return correct_locinfo, uncorrect_locinfo, notsure_locinfo

def check_correct_bytianditupoi(data, poidata):
    correct_locinfo = pd.DataFrame()
    uncorrect_locinfo = pd.DataFrame()
    notsure_locinfo = pd.DataFrame()
    for i, row_t in data.iterrows():
        _poidata = poidata.groupby(['specify']).get_group(row_t['qxmc'])
        _correct_locinfo, _uncorrect_locinfo, _notsure_locinfo = _check_correct_infobypoi(row_t, _poidata)
        correct_locinfo = correct_locinfo.append(_correct_locinfo, ignore_index=True)
        uncorrect_locinfo = uncorrect_locinfo.append(_uncorrect_locinfo, ignore_index=True)
        notsure_locinfo = notsure_locinfo.append(_notsure_locinfo, ignore_index=True)
    return correct_locinfo, uncorrect_locinfo, notsure_locinfo

def check_correct_bygaodepoi(data, poidata):
    correct_locinfo = pd.DataFrame()
    uncorrect_locinfo = pd.DataFrame()
    notsure_locinfo = pd.DataFrame()
    for i, row_t in data.iterrows():
        _poidata = poidata.groupby(['region']).get_group(row_t['qxmc'])
        _correct_locinfo, _uncorrect_locinfo, _notsure_locinfo = _check_correct_infobypoi(row_t, _poidata, type = 'gd')
        correct_locinfo = correct_locinfo.append(_correct_locinfo, ignore_index=True)
        uncorrect_locinfo = uncorrect_locinfo.append(_uncorrect_locinfo, ignore_index=True)
        notsure_locinfo = notsure_locinfo.append(_notsure_locinfo, ignore_index=True)
    return correct_locinfo, uncorrect_locinfo, notsure_locinfo

def check_correct_bybaidupoi(data, poidata):
    correct_locinfo = pd.DataFrame()
    uncorrect_locinfo = pd.DataFrame()
    notsure_locinfo = pd.DataFrame()
    for i, row_t in data.iterrows():
        _poidata = poidata.groupby(['region']).get_group(row_t['qxmc'])
        _correct_locinfo, _uncorrect_locinfo, _notsure_locinfo = _check_correct_infobypoi(row_t, _poidata, type = 'bd')
        correct_locinfo = correct_locinfo.append(_correct_locinfo, ignore_index=True)
        uncorrect_locinfo = uncorrect_locinfo.append(_uncorrect_locinfo, ignore_index=True)
        notsure_locinfo = notsure_locinfo.append(_notsure_locinfo, ignore_index=True)
    return correct_locinfo, uncorrect_locinfo, notsure_locinfo

def check_correct_infobygetgdaddress(data):
    #check by tianditu api
    correct_locinfo = pd.DataFrame()
    uncorrect_locinfo = pd.DataFrame()
    notsure_locinfo = pd.DataFrame()
    correct_series = pd.DataFrame()
    uncorrect_series = pd.DataFrame()
    gaode = gaode_api(gaodekey)
    for i, row_t in data.iterrows():
        loc = (float(row_t['point_x']), float(row_t['point_y']))
        result, loc_v, address = gaode.verify_loc_by_name(row_t['name'], loc)
        series = pd.Series({'verify_point_x': loc_v[0], 'verify_point_y': loc_v[1], 
                'verify_address': address, 'o_point_x': loc[0], 'o_point_y': loc[1]})
        if result == 1:
            correct_series = correct_series.append(series, ignore_index=True)
            correct_locinfo = correct_locinfo.append(row_t, ignore_index=True)
        elif result == 0:
            uncorrect_series = uncorrect_series.append(series, ignore_index=True)
            uncorrect_locinfo = uncorrect_locinfo.append(row_t, ignore_index=True)
        elif result == -1:
            notsure_locinfo = notsure_locinfo.append(row_t, ignore_index=True)
            #notsure_locinfo = notsure_locinfo.append(series, ignore_index=True)
    correct_locinfo = pd.concat([correct_locinfo, correct_series], axis=1)
    uncorrect_locinfo = pd.concat([uncorrect_locinfo, uncorrect_series], axis=1)
    return correct_locinfo, uncorrect_locinfo, notsure_locinfo

def check_correct_infobygetbdaddress(data):
    #check by tianditu api
    correct_locinfo = pd.DataFrame()
    uncorrect_locinfo = pd.DataFrame()
    notsure_locinfo = pd.DataFrame()
    correct_series = pd.DataFrame()
    uncorrect_series = pd.DataFrame()
    baidu = baidu_api(baidukey)
    for i, row_t in data.iterrows():
        loc = (float(row_t['point_x']), float(row_t['point_y']))
        result, loc_v, address = baidu.verify_loc_by_name(row_t['name'], loc)
        series = pd.Series({'verify_point_x': loc_v[0], 'verify_point_y': loc_v[1], 
                'verify_address': address, 'o_point_x': loc[0], 'o_point_y': loc[1]})
        if result == 1:
            correct_series = correct_series.append(series, ignore_index=True)
            correct_locinfo = correct_locinfo.append(row_t, ignore_index=True)
        elif result == 0:
            uncorrect_series = uncorrect_series.append(series, ignore_index=True)
            uncorrect_locinfo = uncorrect_locinfo.append(row_t, ignore_index=True)
        elif result == -1:
            notsure_locinfo = notsure_locinfo.append(row_t, ignore_index=True)
            #notsure_locinfo = notsure_locinfo.append(series, ignore_index=True)
    correct_locinfo = pd.concat([correct_locinfo, correct_series], axis=1)
    uncorrect_locinfo = pd.concat([uncorrect_locinfo, uncorrect_series], axis=1)
    return correct_locinfo, uncorrect_locinfo, notsure_locinfo

def add_extrainfo_bypoi(poidata, existdata, type='tdt'):
    extra_info = pd.DataFrame()
    for i, row_poi in poidata.iterrows():
        flag = False #flag表示POI INFO是否存在在原始数据中， True:存在
        if type == 'gd':
            (x, y) = (float(row_poi['gd_point_x']), float(row_poi['gd_point_y']))
            lon0, lat0 = Gcj2Wgs_SimpleIteration(x, y)
            row_poi['point_x'], row_poi['point_y'] = lon0, lat0
            row_poi['specify'] = row_poi['region']
            loc_poi = (lon0, lat0)
        elif type == 'tdt':
            loc_poi = (float(row_poi['point_x']), float(row_poi['point_y']))
        for j, row_exi in existdata.iterrows():
            loc_exi = (float(row_exi['point_x']), float(row_exi['point_y']))
            distance = get_distance_byloc(loc_poi, loc_exi)
            if distance < 100:
                flag = True
                break
        if flag == False:
            existdata = existdata.append(row_poi[['name', 'address', 'point_x', 'point_y','specify', 'dataType']], ignore_index=True)
            extra_info = extra_info.append(row_poi[['name', 'address', 'point_x', 'point_y','specify', 'dataType']], ignore_index=True)
    return extra_info

def add_allextrainfo_bypoi(data):
    all_extra_info = pd.DataFrame()
    # tdtpoiinfo = tianditu_api(tianditukey).getallpoiinfo()
    # gdpoiinfo = gaode_api(gaodekey).getallpoiinfo()
    # bdpoiinfo = baidu_api(baidukey).getallpoiinfo()
    bdpoiinfo = pd.read_csv('../../data/info/baidupoi_info.csv', encoding='gbk')
    tdtpoiinfo = pd.read_csv('../../data/info/tianditu_schoolinfo.csv', encoding='gbk')
    gdpoiinfo = pd.read_csv('../../data/info/gaode_schoolinfo.csv', encoding='gbk')

    for specify in specifys:
        exist = data.groupby(['specify']).get_group(specify)
        tdtpoi = tdtpoiinfo.groupby(['specify']).get_group(specify)
        gdpoi = gdpoiinfo.groupby(['region']).get_group(specify)
        bdpoi = bdpoiinfo.groupby(['region']).get_group(specify)
        extratdt = add_extrainfo_bypoi(tdtpoi, exist)
        extratdt['tag'] = 'tdt'
        print('STEP1:天地图POI在{}检测到{}个新增学校'.format(specify, len(extratdt)))
        all_extra_info = all_extra_info.append(extratdt, ignore_index=True)
        
        exist = exist.append(extratdt, ignore_index=True)

        extragd = add_extrainfo_bypoi(gdpoi, exist, type='gd')
        extragd['tag'] = 'gd'
        print('STEP2:高德POI在{}检测到{}个新增学校'.format(specify, len(extragd)))
        all_extra_info = all_extra_info.append(extragd, ignore_index=True)
        exist = exist.append(extragd, ignore_index=True)

        extrabd = add_extrainfo_bypoi(bdpoi, exist, type='gd')
        extrabd['tag'] = 'bd'
        print('STEP3:百度POI在{}检测到{}个新增学校'.format(specify, len(extrabd)))
        all_extra_info = all_extra_info.append(extrabd, ignore_index=True)
        exist = exist.append(extrabd, ignore_index=True)

    print('检测结束--共检测到新增学校{}个'.format(len(all_extra_info)))
    return all_extra_info
