from pathlib import Path
import json,subprocess,bisect,hashlib
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).resolve().parent;rows=json.loads((p/'capture.json').read_text());im=Image.open(p/'frames'/rows[0]['file']);w,h=im.size;outheight=h+64
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',22)
ff=Path('work/day07-env/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v9.0').resolve();out=p/'Day25-alphaearth-operation-32s.mp4'
pr=subprocess.Popen([str(ff),'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{outheight}','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
times=[r['t'] for r in rows]
def caption(t):
 if t<3:return '在臺灣自行選點，以 AlphaEarth 地理特徵尋找相似區域'
 if t<9:return '重新選點，搜尋海外四個圖幅；分數為向量相似度'
 if t<14:return '點選另一個候選，並排核對真實位置與影像'
 if t<21:return '改選山區：相似結果隨查詢位置重新計算'
 if t<26:return '加入臺灣其他地區，保留距離排除與空間分散條件'
 return '查看總排名：相似不代表相同，也不是分類正確率'
for i in range(32*30):
 t=i/30;r=rows[max(0,bisect.bisect_right(times,t)-1)];im=Image.open(p/'frames'/r['file']).convert('RGB');can=Image.new('RGB',(w,outheight),'#17394b');can.paste(im,(0,0));ImageDraw.Draw(can).text((24,h+18),caption(t),fill='white',font=font);pr.stdin.write(can.tobytes())
 if i in [30,360,435,525,615,705,795,900]:can.save(p/f'preview-{i//30}.png')
pr.stdin.close();assert pr.wait()==0
subprocess.run([str(ff),'-v','error','-i',str(out),'-f','null','-'],check=True)
gaps=[b-a for a,b in zip(times,times[1:])];q={'seconds':32,'resolution':[w,outheight],'original_frame_resolution':[w,h],'encoded_fps':30,'capture_frames':len(rows),'capture_method':'Timestamped actual browser screenshots during CUA UI operations; resampled to 30fps, no map frame synthesis','capture_average_fps':len(rows)/32,'max_capture_gap_s':max(gaps),'audio':'none; map has no audio','aspect_ratio':'original frame retained pixel-for-pixel; added 64px subtitle band','decode':'PASS','sha256':hashlib.sha256(out.read_bytes()).hexdigest()};(p/'qa.json').write_text(json.dumps(q,ensure_ascii=False,indent=2));print(q)
