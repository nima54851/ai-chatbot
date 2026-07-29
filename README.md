# AI 客服机器人 🤖

基于 Next.js 14 + Groq API 的智能客服聊天机器人，支持流式输出，专为「万能AI超市」产品销售场景定制。

## 功能特性

- 🌊 **流式响应** — Groq Llama 3.3 70B 实时打字效果
- 🎨 **深色主题** — 赛博朋克风格 UI，丝滑动画
- 📱 **响应式** — 完美适配桌面和移动端
- 🔒 **服务端路由** — API Key 安全存储在后端，不泄露前端
- ⚡ **Edge Runtime** — Vercel Edge 部署，极速响应

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/nima54851/ai-chatbot.git
cd ai-chatbot
```

### 2. 配置 API Key

在项目根目录创建 `.env.local`：

```env
GROQ_API_KEY=gsk_your_actual_key_here
# 可选：指定模型（默认 llama-3.3-70b-versatile）
GROQ_MODEL=llama-3.3-70b-versatile
```

> 🔑 获取 Groq API Key：[https://console.groq.com/keys](https://console.groq.com/keys)（免费注册，每月有免费额度）

### 3. 本地运行

```bash
npm install
npm run dev
```

打开 [http://localhost:3000](http://localhost:3000)

### 4. 一键部署到 Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/nima54851/ai-chatbot)

部署后在 Vercel 环境变量中设置 `GROQ_API_KEY`。

## 技术栈

| 技术 | 用途 |
|------|------|
| Next.js 14 App Router | 前端框架 |
| Groq API (OpenAI兼容) | AI 大脑 |
| TypeScript | 类型安全 |
| CSS Variables | 深色主题样式 |

## 可用 Groq 模型

| 模型 | 特点 |
|------|------|
| `llama-3.3-70b-versatile` | 推荐，速度快，效果好 |
| `llama-3.1-8b-instant` | 超快，适合简单问答 |
| `mixtral-8x7b-32768` | 均衡表现 |
| `gemma2-9b-it` | 轻量免费 |

## 产品信息

本机器人客服 Knows 以下产品：

- 📱 Telegram号码查询机器人 — ¥29/月
- ⚡ GitHub Agent自动化系统 — ¥99/月
- 📣 AI内容推流系统 — ¥199/月
- 🔗 n8n工作流自动化系统 — ¥149/月

收款：PayPal `paypalyinanzo@hotmail.com` | USDT TRC20 `TFfwcPBSF2t5t5pruoRfN1McxnuStFNkX3Cy`
客服：**@diquchaxun78_bot**
