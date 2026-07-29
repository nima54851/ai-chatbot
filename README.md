# 🤖 灵犀 AI 客服机器人

基于 **FastAPI** + **Groq Llama 3.3 70B** 的流式聊天机器人，专为「万能AI超市」产品销售场景定制。

---

## 🚀 一键部署到 Vercel（推荐）

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/nima54851/ai-chatbot)

> 点击上方按钮 → 自动跳转到 Vercel → 点 **Deploy**
>
> 部署后在 Vercel 项目 **Settings → Environment Variables** 添加：
> ```
> GROQ_API_KEY = gsk_your_real_key
> ```
> 然后 **Redeploy** 即可！

---

## 🖥️ 本地运行

```bash
# 克隆
git clone https://github.com/nima54851/ai-chatbot.git
cd ai-chatbot

# 安装依赖
npm install

# 配置 API Key
echo "GROQ_API_KEY=你的key" > .env.local

# 启动
npm run dev
# 打开 http://localhost:3000
```

---

## 🐍 Python 版（FastAPI，无需 Node.js）

```bash
# 安装
pip install fastapi uvicorn httpx

# 配置
export GROQ_API_KEY=你的key

# 启动
python app.py
# 打开 http://localhost:3001
```

---

## 🔑 获取 Groq API Key

1. 访问 👉 https://console.groq.com/keys
2. 注册/登录账号（免费）
3. 点击 **Create API Key**
4. 复制 key，填入环境变量

**免费额度**：每月充足，免费模型包括 Llama 3.3 70B / Llama 3.1 8B / Mixtral 8x7B / Gemma 2

---

## 🛠️ 可用 Groq 模型

| 模型 ID | 特点 |
|--------|------|
| `llama-3.3-70b-versatile` | ✅ 推荐，速度快，效果好 |
| `llama-3.1-8b-instant` | 超快，轻量问答 |
| `mixtral-8x7b-32768` | 均衡表现 |
| `gemma2-9b-it` | 轻量免费 |

设置方式：`GROQ_MODEL=llama-3.1-8b-instant`

---

## 💰 产品信息

客服 Knows 以下产品：

| 产品 | 价格 | 功能 |
|------|------|------|
| 📱 Telegram号码查询机器人 | ¥29/月 | 查询 Telegram 用户基础信息 |
| ⚡ GitHub Agent自动化系统 | ¥99/月 | GitHub 自动化运营 |
| 📣 AI内容推流系统 | ¥199/月 | 多平台内容分发 |
| 🔗 n8n工作流自动化 | ¥149/月 | 无代码工作流 |

**收款**：PayPal `paypalyinanzo@hotmail.com` | USDT TRC20 `TFfwcPBSF2t5t5pruoRfN1McxnuStFNkX3Cy`  
**客服**：@diquchaxun78_bot（付款后联系获取下载链接）

---

## 📁 项目结构

```
ai-chatbot/
├── app/
│   ├── page.tsx          ← 前端聊天界面（流式渲染）
│   ├── layout.tsx        ← 页面布局
│   ├── globals.css       ← 赛博朋克深色主题
│   └── api/
│       └── chat/
│           └── route.ts  ← Edge Runtime API（Groq 调用）
├── app.py                ← FastAPI 版本（Python，无需 Node）
├── vercel.json           ← Vercel 配置
└── package.json
```

---

## ⚡ 技术亮点

- 🌊 **SSE 流式输出** — 逐字渲染，打字机效果
- 🔒 **API Key 安全** — Key 只存在服务端，不泄露前端
- ⚡ **Edge Runtime** — Vercel Edge 节点，极速响应
- 🎨 **深色赛博朋克 UI** — 流畅动画，专业视觉
- 📱 **全响应式** — 桌面/平板/手机完美适配
