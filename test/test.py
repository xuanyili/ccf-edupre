
import sys
sys.path.append(sys.path[0]+"/..")

import pandas as pd

from txt2poi import tianditu_api, gaode_api, check_correct_infobygetgdaddress, check_correct_bygaodepoi, get_distance_byloc, check_correct_origininfo, check_correct_bytianditupoi
from data_process import DataProcess

tianditukey = '2423a38b3af5569af8aa521babc5e349'
gaodekey = '6977ecc8c25093a80583a1cb5b2e6155'

process = DataProcess()
data = process.get_allschoolinfo()
correct_locinfo = pd.DataFrame()
uncorrect_locinfo = pd.DataFrame()

print("step1:天地图逆地址编码校验数据集坐标是否准确，原数据集{}个".format(len(data)))
correct1, uncorrect1, unsure1 = check_correct_origininfo(data)
correct1['judge_way'] = 'tdt'
uncorrect1['judge_way'] = 'tdt'
print("step1:天地图逆地址编码校验完成，正确坐标{}个，错误坐标{}个，未匹配坐标{}个"
.format(len(correct1), len(uncorrect1), len(unsure1)))
correct_locinfo = correct_locinfo.append(correct1, ignore_index=True)
uncorrect_locinfo = uncorrect_locinfo.append(uncorrect1, ignore_index=True)

tdtpoiinfo = tianditu_api(tianditukey).getallpoiinfo()
print("step2:获取天地图POI信息校验数据集坐标是否准确，待校验数据{}个".format(len(unsure1)))
correct2, uncorrect2, unsure2 = check_correct_bytianditupoi(unsure1, tdtpoiinfo)
correct2['judge_way'] = 'tdtpoi'
uncorrect2['judge_way'] = 'tdtpoi'
print("step2:获取天地图POI信息校验完成，正确坐标{}个，错误坐标{}个，未匹配坐标{}个"
.format(len(correct2), len(uncorrect2), len(unsure2)))
correct_locinfo = correct_locinfo.append(correct2, ignore_index=True)
uncorrect_locinfo = uncorrect_locinfo.append(uncorrect2, ignore_index=True)

print("step3:高德逆地址编码校验数据集坐标是否准确，待校验数据集{}个".format(len(unsure2)))
correct3, uncorrect3, unsure3 = check_correct_infobygetgdaddress(unsure2)
correct3['judge_way'] = 'gd'
uncorrect3['judge_way'] = 'gd'
print("step3:高德逆地址编码校验完成，正确坐标{}个，错误坐标{}个，未匹配坐标{}个"
.format(len(correct3), len(uncorrect3), len(unsure3)))
correct_locinfo = correct_locinfo.append(correct3, ignore_index=True)
uncorrect_locinfo = uncorrect_locinfo.append(uncorrect3, ignore_index=True)

gdpoiinfo = gaode_api(gaodekey).getallpoiinfo()
print("step4:获取高德POI信息校验数据集坐标是否准确，待校验数据{}个".format(len(unsure3)))
correct4, uncorrect4, unsure4 = check_correct_bygaodepoi(unsure3, gdpoiinfo)
correct4['judge_way'] = 'gdpoi'
uncorrect4['judge_way'] = 'gdpoi'
print("step4:获取高德POI信息校验完成，正确坐标{}个，错误坐标{}个，未匹配坐标{}个"
.format(len(correct4), len(uncorrect4), len(unsure4)))
correct_locinfo = correct_locinfo.append(correct4, ignore_index=True)
uncorrect_locinfo = uncorrect_locinfo.append(uncorrect4, ignore_index=True)

unsure4.to_csv('../data/verify_info/verify_unsure_info.csv', encoding='gbk')
correct_locinfo.to_csv('../data/verify_info/verify_correct_info.csv', encoding='gbk')
uncorrect_locinfo.to_csv('../data/verify_info/verify_uncorrect_info.csv', encoding='gbk')
print("验证结束，正确坐标{}个，错误坐标{}个，未匹配坐标{}个"
.format(len(correct_locinfo), len(uncorrect_locinfo), len(unsure4)))