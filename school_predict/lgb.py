import lightgbm as lgb
import pandas as pd

def lgbm(df_data, col_xs, col_y, df_test):
    # 加载或构造数据
    df_data = df_data

    df_train = df_data[[col_y] + col_xs]
    df_train.to_csv('.temp_train.csv', header=False, index=False)
    df_train = pd.read_csv('.temp_train.csv', header=None)
    y_train = df_train[0]
    X_train = df_train.drop(0, axis=1)
    # 为lightgbm准备Dataset格式数据
    lgb_train = lgb.Dataset(X_train, y_train)
    X_test = df_test

    # 参数设置
    params = {
        'boosting_type': 'gbdt',
        'objective': 'regression',
        'metric': {'l2', 'l1'},
        'num_leaves': 4,
        'learning_rate': 0.05,
        'min_data_in_leaf': 1,
        'feature_fraction': 0.9,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': 0,
        'force_col_wise': True
    }

    # 模型训练
    gbm = lgb.train(params,
                    lgb_train,
                    num_boost_round=2000)
    # 模型预测
    y_pred = gbm.predict(X_test, num_iteration=gbm.best_iteration)
    return y_pred