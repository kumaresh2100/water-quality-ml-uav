
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject
import numpy as np

# --- STEP 1: Load raster ---
input_path = "D:/Kumaresh_water_quality/ARASU/pond_5_osgeo_Clip1111.tif"
output_path = "G:/work_pond5/pond5_stacked_05m_withoutspe.tif"

with rasterio.open(input_path) as src:
    data = src.read().astype('float32')
    data[data < 0] = 0  # Replace negative values with 0

    # --- STEP 2: Reproject to EPSG:32644 ---
    dst_crs = "EPSG:32644"
    transform, width, height = calculate_default_transform(
        src.crs, dst_crs, src.width, src.height, *src.bounds
    )

    kwargs = src.meta.copy()
    kwargs.update({
        'crs': dst_crs,
        'transform': transform,
        'width': width,
        'height': height
    })

    temp_file = "reprojected_temp.tif"
    with rasterio.open(temp_file, 'w', **kwargs) as dst:
        for i in range(1, src.count + 1):
            reproject(
                source=rasterio.band(src, i),
                destination=rasterio.band(dst, i),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest
            )

# --- STEP 3: Resample to 0.5 m resolution ---
with rasterio.open(temp_file) as src:
    scale = src.res[0] / 0.5
    new_height = int(src.height * scale)
    new_width = int(src.width * scale)

    resampled_data = src.read(
        out_shape=(src.count, new_height, new_width),
        resampling=Resampling.bilinear
    )

    new_transform = src.transform * src.transform.scale(
        (src.width / new_width),
        (src.height / new_height)
    )

    kwargs = src.meta.copy()
    kwargs.update({
        'height': new_height,
        'width': new_width,
        'transform': new_transform
    })

    with rasterio.open(output_path, 'w', **kwargs) as dst:
        dst.write(resampled_data)
