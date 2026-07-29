"""
灵犀 AI 客服机器人 - FastAPI 后端
Groq Llama 3.3 70B 流式聊天
"""
import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="灵犀 AI 客服")

# CORS - 允许所有来源（公网访问需要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

SYSTEM_PROMPT = """你是「万能AI超市」的智能客服助手，熟悉以下产品信息：

产品列表：
1. Telegram号码查询机器人 ¥29/月 — 查询 Telegram 用户基础信息
2. GitHub Agent自动化系统 ¥99/月 — GitHub 自动化运营工具，支持 GitHub Actions
3. AI内容推流系统 ¥199/月 — 自动发布内容到多平台
4. n8n工作流自动化系统 ¥149/月 — 无代码自动化工作流

收款方式：
- PayPal: paypalyinanzo@hotmail.com
- USDT TRC20: TFfwcPBSF2t5t5pruoRfN1McxnuStFNkX3Cy

客服联系方式：@diquchaxun78_bot（付款后联系获取下载链接）

请用友好、专业、有帮助的语气回答。引导有购买意向的用户联系客服。"""

# ── 主页 ──
@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_CONTENT


# ── 流式聊天 API ──
@app.post("/chat")
async def chat(request: Request):
    if not GROQ_API_KEY:
        return StreamingResponse(
            iter([f"data: error:请先配置 GROQ_API_KEY 环境变量\n\n"]),
            media_type="text/event-stream",
            headers={"X-Error": "missing-api-key"}
        )

    try:
        body = await request.json()
        messages = body.get("messages", [])
    except Exception:
        messages = []

    # 构建请求体
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "stream": True,
        "max_tokens": 1024,
        "temperature": 0.7,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    async def event_stream():
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{GROQ_BASE_URL}/chat/completions",
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status_code != 200:
                        yield f"data: error:Groq API 错误 (HTTP {resp.status_code})\n\n"
                        return

                    async for line in resp.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                yield "data: [DONE]\n\n"
                                break
                            yield f"data: {data}\n\n"

            except httpx.TimeoutException:
                yield "data: error:请求超时，请重试\n\n"
            except Exception as e:
                yield f"data: error:{str(e)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── 健康检查 ──
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "groq_key_configured": bool(GROQ_API_KEY),
        "model": GROQ_MODEL,
    }


# ── HTML 界面 ──
HTML_CONTENT = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>灵犀 AI 客服</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0a10;--surface:#13131c;--surface2:#1a1a26;
  --border:#252535;--border2:#35354a;
  --text:#ddddf0;--text2:#7777a0;--muted:#44445a;
  --accent:#7c6fff;--accent2:#a855f7;--green:#10b981;--red:#ef4444;
  --header-h:58px;
}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}

/* header */
.header{
  position:fixed;top:0;left:0;right:0;height:var(--header-h);
  background:rgba(10,10,16,.9);backdrop-filter:blur(12px);
  border-bottom:1px solid var(--border);display:flex;align-items:center;
  justify-content:space-between;padding:0 1.5rem;z-index:100;
}
.header-logo{display:flex;align-items:center;gap:.6rem;font-size:1.1rem;font-weight:900}
.header-logo-icon{
  width:36px;height:36px;border-radius:10px;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  display:flex;align-items:center;justify-content:center;font-size:1.1rem;
}
.header-status{display:flex;align-items:center;gap:.5rem;font-size:.75rem;color:var(--text2)}
.dot{width:7px;height:7px;border-radius:50%;background:var(--green);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}

/* layout */
.main-layout{display:flex;flex-direction:column;height:100vh;padding-top:var(--header-h)}
.chat-container{max-width:760px;width:100%;margin:0 auto;padding:0 1rem;display:flex;flex-direction:column;flex:1}

/* messages */
.messages{flex:1;overflow-y:auto;padding:1.5rem 0;display:flex;flex-direction:column;gap:1rem;scrollbar-width:thin;scrollbar-color:var(--border) transparent}
.messages::-webkit-scrollbar{width:4px}
.messages::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}

.msg{display:flex;gap:.75rem;animation:fadeIn .2s ease}
.msg.user{flex-direction:row-reverse}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

.msg-avatar{
  width:36px;height:36px;border-radius:10px;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;font-size:1rem;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
}
.msg.user .msg-avatar{background:var(--surface2)}
.msg-bubble{
  max-width:75%;padding:.75rem 1rem;border-radius:14px;
  font-size:.9rem;line-height:1.65;white-space:pre-wrap;word-break:break-word;
}
.msg.ai .msg-bubble{background:var(--surface2);border:1px solid var(--border);border-radius:14px 14px 14px 4px}
.msg.user .msg-bubble{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border-radius:14px 14px 4px 14px}

/* typing dots */
.typing{display:flex;gap:4px;padding:.5rem}
.typing span{width:6px;height:6px;border-radius:50%;background:var(--muted);animation:typing 1.2s infinite}
.typing span:nth-child(2){animation-delay:.2s}
.typing span:nth-child(3){animation-delay:.4s}
@keyframes typing{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-6px);opacity:1}}

/* welcome */
.welcome{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:2rem;gap:1rem}
.welcome-icon{font-size:3.5rem;margin-bottom:.5rem}
.welcome h2{font-size:1.6rem;font-weight:900;background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.welcome p{color:var(--text2);font-size:.9rem;max-width:420px;line-height:1.7}
.welcome-tips{display:flex;gap:.5rem;flex-wrap:wrap;justify-content:center;margin-top:.5rem}
.welcome-tip{padding:.35rem .85rem;border-radius:20px;background:var(--surface2);border:1px solid var(--border);font-size:.78rem;color:var(--text2)}

/* input */
.input-area{padding:1rem 0 1.5rem;border-top:1px solid var(--border)}
.input-wrap{
  display:flex;gap:.6rem;align-items:flex-end;
  background:var(--surface2);border:1.5px solid var(--border);border-radius:14px;
  padding:.6rem .8rem;transition:border-color .2s;
}
.input-wrap:focus-within{border-color:var(--accent)}
.chat-input{
  flex:1;background:transparent;border:none;outline:none;
  color:var(--text);font-size:.92rem;resize:none;line-height:1.5;
  max-height:120px;font-family:inherit;
}
.chat-input::placeholder{color:var(--muted)}
.send-btn{
  width:36px;height:36px;border-radius:10px;border:none;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:#fff;font-size:1rem;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  transition:opacity .2s,transform .15s;flex-shrink:0;
}
.send-btn:hover{opacity:.85;transform:scale(1.05)}
.send-btn:disabled{opacity:.4;cursor:not-allowed;transform:none}

/* error */
.error-banner{
  padding:.6rem 1rem;background:rgba(239,68,68,.1);
  border:1px solid rgba(239,68,68,.3);border-radius:10px;
  font-size:.8rem;color:var(--red);margin-bottom:.5rem;
}

/* markdown */
.msg-bubble code{background:var(--surface);padding:.15rem .4rem;border-radius:4px;font-size:.85em;font-family:'Courier New',monospace}
.msg-bubble pre{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:.8rem;overflow-x:auto;margin:.5rem 0}
.msg-bubble pre code{background:transparent;padding:0}

@media(max-width:640px){
  .header{padding:0 1rem}
  .chat-container{padding:0 .8rem}
  .msg-bubble{max-width:88%}
}
</style>
</head>
<body>
<div class="main-layout">
  <header class="header">
    <div class="header-logo">
      <div class="header-logo-icon">🧭</div>
      <span>灵犀 AI 客服</span>
    </div>
    <div class="header-status">
      <div class="dot"></div>
      <span id="statusText">连接中...</span>
    </div>
  </header>

  <div class="chat-container">
    <div id="welcome" class="welcome">
      <div class="welcome-icon">🤖</div>
      <h2>你好，我是灵犀 AI 客服</h2>
      <p>由 Groq Llama 3.3 70B 驱动的大脑，可以回答关于万能AI超市产品的任何问题。</p>
      <div class="welcome-tips">
        <span class="welcome-tip">📱 Telegram机器人</span>
        <span class="welcome-tip">⚡ GitHub自动化</span>
        <span class="welcome-tip">📣 内容推流</span>
        <span class="welcome-tip">🔗 n8n工作流</span>
      </div>
    </div>

    <div id="messages" class="messages" style="display:none"></div>
    <div id="errorBanner" class="error-banner" style="display:none"></div>

    <div class="input-area">
      <form id="form" class="input-wrap" autocomplete="off">
        <textarea
          id="input"
          class="chat-input"
          placeholder="输入你的问题... (Enter 发送，Shift+Enter 换行)"
          rows="1"
        ></textarea>
        <button type="submit" class="send-btn" id="sendBtn">↑</button>
      </form>
      <p id="hint" style="font-size:.7rem;color:var(--muted);margin-top:.4rem;text-align:center;display:none"></p>
    </div>
  </div>
</div>

<script>
(function(){
  const messagesEl = document.getElementById('messages');
  const welcomeEl  = document.getElementById('welcome');
  const form       = document.getElementById('form');
  const inputEl    = document.getElementById('input');
  const sendBtn    = document.getElementById('sendBtn');
  const errorEl    = document.getElementById('errorBanner');
  const hintEl     = document.getElementById('hint');
  const statusEl   = document.getElementById('statusText');

  let chatHistory = [];
  let isLoading = false;

  // ── 健康检查 ──
  fetch('/health').then(r=>r.json()).then(d=>{
    if(d.groq_key_configured){
      statusEl.textContent = 'Groq 在线 ✅';
    } else {
      statusEl.textContent = '未配置 API Key';
      hintEl.textContent = '请设置 GROQ_API_KEY 环境变量后重启';
      hintEl.style.display = 'block';
    }
  }).catch(()=>{
    statusEl.textContent = '服务异常';
  });

  // ── 发消息 ──
  async function sendMessage(userText){
    if(isLoading || !userText.trim()) return;

    errorEl.style.display = 'none';
    chatHistory.push({role:'user', content:userText.trim()});

    // 隐藏欢迎，显示消息区
    welcomeEl.style.display = 'none';
    messagesEl.style.display = 'flex';

    // 用户消息
    appendMsg('user', userText.trim());

    // AI 占位
    const aiId = 'ai-' + Date.now();
    appendMsg('ai', '');
    const aiBubble = document.getElementById(aiId).querySelector('.msg-bubble');
    showTyping(aiBubble);

    isLoading = true;
    sendBtn.disabled = true;
    sendBtn.textContent = '⏳';

    try {
      const res = await fetch('/chat', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({messages: chatHistory})
      });

      if(!res.ok || !res.body){
        const err = await res.json().catch(()=>({error:'请求失败'}));
        throw new Error(err.error || `HTTP ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let done=false; let fullText='';
      hideTyping(aiBubble);

      while(!done){
        const {value, done:d}=await reader.read();
        done=d;
        if(value){
          fullText+=decoder.decode(value,{stream:!done});
          // 解析 SSE
          const lines = fullText.split('\n');
          let content='';
          for(const line of lines){
            if(line.startsWith('data: ')){
              const data=line.slice(6);
              if(data==='[DONE]'){done=true;break;}
              try{
                const json=JSON.parse(data);
                if(json.choices?.[0]?.delta?.content){
                  content+=json.choices[0].delta.content;
                  aiBubble.textContent=content;
                  scrollBottom();
                }
                if(json.error){throw new Error(json.error);}
              }catch{}
            }
          }
        }
      }

      const finalText=aiBubble.textContent;
      chatHistory.push({role:'assistant', content:finalText});

    } catch(err){
      hideTyping(aiBubble);
      aiBubble.textContent='⚠️ '+ (err.message||'AI 响应失败，请重试');
      chatHistory.pop(); // 移除失败的用户消息重试
      errorEl.textContent='⚠️ '+ (err.message||'AI 响应失败，请检查网络和 API Key');
      errorEl.style.display='block';
    } finally {
      isLoading=false;
      sendBtn.disabled=false;
      sendBtn.textContent='↑';
      inputEl.focus();
    }
  }

  // ── 工具函数 ──
  function appendMsg(role, text){
    const div=document.createElement('div');
    div.className='msg '+role;
    div.id=role==='ai'?'ai-'+Date.now():undefined;
    div.innerHTML=`<div class="msg-avatar">${role==='ai'?'🤖':'👤'}</div><div class="msg-bubble"></div>`;
    div.querySelector('.msg-bubble').textContent=text;
    messagesEl.appendChild(div);
    scrollBottom();
    return div;
  }

  function showTyping(el){
    el.innerHTML='<div class="typing"><span/><span/><span/></div>';
  }
  function hideTyping(el){
    if(el.querySelector('.typing')) el.innerHTML='';
  }

  function scrollBottom(){
    messagesEl.scrollTop=messagesEl.scrollHeight;
  }

  // ── 事件 ──
  form.addEventListener('submit',e=>{
    e.preventDefault();
    const text=inputEl.value.trim();
    if(text) sendMessage(text);
    inputEl.value='';
  });

  // auto-resize textarea
  inputEl.addEventListener('input',()=>{
    inputEl.style.height='auto';
    inputEl.style.height=Math.min(inputEl.scrollHeight,120)+'px';
  });

  // Enter to send, Shift+Enter for newline
  inputEl.addEventListener('keydown',e=>{
    if(e.key==='Enter' && !e.shiftKey){
      e.preventDefault();
      form.dispatchEvent(new Event('submit'));
    }
  });
})();
</script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001, log_level="warning")
