from pathlib import Path
import json,time,hashlib
import numpy as np
import pyarrow.parquet as pq
import rasterio
from pyproj import Transformer
B=Path(__file__).resolve().parents[1]
regions=[('臺灣北部圖幅',121.15,25.035),('臺灣中部圖幅',120.45,23.85),('日本茨城圖幅',140.20,36.00),('韓國全羅圖幅',126.85,35.80),('越南北部圖幅',106.10,20.80),('泰國中部圖幅',100.55,14.15)]
cols=['path','year','crs','utm_west','utm_south','utm_east','utm_north','wgs84_west','wgs84_south','wgs84_east','wgs84_north']
index=B/'source/aef_index.parquet'
if not index.exists():
 from urllib.request import urlretrieve
 urlretrieve('https://storage.googleapis.com/alphaearth_foundations/satellite_embedding/v1/annual/aef_index.parquet',index)
rows=pq.read_table(B/'source/aef_index.parquet',columns=cols,filters=[('year','=',2024)]).to_pylist()
from shapely.geometry import shape,box
from shapely.ops import unary_union
land=json.loads((B/'source/taiwan-counties.geojson').read_text())
mask=unary_union([shape(f['geometry']) for f in land['features']])
selected=json.loads((B/'source/tiles.json').read_text())[:6]
paths={r['path'] for r in selected}
for r in rows:
 if r['path'] not in paths and mask.intersects(box(r['wgs84_west'],r['wgs84_south'],r['wgs84_east'],r['wgs84_north'])):
  r.update(region='臺灣查詢圖幅',query_lon=None,query_lat=None);selected.append(r);paths.add(r['path'])
print('Selected tiles',len(selected),flush=True)
(B/'source/tiles.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2))
for i,r in enumerate(selected):
    cache=B/f'source/tile-{i}.npz'
    if cache.exists():continue
    url=r['path'].replace('gs://','https://storage.googleapis.com/')
    start=time.time()
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tiff',GDAL_HTTP_TIMEOUT='90'):
      with rasterio.open(url) as ds:
        print('OPEN',i,r['region'],ds.shape,ds.overviews(1),flush=True)
        raw=ds.read(out_shape=(64,64,64))
        transform=ds.transform*ds.transform.scale(ds.width/64,ds.height/64)
        meta={'url':url,'crs':str(ds.crs),'transform':list(transform),'shape':raw.shape,'elapsed_seconds':time.time()-start,'nodata':ds.nodata,'overview_factor':128}
    np.savez_compressed(cache,raw=raw)
    (B/f'source/tile-{i}.json').write_text(json.dumps(meta,indent=2))
    print('DONE',i,cache.stat().st_size,meta['elapsed_seconds'],flush=True)
