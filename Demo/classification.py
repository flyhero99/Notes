import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import Imputer
from xgboost import XGBClassifier
from sklearn.metrics import classification_report

data = ts.get_hist_data('sh') # 从tushare接口获取数据
data_norm = (data - data.mean()) / (data.std()) # 数据归一化
data = data_norm

# 在原有数据基础上增加一列，表示当日股价涨跌
data.eval('is_increase = open - close', inplace=True)
for index, row in data.iterrows():   # 获取每行的index、row
    if row['is_increase'] >= 0:
        row['is_increase'] = int(0)
    else:
        row['is_increase'] = int(1)
print(data)

data.dropna(axis=0, subset=['is_increase'], inplace=True)
date_label = data.index
y = data.is_increase
X = data.drop(['is_increase'], axis=1).select_dtypes(exclude=['object'])
train_X, test_X, train_y, test_y = train_test_split(X.as_matrix(), y.as_matrix(), test_size=0.05)

my_imputer = Imputer()
train_X = my_imputer.fit_transform(train_X)
test_X = my_imputer.transform(test_X)

# 模型，XGBoost分类起
my_model = XGBClassifier(
    silent=0,
    learning_rate= 0.3,
    min_child_weight=1,
    max_depth=6,
    gamma=0,
    subsample=1,
    max_delta_step=0,
    colsample_bytree=1,
    reg_lambda=1,
    n_estimators=100,
    seed=1000
)

# 训练
my_model.fit(train_X, train_y)
my_model.save_model('./classification.model')

# 预测模型
predictions = my_model.predict(test_X)

# 分类结果评估，包含了Accuracy, precision, recall 和 f1-score等
print("Classification Report: " + str(classification_report(predictions, test_y)))

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
