from pathlib import Path
import json,hashlib
import numpy as np
from pyproj import Transformer
from rasterio import Affine
from shapely.geometry import shape,Polygon
from shapely.ops import unary_union
B=Path(__file__).resolve().parents[1];tiles=json.loads((B/'source/tiles.json').read_text());boundary=json.loads((B/'source/taiwan-counties.geojson').read_text());land=unary_union([shape(f['geometry']) for f in boundary['features']]);cells=[];vectors=[];regions=[]
for i,t in enumerate(tiles):
 raw=np.load(B/f'source/tile-{i}.npz')['raw'];m=json.loads((B/f'source/tile-{i}.json').read_text());tr=Affine(*m['transform'][:6]);inv=Transformer.from_crs(m['crs'],4326,always_xy=True);valid=np.all(raw!=-128,axis=0);a=raw.astype(float);a=np.sign(a)*(a/127.5)**2;norm=np.linalg.norm(a,axis=0);valid&=norm>0;a/=np.where(norm>0,norm,1)
 if i in range(2,6):regions.append({'name':t['region'],'corners':[list(inv.transform(*(tr*p))) for p in [(0,0),(64,0),(64,64),(0,64),(0,0)]]})
 for y,x in zip(*np.where(valid)):
  lon,lat=inv.transform(*(tr*(int(x)+.5,int(y)+.5)));west=int(m['crs'][-2:])*6-186
  if not west<=lon<west+6:continue
  ring=[list(inv.transform(*(tr*p))) for p in [(x,y),(x+1,y),(x+1,y+1),(x,y+1),(x,y)]]
  tw=i not in range(2,6)
  if tw and not land.intersects(Polygon(ring)):continue
  cells.append({'id':f'{i}-{y}-{x}','region':'臺灣' if tw else t['region'],'tw':tw,'lon':lon,'lat':lat,'ring':ring});vectors.append(a[:,y,x])
V=np.array(vectors,dtype='<f4');V.tofile(B/'vectors.f32');(B/'catalog.json').write_text(json.dumps({'cells':cells,'regions':regions,'year':2024,'cell_m':1280},ensure_ascii=False,separators=(',',':')))
from shapely.geometry import mapping
(B/'taiwan.geojson').write_text(json.dumps(mapping(land),separators=(',',':')))
qa={'cells':len(cells),'taiwan_query_cells':sum(f['tw'] for f in cells),'overseas_candidate_cells':sum(not f['tw'] for f in cells),'unique_ids':len(set(f['id'] for f in cells)),'max_float32_norm_error':float(abs(np.linalg.norm(V,axis=1)-1).max()),'bytes':V.nbytes,'tiles':len(tiles)}
assert qa['cells']==qa['unique_ids'];assert np.isfinite(V).all();assert qa['max_float32_norm_error']<1e-6
(B/'evidence/select-numeric-qa.json').write_text(json.dumps(qa,indent=2));print(qa)
(B/'source/SHA256-v3.json').write_text(json.dumps({str(p.relative_to(B)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (B/'source').glob('*') if p.is_file() and 'SHA256' not in p.name},indent=2))
