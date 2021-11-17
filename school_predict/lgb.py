import lightgbm as lgb
import pandas as pd
from sklearn.metrics import mean_squared_error


def lgbm(df_data, col_xs, col_y, predict_range, predict_col_x, model):
    # 加载或构造数据
    df_data = df_data

    df_train = df_data[[col_y] + col_xs]
    df_train.to_csv('.temp_train.csv', header=False, index=False)
    # df_test = df_data[[col_y] + col_xs][-4:]
    # df_test.to_csv('temp_test.csv', header=False, index=False)
    df_train = pd.read_csv('.temp_train.csv', header=None)
    # df_test = pd.read_csv('temp_test.csv', header=None)
    y_train = df_train[0]
    # y_test = df_test[0]
    X_train = df_train.drop(0, axis=1)
    # X_test = df_test.drop(0, axis=1)
    # 为lightgbm准备Dataset格式数据
    lgb_train = lgb.Dataset(X_train, y_train)
    # lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)
    X_test = {}
    for predict_col in col_xs:
        if predict_col != predict_col_x:
            res = model(df_data, predict_col_x, predict_col, predict_range)
            X_test[predict_col] = res
        else:
            X_test[predict_col] = [2020 + i for i in range(1, predict_range + 1)]
    df_test = pd.DataFrame(X_test, columns=col_xs)
    df_test.to_csv('.temp_test.csv', header=False, index=False)
    df_test = pd.read_csv('.temp_test.csv', header=None)
    X_test = df_test

    # 参数设置
    params = {
        'boosting_type': 'gbdt',
        'objective': 'regression',
        'metric': {'l2', 'l1'},
        'num_leaves': 4,
        'learning_rate': 0.05,
        'min_data_in_leaf': 2,
        'feature_fraction': 0.9,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': 0,
        'force_col_wise': True
    }

    print('Starting training...')
    # 模型训练
    gbm = lgb.train(params,
                    lgb_train,
                    num_boost_round=2000)
    # 模型预测
    y_pred = gbm.predict(X_test, num_iteration=gbm.best_iteration)
    return y_pred