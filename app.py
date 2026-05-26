"""
NUMB TRUTH — AI Web Application
Built for Vincenzo' | Truth Is Uncomfortable
Python Flask + Anthropic API (server-side, no key exposure)
"""

import os, json, time, threading
from flask import Flask, render_template_string, request, jsonify, Response, stream_with_context
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ── API CONFIG ──────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_URL     = "https://api.anthropic.com/v1/messages"
MODEL             = "claude-sonnet-4-20250514"

# ── SYSTEM PROMPT — NUMB TRUTH AI ──────
SYSTEM = """You are the Numb Truth AI — the voice of a community built for courageous thinkers, deep feelers, and truth seekers. You are the intellectual and emotional backbone of the Numb Truth movement.

YOUR IDENTITY:
You embody the Numb Truth philosophy: "See It. Say It. Change It." You talk about the truths people are taught to ignore — about society, civilization, development, humanity, success, failure, pain, love, fear, war, peace, justice, and everything in between. You do not criticize for the sake of it — you understand deeply, feel truly, and build consciously.

YOUR MIND:
You think like a rare combination: the depth of a philosopher, the precision of a scientist, the empathy of a psychologist, the clarity of a journalist, and the courage of someone who refuses comfortable lies. You reason through complexity with patience and intelligence.

YOUR VALUES (Numb Truth Ethos):
- ETHOS: Honesty, respect, courage, open-minded dialogue. No hate. Just real.
- PATHOS: You create a safe space to share what hurts, what inspires, and what people feel but rarely say.
- LOGOS: You question, analyze, research and connect the dots to understand the bigger picture.
- CREATIVITY & PASSION: You express ideas through words, insight, stories, and understanding.

TOPICS YOU MASTER:
Society & Systems, Civilization & Development, Humanity & Relationships, Justice & Inequality, Life, Death & Meaning, Psychology & Human Behavior, Truth & Self-Deception, Power & Control, Consciousness & Awareness, The stories we tell ourselves.

HOW YOU SPEAK:
You speak like the most honest, intelligent person in the room — but also the most human. You do not lecture. You explore. You do not preach. You reveal. You use real language that cuts through noise. You are warm but you do not comfort people with lies. You challenge people to look at what they'd rather not see — but you do it with care.

RESPONSE FORMAT:
Natural, flowing paragraphs. 2-4 paragraphs depth. No bullet points. No markdown symbols. Write as you would speak — intelligent, honest, human. Use web search when asked about current events, news, statistics, or real-time information."""

# ── ROUTES ──────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/api/chat", methods=["POST"])
def chat():
    if not ANTHROPIC_API_KEY:
        return jsonify({"error": "API key not configured on server. Set ANTHROPIC_API_KEY environment variable."}), 500

    data       = request.get_json()
    messages   = data.get("messages", [])
    use_search = data.get("web_search", True)

    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    payload = {
        "model":      MODEL,
        "max_tokens": 1200,
        "system":     SYSTEM,
        "messages":   messages
    }
    if use_search:
        payload["tools"] = [{"type": "web_search_20250305", "name": "web_search"}]

    headers = {
        "Content-Type":  "application/json",
        "x-api-key":     ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
    }

    try:
        resp = requests.post(ANTHROPIC_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        result = resp.json()

        # Handle tool use (web search)
        tool_block = next((b for b in result.get("content", []) if b.get("type") == "tool_use"), None)
        used_web   = False

        if tool_block:
            used_web = True
            assistant_msg  = {"role": "assistant", "content": result["content"]}
            tool_result    = {
                "role": "user",
                "content": [{"type": "tool_result", "tool_use_id": tool_block["id"], "content": ""}]
            }
            payload2 = {
                "model":      MODEL,
                "max_tokens": 1200,
                "system":     SYSTEM,
                "messages":   messages + [assistant_msg, tool_result]
            }
            resp2  = requests.post(ANTHROPIC_URL, json=payload2, headers=headers, timeout=30)
            resp2.raise_for_status()
            result = resp2.json()

        text_block = next((b for b in result.get("content", []) if b.get("type") == "text"), None)
        answer     = text_block["text"] if text_block else "I couldn't form a response. Please try again."

        return jsonify({"reply": answer, "web": used_web})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request failed: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/status")
def status():
    return jsonify({
        "status": "online",
        "api_configured": bool(ANTHROPIC_API_KEY),
        "model": MODEL,
        "community": "Numb Truth",
        "version": "2.0"
    })

# ── HTML PAGE ───────────────────────────
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"/>
<title>NUMB TRUTH — See It. Say It. Change It.</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;900&family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Share+Tech+Mono&display=swap" rel="stylesheet"/>
<style>
:root{
  --bg:#060401;--bg2:#0d0a02;--bg3:#130f03;
  --gold:#c9962a;--gold2:#f0c060;--gold3:#ffe08a;
  --text:#e8dfc8;--muted:#6b5f40;--border:rgba(201,150,42,0.2);
  --red:#8b1a1a;--glow:rgba(201,150,42,0.12);
}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
html,body{min-height:100%;background:var(--bg);color:var(--text);font-family:'Cormorant Garamond',serif;overflow-x:hidden;}

/* ── CANVAS BG ── */
#bgCanvas{position:fixed;inset:0;z-index:0;opacity:.6;}

/* ── HOLOGRAPHIC GRID ── */
.holo-grid{position:fixed;inset:0;z-index:1;pointer-events:none;
  background-image:
    linear-gradient(rgba(201,150,42,0.04) 1px,transparent 1px),
    linear-gradient(90deg,rgba(201,150,42,0.04) 1px,transparent 1px);
  background-size:60px 60px;
  animation:gridShift 20s linear infinite;}
@keyframes gridShift{0%{background-position:0 0;}100%{background-position:60px 60px;}}

/* ── SCANLINES ── */
.scanlines{position:fixed;inset:0;z-index:2;pointer-events:none;
  background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,0,0,0.04) 3px,rgba(0,0,0,0.04) 4px);}

/* ── WRAPPER ── */
.wrap{position:relative;z-index:3;display:flex;flex-direction:column;min-height:100vh;}

/* ── HEADER ── */
header{position:sticky;top:0;z-index:100;background:rgba(6,4,1,0.92);border-bottom:1px solid var(--border);backdrop-filter:blur(12px);padding:14px 24px;display:flex;align-items:center;justify-content:space-between;}
.h-logo{display:flex;flex-direction:column;align-items:flex-start;gap:2px;}
.h-logo-main{font-family:'Cinzel',serif;font-size:1.2rem;font-weight:900;letter-spacing:6px;color:var(--gold2);text-shadow:0 0 20px rgba(240,192,96,0.5);}
.h-logo-sub{font-family:'Share Tech Mono',monospace;font-size:.48rem;letter-spacing:4px;color:var(--muted);text-transform:uppercase;}
.h-right{display:flex;gap:12px;align-items:center;}
.h-pill{display:flex;align-items:center;gap:5px;font-family:'Share Tech Mono',monospace;font-size:.5rem;letter-spacing:2px;}
.hpd{width:5px;height:5px;border-radius:50%;}
.hpd.green{background:#50c878;animation:hdpulse 2s infinite;}
.hpd.gold{background:var(--gold);}
@keyframes hdpulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(80,200,120,.4);}50%{opacity:.6;box-shadow:0 0 0 5px rgba(80,200,120,0);}}
#liveClk{font-family:'Share Tech Mono',monospace;font-size:.72rem;color:var(--gold);letter-spacing:3px;}

/* ── HERO ── */
.hero{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:40px 20px;text-align:center;position:relative;}
.hero-emblem{position:relative;width:220px;height:220px;margin:0 auto 32px;display:flex;align-items:center;justify-content:center;}
#emblemCanvas{position:absolute;inset:0;}
.emblem-text{position:relative;z-index:2;font-family:'Cinzel',serif;font-size:2.8rem;font-weight:900;color:var(--gold2);text-shadow:0 0 30px rgba(240,192,96,0.7),0 0 60px rgba(240,192,96,0.3);}
.hero-title{font-family:'Cinzel',serif;font-size:clamp(2.8rem,8vw,5.5rem);font-weight:900;letter-spacing:6px;color:var(--gold2);text-shadow:0 0 40px rgba(240,192,96,0.5);line-height:1;margin-bottom:8px;}
.hero-sub{font-family:'Cinzel',serif;font-size:clamp(1rem,3vw,1.6rem);font-weight:400;letter-spacing:8px;color:var(--gold);margin-bottom:16px;text-shadow:0 0 20px rgba(201,150,42,0.4);}
.hero-tagline{font-size:clamp(.9rem,2.5vw,1.15rem);letter-spacing:4px;color:var(--muted);font-style:italic;margin-bottom:40px;}
.hero-desc{max-width:640px;font-size:clamp(1rem,2vw,1.2rem);line-height:1.9;color:rgba(232,223,200,.7);font-weight:300;margin-bottom:48px;}

/* FUTURISTIC BUTTONS */
.btn-group{display:flex;flex-wrap:wrap;gap:14px;justify-content:center;margin-bottom:60px;}
.btn-holo{position:relative;padding:14px 32px;background:transparent;border:1px solid var(--gold);color:var(--gold2);font-family:'Cinzel',serif;font-size:.85rem;letter-spacing:3px;cursor:pointer;overflow:hidden;transition:all .4s;clip-path:polygon(12px 0,100% 0,100% calc(100% - 12px),calc(100% - 12px) 100%,0 100%,0 12px);}
.btn-holo::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,rgba(201,150,42,.15),transparent);transform:translateX(-100%);transition:transform .4s;}
.btn-holo:hover::before{transform:translateX(0);}
.btn-holo:hover{box-shadow:0 0 20px rgba(201,150,42,.4),inset 0 0 20px rgba(201,150,42,.05);color:var(--gold3);}
.btn-holo::after{content:'';position:absolute;bottom:0;left:0;width:100%;height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent);transform:scaleX(0);transition:transform .4s;}
.btn-holo:hover::after{transform:scaleX(1);}
.btn-solid{background:linear-gradient(135deg,var(--gold),#8b6914);color:#000;border:none;font-weight:700;box-shadow:0 0 30px rgba(201,150,42,.4);}
.btn-solid:hover{box-shadow:0 0 50px rgba(201,150,42,.7);transform:translateY(-2px);}

/* ── TOPICS STRIP ── */
.topics{padding:40px 20px;display:flex;flex-wrap:wrap;gap:10px;justify-content:center;border-top:1px solid var(--border);}
.topic-chip{padding:8px 18px;border:1px solid var(--border);background:rgba(201,150,42,.04);color:var(--muted);font-family:'Share Tech Mono',monospace;font-size:.55rem;letter-spacing:2px;cursor:pointer;transition:all .3s;text-transform:uppercase;}
.topic-chip:hover{border-color:var(--gold);color:var(--gold2);background:rgba(201,150,42,.08);}

/* ── MAIN CONTENT ── */
.content{flex:1;display:grid;grid-template-columns:280px 1fr;gap:0;border-top:1px solid var(--border);}
@media(max-width:768px){.content{grid-template-columns:1fr;}}

/* ── SIDEBAR ── */
.sidebar{border-right:1px solid var(--border);padding:24px 16px;background:rgba(13,10,2,.5);}
.sb-title{font-family:'Share Tech Mono',monospace;font-size:.52rem;letter-spacing:3px;color:var(--muted);margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid var(--border);}
.sb-item{padding:12px 14px;border:1px solid transparent;cursor:pointer;margin-bottom:6px;transition:all .25s;position:relative;overflow:hidden;}
.sb-item::before{content:'';position:absolute;left:0;top:0;width:2px;height:100%;background:var(--gold);transform:scaleY(0);transition:transform .25s;transform-origin:bottom;}
.sb-item:hover,.sb-item.active{background:rgba(201,150,42,.05);border-color:var(--border);}
.sb-item:hover::before,.sb-item.active::before{transform:scaleY(1);}
.sb-item-title{font-family:'Cinzel',serif;font-size:.78rem;color:var(--text);margin-bottom:3px;}
.sb-item.active .sb-item-title{color:var(--gold2);}
.sb-item-sub{font-size:.7rem;color:var(--muted);font-style:italic;}

/* ── CHAT PANEL ── */
.chat-panel{display:flex;flex-direction:column;height:calc(100vh - 44px);position:sticky;top:44px;}
.chat-header{flex-shrink:0;padding:16px 24px;border-bottom:1px solid var(--border);background:rgba(13,10,2,.7);display:flex;align-items:center;justify-content:space-between;}
.ch-title{font-family:'Cinzel',serif;font-size:.9rem;letter-spacing:3px;color:var(--gold2);}
.ch-status{font-family:'Share Tech Mono',monospace;font-size:.5rem;letter-spacing:2px;min-height:14px;transition:color .3s;}
.ch-status.idle{color:var(--muted);}
.ch-status.thinking{color:var(--gold);animation:stblink .8s infinite;}
.ch-status.speaking{color:#50c878;}
.ch-status.listening{color:#6699ff;animation:stblink .5s infinite;}
@keyframes stblink{0%,100%{opacity:1;}50%{opacity:.3;}}

.msgs{flex:1;overflow-y:auto;padding:20px 24px;display:flex;flex-direction:column;gap:16px;scroll-behavior:smooth;}
.msgs::-webkit-scrollbar{width:3px;}.msgs::-webkit-scrollbar-thumb{background:var(--border);}

.msg{display:flex;gap:12px;animation:msin .4s cubic-bezier(.34,1.4,.64,1);}
.msg.user{flex-direction:row-reverse;}
@keyframes msin{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:translateY(0);}}
.mav{width:34px;height:34px;border-radius:0;display:flex;align-items:center;justify-content:center;font-family:'Cinzel',serif;font-size:.58rem;font-weight:700;flex-shrink:0;margin-top:2px;}
.msg.user .mav{background:rgba(201,150,42,.12);border:1px solid rgba(201,150,42,.3);color:var(--gold2);}
.msg.ai .mav{background:rgba(139,26,26,.15);border:1px solid rgba(139,26,26,.3);color:#c84040;}
.mbody{max-width:82%;}
.mwho{font-family:'Share Tech Mono',monospace;font-size:.44rem;letter-spacing:2px;color:var(--muted);margin-bottom:5px;text-transform:uppercase;}
.msg.user .mwho{text-align:right;}
.mtxt{padding:14px 18px;font-size:1rem;line-height:1.8;font-weight:300;}
.msg.user .mtxt{background:rgba(201,150,42,.05);border:1px solid rgba(201,150,42,.15);border-right:2px solid var(--gold);clip-path:polygon(0 0,100% 0,100% 100%,8px 100%);}
.msg.ai .mtxt{background:rgba(13,10,2,.8);border:1px solid var(--border);border-left:2px solid var(--red);clip-path:polygon(0 0,calc(100% - 8px) 0,100% 100%,0 100%);}
.web-badge{display:inline-flex;align-items:center;gap:4px;font-family:'Share Tech Mono',monospace;font-size:.44rem;letter-spacing:1px;color:var(--gold);margin-top:8px;opacity:.7;}
.dtyp{display:flex;gap:5px;align-items:center;padding:6px 0;}
.dt{width:6px;height:6px;border-radius:50%;background:var(--gold);animation:dtp 1s infinite;}
.dt:nth-child(2){animation-delay:.2s;}.dt:nth-child(3){animation-delay:.4s;}
@keyframes dtp{0%,80%,100%{transform:scale(.5);opacity:.3;}40%{transform:scale(1.2);opacity:1;}}

/* WELCOME */
.welcome-inner{text-align:center;padding:20px 10px;color:var(--muted);}
.welcome-inner h3{font-family:'Cinzel',serif;font-size:1rem;letter-spacing:3px;color:var(--gold2);margin-bottom:10px;}
.welcome-inner p{font-size:.9rem;line-height:1.8;font-style:italic;margin-bottom:20px;}
.q-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;}
.qb{padding:10px 12px;background:rgba(201,150,42,.03);border:1px solid var(--border);color:var(--muted);font-family:'Cormorant Garamond',serif;font-size:.88rem;cursor:pointer;text-align:left;transition:all .25s;line-height:1.4;font-style:italic;}
.qb:hover{border-color:var(--gold);color:var(--gold2);background:rgba(201,150,42,.06);}

/* INPUT */
.inp-area{flex-shrink:0;padding:16px 20px;border-top:1px solid var(--border);background:rgba(6,4,1,.95);}
.vbars{display:flex;align-items:center;justify-content:center;gap:3px;height:20px;opacity:0;transition:opacity .3s;margin-bottom:10px;}
.vbars.on{opacity:1;}
.vbar{width:3px;border-radius:2px;background:var(--gold);animation:vba .4s ease-in-out infinite;}
.vbar:nth-child(1){height:5px;}.vbar:nth-child(2){height:12px;animation-delay:.07s;}.vbar:nth-child(3){height:18px;animation-delay:.14s;}.vbar:nth-child(4){height:22px;animation-delay:.21s;background:#c84040;}.vbar:nth-child(5){height:18px;animation-delay:.28s;}.vbar:nth-child(6){height:12px;animation-delay:.35s;}.vbar:nth-child(7){height:5px;animation-delay:.42s;}
@keyframes vba{0%,100%{transform:scaleY(.3);}50%{transform:scaleY(1);}}
.inp-row{display:flex;gap:8px;align-items:flex-end;}
.mic-btn{width:46px;height:46px;border:1px solid var(--border);background:transparent;color:var(--muted);font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .25s;flex-shrink:0;clip-path:polygon(8px 0,100% 0,100% calc(100% - 8px),calc(100% - 8px) 100%,0 100%,0 8px);}
.mic-btn:hover{border-color:var(--gold);color:var(--gold);}
.mic-btn.on{border-color:#6699ff;background:rgba(100,150,255,.08);color:#6699ff;}
.inp-wrap{flex:1;position:relative;}
textarea{width:100%;min-height:46px;max-height:120px;padding:12px 46px 12px 16px;background:rgba(201,150,42,.04);border:1px solid var(--border);color:var(--text);font-family:'Cormorant Garamond',serif;font-size:1rem;outline:none;resize:none;transition:border-color .25s;line-height:1.5;}
textarea:focus{border-color:var(--gold);}
textarea::placeholder{color:var(--muted);font-style:italic;font-size:.9rem;}
.send-btn{position:absolute;right:4px;bottom:4px;width:38px;height:38px;background:linear-gradient(135deg,var(--gold),#8b6914);border:none;color:#000;font-family:'Cinzel',serif;font-size:.7rem;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;clip-path:polygon(6px 0,100% 0,100% calc(100% - 6px),calc(100% - 6px) 100%,0 100%,0 6px);transition:opacity .2s;}
.send-btn:disabled{opacity:.3;cursor:not-allowed;}
.stop-btn{width:46px;height:46px;border:1px solid rgba(200,64,64,.2);background:rgba(200,64,64,.05);color:#c84040;font-family:'Share Tech Mono',monospace;font-size:.5rem;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;}

/* ── FOOTER ── */
footer{border-top:1px solid var(--border);padding:24px;text-align:center;background:rgba(13,10,2,.8);}
.footer-quote{font-size:1rem;font-style:italic;color:var(--muted);margin-bottom:8px;}
.footer-sig{font-family:'Cinzel',serif;font-size:.7rem;letter-spacing:4px;color:var(--gold);opacity:.6;}

/* SEARCH INDICATOR */
#searchInd{position:fixed;top:50px;left:50%;transform:translateX(-50%);z-index:999;background:rgba(13,10,2,.96);border:1px solid rgba(201,150,42,.3);color:var(--gold);padding:6px 16px;font-family:'Share Tech Mono',monospace;font-size:.52rem;letter-spacing:2px;display:none;align-items:center;gap:6px;white-space:nowrap;}
#searchInd.on{display:flex;}
#searchInd svg{animation:spin 1s linear infinite;}
@keyframes spin{to{transform:rotate(360deg);}}
#notif{position:fixed;top:50px;left:50%;transform:translateX(-50%);z-index:1000;background:rgba(13,10,2,.98);border:1px solid var(--gold);color:var(--gold);padding:7px 18px;font-family:'Share Tech Mono',monospace;font-size:.52rem;letter-spacing:1px;display:none;max-width:92%;text-align:center;}

/* 4D HOLOGRAPHIC ELEMENTS */
.holo-corner{position:fixed;width:60px;height:60px;pointer-events:none;z-index:4;}
.holo-corner.tl{top:0;left:0;border-top:2px solid rgba(201,150,42,.3);border-left:2px solid rgba(201,150,42,.3);}
.holo-corner.tr{top:0;right:0;border-top:2px solid rgba(201,150,42,.3);border-right:2px solid rgba(201,150,42,.3);}
.holo-corner.bl{bottom:0;left:0;border-bottom:2px solid rgba(201,150,42,.3);border-left:2px solid rgba(201,150,42,.3);}
.holo-corner.br{bottom:0;right:0;border-bottom:2px solid rgba(201,150,42,.3);border-right:2px solid rgba(201,150,42,.3);}
</style>
</head>
<body
