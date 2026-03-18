import pandas as pd


def read_epw_data(file_path):
    # 1. 读取 EPW 数据区
    # EPW 的第9行开始才是数据，所以跳过前8行
    # 第6列(索引为6)是干球温度 Dry Bulb Temperature
    # 第13列(索引为13)是水平面总辐射 Global Horizontal Radiation
    raw_data = pd.read_csv("/Users/zhangleyi/Desktop/Mumbai.epw", skiprows=8, header=None)

    # 2. 提取关键列：年(0), 月(1), 日(2), 时(3), 温度(6), 辐射(13)
    # 注意：EPW的温度是以摄氏度为单位，辐射是 Wh/m2
    df = raw_data[[0, 1, 2, 3, 6, 13]].copy()
    df.columns = ['Year', 'Month', 'Day', 'Hour', 'Temp_Ambient', 'Solar_Rad']

    # 3. 构造 8760 小时的时间索引
    # 注意：EPW的小时是从1-24，Python习惯是0-23，这里合并时需要统一
    df['timestamp'] = pd.to_datetime(df[['Year', 'Month', 'Day']].assign(Hour=df['Hour'] - 1))
    df.set_index('timestamp', inplace=True)

    return df

# 使用方法
df_annual = read_epw_data('india_mumbai.epw')
print(df_annual.head()) # 看看温度数据出来没