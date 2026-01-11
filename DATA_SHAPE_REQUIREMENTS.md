# MJOcast 数据形状要求

本文档详细说明了 MJOcast 工具包对观测数据和预报数据变量的形状要求。

## 观测数据（Observations）要求

### 必需变量

观测数据文件必须包含以下三个变量：

1. **OLR (Outgoing Longwave Radiation)**
   - 变量名：`olr`（如果使用 ERA5 数据）或用户自定义名称
   - 单位：W/m²

2. **U850 (Zonal Wind at 850mb)**
   - 变量名：`uwnd850`（如果使用 ERA5 数据）或用户自定义名称
   - 单位：m/s

3. **U200 (Zonal Wind at 200mb)**
   - 变量名：`uwnd200`（如果使用 ERA5 数据）或用户自定义名称
   - 单位：m/s

### 数据维度要求

**原始数据形状**：
- 维度：`(time, lat, lon)` 或 `(time, lon)`（如果已经做了纬度平均）
- `time`：时间维度，必须包含时间坐标
- `lat`：纬度维度，必须包含 15°S 到 15°N 的范围（工具会自动进行纬度平均）
- `lon`：经度维度，范围应为 **0° 到 360°**（如果数据是 -180° 到 180°，工具会自动转换）

**处理后的数据形状**：
- 工具会自动对 15°S-15°N 进行纬度平均
- 最终形状：`(time, lon)`
- 经度会被插值到预报数据的经度网格上

### 坐标要求

- **经度（longitude）**：
  - 支持范围：0°-360° 或 -180°-180°（工具会自动转换到 0°-360°）
  - 坐标名称：`lon` 或 `longitude`（工具会自动统一为 `lon`）

- **纬度（latitude）**：
  - 必须包含 15°S 到 15°N 的范围
  - 坐标名称：`lat` 或 `latitude`（工具会自动统一为 `lat`）
  - 方向：支持从南到北（-90° 到 90°）或从北到南（90° 到 -90°），工具会自动调整

- **时间（time）**：
  - 必须包含时间坐标
  - 支持 xarray 的时间处理功能

### 示例观测数据形状

```python
# 原始观测数据（3D）
olr: (time=1000, lat=30, lon=360)      # 包含 15°S-15°N 的纬度范围
uwnd850: (time=1000, lat=30, lon=360)
uwnd200: (time=1000, lat=30, lon=360)

# 处理后的观测数据（2D，已做纬度平均）
olr: (time=1000, lon=360)
uwnd850: (time=1000, lon=360)
uwnd200: (time=1000, lon=360)
```

## 预报数据（Forecasts）要求

### 必需变量

预报数据文件必须包含以下三个变量（变量名可在 YAML 配置文件中自定义）：

1. **OLR (Outgoing Longwave Radiation)**
   - 默认变量名：`rlut`（可在配置文件中修改为 `forecast_olr_name`）
   - 单位：W/m²

2. **U850 (Zonal Wind at 850mb)**
   - 默认变量名：`ua_850`（可在配置文件中修改为 `forecast_u850_name`）
   - 单位：m/s

3. **U200 (Zonal Wind at 200mb)**
   - 默认变量名：`ua_200`（可在配置文件中修改为 `forecast_u200_name`）
   - 单位：m/s

### 数据维度要求

**原始数据形状**：
- 维度顺序可以灵活：`(ensemble, time, lat, lon)`、`(time, ensemble, lat, lon)`、`(lat, lon, time, ensemble)` 等
- `ensemble`：集合成员维度（必须存在，即使只有一个成员）
- `time`：预报提前时间（lead time）维度，必须包含时间坐标
- `lat`：纬度维度，必须包含 15°S 到 15°N 的范围
- `lon`：经度维度

**处理后的数据形状**：
- 工具会自动对 15°S-15°N 进行纬度平均
- 最终形状：`(ensemble, time, lon)` 或 `(time, ensemble, lon)`
- 经度会被统一到 0°-360° 范围

### 坐标要求

- **经度（longitude）**：
  - 支持范围：0°-360° 或 -180°-180°（工具会自动转换到 0°-360°）
  - 坐标名称：`lon` 或 `longitude`（工具会自动统一为 `lon`）

- **纬度（latitude）**：
  - 必须包含 15°S 到 15°N 的范围
  - 坐标名称：`lat` 或 `latitude`（工具会自动统一为 `lat`）
  - 方向：支持从南到北或从北到南，工具会自动调整

- **时间（time）**：
  - 必须包含时间坐标
  - 必须支持 `time.dayofyear` 功能（用于计算日序）
  - 时间坐标表示预报的提前时间（lead time）

- **集合（ensemble）**：
  - 坐标名称：可在配置文件中自定义（`forecast_ensemble_dimension_name`）
  - 如果数据中没有集合维度，工具会自动添加一个单成员的集合维度

### 示例预报数据形状

```python
# 原始预报数据（4D，维度顺序可以不同）
rlut: (ensemble=10, time=46, lat=30, lon=360)      # 10个集合成员，46天预报
ua_850: (ensemble=10, time=46, lat=30, lon=360)
ua_200: (ensemble=10, time=46, lat=30, lon=360)

# 或者维度顺序不同也可以
rlut: (time=46, ensemble=10, lat=30, lon=360)

# 处理后的预报数据（3D，已做纬度平均）
rlut: (ensemble=10, time=46, lon=360)
ua_850: (ensemble=10, time=46, lon=360)
ua_200: (ensemble=10, time=46, lon=360)
```

## 重要注意事项

1. **纬度范围**：数据必须包含 15°S 到 15°N 的纬度范围，工具会自动进行纬度平均。

2. **经度范围**：工具会自动处理经度范围转换，但建议使用 0°-360° 范围。

3. **维度顺序**：预报数据的维度顺序可以灵活，工具会自动处理。

4. **集合维度**：预报数据必须包含集合维度（即使只有一个成员）。

5. **时间坐标**：预报数据的时间坐标必须支持 `time.dayofyear` 功能。

6. **文件名**：预报文件名必须包含初始化日期，工具会自动从文件名中提取日期。

## 文件名格式要求

### 观测数据文件名

**使用 ERA5 数据时**：
- 固定文件名：`ERA5_Meridional_Mean_Anomaly_Filtered120.nc`
- 位置：`{obs_data_loc}/ERA5_Meridional_Mean_Anomaly_Filtered120.nc`

**使用自定义观测数据时**：
- 文件名在 YAML 配置文件中通过 `usr_named_obs` 指定
- 可以是任意有效的文件名（建议使用 `.nc` 扩展名）
- 位置：`{obs_data_loc}/{usr_named_obs}`
- 示例：`alternative_name_of_obs.nc`、`my_observations.nc`

**其他相关观测文件**（如果使用）：
- 气候态文件：`ERA5_climo.nc`（位置：`{obs_data_loc}/ERA5_climo.nc`）
- 未滤波异常文件：`ERA5_Meridional_Mean_Anomaly.nc`（位置：`{obs_data_loc}/ERA5_Meridional_Mean_Anomaly.nc`）

### 预报数据文件名

**重要要求**：
1. **必须包含初始化日期**：文件名中必须包含预报的初始化日期
2. **只能有一个日期**：文件名中只能包含一个日期（初始化日期），不能有其他日期
3. **使用 glob 模式**：在 YAML 配置中使用 glob 通配符模式匹配多个文件

**支持的日期格式**：
工具支持以下日期格式（会自动识别并提取）：

| 格式示例 | 格式代码 | 说明 |
|---------|---------|------|
| `01Apr1999` | `%d%b%Y` | 日-月(英文缩写)-年（推荐格式） |
| `Apr-01-1999` | `%b-%d-%Y` | 月(英文缩写)-日-年 |
| `01-Apr-1999` | `%d-%b-%Y` | 日-月(英文缩写)-年 |
| `Apr_01_1999` | `%b_%d_%Y` | 月(英文缩写)_日_年 |
| `040199` | `%m%d%y` | 月日年（2位年份） |

**文件名示例**：
```
# 推荐格式（使用 %d%b%Y）
S2Shindcast_cesm2cam6vs_MJOvars_01Apr1999.nc
S2Shindcast_cesm2cam6vs_MJOvars_15Dec2008.nc
forecast_01Jan2020.nc

# 其他支持的格式
S2Shindcast_cesm2cam6vs_MJOvars_Apr-01-1999.nc
S2Shindcast_cesm2cam6vs_MJOvars_01-Apr-1999.nc
S2Shindcast_cesm2cam6vs_MJOvars_Apr_01_1999.nc
```

**YAML 配置示例**：
```yaml
user_defined_info:
    # 预报数据位置
    forecast_data_loc: /path/to/forecast/data/
    
    # 预报文件名模式（使用 glob 通配符）
    # * 匹配任意字符，用于匹配多个文件
    forecast_data_name_str: S2Shindcast_cesm2cam6vs_MJOvars_*.nc
    
    # 或者更具体的模式
    # forecast_data_name_str: forecast_*.nc
```

**输出文件名格式**：
工具生成的输出文件名格式为：
```
{output_files_loc}{output_files_string}_{初始化日期}.nc
```

示例：
- 配置：`output_files_string: /MJO_Forecast_Init`
- 初始化日期：`01Apr1999`
- 输出文件名：`/path/to/output/MJO_Forecast_Init_01Apr1999.nc`

**注意事项**：
1. 文件名中的日期会被自动提取并转换为 `%d%b%Y` 格式（例如：`01Apr1999`）
2. 如果文件名中没有日期或日期格式无法识别，工具会报错
3. 建议使用 `%d%b%Y` 格式（例如：`01Apr1999`），这是最清晰和推荐的格式
4. 月份缩写使用英文：Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec

## 数据预处理

工具会自动进行以下预处理：

1. **坐标统一**：将 `latitude/longitude` 统一为 `lat/lon`
2. **经度转换**：将 -180°-180° 转换为 0°-360°
3. **纬度方向**：确保纬度从南到北（-90° 到 90°）
4. **纬度平均**：对 15°S-15°N 进行纬度平均
5. **经度插值**：将观测数据插值到预报数据的经度网格上
6. **日期提取**：从预报文件名中自动提取初始化日期

## 配置文件设置

在 `settings.yaml` 文件中，可以自定义变量名称：

```yaml
user_defined_info:
    # 观测数据变量名（如果使用自定义观测数据）
    usr_named_obs: alternative_name_of_obs.nc
    
    # 预报数据变量名
    forecast_olr_name: rlut
    forecast_u200_name: ua_200
    forecast_u850_name: ua_850
    forecast_ensemble_dimension_name: ensemble
```

## 参考代码位置

- 观测数据处理：`MJOcast/utils/ProcessOBS.py`
- 预报数据处理：`MJOcast/utils/ProcessForecasts.py`
- 工具函数：`MJOcast/utils/WHtools.py`

