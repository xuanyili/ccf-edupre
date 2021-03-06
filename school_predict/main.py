import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from autoARIMA import autoARIMA
from polynomial import polynomial
from panet import panet
from lgb import lgbm
from sklearn.metrics import mean_squared_error
# def count_region(df_data):
#     df_data['region'] = df_data['dsmc'] + df_data['qxmc']
#     return df_data['region'].value_counts()

# def count_type(df_data):
#     return df_data['dj'].value_counts()

# def count_grade(df_data):
#     return df_data['xxlb'].value_counts()

def plot_mse(m, c, l, path):
    plt.rcParams['font.sans-serif'] = ['simhei']
    df_data = pd.DataFrame({'model':m, 'class':c, 'MSE': l}, columns=['model', 'class', 'MSE'])
    sns.barplot(data=df_data, x='model', y='MSE', hue="class")

    plt.savefig(path, dpi=400)
    plt.close()

def tocsv_mse(m, c, l, path):
    df_data = pd.DataFrame({'model':m, 'class':c, 'MSE': l}, columns=['model', 'class', 'MSE'])
    df_data.to_csv(path)

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
    return df_test

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='arima',
            help='model name, must be arima, poly, panet, lgbm')
    parser.add_argument('--submodel', default='arima',
            help='submodel name, must be arima, poly, panet')
    parser.add_argument('--predict_range', type=int,default='6',
            help='predict range')
    parser.add_argument('--eval', default=False, action='store_true',
            help='eval')
    opt = parser.parse_args()
    plt.rcParams['font.sans-serif'] = ['simhei']
    sns.set_theme(style="whitegrid")

    pop_data = pd.read_excel('../data/经济人口信息.xlsx')
    if not opt.eval:
        edu_data = pd.read_csv('../data/schoolinfo.csv', encoding='gbk')
        edu_type = ['学前教育', '初等教育', '中等教育']
        edu_region = ['义乌市', '余杭区', '海曙区', '西湖区', '德清县']
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
    else:
        pop_data = pop_data[:-opt.predict_range]
        pop_eval_data = pop_data[-opt.predict_range:]
    if opt.eval:
        models = ['arima', 'poly', 'panet', 'lgbm']
        submodels = ['arima', 'poly', 'panet']
        all_models1 = []
        all_classes1 = []
        all_losses1 = []

        all_models2 = []
        all_classes2 = []
        all_losses2 = []

        all_models3 = []
        all_classes3 = []
        all_losses3 = []
    else:
        print('Model:' + opt.model + ' SubModel:' + opt.submodel)
        models = [opt.model]
        submodels = [opt.submodel if opt.model == 'lgbm' else opt.model]
    for model in models:
        for submodel in submodels:
            if model == 'lgbm':
                df_test = predict_xs(submodel, pop_data, '年份', ['人均余额','总人口数(万人)','常驻人口数(万人)', '幼儿园平均人数', '小学平均人数', '中学平均人数'], opt.predict_range)
            elif model != submodel:
                continue
            if opt.eval:
                print("== Start to eval", model, submodel if model == 'lgbm' else '')
            predict_value = ['幼儿园数', '小学数', '中学数']
            for i in range(len(predict_value)):
                if model != 'lgbm':
                    figure_name = model + '_' + predict_value[i]
                else:
                    figure_name = model + '_' + submodel + '_' + predict_value[i]
                if model == 'arima':
                    res, res_ = autoARIMA(pop_data, '年份', predict_value[i], opt.predict_range)
                elif model == 'poly':
                    res, res_ = polynomial(pop_data, '年份', predict_value[i], opt.predict_range)
                elif model == 'panet':
                    res, res_ = panet(pop_data, '年份', predict_value[i], opt.predict_range)
                elif model == 'lgbm':
                    col_xs = ['年份','人均余额','总人口数(万人)','常驻人口数(万人)']
                    res, res_ = lgbm(pop_data, col_xs, predict_value[i], df_test)
                else:
                    print('Wrong model type')
                    exit
                if not opt.eval:
                    for e in edu_region:
                        print('未来五年' + e + '的' + edu_type[i] + '学校数发展趋势为：')
                        format_str = ''
                        for r in res[:-1]:
                            format_str += str(int(ratio[e][edu_type[i]] * r)) + ', '
                        format_str += str(int(ratio[e][edu_type[i]] * res[-1]))
                        print(format_str)

                    plot(pop_data['年份'].to_list(), pop_data[predict_value[i]].to_list(),  res_ + res if not res_ == None else res, '../data/figure/' + figure_name + '.png')
                    tocsv(pop_data['年份'].to_list(), pop_data[predict_value[i]].to_list(),  res_ + res if not res_ == None else res, '../data/table/' + figure_name + '.csv')
                else:
                    all_models1.append(model if model != 'lgbm' else model + '_' + submodel)
                    all_classes1.append(predict_value[i])
                    all_losses1.append(mean_squared_error(pop_eval_data[predict_value[i]].to_list(), res))

            predict_value = ['幼儿园平均人数', '小学平均人数', '中学平均人数']
            for p in predict_value:
                if model != 'lgbm':
                    figure_name = model + '_' + p
                else:
                    figure_name = model + '_' + submodel + '_' + p
                if model == 'arima':
                    res, res_ = autoARIMA(pop_data, '年份', p, opt.predict_range)
                elif model == 'poly':
                    res, res_ = polynomial(pop_data, '年份', p, opt.predict_range)
                elif model == 'panet':
                    res, res_ = panet(pop_data, '年份', p, opt.predict_range)
                elif model == 'lgbm':
                    col_xs = ['年份','人均余额','总人口数(万人)','常驻人口数(万人)']
                    res, res_ = lgbm(pop_data, col_xs, p, df_test)
                else:
                    print('Wrong model type')
                    exit
                if not opt.eval:
                    plot(pop_data['年份'].to_list(), pop_data[p].to_list(),  res_ + res if not res_ == None else res, '../data/figure/' + figure_name + '.png')
                    tocsv(pop_data['年份'].to_list(), pop_data[p].to_list(),  res_ + res if not res_ == None else res, '../data/table/' + figure_name + '.csv')

                    print('未来五年' + p + '的发展趋势为：')
                    format_str = ''
                    for r in res[:-1]:
                        format_str += str(int(r)) + ', '
                    format_str += str(int(res[-1]))
                    print(format_str)
                else:
                    all_models2.append(model if model != 'lgbm' else model + '_' + submodel[:2])
                    all_classes2.append(p)
                    all_losses2.append(mean_squared_error(pop_eval_data[p].to_list(), res))

            predict_value = ['幼儿园平均教职工数', '小学平均教职工数', '中学平均教职工数']
            for p in predict_value:
                if model != 'lgbm':
                    figure_name = model + '_' + p
                else:
                    figure_name = model + '_' + submodel + '_' + p
                if model == 'arima':
                    res, res_ = autoARIMA(pop_data, '年份', p, opt.predict_range)
                elif model == 'poly':
                    res, res_ = polynomial(pop_data, '年份', p, opt.predict_range)
                elif model == 'panet':
                    res, res_ = panet(pop_data, '年份', p, opt.predict_range)
                elif model == 'lgbm':
                    col_xs = ['年份','人均余额','总人口数(万人)','常驻人口数(万人)', '幼儿园平均人数', '小学平均人数', '中学平均人数']
                    res, res_ = lgbm(pop_data, col_xs, p, df_test)
                else:
                    print('Wrong model type')
                    exit
                if not opt.eval:
                    plot(pop_data['年份'].to_list(), pop_data[p].to_list(),  res_ + res if not res_ == None else res, '../data/figure/' + figure_name + '.png')
                    tocsv(pop_data['年份'].to_list(), pop_data[p].to_list(),  res_ + res if not res_ == None else res, '../data/table/' + figure_name + '.csv')

                    print('未来五年' + p + '的发展趋势为：')
                    format_str = ''
                    for r in res[:-1]:
                        format_str += str(int(r)) + ', '
                    format_str += str(int(res[-1]))
                    print(format_str)
                else:
                    all_models3.append(model if model != 'lgbm' else model + '_' + submodel[:2])
                    all_classes3.append(p)
                    all_losses3.append(mean_squared_error(pop_eval_data[p].to_list(), res))
    if opt.eval:
        plot_mse(all_models1, all_classes1, all_losses1,  '../data/figure/MSE_学校数量.png')
        plot_mse(all_models2, all_classes2, all_losses2, '../data/figure/MSE_学校规模_学生.png')
        plot_mse(all_models3, all_classes3, all_losses3, '../data/figure/MSE_学校规模_教职工.png')
        tocsv_mse(all_models1, all_classes1, all_losses1,  '../data/table/MSE_学校数量.csv')
        tocsv_mse(all_models2, all_classes2, all_losses2, '../data/table/MSE_学校规模_学生.csv')
        tocsv_mse(all_models3, all_classes3, all_losses3, '../data/table/MSE_学校规模_教职工.csv')
        