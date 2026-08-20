# 城市天氣站

使用 Flask 與 Open-Meteo API 查詢不同城市的目前天氣和五日預報，不需要 API Key。

目前包含：

- 河南省 18 個城市與多個世界城市
- 12 種頁面主題、深色/淺色模式和攝氏/華氏切換
- 城市圖片、最近查詢、城市篩選
- 風向、風級、陣風、體感、平均氣溫、能見度、氣壓、UV、日落和月相資料
- 五分鐘天氣快取與圖片快取

## 啟動

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

開啟 http://127.0.0.1:5000 。

### 讓同一 Wi-Fi 的設備訪問

啟動後取得這台電腦的區域 IP，例如 `192.168.1.20`，其他手機、平板或電腦使用：

```text
http://192.168.1.20:5000
```

設備必須連接同一個 Wi-Fi，且 macOS 防火牆需要允許 Python 接受傳入連線。

### 公開給不在同一網路的人

本專案已包含 Render 部署設定。將專案上傳到 GitHub 後，在 Render 建立 Web Service，設定會自動使用：

```bash
gunicorn app:app
```

部署完成後，Render 會提供一個 `https://...onrender.com` 公開網址，其他網路的使用者即可訪問。天氣資料仍需要使用者設備能連線到 Open-Meteo。

## 測試

```bash
python -m unittest -v test_app.py
```

## API

`GET /api/weather?city=台北` 會回傳 JSON 天氣資料。

`GET /api/city-image?city=台北` 會回傳 Wikimedia Commons 城市圖片網址。

天氣資料來自 Open-Meteo，城市圖片搜尋來自 Wikimedia Commons；月相資訊由 Astral 在本機計算。
