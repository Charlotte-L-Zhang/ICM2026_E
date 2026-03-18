import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 设置绘图风格，论文专用高大上风格
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")


class StochasticClimateGenerator:
    def __init__(self, location_name, base_temp, temp_range, base_noise=2.0):
        """
        初始化气候生成器
        :param location_name: 地点名称 (e.g., "Nanjing")
        :param base_temp: 年平均气温 (e.g., 16.0 for Nanjing)
        :param temp_range: 年温差幅度 (e.g., 25.0 means -5 to 35 roughly)
        :param base_noise: 基础天气的随机波动 (每日波动标准差)
        """
        self.location = location_name
        self.base_temp = base_temp
        self.temp_range = temp_range
        self.base_noise = base_noise

    def generate_year(self, year_offset, scenario='normal'):
        """
        生成一整年的每小时数据
        :param year_offset: 距离现在的年份 (0=现在, 50=50年后)
        :param scenario: 'normal' (历史), 'extreme' (未来极端)
        :return: DataFrame
        """
        hours = 8760
        t = np.arange(hours)

        # === 1. 基础物理波动 (Seasonal Sine Wave) ===
        # 模拟一年四季的温度正弦曲线
        # Nanjing Peak in July (approx hour 4000-5000)
        seasonal_cycle = -np.cos(2 * np.pi * t / hours) * (self.temp_range / 2)

        # === 2. 昼夜温差 (Diurnal Cycle) ===
        daily_cycle = -np.cos(2 * np.pi * t / 24) * 5  # 每天温差约 10度

        # === 3. 气候变化趋势 (Climate Change Trend) ===
        # 假设未来 50 年平均升温 2-4 度
        warming_rate = 0.06 if scenario == 'extreme' else 0.0
        global_warming_bias = year_offset * warming_rate

        # === 4. 极端事件注入 (The "Chaos" Factor) ===
        # 随着年份增加，波动率变大 (方差膨胀)
        instability_factor = (1 + 0.02 * year_offset) if scenario == 'extreme' else 1.0
        random_noise = np.random.normal(0, self.base_noise * instability_factor, hours)

        # 合成基础温度
        T_out = self.base_temp + seasonal_cycle + daily_cycle + global_warming_bias + random_noise

        # === 5. 制造“热浪”与“寒潮” (Heatwaves & Cold Snaps) ===
        heatwave_flag = np.zeros(hours)
        cold_snap_flag = np.zeros(hours)

        if scenario == 'extreme':
            # 热浪：概率随年份增加。每次持续 3-7 天 (72-168小时)
            # 逻辑：在夏季 (3000-6000小时) 随机触发
            num_heatwaves = int(2 + year_offset / 10)  # 50年后每年增加5次热浪
            for _ in range(num_heatwaves):
                start = np.random.randint(3500, 6000)
                duration = np.random.randint(72, 168)
                intensity = np.random.uniform(3, 8)  # 突然升温 3-8 度
                T_out[start:start + duration] += intensity
                heatwave_flag[start:start + duration] = 1

            # 寒潮：概率较低，但强度大 (极地涡旋崩溃)
            num_coldsnaps = int(1 + year_offset / 15)
            for _ in range(num_coldsnaps):
                start = np.random.randint(0, 2000)  # 冬季
                duration = np.random.randint(48, 120)
                intensity = np.random.uniform(5, 12)  # 突然降温 5-12 度
                T_out[start:start + duration] -= intensity
                cold_snap_flag[start:start + duration] = 1

        # === 6. 生成风速与降水 (Wind & Precip) ===
        # 基础风速
        wind_speed = np.random.weibull(2, hours) * 3

        # 极端风暴 (Storms)
        if scenario == 'extreme':
            # 增加暴风雨概率
            storm_prob = 0.005 * (1 + year_offset / 20)
            storm_indices = np.random.rand(hours) < storm_prob
            wind_speed[storm_indices] *= np.random.uniform(2.5, 4.0)  # 风速翻倍

        # 构造 DataFrame
        df = pd.DataFrame({
            'Hour': t,
            'T_out': T_out,
            'Wind_Speed': wind_speed,
            'Is_Heatwave': heatwave_flag,
            'Year_Offset': year_offset,
            'Scenario': scenario
        })
        return df


# === 运行模拟 ===

# 设定南京的参数 (假设)
nanjing_gen = StochasticClimateGenerator("Nanjing", base_temp=16, temp_range=28)

# 1. 生成“当前”气候 (Baseline)
df_now = nanjing_gen.generate_year(year_offset=0, scenario='normal')

# 2. 生成“2050年极端”气候 (Future Extreme)
df_future = nanjing_gen.generate_year(year_offset=30, scenario='extreme')

# === 绘图：这就是你要放在论文里的图 ===
plt.figure(figsize=(12, 6))

# 画全年对比
plt.plot(df_now['T_out'], label='Current Climate (2024)', color='gray', alpha=0.5, linewidth=0.5)
plt.plot(df_future['T_out'], label='Predicted Extreme Climate (2054)', color='#FF0000', alpha=0.6, linewidth=0.5)

# 标注热浪
heatwave_idx = df_future[df_future['Is_Heatwave'] == 1].index
plt.scatter(heatwave_idx, df_future.loc[heatwave_idx, 'T_out'], color='darkred', s=1, label='Extreme Heatwave Events')

plt.title(f"Stochastic Generation of Future Climate Extremes: Nanjing (2024 vs 2054)", fontsize=14, fontweight='bold')
plt.ylabel("Outdoor Temperature (°C)")
plt.xlabel("Hours of the Year")
plt.legend(loc='upper right')
plt.grid(True, alpha=0.3)

# 展示一段放大的“热浪”细节图 (Inset)
ax_inset = plt.axes([0.2, 0.2, 0.25, 0.25])
slice_range = slice(4500, 5000)  # 夏季某段
ax_inset.plot(df_now.iloc[slice_range]['T_out'].values, color='gray', alpha=0.8)
ax_inset.plot(df_future.iloc[slice_range]['T_out'].values, color='#FF7F50', linewidth=1.5)
ax_inset.set_title("Heatwave Detail (Zoom-in)", fontsize=9)
ax_inset.set_xticks([])

plt.show()

# 输出给你的微分方程用的数据
print("Max Temp Future:", df_future['T_out'].max())
print("Max Wind Future:", df_future['Wind_Speed'].max())
# df_future.to_csv("future_climate_nanjing.csv") # 存下来用