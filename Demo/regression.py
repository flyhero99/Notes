import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import Imputer
from sklearn.metrics import mean_squared_error

data = ts.get_hist_data('sh') # 从tushare接口获取数据
data.dropna(axis=0, subset=['close'], inplace=True) # 因为要预测的就是收盘价格close
# data_norm = (data - data.mean()) / (data.std()) # 数据归一化
# data = data_norm
# print(data_norm)

y = data.close # label
X = data.drop(['close'], axis=1).select_dtypes(exclude=['object']) # 特征
train_X, test_X, train_y, test_y = train_test_split(X.as_matrix(), y.as_matrix(), test_size=0.05)

my_imputer = Imputer()
train_X = my_imputer.fit_transform(train_X)
test_X = my_imputer.transform(test_X)

# 模型
my_model = XGBRegressor(
    colsample_bytree=0.4603,
    gamma=0.0468,
    learning_rate=0.05,
    max_depth=3,
    min_child_weight=1.7817,
    n_estimators=2200,
    reg_alpha=0.4640,
    reg_lambda=0.8571,
    subsample=0.5213,
    silent=1,
    random_state=7,
    nthread=-1
)

my_model.fit(train_X, train_y, verbose=False) # 训练
my_model.save_model('./regression.model') # 保存模型

# 预测模型
predictions = my_model.predict(test_X)
# 计算均方误差MSE
print("Mean Squared Error : " + str(mean_squared_error(predictions, test_y)))

# Matplotlib画图
x = range(0, 31)

plt.title('real(b) vs prediction(r)')
plt.xlabel('date')
plt.ylabel('$')

plt.plot(x, predictions, color='r', label='prediction')
plt.plot(x, test_y, color='b', label='real')
plt.xticks(x, rotation=0)

plt.legend(bbox_to_anchor=[0.3, 1])
plt.grid()
plt.show()
