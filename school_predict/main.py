import pandas as pd
import argparse
from autoARIMA import autoARIMA
from polynomial import polynomial
from panet import panet
from lgb import lgbm

def count_region(df_data):
    df_data['region'] = df_data['dsmc'] + df_data['qxmc']
    return df_data['region'].value_counts()

def count_type(df_data):
    return df_data['dj'].value_counts()

def count_grade(df_data):
    return df_data['xxlb'].value_counts()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='arima',
            help='model name, must be arima, ploy, panet, lgb')
    opt = parser.parse_args()
    edu_data = pd.read_csv('../data/schoolinfo.csv', encoding='gbk')

    edu_type = ['学前教育', '初等教育', '中等教育']
    edu_region = ['义乌市', '余杭区', '海曙区', '西湖区', '德清县']

    pop_data = pd.read_excel('../data/经济人口信息.xlsx')
    cur_school_num = {}
    cur_school_num['学前教育'] = pop_data['幼儿园数'].values[-1]
    cur_school_num['初等教育'] = pop_data['小学数'].values[-1]
    cur_school_num['中等教育'] = pop_data['中学数'].values[-1]

    ratio = {}
    info = {}
    for r in edu_region:
        info[r] = {}
        ratio[r] = {}
        r_edu_data = edu_data[edu_data['qxmc'] == r]
        for t in edu_type:
            t_edu_data = r_edu_data[r_edu_data['dj'] == t]
            info[r][t] = len(t_edu_data)
            ratio[r][t] = len(t_edu_data) / cur_school_num[t]
    print('各区中不同类型学校数量:')
    for k in info.keys():
        print(k + '：' + str(info[k]))

    print('各区中不同类型学校占全省数量的比例:')
    for k in ratio.keys():
        print(k + '：' + str(ratio[k]))
    predict_value = ['幼儿园数', '小学数', '中学数']

    for i in range(len(predict_value)):
        if opt.model == 'arima':
            res = autoARIMA(pop_data, predict_value[i], 5)
        elif opt.model == 'ploy':
            res = polynomial(pop_data, '年份', predict_value[i], 5)
        elif opt.model == 'panet':
            res = panet(pop_data, '年份', predict_value[i], 5)
        else:
            col_xs = ['年份','人均余额','总人口数(万人)','常驻人口数(万人)']
            res = lgbm(pop_data, col_xs, predict_value[i], 5, '年份', autoARIMA)

        for e in edu_region:
            print('未来五年' + e + '的' + edu_type[i] + '学校数发展趋势为：')
            format_str = ''
            for r in res[:-1]:
                format_str += str(int(ratio[e][edu_type[i]] * r)) + ', '
            format_str += str(int(ratio[e][edu_type[i]] * res[-1]))
            print(format_str)
    
    predict_value = ['幼儿园平均人数', '小学平均人数', '中学平均人数']

    for p in predict_value:
        if opt.model == 'arima':
            res = autoARIMA(pop_data, p, 5)
        elif opt.model == 'ploy':
            res = polynomial(pop_data, '年份', predict_value[i], 5)
        elif opt.model == 'panet':
            res = panet(pop_data, '年份', predict_value[i], 5)
        else:
            col_xs = ['年份','人均余额','总人口数(万人)','常驻人口数(万人)']
            res = lgbm(pop_data, col_xs, predict_value[i], 5, '年份', autoARIMA)

        print('未来五年' + p + '的发展趋势为：')
        format_str = ''
        for r in res[:-1]:
            format_str += str(int(r)) + ', '
        format_str += str(int(res[-1]))
        print(format_str)