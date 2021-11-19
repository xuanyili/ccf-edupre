import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from autoARIMA import autoARIMA
from polynomial import polynomial
from panet import panet
from lgb import lgbm

# def count_region(df_data):
#     df_data['region'] = df_data['dsmc'] + df_data['qxmc']
#     return df_data['region'].value_counts()

# def count_type(df_data):
#     return df_data['dj'].value_counts()

# def count_grade(df_data):
#     return df_data['xxlb'].value_counts()

def plot(x, y1, y2, path):
    if len(y2) > len(y1):
        x = x + x + [x[-1] + i for i in range(1, len(y2) - len(y1) + 1)]
    else:
        x = x + [x[-1] + i for i in range(1, len(y2) + 1)]
    y = y1 + y2
    c = ['True'] * len(y1) + ['Pred'] * len(y2)
    df_data = pd.DataFrame({'X':x, 'Y':y, 'Class': c}, columns=['X', 'Y', 'Class'])
    sns.lineplot(data=df_data, x='X', y='Y', hue="Class")

    plt.savefig(path, dpi=400)
    plt.close()

def tocsv(x, y1, y2, path):
    if len(y2) > len(y1):
        x = x + x + [x[-1] + i for i in range(1, len(y2) - len(y1) + 1)]
    else:
        x = x + [x[-1] + i for i in range(1, len(y2) + 1)]
    y = y1 + y2
    c = ['True'] * len(y1) + ['Pred'] * len(y2)
    df_data = pd.DataFrame({'X':x, 'Y':y, 'Class': c}, columns=['X', 'Y', 'Class'])
    df_data.to_csv(path)

def predict_xs(submodel, pop_data, x, ys, predict_range, add_x=True):
    
    X_test = {}
    for y in ys:
        if submodel == 'arima':
            res, res_  = autoARIMA(pop_data, x, y, predict_range)
        elif submodel == 'poly':
            res, res_ = polynomial(pop_data, x, y, predict_range)
        elif submodel == 'panet':
            res, res_ = panet(pop_data, x, y, predict_range)
        X_test[y] = res
    
    col_xs = ys
    if add_x:
        X_test[x] = [pop_data[x].to_list()[-1] + i for i in range(1, predict_range + 1)]
        col_xs.append(x)

    df_test = pd.DataFrame(X_test, columns=col_xs)
    df_test.to_csv('.temp_test.csv', header=False, index=False)
    df_test = pd.read_csv('.temp_test.csv', header=None)
    return df_test

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='arima',
            help='model name, must be arima, poly, panet, lgbm')
    parser.add_argument('--submodel', default='arima',
            help='submodel name, must be arima, poly, panet')
    parser.add_argument('--predict_range', type=int,default='6',
            help='predict range')
    opt = parser.parse_args()
    edu_data = pd.read_csv('../data/schoolinfo.csv', encoding='gbk')
    print('Model:' + opt.model + ' SubModel:' + opt.submodel)
    sns.set_theme(style="whitegrid")

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
    
    if opt.model == 'lgbm':
        df_test = predict_xs(opt.submodel, pop_data, '年份', ['人均余额','总人口数(万人)','常驻人口数(万人)'], opt.predict_range)
    
    predict_value = ['幼儿园数', '小学数', '中学数']

    for i in range(len(predict_value)):
        if opt.model != 'lgbm':
            figure_name = opt.model + '_' + predict_value[i]
        else:
            figure_name = opt.model + '_' + opt.submodel + '_' + predict_value[i]
        if opt.model == 'arima':
            res, res_ = autoARIMA(pop_data, '年份', predict_value[i], opt.predict_range)
        elif opt.model == 'poly':
            res, res_ = polynomial(pop_data, '年份', predict_value[i], opt.predict_range)
        elif opt.model == 'panet':
            res, res_ = panet(pop_data, '年份', predict_value[i], opt.predict_range)
        elif opt.model == 'lgbm':
            col_xs = ['年份','人均余额','总人口数(万人)','常驻人口数(万人)']
            res, res_ = lgbm(pop_data, col_xs, predict_value[i], df_test)
        else:
            print('Wrong model type')
            exit

        for e in edu_region:
            print('未来五年' + e + '的' + edu_type[i] + '学校数发展趋势为：')
            format_str = ''
            for r in res[:-1]:
                format_str += str(int(ratio[e][edu_type[i]] * r)) + ', '
            format_str += str(int(ratio[e][edu_type[i]] * res[-1]))
            print(format_str)

        plot(pop_data['年份'].to_list(), pop_data[predict_value[i]].to_list(),  res_ + res if not res_ == None else res, '../data/figure/' + figure_name + '.png')
        tocsv(pop_data['年份'].to_list(), pop_data[predict_value[i]].to_list(),  res_ + res if not res_ == None else res, '../data/table/' + figure_name + '.csv')
    predict_value = ['幼儿园平均人数', '小学平均人数', '中学平均人数']

    for p in predict_value:
        if opt.model != 'lgbm':
            figure_name = opt.model + '_' + p
        else:
            figure_name = opt.model + '_' + opt.submodel + '_' + p
        if opt.model == 'arima':
            res, res_ = autoARIMA(pop_data, '年份', p, opt.predict_range)
        elif opt.model == 'poly':
            res, res_ = polynomial(pop_data, '年份', p, opt.predict_range)
        elif opt.model == 'panet':
            res, res_ = panet(pop_data, '年份', p, opt.predict_range)
        elif opt.model == 'lgbm':
            col_xs = ['年份','人均余额','总人口数(万人)','常驻人口数(万人)']
            res, res_ = lgbm(pop_data, col_xs, p, df_test)
        else:
            print('Wrong model type')
            exit
        plot(pop_data['年份'].to_list(), pop_data[predict_value[i]].to_list(),  res_ + res if not res_ == None else res, '../data/figure/' + figure_name + '.png')
        tocsv(pop_data['年份'].to_list(), pop_data[predict_value[i]].to_list(),  res_ + res if not res_ == None else res, '../data/table/' + figure_name + '.csv')

        print('未来五年' + p + '的发展趋势为：')
        format_str = ''
        for r in res[:-1]:
            format_str += str(int(r)) + ', '
        format_str += str(int(res[-1]))
        print(format_str)