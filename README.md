# Day25 — 這裡，像哪裡？
在臺灣地圖選點，以真實 AlphaEarth 2024 年特徵向量，搜尋海外四個圖幅或臺灣其他地區的相似區域。

[互動地圖](https://dongpo.github.io/geomni-30daymap-2026-day25-alphaearth/) · [32秒操作影片](video/Day25-alphaearth-operation-32s.mp4) · [資料與限制](DATA-NOTES.txt)

## 重現
Python 3.11，建立虛擬環境後：
```sh
pip install -r requirements-lock.txt
python scripts/acquire.py
python scripts/build_select.py
python -m http.server 8000
```
瀏覽 http://localhost:8000 。31份原始概覽快取已附；全球索引未附，下載腳本會按需從Google公開來源取得。

## 解讀
- 23,485個臺灣查詢格；15,790個海外候選格。每格約1.28公里見方，使用官方128倍概覽，不冒稱10m分析。
- 海外僅日本茨城、韓國全羅、越南北部、泰國中部四個圖幅；不是全球搜尋。
- cosine分數不是分類機率，亦不保證相同土地用途。影像為Esri多期鑲嵌，非2024同期真值。
- 點擊位置與搜尋向量在瀏覽器計算；底圖及影像仍需連線第三方圖磚服務。

## 來源與授權
The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind. CC BY 4.0.
[官方資料說明](https://developers.google.com/earth-engine/guides/aef_on_gcs_readme)
臺灣範圍：NLSC簡化縣市界，政府資料開放授權條款第1版。[來源](https://data.gov.tw/dataset/7442)
底圖 © OpenStreetMap contributors；影像 © Esri / Maxar / Earthstar Geographics及圖面列明供應者。影片保留圖面署名。未打包底圖或衛星影像圖磚。

影片為實際瀏覽器操作擷取，原始畫面不變形，另加字幕；無音軌。驗收見video/qa.json與evidence。
