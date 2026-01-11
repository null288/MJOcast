"""
生成符合MJOcast工具包格式要求的虚假观测数据

用法:
    python generate_fake_obs.py --start_date 2000-01-01 --end_date 2020-12-31 --output_dir ./Observations
"""

import numpy as np
import xarray as xr
import pandas as pd
import argparse
import os
from datetime import datetime, timedelta


def generate_fake_obs_data(
    start_date="2000-01-01",
    end_date="2020-12-31",
    output_dir="./Observations",
    output_filename="ERA5_Meridional_Mean_Anomaly_Filtered120.nc",
    lon_resolution=1.0,
    lat_resolution=1.0,
    add_noise=True,
    seed=42
):
    """
    生成符合MJOcast格式要求的虚假观测数据
    
    参数:
        start_date (str): 开始日期，格式: "YYYY-MM-DD"
        end_date (str): 结束日期，格式: "YYYY-MM-DD"
        output_dir (str): 输出目录
        output_filename (str): 输出文件名
        lon_resolution (float): 经度分辨率（度）
        lat_resolution (float): 纬度分辨率（度）
        add_noise (bool): 是否添加随机噪声使数据更真实
        seed (int): 随机种子
    """
    
    # 设置随机种子
    np.random.seed(seed)
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 解析日期
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    # 生成时间序列（每天）
    time = pd.date_range(start=start, end=end, freq='D')
    ntime = len(time)
    
    print(f"生成时间范围: {start_date} 到 {end_date}")
    print(f"总天数: {ntime}")
    
    # 创建经纬度网格
    # 经度：0-359度（1度分辨率）
    lons = np.arange(0, 360, lon_resolution)
    
    # 纬度：-15到15度（包含15S-15N，工具会自动平均）
    # 为了更真实，我们生成稍大一点的纬度范围
    lats = np.arange(-20, 21, lat_resolution)  # -20到20度
    
    print(f"经度范围: {lons.min()}° 到 {lons.max()}° (分辨率: {lon_resolution}°)")
    print(f"纬度范围: {lats.min()}° 到 {lats.max()}° (分辨率: {lat_resolution}°)")
    
    # 生成虚假数据
    # 使用简单的正弦波模式模拟MJO信号
    print("生成虚假数据...")
    
    # 创建基础信号（MJO-like pattern）
    # 使用多个频率的正弦波组合
    t_days = np.arange(ntime)
    
    # MJO周期大约40-50天
    mjo_period = 45
    seasonal_period = 365.25
    
    # 经度方向的波数（MJO向东传播）
    lon_wavenumber = 1  # 全球一个波
    
    # 生成3D数据 (time, lat, lon)
    olr_data = np.zeros((ntime, len(lats), len(lons)))
    uwnd850_data = np.zeros((ntime, len(lats), len(lons)))
    uwnd200_data = np.zeros((ntime, len(lats), len(lons)))
    
    for i, t in enumerate(t_days):
        # 时间相关的相位
        time_phase = 2 * np.pi * t / mjo_period
        seasonal_phase = 2 * np.pi * t / seasonal_period
        
        for j, lat in enumerate(lats):
            # 纬度权重（在赤道附近更强）
            lat_weight = np.exp(-(lat/10)**2)
            
            for k, lon in enumerate(lons):
                # 经度相位（MJO向东传播）
                lon_phase = 2 * np.pi * lon / 360 * lon_wavenumber
                
                # OLR信号（负相关，MJO活跃时OLR降低）
                olr_base = 240.0  # 基础OLR值 (W/m²)
                olr_amplitude = 20.0 * lat_weight
                olr_data[i, j, k] = olr_base - olr_amplitude * np.sin(time_phase + lon_phase + seasonal_phase)
                
                # U850信号（西风增强）
                u850_base = 0.0  # 基础风速 (m/s)
                u850_amplitude = 5.0 * lat_weight
                uwnd850_data[i, j, k] = u850_base + u850_amplitude * np.sin(time_phase + lon_phase + seasonal_phase)
                
                # U200信号（与U850反相）
                u200_base = 0.0  # 基础风速 (m/s)
                u200_amplitude = 8.0 * lat_weight
                uwnd200_data[i, j, k] = u200_base - u200_amplitude * np.sin(time_phase + lon_phase + seasonal_phase)
    
    # 添加随机噪声使数据更真实
    if add_noise:
        print("添加随机噪声...")
        olr_data += np.random.normal(0, 5, olr_data.shape)
        uwnd850_data += np.random.normal(0, 1, uwnd850_data.shape)
        uwnd200_data += np.random.normal(0, 1.5, uwnd200_data.shape)
    
    # 创建xarray Dataset
    ds = xr.Dataset(
        {
            'olr': (['time', 'lat', 'lon'], olr_data),
            'uwnd850': (['time', 'lat', 'lon'], uwnd850_data),
            'uwnd200': (['time', 'lat', 'lon'], uwnd200_data),
        },
        coords={
            'time': time,
            'lat': lats,
            'lon': lons,
        }
    )
    
    # 添加属性
    ds.attrs['title'] = 'Fake Observation Data for MJOcast'
    ds.attrs['description'] = f'Generated fake observation data from {start_date} to {end_date}'
    ds.attrs['created'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ds.attrs['source'] = 'generate_fake_obs.py'
    
    ds.olr.attrs['long_name'] = 'Outgoing Longwave Radiation'
    ds.olr.attrs['units'] = 'W/m^2'
    ds.olr.attrs['standard_name'] = 'outgoing_longwave_radiation'
    
    ds.uwnd850.attrs['long_name'] = 'Zonal Wind at 850 hPa'
    ds.uwnd850.attrs['units'] = 'm/s'
    ds.uwnd850.attrs['standard_name'] = 'eastward_wind'
    
    ds.uwnd200.attrs['long_name'] = 'Zonal Wind at 200 hPa'
    ds.uwnd200.attrs['units'] = 'm/s'
    ds.uwnd200.attrs['standard_name'] = 'eastward_wind'
    
    ds.lat.attrs['long_name'] = 'Latitude'
    ds.lat.attrs['units'] = 'degrees_north'
    ds.lat.attrs['standard_name'] = 'latitude'
    
    ds.lon.attrs['long_name'] = 'Longitude'
    ds.lon.attrs['units'] = 'degrees_east'
    ds.lon.attrs['standard_name'] = 'longitude'
    
    # 保存文件
    output_path = os.path.join(output_dir, output_filename)
    print(f"\n保存文件到: {output_path}")
    ds.to_netcdf(output_path)
    
    print(f"✓ 成功生成观测数据文件!")
    print(f"  文件: {output_path}")
    print(f"  维度: {ds.dims}")
    print(f"  变量: {list(ds.data_vars)}")
    
    return ds


def main():
    parser = argparse.ArgumentParser(
        description='生成符合MJOcast格式要求的虚假观测数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成2000-2020年的观测数据
  python generate_fake_obs.py --start_date 2000-01-01 --end_date 2020-12-31
  
  # 使用自定义文件名
  python generate_fake_obs.py --start_date 2000-01-01 --end_date 2020-12-31 \\
      --output_filename my_obs_data.nc
        """
    )
    
    parser.add_argument(
        '--start_date',
        type=str,
        default='2017-08-01',
        help='开始日期 (格式: YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--end_date',
        type=str,
        default='2021-12-31',
        help='结束日期 (格式: YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--output_dir',
        type=str,
        default='./data/obs',
        help='输出目录 (默认: ./Observations)'
    )
    
    parser.add_argument(
        '--output_filename',
        type=str,
        default='ERA5_Meridional_Mean_Anomaly_Filtered120.nc',
        help='输出文件名 (默认: ERA5_Meridional_Mean_Anomaly_Filtered120.nc)'
    )
    
    parser.add_argument(
        '--lon_resolution',
        type=float,
        default=1.0,
        help='经度分辨率（度）(默认: 1.0)'
    )
    
    parser.add_argument(
        '--lat_resolution',
        type=float,
        default=1.0,
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
    generate_fake_obs_data(
        start_date=args.start_date,
        end_date=args.end_date,
        output_dir=args.output_dir,
        output_filename=args.output_filename,
        lon_resolution=args.lon_resolution,
        lat_resolution=args.lat_resolution,
        add_noise=not args.no_noise,
        seed=args.seed
    )


if __name__ == '__main__':
    main()

