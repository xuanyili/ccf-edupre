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

    pop_data = pd.read_excel('../data/??????????????????.xlsx')
    if not opt.eval:
        edu_data = pd.read_csv('../data/schoolinfo.csv', encoding='gbk')
        edu_type = ['????????????', '????????????', '????????????']
        edu_region = ['?????????', '?????????', '?????????', '?????????', '?????????']
        cur_school_num = {}
        cur_school_num['????????????'] = pop_data['????????????'].values[-1]
        cur_school_num['????????????'] = pop_data['?????????'].values[-1]
        cur_school_num['????????????'] = pop_data['?????????'].values[-1]

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
        print('?????????????????????????????????:')
        for k in info.keys():
            print(k + '???' + str(info[k]))

        print('???????????????????????????????????????????????????:')
        for k in ratio.keys():
            print(k + '???' + str(ratio[k]))
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
                df_test = predict_xs(submodel, pop_data, '??????', ['????????????','????????????(??????)','???????????????(??????)', '?????????????????????', '??????????????????', '??????????????????'], opt.predict_range)
            elif model != submodel:
                continue
            if opt.eval:
                print("== Start to eval", model, submodel if model == 'lgbm' else '')
            predict_value = ['????????????', '?????????', '?????????']
            for i in range(len(predict_value)):
                if model != 'lgbm':
                    figure_name = model + '_' + predict_value[i]
                else:
                    figure_name = model + '_' + submodel + '_' + predict_value[i]
                if model == 'arima':
                    res, res_ = autoARIMA(pop_data, '??????', predict_value[i], opt.predict_range)
                elif model == 'poly':
                    res, res_ = polynomial(pop_data, '??????', predict_value[i], opt.predict_range)
                elif model == 'panet':
                    res, res_ = panet(pop_data, '??????', predict_value[i], opt.predict_range)
                elif model == 'lgbm':
                    col_xs = ['??????','????????????','????????????(??????)','???????????????(??????)']
                    res, res_ = lgbm(pop_data, col_xs, predict_value[i], df_test)
                else:
                    print('Wrong model type')
                    exit
                if not opt.eval:
                    for e in edu_region:
                        print('????????????' + e + '???' + edu_type[i] + '???????????????????????????')
                        format_str = ''
                        for r in res[:-1]:
                            format_str += str(int(ratio[e][edu_type[i]] * r)) + ', '
                        format_str += str(int(ratio[e][edu_type[i]] * res[-1]))
                        print(format_str)

                    plot(pop_data['??????'].to_list(), pop_data[predict_value[i]].to_list(),  res_ + res if not res_ == None else res, '../data/figure/' + figure_name + '.png')
                    tocsv(pop_data['??????'].to_list(), pop_data[predict_value[i]].to_list(),  res_ + res if not res_ == None else res, '../data/table/' + figure_name + '.csv')
                else:
                    all_models1.append(model if model != 'lgbm' else model + '_' + submodel)
                    all_classes1.append(predict_value[i])
                    all_losses1.append(mean_squared_error(pop_eval_data[predict_value[i]].to_list(), res))

            predict_value = ['?????????????????????', '??????????????????', '??????????????????']
            for p in predict_value:
                if model != 'lgbm':
                    figure_name = model + '_' + p
                else:
                    figure_name = model + '_' + submodel + '_' + p
                if model == 'arima':
                    res, res_ = autoARIMA(pop_data, '??????', p, opt.predict_range)
                elif model == 'poly':
                    res, res_ = polynomial(pop_data, '??????', p, opt.predict_range)
                elif model == 'panet':
                    res, res_ = panet(pop_data, '??????', p, opt.predict_range)
                elif model == 'lgbm':
                    col_xs = ['??????','????????????','????????????(??????)','???????????????(??????)']
                    res, res_ = lgbm(pop_data, col_xs, p, df_test)
                else:
                    print('Wrong model type')
                    exit
                if not opt.eval:
                    plot(pop_data['??????'].to_list(), pop_data[p].to_list(),  res_ + res if not res_ == None else res, '../data/figure/' + figure_name + '.png')
                    tocsv(pop_data['??????'].to_list(), pop_data[p].to_list(),  res_ + res if not res_ == None else res, '../data/table/' + figure_name + '.csv')

                    print('????????????' + p + '?????????????????????')
                    format_str = ''
                    for r in res[:-1]:
                        format_str += str(int(r)) + ', '
                    format_str += str(int(res[-1]))
                    print(format_str)
                else:
                    all_models2.append(model if model != 'lgbm' else model + '_' + submodel[:2])
                    all_classes2.append(p)
                    all_losses2.append(mean_squared_error(pop_eval_data[p].to_list(), res))

            predict_value = ['???????????????????????????', '????????????????????????', '????????????????????????']
            for p in predict_value:
                if model != 'lgbm':
                    figure_name = model + '_' + p
                else:
                    figure_name = model + '_' + submodel + '_' + p
                if model == 'arima':
                    res, res_ = autoARIMA(pop_data, '??????', p, opt.predict_range)
                elif model == 'poly':
                    res, res_ = polynomial(pop_data, '??????', p, opt.predict_range)
                elif model == 'panet':
                    res, res_ = panet(pop_data, '??????', p, opt.predict_range)
                elif model == 'lgbm':
                    col_xs = ['??????','????????????','????????????(??????)','???????????????(??????)', '?????????????????????', '??????????????????', '??????????????????']
                    res, res_ = lgbm(pop_data, col_xs, p, df_test)
                else:
                    print('Wrong model type')
                    exit
                if not opt.eval:
                    plot(pop_data['??????'].to_list(), pop_data[p].to_list(),  res_ + res if not res_ == None else res, '../data/figure/' + figure_name + '.png')
                    tocsv(pop_data['??????'].to_list(), pop_data[p].to_list(),  res_ + res if not res_ == None else res, '../data/table/' + figure_name + '.csv')

                    print('????????????' + p + '?????????????????????')
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
        plot_mse(all_models1, all_classes1, all_losses1,  '../data/figure/MSE_????????????.png')
        plot_mse(all_models2, all_classes2, all_losses2, '../data/figure/MSE_????????????_??????.png')
        plot_mse(all_models3, all_classes3, all_losses3, '../data/figure/MSE_????????????_?????????.png')
        tocsv_mse(all_models1, all_classes1, all_losses1,  '../data/table/MSE_????????????.csv')
        tocsv_mse(all_models2, all_classes2, all_losses2, '../data/table/MSE_????????????_??????.csv')
        tocsv_mse(all_models3, all_classes3, all_losses3, '../data/table/MSE_????????????_?????????.csv')
        