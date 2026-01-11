"""
生成符合MJOcast工具包格式要求的虚假预报数据

用法:
    python generate_fake_forecast.py --start_date 2018-01-01 --end_date 2018-12-31 --output_dir ./forecast_data
"""

import numpy as np
import xarray as xr
import pandas as pd
import argparse
import os
from datetime import datetime, timedelta


def generate_fake_forecast_data(
    start_date="2018-01-01",
    end_date="2018-12-31",
    output_dir="./forecast_data",
    num_lead_days=46,
    num_ensembles=10,
    lon_resolution=1.0,
    lat_resolution=1.0,
    add_noise=True,
    seed=42
):
    """
    生成符合MJOcast格式要求的虚假预报数据
    
    参数:
        start_date (str): 开始日期（初始化日期范围开始），格式: "YYYY-MM-DD"
        end_date (str): 结束日期（初始化日期范围结束），格式: "YYYY-MM-DD"
        output_dir (str): 输出目录
        num_lead_days (int): 每个预报的提前天数（默认: 46）
        num_ensembles (int): 集合成员数（默认: 10）
        lon_resolution (float): 经度分辨率（度）
        lat_resolution (float): 纬度分辨率（度）
        add_noise (bool): 是否添加随机噪声使数据更真实
        seed (int): 随机种子
    """
    
    # 设置随机种子
    np.random.seed(seed)
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 解析日期范围
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    # 生成初始化日期列表（每天一个初始化）
    init_dates = pd.date_range(start=start, end=end, freq='D')
    
    print(f"生成预报数据")
    print(f"初始化日期范围: {start_date} 到 {end_date}")
    print(f"初始化次数: {len(init_dates)}")
    print(f"每个预报的提前天数: {num_lead_days}")
    print(f"集合成员数: {num_ensembles}")
    
    # 创建经纬度网格
    # 经度：0-359度（1度分辨率）
    lons = np.arange(0, 360, lon_resolution)
    
    # 纬度：-15到15度（包含15S-15N，工具会自动平均）
    lats = np.arange(-20, 21, lat_resolution)  # -20到20度
    
    print(f"经度范围: {lons.min()}° 到 {lons.max()}° (分辨率: {lon_resolution}°)")
    print(f"纬度范围: {lats.min()}° 到 {lats.max()}° (分辨率: {lat_resolution}°)")
    
    # 为每个初始化日期生成一个文件
    for init_idx, init_date in enumerate(init_dates):
        print(f"\n处理初始化日期 {init_idx+1}/{len(init_dates)}: {init_date.strftime('%Y-%m-%d')}")
        
        # 生成预报时间序列（从初始化日期开始的num_lead_days天）
        forecast_times = pd.date_range(
            start=init_date,
            periods=num_lead_days,
            freq='D'
        )
        
        # 生成4D数据 (ensemble, time, lat, lon)
        rlut_data = np.zeros((num_ensembles, num_lead_days, len(lats), len(lons)))
        ua_850_data = np.zeros((num_ensembles, num_lead_days, len(lats), len(lons)))
        ua_200_data = np.zeros((num_ensembles, num_lead_days, len(lats), len(lons)))
        
        # 基础信号（MJO-like pattern）
        mjo_period = 45  # MJO周期约45天
        
        for ens in range(num_ensembles):
            # 每个集合成员有略微不同的相位（模拟集合差异）
            ensemble_phase_offset = 2 * np.pi * ens / num_ensembles * 0.1
            
            for t_idx, forecast_time in enumerate(forecast_times):
                # 从初始化日期开始的天数
                lead_days = t_idx
                
                # 时间相关的相位
                time_phase = 2 * np.pi * lead_days / mjo_period + ensemble_phase_offset
                
                # 季节性相位
                day_of_year = forecast_time.dayofyear
                seasonal_phase = 2 * np.pi * day_of_year / 365.25
                
                for lat_idx, lat in enumerate(lats):
                    # 纬度权重（在赤道附近更强）
                    lat_weight = np.exp(-(lat/10)**2)
                    
                    for lon_idx, lon in enumerate(lons):
                        # 经度相位（MJO向东传播）
                        lon_phase = 2 * np.pi * lon / 360
                        
                        # 预报技能衰减（随着提前时间增加，信号减弱）
                        skill_decay = np.exp(-lead_days / 30.0)
                        
                        # OLR信号
                        olr_base = 240.0
                        olr_amplitude = 20.0 * lat_weight * skill_decay
                        rlut_data[ens, t_idx, lat_idx, lon_idx] = (
                            olr_base - olr_amplitude * np.sin(time_phase + lon_phase + seasonal_phase)
                        )
                        
                        # U850信号
                        u850_base = 0.0
                        u850_amplitude = 5.0 * lat_weight * skill_decay
                        ua_850_data[ens, t_idx, lat_idx, lon_idx] = (
                            u850_base + u850_amplitude * np.sin(time_phase + lon_phase + seasonal_phase)
                        )
                        
                        # U200信号
                        u200_base = 0.0
                        u200_amplitude = 8.0 * lat_weight * skill_decay
                        ua_200_data[ens, t_idx, lat_idx, lon_idx] = (
                            u200_base - u200_amplitude * np.sin(time_phase + lon_phase + seasonal_phase)
                        )
        
        # 添加随机噪声（集合成员之间的差异）
        if add_noise:
            # 集合成员之间的差异
            for ens in range(num_ensembles):
                ensemble_noise = np.random.normal(0, 2, (num_lead_days, len(lats), len(lons)))
                rlut_data[ens] += ensemble_noise
                ua_850_data[ens] += np.random.normal(0, 0.5, (num_lead_days, len(lats), len(lons)))
                ua_200_data[ens] += np.random.normal(0, 0.8, (num_lead_days, len(lats), len(lons)))
        
        # 创建xarray Dataset
        # 注意：维度顺序为 (ensemble, time, lat, lon)
        ds = xr.Dataset(
            {
                'rlut': (['ensemble', 'time', 'lat', 'lon'], rlut_data),
                'ua_850': (['ensemble', 'time', 'lat', 'lon'], ua_850_data),
                'ua_200': (['ensemble', 'time', 'lat', 'lon'], ua_200_data),
            },
            coords={
                'ensemble': np.arange(num_ensembles),
                'time': forecast_times,
                'lat': lats,
                'lon': lons,
            }
        )
        
        # 添加属性
        ds.attrs['title'] = 'Fake Forecast Data for MJOcast'
        ds.attrs['description'] = f'Generated fake forecast data initialized on {init_date.strftime("%Y-%m-%d")}'
        ds.attrs['initialization_date'] = init_date.strftime('%Y-%m-%d')
        ds.attrs['created'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ds.attrs['source'] = 'generate_fake_forecast.py'
        
        ds.rlut.attrs['long_name'] = 'Outgoing Longwave Radiation'
        ds.rlut.attrs['units'] = 'W/m^2'
        ds.rlut.attrs['standard_name'] = 'outgoing_longwave_radiation'
        
        ds.ua_850.attrs['long_name'] = 'Zonal Wind at 850 hPa'
        ds.ua_850.attrs['units'] = 'm/s'
        ds.ua_850.attrs['standard_name'] = 'eastward_wind'
        
        ds.ua_200.attrs['long_name'] = 'Zonal Wind at 200 hPa'
        ds.ua_200.attrs['units'] = 'm/s'
        ds.ua_200.attrs['standard_name'] = 'eastward_wind'
        
        ds.ensemble.attrs['long_name'] = 'Ensemble Member'
        ds.ensemble.attrs['description'] = 'Ensemble member index'
        
        ds.lat.attrs['long_name'] = 'Latitude'
        ds.lat.attrs['units'] = 'degrees_north'
        ds.lat.attrs['standard_name'] = 'latitude'
        
        ds.lon.attrs['long_name'] = 'Longitude'
        ds.lon.attrs['units'] = 'degrees_east'
        ds.lon.attrs['standard_name'] = 'longitude'
        
        # 生成文件名（必须包含初始化日期）
        # 使用推荐的格式: %d%b%Y (例如: 01Apr2018)
        date_str = init_date.strftime('%d%b%Y')
        filename = f'Fake_S2Shindcast_{date_str}.nc'
        output_path = os.path.join(output_dir, filename)
        
        # 保存文件
        ds.to_netcdf(output_path)
        print(f"  ✓ 保存: {filename}")
    
    print(f"\n✓ 成功生成 {len(init_dates)} 个预报文件!")
    print(f"  输出目录: {output_dir}")
    print(f"  文件名格式: Fake_S2Shindcast_<日期>.nc")
    print(f"  日期格式: %d%b%Y (例如: 01Apr2018)")


def main():
    parser = argparse.ArgumentParser(
        description='生成符合MJOcast格式要求的虚假预报数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成2018年全年的预报数据（每天一个初始化）
  python generate_fake_forecast.py --start_date 2018-01-01 --end_date 2018-12-31
  
  # 生成单个月的数据，10个集合成员，60天预报
  python generate_fake_forecast.py --start_date 2018-04-01 --end_date 2018-04-30 \\
      --num_ensembles 10 --num_lead_days 60
        """
    )
    
    parser.add_argument(
        '--start_date',
        type=str,
        default='2018-01-01',
        help='开始日期（初始化日期范围开始）(格式: YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--end_date',
        type=str,
        default='2020-12-31',
        help='结束日期（初始化日期范围结束）(格式: YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--output_dir',
        type=str,
        default='./data/forecast',
        help='输出目录 (默认: ./forecast_data)'
    )
    
    parser.add_argument(
        '--num_lead_days',
        type=int,
        default=3,
        help='每个预报的提前天数 (默认: 46)'
    )
    
    parser.add_argument(
        '--num_ensembles',
        type=int,
        default=1,
        help='集合成员数 (默认: 10)'
    )
    
    parser.add_argument(
        '--lon_resolution',
        type=float,
        default=5.0,
        help='经度分辨率（度）(默认: 1.0)'
    )
    
    parser.add_argument(
        '--lat_resolution',
        type=float,
        default=5.0,
        help='纬度分辨率（度）(默认: 1.0)'
    )
    
    parser.add_argument(
        '--no_noise',
        action='store_true',
        help='不添加随机噪声'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='随机种子 (默认: 42)'
    )
    
    args = parser.parse_args()
    
    # 生成数据
    generate_fake_forecast_data(
        start_date=args.start_date,
        end_date=args.end_date,
        output_dir=args.output_dir,
        num_lead_days=args.num_lead_days,
        num_ensembles=args.num_ensembles,
        lon_resolution=args.lon_resolution,
        lat_resolution=args.lat_resolution,
        add_noise=not args.no_noise,
        seed=args.seed
    )


if __name__ == '__main__':
    main()

