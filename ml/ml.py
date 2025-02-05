import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression  # 用于线性回归 
from sklearn.model_selection import train_test_split

df = pd.read_csv('pm25_train.csv', engine='python')


def data_format(dt):
    time_list = []
    t = time.strptime(dt, '%Y-%m-%d')
    time_list.append(t.tm_year)
    time_list.append(t.tm_mon)
    time_list.append(t.tm_mday)
    time_list.append(t.tm_wday)
    return time_list

date = df['date'].tolist()
jieguo = []
for dt in date:
    jieguo.append(data_format(dt=dt))

df_time = pd.DataFrame(jieguo)
df_time.columns = ['year', 'mon', 'day', 'week']
df_data = pd.concat([df, df_time], axis=1)


y = df_data['pm2.5']
X = df_data.drop(columns=['pm2.5', 'date'])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
lr = LinearRegression().fit(X_train, y_train)

yuce = lr.predict(X_test)
df_jieguo = pd.DataFrame(y_test)
df_jieguo = df_jieguo.reset_index()
df_jieguo['yuce'] = yuce
df_jieguo['wucha'] = pow((df_jieguo['yuce'] - df_jieguo['pm2.5']), 2)
he = sum(df_jieguo['wucha'])
score = he / len(df_jieguo)
print(score)