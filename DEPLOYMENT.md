# 部署與回滾指南

## 日常更新

1. 先在本機啟動並測試：

```bash
source .venv/bin/activate
python -m unittest -v test_app.py
python -m py_compile app.py
```

2. 確認本機頁面和 API 正常：

```bash
curl -i http://127.0.0.1:5000/api/health
```

3. 提交並推送：

```bash
git add .
git commit -m "Describe the change"
git push origin main
```

4. Render 會由 `main` 分支自動部署。到 Render 的 **Events** 或 **Logs** 查看部署狀態。

## 部署後檢查

將下方網址替換成 Render 提供的公開網址：

```bash
curl -i https://city-weather-desk.onrender.com/api/health
curl -I https://city-weather-desk.onrender.com/
```

健康檢查應回傳 HTTP 200，並包含：

```json
{"service":"city-weather-desk","status":"ok"}
```

接著用手機流量或另一個網路開啟首頁，測試：

- 城市搜尋
- 河南城市選擇
- 詳細天氣資料
- 攝氏/華氏切換
- 主題切換
- 重新整理按鈕

## 發布失敗時

1. 打開 Render 的 **Logs**，先查看最後一個錯誤。
2. 確認 Build Command 是：

```bash
pip install -r requirements.txt
```

3. 確認 Start Command 是：

```bash
gunicorn app:app
```

4. 確認 GitHub `main` 分支已包含最新提交。
5. 修正後重新執行 **Manual Deploy -> Deploy latest commit**。

## 回滾

若新版本造成錯誤：

1. 在 GitHub 開啟 **Commits**。
2. 找到上一個正常版本的 commit。
3. 複製 commit ID。
4. 在本機執行：

```bash
git revert <bad-commit-id>
git push origin main
```

Render 會自動部署回滾後的版本。完成後再次檢查 `/api/health` 和首頁。

## 注意

- Render Free 服務長時間無流量後可能休眠，第一次請求可能需要等待。
- 公開網站需要 Open-Meteo 與 Wikimedia Commons 網路連線。
- 不要把密碼、Token 或 API Key 提交到 GitHub。
