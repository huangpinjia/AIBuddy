
# 🧑‍🏫 AIBuddy

一個以「引導式提示語設計」為核心、專為**國中小學生**打造的互動式機器學習教學聊天機器人。使用者可以透過「聊天」的方式，逐步理解監督式機器學習的基礎概念，例如感知器、決策樹、線性回歸等，適合用於資訊課補充教材或自主學習平台。

---

## 🚀 專案特色

- **引導式教學**：整合 GROW 教學模型（Goal, Reality, Analogy...）進行互動式引導，鼓勵學生自發學習。
- **提示語驅動（Prompt Engineering）**：透過 prompt.txt 精細設計對話策略，無須自訓模型，即可產出擬人化教學回應。
- **前後端整合**：Flask 架設 API，配合 HTML+JS 前端打造對話介面。
- **資料儲存**：使用 SQLite 紀錄每位學生的對話歷程，便於後續學習分析。
- **教學主題涵蓋五大監督式演算法**：
  - 感知器（Perceptron）
  - 三分岔決策樹（Decision Tree）
  - 線性回歸（Linear Regression）
  - K-近鄰（K-Nearest Neighbors）
  - 古典機率下的貝氏分類器（Naive Bayes）

---

## 📁 專案結構

```
├── app.py                # Flask 主程式，包含 GPT 呼叫與對話邏輯
├── index.html            # 聊天機器人前端介面
├── prompt.txt            # 核心教學提示語設計
├── chat_history.db       # SQLite 對話紀錄資料庫
├── requirements.txt      # 相依套件清單
├── build.sh              # 安裝腳本
├── render.yaml           # Render 平台部署設定
```

---

## 🛠️ 安裝與執行

### 前置需求
- Python 3.7+
- OpenAI API 金鑰（放入 `.env` 檔）

### 安裝步驟

```bash
git clone https://github.com/你的帳號/專案名稱.git
cd 專案名稱
bash build.sh
```

建立 `.env` 檔案，內容如下：

```env
GPT_API_BASE=https://api.openai.com/v1/chat/completions
GPT_API_KEY=你的API金鑰
```

### 啟動服務

```bash
python app.py
```

開啟瀏覽器，前往 [http://localhost:5000](http://localhost:5000)

---

## 🧪 使用方式

- 在聊天視窗中輸入問題，例如：「什麼是感知器？」
- 機器人會根據教學順序逐步引導，並使用生活化比喻說明。
- 適合搭配投影、課堂講解或小組討論使用。

---

## 🔧 目前開發狀態

- ✅ 第一版原型已完成：可正常互動、支援五大主題。

- 🛠️ 待優化項目：
  - 多人切換與持久記憶機制
  - 主題進度追蹤與歷程分析介面
  - 課程素材可視化與動畫支援

---

## 🙋‍♂️ 開發者貢獻

本專案由團隊開發完成，本人負責前後端架構、資料庫設計與 Prompt 編寫，亦負責其中一項教學主題的完整內容設計，未來也計畫持續優化提示語品質與使用者體驗。

---

## 📜 授權 License

本專案僅供學術研究與教育用途，未經許可請勿商業使用。
