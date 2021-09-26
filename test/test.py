import requests
import json
import sys
sys.path.append(sys.path[0]+"/..")
from data_process import DataProcess
from txt2poi import gaode_api, tianditu_api
import pandas as pd

key = '6977ecc8c25093a80583a1cb5b2e6155'
tianditukey = '2423a38b3af5569af8aa521babc5e349'

tianditu = tianditu_api(tianditukey)

info = tianditu.getallcorrect_gaodepoiinfo(key)
gaode_unmatch_t = tianditu.get_unmatch_info_t()
gaode_unmatch_g = tianditu.get_unmatch_info_g()
info.to_csv("../data/info/matched_gdpoi_point.csv", encoding='gbk')
gaode_unmatch_t.to_csv("../data/info/gaode_unmatch_t.csv", encoding='gbk')
gaode_unmatch_g.to_csv("../data/info/gaode_unmatch_g.csv", encoding='gbk')