# 虚假数据生成脚本使用说明

本目录包含两个脚本，用于生成符合MJOcast工具包格式要求的虚假观测数据和预报数据。

## 脚本说明

### 1. `generate_fake_obs.py` - 生成虚假观测数据

生成符合MJOcast格式要求的观测数据文件。

**输出文件格式**：
- 变量：`olr`, `uwnd850`, `uwnd200`
- 维度：`(time, lat, lon)`
- 经度：0-360度
- 纬度：-20到20度（包含15S-15N）

**使用方法**：
```bash
# 基本用法（生成2000-2020年的数据）
python generate_fake_obs.py --start_date 2000-01-01 --end_date 2020-12-31

# 使用自定义文件名
python generate_fake_obs.py --start_date 2000-01-01 --end_date 2020-12-31 \
    --output_filename my_obs_data.nc \
    --output_dir ./my_observations

# 不添加噪声
python generate_fake_obs.py --start_date 2000-01-01 --end_date 2020-12-31 --no_noise
```

**参数说明**：
- `--start_date`: 开始日期（格式: YYYY-MM-DD）
- `--end_date`: 结束日期（格式: YYYY-MM-DD）
- `--output_dir`: 输出目录（默认: ./Observations）
- `--output_filename`: 输出文件名（默认: ERA5_Meridional_Mean_Anomaly_Filtered120.nc）
- `--lon_resolution`: 经度分辨率（度，默认: 1.0）
- `--lat_resolution`: 纬度分辨率（度，默认: 1.0）
- `--no_noise`: 不添加随机噪声
- `--seed`: 随机种子（默认: 42）

### 2. `generate_fake_forecast.py` - 生成虚假预报数据

生成符合MJOcast格式要求的预报数据文件。每个初始化日期生成一个文件。

**输出文件格式**：
- 变量：`rlut` (OLR), `ua_850` (U850), `ua_200` (U200)
- 维度：`(ensemble, time, lat, lon)`
- 经度：0-360度
- 纬度：-20到20度（包含15S-15N）
- 文件名：`Fake_S2Shindcast_<日期>.nc`（日期格式：%d%b%Y，例如：01Apr2018）

**使用方法**：
```bash
# 基本用法（生成2018年全年的预报数据）
python generate_fake_forecast.py --start_date 2018-01-01 --end_date 2018-12-31

# 自定义集合成员数和预报天数
python generate_fake_forecast.py --start_date 2018-04-01 --end_date 2018-04-30 \
    --num_ensembles 10 \
    --num_lead_days 60 \
    --output_dir ./my_forecast_data

# 生成单个月的数据
python generate_fake_forecast.py --start_date 2018-04-01 --end_date 2018-04-30
```

**参数说明**：
- `--start_date`: 开始日期（初始化日期范围开始，格式: YYYY-MM-DD）
- `--end_date`: 结束日期（初始化日期范围结束，格式: YYYY-MM-DD）
- `--output_dir`: 输出目录（默认: ./forecast_data）
- `--num_lead_days`: 每个预报的提前天数（默认: 46）
- `--num_ensembles`: 集合成员数（默认: 10）
- `--lon_resolution`: 经度分辨率（度，默认: 1.0）
- `--lat_resolution`: 纬度分辨率（度，默认: 1.0）
- `--no_noise`: 不添加随机噪声
- `--seed`: 随机种子（默认: 42）

## 数据特征

### 观测数据特征

- **时间序列**：从开始日期到结束日期的每日数据
- **MJO信号**：包含模拟的MJO信号（约45天周期）
- **季节性变化**：包含季节性变化
- **空间模式**：MJO向东传播的空间模式
- **纬度权重**：在赤道附近信号更强

### 预报数据特征

- **初始化频率**：每天一个初始化
- **预报长度**：可配置的提前天数（默认46天）
- **集合成员**：可配置的集合成员数（默认10个）
- **技能衰减**：随着提前时间增加，预报技能逐渐衰减
- **集合差异**：不同集合成员之间有差异（模拟集合不确定性）

## 完整示例

### 生成测试数据集

```bash
# 1. 生成观测数据（2000-2020年）
python generate_fake_obs.py \
    --start_date 2000-01-01 \
    --end_date 2020-12-31 \
    --output_dir ./Observations

# 2. 生成预报数据（2018年4月，用于测试）
python generate_fake_forecast.py \
    --start_date 2018-04-01 \
    --end_date 2018-04-30 \
    --num_ensembles 10 \
    --num_lead_days 46 \
    --output_dir ./forecast_data
```

### 在MJOcast中使用

生成数据后，可以在`settings.yaml`中配置：

```yaml
user_defined_info:
    # 观测数据
    use_era5: false
    usr_named_obs: ERA5_Meridional_Mean_Anomaly_Filtered120.nc
    obs_data_loc: ./Observations/
    
    # 预报数据
    forecast_data_loc: ./forecast_data
    forecast_data_name_str: Fake_S2Shindcast_*.nc
    forecast_olr_name: rlut
    forecast_u200_name: ua_200
    forecast_u850_name: ua_850
    forecast_ensemble_dimension_name: ensemble
```

## 注意事项

1. **文件名格式**：预报文件名必须包含初始化日期，脚本会自动生成符合要求的文件名格式（`%d%b%Y`，例如：`01Apr2018`）

2. **数据质量**：这些是虚假数据，仅用于测试工具包功能，不应用于实际科学研究

3. **内存使用**：生成大量数据时可能占用较多内存，建议分批生成

4. **文件大小**：观测数据文件可能较大（取决于时间范围），预报数据文件相对较小（每个文件对应一个初始化日期）

5. **日期格式**：预报文件名中的日期使用英文月份缩写（Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec）

## 故障排除

### 问题：文件生成失败

- 检查输出目录是否存在写入权限
- 检查日期格式是否正确（YYYY-MM-DD）
- 检查是否有足够的磁盘空间

### 问题：数据维度不正确

- 确保使用最新版本的xarray和numpy
- 检查生成的NetCDF文件是否可以被xarray正确读取

### 问题：预报文件名格式错误

- 脚本会自动生成正确的文件名格式
- 如果使用自定义文件名，确保包含初始化日期（格式：`%d%b%Y`）

## 依赖包

确保安装以下Python包：
- numpy
- xarray
- pandas

安装命令：
```bash
pip install numpy xarray pandas
```

