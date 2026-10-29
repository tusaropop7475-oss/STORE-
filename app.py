#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ FLASH PREMIUM STORE v15 — VERCEL-READY EDITION (MONGO DNS FIXED) ⚡
"""

import os, sys, json, time, secrets, string, socket, re, csv, io, random
from datetime import datetime, timedelta, timezone
from functools import wraps

# ================= IST TIMEZONE =================
try:
    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")
except ImportError:
    IST = timezone(timedelta(hours=5, minutes=30))

def now_ist():
    try: return datetime.now(IST)
    except: return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30)))

def now_str(): return now_ist().isoformat()

def now_str_naive():
    return now_ist().strftime("%Y-%m-%d %H:%M:%S")

def fmt(iso_str):
    if not iso_str: return '-'
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None: dt = dt.replace(tzinfo=IST)
        else: dt = dt.astimezone(IST)
        return dt.strftime("%d %b %Y, %I:%M %p IST")
    except: return str(iso_str)

# ================= SMALL CAPS =================
_SC_MAP = str.maketrans(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘQʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘQʀꜱᴛᴜᴠᴡxʏᴢ"
)
def sc(text): return str(text).translate(_SC_MAP)

# ================= IPv4 FORCE =================
_og = socket.getaddrinfo
def _ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return _og(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = _ipv4

# ================= IMPORTS =================
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, Response, send_file
from werkzeug.utils import secure_filename
import requests as rq
import psutil

# ---- MONGO DNS FIX START ----
try:
    import dns.resolver
    # Vercel-এ DNS রিজলভ ঠিক করতে Google DNS ব্যবহার করা হলো
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4', '1.1.1.1']
except ImportError:
    print("[!] dnspython missing")

from pymongo import MongoClient
from bson.objectid import ObjectId
# ---- MONGO DNS FIX END ----

# ================= CONFIG =================
MONGO_URI = "mongodb+srv://tusaropop7475_db_user:zY4MJmAQUaf1nZGd@cluster0.hu0hqpt.mongodb.net/?appName=Cluster0"
DB_NAME = "attack_bot"
BOT_TOKEN = "8682709779:AAF6EkmBF_y0bc2iFwKZ_eEQ20HP_HyCuCg"
BOT_USER = "APROLXDDOSBOT"
CHANNEL = "VIPCHANEEL01"
POWER_BY = "@FLASH_OWERR"
FAM_KEY = "fam_5fcfeea57257135beedda3a96909a0ca98be7cab"
FAM_CREATE = "https://famgateway.in/api/create-order"
FAM_VERIFY = "https://famgateway.in/api/verify-order.php"
ADMIN_U = "FLASH"
ADMIN_P = "FLASH123"
PORT = int(os.environ.get("PORT", 5000))
HOST = "0.0.0.0"
SECRET = os.environ.get("FLASK_SECRET", "flash_premium_v15_secret_key_change_me_please")
BG_IMG = "https://host.hemnthapp.shop/uploads/Screenshot_20260921-023919.jpg"
LOGO_IMG = "https://i.ibb.co/ccZvH6Sc/Screenshot-20260921-023919.jpg"
OWNER_TG_ID = "8605900206"
DEFAULT_MAX_TIME = 400
DEFAULT_MAX_CONC = 4
DEFAULT_COOLDOWN = 5

VIP_USERS = {"baby"}
HELPERS = {}

# ================= COLORS =================
C_PRIMARY   = "#FFD700"
C_SECONDARY = "#00FFFF"
C_ACCENT    = "#FF0055"
C_SUCCESS   = "#00FF88"
C_WARN      = "#FFA500"
C_DANGER    = "#FF0000"
C_GRAD_MAIN = "linear-gradient(135deg,#FFD700,#00FFFF,#FF0055)"
C_GRAD_BTN  = "linear-gradient(135deg,#FFD700,#FF0055)"
C_GRAD_ALT  = "linear-gradient(135deg,#00FFFF,#FFD700)"

# ================= MEDIA (Vercel /tmp) =================
CHAT_MEDIA_DIR = "/tmp/chat_media"
try:
    os.makedirs(CHAT_MEDIA_DIR, exist_ok=True)
except Exception as e:
    print(f"[!] Media dir: {e}")

MAX_MEDIA_MB = 4
ALLOWED_MEDIA = {"jpg","jpeg","png","gif","webp","bmp","mp3","m4a","wav","ogg","oga","opus",
    "mp4","webm","mov","mkv","pdf","doc","docx","xls","xlsx","ppt","pptx","txt","zip","rar"}

app = Flask(__name__)
app.secret_key = SECRET
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

# ================= MONGO (FIXED CONNECTION) =================
def connect():
    for i in range(3):
        try:
            # টাইমআউট বাড়ানো হলো এবং TLS অ্যালাউ করা হলো Vercel-এর জন্য
            c = MongoClient(
                MONGO_URI, 
                serverSelectionTimeoutMS=15000, 
                connectTimeoutMS=15000,
                socketTimeoutMS=15000,
                maxPoolSize=10,
                tlsAllowInvalidCertificates=True, 
                retryWrites=True
            )
            c.server_info()
            print("[OK] MongoDB connected successfully ✅")
            return c
        except Exception as e:
            print(f"[!] Mongo Error {i+1}: {str(e)[:150]}")
            time.sleep(3)
    return None

cli = connect()
if not cli:
    print("[X] Mongo failed")
    cli = None

db = cli[DB_NAME] if cli else None

keys_col = db["keys"] if db else None
plans_col = db["user_plans"] if db else None
prods_col = db["store_products"] if db else None
orders_col = db["store_orders"] if db else None
settings_col = db["settings"] if db else None
logs_col = db["admin_logs"] if db else None
users_col = db["store_users"] if db else None
known_col = db["known_users"] if db else None
bans_col = db["banned_users"] if db else None
chat_col = db["live_chat"] if db else None
ratings_col = db["order_ratings"] if db else None
coupons_col = db["coupons"] if db else None
wallet_col = db["wallet_txns"] if db else None
faqs_col = db["faqs"] if db else None
testimonials_col = db["testimonials"] if db else None
notif_col = db["notifications"] if db else None
activity_col = db["activity_log"] if db else None
visits_col = db["visitor_log"] if db else None
commands_col = db["command_log"] if db else None
helpers_col = db["helpers_collection"] if db else None
wishlist_col = db["wishlist"] if db else None
comments_col = db["advanced_comments"] if db else None
premium_locks_col = db["premium_locks"] if db else None
achievements_col = db["user_achievements"] if db else None
audit_trail_col = db["audit_trail"] if db else None
feature_flags_col = db["feature_flags"] if db else None
referrals_col = db["referral_tracking"] if db else None
daily_stats_col = db["daily_stats"] if db else None
templates_col = db["chat_templates"] if db else None
recently_viewed_col = db["recently_viewed"] if db else None

# ================= SAFE DB HELPER =================
def safe_count(col, q=None):
    try:
        return col.count_documents(q or {}) if col else 0
    except: return 0

def safe_find(col, q=None, limit=None, sort=None):
    try:
        if not col: return []
        cur = col.find(q or {})
        if sort: cur = cur.sort(sort)
        if limit: cur = cur.limit(limit)
        return list(cur)
    except: return []

def safe_find_one(col, q):
    try:
        return col.find_one(q) if col else None
    except: return None

def safe_insert(col, doc):
    try:
        return col.insert_one(doc) if col else None
    except Exception as e:
        print(f"[insert err] {e}"); return None

def safe_update(col, q, u, upsert=False):
    try:
        return col.update_one(q, u, upsert=upsert) if col else None
    except Exception as e:
        print(f"[update err] {e}"); return None

def safe_delete(col, q):
    try:
        return col.delete_one(q) if col else None
    except: return None

# ================= AUTO-MIGRATE =================
def migrate_old_keys():
    try:
        if not keys_col: return
        fixed = 0
        for key in keys_col.find({"expires": {"$regex": "T"}}):
            try:
                dt = datetime.fromisoformat(key["expires"])
                keys_col.update_one({"_id": key["_id"]},
                    {"$set": {"expires": dt.strftime("%Y-%m-%d %H:%M:%S")}})
                fixed += 1
            except: pass
        if fixed > 0:
            print(f"[OK] Auto-migrated {fixed} old keys ✅")
    except: pass

migrate_old_keys()

# ================= HELPERS =================
def setting(k, d=None):
    doc = safe_find_one(settings_col, {}) or {}
    return doc.get(k, d)

def tg_send(cid, txt, pm="HTML"):
    if not cid: return False
    try:
        r = rq.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={"chat_id":cid,"text":txt,"parse_mode":pm,
                          "disable_web_page_preview":True}, timeout=8)
        return r.status_code == 200 and r.json().get("ok", False)
    except: return False

def notify_admin(title, body, typ="info"):
    try:
        owner = str(setting("owner_telegram_id", OWNER_TG_ID) or "").strip()
        if not owner: return
        icons = {"info":"ℹ️","success":"✅","warning":"⚠️","alert":"🚨","order":"💰",
                 "visit":"👁️","command":"⚡","chat":"💬","user":"👤","key":"🔑",
                 "payment":"💳","vip":"👶"}
        icon = icons.get(typ, "ℹ️")
        ts = now_ist().strftime("%d %b %Y, %I:%M:%S %p IST")
        msg = (f"{icon} <b>{sc(title)}</b>\n"
               f"━━━━━━━━━━━━━━━━━━━━\n"
               f"{body}\n"
               f"━━━━━━━━━━━━━━━━━━━━\n"
               f"🕐 <code>{ts}</code>\n"
               f"⚡ <b>FLASH PREMIUM v15</b>")
        try: tg_send(owner, msg)
        except: pass
    except: pass

def log_adm(action, det=""):
    admin = session.get("username","admin")
    safe_insert(logs_col, {"timestamp": now_str(),"admin_id": admin,
                           "action": action,"details": det})
    try:
        ts = now_ist().strftime("%d %b %Y, %I:%M:%S %p IST")
        ip = (request.headers.get("X-Forwarded-For", request.remote_addr or "?")
              .split(",")[0].strip()) if request else "?"
        body = (f"👤 <b>{sc('admin')}:</b> <code>{admin}</code>\n"
                f"🎯 <b>{sc('action')}:</b> <code>{action}</code>\n"
                f"📝 <b>{sc('details')}:</b> {det[:200] if det else '-'}\n"
                f"🌐 <b>IP:</b> <code>{ip}</code>\n"
                f"🕐 <code>{ts}</code>")
        notify_admin("Admin Command", body, "command")
    except: pass

def log_activity(uid, act, det=""):
    safe_insert(activity_col, {"user_id": str(uid), "action": act,
                               "details": det, "timestamp": now_str()})

def push_notif(uid, title, body, typ="info"):
    safe_insert(notif_col, {"user_id": str(uid), "title": title, "body": body,
        "type": typ, "read": False, "time": now_str()})

def gen_code(prefix="", length=12):
    c = string.ascii_uppercase + string.digits
    rnd = ''.join(secrets.choice(c) for _ in range(length))
    return f"{prefix.upper()}-{rnd}" if prefix else rnd

def get_balance(uid):
    txns = safe_find(wallet_col, {"user_id": str(uid)})
    bal = 0
    for t in txns:
        if t.get("type") == "credit": bal += t.get("amount", 0)
        elif t.get("type") == "debit": bal -= t.get("amount", 0)
    return round(bal, 2)

def get_tier(spent):
    if spent >= 5000: return ("💎 DIAMOND", "#67e8f9")
    if spent >= 2000: return ("🏆 PLATINUM", "#e5e7eb")
    if spent >= 1000: return ("👑 VIP", "#ec4899")
    if spent >= 500: return ("🥇 GOLD", "#8b5cf6")
    if spent >= 100: return ("🥈 SILVER", "#06b6d4")
    return ("🥉 BRONZE", "#f59e0b")

def is_vip_user(uid):
    return str(uid).lower() in VIP_USERS

def get_badges(uid):
    badges = []
    orders = safe_find(orders_col, {"telegram_id": str(uid), "status": "success"})
    total = len(orders)
    spent = sum(o.get("amount", 0) for o in orders)
    if is_vip_user(uid): badges.append({"name": "👶 VIP MEMBER", "icon": "👶", "color": C_ACCENT})
    if total >= 1: badges.append({"name": "🎉 FIRST PURCHASE", "icon": "🎉", "color": C_SUCCESS})
    if total >= 5: badges.append({"name": "⭐ REGULAR", "icon": "⭐", "color": C_SECONDARY})
    if total >= 10: badges.append({"name": "👑 LOYAL", "icon": "👑", "color": C_ACCENT})
    if total >= 25: badges.append({"name": "🏆 CHAMPION", "icon": "🏆", "color": C_WARN})
    if spent >= 500: badges.append({"name": "💰 BIG SPENDER", "icon": "💰", "color": C_ACCENT})
    if spent >= 2000: badges.append({"name": "💎 HIGH ROLLER", "icon": "💎", "color": C_SECONDARY})
    if get_balance(uid) > 500: badges.append({"name": "💳 WALLET HOLDER", "icon": "💳", "color": C_SUCCESS})
    if total >= 3 and spent >= 250: badges.append({"name": "🔥 PREMIUM", "icon": "🔥", "color": C_DANGER})
    if total >= 50: badges.append({"name": "🌟 LEGEND", "icon": "🌟", "color": C_WARN})
    return badges

# ================= ADVANCED COMMENTS =================
def add_admin_comment(entity_type, entity_id, comment, admin=None, tags=None, priority="normal"):
    try:
        doc = {
            "entity_type": entity_type, "entity_id": str(entity_id),
            "comment": comment.strip()[:2000],
            "admin": admin or session.get("username", "system"),
            "tags": tags or [], "priority": priority, "pinned": False,
            "created_at": now_str(), "updated_at": now_str(),
        }
        r = safe_insert(comments_col, doc)
        safe_insert(audit_trail_col, {
            "action": "add_comment", "entity": f"{entity_type}:{entity_id}",
            "admin": doc["admin"], "time": now_str(),
            "ip": request.remote_addr if request else "-"
        })
        return str(r.inserted_id) if r else None
    except Exception as e:
        print(f"[!] comment error: {e}"); return None

def get_admin_comments(entity_type, entity_id, limit=50):
    try:
        docs = safe_find(comments_col,
            {"entity_type": entity_type, "entity_id": str(entity_id)},
            limit=limit, sort=[("pinned", -1), ("created_at", -1)])
        for d in docs: d["_id"] = str(d["_id"])
        return docs
    except: return []

# ================= PREMIUM LOCKS =================
def user_has_purchased(uid):
    return safe_count(orders_col, {"telegram_id": str(uid), "status": "success"}) > 0

def get_user_locks(uid):
    purchased = user_has_purchased(uid)
    result = {
        "is_premium": purchased, "is_vip": is_vip_user(uid),
        "locks": {
            "wheel": not purchased and not is_vip_user(uid),
            "referral_bonus": not purchased, "premium_support": not purchased,
            "advanced_stats": not purchased, "priority_delivery": not purchased,
            "exclusive_keys": not purchased, "daily_streak_bonus": not purchased,
            "advanced_badges": not purchased,
        },
        "unlock_progress": 0, "next_unlock": None,
    }
    if purchased or is_vip_user(uid):
        result["locks"] = {k: False for k in result["locks"]}
        result["unlock_progress"] = 100
    else:
        total_orders = safe_count(orders_col, {"telegram_id": str(uid)})
        result["unlock_progress"] = min(100, total_orders * 25)
        result["next_unlock"] = "First Purchase Unlocks All Premium Features"
    return result

def create_premium_lock(uid, feature, reason=""):
    try:
        premium_locks_col.update_one(
            {"user_id": str(uid), "feature": feature},
            {"$set": {"active": True, "reason": reason, "created_at": now_str()}},
            upsert=True
        )
    except: pass

def remove_premium_lock(uid, feature):
    try:
        premium_locks_col.update_one(
            {"user_id": str(uid), "feature": feature},
            {"$set": {"active": False, "removed_at": now_str()}}
        )
    except: pass

# ================= INIT =================
def init_prods():
    try:
        if safe_count(prods_col) == 0:
            prods = [
                {"_id":"1hr","name":"⚡ 1 Hour Key","duration":"⏱️ 1 Hour","hours":1,"price":30,"active":True,"order":1,"popular":False,"category":"BASIC","featured":False},
                {"_id":"6hr","name":"⚡ 6 Hours Key","duration":"⏱️ 6 Hours","hours":6,"price":50,"active":True,"order":2,"popular":False,"category":"BASIC","featured":False},
                {"_id":"12hr","name":"🔥 12 Hours Key","duration":"⏱️ 12 Hours","hours":12,"price":80,"active":True,"order":3,"popular":True,"category":"PRO","featured":True},
                {"_id":"1d","name":"🔥 1 Day Key","duration":"📅 1 Day","hours":24,"price":100,"active":True,"order":4,"popular":True,"category":"PRO","featured":True},
                {"_id":"2d","name":"⭐ 2 Days Key","duration":"📅 2 Days","hours":48,"price":220,"active":True,"order":5,"popular":False,"category":"PRO","featured":False},
                {"_id":"3d","name":"⭐ 3 Days Key","duration":"📅 3 Days","hours":72,"price":350,"active":True,"order":6,"popular":False,"category":"VIP","featured":False},
                {"_id":"7d","name":"💎 7 Days Key","duration":"📅 7 Days","hours":168,"price":750,"active":True,"order":7,"popular":True,"category":"VIP","featured":True},
                {"_id":"30d","name":"👑 30 Days Key","duration":"📅 30 Days","hours":720,"price":3000,"active":True,"order":8,"popular":True,"category":"VIP","featured":False},
            ]
            prods_col.insert_many(prods)
            print("[OK] Products initialized ✅")
    except Exception as e:
        print(f"[init_prods] {e}")
init_prods()

def init_faqs():
    try:
        if safe_count(faqs_col) == 0:
            faqs_col.insert_many([
                {"q":"🎁 How do I receive my key?","a":"After successful payment, your key is instantly delivered to your Telegram DM.","order":1},
                {"q":"🔑 How do I redeem my key?","a":"Open our Telegram bot and send /redeem YOUR_KEY.","order":2},
                {"q":"⚠️ What if my payment fails?","a":"Our system auto-verifies every payment. Contact support if not delivered in 10 min.","order":3},
                {"q":"💸 Can I get a refund?","a":"Digital keys are non-refundable once delivered.","order":4},
            ])
    except: pass
init_faqs()

def init_testimonials():
    try:
        if safe_count(testimonials_col) == 0:
            testimonials_col.insert_many([
                {"text":"⚡ Very fast delivery, got the key instantly!","who":"Rahul K.","stars":5,"order":1},
                {"text":"💎 Premium quality keys, no lag at all.","who":"Amit S.","stars":5,"order":2},
                {"text":"🎯 Support team is very helpful.","who":"Priya M.","stars":5,"order":3},
            ])
    except: pass
init_testimonials()

# ================= FAMGATEWAY =================
def fam_key(): return setting("famgateway_api_key", FAM_KEY)

def fam_create(amount, name="", email="", phone="", redirect="", webhook=""):
    try:
        k = fam_key()
        p = {"api_key":k,"amount":float(amount),"customer_name":name or "Customer",
             "customer_email":email or "","customer_phone":phone or "",
             "redirect_url":redirect or "","webhook_url":webhook or ""}
        r = rq.post(FAM_CREATE, json=p,
            headers={"Content-Type":"application/json","X-Api-Key":k}, timeout=15)
        if r.status_code == 200:
            d = r.json()
            if d.get("status") == "success":
                return {"success":True,"data":d.get("data",{})}
            return {"success":False,"error":d.get("message","Gateway error")}
        return {"success":False,"error":r.text[:250]}
    except Exception as e: return {"success":False,"error":str(e)}

def fam_verify(oid):
    try:
        r = rq.get(FAM_VERIFY, params={"api_key":fam_key(),"order_id":oid}, timeout=15)
        if r.status_code == 200: return {"success":True,"data":r.json()}
        return {"success":False,"error":r.text[:200]}
    except Exception as e: return {"success":False,"error":str(e)}

def tg_send_media(chat_id, file_path, media_type="document", caption=""):
    if not chat_id: return False
    endpoints = {"photo":("sendPhoto","photo"),"voice":("sendVoice","voice"),
                 "audio":("sendAudio","audio"),"video":("sendVideo","video"),
                 "document":("sendDocument","document")}
    ep, field = endpoints.get(media_type, ("sendDocument","document"))
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{ep}"
    try:
        with open(file_path, "rb") as f:
            files = {field: f}; data = {"chat_id": chat_id}
            if caption:
                data["caption"] = caption[:1024]; data["parse_mode"] = "HTML"
            r = rq.post(url, files=files, data=data, timeout=30)
        return r.status_code == 200 and r.json().get("ok", False)
    except: return False

def detect_media_type(ext):
    ext = ext.lower().lstrip(".")
    if ext in {"jpg","jpeg","png","gif","webp","bmp"}: return "photo"
    if ext in {"ogg","oga","opus"}: return "voice"
    if ext in {"mp3","m4a","wav"}: return "audio"
    if ext in {"mp4","webm","mov","mkv"}: return "video"
    return "document"

# ================= AUTH =================
def adm_req(f):
    @wraps(f)
    def d(*a,**k):
        if not session.get("adm"):
            if request.path.startswith("/api/"):
                return jsonify({"error":"Unauthorized"}),401
            return redirect(url_for("login"))
        return f(*a,**k)
    return d

def usr_req(f):
    @wraps(f)
    def d(*a,**k):
        if not session.get("usr"):
            if request.path.startswith("/api/"):
                return jsonify({"error":"Unauthorized"}),401
            return redirect(url_for("usr_login"))
        return f(*a,**k)
    return d

def helper_req(f):
    @wraps(f)
    def d(*a,**k):
        if not session.get("helper") and not session.get("adm"):
            if request.path.startswith("/api/"):
                return jsonify({"error":"Unauthorized"}),401
            return redirect(url_for("helper_login"))
        return f(*a,**k)
    return d

# ================= VISITOR TRACKING =================
_seen_visitors = {}
_seen_lock = __import__("threading").Lock()

@app.before_request
def track_visitor():
    try:
        if request.path.startswith("/static"): return
        if request.path.startswith("/chat_media"): return
        if request.path.startswith("/api/"): return
        if not db: return
        ip = (request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
              .split(",")[0].strip())
        if ip in ("127.0.0.1","localhost","unknown","::1"): return
        now = time.time()
        with _seen_lock:
            last = _seen_visitors.get(ip, 0)
            if now - last < 600: return
            _seen_visitors[ip] = now
        ua = request.headers.get("User-Agent", "Unknown")[:120]
        path = request.path
        device = "📱 Mobile" if any(x in ua.lower() for x in ["mobile","android","iphone"]) else "💻 Desktop"
        safe_insert(visits_col, {"ip": ip, "path": path, "user_agent": ua,
            "device": device, "time": now_str()})
        ts = now_ist().strftime("%d %b %Y, %I:%M:%S %p IST")
        body = (f"🌐 <b>{sc('ip')}:</b> <code>{ip}</code>\n"
                f"📍 <b>{sc('path')}:</b> <code>{path}</code>\n"
                f"{device}\n"
                f"🕐 <code>{ts}</code>")
        notify_admin("New Visitor", body, "visit")
    except: pass

@app.before_request
def check_maintenance():
    if setting("maintenance_mode", False) and not session.get("adm"):
        allowed = ["/login", "/api/", "/static", "/chat_media/"]
        if not any(request.path.startswith(p) for p in allowed):
            return f"""<!DOCTYPE html><html><head><title>🔧 MAINTENANCE</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{{font-family:sans-serif;background:#0a0a0f;color:#fff;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;text-align:center;padding:20px}}
.box{{background:rgba(15,15,25,.9);border:1px solid {C_PRIMARY}66;border-radius:24px;padding:50px 40px;max-width:500px;box-shadow:0 0 50px {C_PRIMARY}33}}
h1{{font-size:64px;margin:0}}
h2{{font-size:28px;font-weight:900;letter-spacing:3px;background:{C_GRAD_MAIN};-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:16px 0}}</style></head><body>
<div class="box"><h1>🔧⚙️🔨</h1><h2>UNDER MAINTENANCE</h2>
<p style="color:rgba(255,255,255,.7)">⚡ Premium store is being upgraded. ⚡</p></div></body></html>""", 503

# ================= LOGIN =================
LOGIN_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>🔐 ADMIN LOGIN · FLASH PREMIUM v15</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;background:#05050A;overflow:hidden;position:relative}
body::before{content:'';position:absolute;inset:0;background:radial-gradient(circle at 20% 20%,#FFD70015,transparent 40%),radial-gradient(circle at 80% 80%,#00FFFF15,transparent 40%),radial-gradient(circle at 50% 50%,#FF005515,transparent 50%);animation:bg 15s infinite}
@keyframes bg{0%,100%{transform:scale(1)}50%{transform:scale(1.15)}}
.box{position:relative;z-index:2;background:rgba(10,10,15,.92);backdrop-filter:blur(30px);border:1px solid #FFD70055;border-radius:24px;padding:46px 40px;width:100%;max-width:440px;box-shadow:0 30px 80px rgba(0,0,0,.8), 0 0 40px #FFD70022}
.logo{text-align:center;margin-bottom:32px}
.logo img{width:90px;height:90px;border-radius:50%;border:3px solid #FFD700;box-shadow:0 0 40px #FFD700cc;object-fit:cover;animation:fl 3s infinite}
@keyframes fl{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-12px) scale(1.05)}}
.logo h1{font-size:22px;font-weight:900;margin-top:14px;letter-spacing:3px;text-transform:uppercase;background:linear-gradient(135deg,#FFD700,#00FFFF,#FF0055);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.logo p{color:rgba(255,255,255,.5);font-size:10px;margin-top:8px;letter-spacing:4px;text-transform:uppercase;font-weight:800}
.fg{margin-bottom:16px}
.fg label{display:block;color:rgba(255,255,255,.8);font-size:11px;font-weight:800;margin-bottom:6px;letter-spacing:1.5px;text-transform:uppercase}
.fg input{width:100%;padding:15px 16px;background:rgba(0,0,0,.4);border:1px solid #FFD70044;border-radius:12px;color:#fff;font-size:14px;font-family:inherit;outline:none;transition:.3s}
.fg input:focus{border-color:#FFD700;box-shadow:0 0 15px #FFD70044;background:#FFD7000a}
.btn{width:100%;padding:15px;background:rgba(255,215,0,.05);border:1px solid #FFD700;border-radius:12px;color:#FFD700;font-size:14px;font-weight:900;cursor:pointer;letter-spacing:2px;text-transform:uppercase;margin-top:6px;font-family:inherit;transition:.3s;text-shadow: 0 0 10px #FFD70088;}
.btn:hover{background:#FFD700;color:#000;box-shadow:0 0 20px #FFD70088;text-shadow:none}
.err{background:rgba(255,0,0,.15);border:1px solid rgba(255,0,0,.35);color:#ff4444;padding:12px;border-radius:12px;font-size:12px;margin-bottom:18px;text-align:center;font-weight:700;text-transform:uppercase}
.link{text-align:center;margin-top:16px;font-size:12px;color:rgba(255,255,255,.5)}
.link a{color:#00FFFF;text-decoration:none;font-weight:800;text-transform:uppercase}
.ist-time{text-align:center;margin-top:12px;font-size:11px;color:#00FFFF;font-weight:800;letter-spacing:2px;font-family:monospace;text-shadow: 0 0 10px #00FFFF88}</style></head><body>
<div class="box"><div class="logo"><img src="{{ logo }}" alt="Logo"><h1>⚡ FLASH PREMIUM v15</h1><p>🔐 ᴀᴅᴍɪɴ ᴏɴʟʏ ᴄᴏᴍᴍᴀɴᴅ</p></div>
{% if error %}<div class="err">⚠️ {{ error }}</div>{% endif %}
<form method="POST">
<div class="fg"><label>👤 Username</label><input type="text" name="username" required autofocus></div>
<div class="fg"><label>🔑 Password</label><input type="password" name="password" required></div>
<button class="btn" type="submit">🚀 ʟᴏɢɪɴ ᴛᴏ ᴘᴀɴᴇʟ</button></form>
<div class="ist-time">🇮🇳 {{ ist_now }}</div>
<div class="link">👥 ᴜꜱᴇʀ? <a href="/user/login">ᴜꜱᴇʀ ʟᴏɢɪɴ</a> · 🤝 <a href="/helper/login">ʜᴇʟᴘᴇʀ</a></div></div></body></html>"""

@app.route("/login", methods=["GET","POST"])
def login():
    err = None
    if request.method == "POST":
        u = request.form.get("username"); p = request.form.get("password")
        ip = (request.headers.get("X-Forwarded-For", request.remote_addr or "?")
              .split(",")[0].strip())
        if u == ADMIN_U and p == ADMIN_P:
            session["adm"] = True; session["username"] = ADMIN_U; session.permanent = True
            ts = now_ist().strftime("%d %b %Y, %I:%M:%S %p IST")
            notify_admin("Admin Login Success",
                f"👤 <code>{u}</code>\n🌐 <code>{ip}</code>\n🕐 <code>{ts}</code>", "success")
            return redirect(url_for("admin"))
        err = "INVALID CREDENTIALS"
    return render_template_string(LOGIN_HTML, error=err,
        logo=setting("logo_image",LOGO_IMG),
        ist_now=now_ist().strftime("%d %b %Y, %I:%M:%S %p IST"))

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("login"))

# ================= HELPER LOGIN =================
HELPER_LOGIN_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>🤝 HELPER LOGIN</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;background:#05050A;overflow:hidden;position:relative}
body::before{content:'';position:absolute;inset:0;background:radial-gradient(circle at 30% 30%,#00FFFF15,transparent 40%),radial-gradient(circle at 70% 70%,#FFD70015,transparent 40%)}
.box{position:relative;z-index:2;background:rgba(10,10,15,.92);backdrop-filter:blur(30px);border:1px solid #00FFFF55;border-radius:24px;padding:46px 40px;width:100%;max-width:440px;box-shadow: 0 0 40px #00FFFF22}
.logo{text-align:center;margin-bottom:32px}
.logo img{width:90px;height:90px;border-radius:50%;border:3px solid #00FFFF;box-shadow:0 0 40px #00FFFFcc;object-fit:cover}
.logo h1{font-size:22px;font-weight:900;margin-top:14px;letter-spacing:3px;text-transform:uppercase;background:linear-gradient(135deg,#00FFFF,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.logo p{color:rgba(255,255,255,.5);font-size:10px;margin-top:8px;letter-spacing:4px;text-transform:uppercase;font-weight:800}
.info{background:rgba(0,255,255,.05);border:1px solid rgba(0,255,255,.3);border-radius:12px;padding:14px;font-size:11.5px;color:rgba(255,255,255,.75);margin-bottom:18px;line-height:1.7}
.fg{margin-bottom:16px}
.fg label{display:block;color:rgba(255,255,255,.8);font-size:11px;font-weight:800;margin-bottom:6px;letter-spacing:1.5px;text-transform:uppercase}
.fg input{width:100%;padding:15px 16px;background:rgba(0,0,0,.4);border:1px solid #00FFFF44;border-radius:12px;color:#fff;font-size:14px;outline:none;transition:.3s}
.fg input:focus{border-color:#00FFFF;box-shadow:0 0 15px #00FFFF44}
.btn{width:100%;padding:15px;background:rgba(0,255,255,.05);border:1px solid #00FFFF;border-radius:12px;color:#00FFFF;font-size:14px;font-weight:900;cursor:pointer;letter-spacing:2px;text-transform:uppercase;margin-top:6px;font-family:inherit;transition:.3s;text-shadow:0 0 10px #00FFFF88}
.btn:hover{background:#00FFFF;color:#000;box-shadow:0 0 20px #00FFFF88;text-shadow:none}
.err{background:rgba(255,0,0,.15);border:1px solid rgba(255,0,0,.35);color:#ff4444;padding:12px;border-radius:12px;font-size:12px;margin-bottom:18px;text-align:center;font-weight:700;text-transform:uppercase}
.link{text-align:center;margin-top:16px;font-size:12px;color:rgba(255,255,255,.5)}
.link a{color:#FFD700;text-decoration:none;font-weight:800;text-transform:uppercase}</style></head><body>
<div class="box"><div class="logo"><img src="{{ logo }}"><h1>🤝 HELPER PANEL</h1><p>ʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇꜱꜱ</p></div>
{% if error %}<div class="err">⚠️ {{ error }}</div>{% endif %}
<div class="info">🤝 <b>HELPER ACCESS</b><br>Limited permissions: view orders, chat support, view stats only.</div>
<form method="POST">
<div class="fg"><label>👤 Helper Username</label><input type="text" name="username" required autofocus></div>
<div class="fg"><label>🔑 Password</label><input type="password" name="password" required></div>
<button class="btn" type="submit">🤝 ᴇɴᴛᴇʀ ʜᴇʟᴘᴇʀ ᴘᴀɴᴇʟ</button></form>
<div class="link">🔐 <a href="/login">ᴀᴅᴍɪɴ</a> · 👤 <a href="/user/login">ᴜꜱᴇʀ</a></div></div></body></html>"""

@app.route("/helper/login", methods=["GET","POST"])
def helper_login():
    err = None
    if request.method == "POST":
        u = request.form.get("username","").strip()
        p = request.form.get("password","")
        h = safe_find_one(helpers_col, {"_id": u})
        if h and h.get("password") == p and h.get("active", True):
            session["helper"] = True; session["helper_name"] = u; session.permanent = True
            notify_admin("Helper Login", f"🤝 <code>{u}</code>", "info")
            return redirect(url_for("helper_panel"))
        if HELPERS.get(u) == p:
            session["helper"] = True; session["helper_name"] = u; session.permanent = True
            return redirect(url_for("helper_panel"))
        err = "INVALID HELPER CREDENTIALS"
    return render_template_string(HELPER_LOGIN_HTML, error=err,
        logo=setting("logo_image",LOGO_IMG))

@app.route("/helper/logout")
def helper_logout():
    session.clear(); return redirect(url_for("helper_login"))

# ================= USER LOGIN =================
ULOGIN_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>👤 USER LOGIN · FLASH PREMIUM v15</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;background:#05050A;position:relative;overflow:hidden}
body::before{content:'';position:absolute;inset:0;background:radial-gradient(circle at 20% 20%,#FF005515,transparent 40%),radial-gradient(circle at 80% 80%,#00FFFF15,transparent 40%)}
.box{position:relative;z-index:2;background:rgba(10,10,15,.92);backdrop-filter:blur(30px);border:1px solid #FF005555;border-radius:24px;padding:46px 40px;width:100%;max-width:440px;box-shadow:0 0 40px #FF005522}
.logo{text-align:center;margin-bottom:32px}
.logo img{width:90px;height:90px;border-radius:50%;border:3px solid #FF0055;box-shadow:0 0 40px #FF0055cc;object-fit:cover}
.logo h1{font-size:22px;font-weight:900;margin-top:14px;letter-spacing:3px;text-transform:uppercase;background:linear-gradient(135deg,#FF0055,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.logo p{color:rgba(255,255,255,.5);font-size:10px;margin-top:8px;letter-spacing:4px;text-transform:uppercase;font-weight:800}
.info{background:rgba(255,0,85,.05);border:1px solid rgba(255,0,85,.3);border-radius:12px;padding:14px;font-size:11.5px;color:rgba(255,255,255,.75);margin-bottom:18px;line-height:1.7}
.fg{margin-bottom:16px}
.fg label{display:block;color:rgba(255,255,255,.8);font-size:11px;font-weight:800;margin-bottom:6px;letter-spacing:1.5px;text-transform:uppercase}
.fg input{width:100%;padding:15px 16px;background:rgba(0,0,0,.4);border:1px solid #FF005544;border-radius:12px;color:#fff;font-size:14px;outline:none;transition:.3s}
.fg input:focus{border-color:#FF0055;box-shadow:0 0 15px #FF005544}
.btn{width:100%;padding:15px;background:rgba(255,0,85,.05);border:1px solid #FF0055;border-radius:12px;color:#FF0055;font-size:14px;font-weight:900;cursor:pointer;letter-spacing:2px;text-transform:uppercase;margin-top:6px;font-family:inherit;transition:.3s;text-shadow:0 0 10px #FF005588}
.btn:hover{background:#FF0055;color:#fff;box-shadow:0 0 20px #FF005588;text-shadow:none}
.err{background:rgba(255,0,0,.15);border:1px solid rgba(255,0,0,.35);color:#ff4444;padding:12px;border-radius:12px;font-size:12px;margin-bottom:18px;text-align:center;font-weight:700;text-transform:uppercase}
.link{text-align:center;margin-top:16px;font-size:12px;color:rgba(255,255,255,.5)}
.link a{color:#00FFFF;text-decoration:none;font-weight:800;text-transform:uppercase}
.ist-time{text-align:center;margin-top:12px;font-size:11px;color:#00FFFF;font-weight:800;letter-spacing:2px;font-family:monospace;text-shadow:0 0 10px #00FFFF88}</style></head><body>
<div class="box"><div class="logo"><img src="{{ logo }}"><h1>⚡ FLASH PREMIUM v15</h1><p>👤 ᴜꜱᴇʀ ᴘᴀɴᴇʟ ʟᴏɢɪɴ</p></div>
{% if error %}<div class="err">⚠️ {{ error }}</div>{% endif %}
<div class="info">📌 <b>FIRST TIME?</b><br>🤖 Send <b>/start</b> to <b>@APROLXDDOSBOT</b> and get your <b>Telegram ID</b>.</div>
<form method="POST">
<div class="fg"><label>👤 Username (Telegram ID)</label><input type="text" name="username" required autofocus placeholder="123456789"></div>
<div class="fg"><label>🔑 Password</label><input type="password" name="password" required placeholder="user123"></div>
<button class="btn" type="submit">🚀 ᴇɴᴛᴇʀ ᴜꜱᴇʀ ᴘᴀɴᴇʟ</button></form>
<div class="ist-time">🇮🇳 {{ ist_now }}</div>
<div class="link">🔐 <a href="/login">ᴀᴅᴍɪɴ</a> · 🤝 <a href="/helper/login">ʜᴇʟᴘᴇʀ</a></div></div></body></html>"""

@app.route("/user/login", methods=["GET","POST"])
def usr_login():
    err = None
    if request.method == "POST":
        u = request.form.get("username","").strip()
        p = request.form.get("password","")
        doc = safe_find_one(users_col, {"_id": u})
        ip = (request.headers.get("X-Forwarded-For", request.remote_addr or "?")
              .split(",")[0].strip())
        if not doc:
            ref = request.args.get("ref","")
            safe_insert(users_col, {"_id":u,"password":"user123","created_at":now_str(),
                "total_orders":0,"referred_by":ref,"referral_code":gen_code("REF",8)})
            session["usr"]=True; session["uid"]=u; session.permanent=True
            notify_admin("New User Registered",
                f"👤 <code>{u}</code>\n🎁 {ref or '-'}\n🌐 <code>{ip}</code>", "user")
            return redirect(url_for("usr_panel"))
        if p == doc.get("password","user123"):
            session["usr"]=True; session["uid"]=u; session.permanent=True
            notify_admin("User Login", f"👤 <code>{u}</code>\n🌐 <code>{ip}</code>", "user")
            return redirect(url_for("usr_panel"))
        err = "INVALID PASSWORD"
    return render_template_string(ULOGIN_HTML, error=err,
        logo=setting("logo_image",LOGO_IMG),
        ist_now=now_ist().strftime("%d %b %Y, %I:%M:%S %p IST"))

@app.route("/user/logout")
def usr_logout():
    session.clear(); return redirect(url_for("usr_login"))

# ================= MEDIA SERVE =================
@app.route("/chat_media/<path:fname>")
def serve_chat_media(fname):
    try:
        path = os.path.join(CHAT_MEDIA_DIR, fname)
        if os.path.exists(path):
            return send_file(path)
    except: pass
    return "Not found", 404

@app.route("/api/chat/upload", methods=["POST"])
def api_chat_upload():
    try:
        cid = (request.form.get("chat_id") or "").strip()
        name = (request.form.get("name") or "Anonymous").strip()
        caption = (request.form.get("caption") or "").strip()[:800]
        is_voice = request.form.get("voice") == "1"
        if not cid or "file" not in request.files:
            return jsonify({"success": False, "error": "Missing"})
        f = request.files["file"]
        if not f.filename:
            return jsonify({"success": False, "error": "Empty filename"})
        raw_name = secure_filename(f.filename) or "file"
        ext = raw_name.rsplit(".", 1)[-1].lower() if "." in raw_name else ""
        if ext not in ALLOWED_MEDIA:
            return jsonify({"success": False, "error": f".{ext} not allowed"})
        f.seek(0, 2); size = f.tell(); f.seek(0)
        if size > MAX_MEDIA_MB * 1024 * 1024:
            return jsonify({"success": False, "error": f"File > {MAX_MEDIA_MB}MB"})
        media_type = "voice" if is_voice else detect_media_type(ext)
        stored = f"{secrets.token_hex(14)}.{ext}"
        path = os.path.join(CHAT_MEDIA_DIR, stored)
        f.save(path)
        url = f"/chat_media/{stored}"
        safe_insert(chat_col, {"chat_id": cid, "name": name,
            "text": caption or f"[{media_type.upper()}]",
            "caption": caption, "sender": "user", "media_type": media_type,
            "media_url": url, "media_name": raw_name, "time": now_str(),
            "status": "open"})
        notify_admin(f"New {media_type.title()} in Chat",
            f"👤 <b>{sc('from')}:</b> {name}\n🆔 <code>{cid}</code>\n📎 {media_type.upper()}\n📝 {caption[:150] or '-'}", "chat")
        owner_id = str(setting("owner_telegram_id", OWNER_TG_ID) or "").strip()
        if owner_id:
            head = f"💬 <b>New {media_type.title()}</b>\n👤 {name}\n🆔 <code>{cid}</code>"
            cap = f"{head}\n\n📝 {caption}" if caption else head
            try: tg_send_media(owner_id, path, media_type, cap)
            except: pass
        return jsonify({"success": True, "url": url, "type": media_type})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/chat/reply-media", methods=["POST"])
@helper_req
def api_chat_reply_media():
    try:
        cid = (request.form.get("chat_id") or "").strip()
        caption = (request.form.get("caption") or "").strip()[:800]
        if not cid or "file" not in request.files:
            return jsonify({"success": False, "error": "Missing"})
        f = request.files["file"]
        raw_name = secure_filename(f.filename) or "file"
        ext = raw_name.rsplit(".", 1)[-1].lower() if "." in raw_name else ""
        if ext not in ALLOWED_MEDIA:
            return jsonify({"success": False, "error": "Type not allowed"})
        stored = f"{secrets.token_hex(14)}.{ext}"
        path = os.path.join(CHAT_MEDIA_DIR, stored)
        f.save(path)
        media_type = detect_media_type(ext)
        url = f"/chat_media/{stored}"
        safe_insert(chat_col, {"chat_id": cid, "name": "Support",
            "text": caption or f"[{media_type.upper()}]",
            "sender": "owner", "media_type": media_type, "media_url": url,
            "media_name": raw_name, "time": now_str()})
        log_adm("chat_reply_media", f"to {cid} ({media_type})")
        return jsonify({"success": True, "url": url, "type": media_type})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ================= STORE HTML =================
# (Full store HTML unchanged — see below for complete HTML embedded)
STORE_HTML = r"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>⚡ FLASH PREMIUM STORE v15 · Ultra Premium 🇮🇳</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=JetBrains+Mono:wght@600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--p:#FFD700;--s:#00FFFF;--a:#FF0055;--ok:#00FF88}
body{font-family:'Inter',sans-serif;background:#05050A;color:#fff;min-height:100vh;overflow-x:hidden}
body::before{content:'';position:fixed;inset:0;
  background:radial-gradient(at 20% 30%,#FFD70015 0px,transparent 50%),
  radial-gradient(at 80% 20%,#FF005515 0px,transparent 50%),
  radial-gradient(at 50% 80%,#00FFFF15 0px,transparent 50%),
  radial-gradient(at 90% 90%,#FFD70015 0px,transparent 40%),#05050A;
  background-size:200% 200%;animation:auroraMove 20s ease infinite;
  filter:blur(60px) brightness(.6) saturate(1.5);z-index:-2;transform:scale(1.2)}
@keyframes auroraMove{0%,100%{background-position:0% 0%}25%{background-position:100% 0%}50%{background-position:100% 100%}75%{background-position:0% 100%}}
body::after{content:'';position:fixed;inset:0;background-image:url('{{ bg }}');background-size:cover;
  background-position:center;opacity:.08;mix-blend-mode:overlay;z-index:-1;pointer-events:none}
.tb{position:fixed;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#FFD700,#00FFFF,#FF0055,#FFD700);background-size:400% 100%;animation:sl 3s linear infinite;z-index:100}
@keyframes sl{0%{background-position:0 0}100%{background-position:400% 0}}
.ist-badge{position:fixed;top:20px;right:20px;background:rgba(10,10,15,.95);backdrop-filter:blur(20px);border:1px solid #FFD70066;border-radius:14px;padding:10px 16px;font-size:12px;font-weight:900;color:#00FFFF;letter-spacing:1.5px;z-index:999;font-family:'JetBrains Mono',monospace;box-shadow:0 8px 24px rgba(0,0,0,.6), 0 0 15px #FFD70022;text-shadow:0 0 8px #00FFFF88}
.hero-premium{position:relative;text-align:center;padding:110px 20px 50px;overflow:hidden}
.hero-glow{position:absolute;top:-100px;left:50%;transform:translateX(-50%);width:700px;height:700px;border-radius:50%;
  background:radial-gradient(circle,#FFD70033 0%,transparent 65%);filter:blur(80px);pointer-events:none;
  animation:glowPulse 5s ease-in-out infinite;z-index:0}
@keyframes glowPulse{0%,100%{opacity:.7;transform:translateX(-50%) scale(1)}50%{opacity:1;transform:translateX(-50%) scale(1.15)}}
.hero-badge{display:inline-flex;align-items:center;gap:8px;padding:8px 20px;
  background:rgba(255,215,0,.05);border:1px solid rgba(255,215,0,.4);border-radius:30px;
  font-size:10.5px;font-weight:900;letter-spacing:2.5px;text-transform:uppercase;color:#FFD700;
  margin-bottom:24px;position:relative;z-index:2;backdrop-filter:blur(10px);box-shadow:0 0 15px #FFD70033;text-shadow:0 0 8px #FFD70088}
.hero-badge::before{content:'';width:6px;height:6px;background:#00FF88;border-radius:50%;box-shadow:0 0 10px #00FF88;animation:dotPulse 1.5s infinite}
@keyframes dotPulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(1.4)}}
.hero-premium h1{font-size:clamp(38px,7vw,82px);font-weight:900;line-height:1.05;letter-spacing:-3px;text-transform:uppercase;position:relative;z-index:2;margin-bottom:20px;color:#fff}
.hero-premium h1 span{display:block;background:linear-gradient(135deg,#FFD700 0%,#00FFFF 40%,#FF0055 70%,#FFD700 100%);background-size:300% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:gradientShift 5s linear infinite; filter: drop-shadow(0 0 15px #FFD70055)}
@keyframes gradientShift{0%{background-position:0% center}100%{background-position:300% center}}
.hero-premium .hero-sub{font-size:13px;color:rgba(255,255,255,.55);letter-spacing:3px;text-transform:uppercase;font-weight:800;margin-bottom:36px;position:relative;z-index:2}
.hero-actions{display:flex;justify-content:center;gap:14px;flex-wrap:wrap;position:relative;z-index:2}
.btn-primary,.btn-ghost{padding:16px 32px;border-radius:16px;font-size:12px;font-weight:900;letter-spacing:2.5px;text-transform:uppercase;cursor:pointer;border:1px solid;font-family:inherit;text-decoration:none;display:inline-flex;align-items:center;gap:10px;transition:all .4s cubic-bezier(.34,1.56,.64,1);position:relative;overflow:hidden}
.btn-primary{background:rgba(255,215,0,.05);border-color:#FFD700;color:#FFD700;text-shadow:0 0 8px #FFD70088;box-shadow:0 0 20px #FFD70022}
.btn-primary:hover{background:#FFD700;color:#000;transform:translateY(-4px) scale(1.03);box-shadow:0 20px 40px #FFD70066;text-shadow:none}
.btn-ghost{background:rgba(0,255,255,.05);border-color:#00FFFF;color:#00FFFF;text-shadow:0 0 8px #00FFFF88}
.btn-ghost:hover{background:#00FFFF;color:#000;transform:translateY(-4px);box-shadow:0 20px 40px #00FFFF66;text-shadow:none}
.brow{display:flex;justify-content:center;gap:10px;margin-top:18px;flex-wrap:wrap}
.bd{padding:8px 18px;background:rgba(0,255,136,.05);border:1px solid rgba(0,255,136,.4);border-radius:24px;font-size:11px;font-weight:900;color:#00FF88;text-transform:uppercase;letter-spacing:1.5px;text-shadow:0 0 8px #00FF8888;box-shadow:0 0 15px #00FF8822}
.bd.g{background:rgba(255,215,0,.05);border-color:rgba(255,215,0,.4);color:#FFD700;text-shadow:0 0 8px #FFD70088;box-shadow:0 0 15px #FFD70022}
.bd.p{background:rgba(255,0,85,.05);border-color:rgba(255,0,85,.4);color:#FF0055;text-shadow:0 0 8px #FF005588;box-shadow:0 0 15px #FF005522}
.countdown-box{max-width:700px;margin:28px auto 0;padding:0 20px}
.countdown-inner{background:linear-gradient(135deg,rgba(255,215,0,.08),rgba(255,0,85,.05));border:2px solid rgba(255,215,0,.5);border-radius:20px;padding:20px;text-align:center;box-shadow:0 0 30px #FFD70022}
.countdown-inner .ct-label{font-size:11px;letter-spacing:3px;text-transform:uppercase;font-weight:900;color:#FF0055;margin-bottom:12px;text-shadow:0 0 8px #FF005588}
.countdown-inner .ct-timer{display:flex;justify-content:center;gap:14px;flex-wrap:wrap}
.ct-seg{background:rgba(0,0,0,.4);border:1px solid rgba(255,215,0,.3);border-radius:12px;padding:10px 14px;min-width:70px;box-shadow:inset 0 0 15px #FFD70011}
.ct-num{font-family:'JetBrains Mono',monospace;font-size:24px;font-weight:900;color:#FFD700;text-shadow:0 0 12px #FFD70088}
.ct-lbl{font-size:9px;text-transform:uppercase;letter-spacing:2px;color:rgba(255,255,255,.5);font-weight:800;margin-top:4px}
.live-bar{max-width:900px;margin:24px auto 0;padding:0 20px;display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}
.live-item{background:rgba(10,10,15,.85);backdrop-filter:blur(20px);border:1px solid rgba(255,215,0,.25);border-left:3px solid #FFD700;border-radius:16px;padding:16px;text-align:center;transition:.3s;box-shadow:0 0 20px #FFD70011}
.live-item:nth-child(2){border-left-color:#00FFFF;border-color:rgba(0,255,255,.25);box-shadow:0 0 20px #00FFFF11}
.live-item:nth-child(3){border-left-color:#FF0055;border-color:rgba(255,0,85,.25);box-shadow:0 0 20px #FF005511}
.live-item:nth-child(4){border-left-color:#00FF88;border-color:rgba(0,255,136,.25);box-shadow:0 0 20px #00FF8811}
.live-item:hover{transform:translateY(-4px);filter:brightness(1.2)}
.live-item .ic{font-size:24px;margin-bottom:6px}
.live-item .n{font-size:22px;font-weight:900;font-family:'JetBrains Mono',monospace;background:linear-gradient(135deg,#fff,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 8px #FFD70055)}
.live-item .l{font-size:9.5px;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:2px;font-weight:800;margin-top:4px}
.trust-bar{max-width:900px;margin:24px auto 0;padding:0 20px;display:flex;justify-content:center;gap:12px;flex-wrap:wrap}
.trust-item{background:rgba(10,10,15,.7);border:1px solid rgba(255,255,255,.1);border-radius:12px;padding:10px 16px;font-size:11px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:rgba(255,255,255,.7);display:flex;align-items:center;gap:8px}
.cont{max-width:1300px;margin:0 auto;padding:20px}
.st{text-align:center;font-size:24px;font-weight:900;margin-bottom:8px;letter-spacing:4px;text-transform:uppercase;background:linear-gradient(135deg,#FFD700,#00FFFF,#FF0055);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 10px #FFD70055)}
.ss{text-align:center;font-size:11px;color:rgba(255,255,255,.5);margin-bottom:24px;letter-spacing:2px;text-transform:uppercase;font-weight:700}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px;margin-top:20px}
.card{background:rgba(10,10,15,.85);backdrop-filter:blur(20px) saturate(180%);border:1px solid rgba(255,255,255,.1);border-left:4px solid #FFD700;border-radius:22px;padding:24px;position:relative;overflow:hidden;transition:.4s cubic-bezier(.16,1,.3,1);cursor:pointer;transform-style:preserve-3d;will-change:transform;box-shadow:0 0 20px #FFD70011}
.card:nth-child(even){border-left-color:#00FFFF;box-shadow:0 0 20px #00FFFF11}
.card:nth-child(3n){border-left-color:#FF0055;box-shadow:0 0 20px #FF005511}
.card:hover{box-shadow:0 25px 70px rgba(255,215,0,.2);border-color:rgba(255,215,0,.6)}
.card.featured{border:2px solid #FFD70066;box-shadow:0 0 40px #FFD70033}
.ribbon{position:absolute;top:20px;right:-38px;transform:rotate(45deg);background:linear-gradient(135deg,#FF0055,#FFD700);padding:6px 46px;font-size:9px;font-weight:900;letter-spacing:2px;color:#fff;box-shadow:0 4px 20px #FF005599;z-index:5;text-transform:uppercase;text-shadow:0 1px 3px rgba(0,0,0,.5)}
.card .cat{position:absolute;top:14px;left:14px;background:rgba(0,255,255,.1);color:#00FFFF;border:1px solid rgba(0,255,255,.4);font-size:9px;font-weight:900;padding:5px 12px;border-radius:24px;letter-spacing:1.5px;text-transform:uppercase;z-index:4;text-shadow:0 0 8px #00FFFF88;box-shadow:0 0 10px #00FFFF22}
.card .ic{font-size:44px;margin-bottom:14px;filter:drop-shadow(0 0 15px #FFD700cc)}
.card h3{font-size:18px;font-weight:900;margin-bottom:8px;text-transform:uppercase;letter-spacing:1.5px;color:#FFD700;text-shadow:0 0 10px #FFD70044}
.card:nth-child(even) h3{color:#00FFFF;text-shadow:0 0 10px #00FFFF44}
.card:nth-child(3n) h3{color:#FF0055;text-shadow:0 0 10px #FF005544}
.card .dur{font-size:11px;color:rgba(255,255,255,.55);text-transform:uppercase;letter-spacing:2px;font-weight:800;margin-bottom:14px}
.card .feats{display:flex;flex-direction:column;gap:7px;margin:14px 0;padding:12px;background:rgba(0,0,0,.3);border-radius:12px;border:1px solid rgba(255,215,0,.15)}
.card .ft{display:flex;justify-content:space-between;align-items:center;font-size:10.5px;font-weight:700}
.card .fk{color:rgba(255,255,255,.55);letter-spacing:.5px;text-transform:uppercase}
.card .fv{color:#FFD700;font-family:'JetBrains Mono',monospace;font-weight:800;font-size:11px}
.card .pr{font-size:34px;font-weight:900;font-family:'JetBrains Mono',monospace;background:linear-gradient(135deg,#fff,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-top:14px;filter:drop-shadow(0 0 10px #FFD70055)}
.card .pr small{font-size:14px;color:rgba(255,255,255,.4);-webkit-text-fill-color:rgba(255,255,255,.4);margin-left:4px}
.card .bb{display:block;width:100%;margin-top:18px;padding:13px;background:rgba(255,215,0,.05);border:1px solid #FFD700;border-radius:12px;color:#FFD700;font-size:12px;font-weight:900;cursor:pointer;letter-spacing:2px;text-transform:uppercase;font-family:inherit;transition:.3s;text-shadow:0 0 8px #FFD70088}
.card .bb:hover{background:#FFD700;color:#000;box-shadow:0 8px 24px #FFD70066;text-shadow:none}
.skeleton{background:linear-gradient(90deg,rgba(255,255,255,.03) 25%,rgba(255,215,0,.1) 50%,rgba(255,255,255,.03) 75%);background-size:200% 100%;animation:shimmer 1.5s infinite;border-radius:22px}
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
.skeleton-card{height:340px}
.ov{display:none;position:fixed;inset:0;background:rgba(0,0,0,.9);backdrop-filter:blur(20px);z-index:1000;align-items:center;justify-content:center;padding:20px}
.ov.act{display:flex}
.mdl{background:rgba(10,10,15,.98);border:1px solid #FFD70066;border-radius:24px;padding:30px;max-width:540px;width:100%;max-height:90vh;overflow-y:auto;animation:mu .4s;box-shadow:0 0 50px #FFD70033}
@keyframes mu{from{opacity:0;transform:scale(.9)}to{opacity:1;transform:scale(1)}}
.mdl h3{font-size:20px;margin-bottom:8px;font-weight:900;letter-spacing:2px;text-transform:uppercase;background:linear-gradient(135deg,#FFD700,#FF0055);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 8px #FFD70055)}
.mdl .sb{color:rgba(255,255,255,.55);font-size:12px;margin-bottom:16px;text-transform:uppercase;letter-spacing:1px}
.fg{margin-bottom:16px}
.fg label{display:block;font-size:11px;font-weight:800;color:rgba(255,255,255,.75);margin-bottom:7px;letter-spacing:1.5px;text-transform:uppercase}
.fg input{width:100%;padding:13px 15px;background:rgba(0,0,0,.4);border:1px solid rgba(255,215,0,.3);border-radius:12px;color:#fff;font-size:13px;outline:none;font-family:inherit;transition:.3s}
.fg input:focus{border-color:#FFD700;background:#FFD7000a;box-shadow:0 0 15px #FFD70033}
.coupon-row{display:flex;gap:8px}
.coupon-row input{flex:1}
.coupon-row button{padding:13px 18px;background:rgba(0,255,255,.05);border:1px solid #00FFFF;border-radius:12px;color:#00FFFF;font-size:11px;font-weight:900;cursor:pointer;letter-spacing:1.5px;text-transform:uppercase;text-shadow:0 0 8px #00FFFF88;transition:.3s}
.coupon-row button:hover{background:#00FFFF;color:#000;text-shadow:none;box-shadow:0 0 15px #00FFFF66}
.tb2{background:linear-gradient(135deg,rgba(255,215,0,.08),rgba(255,0,85,.05));border:1px solid rgba(255,215,0,.4);border-radius:14px;padding:16px;margin:18px 0;display:flex;justify-content:space-between;align-items:center}
.tb2 .l{font-size:11px;color:rgba(255,255,255,.7);text-transform:uppercase;letter-spacing:2px;font-weight:800}
.tb2 .a{font-size:28px;font-weight:900;font-family:'JetBrains Mono',monospace;color:#FFD700;text-shadow:0 0 12px #FFD70088}
.act{display:flex;gap:10px;margin-top:20px;flex-wrap:wrap}
.bp{flex:1;padding:15px;background:rgba(0,255,136,.05);border:1px solid #00FF88;border-radius:13px;color:#00FF88;font-size:12px;font-weight:900;cursor:pointer;letter-spacing:2px;text-transform:uppercase;font-family:inherit;text-align:center;text-decoration:none;display:inline-block;position:relative;overflow:hidden;text-shadow:0 0 8px #00FF8888;transition:.3s}
.bp:hover{background:#00FF88;color:#000;transform:translateY(-2px);box-shadow:0 10px 30px #00FF8866;text-shadow:none}
.bc{padding:15px 22px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.2);border-radius:13px;color:rgba(255,255,255,.7);font-size:12px;font-weight:800;cursor:pointer;letter-spacing:1.5px;text-transform:uppercase;transition:.3s}
.bc:hover{background:rgba(255,255,255,.1);color:#fff;border-color:rgba(255,255,255,.4)}
.qr{text-align:center;padding:20px 0}
.qr img{max-width:240px;border-radius:18px;border:3px solid #FFD70066;box-shadow:0 0 50px #FFD70066}
.qr .u{font-family:'JetBrains Mono',monospace;font-size:13px;color:#FFD700;margin-top:16px;font-weight:700}
.qr .ab{font-size:38px;font-weight:900;background:linear-gradient(135deg,#00FF88,#00FFFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-family:'JetBrains Mono',monospace;margin:10px 0;filter:drop-shadow(0 0 15px #00FF8855)}
.ps{margin-top:18px;padding:14px;background:rgba(255,215,0,.05);border:1px solid rgba(255,215,0,.35);border-radius:12px;font-size:12px;color:#FFD700;font-weight:700;text-align:center;letter-spacing:1.5px;text-transform:uppercase;text-shadow:0 0 8px #FFD70088}
.kr{background:linear-gradient(135deg,rgba(0,255,136,.08),rgba(0,255,255,.05));border:2px solid rgba(0,255,136,.5);border-radius:16px;padding:24px;margin:18px 0;text-align:center;box-shadow:0 0 30px #00FF8822}
.kr .cd{font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:900;color:#00FF88;letter-spacing:2px;word-break:break-all;padding:12px 0;text-shadow:0 0 15px #00FF8888}
.cpb{padding:12px 24px;background:rgba(0,255,136,.05);border:1px solid #00FF88;border-radius:11px;color:#00FF88;font-size:11px;font-weight:900;cursor:pointer;letter-spacing:2px;text-transform:uppercase;font-family:inherit;margin-top:10px;transition:.3s;text-shadow:0 0 8px #00FF8888}
.cpb:hover{background:#00FF88;color:#000;box-shadow:0 0 20px #00FF8866;text-shadow:none}
#toastContainer{position:fixed;top:24px;right:24px;z-index:99999;display:flex;flex-direction:column;gap:10px;pointer-events:none;max-width:400px}
.premium-toast{background:rgba(10,10,15,.98);backdrop-filter:blur(24px);border-radius:16px;padding:16px 20px;color:#fff;font-size:13px;font-weight:700;display:flex;align-items:center;gap:14px;box-shadow:0 20px 60px rgba(0,0,0,.6),0 0 0 1px rgba(255,255,255,.05);transform:translateX(440px);transition:transform .4s cubic-bezier(.34,1.56,.64,1);position:relative;overflow:hidden;pointer-events:auto;min-width:280px}
.premium-toast.show{transform:translateX(0)}
.premium-toast .pt-icon{font-size:22px;flex-shrink:0;width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:10px}
.premium-toast .pt-msg{flex:1;line-height:1.4}
.premium-toast .pt-progress{position:absolute;bottom:0;left:0;height:3px;border-radius:0 0 0 16px;animation:toastProgress linear forwards}
@keyframes toastProgress{from{width:100%}to{width:0%}}
.premium-toast.success{border-left:4px solid #00FF88;box-shadow:0 0 20px #00FF8822}.premium-toast.success .pt-icon{background:rgba(0,255,136,.1);color:#00FF88}.premium-toast.success .pt-progress{background:#00FF88}
.premium-toast.error{border-left:4px solid #FF0055;box-shadow:0 0 20px #FF005522}.premium-toast.error .pt-icon{background:rgba(255,0,85,.1);color:#FF0055}.premium-toast.error .pt-progress{background:#FF0055}
.premium-toast.warning{border-left:4px solid #FFA500;box-shadow:0 0 20px #FFA50022}.premium-toast.warning .pt-icon{background:rgba(255,165,0,.1);color:#FFA500}.premium-toast.warning .pt-progress{background:#FFA500}
.premium-toast.info{border-left:4px solid #FFD700;box-shadow:0 0 20px #FFD70022}.premium-toast.info .pt-icon{background:rgba(255,215,0,.1);color:#FFD700}.premium-toast.info .pt-progress{background:#FFD700}
.premium-toast.vip{border-left:4px solid #FF0055;box-shadow:0 0 20px #FF005522}.premium-toast.vip .pt-icon{background:rgba(255,0,85,.1);color:#FF0055}.premium-toast.vip .pt-progress{background:#FF0055}
.btn-ripple{position:relative;overflow:hidden}
.btn-ripple .ripple{position:absolute;border-radius:50%;background:rgba(255,255,255,.4);transform:scale(0);animation:rippleEffect .6s linear;pointer-events:none}
@keyframes rippleEffect{to{transform:scale(4);opacity:0}}
.test-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
.test-card{background:rgba(10,10,15,.75);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.1);border-top:2px solid #00FFFF;border-radius:18px;padding:22px;transition:.3s;box-shadow:0 0 15px #00FFFF11}
.test-card:hover{border-color:rgba(0,255,255,.5);transform:translateY(-4px);box-shadow:0 15px 40px rgba(0,255,255,.2)}
.test-card .stars{color:#FFD700;font-size:14px;margin-bottom:10px;letter-spacing:2px;text-shadow:0 0 8px #FFD70088}
.test-card p{font-size:13px;color:rgba(255,255,255,.75);line-height:1.7;font-style:italic}
.test-card .who{margin-top:14px;font-size:11px;color:#00FFFF;font-weight:800;text-transform:uppercase;letter-spacing:1.8px}
.faq-grid{display:grid;gap:12px;max-width:900px;margin:0 auto}
.faq-item{background:rgba(10,10,15,.75);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.1);border-left:3px solid #FFD700;border-radius:16px;padding:18px 22px;cursor:pointer;transition:.3s;box-shadow:0 0 15px #FFD70011}
.faq-item:hover{border-color:rgba(255,215,0,.5);box-shadow:0 10px 30px rgba(255,215,0,.2)}
.faq-item h4{font-size:14px;font-weight:800;color:#FFD700;display:flex;justify-content:space-between;align-items:center;letter-spacing:1px;text-shadow:0 0 5px #FFD70044}
.faq-item p{font-size:12.5px;color:rgba(255,255,255,.7);line-height:1.7;margin-top:10px;display:none}
.faq-item.open p{display:block}
.faq-item .chev{transition:.3s;font-size:14px}
.faq-item.open .chev{transform:rotate(180deg)}
.track-box{max-width:600px;margin:0 auto;background:rgba(10,10,15,.85);backdrop-filter:blur(20px);border:1px solid rgba(255,215,0,.3);border-radius:20px;padding:26px;text-align:center;box-shadow:0 0 25px #FFD70022}
.track-box input{width:100%;padding:14px 16px;background:rgba(0,0,0,.4);border:1px solid rgba(255,215,0,.3);border-radius:12px;color:#fff;font-size:13px;outline:none;font-family:'JetBrains Mono',monospace;margin-bottom:12px;transition:.3s}
.track-box input:focus{border-color:#FFD700;box-shadow:0 0 15px #FFD70033}
.track-box button{width:100%;padding:14px;background:rgba(255,215,0,.05);border:1px solid #FFD700;border-radius:12px;color:#FFD700;font-size:12px;font-weight:900;cursor:pointer;letter-spacing:2px;text-transform:uppercase;font-family:inherit;text-shadow:0 0 8px #FFD70088;transition:.3s}
.track-box button:hover{background:#FFD700;color:#000;box-shadow:0 0 20px #FFD70066;text-shadow:none}
.track-result{margin-top:16px;padding:14px;background:rgba(0,0,0,.4);border-radius:12px;font-size:12.5px;text-align:left;display:none}
.track-result.show{display:block}
.section-title{text-align:center;font-size:22px;font-weight:900;margin:44px 0 8px;letter-spacing:3px;text-transform:uppercase;background:linear-gradient(135deg,#FFD700,#00FFFF,#FF0055);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 10px #FFD70055)}
.section-sub{text-align:center;font-size:11px;color:rgba(255,255,255,.5);margin-bottom:24px;letter-spacing:2px;text-transform:uppercase;font-weight:700}
.premium-lock-overlay{position:fixed;inset:0;background:rgba(5,5,10,.95);backdrop-filter:blur(20px);z-index:3000;display:flex;align-items:center;justify-content:center;padding:20px;animation:fadeIn .4s}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.premium-lock-card{background:linear-gradient(135deg,rgba(255,215,0,.15),rgba(255,0,85,.1));border:2px solid #FFD700;border-radius:28px;padding:40px 32px;max-width:480px;width:100%;text-align:center;position:relative;box-shadow:0 30px 100px #FFD70044,0 0 80px #FF005544;animation:lockPop .5s}
@keyframes lockPop{from{transform:scale(.85);opacity:0}to{transform:scale(1);opacity:1}}
.lock-crown{font-size:80px;margin-bottom:10px;animation:crownBounce 2s infinite;filter:drop-shadow(0 0 20px #FFD70088)}
@keyframes crownBounce{0%,100%{transform:translateY(0) rotate(-8deg)}50%{transform:translateY(-15px) rotate(8deg)}}
.premium-lock-card h2{font-size:26px;font-weight:900;letter-spacing:3px;background:linear-gradient(135deg,#FF0055,#FFD700,#00FFFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:12px;filter:drop-shadow(0 0 10px #FFD70055)}
.premium-lock-card p{color:rgba(255,255,255,.75);font-size:13px;margin-bottom:22px;letter-spacing:1.5px;line-height:1.6}
.lock-progress-wrap{background:rgba(0,0,0,.5);height:22px;border-radius:14px;overflow:hidden;position:relative;margin-bottom:24px;border:1px solid rgba(255,215,0,.3)}
.lock-progress-bar{height:100%;background:linear-gradient(90deg,#FF0055,#FFD700,#00FFFF);background-size:200%;border-radius:14px;transition:width .8s;animation:lockShimmer 3s infinite;box-shadow:0 0 15px #FFD70066}
@keyframes lockShimmer{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
.lock-progress-text{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:900;color:#fff;letter-spacing:2px;text-shadow:0 1px 3px rgba(0,0,0,.8)}
.lock-perks{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:24px}
.lock-perk{background:rgba(0,0,0,.4);border:1px solid rgba(255,215,0,.3);border-radius:14px;padding:14px 8px;transition:.3s}
.lock-perk:hover{transform:translateY(-3px);border-color:#FFD700;box-shadow:0 0 15px #FFD70033}
.lock-perk span{font-size:28px;display:block;margin-bottom:6px;filter:drop-shadow(0 0 8px #FFD70088)}
.lock-perk p{font-size:10.5px;color:rgba(255,255,255,.7);font-weight:900;letter-spacing:1.5px;text-transform:uppercase;margin:0}
.lock-cta{padding:16px 40px;background:rgba(255,215,0,.05);border:1px solid #FFD700;border-radius:16px;color:#FFD700;font-size:14px;font-weight:900;cursor:pointer;letter-spacing:2.5px;text-transform:uppercase;font-family:inherit;box-shadow:0 10px 40px #FFD70066;transition:.3s;width:100%;text-shadow:0 0 8px #FFD70088}
.lock-cta:hover{background:#FFD700;color:#000;transform:translateY(-3px);box-shadow:0 15px 50px #FFD70088;text-shadow:none}
.lock-close{position:absolute;top:14px;right:14px;background:rgba(255,255,255,.1);border:none;color:#fff;width:32px;height:32px;border-radius:50%;font-size:16px;cursor:pointer;font-weight:900}
.lock-close:hover{background:rgba(255,0,85,.3)}
.ticker{position:fixed;bottom:0;left:0;right:0;background:rgba(5,5,10,.95);backdrop-filter:blur(20px);border-top:1px solid #FFD70066;height:40px;overflow:hidden;z-index:1400;display:flex;align-items:center;box-shadow:0 -5px 20px #FFD70011}
.ticker-track{display:flex;gap:40px;animation:tickerScroll 40s linear infinite;white-space:nowrap;padding-left:100%}
@keyframes tickerScroll{0%{transform:translateX(0)}100%{transform:translateX(-100%)}}
.ticker-item{font-size:11px;font-weight:700;color:rgba(255,255,255,.7);letter-spacing:1px;text-transform:uppercase}
.ticker-item b{color:#00FF88;font-weight:900;text-shadow:0 0 8px #00FF8888}
.chat-fab{position:fixed;bottom:60px;right:28px;z-index:1500;width:60px;height:60px;border-radius:50%;background:rgba(255,215,0,.05);border:1px solid #FFD700;color:#FFD700;font-size:26px;cursor:pointer;box-shadow:0 10px 40px #FFD70066;transition:.3s;display:flex;align-items:center;justify-content:center;animation:bounce 3s infinite;text-shadow:0 0 10px #FFD70088}
@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
.chat-fab:hover{transform:scale(1.15) rotate(10deg);animation:none;background:#FFD700;color:#000;text-shadow:none}
.chat-box{position:fixed;bottom:130px;right:28px;z-index:1500;width:380px;max-width:calc(100vw - 40px);background:rgba(10,10,15,.98);backdrop-filter:blur(30px);border:1px solid #FFD70066;border-radius:22px;box-shadow:0 30px 80px rgba(0,0,0,.8), 0 0 30px #FFD70022;display:none;overflow:hidden;animation:cu .3s;flex-direction:column;height:560px;max-height:calc(100vh - 180px)}
.chat-box.open{display:flex}
@keyframes cu{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
.chat-head{background:linear-gradient(135deg,rgba(255,215,0,.1),rgba(255,0,85,.1));padding:16px 20px;color:#fff;display:flex;justify-content:space-between;align-items:center;flex-shrink:0;border-bottom:1px solid #FFD70033}
.chat-head h4{font-size:13px;font-weight:900;letter-spacing:2px;text-transform:uppercase;color:#FFD700;text-shadow:0 0 8px #FFD70088}
.chat-head p{font-size:10px;font-weight:700;opacity:.8;margin-top:2px;color:#00FFFF}
.chat-head button{background:rgba(255,255,255,.2);border:none;color:#fff;width:28px;height:28px;border-radius:8px;cursor:pointer;font-size:16px;font-weight:900}
.chat-body{padding:18px;flex:1;overflow-y:auto}
.chat-msg{margin-bottom:12px;display:flex;flex-direction:column;animation:cmsg .3s}
@keyframes cmsg{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.chat-msg .bbl{padding:10px 14px;border-radius:14px;font-size:12.5px;line-height:1.5;max-width:85%;word-wrap:break-word}
.chat-msg.user .bbl{background:rgba(255,215,0,.1);color:#FFD700;border:1px solid #FFD70055;align-self:flex-end;font-weight:600}
.chat-msg.owner .bbl{background:rgba(0,255,255,.1);color:#00FFFF;border:1px solid #00FFFF55;align-self:flex-start}
.chat-msg.system .bbl{background:rgba(255,255,255,.05);color:rgba(255,255,255,.7);align-self:center;text-align:center;font-size:11px;max-width:100%;border:1px solid rgba(255,255,255,.2)}
.chat-msg .tm{font-size:9px;color:rgba(255,255,255,.4);margin-top:4px;font-weight:600}
.chat-msg.user .tm{text-align:right}
.chat-msg .bbl img,.chat-msg .bbl video{max-width:100%;border-radius:12px;display:block}
.chat-msg .bbl audio{width:220px;max-width:100%}
.chat-msg .bbl .file-chip{display:flex;align-items:center;gap:8px;background:rgba(0,0,0,.35);padding:8px 12px;border-radius:10px;text-decoration:none;color:#FFD700}
.chat-msg.user .bbl .file-chip{color:#fff;background:rgba(255,255,255,.3)}
.chat-foot{padding:14px;border-top:1px solid rgba(255,255,255,.08);display:flex;gap:8px;flex-shrink:0;flex-direction:column}
.chat-foot input{padding:11px 14px;background:rgba(0,0,0,.4);border:1px solid rgba(255,215,0,.3);border-radius:11px;color:#fff;font-size:12.5px;outline:none;font-family:inherit;width:100%;transition:.3s}
.chat-foot input:focus{border-color:#FFD700;box-shadow:0 0 15px #FFD70033}
.chat-row{display:flex;gap:8px;align-items:center}
.chat-row input{flex:1}
.chat-foot button{padding:11px 16px;background:rgba(255,215,0,.05);border:1px solid #FFD700;border-radius:11px;color:#FFD700;font-size:14px;font-weight:900;cursor:pointer;text-shadow:0 0 8px #FFD70088;transition:.3s}
.chat-foot button:hover{background:#FFD700;color:#000;text-shadow:none}
.chat-attach,.chat-rec{width:44px;height:44px;border-radius:12px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.05);color:#00FFFF;font-size:18px;cursor:pointer;transition:.25s;flex-shrink:0;font-weight:900;text-shadow:0 0 8px #00FFFF88}
.chat-attach:hover,.chat-rec:hover{background:rgba(0,255,255,.1);border-color:#00FFFF;transform:scale(1.08);box-shadow:0 0 15px #00FFFF33}
.chat-rec.recording{background:rgba(255,0,85,.1);border-color:#FF0055;color:#FF0055;animation:recPulse .8s infinite;text-shadow:0 0 8px #FF005588}
@keyframes recPulse{0%,100%{box-shadow:0 0 0 0 rgba(255,0,85,.7)}50%{box-shadow:0 0 0 12px rgba(255,0,85,0)}}
.chat-preview{padding:6px 0;display:none}
.chat-preview.show{display:block}
.chat-preview .pv{background:rgba(255,215,0,.05);border:1px dashed rgba(255,215,0,.4);border-radius:12px;padding:8px 12px;display:flex;align-items:center;gap:10px;margin-bottom:8px}
.chat-preview .pv img{width:48px;height:48px;border-radius:8px;object-fit:cover}
.chat-preview .pv .pv-n{flex:1;font-size:11px;color:#FFD700;font-weight:800;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.chat-preview .pv .pv-x{background:rgba(255,0,85,.1);border:1px solid #FF0055;color:#FF0055;width:24px;height:24px;border-radius:50%;cursor:pointer;font-weight:900;text-shadow:0 0 5px #FF005588}
.live-pop{position:fixed;bottom:110px;left:28px;z-index:1400;background:linear-gradient(135deg,rgba(0,255,136,.1),rgba(0,255,255,.1));border:1px solid #00FF88;border-radius:14px;padding:12px 18px;color:#00FF88;font-size:12px;font-weight:800;box-shadow:0 10px 30px #00FF8866;animation:liveSlide .5s;display:none;text-shadow:0 0 8px #00FF8888}
@keyframes liveSlide{from{opacity:0;transform:translateX(-60px)}to{opacity:1;transform:translateX(0)}}
.live-pop.show{display:block}
.live-pop b{color:#fff;font-weight:900;text-shadow:none}
.ann-pop{position:fixed;bottom:100px;left:28px;z-index:1499;max-width:340px;background:linear-gradient(135deg,rgba(255,215,0,.15),rgba(255,0,85,.15));border:1px solid #FFD700;border-radius:18px;padding:18px 22px;color:#fff;box-shadow:0 20px 60px #FFD70044;animation:annIn .5s;display:none;cursor:pointer}
.ann-pop.show{display:block}
.ann-pop .ann-h{font-size:13px;font-weight:900;margin-bottom:6px;letter-spacing:2px;text-transform:uppercase;color:#FFD700;text-shadow:0 0 8px #FFD70088}
.ann-pop .ann-b{font-size:12.5px;font-weight:700;line-height:1.5}
.ann-pop .ann-x{position:absolute;top:8px;right:12px;background:rgba(255,255,255,.2);border:none;color:#fff;width:22px;height:22px;border-radius:50%;cursor:pointer;font-size:13px;font-weight:900}
@keyframes annIn{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
.ld{width:18px;height:18px;border:2px solid rgba(255,255,255,.2);border-top-color:#FFD700;border-radius:50%;animation:sp .8s linear infinite;display:inline-block;box-shadow:0 0 10px #FFD70044}
@keyframes sp{to{transform:rotate(360deg)}}
footer{text-align:center;padding:50px 20px 80px;color:rgba(255,255,255,.3);font-size:11px;font-weight:600;letter-spacing:2px;text-transform:uppercase}
footer .fl{background:linear-gradient(135deg,#FFD700,#00FFFF,#FF0055);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:900;filter:drop-shadow(0 0 8px #FFD70055)}
.flash-sale{position:fixed;top:0;left:0;right:0;background:linear-gradient(90deg,#FF0055,#FFD700,#00FFFF);padding:6px;text-align:center;font-size:11px;font-weight:900;letter-spacing:3px;text-transform:uppercase;z-index:99;color:#000;animation:flashPulse 2s infinite}
@keyframes flashPulse{0%,100%{opacity:.9}50%{opacity:1;box-shadow:0 0 30px #FF0055}}
.stars-bg{position:fixed;inset:0;pointer-events:none;z-index:-1;overflow:hidden}
.star-bg{position:absolute;width:2px;height:2px;background:#FFD700;border-radius:50%;animation:twinkle 4s infinite;box-shadow:0 0 6px #FFD700}
@keyframes twinkle{0%,100%{opacity:0}50%{opacity:1}}
.mobile-nav{display:none;position:fixed;bottom:0;left:0;right:0;background:rgba(10,10,15,.96);backdrop-filter:blur(24px) saturate(180%);border-top:1px solid rgba(255,215,0,.25);padding:10px 8px calc(10px + env(safe-area-inset-bottom));z-index:1600;justify-content:space-around;box-shadow:0 -10px 40px rgba(0,0,0,.5)}
.mn-item{display:flex;flex-direction:column;align-items:center;gap:4px;text-decoration:none;color:rgba(255,255,255,.5);padding:6px 12px;border-radius:12px;transition:all .25s;flex:1;max-width:80px}
.mn-item.active,.mn-item:hover{color:#FFD700;background:rgba(255,215,0,.05);text-shadow:0 0 8px #FFD70088}
.mn-icon{font-size:20px}
.mn-label{font-size:9px;font-weight:800;letter-spacing:1px;text-transform:uppercase}
.search-bar{max-width:600px;margin:0 auto 24px;position:relative}
.search-bar input{width:100%;padding:14px 50px 14px 18px;background:rgba(10,10,15,.85);backdrop-filter:blur(20px);border:1px solid rgba(255,215,0,.3);border-radius:14px;color:#fff;font-size:13px;outline:none;font-family:inherit;transition:.3s}
.search-bar input:focus{border-color:#FFD700;background:rgba(255,215,0,.05);box-shadow:0 0 30px #FFD70033}
.search-bar .s-icon{position:absolute;right:18px;top:50%;transform:translateY(-50%);font-size:16px;color:#FFD700;pointer-events:none;text-shadow:0 0 8px #FFD70088}
.cat-tabs{display:flex;justify-content:center;gap:8px;margin-bottom:20px;flex-wrap:wrap}
.cat-tab{padding:9px 18px;border-radius:20px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.12);color:rgba(255,255,255,.7);font-size:11px;font-weight:900;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;transition:.25s;font-family:inherit}
.cat-tab.active{background:rgba(255,215,0,.1);color:#FFD700;border-color:#FFD700;box-shadow:0 0 15px #FFD70044;text-shadow:0 0 8px #FFD70088}
.cat-tab:hover:not(.active){background:rgba(255,215,0,.05);border-color:rgba(255,215,0,.4)}
@media(max-width:600px){
  .hero-premium{padding:80px 16px 30px}
  .hero-premium h1{letter-spacing:-1.5px}
  .hero-actions{flex-direction:column;width:100%}
  .btn-primary,.btn-ghost{width:100%;justify-content:center}
  #toastContainer{left:16px;right:16px;max-width:none}
  .chat-box{right:16px;bottom:160px}
  .chat-fab{right:16px;bottom:100px}
  .live-bar{grid-template-columns:1fr 1fr;padding:0 12px}
  .ann-pop{left:16px;bottom:130px}
  .st{font-size:20px;letter-spacing:2px}
  .ist-badge{top:35px;right:10px;font-size:10px;padding:6px 10px}
  .flash-sale{font-size:9px;letter-spacing:2px}
  .mobile-nav{display:flex}
  body{padding-bottom:80px}
  .ticker{bottom:76px !important}
}
</style></head><body>

<div class="flash-sale">🔥 FLASH SALE LIVE — 20% OFF ON ALL VIP KEYS · USE CODE: FLASH20 🔥</div>
<div class="tb" style="top:28px"></div>
<div class="ist-badge">🇮🇳 <span id="ist-clock">Loading...</span></div>
<div class="stars-bg" id="stars"></div>

<div class="hero-premium">
  <div class="hero-glow"></div>
  <div class="hero-badge"><span style="animation:none">⚡</span> POWERED BY FLASH NETWORK</div>
  <h1>Premium Access<br><span>Redefined.</span></h1>
  <p class="hero-sub">Instant Keys · 24/7 Support · 10,000+ Happy Users</p>
  <div class="hero-actions">
    <a href="https://t.me/{{ bot }}" target="_blank" class="btn-primary btn-ripple"><span style="font-size:18px">🚀</span> Get Started</a>
    <a href="https://t.me/{{ channel }}" target="_blank" class="btn-ghost btn-ripple"><span style="font-size:18px">📢</span> Join Channel</a>
  </div>
  <div class="brow" style="margin-top:36px;position:relative;z-index:2">
    <div class="bd g">⚡ INSTANT DELIVERY</div>
    <div class="bd">🔒 SECURE PAYMENT</div>
    <div class="bd g">💎 PREMIUM QUALITY</div>
    <div class="bd p">🎁 REFER & EARN</div>
  </div>
</div>

<div class="countdown-box">
  <div class="countdown-inner">
    <div class="ct-label">🔥 LIMITED TIME OFFER ENDS IN 🔥</div>
    <div class="ct-timer" id="ctTimer">
      <div class="ct-seg"><div class="ct-num" id="ctH">00</div><div class="ct-lbl">HRS</div></div>
      <div class="ct-seg"><div class="ct-num" id="ctM">00</div><div class="ct-lbl">MIN</div></div>
      <div class="ct-seg"><div class="ct-num" id="ctS">00</div><div class="ct-lbl">SEC</div></div>
    </div>
  </div>
</div>

<div class="live-bar">
  <div class="live-item"><div class="ic">🔑</div><div class="n" id="ls-keys">-</div><div class="l">KEYS SOLD</div></div>
  <div class="live-item"><div class="ic">👥</div><div class="n" id="ls-users">-</div><div class="l">HAPPY USERS</div></div>
  <div class="live-item"><div class="ic">⭐</div><div class="n" id="ls-rating">5.0</div><div class="l">AVG RATING</div></div>
  <div class="live-item"><div class="ic">👁️</div><div class="n" id="ls-visits">-</div><div class="l">TODAY VISITS</div></div>
</div>

<div class="trust-bar">
  <div class="trust-item">🔒 SSL SECURED</div>
  <div class="trust-item">⚡ INSTANT</div>
  <div class="trust-item">🇮🇳 INDIAN SUPPORT</div>
  <div class="trust-item">💳 UPI/QR</div>
</div>

<div class="cont">
  <div class="st">💎 CHOOSE YOUR PLAN 💎</div>
  <div class="ss">✨ All Plans Include Full Access ✨</div>
  
  <div style="max-width:800px;margin:0 auto 20px">
    <div class="search-bar" style="margin-bottom:16px">
      <input type="text" id="storeSearch" placeholder="🔍 Search products..." oninput="filterStoreProducts()">
      <span class="s-icon">🔍</span>
    </div>
    <div class="cat-tabs" id="catTabs">
      <button class="cat-tab active" data-cat="ALL" onclick="filterStoreCategory('ALL',this)">🌟 ᴀʟʟ</button>
      <button class="cat-tab" data-cat="BASIC" onclick="filterStoreCategory('BASIC',this)">⚡ ʙᴀꜱɪᴄ</button>
      <button class="cat-tab" data-cat="PRO" onclick="filterStoreCategory('PRO',this)">🔥 ᴘʀᴏ</button>
      <button class="cat-tab" data-cat="VIP" onclick="filterStoreCategory('VIP',this)">💎 ᴠɪᴘ</button>
    </div>
  </div>
  
  <div class="grid" id="pg"><div style="grid-column:1/-1;text-align:center;padding:60px"><div class="ld"></div></div></div>
</div>

<div class="cont">
  <div class="section-title">🔎 TRACK YOUR ORDER 🔎</div>
  <div class="section-sub">📍 Enter your Order ID</div>
  <div class="track-box">
    <input id="trackInput" placeholder="FLASH-1234567890-ABC">
    <button onclick="trackOrder()">🔎 ᴛʀᴀᴄᴋ ᴏʀᴅᴇʀ</button>
    <div class="track-result" id="trackResult"></div>
  </div>
</div>

<div class="cont">
  <div class="section-title">💬 WHAT OUR USERS SAY 💬</div>
  <div class="section-sub">🌟 Real reviews</div>
  <div class="test-grid" id="testGrid"></div>
</div>

<div class="cont">
  <div class="section-title">❓ FREQUENTLY ASKED ❓</div>
  <div class="section-sub">💡 Get answers</div>
  <div class="faq-grid" id="faqGrid"></div>
</div>

<div class="premium-lock-overlay" id="premiumLock" style="display:none">
  <div class="premium-lock-card">
    <div class="lock-crown">👑</div>
    <h2>🔒 PREMIUM LOCKED</h2>
    <p>Unlock premium features with your first purchase</p>
    <div class="lock-progress-wrap">
      <div class="lock-progress-bar" id="lockProgressBar" style="width:0%"></div>
      <span class="lock-progress-text" id="lockProgressText">0%</span>
    </div>
    <div class="lock-perks">
      <div class="lock-perk"><span>🎰</span><p>Lucky Wheel</p></div>
      <div class="lock-perk"><span>🎁</span><p>Referral Bonus</p></div>
      <div class="lock-perk"><span>⚡</span><p>Priority Support</p></div>
      <div class="lock-perk"><span>💎</span><p>Exclusive Keys</p></div>
    </div>
    <button class="lock-cta" onclick="document.getElementById('premiumLock').style.display='none';document.getElementById('pg').scrollIntoView({behavior:'smooth'})">🚀 ᴜɴʟᴏᴄᴋ ɴᴏᴡ</button>
    <button class="lock-close" onclick="document.getElementById('premiumLock').style.display='none'">✕</button>
  </div>
</div>

<footer>© 2026 <span class="fl">⚡ FLASH PREMIUM v15 ⚡</span><br>
<span style="font-size:10px;opacity:.6;margin-top:8px;display:inline-block">⚡ POWERED BY {{ power }} ⚡</span><br>
<span style="font-size:10px;opacity:.6;margin-top:4px;display:inline-block">🇮🇳 Made in India · IST</span><br>
<a href="/user/login" style="color:#FFD700;font-size:11px;text-decoration:none;margin-top:8px;display:inline-block;letter-spacing:2px;font-weight:800;text-shadow:0 0 5px #FFD70088">👤 USER LOGIN</a>
&nbsp;·&nbsp;<a href="/helper/login" style="color:#00FFFF;font-size:11px;text-decoration:none;letter-spacing:2px;font-weight:800;text-shadow:0 0 5px #00FFFF88">🤝 HELPER</a></footer>

<div class="ticker" id="ticker"><div class="ticker-track" id="tickerTrack"></div></div>
<div class="ov" id="bm"><div class="mdl" id="bc"></div></div>
<div id="toastContainer"></div>
<div class="live-pop" id="livePop"></div>

<div class="ann-pop" id="annPop">
  <button class="ann-x" onclick="closeAnn(event)">&times;</button>
  <div class="ann-h" id="annH">📢 ANNOUNCEMENT</div>
  <div class="ann-b" id="annB"></div>
</div>

<div class="mobile-nav" id="mobileNav">
  <a href="/" class="mn-item active"><span class="mn-icon">🏠</span><span class="mn-label">Home</span></a>
  <a href="#pg" class="mn-item" onclick="document.getElementById('pg').scrollIntoView({behavior:'smooth'})"><span class="mn-icon">💎</span><span class="mn-label">Plans</span></a>
  <a href="#trackInput" class="mn-item" onclick="document.getElementById('trackInput').focus();document.getElementById('trackInput').scrollIntoView({behavior:'smooth'})"><span class="mn-icon">🔎</span><span class="mn-label">Track</span></a>
  <a href="https://t.me/{{ bot }}" target="_blank" class="mn-item"><span class="mn-icon">🤖</span><span class="mn-label">Bot</span></a>
  <a href="/user/login" class="mn-item"><span class="mn-icon">👤</span><span class="mn-label">Account</span></a>
</div>

<button class="chat-fab" onclick="toggleChat()">💬</button>
<div class="chat-box" id="chatBox">
  <div class="chat-head">
    <div><h4>💬 LIVE SUPPORT</h4><p>⚡ text · 📸 photo · 🎤 voice · 🎥 video</p></div>
    <button onclick="toggleChat()">&times;</button>
  </div>
  <div class="chat-body" id="chatBody"></div>
  <div class="chat-foot" id="chatFoot">
    <div id="chatPreview" class="chat-preview"></div>
    <div id="chatStartView">
      <input id="chatName" placeholder="👤 Enter your name / Telegram ID">
      <div style="height:8px"></div>
      <button onclick="startChat()" style="width:100%">🚀 ᴛᴀᴘ ᴛᴏ ᴄʜᴀᴛ</button>
    </div>
    <div id="chatMsgView" class="chat-row" style="display:none">
      <button class="chat-attach" onclick="document.getElementById('chatFile').click()">📎</button>
      <input type="file" id="chatFile" style="display:none" accept="image/*,audio/*,video/*,.pdf,.doc,.docx,.zip,.txt" onchange="previewFile(this)">
      <input id="chatMsg" placeholder="✏️ Type..." onkeydown="if(event.key==='Enter')sendChat()">
      <button class="chat-rec" id="recBtn" onclick="toggleRecord()">🎤</button>
      <button onclick="sendChat()">➤</button>
    </div>
  </div>
</div>

<script>
(function initToastContainer(){
  if(!document.getElementById('toastContainer')){
    const tc = document.createElement('div');
    tc.id = 'toastContainer';
    document.body.appendChild(tc);
  }
})();

function premiumToast(msg, type='info', duration=4000){
  const icons = {success:'✅',error:'❌',warning:'⚠️',info:'ℹ️',vip:'👶'};
  const tc = document.getElementById('toastContainer');
  const t = document.createElement('div');
  t.className = `premium-toast ${type}`;
  t.innerHTML = `<div class="pt-icon">${icons[type]||'ℹ️'}</div><div class="pt-msg">${msg}</div><div class="pt-progress" style="animation-duration:${duration}ms"></div>`;
  tc.appendChild(t);
  requestAnimationFrame(()=>t.classList.add('show'));
  setTimeout(()=>{t.classList.remove('show');setTimeout(()=>t.remove(),400);}, duration);
}

window.toast = function(m, t='info'){
  const map = {s:'success',e:'error',w:'warning',i:'info',v:'vip'};
  premiumToast(m, map[t] || t);
};

function init3DTilt(){
  document.querySelectorAll('.card').forEach(card=>{
    card.style.transition = 'transform .3s cubic-bezier(.34,1.56,.64,1)';
    card.onmousemove = e => {
      const r = card.getBoundingClientRect();
      const x = (e.clientX - r.left)/r.width - 0.5;
      const y = (e.clientY - r.top)/r.height - 0.5;
      card.style.transform = `perspective(1200px) rotateY(${x*12}deg) rotateX(${-y*12}deg) scale(1.03)`;
    };
    card.onmouseleave = () => { card.style.transform = ''; };
  });
}

document.addEventListener('click', e=>{
  const btn = e.target.closest('.btn-ripple, .bb, .bp, .bh, .lock-cta');
  if(!btn) return;
  const r = btn.getBoundingClientRect();
  const ripple = document.createElement('span');
  ripple.className = 'ripple';
  const size = Math.max(r.width, r.height);
  ripple.style.width = ripple.style.height = size + 'px';
  ripple.style.left = (e.clientX - r.left - size/2) + 'px';
  ripple.style.top = (e.clientY - r.top - size/2) + 'px';
  btn.appendChild(ripple);
  setTimeout(()=>ripple.remove(), 600);
});

let cp=null,pi=null,curOid=null,couponCode=null,couponDiscount=0;
function cm(){document.getElementById('bm').classList.remove('act');if(pi)clearInterval(pi);couponCode=null;couponDiscount=0;}
document.getElementById('bm').addEventListener('click',e=>{if(e.target.id==='bm')cm();});
function cpt(t){navigator.clipboard.writeText(t).then(()=>toast('✅ COPIED','s'));}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}

(function(){const s=document.getElementById('stars');for(let i=0;i<60;i++){const st=document.createElement('div');st.className='star-bg';st.style.left=Math.random()*100+'%';st.style.top=Math.random()*100+'%';st.style.animationDelay=(Math.random()*4)+'s';st.style.width=st.style.height=(Math.random()*3+1)+'px';s.appendChild(st);}})();

function tickIST(){const now=new Date();const opts={timeZone:'Asia/Kolkata',day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:true};document.getElementById('ist-clock').textContent=new Intl.DateTimeFormat('en-IN',opts).format(now);}
tickIST(); setInterval(tickIST, 1000);

function featsHtml(p){return `<div class="feats">
<div class="ft"><span class="fk">⚡ Time</span><span class="fv">${p.max_time||400}s</span></div>
<div class="ft"><span class="fk">🔢 Conc</span><span class="fv">${p.max_concurrent||4}</span></div>
<div class="ft"><span class="fk">⏳ Cooldown</span><span class="fv">${p.cooldown||60}s</span></div>
<div class="ft"><span class="fk">🎯 Attacks</span><span class="fv">UNLIMITED</span></div>
<div class="ft"><span class="fk">🚀 Delivery</span><span class="fv">INSTANT</span></div></div>`;}

let currentStoreCat = 'ALL';
let allStoreProducts = [];

async function lp(){
  const g = document.getElementById('pg');
  g.innerHTML = Array(6).fill(0).map(()=>`<div class="skeleton skeleton-card"></div>`).join('');
  try{
    const r = await fetch('/api/products');
    const d = await r.json();
    if(!d||!d.length){g.innerHTML='<div style="text-align:center;padding:40px">📭 NO PRODUCTS</div>';return;}
    allStoreProducts = d;
    renderStoreProducts();
  }catch(e){g.innerHTML='<div style="text-align:center;padding:40px">❌ LOAD FAILED</div>';toast('Load failed','e');}
}

function renderStoreProducts() {
  const g = document.getElementById('pg');
  const q = (document.getElementById('storeSearch')?.value || '').toLowerCase();
  let filtered = allStoreProducts;
  if (currentStoreCat !== 'ALL') {
    filtered = filtered.filter(p => (p.category || '').toUpperCase() === currentStoreCat);
  }
  if (q) {
    filtered = filtered.filter(p => (p.name || '').toLowerCase().includes(q));
  }
  if (!filtered.length) {
    g.innerHTML = '<div style="text-align:center;padding:40px">🔍 No matching products</div>';
    return;
  }
  g.innerHTML = filtered.map((p, i) => `
    <div class="card ${p.featured ? 'featured' : ''} btn-ripple" onclick="ob('${p._id}')" style="animation:cardFadeIn .6s ease ${i * 0.08}s both">
      ${p.popular ? '<div class="ribbon">🔥 BEST SELLER</div>' : ''}
      ${p.category ? '<div class="cat">' + esc(p.category).toUpperCase() + '</div>' : ''}
      <div class="ic">🔑</div>
      <h3>${esc(p.name)}</h3>
      <div class="dur">${esc(p.duration)}</div>
      ${featsHtml(p)}
      <div class="pr">₹${p.price}<small>INR</small></div>
      <button class="bb">⚡ ʙᴜʏ ɴᴏᴡ</button>
    </div>`).join('');
  setTimeout(init3DTilt, 100);
}

function filterStoreCategory(cat, el) {
  currentStoreCat = cat;
  document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  renderStoreProducts();
}

function filterStoreProducts() { renderStoreProducts(); }

const styleEl = document.createElement('style');
styleEl.textContent = '@keyframes cardFadeIn{from{opacity:0;transform:translateY(40px) scale(.95)}to{opacity:1;transform:translateY(0) scale(1)}}';
document.head.appendChild(styleEl);

async function ls(){try{const r=await fetch('/api/store-stats');const d=await r.json();document.getElementById('ls-keys').textContent=d.keys_sold||0;document.getElementById('ls-users').textContent=d.users||0;document.getElementById('ls-rating').textContent=(d.avg_rating||5.0).toFixed(1);document.getElementById('ls-visits').textContent=d.today_visits||0;}catch(e){}}
async function lf(){try{const r=await fetch('/api/faqs');const d=await r.json();document.getElementById('faqGrid').innerHTML=d.map(f=>`<div class="faq-item" onclick="this.classList.toggle('open')"><h4>${esc(f.q)} <span class="chev">▼</span></h4><p>${esc(f.a)}</p></div>`).join('');}catch(e){}}
async function lt(){try{const r=await fetch('/api/testimonials');const d=await r.json();document.getElementById('testGrid').innerHTML=d.map(t=>`<div class="test-card"><div class="stars">${'★'.repeat(t.stars)}${'☆'.repeat(5-t.stars)}</div><p>"${esc(t.text)}"</p><div class="who">- ${esc(t.who)}</div></div>`).join('');}catch(e){}}
async function la(){try{const r=await fetch('/api/announcement');const d=await r.json();if(d.enabled&&d.text){document.getElementById('annH').textContent='📢 '+(d.title||'ANNOUNCEMENT').toUpperCase();document.getElementById('annB').textContent=d.text;document.getElementById('annPop').classList.add('show');}}catch(e){}}
async function lticker(){try{const r=await fetch('/api/recent-purchases');const d=await r.json();if(!d||!d.length){document.getElementById('tickerTrack').innerHTML='<span class="ticker-item">🎉 BE THE FIRST!</span>';return;}document.getElementById('tickerTrack').innerHTML=d.map(x=>`<span class="ticker-item">🎉 <b>${esc(x.name)}</b> purchased ${esc(x.product)} ⚡</span>`).join('');}catch(e){}}
async function livePurchase(){try{const r=await fetch('/api/recent-purchases');const d=await r.json();if(!d||!d.length)return;const x=d[Math.floor(Math.random()*d.length)];const pop=document.getElementById('livePop');pop.innerHTML=`🎉 <b>${esc(x.name)}</b> just bought <b>${esc(x.product)}</b>`;pop.classList.add('show');setTimeout(()=>pop.classList.remove('show'),5000);}catch(e){}}

function initCountdown(){function tick(){const now=new Date();const istStr=now.toLocaleString('en-US',{timeZone:'Asia/Kolkata'});const istNow=new Date(istStr);const eod=new Date(istNow);eod.setHours(23,59,59,999);const diff=eod-istNow;if(diff<0){['ctH','ctM','ctS'].forEach(id=>document.getElementById(id).textContent='00');return;}const h=Math.floor(diff/3600000);const m=Math.floor((diff%3600000)/60000);const s=Math.floor((diff%60000)/1000);document.getElementById('ctH').textContent=String(h).padStart(2,'0');document.getElementById('ctM').textContent=String(m).padStart(2,'0');document.getElementById('ctS').textContent=String(s).padStart(2,'0');}tick();setInterval(tick,1000);}
initCountdown();
function closeAnn(e){e.stopPropagation();document.getElementById('annPop').classList.remove('show');}

function ob(pid){fetch('/api/product/'+pid).then(r=>r.json()).then(p=>{if(!p||p.error){toast('❌ NOT FOUND','e');return;}
cp=p;couponCode=null;couponDiscount=0;
document.getElementById('bc').innerHTML=`<h3>⚡ ${esc(p.name)}</h3>
<div class="sb">⏱ ${esc(p.duration)}</div>
${featsHtml(p)}
<div class="fg"><label>👤 Your Name</label><input id="bn" placeholder="Enter your name"></div>
<div class="fg"><label>📧 Email</label><input id="be" type="email" placeholder="you@example.com"></div>
<div class="fg"><label>📱 Phone</label><input id="bp" type="tel" maxlength="10" placeholder="9876543210"></div>
<div class="fg"><label>📨 Telegram ID</label><input id="btg" placeholder="Get from @userinfobot"></div>
<div class="fg"><label>🎟️ Coupon (optional)</label><div class="coupon-row"><input id="couponIn" placeholder="FLASH20"><button onclick="applyCoupon()">✅</button></div><div id="couponMsg" style="font-size:11px;margin-top:6px"></div></div>
<div class="tb2"><span class="l">💰 TOTAL</span><span class="a" id="totalAmt">₹${p.price}</span></div>
<div class="act"><button class="bc" onclick="cm()">❌ CANCEL</button><button class="bp" id="pb" onclick="pp()">💳 PAY ₹${p.price}</button></div>`;
document.getElementById('bm').classList.add('act');});}

async function applyCoupon(){const code=document.getElementById('couponIn').value.trim();if(!code){toast('⚠️ ENTER CODE','e');return;}const r=await fetch('/api/validate-coupon',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:code,product_id:cp._id})});const d=await r.json();const m=document.getElementById('couponMsg');if(!d.valid){m.style.color='#ff4444';m.textContent='❌ '+(d.error||'Invalid').toUpperCase();couponCode=null;document.getElementById('totalAmt').textContent='₹'+cp.price;return;}couponCode=code;couponDiscount=d.discount;const nt=Math.max(0,cp.price-d.discount);m.style.color='#00FF88';m.textContent='✅ ₹'+d.discount+' OFF';document.getElementById('totalAmt').textContent='₹'+nt;document.getElementById('pb').textContent='💳 PAY ₹'+nt;toast('🎉 COUPON APPLIED','s');}

async function pp(){const n=document.getElementById('bn').value.trim();const e=document.getElementById('be').value.trim();const ph=document.getElementById('bp').value.trim();const tg=document.getElementById('btg').value.trim();
if(!n){toast('⚠️ ENTER NAME','e');return;}
if(!tg||!/^\\d+$/.test(tg)){toast('⚠️ VALID TG ID','e');return;}
const b=document.getElementById('pb');b.innerHTML='<span class="ld"></span> CREATING...';b.disabled=true;
try{const r=await fetch('/api/create-order',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product_id:cp._id,customer_name:n,customer_email:e,customer_phone:ph,telegram_id:tg,coupon:couponCode})});
const d=await r.json();
if(!d.success){toast('❌ '+(d.error||'FAILED').toUpperCase(),'e');b.innerHTML='💳 PAY';b.disabled=false;return;}
curOid=d.order_id;
if(d.free){sw({key:d.key},d.order_id);return;}
document.getElementById('bc').innerHTML=`<h3>💳 COMPLETE PAYMENT</h3><div class="sb">📱 Scan QR</div>
<div class="qr"><div class="ab">₹${d.amount}</div><img src="https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(d.upi_intent||d.qr_url||d.order_id)}" alt="QR"><div class="u">🆔 ${d.order_id}</div></div>
<div class="ps"><div class="ld"></div> ⏳ WAITING FOR PAYMENT...</div>
<div style="margin-top:18px;display:flex;gap:10px">${d.checkout_url?`<a href="${d.checkout_url}" target="_blank" class="bp" style="text-decoration:none;flex:1">📱 OPEN UPI</a>`:''}<button class="bc" onclick="cm()">CLOSE</button></div>`;
sp(d.order_id);}catch(err){toast('❌ '+err.message,'e');b.innerHTML='💳 PAY';b.disabled=false;}}

function sp(oid){if(pi)clearInterval(pi);let a=0;pi=setInterval(async()=>{a++;if(a>120){clearInterval(pi);return;}try{const r=await fetch('/api/order-status/'+oid);const d=await r.json();if(d.status==='success'){clearInterval(pi);sw(d,oid);}}catch(e){}},3000);}

function sw(d,oid){curOid=oid||curOid;
document.getElementById('bc').innerHTML=`<div style="text-align:center;padding:16px 0"><div style="font-size:64px">✅🎉✅</div><h3 style="margin-top:14px">🎉 SUCCESS! 🎉</h3></div>
<div class="kr"><div style="font-size:11px;color:rgba(255,255,255,.6);text-transform:uppercase;letter-spacing:2px;font-weight:900;margin-bottom:10px">⚡ YOUR KEY ⚡</div><div class="cd">${d.key}</div><button class="cpb" onclick="cpt('${d.key}')">📋 ᴄᴏᴘʏ ᴋᴇʏ</button></div>
<div style="margin-top:16px;padding:14px;background:rgba(255,215,0,.05);border:1px solid rgba(255,215,0,.3);border-radius:12px;font-size:12px;color:rgba(255,255,255,.75);line-height:1.8"><b style="color:#FFD700">📖 HOW TO USE:</b><br>1️⃣ Join: @{{ channel }}<br>2️⃣ Open: @{{ bot }}<br>3️⃣ Send: <code>/redeem ${d.key}</code></div>
<a href="https://t.me/{{ bot }}" target="_blank" class="bp" style="width:100%;margin-top:18px;display:block">🚀 ᴏᴘᴇɴ ʙᴏᴛ</a>
<div style="margin-top:10px"><button class="bc" style="width:100%" onclick="showRate()">⭐ ʀᴀᴛᴇ ᴜꜱ</button></div>
<div style="margin-top:8px"><button class="bc" style="width:100%" onclick="downloadInvoice('${curOid}')">🧾 ɪɴᴠᴏɪᴄᴇ</button></div>
<div style="margin-top:8px"><button class="bc" style="width:100%" onclick="backToStore()">🔙 ʙᴀᴄᴋ</button></div>`;
toast('🎉 KEY DELIVERED','s');}

function downloadInvoice(oid){window.open('/invoice/'+oid,'_blank');}

function showRate(){document.getElementById('bc').innerHTML=`<div class="rate-wrap"><h3>⭐ RATE US ⭐</h3><p>How was your purchase?</p><div class="rate-stars" id="rateStars"><span class="star" onclick="setStar(1)">★</span><span class="star" onclick="setStar(2)">★</span><span class="star" onclick="setStar(3)">★</span><span class="star" onclick="setStar(4)">★</span><span class="star" onclick="setStar(5)">★</span></div><input id="rateComment" placeholder="💬 Optional..." style="width:100%;padding:11px 14px;background:rgba(0,0,0,.4);border:1px solid rgba(255,215,0,.3);border-radius:11px;color:#fff;font-size:12.5px;outline:none;margin-bottom:14px"><button class="rate-submit" id="rateBtn" onclick="submitRate()" disabled>📤 ꜱᴜʙᴍɪᴛ</button><div style="margin-top:14px"><button class="bc" onclick="backToStore()">⏭️ ꜱᴋɪᴘ</button></div></div>`;}

let ratingStars=0;
function setStar(n){ratingStars=n;document.querySelectorAll('#rateStars .star').forEach((s,i)=>s.classList.toggle('lit',i<n));document.getElementById('rateBtn').disabled=false;}
async function submitRate(){if(!ratingStars){toast('⚠️ SELECT','e');return;}const c=document.getElementById('rateComment').value.trim();try{const r=await fetch('/api/rate-order',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({order_id:curOid,stars:ratingStars,comment:c})});const d=await r.json();if(d.success){document.getElementById('bc').innerHTML=`<div class="rate-wrap"><div style="font-size:64px">🙏</div><h3>❤️ THANK YOU ❤️</h3><div style="margin-top:20px"><button class="bc" onclick="backToStore()">🔙 ʙᴀᴄᴋ</button></div></div>`;ls();}else toast('❌','e');}catch(e){toast('❌','e');}}
function backToStore(){cm();window.scrollTo({top:0,behavior:'smooth'});}

lp();ls();lf();lt();la();lticker();
setInterval(lticker, 15000);
setInterval(ls, 30000);
setInterval(livePurchase, 25000);
setTimeout(livePurchase, 8000);

async function trackOrder(){const id=document.getElementById('trackInput').value.trim();const res=document.getElementById('trackResult');if(!id){toast('⚠️ ENTER ID','e');return;}res.innerHTML='<div style="text-align:center"><div class="ld"></div></div>';res.classList.add('show');try{const r=await fetch('/api/track/'+encodeURIComponent(id));const d=await r.json();if(!d.found){res.innerHTML='<div style="color:#ff4444;text-align:center">❌ NOT FOUND</div>';return;}let sc2=d.status==='success'?'#00FF88':d.status==='pending'?'#FFA500':'#FF0055';res.innerHTML=`<div>🆔 <b>ORDER:</b> <span style="font-family:monospace;color:#FFD700">${d.order_id}</span></div><div style="margin-top:8px">📦 <b>PRODUCT:</b> ${esc(d.product_name)}</div><div style="margin-top:8px">💰 <b>AMOUNT:</b> ₹${d.amount}</div><div style="margin-top:8px">📊 <b>STATUS:</b> <span style="color:${sc2};font-weight:900;text-transform:uppercase">${d.status}</span></div>${d.key?`<div style="margin-top:12px;padding:10px;background:rgba(0,255,136,.05);border:1px solid #00FF88;border-radius:10px;text-align:center"><b style="color:#00FF88;font-size:11px">🔑 YOUR KEY</b><br><span style="font-family:monospace;color:#00FF88;font-size:13px;font-weight:700">${d.key}</span></div>`:''}`;}catch(e){res.innerHTML='<div style="color:#ff4444;text-align:center">❌ ERROR</div>';}}

let chatOpen=false, pendingFile=null;
function getChatId(){let c=localStorage.getItem('flash_chat_id');if(!c){c='U'+Date.now()+Math.random().toString(36).substring(2,10);localStorage.setItem('flash_chat_id',c);}return c;}
function getUserName(){return localStorage.getItem('flash_chat_name')||'';}
function toggleChat(){chatOpen=!chatOpen;document.getElementById('chatBox').classList.toggle('open',chatOpen);if(chatOpen)initChatView();}
function initChatView(){const name=getUserName();const sv=document.getElementById('chatStartView');const mv=document.getElementById('chatMsgView');if(name){sv.style.display='none';mv.style.display='flex';loadChat();}else{sv.style.display='block';mv.style.display='none';}}
function startChat(){const n=document.getElementById('chatName').value.trim();if(!n){toast('⚠️ ENTER NAME','e');return;}localStorage.setItem('flash_chat_name',n);const sv=document.getElementById('chatStartView');const mv=document.getElementById('chatMsgView');sv.style.display='none';mv.style.display='flex';loadChat();}
function fileEmoji(n){const e=(n.split('.').pop()||'').toLowerCase();if(['jpg','jpeg','png','gif','webp'].includes(e))return'🖼️';if(['mp3','wav','m4a','ogg'].includes(e))return'🎵';if(['mp4','webm','mov'].includes(e))return'🎥';if(['pdf'].includes(e))return'📕';if(['zip','rar'].includes(e))return'📦';return'📄';}
function previewFile(input){const f=input.files&&input.files[0];if(!f)return;pendingFile=f;const pv=document.getElementById('chatPreview');let thumb='';if(f.type.startsWith('image/')){const url=URL.createObjectURL(f);thumb=`<img src="${url}">`;}else{thumb=`<span style="font-size:28px">${fileEmoji(f.name)}</span>`;}pv.innerHTML=`<div class="pv">${thumb}<div class="pv-n">${esc(f.name)}<br><span style="opacity:.6;font-size:10px">${(f.size/1024).toFixed(1)} KB</span></div><button class="pv-x" onclick="clearFile()">✕</button></div>`;pv.classList.add('show');}
function clearFile(){pendingFile=null;document.getElementById('chatPreview').classList.remove('show');document.getElementById('chatPreview').innerHTML='';document.getElementById('chatFile').value='';}
async function uploadFile(file, caption, isVoice){
  const cid = getChatId(); const name = getUserName();
  const fd = new FormData();
  fd.append('chat_id', cid); fd.append('name', name); fd.append('caption', caption||'');
  if(isVoice) fd.append('voice','1');
  fd.append('file', file, file.name||'voice.webm');
  try{const r=await fetch('/api/chat/upload',{method:'POST',body:fd});const d=await r.json();
    if(!d.success) toast('❌ '+(d.error||'FAIL').toUpperCase(),'e'); else loadChat();return d.success;}catch(e){toast('❌','e');return false;}
}
let mediaRecorder=null, recChunks=[], recording=false;
async function toggleRecord(){const btn=document.getElementById('recBtn');
  if(!recording){try{const stream=await navigator.mediaDevices.getUserMedia({audio:true});mediaRecorder=new MediaRecorder(stream);recChunks=[];
    mediaRecorder.ondataavailable=e=>{if(e.data.size>0)recChunks.push(e.data);};
    mediaRecorder.onstop=async()=>{stream.getTracks().forEach(t=>t.stop());const blob=new Blob(recChunks,{type:'audio/webm'});const file=new File([blob],`voice_${Date.now()}.webm`,{type:'audio/webm'});await uploadFile(file,'',true);};
    mediaRecorder.start();recording=true;btn.classList.add('recording');btn.textContent='⏹';
  }catch(e){toast('❌ MIC DENIED','e');}} else {try{mediaRecorder.stop();}catch(e){}recording=false;btn.classList.remove('recording');btn.textContent='🎤';}}
async function sendChat(){const inp=document.getElementById('chatMsg');const t=inp.value.trim();if(!t&&!pendingFile)return;
  if(pendingFile){const f=pendingFile;clearFile();inp.value='';await uploadFile(f,t,false);return;}
  inp.value='';const cid=getChatId();const name=getUserName();const b=document.getElementById('chatBody');
  const time=new Date().toLocaleTimeString('en-IN',{timeZone:'Asia/Kolkata',hour:'2-digit',minute:'2-digit'});
  b.innerHTML+=`<div class="chat-msg user"><div class="bbl">${esc(t)}</div><div class="tm">${time} IST · 👤 You</div></div>`;b.scrollTop=b.scrollHeight;
  try{const r=await fetch('/api/chat/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({chat_id:cid,name,text:t})});const d=await r.json();if(!d.success)toast('❌','e');}catch(e){toast('❌','e');}}
async function loadChat(){try{const cid=getChatId();const r=await fetch('/api/chat/messages?chat_id='+cid);const d=await r.json();const b=document.getElementById('chatBody');
  if(!d||!d.length){b.innerHTML='<div class="chat-msg system"><div class="bbl">💬 Send us a message!</div></div>';return;}
  b.innerHTML=d.map(m=>{let inner='';
    if(m.media_type==='photo' && m.media_url){inner=`<img src="${m.media_url}" onclick="window.open('${m.media_url}','_blank')">`;if(m.caption)inner+=`<div style="margin-top:6px">${esc(m.caption)}</div>`;}
    else if(m.media_type==='voice'||m.media_type==='audio')inner=`<audio controls src="${m.media_url}"></audio>`;
    else if(m.media_type==='video')inner=`<video controls src="${m.media_url}" style="max-width:100%"></video>`;
    else if(m.media_type==='document')inner=`<a href="${m.media_url}" target="_blank" class="file-chip">📄 <span>${esc(m.media_name||'file')}</span></a>`;
    else inner=esc(m.text||'');
    return `<div class="chat-msg ${m.sender==='user'?'user':'owner'}"><div class="bbl">${inner}</div><div class="tm">${esc(m.time)} · ${m.sender==='user'?'👤 You':'🎧 Support'}</div></div>`;}).join('');
  b.scrollTop=b.scrollHeight;}catch(e){}}
setInterval(()=>{if(chatOpen&&getUserName())loadChat();},8000);

async function checkPremiumLock() {
  try {
    const r = await fetch('/api/public-lock-check');
    const d = await r.json();
    if (d && !d.is_premium) {
      setTimeout(() => {
        const overlay = document.getElementById('premiumLock');
        const progress = document.getElementById('lockProgressBar');
        const text = document.getElementById('lockProgressText');
        if (progress) progress.style.width = (d.progress || 0) + '%';
        if (text) text.textContent = (d.progress || 0) + '% UNLOCKED';
        if (overlay) overlay.style.display = 'flex';
      }, 3000);
    }
  } catch (e) {}
}
window.addEventListener('load', () => setTimeout(checkPremiumLock, 4000));

console.log('%c⚡ FLASH PREMIUM v15 ⚡', 'color:#FFD700;font-size:20px;font-weight:900;text-shadow:0 0 20px #FFD700');
console.log('%cNeon UI + 3D Cards + Premium Toasts Loaded', 'color:#00FFFF;font-size:11px;letter-spacing:2px');
</script></body></html>"""

@app.route("/")
def index():
    return render_template_string(STORE_HTML, bg=setting("background_image",BG_IMG),
        bot=BOT_USER, channel=CHANNEL, power=POWER_BY, logo=setting("logo_image",LOGO_IMG))

# ================= USER PANEL =================
UPANEL_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>👤 USER PANEL · FLASH PREMIUM v15</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=JetBrains+Mono:wght@600&display=swap" rel="stylesheet">
<style>*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;background:#05050A;color:#fff;min-height:100vh;overflow-x:hidden}
body::before{content:'';position:fixed;inset:0;background:radial-gradient(at 20% 30%,#FFD70015 0px,transparent 50%),radial-gradient(at 80% 20%,#FF005515 0px,transparent 50%),radial-gradient(at 50% 80%,#00FFFF15 0px,transparent 50%),#05050A;background-size:200% 200%;animation:auroraMove 20s ease infinite;filter:blur(60px) brightness(.6);z-index:-2;transform:scale(1.2)}
@keyframes auroraMove{0%,100%{background-position:0% 0%}50%{background-position:100% 100%}}
body::after{content:'';position:fixed;inset:0;background-image:url('{{ bg }}');background-size:cover;background-position:center;opacity:.08;mix-blend-mode:overlay;z-index:-1;pointer-events:none}
.tb{position:fixed;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#FFD700,#00FFFF,#FF0055,#FFD700);background-size:400%;animation:sl 3s linear infinite;z-index:100}
@keyframes sl{0%{background-position:0 0}100%{background-position:400% 0}}
.ist-badge{position:fixed;top:20px;right:20px;background:rgba(10,10,15,.95);backdrop-filter:blur(20px);border:1px solid #FFD70066;border-radius:14px;padding:10px 16px;font-size:12px;font-weight:900;color:#00FFFF;letter-spacing:1.5px;z-index:999;font-family:'JetBrains Mono',monospace;box-shadow:0 0 15px #FFD70022;text-shadow:0 0 8px #00FFFF88}
.hd{padding:20px;background:rgba(10,10,15,.85);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,215,0,.2);position:sticky;top:4px;z-index:50;box-shadow:0 5px 20px #FFD70011}
.hdc{max-width:1200px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px}
.br{display:flex;align-items:center;gap:12px}
.bri{width:48px;height:48px;border-radius:14px;overflow:hidden;box-shadow:0 0 20px #FFD70066}
.bri img{width:100%;height:100%;object-fit:cover}
.brt h2{font-size:18px;font-weight:900;letter-spacing:2px;text-transform:uppercase;background:linear-gradient(135deg,#FFD700,#FF0055);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 5px #FFD70055)}
.brt p{font-size:10px;color:rgba(255,255,255,.5);letter-spacing:3px;text-transform:uppercase;font-weight:800;margin-top:2px}
.ha{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.ub{padding:8px 16px;background:rgba(255,215,0,.05);border:1px solid rgba(255,215,0,.4);border-radius:24px;font-size:11px;font-weight:800;color:#FFD700;letter-spacing:1px;box-shadow:0 0 10px #FFD70022;text-shadow:0 0 5px #FFD70088}
.bts{padding:8px 16px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-radius:10px;color:rgba(255,255,255,.7);font-size:11px;font-weight:800;cursor:pointer;text-decoration:none;transition:.25s;letter-spacing:1.5px;text-transform:uppercase}
.bts:hover{background:rgba(255,255,255,.1);color:#fff}
.bts.r{color:#FF0055;border-color:rgba(255,0,85,.35);text-shadow:0 0 5px #FF005588}
.bts.r:hover{background:rgba(255,0,85,.1);border-color:#FF0055;box-shadow:0 0 10px #FF005544}
.notif-btn{position:relative}
.notif-badge{position:absolute;top:-6px;right:-6px;background:#FF0055;color:#fff;font-size:9px;font-weight:900;width:18px;height:18px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:2px solid #05050A;animation:pulseRed 2s infinite;box-shadow:0 0 10px #FF0055}
@keyframes pulseRed{0%,100%{box-shadow:0 0 0 0 rgba(255,0,85,.7)}50%{box-shadow:0 0 0 8px rgba(255,0,85,0)}}
.cont{max-width:1200px;margin:0 auto;padding:24px 20px}
.wb{background:linear-gradient(135deg,rgba(255,215,0,.1),rgba(255,0,85,.05));border:2px solid rgba(255,215,0,.4);border-radius:22px;padding:28px;margin-bottom:24px;text-align:center;position:relative;overflow:hidden;box-shadow:0 0 30px #FFD70022}
.wb.vip{background:linear-gradient(135deg,rgba(255,0,85,.15),rgba(255,215,0,.1),rgba(0,255,255,.05));border:2px solid #FF0055;box-shadow:0 0 60px #FF005544}
.wb .vip-crown{position:absolute;top:-20px;right:-20px;font-size:100px;opacity:.06;transform:rotate(-20deg)}
.wb .ic{font-size:60px;filter:drop-shadow(0 0 30px #FFD700cc);animation:fl 2.5s infinite}
@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
.wb h2{font-size:26px;font-weight:900;margin-top:12px;letter-spacing:3px;text-transform:uppercase;background:linear-gradient(135deg,#FFD700,#00FFFF,#FF0055);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 10px #FFD70055)}
.wb p{color:rgba(255,255,255,.7);font-size:12px;margin-top:10px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase}
.ug{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin-bottom:24px}
.uc{background:rgba(10,10,15,.85);backdrop-filter:blur(24px) saturate(180%);border:1px solid rgba(255,255,255,.1);border-left:4px solid #FFD700;border-radius:16px;padding:18px;transition:all .4s cubic-bezier(.34,1.56,.64,1);position:relative;overflow:hidden;box-shadow:0 0 15px #FFD70011}
.uc:nth-child(even){border-left-color:#00FFFF;box-shadow:0 0 15px #00FFFF11}
.uc:nth-child(3n){border-left-color:#FF0055;box-shadow:0 0 15px #FF005511}
.uc:nth-child(4n){border-left-color:#00FF88;box-shadow:0 0 15px #00FF8811}
.uc:hover{transform:translateY(-6px) scale(1.02);border-color:rgba(255,215,0,.5);box-shadow:0 20px 50px rgba(255,215,0,.2);filter:brightness(1.2)}
.uc .ic{font-size:22px;margin-bottom:8px;filter:drop-shadow(0 0 8px currentColor)}
.uc .n{font-size:22px;font-weight:900;font-family:'JetBrains Mono',monospace;background:linear-gradient(135deg,#fff,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 8px #FFD70055)}
.uc .l{font-size:9.5px;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:1.8px;font-weight:800;margin-top:4px}
.tier-box{background:rgba(10,10,15,.85);backdrop-filter:blur(20px);border:1px solid rgba(255,215,0,.3);border-radius:18px;padding:22px;margin-bottom:24px;box-shadow:0 0 20px #FFD70011}
.tier-hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:10px}
.tier-hdr h3{font-size:15px;font-weight:900;letter-spacing:2px;text-transform:uppercase;color:#FFD700;text-shadow:0 0 8px #FFD70055}
.tier-badge{padding:6px 14px;border-radius:20px;font-size:11px;font-weight:900;letter-spacing:2px;text-transform:uppercase;background:rgba(255,215,0,.1);color:#FFD700;border:1px solid rgba(255,215,0,.4);box-shadow:0 0 10px #FFD70033;text-shadow:0 0 5px #FFD70088}
.tier-bar-wrap{background:rgba(0,0,0,.4);border-radius:20px;height:14px;overflow:hidden;position:relative;margin-bottom:8px;border:1px solid rgba(255,255,255,.1)}
.tier-bar{height:100%;background:linear-gradient(90deg,#FFD700,#00FFFF,#FF0055);border-radius:20px;transition:width .8s;box-shadow:0 0 20px #FFD700cc}
.tier-info{display:flex;justify-content:space-between;font-size:11px;color:rgba(255,255,255,.6);font-weight:700;letter-spacing:1px}
.badges-wrap{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px;margin-bottom:24px}
.badge{background:rgba(10,10,15,.85);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.1);border-radius:14px;padding:14px;text-align:center;transition:.3s;position:relative;overflow:hidden}
.badge:hover{transform:translateY(-3px);box-shadow:0 10px 30px rgba(255,215,0,.2);border-color:rgba(255,215,0,.4)}
.badge .bdg-ic{font-size:28px;margin-bottom:6px;filter:drop-shadow(0 0 10px currentColor)}
.badge .bdg-n{font-size:10px;font-weight:900;letter-spacing:1.5px;text-transform:uppercase;text-shadow:0 0 5px currentColor}
.kr{background:linear-gradient(135deg,rgba(0,255,136,.08),rgba(0,255,255,.05));border:2px solid rgba(0,255,136,.5);border-radius:20px;padding:24px;margin-bottom:24px;text-align:center;box-shadow:0 0 30px #00FF8822}
.kr h3{font-size:18px;font-weight:900;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;color:#00FF88;text-shadow:0 0 10px #00FF8888}
.kr p{font-size:12px;color:rgba(255,255,255,.6);margin-bottom:16px;letter-spacing:1px;text-transform:uppercase}
.kc{font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:900;color:#00FF88;letter-spacing:2px;padding:14px;background:rgba(0,0,0,.4);border-radius:12px;margin-bottom:14px;word-break:break-all;text-shadow:0 0 15px #00FF8888;border:1px solid rgba(0,255,136,.2)}
.ka{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.ka button,.ka a{padding:12px 22px;border:1px solid;border-radius:11px;font-size:11px;font-weight:900;cursor:pointer;letter-spacing:2px;text-transform:uppercase;text-decoration:none;font-family:inherit;display:inline-flex;align-items:center;gap:6px;transition:.25s;text-shadow:0 0 8px currentColor}
.ka .cp{background:rgba(255,215,0,.05);border-color:#FFD700;color:#FFD700}
.ka .cp:hover{background:#FFD700;color:#000;box-shadow:0 0 20px #FFD70066;text-shadow:none}
.ka .ob{background:rgba(0,255,136,.05);border-color:#00FF88;color:#00FF88}
.ka .ob:hover{background:#00FF88;color:#000;box-shadow:0 0 20px #00FF8866;text-shadow:none}
.st2{text-align:center;font-size:22px;font-weight:900;margin-bottom:8px;letter-spacing:3px;text-transform:uppercase;background:linear-gradient(135deg,#FFD700,#00FFFF,#FF0055);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 10px #FFD70055)}
.ss{text-align:center;font-size:11px;color:rgba(255,255,255,.5);margin-bottom:20px;letter-spacing:2px;text-transform:uppercase;font-weight:700}
.tabs{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;justify-content:center}
.tab{padding:9px 18px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-radius:12px;font-size:11px;font-weight:800;cursor:pointer;letter-spacing:1.5px;text-transform:uppercase;color:rgba(255,255,255,.7);transition:.25s}
.tab.active{background:rgba(255,215,0,.1);color:#FFD700;border-color:#FFD700;box-shadow:0 0 15px #FFD70044;text-shadow:0 0 8px #FFD70088}
.tab-content{display:none}
.tab-content.active{display:block}
.ref-box{background:linear-gradient(135deg,rgba(255,215,0,.08),rgba(0,255,255,.05));border:1px solid rgba(255,215,0,.4);border-radius:18px;padding:20px;margin-bottom:24px;text-align:center;box-shadow:0 0 20px #FFD70011}
.ref-box h4{font-size:14px;color:#FF0055;font-weight:900;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;text-shadow:0 0 8px #FF005588}
.ref-box p{font-size:12px;color:rgba(255,255,255,.6);margin-bottom:12px}
.ref-url{font-family:'JetBrains Mono',monospace;font-size:12px;color:#00FFFF;background:rgba(0,0,0,.4);padding:10px;border-radius:10px;word-break:break-all;margin-bottom:10px;border:1px solid rgba(0,255,255,.2)}
.ref-box button{padding:10px 20px;background:rgba(255,215,0,.05);border:1px solid #FFD700;border-radius:10px;color:#FFD700;font-size:11px;font-weight:900;cursor:pointer;letter-spacing:2px;text-transform:uppercase;font-family:inherit;transition:.3s;text-shadow:0 0 5px #FFD70088}
.ref-box button:hover{background:#FFD700;color:#000;box-shadow:0 0 15px #FFD70066;text-shadow:none}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-bottom:24px}
.stp{background:rgba(10,10,15,.85);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.1);border-bottom:3px solid #FFD700;border-radius:18px;padding:22px;position:relative;overflow:hidden;transition:.35s;box-shadow:0 0 15px #FFD70011}
.stp:nth-child(2){border-bottom-color:#00FFFF;box-shadow:0 0 15px #00FFFF11}
.stp:nth-child(3){border-bottom-color:#FF0055;box-shadow:0 0 15px #FF005511}
.stp:hover{transform:translateY(-5px);border-color:rgba(255,215,0,.5);box-shadow:0 20px 60px rgba(255,215,0,.2);filter:brightness(1.2)}
.stp .n{position:absolute;top:14px;right:18px;font-size:52px;font-weight:900;color:rgba(255,255,255,.05);line-height:1}
.stp .ic{font-size:36px;margin-bottom:12px;filter:drop-shadow(0 0 15px currentColor)}
.stp h3{font-size:14px;font-weight:900;margin-bottom:8px;letter-spacing:2px;text-transform:uppercase;color:#FFD700;text-shadow:0 0 8px #FFD70055}
.stp p{font-size:12px;color:rgba(255,255,255,.6);line-height:1.7;font-weight:600}
.stp .ab{display:inline-block;margin-top:14px;padding:10px 18px;border:1px solid;border-radius:11px;font-size:11px;font-weight:900;text-decoration:none;letter-spacing:2px;text-transform:uppercase;transition:.25s;cursor:pointer;font-family:inherit;text-shadow:0 0 5px currentColor}
.stp .ab.b{background:rgba(255,215,0,.05);border-color:#FFD700;color:#FFD700}
.stp .ab.b:hover{background:#FFD700;color:#000;text-shadow:none;box-shadow:0 0 15px #FFD70066}
.stp .ab.g{background:rgba(0,255,255,.05);border-color:#00FFFF;color:#00FFFF}
.stp .ab.g:hover{background:#00FFFF;color:#000;text-shadow:none;box-shadow:0 0 15px #00FFFF66}
.stp .ab.p{background:rgba(255,0,85,.05);border-color:#FF0055;color:#FF0055}
.stp .ab.p:hover{background:#FF0055;color:#fff;text-shadow:none;box-shadow:0 0 15px #FF005566}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:18px}
.card{background:rgba(10,10,15,.85);border:1px solid rgba(255,255,255,.1);border-left:4px solid #FFD700;border-radius:22px;padding:24px;transition:.4s;cursor:pointer;box-shadow:0 0 15px #FFD70011}
.card:hover{transform:translateY(-6px);border-color:rgba(255,215,0,.6);box-shadow:0 20px 60px rgba(255,215,0,.2);filter:brightness(1.2)}
.card .ic{font-size:36px;margin-bottom:12px;filter:drop-shadow(0 0 10px #FFD700cc)}
.card h3{font-size:16px;font-weight:900;margin-bottom:6px;letter-spacing:1.5px;text-transform:uppercase;color:#FFD700;text-shadow:0 0 8px #FFD70055}
.card .dur{font-size:10.5px;color:rgba(255,255,255,.55);text-transform:uppercase;letter-spacing:2px;font-weight:700;margin-bottom:14px}
.card .pr{font-size:30px;font-weight:900;font-family:'JetBrains Mono',monospace;background:linear-gradient(135deg,#fff,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 10px #FFD70055)}
.card .bb{display:block;width:100%;margin-top:16px;padding:12px;background:rgba(255,215,0,.05);border:1px solid #FFD700;border-radius:11px;color:#FFD700;font-size:11px;font-weight:900;cursor:pointer;letter-spacing:2px;text-transform:uppercase;font-family:inherit;transition:.3s;text-shadow:0 0 8px #FFD70088}
.card .bb:hover{background:#FFD700;color:#000;box-shadow:0 0 20px #FFD70066;text-shadow:none}
.tc2{position:fixed;top:20px;right:20px;z-index:2000;display:flex;flex-direction:column;gap:10px;max-width:340px}
.tst{background:rgba(10,10,15,.98);border:1px solid rgba(255,255,255,.15);border-left:4px solid #FFD700;border-radius:14px;padding:14px 18px;font-size:12.5px;font-weight:700;box-shadow:0 15px 50px rgba(0,0,0,.6), 0 0 20px #FFD70022;animation:ti .4s;color:#fff}
.tst.s{border-left-color:#00FF88;box-shadow:0 0 20px #00FF8822}
@keyframes ti{from{opacity:0;transform:translateX(120px)}to{opacity:1;transform:translateX(0)}}
footer{text-align:center;padding:40px 20px 30px;color:rgba(255,255,255,.3);font-size:11px;font-weight:600;letter-spacing:2px;text-transform:uppercase}
footer .fl{background:linear-gradient(135deg,#FFD700,#00FFFF,#FF0055);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:900;filter:drop-shadow(0 0 8px #FFD70055)}
.orders-list{display:flex;flex-direction:column;gap:10px;margin-top:14px}
.order-row{background:rgba(10,10,15,.75);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.1);border-radius:14px;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;transition:.3s}
.order-row:hover{border-color:rgba(255,215,0,.5);box-shadow:0 0 15px #FFD70022}
.order-row .oi{font-family:'JetBrains Mono',monospace;font-size:11px;color:#FFD700;font-weight:700;text-shadow:0 0 5px #FFD70055}
.order-row .op{font-size:13px;font-weight:700;color:#fff;margin-top:4px}
.order-row .oa{font-size:12px;color:rgba(255,255,255,.5);margin-top:4px}
.bdg{display:inline-block;padding:4px 11px;border-radius:20px;font-size:10px;font-weight:900;letter-spacing:1px;text-transform:uppercase}
.bgs{background:rgba(0,255,136,.1);color:#00FF88;border:1px solid rgba(0,255,136,.35);box-shadow:0 0 10px #00FF8822;text-shadow:0 0 5px #00FF8855}
.bgd{background:rgba(255,0,85,.1);color:#FF0055;border:1px solid rgba(255,0,85,.35);text-shadow:0 0 5px #FF005555}
.bgw{background:rgba(255,165,0,.1);color:#FFA500;border:1px solid rgba(255,165,0,.35);text-shadow:0 0 5px #FFA50055}
.notif-panel{position:fixed;top:80px;right:20px;width:380px;max-width:calc(100vw - 40px);background:rgba(10,10,15,.98);backdrop-filter:blur(30px);border:1px solid #FFD70066;border-radius:18px;box-shadow:0 20px 60px rgba(0,0,0,.8), 0 0 30px #FFD70022;z-index:1600;max-height:500px;overflow-y:auto;display:none}
.notif-panel.open{display:block}
.notif-hdr{padding:16px 20px;border-bottom:1px solid rgba(255,255,255,.08);font-size:13px;font-weight:900;letter-spacing:2px;text-transform:uppercase;color:#FFD700;text-shadow:0 0 8px #FFD70088}
.notif-item{padding:14px 20px;border-bottom:1px solid rgba(255,255,255,.05);transition:.2s;cursor:pointer}
.notif-item:hover{background:rgba(255,215,0,.05)}
.notif-item.unread{border-left:3px solid #FFD700;background:rgba(255,215,0,.03)}
.notif-item .nf-title{font-size:12px;font-weight:900;letter-spacing:1px;text-transform:uppercase;color:#fff;margin-bottom:4px}
.notif-item .nf-body{font-size:12px;color:rgba(255,255,255,.7);line-height:1.5}
.notif-item .nf-time{font-size:10px;color:rgba(255,255,255,.4);margin-top:6px}
.wallet-list{display:flex;flex-direction:column;gap:8px;margin-top:14px}
.wallet-row{background:rgba(10,10,15,.75);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:12px 16px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}
.wallet-row .wl-note{font-size:12px;color:rgba(255,255,255,.7)}
.wallet-row .wl-time{font-size:10px;color:rgba(255,255,255,.4);margin-top:3px}
.wallet-row .wl-amt{font-family:'JetBrains Mono',monospace;font-weight:900;font-size:14px}
.wallet-row .wl-amt.credit{color:#00FF88;text-shadow:0 0 8px #00FF8866}
.wallet-row .wl-amt.debit{color:#FF0055;text-shadow:0 0 8px #FF005566}
.streak-box{background:linear-gradient(135deg,rgba(0,255,136,.08),rgba(0,255,255,.05));border:1px solid rgba(0,255,136,.4);border-radius:18px;padding:20px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;box-shadow:0 0 20px #00FF8811}
.streak-box .sb-info h4{font-size:14px;font-weight:900;color:#00FF88;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;text-shadow:0 0 8px #00FF8888}
.streak-box .sb-info p{font-size:11.5px;color:rgba(255,255,255,.6);letter-spacing:1px}
.streak-box .sb-count{font-size:42px;font-weight:900;font-family:'JetBrains Mono',monospace;background:linear-gradient(135deg,#00FF88,#00FFFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 15px #00FF8866)}
.wheel-section{background:linear-gradient(135deg,rgba(255,215,0,.08),rgba(255,0,85,.05));border:2px solid rgba(255,215,0,.4);border-radius:20px;padding:24px;margin-bottom:24px;text-align:center;box-shadow:0 0 30px #FFD70022}
.wheel-section h3{font-size:18px;font-weight:900;letter-spacing:2px;text-transform:uppercase;background:linear-gradient(135deg,#FFD700,#FF0055);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px;filter:drop-shadow(0 0 8px #FFD70055)}
.wheel-section p{font-size:12px;color:rgba(255,255,255,.6);margin-bottom:18px;letter-spacing:1px;text-transform:uppercase}
.wheel-btn{padding:14px 32px;background:rgba(255,215,0,.05);border:1px solid #FFD700;border-radius:14px;color:#FFD700;font-size:13px;font-weight:900;cursor:pointer;letter-spacing:2px;text-transform:uppercase;font-family:inherit;animation:wheelGlow 2s infinite;transition:.3s;text-shadow:0 0 8px #FFD70088}
@keyframes wheelGlow{0%,100%{box-shadow:0 10px 30px #FFD70033}50%{box-shadow:0 15px 50px #FFD70066,0 0 40px #FF005544}}
.wheel-btn:hover{background:#FFD700;color:#000;transform:translateY(-3px) scale(1.05);text-shadow:none}
.wheel-btn:disabled{opacity:.5;cursor:not-allowed;animation:none}
.wheel-result{margin-top:16px;font-size:14px;font-weight:900;color:#00FFFF;letter-spacing:1.5px;text-transform:uppercase;min-height:24px;text-shadow:0 0 10px #00FFFF88}
.vip-zone{background:linear-gradient(135deg,rgba(255,0,85,.15),rgba(255,215,0,.1),rgba(0,255,255,.05));border:2px dashed #FF0055;border-radius:20px;padding:24px;margin-bottom:24px;box-shadow:0 0 30px #FF005522}
.vip-zone h3{font-size:18px;font-weight:900;letter-spacing:3px;text-transform:uppercase;background:linear-gradient(135deg,#FF0055,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:12px;text-align:center;filter:drop-shadow(0 0 10px #FF005555)}
.vip-perks{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.vip-perk{background:rgba(0,0,0,.3);padding:14px;border-radius:12px;border:1px solid rgba(255,0,85,.3);text-align:center;transition:.3s}
.vip-perk:hover{transform:translateY(-3px);border-color:#FF0055;box-shadow:0 0 15px #FF005533}
.vip-perk .vi{font-size:24px;margin-bottom:6px;filter:drop-shadow(0 0 10px #FF005588)}
.vip-perk .vn{font-size:11px;font-weight:900;letter-spacing:1.5px;text-transform:uppercase;color:#FF0055;text-shadow:0 0 5px #FF005588}
.user-chart{background:linear-gradient(135deg,rgba(255,215,0,.05),rgba(0,255,255,.05));border:1px solid rgba(255,215,0,.3);border-radius:18px;padding:18px;margin-bottom:20px;box-shadow:0 0 15px #FFD70011}
.user-chart h4{font-size:12px;font-weight:900;letter-spacing:2px;text-transform:uppercase;color:rgba(255,255,255,.75);margin-bottom:12px}
.user-chart canvas{width:100%;height:100px;display:block;border-radius:10px}
@media(max-width:600px){.wb h2{font-size:20px;letter-spacing:2px}.ug{grid-template-columns:1fr 1fr}.st2{font-size:18px;letter-spacing:2px}.notif-panel{right:10px;top:70px;width:calc(100vw - 20px)}.badges-wrap{grid-template-columns:1fr 1fr}.ist-badge{top:10px;right:10px;font-size:10px;padding:6px 10px}}</style></head><body>
<div class="tb"></div>
<div class="ist-badge">🇮🇳 <span id="ist-clock">Loading...</span></div>
<div class="hd"><div class="hdc">
<div class="br"><div class="bri"><img src="{{ logo }}"></div><div class="brt"><h2>⚡ FLASH PREMIUM v15</h2><p>👤 {% if is_vip %}👶 ᴠɪᴘ ᴍᴇᴍʙᴇʀ{% else %}ᴜꜱᴇʀ ᴘᴀɴᴇʟ{% endif %}</p></div></div>
<div class="ha">
<button class="bts notif-btn" onclick="toggleNotif()">🔔<span class="notif-badge" id="notifBadge" style="display:none">0</span></button>
<div class="ub">{% if is_vip %}👶{% else %}👤{% endif %} {{ uid }}</div>
<a href="/user/logout" class="bts r">🚪 ʟᴏɢᴏᴜᴛ</a>
</div></div></div>

<div class="notif-panel" id="notifPanel">
<div class="notif-hdr">🔔 ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴꜱ</div>
<div id="notifList"><div style="padding:30px;text-align:center;color:rgba(255,255,255,.4);font-size:12px">📭 NO NOTIFICATIONS</div></div></div>

<div class="cont">
<div class="wb {% if is_vip %}vip{% endif %}">
{% if is_vip %}<div class="vip-crown">👶</div>{% endif %}
<div class="ic">{% if is_vip %}👶{% else %}⚡{% endif %}</div>
<h2>{% if is_vip %}👶 ᴡᴇʟᴄᴏᴍᴇ ᴠɪᴘ, ʙᴀʙʏ! 👶{% else %}🎉 ᴡᴇʟᴄᴏᴍᴇ, ᴀɢᴇɴᴛ! 🎉{% endif %}</h2>
<p>{% if is_vip %}💎 ᴘʀᴇᴍɪᴜᴍ ᴠɪᴘ ᴍᴇᴍʙᴇʀ ꜱɪɴᴄᴇ ᴅᴀʏ 1{% else %}Your Premium Access is ready{% endif %}</p></div>

<div class="user-chart">
<h4>📊 ʏᴏᴜʀ 7-ᴅᴀʏ ꜱᴘᴇɴᴅɪɴɢ</h4>
<canvas id="userSpendCanvas"></canvas>
</div>

<div id="premiumLockBanner" style="display:none;background:linear-gradient(135deg,rgba(255,0,85,.1),rgba(255,215,0,.05));border:2px solid #FF0055;border-radius:18px;padding:20px;margin-bottom:20px;text-align:center;box-shadow:0 0 25px #FF005522">
  <div style="font-size:44px;margin-bottom:6px">🔒</div>
  <h3 style="font-size:15px;font-weight:900;letter-spacing:2px;color:#FF0055;margin-bottom:6px;text-shadow:0 0 8px #FF005588">ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇꜱ ʟᴏᴄᴋᴇᴅ</h3>
  <p style="font-size:12px;color:rgba(255,255,255,.65);margin-bottom:14px">Buy your first key to unlock all premium features</p>
  <button onclick="document.getElementById('pg').scrollIntoView({behavior:'smooth'})" style="padding:11px 24px;background:rgba(255,0,85,.05);border:1px solid #FF0055;border-radius:12px;color:#FF0055;font-size:11px;font-weight:900;letter-spacing:2px;cursor:pointer;font-family:inherit;text-shadow:0 0 5px #FF005588;transition:.3s">🚀 ᴜɴʟᴏᴄᴋ ɴᴏᴡ</button>
</div>

{% if is_vip %}
<div class="vip-zone">
<h3>👑 ʙᴀʙʏ ᴠɪᴘ ᴢᴏɴᴇ 👑</h3>
<div class="vip-perks">
<div class="vip-perk"><div class="vi">🎁</div><div class="vn">ᴇxᴛʀᴀ ᴅɪꜱᴄᴏᴜɴᴛ</div></div>
<div class="vip-perk"><div class="vi">⚡</div><div class="vn">ᴘʀɪᴏʀɪᴛʏ ꜱᴜᴘᴘᴏʀᴛ</div></div>
<div class="vip-perk"><div class="vi">💎</div><div class="vn">ᴅᴏᴜʙʟᴇ ᴡʜᴇᴇʟ ᴄʜᴀɴᴄᴇ</div></div>
<div class="vip-perk"><div class="vi">🚀</div><div class="vn">ꜰᴀꜱᴛ ᴛʀᴀᴄᴋ</div></div>
</div></div>
{% endif %}

<div class="ug">
<div class="uc"><div class="ic">🔑</div><div class="n">{{ user_keys }}</div><div class="l">ᴋᴇʏꜱ</div></div>
<div class="uc"><div class="ic">📦</div><div class="n">{{ user_orders }}</div><div class="l">ᴏʀᴅᴇʀꜱ</div></div>
<div class="uc"><div class="ic">💰</div><div class="n">₹{{ user_spent }}</div><div class="l">ꜱᴘᴇɴᴛ</div></div>
<div class="uc"><div class="ic">💳</div><div class="n">₹{{ balance }}</div><div class="l">ᴡᴀʟʟᴇᴛ</div></div>
<div class="uc"><div class="ic">⭐</div><div class="n">{{ user_level }}</div><div class="l">ᴛɪᴇʀ</div></div>
</div>

<div class="tier-box">
<div class="tier-hdr"><h3>📊 ᴛɪᴇʀ ᴘʀᴏɢʀᴇꜱꜱ</h3><div class="tier-badge">{{ user_level }}</div></div>
<div class="tier-bar-wrap"><div class="tier-bar" style="width:{{ tier_pct }}%"></div></div>
<div class="tier-info"><span>💰 {{ user_spent }} ꜱᴘᴇɴᴛ</span><span>🚀 {{ next_tier }}</span></div></div>

<div class="streak-box">
<div class="sb-info"><h4>🔥 ᴅᴀɪʟʏ ꜱᴛʀᴇᴀᴋ</h4><p>Login daily to keep your streak alive!</p></div>
<div class="sb-count" id="streakCount">🔥 0</div></div>

<div class="wheel-section">
<h3>🎰 ʟᴜᴄᴋʏ ᴡʜᴇᴇʟ 🎰</h3>
<p>Spin once every 24h {% if is_vip %}· 👶 VIP: DOUBLE CHANCE!{% endif %}</p>
<button class="wheel-btn" id="wheelBtn" onclick="spinWheel()">🎡 ꜱᴘɪɴ ɴᴏᴡ</button>
<div class="wheel-result" id="wheelResult"></div></div>

<div class="st2">🏆 ʏᴏᴜʀ ʙᴀᴅɢᴇꜱ 🏆</div>
<div class="ss">✨ Achievements ✨</div>
<div class="badges-wrap" id="badgesWrap"><div style="text-align:center;padding:20px;color:rgba(255,255,255,.5);grid-column:1/-1">⏳ LOADING...</div></div>

<div class="kr"><h3>🎁 ʏᴏᴜʀ ʀᴇᴀᴅʏ ᴋᴇʏ 🎁</h3><p>💡 This key is in your account</p>
<div class="kc" id="rk">{{ rkey }}</div>
<div class="ka"><button class="cp" onclick="ck()">📋 ᴄᴏᴘʏ ᴋᴇʏ</button>
<a href="https://t.me/{{ bot }}" target="_blank" class="ob">🚀 ᴏᴘᴇɴ ʙᴏᴛ</a></div></div>

<div class="ref-box">
<h4>🎁 ʀᴇꜰᴇʀ &amp; ᴇᴀʀɴ 🎁</h4>
<p>💸 Share your referral link!</p>
<div class="ref-url" id="refUrl">{{ ref_url }}</div>
<button onclick="copyRef()">📋 ᴄᴏᴘʏ ʀᴇꜰ ᴜʀʟ</button></div>

<div class="st2">🚀 ʜᴏᴡ ᴛᴏ ꜱᴛᴀʀᴛ 🚀</div>
<div class="ss">✨ 3 Simple Steps ✨</div>
<div class="steps">
<div class="stp"><div class="n">1</div><div class="ic">📢</div><h3>ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ</h3><p>Join for updates</p><a href="https://t.me/{{ channel }}" target="_blank" class="ab b">📢 ᴊᴏɪɴ</a></div>
<div class="stp"><div class="n">2</div><div class="ic">🤖</div><h3>ꜱᴛᴀʀᴛ ʙᴏᴛ</h3><p>Activate access</p><a href="https://t.me/{{ bot }}" target="_blank" class="ab g">🚀 ꜱᴛᴀʀᴛ</a></div>
<div class="stp"><div class="n">3</div><div class="ic">🔑</div><h3>ʀᴇᴅᴇᴇᴍ ᴋᴇʏ</h3><p>Copy key & redeem</p><button class="ab p" onclick="rk2()">🎯 ʀᴇᴅᴇᴇᴍ</button></div></div>

<div class="st2">📜 ᴀᴄᴛɪᴠɪᴛʏ 📜</div>
<div class="tabs"><button class="tab active" onclick="switchTab('orders',this)">📦 ᴏʀᴅᴇʀꜱ</button><button class="tab" onclick="switchTab('wallet',this)">💰 ᴡᴀʟʟᴇᴛ</button></div>
<div class="tab-content active" id="tab-orders"><div class="orders-list" id="ordersList"><div style="text-align:center;padding:20px">⏳</div></div></div>
<div class="tab-content" id="tab-wallet"><div class="wallet-list" id="walletList"><div style="text-align:center;padding:20px">⏳</div></div></div>

<div style="margin-top:32px"><div class="st2">🛒 ʙᴜʏ ᴍᴏʀᴇ 🛒</div><div class="ss">💎 Upgrade Your Access</div>
<div class="grid" id="pg"></div></div>
</div>
<footer>© 2026 <span class="fl">⚡ FLASH PREMIUM v15 ⚡</span><br><span style="font-size:10px;opacity:.6;margin-top:8px;display:inline-block">⚡ POWERED BY {{ power }} ⚡</span><br><span style="font-size:10px;opacity:.6;margin-top:4px;display:inline-block">🇮🇳 IST</span></footer>
<div class="tc2" id="tcc"></div>

<script>
const BOT="{{ bot }}";const RK="{{ rkey }}";const REF="{{ ref_url }}";const UID="{{ uid }}";
function toast(m,t='info'){const c=document.getElementById('tcc');const e=document.createElement('div');e.className='tst '+t;e.textContent=m;c.appendChild(e);setTimeout(()=>{e.style.opacity='0';e.style.transform='translateX(100px)';setTimeout(()=>e.remove(),300)},3500);}
function ck(){navigator.clipboard.writeText(RK).then(()=>toast('✅ COPIED','s'));}
function rk2(){navigator.clipboard.writeText(RK).then(()=>{toast('✅ COPIED!','s');setTimeout(()=>window.open('https://t.me/'+BOT,'_blank'),800);});}
function copyRef(){navigator.clipboard.writeText(REF).then(()=>toast('✅ COPIED','s'));}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function switchTab(name,el){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));el.classList.add('active');document.getElementById('tab-'+name).classList.add('active');}
function tickIST(){const now=new Date();const opts={timeZone:'Asia/Kolkata',day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:true};document.getElementById('ist-clock').textContent=new Intl.DateTimeFormat('en-IN',opts).format(now);}
tickIST(); setInterval(tickIST, 1000);

async function lp(){try{const r=await fetch('/api/products');const d=await r.json();const g=document.getElementById('pg');if(!d||!d.length){g.innerHTML='<div style="grid-column:1/-1;text-align:center;padding:40px">📭 NO PRODUCTS</div>';return;}g.innerHTML=d.map(p=>`<div class="card" onclick="window.open('https://t.me/${BOT}','_blank')"><div class="ic">🔑</div><h3>${esc(p.name)}</h3><div class="dur">${esc(p.duration)}</div><div class="pr">₹${p.price}</div><button class="bb">⚡ ʙᴜʏ ɴᴏᴡ</button></div>`).join('');}catch(e){}}
async function lorder(){try{const r=await fetch('/api/my-orders');const d=await r.json();const c=document.getElementById('ordersList');if(!d||!d.length){c.innerHTML='<div style="text-align:center;padding:20px;color:rgba(255,255,255,.5)">📭 NO ORDERS</div>';return;}c.innerHTML=d.map(o=>`<div class="order-row"><div><div class="oi">🆔 ${esc(o.order_id)}</div><div class="op">📦 ${esc(o.product_name)} - ₹${o.amount}</div><div class="oa">📅 ${esc(o.created_at)}</div></div><div><span class="bdg ${o.status==='success'?'bgs':o.status==='pending'?'bgw':'bgd'}">${o.status}</span>${o.key?`<button class="bts" onclick="navigator.clipboard.writeText('${o.key}').then(()=>toast('✅','s'))" style="border-color:#FFD700;color:#FFD700">🔑</button>`:''}<a href="/invoice/${o.order_id}" target="_blank" class="bts" style="border-color:#00FFFF;color:#00FFFF;text-decoration:none">🧾</a></div></div>`).join('');}catch(e){}}
async function lwallet(){try{const r=await fetch('/api/my-wallet');const d=await r.json();const c=document.getElementById('walletList');if(!d||!d.length){c.innerHTML='<div style="text-align:center;padding:20px;color:rgba(255,255,255,.5)">📭 NO TXNS</div>';return;}c.innerHTML=d.map(t=>`<div class="wallet-row"><div><div class="wl-note">${esc(t.note||'Transaction')}</div><div class="wl-time">📅 ${esc(t.time)}</div></div><div class="wl-amt ${t.type==='credit'?'credit':'debit'}">${t.type==='credit'?'+':'-'}₹${t.amount}</div></div>`).join('');}catch(e){}}
async function lbadges(){try{const r=await fetch('/api/my-badges');const d=await r.json();const c=document.getElementById('badgesWrap');if(!d||!d.length){c.innerHTML='<div style="text-align:center;padding:20px;grid-column:1/-1">🎯 NO BADGES YET</div>';return;}c.innerHTML=d.map(b=>`<div class="badge" style="border-color:${b.color}33"><div class="bdg-ic" style="color:${b.color}">${b.icon}</div><div class="bdg-n" style="color:${b.color}">${esc(b.name)}</div></div>`).join('');}catch(e){}}
async function lnotif(){try{const r=await fetch('/api/my-notifications');const d=await r.json();const list=document.getElementById('notifList');const badge=document.getElementById('notifBadge');if(!d||!d.length){list.innerHTML='<div style="padding:30px;text-align:center;color:rgba(255,255,255,.4);font-size:12px">📭 NO NOTIFICATIONS</div>';badge.style.display='none';return;}const unread=d.filter(n=>!n.read).length;if(unread>0){badge.textContent=unread;badge.style.display='flex';}else{badge.style.display='none';}list.innerHTML=d.map(n=>`<div class="notif-item ${!n.read?'unread':''}" onclick="markRead('${n._id}')"><div class="nf-title">📢 ${esc(n.title)}</div><div class="nf-body">${esc(n.body)}</div><div class="nf-time">📅 ${esc(n.time)}</div></div>`).join('');}catch(e){}}
async function markRead(id){try{await fetch('/api/mark-notification-read',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id})});lnotif();}catch(e){}}
function toggleNotif(){document.getElementById('notifPanel').classList.toggle('open');}
document.addEventListener('click',(e)=>{if(!e.target.closest('.notif-btn')&&!e.target.closest('.notif-panel'))document.getElementById('notifPanel').classList.remove('open');});
async function loadStreak(){try{const r=await fetch('/api/streak');const d=await r.json();document.getElementById('streakCount').textContent='🔥 '+(d.streak||0);}catch(e){}}
async function spinWheel(){const btn=document.getElementById('wheelBtn');const res=document.getElementById('wheelResult');btn.disabled=true;btn.innerHTML='🎡 ꜱᴘɪɴɴɪɴɢ...';try{const r=await fetch('/api/spin-wheel',{method:'POST'});const d=await r.json();if(!d.success){res.style.color='#ff4444';res.textContent='❌ '+(d.error||'FAIL').toUpperCase();btn.disabled=false;btn.innerHTML='🎡 ꜱᴘɪɴ ɴᴏᴡ';return;}let c=0;const intv=setInterval(()=>{c++;res.textContent='🎰 '+['₹5','₹10','₹25','₹50','₹100','🎁'].sort(()=>Math.random()-0.5)[0];if(c>10){clearInterval(intv);res.style.color='#00FF88';res.textContent='🎉 WON ₹'+d.reward;btn.innerHTML='🎡 ᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ';toast('🎉 WON ₹'+d.reward,'s');lwallet();}},100);}catch(e){res.style.color='#ff4444';res.textContent='❌ FAIL';btn.disabled=false;btn.innerHTML='🎡 ꜱᴘɪɴ ɴᴏᴡ';}}
lp();lorder();lwallet();lbadges();lnotif();loadStreak();
setInterval(lnotif, 20000);

async function loadUserChart() {
  try {
    const d = await fetch('/api/user-spending-chart').then(r => r.json());
    if (!d || !d.length) return;
    const canvas = document.getElementById('userSpendCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * 2;
    canvas.height = rect.height * 2;
    ctx.scale(2, 2);
    const W = rect.width, H = rect.height;
    ctx.clearRect(0, 0, W, H);
    const max = Math.max(...d.map(x => x.spent), 1);
    const barW = W / d.length * 0.7;
    const gap = W / d.length * 0.3;
    d.forEach((pt, i) => {
      const x = i * (barW + gap) + gap / 2;
      const barH = (pt.spent / max) * (H - 20);
      const y = H - barH - 10;
      const grad = ctx.createLinearGradient(0, y, 0, H);
      grad.addColorStop(0, '#FFD700');
      grad.addColorStop(1, '#FF0055');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.rect(x, y, barW, barH);
      ctx.fill();
      ctx.fillStyle = 'rgba(255,255,255,.5)';
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(pt.label, x + barW / 2, H - 1);
    });
  } catch(e){}
}
setTimeout(loadUserChart, 800);

async function checkUserLocks() {
  try {
    const r = await fetch('/api/my-locks');
    const d = await r.json();
    if (d && d.locks) {
      const wheelBtn = document.getElementById('wheelBtn');
      if (wheelBtn && d.locks.wheel) {
        wheelBtn.disabled = true;
        wheelBtn.textContent = '🔒 ʟᴏᴄᴋᴇᴅ';
        wheelBtn.title = 'Unlock with first purchase';
      }
      if (!d.is_premium && !d.is_vip) {
        const banner = document.getElementById('premiumLockBanner');
        if (banner) banner.style.display = 'block';
      }
    }
  } catch (e) {}
}
setTimeout(checkUserLocks, 500);
</script></body></html>"""

@app.route("/user/panel")
@usr_req
def usr_panel():
    uid = session.get("uid","Unknown")
    rkey = None
    ex = safe_find_one(keys_col, {"created_for": uid, "redeemed_by": None,
        "expires": {"$gt": now_str_naive()}})
    if ex: rkey = ex["_id"]
    else:
        plan = safe_find_one(plans_col, {"_id": uid})
        if plan and plan.get("redeemed_code"): rkey = plan["redeemed_code"]
        else:
            rkey = gen_code("READY", 12)
            exp = now_ist() + timedelta(days=1)
            safe_insert(keys_col, {"_id": rkey, "type": "user_ready", "attacks_left": -1,
                "max_duration": DEFAULT_MAX_TIME,
                "max_concurrent": DEFAULT_MAX_CONC,
                "cooldown": DEFAULT_COOLDOWN,
                "expires": exp.strftime("%Y-%m-%d %H:%M:%S"),
                "created_by": "FLASH_STORE", "created_for": uid, "redeemed_by": None,
                "trial": False, "created_at": now_str(),
                "duration_label": "1 Day(s)", "duration_hours": 24})
    u_orders = safe_count(orders_col, {"telegram_id": uid, "status":"success"})
    u_spent = sum(o.get("amount",0) for o in safe_find(orders_col,
        {"telegram_id": uid, "status":"success"}))
    u_keys = safe_count(keys_col, {"created_for": uid})
    balance = get_balance(uid)
    tier, _ = get_tier(u_spent)
    if u_spent >= 5000: pct = 100; nxt = "🏆 MAX TIER"
    elif u_spent >= 2000: pct = int(((u_spent-2000)/(5000-2000))*100); nxt = f"₹{5000-u_spent} ᴛᴏ ᴅɪᴀᴍᴏɴᴅ"
    elif u_spent >= 1000: pct = int(((u_spent-1000)/(2000-1000))*100); nxt = f"₹{2000-u_spent} ᴛᴏ ᴘʟᴀᴛɪɴᴜᴍ"
    elif u_spent >= 500: pct = int(((u_spent-500)/(1000-500))*100); nxt = f"₹{1000-u_spent} ᴛᴏ ᴠɪᴘ"
    elif u_spent >= 100: pct = int(((u_spent-100)/(500-100))*100); nxt = f"₹{500-u_spent} ᴛᴏ ɢᴏʟᴅ"
    else: pct = int((u_spent/100)*100); nxt = f"₹{100-u_spent} ᴛᴏ ꜱɪʟᴠᴇʀ"
    doc = safe_find_one(users_col, {"_id": uid}) or {}
    ref_code = doc.get("referral_code")
    if not ref_code:
        ref_code = gen_code("REF", 8)
        safe_update(users_col, {"_id": uid}, {"$set": {"referral_code": ref_code}})
    ref_url = f"{request.host_url}?ref={ref_code}"
    return render_template_string(UPANEL_HTML, bg=setting("background_image",BG_IMG),
        uid=uid, rkey=rkey, bot=BOT_USER, channel=CHANNEL, power=POWER_BY,
        logo=setting("logo_image",LOGO_IMG),
        user_orders=u_orders, user_spent=u_spent, user_keys=u_keys,
        user_level=tier, balance=balance, ref_url=ref_url,
        tier_pct=pct, next_tier=nxt, is_vip=is_vip_user(uid))

# ================= HELPER PANEL =================
HELPER_PANEL_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>🤝 HELPER PANEL · FLASH PREMIUM v15</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=JetBrains+Mono:wght@600&display=swap" rel="stylesheet">
<style>*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;background:#05050A;color:#fff;min-height:100vh;overflow-x:hidden}
body::before{content:'';position:fixed;inset:0;background:radial-gradient(circle at 30% 30%,#00FFFF15,transparent 40%),radial-gradient(circle at 70% 70%,#FFD70015,transparent 40%);z-index:-1}
.tb{position:fixed;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#00FFFF,#FFD700,#00FFFF);background-size:400%;animation:sl 3s linear infinite;z-index:100}
@keyframes sl{0%{background-position:0 0}100%{background-position:400% 0}}
.hd{padding:20px;background:rgba(10,10,15,.85);backdrop-filter:blur(20px);border-bottom:1px solid rgba(0,255,255,.2);position:sticky;top:4px;z-index:50;box-shadow:0 5px 20px #00FFFF11}
.hdc{max-width:1200px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px}
.hdc h2{font-size:20px;font-weight:900;letter-spacing:2px;text-transform:uppercase;background:linear-gradient(135deg,#00FFFF,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 8px #00FFFF55)}
.cont{max-width:1200px;margin:0 auto;padding:24px 20px}
.wb{background:linear-gradient(135deg,rgba(0,255,255,.1),rgba(255,215,0,.05));border:2px solid rgba(0,255,255,.4);border-radius:22px;padding:28px;margin-bottom:24px;text-align:center;box-shadow:0 0 30px #00FFFF22}
.wb .ic{font-size:60px;filter:drop-shadow(0 0 20px #00FFFFcc)}
.wb h2{font-size:24px;font-weight:900;margin-top:12px;letter-spacing:3px;text-transform:uppercase;background:linear-gradient(135deg,#00FFFF,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 10px #00FFFF55)}
.wb p{color:rgba(255,255,255,.7);font-size:12px;margin-top:10px;letter-spacing:1.5px;text-transform:uppercase}
.ug{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin-bottom:24px}
.uc{background:rgba(10,10,15,.85);border:1px solid rgba(255,255,255,.1);border-left:4px solid #00FFFF;border-radius:16px;padding:18px;box-shadow:0 0 15px #00FFFF11;transition:.3s}
.uc:nth-child(even){border-left-color:#FFD700;box-shadow:0 0 15px #FFD70011}
.uc:hover{transform:translateY(-4px);filter:brightness(1.2)}
.uc .ic{font-size:22px;margin-bottom:8px;filter:drop-shadow(0 0 8px currentColor)}
.uc .n{font-size:22px;font-weight:900;font-family:'JetBrains Mono',monospace;color:#00FFFF;text-shadow:0 0 10px #00FFFF88}
.uc:nth-child(even) .n{color:#FFD700;text-shadow:0 0 10px #FFD70088}
.uc .l{font-size:9.5px;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:1.8px;font-weight:800;margin-top:4px}
.pnl{background:rgba(10,10,15,.85);border:1px solid rgba(255,255,255,.1);border-radius:20px;padding:22px;margin-bottom:18px;box-shadow:0 0 20px rgba(0,0,0,.5)}
.ph{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,.08);flex-wrap:wrap;gap:12px}
.ph h3{font-size:15px;font-weight:900;letter-spacing:2px;text-transform:uppercase;color:#00FFFF;text-shadow:0 0 8px #00FFFF55}
.bt{padding:10px 18px;border:1px solid #00FFFF;border-radius:12px;font-size:11px;font-weight:900;cursor:pointer;letter-spacing:1.5px;text-transform:uppercase;background:rgba(0,255,255,.05);color:#00FFFF;text-shadow:0 0 5px #00FFFF88;transition:.3s}
.bt:hover{background:#00FFFF;color:#000;box-shadow:0 0 15px #00FFFF66;text-shadow:none}
.tw{overflow-x:auto;border-radius:16px;border:1px solid rgba(255,255,255,.08);background:rgba(0,0,0,.25)}
table{width:100%;border-collapse:collapse;font-size:12px}
th{background:rgba(255,255,255,.03);padding:13px 15px;text-align:left;font-size:9.5px;font-weight:900;text-transform:uppercase;letter-spacing:2px;color:rgba(255,255,255,.4);border-bottom:1px solid rgba(255,255,255,.08)}
td{padding:12px 15px;border-bottom:1px solid rgba(255,255,255,.04);color:rgba(255,255,255,.7)}
tr:hover td{background:rgba(0,255,255,.05)}
.cd{font-family:'JetBrains Mono',monospace;font-size:11px;background:rgba(0,255,255,.1);border:1px solid rgba(0,255,255,.3);padding:4px 9px;border-radius:7px;color:#00FFFF;font-weight:700;text-shadow:0 0 5px #00FFFF55}
.bdg{display:inline-block;padding:4px 11px;border-radius:20px;font-size:10px;font-weight:900;letter-spacing:1.2px;text-transform:uppercase}
.bgs{background:rgba(0,255,136,.1);color:#00FF88;border:1px solid rgba(0,255,136,.35)}
.bgw{background:rgba(255,165,0,.1);color:#FFA500;border:1px solid rgba(255,165,0,.35)}
.bgd{background:rgba(255,0,85,.1);color:#FF0055;border:1px solid rgba(255,0,85,.35)}
.chat-item{background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.08);border-left:3px solid #FFD700;border-radius:14px;padding:14px 18px;margin-bottom:12px}
.chat-item .ch-h{display:flex;justify-content:space-between;margin-bottom:8px;flex-wrap:wrap;gap:8px}
.chat-item .ch-n{color:#FFD700;font-size:12px;font-weight:900;letter-spacing:1.5px;text-transform:uppercase;text-shadow:0 0 5px #FFD70055}
.chat-item .ch-t{font-size:10px;color:rgba(255,255,255,.4)}
.chat-item .ch-b{font-size:13px;color:rgba(255,255,255,.85);line-height:1.6;background:rgba(255,215,0,.05);padding:10px 14px;border-radius:10px;border-left:3px solid #FFD700}
.chat-item .ch-b img{max-width:200px;border-radius:10px;display:block;margin-top:8px}
.chat-item .ch-b audio{margin-top:8px}
.chat-item .ch-b video{max-width:220px;border-radius:10px;display:block;margin-top:8px}
.chat-item .ch-r{margin-top:12px;display:flex;gap:8px}
.chat-item .ch-r input{flex:1;padding:8px 12px;background:rgba(0,0,0,.4);border:1px solid rgba(255,215,0,.3);border-radius:9px;color:#fff;font-size:12px;outline:none;transition:.3s}
.chat-item .ch-r input:focus{border-color:#FFD700;box-shadow:0 0 15px #FFD70033}
.chat-item .ch-reply{font-size:11.5px;color:#00FF88;background:rgba(0,255,136,.05);padding:8px 12px;border-radius:9px;margin-top:8px;border-left:3px solid #00FF88}
.tc2{position:fixed;top:20px;right:20px;z-index:2000;display:flex;flex-direction:column;gap:10px;max-width:340px}
.tst{background:rgba(10,10,15,.98);border:1px solid rgba(255,255,255,.15);border-left:4px solid #00FFFF;border-radius:14px;padding:14px 18px;font-size:12.5px;font-weight:700;box-shadow:0 15px 50px rgba(0,0,0,.6), 0 0 20px #00FFFF22;animation:ti .4s;color:#fff}
@keyframes ti{from{opacity:0;transform:translateX(120px)}to{opacity:1;transform:translateX(0)}}
.emp{text-align:center;padding:40px 20px;color:rgba(255,255,255,.4);font-size:12px;font-weight:800;letter-spacing:2px;text-transform:uppercase}
@media(max-width:600px){.ug{grid-template-columns:1fr 1fr}}
</style></head><body>
<div class="tb"></div>
<div class="hd"><div class="hdc">
<h2>🤝 HELPER PANEL · v15</h2>
<div style="display:flex;gap:10px;align-items:center">
<div class="cd" style="padding:8px 16px;border-radius:20px;background:rgba(0,255,255,.1);border:1px solid #00FFFF;color:#00FFFF">🤝 {{ helper_name }}</div>
<a href="/helper/logout" class="bt" style="text-decoration:none;background:rgba(255,0,85,.05);border-color:#FF0055;color:#FF0055">🚪 ᴇxɪᴛ</a>
</div></div></div>

<div class="cont">
<div class="wb"><div class="ic">🤝</div><h2>ᴡᴇʟᴄᴏᴍᴇ ʜᴇʟᴘᴇʀ</h2><p>Limited access · View orders · Chat support</p></div>

<div class="ug">
<div class="uc"><div class="ic">📦</div><div class="n" id="h-orders">-</div><div class="l">ᴛᴏᴛᴀʟ ᴏʀᴅᴇʀꜱ</div></div>
<div class="uc"><div class="ic">✅</div><div class="n" id="h-paid">-</div><div class="l">ᴘᴀɪᴅ</div></div>
<div class="uc"><div class="ic">⏳</div><div class="n" id="h-pending">-</div><div class="l">ᴘᴇɴᴅɪɴɢ</div></div>
<div class="uc"><div class="ic">💬</div><div class="n" id="h-chats">-</div><div class="l">ᴄʜᴀᴛꜱ</div></div>
</div>

<div class="pnl">
<div class="ph"><h3>💬 ʟɪᴠᴇ ᴄʜᴀᴛ ᴍᴀɴᴀɢᴇʀ</h3><button class="bt" onclick="hc()">🔄 ʀᴇꜰʀᴇꜱʜ</button></div>
<div id="chatList" class="emp">⏳ ʟᴏᴀᴅɪɴɢ...</div>
</div>

<div class="pnl">
<div class="ph"><h3>📦 ʀᴇᴄᴇɴᴛ ᴏʀᴅᴇʀꜱ</h3><button class="bt" onclick="ho()">🔄 ʀᴇꜰʀᴇꜱʜ</button></div>
<div class="tw"><table id="ordTable"><thead><tr><th>⏰ ᴛɪᴍᴇ</th><th>🆔 ᴏʀᴅᴇʀ</th><th>👤 ᴄᴜꜱᴛᴏᴍᴇʀ</th><th>📦 ᴘʀᴏᴅᴜᴄᴛ</th><th>💰 ᴀᴍᴏᴜɴᴛ</th><th>📊 ꜱᴛᴀᴛᴜꜱ</th></tr></thead><tbody></tbody></table></div>
</div>
</div>
<div class="tc2" id="tcc"></div>

<script>
function toast(m,t='info'){const c=document.getElementById('tcc');const e=document.createElement('div');e.className='tst '+t;e.textContent=m;c.appendChild(e);setTimeout(()=>{e.style.opacity='0';e.style.transform='translateX(100px)';setTimeout(()=>e.remove(),300)},3500);}
function fd(iso){if(!iso)return'-';try{const d=new Date(iso);const o={timeZone:'Asia/Kolkata',day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit',hour12:true};return new Intl.DateTimeFormat('en-IN',o).format(d)+' IST';}catch{return iso;}}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
async function api(ep,o={}){try{const r=await fetch('/api'+ep,{headers:{'Content-Type':'application/json'},...o});return await r.json();}catch(e){return null;}}
async function hs(){const d=await api('/stats');if(!d)return;document.getElementById('h-orders').textContent=d.total_orders||0;document.getElementById('h-paid').textContent=d.paid_orders||0;document.getElementById('h-pending').textContent=d.pending_orders||0;document.getElementById('h-chats').textContent=d.store_users||0;}
async function hc(){const d=await api('/chat/list');const c=document.getElementById('chatList');if(!d||!d.length){c.innerHTML='<div class="emp">📭 ɴᴏ ᴄʜᴀᴛꜱ</div>';return;}c.innerHTML=d.map(m=>{let mediaHtml='';if(m.media_type==='photo'&&m.media_url)mediaHtml=`<img src="${m.media_url}" onclick="window.open('${m.media_url}','_blank')">`;else if(m.media_type==='voice'||m.media_type==='audio')mediaHtml=`<audio controls src="${m.media_url}"></audio>`;else if(m.media_type==='video')mediaHtml=`<video controls src="${m.media_url}"></video>`;else if(m.media_type==='document')mediaHtml=`<a href="${m.media_url}" target="_blank" style="color:#00FFFF">📄 ${esc(m.media_name||'file')}</a>`;return `<div class="chat-item"><div class="ch-h"><div class="ch-n">👤 ${esc(m.name||'Anon')} <span style="opacity:.5;font-size:10px">(${esc(m.chat_id||'')})</span></div><div class="ch-t">📅 ${fd(m.time)}</div></div><div class="ch-b">💬 ${esc(m.text||'')}${mediaHtml?`<div>${mediaHtml}</div>`:''}</div>${m.replies&&m.replies.length?m.replies.map(r=>`<div class="ch-reply"><b>🎧:</b> ${esc(r.text||'')}</div>`).join(''):''}<div class="ch-r"><input id="reply-${m.chat_id}" placeholder="✏️ ʀᴇᴘʟʏ..."><button class="bt" onclick="hrpl('${m.chat_id}')">📨</button><button class="bt" style="border-color:#FF0055;color:#FF0055;background:rgba(255,0,85,.05)" onclick="hrplMedia('${m.chat_id}')">📎</button></div></div>`;}).join('');}
async function hrpl(cid){const i=document.getElementById('reply-'+cid);const t=i.value.trim();if(!t)return;const r=await api('/chat/reply',{method:'POST',body:JSON.stringify({chat_id:cid,text:t})});if(r?.success){toast('📨 ꜱᴇɴᴛ','s');i.value='';hc();}}
function hrplMedia(cid){const inp=document.createElement('input');inp.type='file';inp.accept='image/*,audio/*,video/*,.pdf,.doc,.docx,.zip';inp.onchange=async()=>{const f=inp.files&&inp.files[0];if(!f)return;const cap=prompt('Caption:','')||'';const fd=new FormData();fd.append('chat_id',cid);fd.append('caption',cap);fd.append('file',f,f.name);try{const r=await fetch('/api/chat/reply-media',{method:'POST',body:fd});const d=await r.json();if(d.success){toast('📎 ꜱᴇɴᴛ','s');hc();}else toast('❌','e');}catch(e){toast('❌','e');}};inp.click();}
async function ho(){const d=await api('/orders');const tb=document.querySelector('#ordTable tbody');if(!d||!d.length){tb.innerHTML='<tr><td colspan="6" class="emp">📭 ɴᴏ ᴏʀᴅᴇʀꜱ</td></tr>';return;}tb.innerHTML=d.slice(0,50).map(x=>`<tr><td>${fd(x.created_at)}</td><td><span class="cd">${esc(x.order_id||'')}</span></td><td>${esc(x.customer_name||'-')}</td><td>${esc(x.product_name||'-')}</td><td><b style="color:#00FF88">₹${x.amount}</b></td><td><span class="bdg ${x.status==='success'?'bgs':x.status==='pending'?'bgw':'bgd'}">${x.status}</span></td></tr>`).join('');}
hs();hc();ho();
setInterval(hs,30000);
</script></body></html>"""

@app.route("/helper/panel")
@helper_req
def helper_panel():
    return render_template_string(HELPER_PANEL_HTML,
        bg=setting("background_image",BG_IMG), logo=setting("logo_image",LOGO_IMG),
        helper_name=session.get("helper_name","helper"), power=POWER_BY)

# ================= INVOICE =================
@app.route("/invoice/<oid>")
def invoice(oid):
    o = safe_find_one(orders_col, {"_id": oid})
    if not o: return "Order not found", 404
    logo = setting("logo_image", LOGO_IMG)
    key_block = f'<div class="key-box"><div class="k-label">🔑 Your Key</div><div class="k-val">{o.get("key","-")}</div></div>' if o.get('key') else ''
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>🧾 INVOICE {oid}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',sans-serif;max-width:680px;margin:20px auto;padding:0;background:#05050A;color:#fff}}
.invoice-wrap{{background:#0A0A15;border:1px solid #FFD70044;border-radius:20px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.8), 0 0 40px #FFD70022}}
.inv-header{{background:linear-gradient(135deg,rgba(255,215,0,.1),rgba(255,0,85,.1));padding:36px 30px;text-align:center;color:#fff;position:relative;overflow:hidden;border-bottom:1px solid #FFD70033}}
.inv-header::before{{content:'';position:absolute;inset:0;background:radial-gradient(circle at 30% 20%,rgba(255,215,0,.15),transparent 50%)}}
.inv-header img{{width:76px;height:76px;border-radius:50%;border:3px solid #FFD700;box-shadow:0 0 30px #FFD700cc;margin-bottom:14px;position:relative;z-index:1}}
.inv-header h1{{font-size:22px;font-weight:900;letter-spacing:4px;text-transform:uppercase;position:relative;z-index:1;color:#FFD700;text-shadow:0 0 10px #FFD70088}}
.inv-header p{{font-size:10px;letter-spacing:3px;opacity:.85;margin-top:6px;text-transform:uppercase;font-weight:700;position:relative;z-index:1;color:#00FFFF}}
.inv-body{{padding:30px}}
.inv-meta{{display:flex;justify-content:space-between;align-items:center;padding:16px 20px;background:rgba(255,215,0,.05);border:1px solid #FFD70033;border-radius:12px;margin-bottom:24px;flex-wrap:wrap;gap:12px}}
.inv-meta .meta-item{{font-size:11px;color:#00FFFF;font-weight:800;letter-spacing:1.2px;text-transform:uppercase}}
.inv-meta .meta-item b{{display:block;color:#fff;font-size:13px;font-family:'Courier New',monospace;margin-top:3px;letter-spacing:0}}
table{{width:100%;border-collapse:collapse}}
td{{padding:14px 10px;border-bottom:1px solid rgba(255,255,255,.05);font-size:13px}}
.lbl{{font-weight:800;color:rgba(255,255,255,.6);font-size:11px;text-transform:uppercase;letter-spacing:1.2px;width:40%}}
.val{{font-weight:700;color:#fff}}
.tot{{background:linear-gradient(135deg,rgba(255,215,0,.1),rgba(255,0,85,.05));font-weight:900;font-size:22px;color:#FFD700;text-shadow:0 0 10px #FFD70088}}
.tot .lbl{{font-size:13px;color:#FFD700}}
.badge{{display:inline-block;padding:5px 14px;background:rgba(0,255,136,.1);color:#00FF88;border-radius:20px;font-size:11px;font-weight:900;letter-spacing:1.5px;text-transform:uppercase;border:1px solid #00FF88}}
.key-box{{background:rgba(0,255,136,.05);border:2px dashed #00FF88;border-radius:12px;padding:18px;text-align:center;margin:20px 0}}
.key-box .k-label{{font-size:10px;color:#00FF88;letter-spacing:2.5px;text-transform:uppercase;font-weight:900;margin-bottom:8px}}
.key-box .k-val{{font-family:'Courier New',monospace;font-size:18px;font-weight:900;color:#00FF88;letter-spacing:1.5px;word-break:break-all}}
.inv-footer{{text-align:center;padding:24px 30px;background:rgba(255,255,255,.02);border-top:1px solid rgba(255,255,255,.05)}}
.inv-footer p{{font-size:10px;color:rgba(255,255,255,.5);letter-spacing:2px;text-transform:uppercase;font-weight:700}}
.inv-footer p + p{{margin-top:6px;color:#FFD700}}
</style></head><body>
<div class="invoice-wrap">
<div class="inv-header">
<img src="{logo}" alt="Logo">
<h1>⚡ FLASH PREMIUM ⚡</h1>
<p>Premium Digital Store · Invoice</p>
</div>
<div class="inv-body">
<div class="inv-meta">
<div class="meta-item">🧾 Invoice No<b>{o.get('order_id')}</b></div>
<div class="meta-item">📅 Date<b>{now_ist().strftime("%d %b %Y")}</b></div>
<div class="meta-item">🇮🇳 Time<b>{now_ist().strftime("%I:%M %p IST")}</b></div>
</div>
<table>
<tr><td class="lbl">👤 Customer</td><td class="val">{o.get('customer_name','-')}</td></tr>
<tr><td class="lbl">📨 Telegram ID</td><td class="val">{o.get('telegram_id','-')}</td></tr>
<tr><td class="lbl">📦 Product</td><td class="val">{o.get('product_name','-')}</td></tr>
<tr><td class="lbl">⏱ Duration</td><td class="val">{o.get('product_duration','-')}</td></tr>
<tr><td class="lbl">📊 Status</td><td><span class="badge">{o.get('status','-').upper()}</span></td></tr>
</table>
{key_block}
<table>
<tr class="tot"><td class="lbl">💰 Total Paid</td><td>₹{o.get('amount',0)}</td></tr>
</table>
</div>
<div class="inv-footer">
<p>🙏 Thank you for your purchase! 🙏</p>
<p>⚡ FLASH PREMIUM v15 ⚡</p>
</div>
</div>
<script>window.onload=function(){{setTimeout(()=>window.print(),600)}}</script>
</body></html>"""

# ================= ADMIN PANEL =================
ADMIN_HTML = open(os.path.join(os.path.dirname(__file__), "admin.html")).read() if os.path.exists(os.path.join(os.path.dirname(__file__), "admin.html")) else "<h1>admin.html missing</h1>"

@app.route("/admin")
@adm_req
def admin():
    return render_template_string(ADMIN_HTML,
        bg=setting("background_image",BG_IMG),
        logo=setting("logo_image",LOGO_IMG))

# ================= APIs (all the same, with safe_ helpers) =================
@app.route("/api/products")
def api_prods():
    ps = safe_find(prods_col, {"active":True}, sort=[("order",1)])
    return jsonify([{"_id":p["_id"],"name":p["name"],"duration":p["duration"],
        "hours":p.get("hours",0),"price":p["price"],"popular":p.get("popular",False),
        "category":p.get("category",""),"featured":p.get("featured",False),
        "max_time":p.get("max_time",DEFAULT_MAX_TIME),
        "max_concurrent":p.get("max_concurrent",DEFAULT_MAX_CONC),
        "cooldown":p.get("cooldown",DEFAULT_COOLDOWN)} for p in ps])

@app.route("/api/product/<pid>")
def api_prod(pid):
    p = safe_find_one(prods_col, {"_id":pid})
    if not p: return jsonify({"error":"Not found"}),404
    return jsonify({"_id":p["_id"],"name":p["name"],"duration":p["duration"],
        "hours":p.get("hours",0),"price":p["price"],"popular":p.get("popular",False),
        "category":p.get("category",""),"featured":p.get("featured",False),
        "max_time":p.get("max_time",DEFAULT_MAX_TIME),
        "max_concurrent":p.get("max_concurrent",DEFAULT_MAX_CONC),
        "cooldown":p.get("cooldown",DEFAULT_COOLDOWN)})

@app.route("/api/faqs")
def api_faqs():
    fs = safe_find(faqs_col, sort=[("order",1)])
    return jsonify([{"q":f.get("q",""),"a":f.get("a","")} for f in fs])

@app.route("/api/testimonials")
def api_testimonials():
    ts = safe_find(testimonials_col, sort=[("order",1)])
    return jsonify([{"text":t.get("text",""),"who":t.get("who",""),"stars":t.get("stars",5)} for t in ts])

@app.route("/api/announcement")
def api_announcement():
    return jsonify({"enabled": setting("announcement_enabled", False),
        "title": setting("announcement_title", ""), "text": setting("announcement_text", "")})

@app.route("/api/store-stats")
def api_store_stats():
    ratings = safe_find(ratings_col)
    avg = sum(r.get("stars",0) for r in ratings)/len(ratings) if ratings else 5.0
    today_start = now_ist().replace(hour=0,minute=0,second=0,microsecond=0)
    today_visits = safe_count(visits_col, {"time":{"$gte":today_start.isoformat()}})
    return jsonify({"keys_sold": safe_count(orders_col, {"status":"success"}),
        "users": safe_count(users_col), "avg_rating": round(avg, 1),
        "today_visits": today_visits})

@app.route("/api/recent-purchases")
def api_recent_purchases():
    o = safe_find(orders_col, {"status":"success"}, limit=20, sort=[("paid_at",-1)])
    out = []
    for x in o:
        tid = str(x.get("telegram_id",""))
        name = tid[-4:].rjust(4,'*') if tid else "user"
        out.append({"name": f"USER-{name}", "product": x.get("product_name","Key")})
    return jsonify(out)

@app.route("/api/track/<oid>")
def api_track(oid):
    o = safe_find_one(orders_col, {"_id":oid})
    if not o: return jsonify({"found":False})
    return jsonify({"found":True,"order_id":o.get("order_id"),
        "product_name":o.get("product_name"),"amount":o.get("amount"),
        "status":o.get("status"),"key":o.get("key")})

@app.route("/api/rate-order", methods=["POST"])
def api_rate_order():
    try:
        d = request.get_json()
        oid = d.get("order_id"); stars = int(d.get("stars",0))
        comment = (d.get("comment") or "").strip()[:500]
        if not oid or stars < 1 or stars > 5:
            return jsonify({"success":False,"error":"Invalid"})
        if safe_count(ratings_col, {"order_id": oid}) > 0:
            return jsonify({"success":False,"error":"Already rated"})
        safe_insert(ratings_col, {"order_id": oid, "stars": stars,
            "comment": comment, "time": now_str()})
        notify_admin("New Rating", f"⭐ {stars}/5\n🆔 {oid}\n💬 {comment[:150] or '-'}", "success")
        return jsonify({"success":True})
    except Exception as e: return jsonify({"success":False,"error":str(e)})

@app.route("/api/validate-coupon", methods=["POST"])
def api_validate_coupon():
    try:
        d = request.get_json()
        code = (d.get("code") or "").strip().upper()
        pid = d.get("product_id")
        c = safe_find_one(coupons_col, {"code": code})
        if not c: return jsonify({"valid":False,"error":"Not found"})
        if not c.get("active", True): return jsonify({"valid":False,"error":"Inactive"})
        exp = c.get("expires")
        if exp and exp < now_ist().strftime("%Y-%m-%d"):
            return jsonify({"valid":False,"error":"Expired"})
        max_u = c.get("max_uses",0)
        if max_u > 0 and c.get("uses",0) >= max_u:
            return jsonify({"valid":False,"error":"Limit reached"})
        prod = safe_find_one(prods_col, {"_id":pid})
        if not prod: return jsonify({"valid":False,"error":"Product missing"})
        if c.get("min_order",0) > prod["price"]:
            return jsonify({"valid":False,"error":f"Min ₹{c['min_order']}"})
        if c.get("type") == "percent":
            disc = round(prod["price"] * c["value"] / 100, 2)
        else:
            disc = min(float(c["value"]), prod["price"])
        return jsonify({"valid":True,"discount":disc})
    except Exception as e: return jsonify({"valid":False,"error":str(e)})

@app.route("/api/create-order", methods=["POST"])
def api_create_order():
    try:
        d = request.get_json()
        prod = safe_find_one(prods_col, {"_id":d.get("product_id")})
        if not prod: return jsonify({"success":False,"error":"Product not found"})
        amt = prod["price"]
        coupon_code = (d.get("coupon") or "").strip().upper()
        discount = 0
        if coupon_code:
            c = safe_find_one(coupons_col, {"code": coupon_code, "active": True})
            if c:
                exp = c.get("expires")
                valid = True
                if exp and exp < now_ist().strftime("%Y-%m-%d"): valid = False
                max_u = c.get("max_uses",0)
                if max_u > 0 and c.get("uses",0) >= max_u: valid = False
                if c.get("min_order",0) > amt: valid = False
                if valid:
                    if c.get("type") == "percent":
                        discount = round(amt * c["value"] / 100, 2)
                    else:
                        discount = min(float(c["value"]), amt)
                    coupons_col.update_one({"code": coupon_code}, {"$inc": {"uses": 1}})
        final = max(0, amt - discount)
        tid = d.get("telegram_id","")
        oid = f"FLASH-{int(time.time())}-{secrets.token_hex(3).upper()}"
        safe_insert(orders_col, {"_id":oid,"order_id":oid,"product_id":d.get("product_id"),
            "product_name":prod["name"],"product_duration":prod["duration"],
            "product_hours":prod.get("hours",0),"amount":final,"original_amount":amt,
            "discount":discount,"coupon":coupon_code,
            "customer_name":d.get("customer_name",""),"customer_email":d.get("customer_email",""),
            "customer_phone":d.get("customer_phone",""),"telegram_id":tid,
            "status":"pending","key":None,"created_at":now_str(),"paid_at":None})
        notify_admin("New Order",
            f"🆔 <code>{oid}</code>\n📦 {prod['name']}\n💵 ₹{final}\n👤 {d.get('customer_name','-')}\n📨 <code>{tid or '-'}</code>", "order")
        if final <= 0:
            o = safe_find_one(orders_col, {"_id": oid})
            k = deliver(o)
            return jsonify({"success":True,"order_id":oid,"amount":0,"free":True,"key":k})
        res = fam_create(final, d.get("customer_name",""), d.get("customer_email",""),
            d.get("customer_phone",""),
            f"{request.host_url}payment-success",
            f"{request.host_url}api/webhook")
        if not res["success"]:
            return jsonify({"success":False,"error":res.get("error","Gateway error")})
        data = res["data"]
        safe_update(orders_col, {"_id":oid}, {"$set":{
            "fam_order_id":data.get("order_id",""),
            "qr_url":data.get("qr_url",""),
            "upi_intent":data.get("upi_intent",""),
            "checkout_url":data.get("checkout_url","")}})
        return jsonify({"success":True,"order_id":oid,"amount":final,
            "qr_url":data.get("qr_url",""),"upi_intent":data.get("upi_intent",""),
            "checkout_url":data.get("checkout_url","")})
    except Exception as e: return jsonify({"success":False,"error":str(e)})

@app.route("/api/order-status/<oid>")
def api_ost(oid):
    try:
        o = safe_find_one(orders_col, {"_id":oid})
        if not o: return jsonify({"status":"not_found"})
        if o.get("status") == "success":
            return jsonify({"status":"success","key":o.get("key","")})
        fid = o.get("fam_order_id","")
        if fid:
            r = fam_verify(fid)
            if r["success"] and r.get("data",{}).get("status") == "success":
                k = deliver(o); return jsonify({"status":"success","key":k})
        return jsonify({"status":o.get("status","pending")})
    except Exception as e: return jsonify({"status":"error"})

def deliver(o):
    try:
        res = orders_col.update_one({"_id": o["_id"], "key": None},
            {"$set": {"status": "processing", "processing_started": now_str()}})
        if res.modified_count == 0:
            fresh = safe_find_one(orders_col, {"_id": o["_id"]})
            return fresh.get("key") if fresh else None
        hrs = o.get("product_hours",24)
        dl = o.get("product_duration",f"{hrs} hour(s)")
        code = gen_code("FLASH",12)
        exp = now_ist() + timedelta(hours=hrs)
        exp_str = exp.strftime("%Y-%m-%d %H:%M:%S")
        safe_insert(keys_col, {"_id":code,"type":"store_purchase","attacks_left":-1,
            "max_duration":setting("max_attack_time",DEFAULT_MAX_TIME),
            "max_concurrent":setting("max_concurrent",DEFAULT_MAX_CONC),
            "cooldown":setting("cooldown",DEFAULT_COOLDOWN),
            "expires":exp_str,"created_by":"FLASH_STORE","redeemed_by":None,
            "redeemed_at":None,"trial":False,"created_at":now_str(),
            "duration_hours":hrs,"duration_label":dl,"prefix":"FLASH","order_id":o["order_id"]})
        safe_update(orders_col, {"_id":o["_id"]},
            {"$set":{"status":"success","key":code,"paid_at":now_str()}})
        tid = str(o.get("telegram_id",""))
        if tid:
            u = safe_find_one(users_col, {"_id": tid})
            if u and u.get("referred_by"):
                reward = setting("referral_reward", 50)
                if reward > 0:
                    referrer = safe_find_one(users_col, {"referral_code": u["referred_by"]})
                    if referrer:
                        safe_insert(wallet_col, {"user_id": referrer["_id"], "amount": reward,
                            "type": "credit", "note": f"Referral from {tid}",
                            "time": now_str(), "by": "system"})
                        push_notif(referrer["_id"], "🎁 Referral Bonus",
                            f"You earned ₹{reward}!", "success")
                        tg_send(referrer["_id"], f"🎁 You earned ₹{reward} referral bonus!")
        if tid:
            msg = (f"⚡ <b>Payment Successful!</b> ✅\n\n"
                f"🛒 <b>Order Id:</b> <code>{o['order_id']}</code>\n"
                f"🔑 <b>Your Key:</b> <code>{code}</code>\n"
                f"⏱ <b>Duration:</b> {dl}\n"
                f"💰 <b>Amount:</b> ₹{o['amount']}\n\n"
                f"━━━━━━ <b>How To Use</b> ━━━━━━\n"
                f"1️⃣ Join: @{CHANNEL}\n2️⃣ Open: @{BOT_USER}\n"
                f"3️⃣ Send: <code>/redeem {code}</code>\n\n"
                f"⚡ <b>Flash Premium v15</b> ⚡")
            tg_send(tid, msg)
            push_notif(tid, "🎉 Order Delivered",
                f"Key for {o['product_name']} is ready!", "success")
        notify_admin("Order Delivered",
            f"🆔 <code>{o['order_id']}</code>\n🔑 <code>{code}</code>\n💵 ₹{o['amount']}", "success")
        log_adm("deliver_key", f"{o['order_id']} -> {code}")
        return code
    except Exception as e:
        print(f"[!] deliver: {e}"); return None

@app.route("/api/webhook", methods=["POST"])
def api_wh():
    try:
        d = request.get_json() or {}
        if d.get("status") == "success" and d.get("order_id"):
            o = safe_find_one(orders_col, {"fam_order_id":d["order_id"]})
            if o: deliver(o)
        return jsonify({"status":"ok"})
    except: return jsonify({"status":"error"})

@app.route("/api/chat/send", methods=["POST"])
def api_chat_send():
    try:
        d = request.get_json()
        cid = (d.get("chat_id") or "").strip()
        name = (d.get("name") or "Anonymous").strip()
        text = (d.get("text") or "").strip()
        if not text or not cid: return jsonify({"success":False,"error":"Missing"})
        safe_insert(chat_col, {"chat_id": cid, "name": name, "text": text,
            "sender": "user", "time": now_str(), "status": "open"})
        owner_id = setting("owner_telegram_id", OWNER_TG_ID)
        if owner_id and str(owner_id).strip():
            msg = (f"💬 <b>{sc('new chat')}</b>\n👤 {name}\n🆔 <code>{cid}</code>\n"
                   f"📝 {text}\n🕐 <code>{now_ist().strftime('%d %b %Y, %I:%M:%S %p IST')}</code>")
            try: tg_send(str(owner_id).strip(), msg)
            except: pass
        return jsonify({"success":True})
    except Exception as e: return jsonify({"success":False,"error":str(e)})

@app.route("/api/chat/messages")
def api_chat_messages():
    cid = request.args.get("chat_id", "")
    if not cid: return jsonify([])
    msgs = safe_find(chat_col, {"chat_id": cid}, limit=80, sort=[("time", -1)])
    msgs.reverse()
    return jsonify([{"text": m.get("text", ""),"caption": m.get("caption", ""),
        "sender": m.get("sender", "user"),"time": fmt(m.get("time", "")),
        "media_type": m.get("media_type"),"media_url": m.get("media_url"),
        "media_name": m.get("media_name", "")} for m in msgs])

@app.route("/api/chat/list")
@helper_req
def api_chat_list():
    try:
        pipeline = [{"$sort": {"time": -1}},
            {"$group": {"_id": "$chat_id", "latest": {"$first": "$$ROOT"},
                        "all": {"$push": "$$ROOT"}}},
            {"$limit": 100}]
        results = list(chat_col.aggregate(pipeline))
        out = []
        for g in results:
            cid = g["_id"]
            if not cid: continue
            all_msgs = sorted(g["all"], key=lambda x: x.get("time",""))
            user_msgs = [m for m in all_msgs if m.get("sender")=="user"]
            owner_msgs = [m for m in all_msgs if m.get("sender")=="owner"]
            if not user_msgs: continue
            latest = user_msgs[-1]
            out.append({"chat_id": cid, "name": latest.get("name","Anonymous"),
                "text": latest.get("text",""), "time": latest.get("time",""),
                "media_type": latest.get("media_type"),
                "media_url": latest.get("media_url"),
                "media_name": latest.get("media_name",""),
                "replies": [{"text": r.get("text",""), "media_url": r.get("media_url")}
                            for r in owner_msgs]})
        out.sort(key=lambda x: x["time"], reverse=True)
        return jsonify(out[:50])
    except: return jsonify([])

@app.route("/api/chat/reply", methods=["POST"])
@helper_req
def api_chat_reply():
    try:
        d = request.get_json()
        cid = d.get("chat_id"); text = (d.get("text") or "").strip()
        if not cid or not text: return jsonify({"success":False,"error":"Missing"})
        safe_insert(chat_col, {"chat_id": cid, "name": "Support", "text": text,
            "sender": "owner", "time": now_str()})
        return jsonify({"success":True})
    except Exception as e: return jsonify({"success":False,"error":str(e)})

@app.route("/api/my-orders")
@usr_req
def api_my_orders():
    uid = session.get("uid","")
    o = safe_find(orders_col, {"telegram_id":uid}, limit=10, sort=[("created_at",-1)])
    return jsonify([{"order_id":x.get("order_id"),"product_name":x.get("product_name"),
        "amount":x.get("amount"),"status":x.get("status"),"key":x.get("key"),
        "created_at":fmt(x.get("created_at"))} for x in o])

@app.route("/api/my-wallet")
@usr_req
def api_my_wallet():
    uid = session.get("uid","")
    txns = safe_find(wallet_col, {"user_id": str(uid)}, limit=50, sort=[("time",-1)])
    return jsonify([{"type": t.get("type","credit"), "amount": t.get("amount",0),
        "note": t.get("note",""), "time": fmt(t.get("time",""))} for t in txns])

@app.route("/api/my-badges")
@usr_req
def api_my_badges(): return jsonify(get_badges(session.get("uid","")))

@app.route("/api/my-notifications")
@usr_req
def api_my_notifications():
    uid = session.get("uid","")
    n = safe_find(notif_col, {"user_id": str(uid)}, limit=50, sort=[("time",-1)])
    return jsonify([{"_id": str(x["_id"]), "title": x.get("title",""),
        "body": x.get("body",""),"type": x.get("type","info"),
        "read": x.get("read", False),"time": fmt(x.get("time",""))} for x in n])

@app.route("/api/mark-notification-read", methods=["POST"])
@usr_req
def api_mark_read():
    try:
        d = request.get_json()
        notif_col.update_one({"_id": ObjectId(d.get("id"))}, {"$set": {"read": True}})
        return jsonify({"success":True})
    except: return jsonify({"success":False})

@app.route("/api/streak")
@usr_req
def api_streak():
    uid = session.get("uid","")
    doc = safe_find_one(users_col, {"_id": uid}) or {}
    today = now_ist().strftime("%Y-%m-%d")
    last = doc.get("last_streak_date","")
    streak = doc.get("streak", 0)
    if last != today:
        yesterday = (now_ist() - timedelta(days=1)).strftime("%Y-%m-%d")
        if last == yesterday: streak += 1
        else: streak = 1
        safe_update(users_col, {"_id": uid},
            {"$set": {"streak": streak, "last_streak_date": today}})
        bonus = min(streak * 2, 20)
        if bonus > 0 and streak > 1:
            safe_insert(wallet_col, {"user_id": uid, "amount": bonus, "type": "credit",
                "note": f"Daily streak Day {streak}", "time": now_str(), "by": "system"})
    return jsonify({"streak": streak})

@app.route("/api/spin-wheel", methods=["POST"])
@usr_req
def api_spin_wheel():
    try:
        uid = session.get("uid","")
        doc = safe_find_one(users_col, {"_id": uid}) or {}
        last_spin = doc.get("last_spin","")
        if last_spin:
            try:
                ldt = datetime.fromisoformat(last_spin)
                if ldt.tzinfo is None: ldt = ldt.replace(tzinfo=IST)
                hrs = (now_ist() - ldt).total_seconds() / 3600
                if hrs < 24:
                    return jsonify({"success": False,
                        "error": f"Come back in {24-int(hrs)}h"})
            except: pass
        rewards = [5, 10, 15, 20, 25, 50, 100]
        if is_vip_user(uid):
            rewards = [10, 20, 30, 50, 75, 100, 200]
        reward = random.choice(rewards)
        safe_insert(wallet_col, {"user_id": uid, "amount": reward, "type": "credit",
            "note": "🎰 Lucky Wheel" + (" (VIP)" if is_vip_user(uid) else ""),
            "time": now_str(), "by": "system"})
        safe_update(users_col, {"_id": uid}, {"$set": {"last_spin": now_str()}})
        push_notif(uid, "🎰 Lucky Wheel", f"You won ₹{reward}!", "success")
        notify_admin("Lucky Wheel Spin",
            f"👤 <code>{uid}</code>\n💰 ₹{reward}" + (" 👶 VIP" if is_vip_user(uid) else ""), "success")
        return jsonify({"success": True, "reward": reward})
    except Exception as e: return jsonify({"success": False, "error": str(e)})

@app.route("/api/stats")
@helper_req
def api_stats():
    ratings = safe_find(ratings_col)
    avg = sum(r.get("stars",0) for r in ratings)/len(ratings) if ratings else 0
    today_start = now_ist().replace(hour=0,minute=0,second=0,microsecond=0)
    today_visits = safe_count(visits_col, {"time":{"$gte":today_start.isoformat()}})
    return jsonify({"total_orders":safe_count(orders_col),
        "paid_orders":safe_count(orders_col, {"status":"success"}),
        "pending_orders":safe_count(orders_col, {"status":"pending"}),
        "total_revenue":sum(o.get("amount",0) for o in safe_find(orders_col, {"status":"success"})),
        "total_products":safe_count(prods_col),
        "total_keys":safe_count(keys_col),
        "active_keys":safe_count(keys_col, {"redeemed_by":None,"expires":{"$gt":now_str_naive()}}),
        "store_users":safe_count(users_col),
        "avg_rating": round(avg,1), "total_ratings": len(ratings),
        "today_visits": today_visits,
        "vip_users": len(VIP_USERS),
        "helpers": safe_count(helpers_col),
        "total_coupons": safe_count(coupons_col, {"active":True})})

@app.route("/api/visitors")
@adm_req
def api_visitors():
    v = safe_find(visits_col, limit=100, sort=[("time",-1)])
    return jsonify([{"ip":x.get("ip",""),"path":x.get("path",""),
        "device":x.get("device",""),"time":x.get("time","")} for x in v])

@app.route("/api/command-logs")
@adm_req
def api_command_logs():
    c = safe_find(commands_col, limit=100, sort=[("time",-1)])
    return jsonify([{"user_id":x.get("user_id",""),"command":x.get("command",""),
        "details":x.get("details",""),"ip":x.get("ip",""),"time":x.get("time","")} for x in c])

@app.route("/api/system-stats")
@adm_req
def api_sys_stats():
    try:
        return jsonify({"cpu_percent": psutil.cpu_percent(interval=0.3),
            "memory_percent": psutil.virtual_memory().percent})
    except: return jsonify({"cpu_percent":0,"memory_percent":0})

@app.route("/api/system-health")
@adm_req
def api_sys_health():
    try:
        cpu = psutil.cpu_percent(interval=0.5); mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        hrs = int(uptime.total_seconds() // 3600)
        mins = int((uptime.total_seconds() % 3600) // 60)
        return jsonify({"cpu": cpu, "ram": mem.percent,
            "ram_total": round(mem.total / (1024**3), 2),
            "disk": disk.percent, "disk_free": round(disk.free / (1024**3), 2),
            "uptime": f"{hrs}H {mins}M", "python": sys.version.split()[0],
            "pid": os.getpid()})
    except: return jsonify({"cpu":0,"ram":0,"ram_total":0,"disk":0,
        "disk_free":0,"uptime":"-","python":"-","pid":0})

@app.route("/api/db-stats")
@adm_req
def api_db_stats():
    return jsonify({"orders": safe_count(orders_col),"keys": safe_count(keys_col),
        "users": safe_count(users_col),"products": safe_count(prods_col),
        "coupons": safe_count(coupons_col),"ratings": safe_count(ratings_col),
        "chats": safe_count(chat_col),"wallet_txns": safe_count(wallet_col),
        "logs": safe_count(logs_col),"notifications": safe_count(notif_col),
        "visitors": safe_count(visits_col),"commands": safe_count(commands_col),
        "helpers": safe_count(helpers_col)})

@app.route("/api/chart-7d")
@adm_req
def api_chart_7d():
    out = []
    for i in range(6, -1, -1):
        d = now_ist() - timedelta(days=i)
        dstart = d.replace(hour=0, minute=0, second=0, microsecond=0)
        dend = dstart + timedelta(days=1)
        rev = sum(o.get("amount",0) for o in safe_find(orders_col, {
            "status":"success",
            "paid_at": {"$gte": dstart.isoformat(), "$lt": dend.isoformat()}}))
        out.append({"label": d.strftime("%a %d"), "revenue": round(rev,2)})
    return jsonify(out)

@app.route("/api/chart-sparkline")
@adm_req
def api_chart_sparkline():
    now = now_ist()
    points = []
    for i in range(23, -1, -1):
        hr_start = (now - timedelta(hours=i)).replace(minute=0, second=0, microsecond=0)
        hr_end = hr_start + timedelta(hours=1)
        rev = sum(o.get("amount", 0) for o in safe_find(orders_col, {
            "status": "success",
            "paid_at": {"$gte": hr_start.isoformat(), "$lt": hr_end.isoformat()}
        }))
        points.append({"hour": hr_start.strftime("%H:00"), "revenue": round(rev, 2)})
    return jsonify(points)

@app.route("/api/bulk-orders", methods=["POST"])
@adm_req
def api_bulk_orders():
    d = request.get_json()
    action = d.get("action")
    order_ids = d.get("order_ids", [])
    if not action or not order_ids:
        return jsonify({"success": False, "error": "Missing params"})
    count = 0
    for oid in order_ids:
        o = safe_find_one(orders_col, {"_id": oid})
        if not o: continue
        try:
            if action == "resend":
                if o.get("key") and o.get("telegram_id"):
                    msg = (f"⚡ <b>Key Resent</b>\n🛒 <code>{oid}</code>\n"
                           f"🔑 <code>{o['key']}</code>")
                    if tg_send(o["telegram_id"], msg): count += 1
            elif action == "mark_paid":
                if o.get("status") != "success":
                    deliver(o); count += 1
            elif action == "delete":
                orders_col.delete_one({"_id": oid}); count += 1
            elif action == "refund":
                safe_update(orders_col, {"_id": oid},
                    {"$set": {"status": "refunded"}})
                if o.get("telegram_id"):
                    push_notif(o["telegram_id"], "💸 Refund Processed",
                        f"Order {oid} refunded", "warning")
                count += 1
        except Exception as e:
            print(f"[bulk {action}] {oid}: {e}")
    log_adm(f"bulk_{action}", f"{count}/{len(order_ids)}")
    return jsonify({"success": True, "count": count, "total": len(order_ids)})

@app.route("/api/search-orders")
@adm_req
def api_search_orders():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    min_amt = request.args.get("min", "").strip()
    max_amt = request.args.get("max", "").strip()
    date_from = request.args.get("from", "").strip()
    date_to = request.args.get("to", "").strip()
    query = {}
    if status and status != "all": query["status"] = status
    if min_amt or max_amt:
        amt_q = {}
        if min_amt:
            try: amt_q["$gte"] = float(min_amt)
            except: pass
        if max_amt:
            try: amt_q["$lte"] = float(max_amt)
            except: pass
        if amt_q: query["amount"] = amt_q
    if date_from or date_to:
        dt_q = {}
        if date_from: dt_q["$gte"] = date_from
        if date_to: dt_q["$lte"] = date_to + "T23:59:59"
        if dt_q: query["created_at"] = dt_q
    results = safe_find(orders_col, query, limit=300, sort=[("created_at", -1)])
    if q:
        ql = q.lower()
        results = [r for r in results if
                   ql in (r.get("order_id", "") or "").lower() or
                   ql in (r.get("customer_name", "") or "").lower() or
                   ql in (r.get("telegram_id", "") or "").lower() or
                   ql in (r.get("product_name", "") or "").lower()]
    return jsonify([{
        "order_id": x.get("order_id"), "customer_name": x.get("customer_name"),
        "telegram_id": x.get("telegram_id"), "product_name": x.get("product_name"),
        "amount": x.get("amount"), "status": x.get("status"),
        "key": x.get("key"), "created_at": x.get("created_at")
    } for x in results])

@app.route("/api/user-spending-chart")
@usr_req
def api_user_spending_chart():
    uid = session.get("uid", "")
    out = []
    for i in range(6, -1, -1):
        d = now_ist() - timedelta(days=i)
        ds = d.replace(hour=0, minute=0, second=0, microsecond=0)
        de = ds + timedelta(days=1)
        spent = sum(o.get("amount", 0) for o in safe_find(orders_col, {
            "telegram_id": uid, "status": "success",
            "paid_at": {"$gte": ds.isoformat(), "$lt": de.isoformat()}
        }))
        out.append({"label": d.strftime("%a"), "spent": round(spent, 2)})
    return jsonify(out)

@app.route("/api/leaderboard")
@adm_req
def api_leaderboard():
    paid = safe_find(orders_col, {"status":"success"})
    agg = {}
    for o in paid:
        uid = str(o.get("telegram_id",""))
        if not uid: continue
        if uid not in agg: agg[uid] = {"spent":0, "orders":0}
        agg[uid]["spent"] += o.get("amount",0); agg[uid]["orders"] += 1
    out = [{"user_id":k, "spent":round(v["spent"],2), "orders":v["orders"]}
           for k,v in agg.items()]
    out.sort(key=lambda x: x["spent"], reverse=True)
    return jsonify(out[:10])

@app.route("/api/analytics")
@adm_req
def api_analytics():
    now = now_ist()
    today = now.replace(hour=0,minute=0,second=0,microsecond=0)
    week = now - timedelta(days=7); month = now - timedelta(days=30)
    paid = safe_find(orders_col, {"status":"success"})
    def rev_since(dt):
        tot = 0
        for o in paid:
            pa = o.get("paid_at","")
            if not pa: continue
            try:
                pdt = datetime.fromisoformat(pa)
                if pdt.tzinfo is None: pdt = pdt.replace(tzinfo=IST)
                if pdt >= dt: tot += o.get("amount",0)
            except: pass
        return tot
    from collections import Counter
    pc = Counter(o.get("product_name","?") for o in paid)
    prev = {}
    for o in paid:
        n = o.get("product_name","?"); prev[n] = prev.get(n,0) + o.get("amount",0)
    top = [{"_id":n,"count":c,"revenue":prev.get(n,0)} for n,c in pc.most_common(5)]
    return jsonify({"today":rev_since(today),"week":rev_since(week),
        "month":rev_since(month),
        "avg": round(sum(o.get("amount",0) for o in paid)/len(paid),2) if paid else 0,
        "top":top})

@app.route("/api/broadcast", methods=["POST"])
@adm_req
def api_broadcast():
    try:
        d = request.get_json()
        msg = (d.get("message") or "").strip()
        if not msg: return jsonify({"success":False,"error":"Empty"})
        tg_ids = set()
        if d.get("to_buyers"):
            for o in safe_find(orders_col, {"status":"success"}):
                tid = o.get("telegram_id")
                if tid and str(tid).strip(): tg_ids.add(str(tid).strip())
        if d.get("to_known"):
            for k in safe_find(known_col):
                if k.get("_id"): tg_ids.add(str(k["_id"]))
        sent = 0; failed = 0
        for tid in tg_ids:
            if tg_send(tid, msg): sent += 1
            else: failed += 1
            time.sleep(0.02)
        log_adm("broadcast", f"{sent} sent, {failed} failed")
        return jsonify({"success":True,"sent":sent,"failed":failed})
    except Exception as e: return jsonify({"success":False,"error":str(e)})

@app.route("/api/send-notification", methods=["POST"])
@adm_req
def api_send_notification():
    try:
        d = request.get_json()
        uid = (d.get("user_id") or "").strip()
        title = (d.get("title") or "").strip()
        body = (d.get("body") or "").strip()
        typ = d.get("type", "info")
        if not title or not body: return jsonify({"success":False,"error":"Missing"})
        count = 0
        if uid.upper() == "ALL":
            for u in safe_find(users_col, limit=500):
                push_notif(u["_id"], title, body, typ); count += 1
        elif uid:
            push_notif(uid, title, body, typ); count = 1
        log_adm("send_notification", f"to {uid}: {title[:40]}")
        return jsonify({"success":True, "count": count})
    except Exception as e: return jsonify({"success":False,"error":str(e)})

@app.route("/api/recent-orders")
@adm_req
def api_ro():
    o = safe_find(orders_col, limit=10, sort=[("created_at",-1)])
    return jsonify([{"order_id":x.get("order_id"),"product_name":x.get("product_name"),
        "amount":x.get("amount"),"status":x.get("status"),
        "created_at":x.get("created_at")} for x in o])

@app.route("/api/orders")
@helper_req
def api_ord():
    o = safe_find(orders_col, limit=500, sort=[("created_at",-1)])
    return jsonify([{"order_id":x.get("order_id"),"customer_name":x.get("customer_name"),
        "telegram_id":x.get("telegram_id"),"product_name":x.get("product_name"),
        "amount":x.get("amount"),"status":x.get("status"),"key":x.get("key"),
        "created_at":x.get("created_at")} for x in o])

@app.route("/api/order-detail/<oid>")
@adm_req
def api_order_detail(oid):
    o = safe_find_one(orders_col, {"_id": oid})
    if not o: return jsonify({"error":"not found"}), 404
    o["_id"] = str(o["_id"]); return jsonify(o)

@app.route("/api/user-detail/<uid>")
@adm_req
def api_user_detail(uid):
    u = safe_find_one(users_col, {"_id": uid}) or {"_id": uid}
    orders = safe_find(orders_col, {"telegram_id": uid, "status":"success"})
    spent = sum(o.get("amount",0) for o in orders); tier, _ = get_tier(spent)
    recent = [{"order_id":x.get("order_id",""),"amount":x.get("amount",0),
               "status":x.get("status","")}
              for x in safe_find(orders_col, {"telegram_id": uid},
                                 limit=5, sort=[("created_at",-1)])]
    return jsonify({"user_id": uid,"created_at": fmt(u.get("created_at","")),
        "total_orders": len(orders),"spent": round(spent,2),
        "balance": get_balance(uid),"referral_code": u.get("referral_code",""),
        "referred_by": u.get("referred_by",""),"tier": tier,
        "recent_orders": recent})

@app.route("/api/products-admin")
@adm_req
def api_padm(): return jsonify(safe_find(prods_col, sort=[("order",1)]))

@app.route("/api/add-product", methods=["POST"])
@adm_req
def api_ap():
    d = request.get_json()
    pid = d.get("id","").strip()
    if not pid: return jsonify({"success":False,"error":"ID required"})
    if safe_count(prods_col, {"_id":pid}) > 0:
        return jsonify({"success":False,"error":"ID exists"})
    safe_insert(prods_col, {"_id":pid,"name":d.get("name",""),
        "duration":d.get("duration",""),"category":d.get("category",""),
        "hours":int(d.get("hours",0)),"price":float(d.get("price",0)),
        "max_time":int(d.get("max_time",DEFAULT_MAX_TIME)),
        "max_concurrent":int(d.get("max_concurrent",DEFAULT_MAX_CONC)),
        "cooldown":int(d.get("cooldown",DEFAULT_COOLDOWN)),
        "active":True,"order":999,"popular":d.get("popular",False)})
    log_adm("add_product",pid); return jsonify({"success":True})

@app.route("/api/product-admin/<pid>")
def api_padm2(pid):
    p = safe_find_one(prods_col, {"_id":pid})
    if not p: return jsonify({"error":"Not found"}),404
    return jsonify({**p,"_id":pid})

@app.route("/api/update-product/<pid>", methods=["POST"])
@adm_req
def api_up(pid):
    d = request.get_json()
    safe_update(prods_col, {"_id":pid}, {"$set":{
        "name":d.get("name"),"duration":d.get("duration"),
        "category":d.get("category",""),"hours":int(d.get("hours",0)),
        "price":float(d.get("price",0)),
        "max_time":int(d.get("max_time",DEFAULT_MAX_TIME)),
        "max_concurrent":int(d.get("max_concurrent",DEFAULT_MAX_CONC)),
        "cooldown":int(d.get("cooldown",DEFAULT_COOLDOWN)),
        "popular":d.get("popular",False)}})
    log_adm("update_product",pid); return jsonify({"success":True})

@app.route("/api/toggle-product/<pid>", methods=["POST"])
@adm_req
def api_tp(pid):
    p = safe_find_one(prods_col, {"_id":pid})
    if p:
        safe_update(prods_col, {"_id":pid}, {"$set":{"active":not p.get("active",True)}})
    return jsonify({"success":True})

@app.route("/api/delete-product/<pid>", methods=["POST"])
@adm_req
def api_dp(pid):
    safe_delete(prods_col, {"_id":pid})
    log_adm("delete_product",pid); return jsonify({"success":True})

@app.route("/api/bulk-price-update", methods=["POST"])
@adm_req
def api_bulk_price():
    try:
        d = request.get_json()
        cat = (d.get("category") or "ALL").strip().upper()
        op = d.get("op", "pct"); val = float(d.get("value", 0))
        q = {} if cat == "ALL" else {"category": cat}
        products = safe_find(prods_col, q); count = 0
        for p in products:
            old = float(p.get("price", 0))
            if op == "pct": new = round(old * (1 + val/100), 2)
            else: new = max(0, round(old + val, 2))
            safe_update(prods_col, {"_id": p["_id"]}, {"$set": {"price": new}})
            count += 1
        log_adm("bulk_price_update", f"{count} products")
        return jsonify({"success":True, "count": count})
    except Exception as e: return jsonify({"success":False,"error":str(e)})

@app.route("/api/generate-keys", methods=["POST"])
@adm_req
def api_gk():
    d = request.get_json()
    prefix = d.get("prefix","VIP").upper(); dur = d.get("duration","1d").lower()
    cnt = min(int(d.get("count",1)),100)
    mt = min(max(int(d.get("max_time",DEFAULT_MAX_TIME)),30),400)
    cd = min(max(int(d.get("cooldown",DEFAULT_COOLDOWN)),10),300)
    if dur.endswith('hr') or dur.endswith('h'):
        hrs = int(dur.replace('hr','').replace('h','').strip()); dl = f"{hrs} Hour(s)"
    elif dur.endswith('d'):
        days = int(dur.replace('d','').strip()); hrs = days*24; dl = f"{days} Day(s)"
    else: return jsonify({"error":"Invalid duration"}),400
    exp_str = (now_ist() + timedelta(hours=hrs)).strftime("%Y-%m-%d %H:%M:%S")
    codes = []
    for _ in range(cnt):
        c = gen_code(prefix,12)
        safe_insert(keys_col, {"_id":c,"type":"admin_generated","attacks_left":-1,
            "max_duration":mt,"cooldown":cd,"expires":exp_str,
            "max_concurrent":setting("max_concurrent", DEFAULT_MAX_CONC),
            "created_by":session.get("username","admin"),
            "redeemed_by":None,"redeemed_at":None,"trial":False,
            "created_at":now_str(),"duration_label":dl,"duration_hours":hrs})
        codes.append(c)
    log_adm("generate_keys",f"{cnt} keys ({dl})")
    return jsonify({"success":True,"codes":codes,"count":cnt})

@app.route("/api/active-keys")
@adm_req
def api_ak():
    k = safe_find(keys_col, {"redeemed_by":None,
        "expires":{"$gt":now_str_naive()}}, limit=500)
    return jsonify([{"code":x.get("_id"),"type":x.get("type"),
        "duration_label":x.get("duration_label","-"),"expires":x.get("expires"),
        "max_duration":x.get("max_duration",400)} for x in k])

@app.route("/api/redeemed-keys")
@adm_req
def api_rk():
    k = safe_find(keys_col, {"redeemed_by":{"$ne":None}}, limit=500,
        sort=[("redeemed_at",-1)])
    return jsonify([{"code":x.get("_id"),"redeemed_by":x.get("redeemed_by"),
        "redeemed_at":x.get("redeemed_at"),"expires":x.get("expires")} for x in k])

@app.route("/api/store-users")
@adm_req
def api_su():
    u = safe_find(users_col, limit=200, sort=[("created_at",-1)])
    return jsonify([{"user_id":x.get("_id"),"created_at":x.get("created_at"),
        "total_orders":x.get("total_orders",0),
        "balance": get_balance(x.get("_id"))} for x in u])

@app.route("/api/helpers")
@adm_req
def api_helpers():
    h = safe_find(helpers_col, limit=100)
    return jsonify([{"username":x.get("_id"),"added_at":x.get("added_at"),
        "active":x.get("active",True)} for x in h])

@app.route("/api/add-helper", methods=["POST"])
@adm_req
def api_add_helper():
    d = request.get_json()
    u = (d.get("username") or "").strip(); p = (d.get("password") or "").strip()
    if not u or not p: return jsonify({"success":False,"error":"Missing"})
    if safe_count(helpers_col, {"_id":u}) > 0:
        return jsonify({"success":False,"error":"Exists"})
    safe_insert(helpers_col, {"_id":u,"password":p,"added_at":now_str(),
        "active":True,"added_by":session.get("username","admin")})
    log_adm("add_helper",u); return jsonify({"success":True})

@app.route("/api/delete-helper", methods=["POST"])
@adm_req
def api_del_helper():
    d = request.get_json()
    safe_delete(helpers_col, {"_id":d.get("username","")})
    log_adm("delete_helper",d.get("username",""))
    return jsonify({"success":True})

@app.route("/api/known-users")
@adm_req
def api_ku():
    u = safe_find(known_col, limit=100, sort=[("last_seen",-1)])
    return jsonify([{"user_id":x.get("_id"),"last_seen":x.get("last_seen")} for x in u])

@app.route("/api/banned")
@adm_req
def api_bn():
    b = safe_find(bans_col, limit=100)
    return jsonify([{"user_id":x.get("_id"),"banned_at":x.get("banned_at")} for x in b])

@app.route("/api/ban", methods=["POST"])
@adm_req
def api_b():
    d = request.get_json(); uid = str(d.get("user_id",""))
    if safe_count(bans_col, {"_id":uid}) == 0:
        safe_insert(bans_col, {"_id":uid,"banned_by":session.get("username","admin"),
            "banned_at":now_str()})
        log_adm("ban",uid)
    return jsonify({"success":True})

@app.route("/api/unban", methods=["POST"])
@adm_req
def api_ub():
    d = request.get_json()
    safe_delete(bans_col, {"_id":str(d.get("user_id",""))})
    log_adm("unban",d.get("user_id","")); return jsonify({"success":True})

@app.route("/api/settings", methods=["GET","POST"])
@adm_req
def api_st():
    if request.method == "GET":
        s = safe_find_one(settings_col, {}) or {}
        s.pop("_id",None); return jsonify(s)
    d = request.get_json()
    settings_col.update_one({},{"$set":d},upsert=True)
    log_adm("update_settings",json.dumps(d)[:200])
    return jsonify({"success":True})

@app.route("/api/logs")
@adm_req
def api_lg():
    return jsonify([{"timestamp":x.get("timestamp"),"admin_id":x.get("admin_id"),
        "action":x.get("action"),"details":x.get("details")}
        for x in safe_find(logs_col, limit=100, sort=[("timestamp",-1)])])

@app.route("/api/backup")
@adm_req
def api_backup():
    try:
        data = {"timestamp": now_str(),
            "products": safe_find(prods_col),
            "coupons": safe_find(coupons_col),
            "settings": safe_find(settings_col),
            "users": safe_find(users_col),
            "faqs": safe_find(faqs_col),
            "testimonials": safe_find(testimonials_col)}
        for coll in ["coupons","settings","users","faqs","testimonials","products"]:
            for i, doc in enumerate(data[coll]):
                if "_id" in doc: data[coll][i]["_id"] = str(doc["_id"])
        return Response(json.dumps(data, default=str, indent=2),
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment; filename=flash_v15_backup_{int(time.time())}.json"})
    except Exception as e: return jsonify({"success":False,"error":str(e)})

@app.route("/api/restore", methods=["POST"])
@adm_req
def api_restore():
    try:
        data = request.get_json()
        if not data: return jsonify({"success":False,"error":"No data"})
        count = 0
        for coll_name, col_obj in [("products",prods_col),("coupons",coupons_col),
                                    ("settings",settings_col),("faqs",faqs_col),
                                    ("testimonials",testimonials_col)]:
            if coll_name in data:
                col_obj.delete_many({})
                for item in data[coll_name]:
                    item.pop("_id", None); col_obj.insert_one(item)
                count += 1
        log_adm("restore_backup", f"{count}")
        return jsonify({"success":True, "count": count})
    except Exception as e: return jsonify({"success":False,"error":str(e)})

@app.route("/api/ratings")
@adm_req
def api_ratings():
    all_r = safe_find(ratings_col, limit=200, sort=[("time",-1)])
    total = len(all_r)
    avg = sum(r.get("stars",0) for r in all_r)/total if total else 0
    return jsonify({"avg": round(avg,1), "total": total,
        "five": sum(1 for r in all_r if r.get("stars")==5),
        "one": sum(1 for r in all_r if r.get("stars")==1),
        "list": [{"order_id": r.get("order_id"), "stars": r.get("stars",0),
            "comment": r.get("comment",""), "time": r.get("time","")} for r in all_r]})

@app.route("/api/resend-key", methods=["POST"])
@adm_req
def api_resend_key():
    try:
        d = request.get_json(); o = safe_find_one(orders_col, {"_id": d.get("order_id")})
        if not o or not o.get("key"):
            return jsonify({"success":False,"error":"No key"})
        tg = o.get("telegram_id")
        if not tg: return jsonify({"success":False,"error":"No tg"})
        msg = (f"⚡ <b>Key Resent</b>\n🛒 <code>{o['order_id']}</code>\n"
               f"🔑 <code>{o['key']}</code>")
        ok = tg_send(tg, msg); log_adm("resend_key", o["order_id"])
        return jsonify({"success": ok})
    except Exception as e: return jsonify({"success":False,"error":str(e)})

@app.route("/api/export-orders")
@adm_req
def api_export_orders():
    si = io.StringIO(); cw = csv.writer(si)
    cw.writerow(["Order ID","Customer","Telegram ID","Product","Amount",
                 "Discount","Coupon","Status","Key","Created","Paid"])
    for o in safe_find(orders_col, sort=[("created_at",-1)]):
        cw.writerow([o.get("order_id",""), o.get("customer_name",""),
            o.get("telegram_id",""), o.get("product_name",""), o.get("amount",""),
            o.get("discount",""), o.get("coupon",""), o.get("status",""),
            o.get("key","") or "", o.get("created_at",""), o.get("paid_at","") or ""])
    return Response(si.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=flash_v15_orders.csv"})

@app.route("/api/delete-key", methods=["POST"])
@adm_req
def api_delete_key():
    d = request.get_json(); safe_delete(keys_col, {"_id": d.get("code","")})
    log_adm("delete_key", d.get("code","")); return jsonify({"success":True})

@app.route("/api/extend-key", methods=["POST"])
@adm_req
def api_extend_key():
    try:
        d = request.get_json(); code = d.get("code",""); hrs = int(d.get("hours",24))
        k = safe_find_one(keys_col, {"_id": code})
        if not k: return jsonify({"success":False,"error":"Not found"})
        old_exp = k.get("expires")
        if old_exp:
            try:
                base = datetime.strptime(old_exp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=IST)
            except: base = now_ist()
        else: base = now_ist()
        if base < now_ist(): base = now_ist()
        new_exp = base + timedelta(hours=hrs)
        safe_update(keys_col, {"_id":code},
            {"$set":{"expires":new_exp.strftime("%Y-%m-%d %H:%M:%S")}})
        log_adm("extend_key", f"{code} +{hrs}h"); return jsonify({"success":True})
    except Exception as e: return jsonify({"success":False,"error":str(e)})

@app.route("/api/clean-expired-keys", methods=["POST"])
@adm_req
def api_clean_expired():
    r = keys_col.delete_many({"redeemed_by":None,"expires":{"$lt":now_str_naive()}})
    log_adm("clean_expired", f"{r.deleted_count}")
    return jsonify({"success":True,"count":r.deleted_count})

@app.route("/api/revoke-key", methods=["POST"])
@adm_req
def api_revoke_key():
    d = request.get_json()
    safe_update(keys_col, {"_id":d.get("code","")},
        {"$set":{"redeemed_by":None,"revoked":True,"revoked_at":now_str(),
                 "expires":now_str_naive()}})
    log_adm("revoke_key", d.get("code","")); return jsonify({"success":True})

@app.route("/api/revoke-expired", methods=["POST"])
@adm_req
def api_revoke_expired():
    r = keys_col.update_many({"redeemed_by":{"$ne":None},
        "expires":{"$lt":now_str_naive()}},{"$set":{"revoked":True}})
    log_adm("revoke_expired", f"{r.modified_count}")
    return jsonify({"success":True,"count":r.modified_count})

@app.route("/api/send-dm", methods=["POST"])
@adm_req
def api_send_dm():
    d = request.get_json()
    ok = tg_send(str(d.get("user_id","")), d.get("message",""))
    log_adm("send_dm", d.get("user_id","")); return jsonify({"success":ok})

@app.route("/api/export-keys")
@adm_req
def api_export_keys():
    si = io.StringIO(); cw = csv.writer(si)
    cw.writerow(["Code","Type","Duration","Expires","Max Time","Created By","Created At"])
    for k in safe_find(keys_col, {"redeemed_by":None}, sort=[("created_at",-1)]):
        cw.writerow([k.get("_id",""),k.get("type",""),k.get("duration_label",""),
            k.get("expires",""),k.get("max_duration",""),
            k.get("created_by",""),k.get("created_at","")])
    return Response(si.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition":"attachment; filename=active_keys.csv"})

@app.route("/api/export-redeemed")
@adm_req
def api_export_redeemed():
    si = io.StringIO(); cw = csv.writer(si)
    cw.writerow(["Code","Redeemed By","Redeemed At","Expires","Duration"])
    for k in safe_find(keys_col, {"redeemed_by":{"$ne":None}}, sort=[("redeemed_at",-1)]):
        cw.writerow([k.get("_id",""),k.get("redeemed_by",""),
            k.get("redeemed_at",""),k.get("expires",""),k.get("duration_label","")])
    return Response(si.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition":"attachment; filename=redeemed_keys.csv"})

@app.route("/api/coupons")
@adm_req
def api_coupons():
    return jsonify([{**{k:v for k,v in c.items() if k!="_id"},
                     "code": c.get("code","")}
                    for c in safe_find(coupons_col, sort=[("code",1)])])

@app.route("/api/add-coupon", methods=["POST"])
@adm_req
def api_add_coupon():
    d = request.get_json()
    code = (d.get("code") or "").strip().upper()
    if not code: return jsonify({"success":False,"error":"Code required"})
    if safe_count(coupons_col, {"code": code}) > 0:
        return jsonify({"success":False,"error":"Exists"})
    safe_insert(coupons_col, {"code": code, "type": d.get("type","percent"),
        "value": float(d.get("value",0)), "min_order": float(d.get("min_order",0)),
        "max_uses": int(d.get("max_uses",0)), "uses": 0,
        "expires": d.get("expires") or None, "active": True, "created_at": now_str()})
    log_adm("add_coupon", code); return jsonify({"success":True})

@app.route("/api/delete-coupon", methods=["POST"])
@adm_req
def api_del_coupon():
    d = request.get_json(); safe_delete(coupons_col, {"code": d.get("code","")})
    log_adm("delete_coupon", d.get("code","")); return jsonify({"success":True})

@app.route("/api/add-balance", methods=["POST"])
@adm_req
def api_add_balance():
    try:
        d = request.get_json()
        uid = str(d.get("user_id","")); amt = float(d.get("amount",0))
        if not uid or amt <= 0:
            return jsonify({"success":False,"error":"Invalid"})
        safe_insert(wallet_col, {"user_id": uid, "amount": amt, "type": "credit",
            "note": d.get("note",""), "time": now_str(),
            "by": session.get("username","admin")})
        push_notif(uid, "💰 Wallet Credited",
            f"₹{amt} added. Note: {d.get('note','')}", "success")
        log_adm("add_balance", f"{uid} +₹{amt}")
        return jsonify({"success":True})
    except Exception as e: return jsonify({"success":False,"error":str(e)})

@app.route("/api/faqs-all")
@adm_req
def api_faqs_all():
    return jsonify([{"_id":str(f["_id"]),"q":f.get("q",""),"a":f.get("a","")}
                    for f in safe_find(faqs_col, sort=[("order",1)])])

@app.route("/api/add-faq", methods=["POST"])
@adm_req
def api_add_faq():
    d = request.get_json()
    safe_insert(faqs_col, {"q":d.get("q",""),"a":d.get("a",""),
        "order":int(time.time())})
    log_adm("add_faq", d.get("q","")[:50]); return jsonify({"success":True})

@app.route("/api/delete-faq", methods=["POST"])
@adm_req
def api_del_faq():
    d = request.get_json()
    try: safe_delete(faqs_col, {"_id": ObjectId(d.get("id"))})
    except: pass
    return jsonify({"success":True})

@app.route("/api/testimonials-all")
@adm_req
def api_testimonials_all():
    return jsonify([{"_id":str(t["_id"]),"text":t.get("text",""),
                     "who":t.get("who",""),"stars":t.get("stars",5)}
                    for t in safe_find(testimonials_col, sort=[("order",1)])])

@app.route("/api/add-testimonial", methods=["POST"])
@adm_req
def api_add_testimonial():
    d = request.get_json()
    safe_insert(testimonials_col, {"text":d.get("text",""),"who":d.get("who",""),
        "stars":int(d.get("stars",5)),"order":int(time.time())})
    return jsonify({"success":True})

@app.route("/api/delete-testimonial", methods=["POST"])
@adm_req
def api_del_testimonial():
    d = request.get_json()
    try: safe_delete(testimonials_col, {"_id": ObjectId(d.get("id"))})
    except: pass
    return jsonify({"success":True})

@app.route("/api/order-comments/<oid>", methods=["GET"])
@adm_req
def api_order_comments(oid):
    return jsonify(get_admin_comments("order", oid))

@app.route("/api/order-comments/<oid>/add", methods=["POST"])
@adm_req
def api_add_order_comment(oid):
    d = request.get_json()
    cid = add_admin_comment("order", oid, d.get("comment", ""),
        tags=d.get("tags", []), priority=d.get("priority", "normal"))
    log_adm("add_order_comment", f"{oid}: {d.get('comment','')[:60]}")
    return jsonify({"success": bool(cid), "id": cid})

@app.route("/api/comment/pin", methods=["POST"])
@adm_req
def api_pin_comment():
    d = request.get_json()
    try:
        comments_col.update_one({"_id": ObjectId(d.get("id"))},
            {"$set": {"pinned": bool(d.get("pinned", True)), "updated_at": now_str()}})
        return jsonify({"success": True})
    except: return jsonify({"success": False})

@app.route("/api/comment/delete", methods=["POST"])
@adm_req
def api_del_comment():
    d = request.get_json()
    try:
        comments_col.delete_one({"_id": ObjectId(d.get("id"))})
        return jsonify({"success": True})
    except: return jsonify({"success": False})

@app.route("/api/user-notes/<uid>", methods=["GET"])
@adm_req
def api_user_notes(uid):
    return jsonify(get_admin_comments("user", uid))

@app.route("/api/user-notes/<uid>/add", methods=["POST"])
@adm_req
def api_add_user_note(uid):
    d = request.get_json()
    cid = add_admin_comment("user", uid, d.get("comment", ""),
        tags=d.get("tags", []), priority=d.get("priority", "normal"))
    return jsonify({"success": bool(cid), "id": cid})

@app.route("/api/my-locks")
@usr_req
def api_my_locks():
    return jsonify(get_user_locks(session.get("uid", "")))

@app.route("/api/admin/user-locks/<uid>", methods=["GET"])
@adm_req
def api_admin_user_locks(uid):
    locks = safe_find(premium_locks_col, {"user_id": str(uid)})
    for l in locks: l["_id"] = str(l["_id"])
    return jsonify({"purchased": user_has_purchased(uid), "locks": locks})

@app.route("/api/admin/toggle-lock", methods=["POST"])
@adm_req
def api_admin_toggle_lock():
    d = request.get_json()
    uid = d.get("user_id"); feat = d.get("feature"); action = d.get("action")
    if action == "lock": create_premium_lock(uid, feat, d.get("reason", ""))
    else: remove_premium_lock(uid, feat)
    log_adm(f"{action}_lock", f"{uid}:{feat}")
    return jsonify({"success": True})

@app.route("/api/public-lock-check")
def api_public_lock_check():
    try: return jsonify({"is_premium": False, "progress": 0})
    except: return jsonify({"is_premium": False, "progress": 0})

# ⚠️ Vercel limitation: SSE not reliable — return simple polling-compatible endpoint
@app.route("/api/orders/stream")
@adm_req
def orders_stream():
    """Returns current order count only — client polls this"""
    try:
        count = safe_count(orders_col)
        return jsonify({"count": count, "type": "poll"})
    except:
        return jsonify({"count": 0, "type": "poll"})

# ================= HEALTH CHECK =================
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "mongo": "connected" if cli else "disconnected",
        "time": now_str(),
        "platform": "vercel" if os.environ.get("VERCEL") else "local"
    })

@app.route("/debug")
def debug():
    return jsonify({
        "mongo_ok": cli is not None,
        "products_count": safe_count(prods_col),
        "orders_count": safe_count(orders_col),
        "media_dir": CHAT_MEDIA_DIR,
        "media_dir_exists": os.path.exists(CHAT_MEDIA_DIR),
        "env": {k: "***" if "key" in k.lower() or "token" in k.lower() or "uri" in k.lower() else v
                for k,v in os.environ.items() if k in ["VERCEL", "PORT", "FLASK_SECRET"]}
    })

# ================= VERCEL HANDLER =================
# Vercel needs `app` at module level (already defined above)
# No `if __name__ == "__main__"` — Vercel imports this module

if __name__ == "__main__":
    # Local dev only
    print(f"[local] http://localhost:{PORT}")
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
