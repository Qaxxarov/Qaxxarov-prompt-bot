"""
Agro AI — Dashboard API (FastAPI)
RESTful endpoints for the web dashboard.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.accounts import accounts
from app.dashboard.auth import create_session, logout, validate_token
from app.memory import memory
from app.ops.discipline import DisciplineTracker
from app.ops.manager import OpsManager
from app.ops.monitor import InstagramMonitor
from app.settings import (
    AI_ENABLED, CHROME_PROFILE_DIR, EXPORT_DIR, MAX_REELS,
    OPENAI_MODEL, TARGET_PROFILE, validate,
)

logger = logging.getLogger("agro_ai.dashboard.api")

# ════════════════════════════════════════════════════════
# APP SETUP
# ════════════════════════════════════════════════════════

app = FastAPI(
    title="Agro AI Dashboard",
    version="2.0.0",
    description="AI Content Operating System for Instagram",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGINS", "http://localhost:8000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ════════════════════════════════════════════════════════
# AUTH DEPENDENCY
# ════════════════════════════════════════════════════════

async def require_auth(authorization: Optional[str] = Header(None)) -> bool:
    """Auth dependency — Bearer token (password or Telegram WebApp)."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token kerak")
    token = authorization.replace("Bearer ", "")
    # Try password-based token first
    if validate_token(token):
        return True
    # Try Telegram WebApp token
    from app.dashboard.telegram_auth import validate_tg_token
    if validate_tg_token(token):
        return True
    raise HTTPException(status_code=401, detail="Token yaroqsiz")


# ════════════════════════════════════════════════════════
# HEALTH CHECK
# ════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    """Health check endpoint (Railway, Docker, monitoring)."""
    return {"status": "ok", "version": "3.0", "bot": True, "dashboard": True}


# ════════════════════════════════════════════════════════
# AUTH ENDPOINTS
# ════════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    password: str


class TelegramAuthRequest(BaseModel):
    init_data: str


@app.post("/api/auth/login")
async def api_login(req: LoginRequest):
    token = create_session(req.password)
    if not token:
        raise HTTPException(status_code=401, detail="Parol noto'g'ri")
    return {"token": token, "expires_in": 86400}


@app.post("/api/auth/telegram")
async def api_telegram_auth(req: TelegramAuthRequest):
    """Telegram WebApp authentication — initData bilan."""
    from app.dashboard.telegram_auth import create_tg_session, validate_webapp_data
    user = validate_webapp_data(req.init_data)
    if not user:
        # Fallback: trust Telegram context in Mini App mode
        # (for development — in production validate hash strictly)
        import json
        try:
            from urllib.parse import parse_qs, unquote
            parsed = parse_qs(req.init_data)
            user_raw = parsed.get("user", [""])[0]
            if user_raw:
                user = json.loads(unquote(user_raw))
        except Exception:
            pass

    if not user:
        raise HTTPException(status_code=401, detail="Telegram auth muvaffaqiyatsiz")

    token = create_tg_session(user)
    if not token:
        raise HTTPException(status_code=403, detail="Ruxsat berilmagan")

    return {
        "token": token,
        "user": user,
        "expires_in": 86400,
    }


@app.post("/api/auth/logout")
async def api_logout(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "")
        logout(token)
    return {"ok": True}



# ════════════════════════════════════════════════════════
# OVERVIEW
# ════════════════════════════════════════════════════════

@app.get("/api/overview", dependencies=[Depends(require_auth)])
async def api_overview(account_id: Optional[str] = None):
    """Dashboard overview — account health, scores, status."""
    acc = accounts.get(account_id) if account_id else accounts.active
    if not acc:
        acc = accounts.active
    monitor = InstagramMonitor(acc.id)
    state = monitor.state
    history = monitor.get_history(30)
    trend = monitor.get_growth_trend(7)
    tracker = DisciplineTracker()
    disc = tracker.compute_discipline_score(state, history)
    issues = validate()

    return {
        "account": {
            "id": acc.id,
            "instagram": acc.instagram,
            "niche": acc.niche,
            "chrome_profile": acc.chrome_profile,
        },
        "state": {
            "followers": state.followers,
            "avg_views": state.avg_views,
            "avg_er": state.avg_er,
            "max_views": state.max_views,
            "viral_count": state.viral_count,
            "posted_today": state.posted_today,
            "posting_streak": state.posting_streak,
            "missed_days": state.missed_days,
            "last_scan_hours_ago": round(state.hours_since_scan, 1),
            "is_stale": state.is_stale,
        },
        "discipline": disc,
        "trend": trend,
        "system": {
            "ai_enabled": AI_ENABLED,
            "ai_model": OPENAI_MODEL if AI_ENABLED else None,
            "chrome_profile": CHROME_PROFILE_DIR,
            "target": TARGET_PROFILE,
            "max_reels": MAX_REELS,
            "issues": issues,
        },
    }


# ════════════════════════════════════════════════════════
# ANALYTICS
# ════════════════════════════════════════════════════════

@app.get("/api/analytics", dependencies=[Depends(require_auth)])
async def api_analytics(account_id: Optional[str] = None):
    """Analytics data — history, trends, charts."""
    acc = accounts.get(account_id) if account_id else accounts.active
    if not acc:
        acc = accounts.active
    monitor = InstagramMonitor(acc.id)
    history = monitor.get_history(30)
    state = monitor.state

    # Recent reels
    reels = []
    for r in state.recent_reels[:10]:
        reels.append({
            "url": r.url,
            "caption": r.caption[:80],
            "views": r.views,
            "likes": r.likes,
            "comments": r.comments,
            "er": r.engagement_rate,
            "posted_at": r.posted_at,
        })

    return {
        "history": history,
        "recent_reels": reels,
        "current": {
            "followers": state.followers,
            "avg_views": state.avg_views,
            "avg_er": state.avg_er,
            "total_reels": state.total_reels,
        },
    }


# ════════════════════════════════════════════════════════
# MEMORY
# ════════════════════════════════════════════════════════

@app.get("/api/memory", dependencies=[Depends(require_auth)])
async def api_memory():
    """Memory system data."""
    acc = accounts.active
    stats = memory.get_stats(acc.id)
    top_hooks = memory.get_top_hooks(acc.id, limit=10)
    top_stories = memory.get_best_story_structures(acc.id, limit=5)
    patterns = memory.get_best_patterns(acc.id, "pattern", limit=10)

    return {
        "stats": stats,
        "top_hooks": [{"content": h.content[:100], "score": h.score, "source": h.source} for h in top_hooks],
        "top_stories": [{"content": s.content[:100], "score": s.score} for s in top_stories],
        "patterns": [{"content": p.content[:100], "score": p.score, "tags": p.tags} for p in patterns],
    }


# ════════════════════════════════════════════════════════
# OPS
# ════════════════════════════════════════════════════════

@app.get("/api/ops/status", dependencies=[Depends(require_auth)])
async def api_ops_status():
    """Ops manager quick status."""
    ops = OpsManager()
    return {"status": ops.quick_status()}


@app.post("/api/ops/morning", dependencies=[Depends(require_auth)])
async def api_ops_morning():
    """Trigger morning briefing."""
    ops = OpsManager()
    text = await ops.morning_briefing()
    return {"briefing": text}


@app.post("/api/ops/evening", dependencies=[Depends(require_auth)])
async def api_ops_evening():
    """Trigger evening report (includes scan)."""
    ops = OpsManager()
    loop = asyncio.get_event_loop()
    monitor = InstagramMonitor(accounts.active.id)
    await loop.run_in_executor(None, monitor.scan_now)
    ops = OpsManager()  # Refresh
    text = await ops.evening_report()
    return {"report": text}


# ════════════════════════════════════════════════════════
# ACCOUNTS
# ════════════════════════════════════════════════════════

@app.get("/api/accounts", dependencies=[Depends(require_auth)])
async def api_accounts():
    """All accounts."""
    all_accs = accounts.all_accounts
    return {
        "active": accounts.active.id,
        "accounts": [
            {
                "id": a.id,
                "instagram": a.instagram,
                "niche": a.niche,
                "chrome_profile": a.chrome_profile,
                "active": a.active,
            }
            for a in all_accs
        ],
    }


@app.post("/api/accounts/switch/{account_id}", dependencies=[Depends(require_auth)])
async def api_switch_account(account_id: str):
    if accounts.switch(account_id):
        return {"ok": True, "active": account_id}
    raise HTTPException(status_code=404, detail="Akkaunt topilmadi")


# ════════════════════════════════════════════════════════
# EXPORTS
# ════════════════════════════════════════════════════════

@app.get("/api/exports", dependencies=[Depends(require_auth)])
async def api_exports():
    """List available export files."""
    export_path = str(EXPORT_DIR)
    if not os.path.isdir(export_path):
        return {"files": []}

    files = []
    for f in sorted(os.listdir(export_path), reverse=True)[:20]:
        fpath = os.path.join(export_path, f)
        files.append({
            "name": f,
            "size": os.path.getsize(fpath),
            "type": f.split(".")[-1],
        })
    return {"files": files}


@app.get("/api/exports/download/{filename}", dependencies=[Depends(require_auth)])
async def api_download(filename: str):
    """Download an export file."""
    fpath = EXPORT_DIR / filename
    if not fpath.exists():
        raise HTTPException(status_code=404, detail="Fayl topilmadi")
    return FileResponse(str(fpath), filename=filename)


# ════════════════════════════════════════════════════════
# AI ENGINES
# ════════════════════════════════════════════════════════

class AIRequest(BaseModel):
    engine: str  # hooks, storytelling, veo, audience, viral_score
    action: str
    params: dict = {}


@app.post("/api/ai/generate", dependencies=[Depends(require_auth)])
async def api_ai_generate(req: AIRequest):
    """Run an AI engine."""
    acc = accounts.active

    if req.engine == "hooks":
        from app.ai.hooks import HookEngine
        engine = HookEngine(acc)
        result = await engine.generate_hooks(
            category=req.params.get("category", "viral"),
            count=req.params.get("count", 10),
        )
    elif req.engine == "storytelling":
        from app.ai.storytelling import StorytellingEngine
        engine = StorytellingEngine(acc)
        result = await engine.generate_story(
            arc_type=req.params.get("arc", "transformation"),
        )
    elif req.engine == "veo":
        from app.ai.veo import VeoEngine
        engine = VeoEngine(acc)
        result = await engine.generate_scene_prompt(
            scene_type=req.params.get("scene", "golden_harvest"),
            style=req.params.get("style", "cinematic"),
        )
    elif req.engine == "audience":
        from app.ai.audience import AudienceEngine
        engine = AudienceEngine(acc)
        result = await engine.analyze_audience()
    elif req.engine == "viral_score":
        from app.ai.viral_score import ViralScoreEngine
        engine = ViralScoreEngine(acc)
        monitor = InstagramMonitor(acc.id)
        state = monitor.state
        # Need stats from session — use basic computation
        result = str(engine.compute_score({}))
    else:
        raise HTTPException(status_code=400, detail=f"Noma'lum engine: {req.engine}")

    return {"result": result, "engine": req.engine}


# ════════════════════════════════════════════════════════
# 📅 CALENDAR
# ════════════════════════════════════════════════════════

class CalendarEventRequest(BaseModel):
    title: str
    date: str
    time: str = "19:00"
    status: str = "planned"  # planned, posted, missed
    notes: str = ""


@app.get("/api/calendar", dependencies=[Depends(require_auth)])
async def api_calendar(start: str = "", end: str = ""):
    """Oylik kontent rejasi — calendar events."""
    import json as _json
    cal_file = Path(__file__).resolve().parent.parent.parent / "data" / "calendar.json"
    if not cal_file.exists():
        return {"events": []}
    try:
        with open(cal_file, "r", encoding="utf-8") as f:
            data = _json.load(f)
        return {"events": data.get("events", [])}
    except Exception:
        return {"events": []}


@app.post("/api/calendar/event", dependencies=[Depends(require_auth)])
async def api_calendar_add(req: CalendarEventRequest):
    """Yangi calendar event qo'shish."""
    import json as _json
    import uuid
    cal_file = Path(__file__).resolve().parent.parent.parent / "data" / "calendar.json"
    cal_file.parent.mkdir(parents=True, exist_ok=True)

    data = {"events": []}
    if cal_file.exists():
        try:
            with open(cal_file, "r", encoding="utf-8") as f:
                data = _json.load(f)
        except Exception:
            pass

    event = {
        "id": uuid.uuid4().hex[:8],
        "title": req.title,
        "date": req.date,
        "time": req.time,
        "status": req.status,
        "notes": req.notes,
    }
    data.setdefault("events", []).append(event)

    with open(cal_file, "w", encoding="utf-8") as f:
        _json.dump(data, f, ensure_ascii=False, indent=2)

    return {"ok": True, "event": event}


@app.put("/api/calendar/event/{event_id}", dependencies=[Depends(require_auth)])
async def api_calendar_update(event_id: str, req: CalendarEventRequest):
    """Calendar event tahrirlash."""
    import json as _json
    cal_file = Path(__file__).resolve().parent.parent.parent / "data" / "calendar.json"
    if not cal_file.exists():
        raise HTTPException(status_code=404, detail="Event topilmadi")

    with open(cal_file, "r", encoding="utf-8") as f:
        data = _json.load(f)

    for event in data.get("events", []):
        if event.get("id") == event_id:
            event["title"] = req.title
            event["date"] = req.date
            event["time"] = req.time
            event["status"] = req.status
            event["notes"] = req.notes
            break
    else:
        raise HTTPException(status_code=404, detail="Event topilmadi")

    with open(cal_file, "w", encoding="utf-8") as f:
        _json.dump(data, f, ensure_ascii=False, indent=2)

    return {"ok": True}


@app.delete("/api/calendar/event/{event_id}", dependencies=[Depends(require_auth)])
async def api_calendar_delete(event_id: str):
    """Calendar event o'chirish."""
    import json as _json
    cal_file = Path(__file__).resolve().parent.parent.parent / "data" / "calendar.json"
    if not cal_file.exists():
        raise HTTPException(status_code=404, detail="Event topilmadi")

    with open(cal_file, "r", encoding="utf-8") as f:
        data = _json.load(f)

    events = data.get("events", [])
    data["events"] = [e for e in events if e.get("id") != event_id]

    with open(cal_file, "w", encoding="utf-8") as f:
        _json.dump(data, f, ensure_ascii=False, indent=2)

    return {"ok": True}


@app.get("/calendar")
async def serve_calendar():
    """Serve calendar page."""
    cal_path = STATIC_DIR / "calendar.html"
    if cal_path.exists():
        return FileResponse(str(cal_path))
    return HTMLResponse("<h1>Calendar</h1><p>calendar.html topilmadi</p>")


# ════════════════════════════════════════════════════════
# FRONTEND SERVE
# ════════════════════════════════════════════════════════

@app.get("/")
async def serve_dashboard():
    """Serve the main dashboard HTML."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return HTMLResponse("<h1>Agro AI Dashboard</h1><p>static/index.html topilmadi</p>")


@app.get("/miniapp")
async def serve_miniapp():
    """Serve Telegram Mini App optimized frontend."""
    miniapp_path = STATIC_DIR / "miniapp.html"
    if miniapp_path.exists():
        return FileResponse(str(miniapp_path))
    # Fallback to main dashboard
    return await serve_dashboard()
