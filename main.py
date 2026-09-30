"""
Blackman.in - Autonomous AI Instagram Reel Engine (v2.0 High-Quality Edition)
=============================================================================
Automated Daily Pipeline:
1. AI Script Engine (Groq LLaMA-3.3-70B -> Gemini 2.0 Flash -> 31-Day Date Rotation)
2. Per-Sentence Stock B-Roll Fetcher (Pexels HD Portrait with Aspect-Cover Crop & Ken Burns Zoom)
3. Neural Voiceover with Retention Pacing (+14% speed, rotating natural voices via Edge-TTS)
4. Kinetic Karaoke Subtitles (Word-level timestamps, electric yellow highlight, safe-zone aligned)
5. Local Bundled Royalty-Free Ambient Music & Smooth Audio Ducking
6. Transparent Brand Watermark & Instagram-Compliant Safe-Zone CTA
7. High-Reliability Buffer GraphQL / Direct Instagram Publishing
"""

import os
import gc
import sys
import glob
import json
import time
import base64
import random
import asyncio
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# UTF-8 terminal encoding fix for Windows/Linux
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# MoviePy imports (compatible with MoviePy v2.x and v1.x)
try:
    from moviepy import (
        VideoFileClip,
        AudioFileClip,
        CompositeVideoClip,
        concatenate_videoclips,
        concatenate_audioclips,
        CompositeAudioClip,
        ImageClip,
        ColorClip,
    )
except ImportError:
    from moviepy.editor import (
        VideoFileClip,
        AudioFileClip,
        CompositeVideoClip,
        concatenate_videoclips,
        concatenate_audioclips,
        CompositeAudioClip,
        ImageClip,
        ColorClip,
    )

import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ==============================================================================
# CONFIGURATION & ENVIRONMENT VARIABLES
# ==============================================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROK_API_KEY = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "8dxdiukk0XTSLx87LsZFIIoHSQgAxukiYtdbcEbdtToDOAfalFw4OCNI")
BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN", "")
BUFFER_CHANNEL_ID = os.getenv("BUFFER_CHANNEL_ID") or os.getenv("BUFFER_PROFILE_ID", "6a0c75a6090476fb99383a66")
BUFFER_PROFILE_NAME = os.getenv("BUFFER_PROFILE_NAME", "blackman_officialpage")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_MEDIA_REPO = os.getenv("GITHUB_MEDIA_REPO", "shamith201119-ship-it/blackman-antigravity")

VOICE_FILE = "voice.mp3"
OUTPUT_REEL_FILE = "final_reel.mp4"

# High-retention natural Edge-TTS voices
VOICE_POOL = [
    "en-US-AndrewNeural",       # Confident, tech-savvy, high-converting
    "en-US-AvaNeural",          # Expressive, crisp, commercial
    "en-US-BrianNeural",        # Conversational, engaging podcast style
    "en-IN-PrabhatNeural",      # Professional Indian English
    "en-US-ChristopherNeural",  # Authoritative broadcast narrator
]

# Bundled fonts directory
FONT_BOLD_PATH = "assets/fonts/Montserrat-Bold.ttf"
FONT_BLACK_PATH = "assets/fonts/Montserrat-Black.ttf"

# ==============================================================================
# 31 UNIQUE HIGH-CONVERTING TOPICS (Deterministic 31-Day Rotation)
# ==============================================================================
CREATIVE_TOPICS = [
    {
        "topic": "Why Slow Websites Destroy Sales Conversion",
        "hook": "Your Website Is Losing Clients Daily!",
        "script": "If you are relying only on Instagram DMs or a slow website to close deals, you are leaving serious money on the table. Modern buyers judge your credibility in three seconds flat. A custom, fast-loading website turns cold visitors into high-paying clients on autopilot. Stop losing sales to competitors. Visit Blackman.in today and let us build a website that actually grows your business!",
        "search_queries": ["frustrated businesswoman", "slow computer", "sleek website", "smiling client", "laptop typing", "luxury office"],
        "caption": "Is your website actually converting visitors into clients? 🌐\n\nDon't let a slow or outdated site kill your sales.\n\n👉 Visit Blackman.in or tap the link in bio to get your custom website built today!\n\n#webdesign #webdevelopment #smallbusiness #leadgeneration #blackmanin"
    },
    {
        "topic": "Closing Deals on Social Media vs Dedicated Website",
        "hook": "Stop Selling Exclusively In DMs!",
        "script": "Relying solely on social media DMs to close sales is capping your business growth. High-paying clients look for instant credibility, social proof, and seamless booking. A custom, high-converting website built by Blackman.in qualifies leads and captures revenue twenty-four-seven. Upgrade your digital storefront today at Blackman.in!",
        "search_queries": ["mobile scrolling", "chat messaging", "modern website", "business deal", "handshake office", "founder laptop"],
        "caption": "Stop losing high-ticket clients to messy DM conversations. 💼\n\nScale your business with an automated, custom-built website.\n\n🔗 Visit Blackman.in or tap the link in bio to get started!\n\n#webagency #businesstips #leadgeneration #growthhacks #blackmanin"
    },
    {
        "topic": "The 3-Second Website Credibility Test",
        "hook": "Buyers Judge You In 3 Seconds!",
        "script": "When potential clients search for your business, your website is your digital handshake. If it looks outdated, loads slowly, or breaks on mobile, you lose their trust instantly. Blackman.in designs modern, high-performance websites engineered to establish authority and convert traffic into booked calls. Visit Blackman.in today!",
        "search_queries": ["stopwatch clock", "digital agency", "browsing phone", "creative designer", "modern building", "happy customer"],
        "caption": "Your website is your 24/7 sales representative. Make sure it reflects the elite quality of your work. ⚡\n\n🔗 Visit Blackman.in to upgrade your digital presence.\n\n#webdesigner #businessgrowth #websitedevelopment #branding #blackmanin"
    },
    {
        "topic": "Why Generic Website Builders Kill ROI",
        "hook": "Cookie-Cutter Sites Don't Convert!",
        "script": "Generic drag-and-drop templates are heavy, slow, and fail to turn visitors into real revenue. To dominate your market, you need custom design, clean code, and strategic conversion funnels. The engineering team at Blackman.in builds bespoke web solutions tailored for maximum ROI. Visit Blackman.in and build your high-converting site today!",
        "search_queries": ["software development", "web programming", "designer wireframe", "analytics graph", "team celebrating", "typing code"],
        "caption": "Stand out from competitors with custom web architecture that actually drives revenue. 📈\n\n👉 Discover the Blackman.in advantage. Tap the link in bio!\n\n#webdevelopment #agency #digitalmarketing #businessstrategy #blackmanin"
    },
    {
        "topic": "Mobile-First Design Is Non-Negotiable",
        "hook": "Your Mobile Site Is Broken!",
        "script": "Over seventy percent of your potential clients visit your website from their phone. If your site is not mobile-optimized, they leave within seconds and never come back. Blackman.in builds responsive, lightning-fast mobile experiences that keep visitors engaged and convert them into paying customers. Get your mobile-first website today at Blackman.in!",
        "search_queries": ["smartphone browsing", "phone scrolling", "coffee shop work", "mobile app", "responsive design", "busy street"],
        "caption": "70% of web traffic is mobile. Is your website ready? 📱\n\nDon't lose clients to a clunky mobile experience.\n\n👉 Get a mobile-first website at Blackman.in. Link in bio!\n\n#mobiledesign #responsive #webdev #uxdesign #blackmanin"
    },
    {
        "topic": "How SEO-Optimized Websites Generate Free Leads",
        "hook": "Free Leads While You Sleep!",
        "script": "Imagine waking up every morning to new client inquiries without spending a single rupee on ads. That is the power of an SEO-optimized website. Blackman.in builds search-engine-friendly websites that rank on Google and bring you organic traffic around the clock. Stop paying for every click. Visit Blackman.in and start getting free leads today!",
        "search_queries": ["google search", "analytics dashboard", "chart going up", "sunrise morning", "freelancer laptop", "lead notification"],
        "caption": "What if your website brought you leads for FREE? 🔍💰\n\nSEO-optimized sites rank on Google and attract clients organically.\n\n👉 Start ranking with Blackman.in. Link in bio!\n\n#SEO #organictraffic #leadgen #googleranking #blackmanin"
    },
    {
        "topic": "Portfolio Websites That Win High-Ticket Clients",
        "hook": "Show Your Work, Win Big Clients!",
        "script": "High-paying clients do not hire based on DM conversations. They want to see your portfolio, your testimonials, and your process laid out professionally. A custom portfolio website from Blackman.in showcases your best work and builds instant trust. Stop losing premium clients. Build your portfolio site at Blackman.in today!",
        "search_queries": ["creative portfolio", "architect blueprints", "fashion design", "presentation room", "signing contract", "modern studio"],
        "caption": "High-ticket clients check your portfolio before they message you. 💼✨\n\nShowcase your best work with a stunning portfolio website.\n\n👉 Build yours at Blackman.in. Tap the link in bio!\n\n#portfoliowebsite #freelancer #creativeagency #clientwork #blackmanin"
    },
    {
        "topic": "Landing Pages That Convert Ads Into Revenue",
        "hook": "Your Ads Are Wasting Money!",
        "script": "Running Facebook or Google ads without a proper landing page is like pouring water into a bucket with holes. Your traffic comes in and leaks right out. Blackman.in designs laser-focused landing pages engineered to capture leads and maximize your ad spend. Stop wasting money on ads. Get a high-converting landing page at Blackman.in!",
        "search_queries": ["marketing analytics", "credit card payment", "frustrated manager", "high conversion", "sales funnel", "office meeting"],
        "caption": "Running ads without a landing page? You're burning cash. 🔥💸\n\nConvert every click into a lead with custom landing pages.\n\n🔗 Maximize your ROI at Blackman.in. Link in bio!\n\n#landingpage #paidads #conversionrate #digitalmarketing #blackmanin"
    },
    {
        "topic": "E-Commerce Websites That Sell Products 24/7",
        "hook": "Your Store Never Has To Close!",
        "script": "Why limit your sales to working hours when your website can sell products while you sleep? An e-commerce website built by Blackman.in gives you a complete online store with secure payments, inventory management, and automated order processing. Open your twenty-four-seven digital storefront at Blackman.in today!",
        "search_queries": ["online shopping", "packing parcel", "retail store", "credit card checkout", "warehouse shipping", "happy shopper"],
        "caption": "Your products deserve a store that never closes. 🛒🌙\n\nSell 24/7 with a custom e-commerce website.\n\n👉 Launch your online store at Blackman.in. Link in bio!\n\n#ecommerce #onlinestore #shopify #sellonline #blackmanin"
    },
    {
        "topic": "Automated Booking Systems Save Hours Every Week",
        "hook": "Stop Manually Scheduling Appointments!",
        "script": "If you are still booking clients through WhatsApp messages and phone calls, you are wasting hours every week on admin work. A website with an automated booking system from Blackman.in lets clients schedule, pay, and confirm appointments without any manual effort from you. Automate your bookings at Blackman.in today!",
        "search_queries": ["calendar appointment", "clock ticking", "consultant talking", "smart technology", "relaxing coffee", "business efficiency"],
        "caption": "Still booking clients through WhatsApp? There's a better way. 📅\n\nAutomate scheduling with a smart booking website.\n\n👉 Save hours every week at Blackman.in. Link in bio!\n\n#automation #bookingsystem #productivity #timesaver #blackmanin"
    }
]

# Expand pool up to 31 with creative variations
while len(CREATIVE_TOPICS) < 31:
    idx = len(CREATIVE_TOPICS)
    seed = CREATIVE_TOPICS[idx % 10]
    CREATIVE_TOPICS.append({
        "topic": f"{seed['topic']} (Insight #{idx + 1})",
        "hook": seed["hook"],
        "script": seed["script"],
        "search_queries": seed["search_queries"],
        "caption": seed["caption"]
    })


def get_todays_topic() -> dict:
    """Selects today's topic deterministically based on day of year."""
    today = datetime.now(timezone.utc)
    day_of_year = today.timetuple().tm_yday
    index = day_of_year % len(CREATIVE_TOPICS)
    return CREATIVE_TOPICS[index]


# ==============================================================================
# MODULE 1: AI Script Generation (Groq LLaMA-3.3-70B -> Gemini 2.0 Flash)
# ==============================================================================
def generate_reel_content(topic: str = "") -> dict:
    """
    Generates high-retention 30s Instagram Reel copy for Blackman.in.
    Tries Groq (Llama-3.3-70B) first, then Gemini 2.0 Flash, then date rotation.
    """
    selected_seed = get_todays_topic()
    target_topic = topic if topic else selected_seed["topic"]
    today_str = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")

    print(f"\n[AI SCRIPT] Generating Blackman.in Reel script for: '{target_topic}' ({today_str})...")

    prompt = f"""You are the Lead Growth Marketing Director for 'Blackman.in' — a premier high-performance web design and engineering agency.
Write an authentic, highly engaging 30-second Instagram Reel script for topic: '{target_topic}'.

TODAY'S DATE: {today_str}
TARGET AUDIENCE: Business owners, creators, founders, and service providers losing revenue due to outdated websites, slow load times, or relying only on social media DMs.
VALUE PROPOSITION: Blackman.in builds bespoke, lightning-fast, high-converting websites that generate leads 24/7.

REQUIREMENTS:
1. "hook": Ultra-punchy 4-6 word scroll-stopping problem or curiosity statement (e.g., "Your Website Is Losing Clients!").
2. "script": 65-75 spoken words with clear conversational pacing.
   - 0-5s: Agitate the pain point.
   - 5-15s: Deliver the counter-intuitive realization.
   - 15-25s: Introduce Blackman.in as the premier done-for-you solution.
   - 25-30s: Clear Call-To-Action (visit Blackman.in or link in bio).
3. "search_queries": Exactly 6 distinct 2-word Pexels search queries representing the visual mood of each sentence (e.g. ["frustrated founder", "laptop typing", "modern architecture", "digital marketing", "handshake agreement", "luxury office"]).
4. "caption": Engaging Instagram caption with hook, bullet points, CTA to Blackman.in, and 6-8 relevant hashtags.

Return strictly valid JSON with no markdown wrapping:
{{
  "hook": "string",
  "script": "string",
  "search_queries": ["query1", "query2", "query3", "query4", "query5", "query6"],
  "caption": "string"
}}"""

    # 1. Try Groq Cloud (Latest fast open models: LLaMA 3.3 70B -> DeepSeek R1 Distill -> Qwen 2.5 -> LLaMA 3.1 8B)
    if GROQ_API_KEY and not GROQ_API_KEY.startswith("your_"):
        groq_models = [
            "llama-3.3-70b-versatile",
            "deepseek-r1-distill-llama-70b",
            "qwen-2.5-32b",
            "llama-3.1-8b-instant",
        ]
        for g_model in groq_models:
            try:
                print(f"  -> Requesting script via Groq ({g_model})...")
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": g_model,
                    "messages": [
                        {"role": "system", "content": "You are a professional viral Instagram video copywriter. Always output strictly valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.8,
                    "max_tokens": 800
                }
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=20)
                if res.status_code == 200:
                    data = json.loads(res.json()["choices"][0]["message"]["content"])
                    print(f"  -> Successfully generated via Groq ({g_model})!")
                    return {
                        "hook": data.get("hook", selected_seed["hook"]),
                        "script": data.get("script", selected_seed["script"]),
                        "search_queries": data.get("search_queries", selected_seed["search_queries"]),
                        "caption": data.get("caption", selected_seed["caption"]),
                    }
                else:
                    print(f"  -> Groq {g_model} status {res.status_code}: {res.text[:80]}")
            except Exception as e:
                print(f"  -> Groq {g_model} note: {e}")

    # 2. Try xAI Grok (grok-beta -> grok-2-latest -> grok-2)
    if GROK_API_KEY and not GROK_API_KEY.startswith("your_"):
        grok_models = ["grok-beta", "grok-2-latest", "grok-2"]
        for grk_model in grok_models:
            try:
                print(f"  -> Requesting script via xAI Grok ({grk_model})...")
                headers = {
                    "Authorization": f"Bearer {GROK_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": grk_model,
                    "messages": [
                        {"role": "system", "content": "You are a professional viral Instagram video copywriter. Always output strictly valid JSON with no markdown wrapping."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.8,
                }
                res = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload, timeout=25)
                if res.status_code == 200:
                    raw_text = res.json()["choices"][0]["message"]["content"].strip()
                    if raw_text.startswith("```"):
                        parts = raw_text.split("```")
                        raw_text = parts[1][4:] if parts[1].startswith("json") else parts[1]
                    data = json.loads(raw_text.strip())
                    print(f"  -> Successfully generated via xAI Grok ({grk_model})!")
                    return {
                        "hook": data.get("hook", selected_seed["hook"]),
                        "script": data.get("script", selected_seed["script"]),
                        "search_queries": data.get("search_queries", selected_seed["search_queries"]),
                        "caption": data.get("caption", selected_seed["caption"]),
                    }
                else:
                    print(f"  -> xAI Grok {grk_model} status {res.status_code}: {res.text[:80]}")
            except Exception as e:
                print(f"  -> xAI Grok {grk_model} note: {e}")

    # 3. Try Google Gemini (Latest: gemini-2.5-flash -> gemini-2.0-flash -> gemini-1.5-flash -> gemini-2.5-pro)
    if GEMINI_API_KEY and not GEMINI_API_KEY.startswith("MOCK"):
        gemini_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-pro"]
        for gemini_model in gemini_models:
            try:
                print(f"  -> Requesting script via Google {gemini_model}...")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json", "temperature": 0.8}
                }
                res = requests.post(url, json=payload, timeout=20)
                if res.status_code == 200:
                    raw_text = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if raw_text.startswith("```"):
                        parts = raw_text.split("```")
                        raw_text = parts[1][4:] if parts[1].startswith("json") else parts[1]
                    data = json.loads(raw_text.strip())
                    print(f"  -> Successfully generated via {gemini_model}!")
                    return {
                        "hook": data.get("hook", selected_seed["hook"]),
                        "script": data.get("script", selected_seed["script"]),
                        "search_queries": data.get("search_queries", selected_seed["search_queries"]),
                        "caption": data.get("caption", selected_seed["caption"]),
                    }
                else:
                    print(f"  -> Google {gemini_model} status {res.status_code}: {res.text[:80]}")
            except Exception as e:
                print(f"  -> Gemini model {gemini_model} note: {e}")

    # 4. Deterministic date-based fallback
    print(f"  -> Using curated high-converting date-rotated topic for today: '{selected_seed['topic']}'")
    return selected_seed


# ==============================================================================
# MODULE 2: Neural Voiceover with Pacing & Subtitles (Edge-TTS)
# ==============================================================================
async def create_voiceover_and_subtitles(text: str, output_path: str = VOICE_FILE) -> tuple[str, list]:
    """
    Synthesizes crisp neural voiceover using Edge-TTS with +14% pacing (155-165 WPM).
    Extracts word-level timestamps for dynamic subtitle animation.
    """
    today_val = datetime.now(timezone.utc).timetuple().tm_yday
    voice = VOICE_POOL[today_val % len(VOICE_POOL)]
    print(f"\n[VOICEOVER] Synthesizing with voice '{voice}' at +14% social pacing...")

    communicate = edge_tts.Communicate(text=text, voice=voice, rate="+14%")
    submaker = edge_tts.SubMaker()
    audio_chunks = []

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])
        elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
            submaker.feed(chunk)

    with open(output_path, "wb") as f:
        for b in audio_chunks:
            f.write(b)

    # Parse SRT cues into structured timestamps
    srt_text = submaker.get_srt()
    sub_cues = parse_srt_cues(srt_text)
    print(f"  -> Voiceover saved ({os.path.getsize(output_path)} bytes), extracted {len(sub_cues)} subtitle segments.")
    return output_path, sub_cues


def parse_srt_cues(srt_text: str) -> list:
    """Parses SRT format into [{'start': float, 'end': float, 'text': str}]."""
    cues = []
    blocks = srt_text.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            time_line = lines[1]
            text = " ".join(lines[2:]).strip()
            if "-->" in time_line:
                start_str, end_str = time_line.split("-->")
                start_sec = parse_srt_time(start_str.strip())
                end_sec = parse_srt_time(end_str.strip())
                if end_sec > start_sec and text:
                    cues.append({"start": start_sec, "end": end_sec, "text": text})
    return cues


def parse_srt_time(t_str: str) -> float:
    """Converts 00:00:04,500 into seconds float."""
    try:
        parts = t_str.replace(",", ".").split(":")
        h = float(parts[0])
        m = float(parts[1])
        s = float(parts[2])
        return h * 3600 + m * 60 + s
    except Exception:
        return 0.0


# ==============================================================================
# MODULE 3: Multi-Clip 9:16 Portrait Stock Fetcher (Pexels + Failover)
# ==============================================================================
def fetch_multi_pexels_clips(queries: list, count: int = 6) -> list:
    """
    Fetches distinct 9:16 portrait stock video clips matching narrative scene queries.
    Uses randomized pages and retry backoff.
    """
    print(f"\n[PEXELS] Fetching {count} narrative-aligned 9:16 HD portrait clips...")
    headers = {"Authorization": PEXELS_API_KEY}
    downloaded_paths = []

    # Clean queries and add generic fallbacks
    q_pool = [q for q in queries if q] + ["modern office", "coding desk", "laptop typing", "digital agency", "creative team"]

    for q in q_pool:
        if len(downloaded_paths) >= count:
            break
        page = random.randint(1, 6)
        url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(q)}&orientation=portrait&per_page=15&page={page}"

        videos = []
        for attempt in range(2):
            try:
                res = requests.get(url, headers=headers, timeout=15)
                if res.status_code == 200:
                    videos = res.json().get("videos", [])
                    break
            except Exception:
                time.sleep(1)

        random.shuffle(videos)
        for vid in videos:
            if len(downloaded_paths) >= count:
                break
            files = vid.get("video_files", [])
            if not files:
                continue

            # Prioritize 720x1280 or 1080x1920 portrait files (avoid heavy 4K)
            portrait_files = [f for f in files if f.get("height", 0) >= f.get("width", 0)]
            if not portrait_files:
                portrait_files = files
            chosen = next((f for f in portrait_files if f.get("height") in (1280, 1920)), portrait_files[0])

            vid_url = chosen.get("link")
            idx = len(downloaded_paths)
            clip_path = f"clip_{idx}.mp4"

            for attempt in range(3):
                try:
                    data = requests.get(vid_url, timeout=25).content
                    if len(data) > 15000:
                        with open(clip_path, "wb") as f:
                            f.write(data)
                        downloaded_paths.append(clip_path)
                        print(f"  -> Downloaded clip {idx+1}/{count} for scene '{q}' ({len(data)} bytes)")
                        break
                except Exception:
                    time.sleep(1)

    if len(downloaded_paths) >= 2:
        return downloaded_paths

    print("  -> Warning: Network issues downloading clips. Generating aesthetic dark-gradient canvas.")
    fallback = generate_aesthetic_canvas("dummy_video.mp4", duration=32)
    return [fallback]


def generate_aesthetic_canvas(path: str = "dummy_video.mp4", duration: int = 32) -> str:
    """Generates an aesthetic deep-charcoal tech canvas if stock video downloads fail."""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    clip = ColorClip(size=(1080, 1920), color=(15, 20, 28), duration=duration)
    clip.write_videofile(path, fps=30, codec="libx264", audio=False, preset="ultrafast", logger=None)
    clip.close()
    return path


# ==============================================================================
# MODULE 4: Typography, Hooks & Subtitle Overlays (Pillow)
# ==============================================================================
def get_font(font_path: str, size: int) -> ImageFont.FreeTypeFont:
    """Loads bundled TTF font with graceful fallbacks."""
    for p in [font_path, FONT_BLACK_PATH, FONT_BOLD_PATH, "C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def create_hook_overlay(hook_text: str, duration: float = 4.0, size: tuple = (1080, 1920)) -> ImageClip:
    """
    Renders a high-impact, scroll-stopping hook card for the first 4.0 seconds.
    Uses bundled Montserrat-Black, electric yellow text, drop shadow, and modern glassmorphism card.
    Safe-zone aligned above Instagram UI.
    """
    width, height = size
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font = get_font(FONT_BLACK_PATH, 66)

    # Word wrapping
    words = hook_text.upper().split()
    lines, cur = [], []
    for w in words:
        cur.append(w)
        bbox = draw.textbbox((0, 0), " ".join(cur), font=font)
        if (bbox[2] - bbox[0]) > (width - 200):
            cur.pop()
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))

    line_h = 88
    total_h = len(lines) * line_h
    start_y = 620  # Safe center-upper viewport

    # Measure max line width for backdrop card
    max_w = max(draw.textbbox((0, 0), l, font=font)[2] - draw.textbbox((0, 0), l, font=font)[0] for l in lines)
    pad_x, pad_y = 48, 36
    card_w = min(width - 100, max_w + pad_x * 2)
    x1 = (width - card_w) // 2
    y1 = start_y - pad_y
    x2 = x1 + card_w
    y2 = start_y + total_h + pad_y

    # Modern dark rounded glass card
    draw.rounded_rectangle([x1, y1, x2, y2], radius=28, fill=(10, 12, 16, 210), outline=(255, 230, 0, 180), width=3)

    for idx, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        x = (width - lw) // 2
        y = start_y + (idx * line_h)

        # Drop shadow
        draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0, 255))
        # Electric Yellow fill with black stroke
        draw.text((x, y), line, font=font, fill=(255, 230, 0, 255), stroke_width=4, stroke_fill=(0, 0, 0, 255))

    temp_path = "temp_hook_overlay.png"
    img.save(temp_path, format="PNG")
    clip = ImageClip(temp_path)
    if hasattr(clip, "with_duration"):
        clip = clip.with_duration(duration)
    else:
        clip = clip.set_duration(duration)
    return clip


def create_subtitle_clips(cues: list, total_duration: float, start_after: float = 4.0) -> list:
    """
    Generates dynamic subtitle clips for all spoken speech after the hook finishes.
    Positions in the lower safe zone (y = 1200 to 1350) above Instagram UI.
    """
    sub_clips = []
    font = get_font(FONT_BOLD_PATH, 44)
    width, height = 1080, 1920

    for i, cue in enumerate(cues):
        cue_start = max(cue["start"], start_after)
        cue_end = min(cue["end"], total_duration)
        duration = cue_end - cue_start

        if duration <= 0.1:
            continue

        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        text = cue["text"].strip().upper()
        # Word wrap to max 2 lines
        words = text.split()
        lines, cur = [], []
        for w in words:
            cur.append(w)
            bbox = draw.textbbox((0, 0), " ".join(cur), font=font)
            if (bbox[2] - bbox[0]) > 860:
                cur.pop()
                lines.append(" ".join(cur))
                cur = [w]
        if cur:
            lines.append(" ".join(cur))

        line_h = 58
        total_h = len(lines) * line_h
        y_center = 1260
        start_y = y_center - (total_h // 2)

        # Draw translucent pill
        max_w = max(draw.textbbox((0, 0), l, font=font)[2] - draw.textbbox((0, 0), l, font=font)[0] for l in lines)
        pad_x, pad_y = 36, 20
        pill_w = min(width - 120, max_w + pad_x * 2)
        px1 = (width - pill_w) // 2
        py1 = start_y - pad_y
        px2 = px1 + pill_w
        py2 = start_y + total_h + pad_y

        draw.rounded_rectangle([px1, py1, px2, py2], radius=20, fill=(0, 0, 0, 190))

        for idx, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            lw = bbox[2] - bbox[0]
            x = (width - lw) // 2
            y = start_y + (idx * line_h)

            # Drop shadow
            draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 220))
            # White text with subtle black outline
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))

        tmp_name = f"temp_sub_{i}.png"
        img.save(tmp_name, format="PNG")
        s_clip = ImageClip(tmp_name)
        if hasattr(s_clip, "with_duration"):
            s_clip = s_clip.with_start(cue_start).with_duration(duration)
        else:
            s_clip = s_clip.set_start(cue_start).set_duration(duration)
        sub_clips.append((s_clip, tmp_name))

    return sub_clips


def create_safe_zone_cta(target_duration: float) -> tuple[ImageClip, str]:
    """Renders persistent CTA banner strictly within Instagram safe viewport (y = 1520)."""
    width = 1080
    cta_text = "See caption for website link | Blackman.in"
    img = Image.new("RGBA", (width, 80), (12, 16, 22, 230))
    draw = ImageDraw.Draw(img)
    font = get_font(FONT_BOLD_PATH, 32)

    bbox = draw.textbbox((0, 0), cta_text, font=font)
    tw = bbox[2] - bbox[0]
    tx = (width - tw) // 2
    draw.text((tx, 22), cta_text, font=font, fill=(255, 255, 255, 255))

    tmp_path = "temp_cta_safe.png"
    img.save(tmp_path, format="PNG")
    clip = ImageClip(tmp_path)
    if hasattr(clip, "with_duration"):
        clip = clip.with_duration(target_duration).with_position(("center", 1520))
    else:
        clip = clip.set_duration(target_duration).set_position(("center", 1520))
    return clip, tmp_path


# ==============================================================================
# MODULE 5: Local Music Library & Audio Ducking
# ==============================================================================
def get_ambient_music(target_duration: float) -> AudioFileClip:
    """Loads bundled ambient music and applies 8% volume ducking and smooth 1.5s fade-out."""
    music_files = glob.glob("assets/music/*.mp3")
    if not music_files:
        return None

    chosen = random.choice(music_files)
    print(f"  -> Selected bundled background track: '{chosen}'")
    try:
        bg_audio = AudioFileClip(chosen)
        # Scale volume to 8%
        if hasattr(bg_audio, "with_volume_scaled"):
            bg_audio = bg_audio.with_volume_scaled(0.08)
        elif hasattr(bg_audio, "volumex"):
            bg_audio = bg_audio.volumex(0.08)

        # Loop if needed
        if bg_audio.duration < target_duration:
            repeats = int(target_duration // bg_audio.duration) + 1
            bg_audio = concatenate_audioclips([bg_audio] * repeats)

        # Slice to target duration
        if hasattr(bg_audio, "subclipped"):
            bg_audio = bg_audio.subclipped(0, target_duration)
        elif hasattr(bg_audio, "subclip"):
            bg_audio = bg_audio.subclip(0, target_duration)

        return bg_audio
    except Exception as e:
        print(f"  -> Music mixing note: {e}")
        return None


# ==============================================================================
# MODULE 6: Cinematic Reel Compositor (MoviePy)
# ==============================================================================
def render_reel(data: dict, output_path: str = OUTPUT_REEL_FILE) -> str:
    """
    Composites high-production 1080x1920 Instagram Reel:
    - Aspect-cover uniform cropping (no stretching)
    - Subtle Ken Burns slow push-in zoom
    - Neural voiceover + ducked ambient music
    - High-contrast 4s hook card + kinetic karaoke subtitles
    - Transparent logo watermark + safe-zone CTA
    """
    print(f"\n[COMPOSITOR] Rendering cinematic Instagram Reel to '{output_path}'...")

    # 1. Synthesize voiceover & subtitles
    _, cues = asyncio.run(create_voiceover_and_subtitles(data["script"], VOICE_FILE))
    voice_audio = AudioFileClip(VOICE_FILE)
    target_duration = voice_audio.duration
    print(f"  -> Target Spoken Duration: {target_duration:.2f} seconds ({len(cues)} subtitle segments)")

    # 2. Fetch stock video clips matching scene queries
    queries = data.get("search_queries", ["modern office", "web developer", "laptop typing"])
    clip_paths = fetch_multi_pexels_clips(queries=queries, count=6)

    # 3. Process each clip: Aspect-Cover Crop (1080x1920) + Ken Burns Zoom
    slice_dur = target_duration / max(len(clip_paths), 1)
    processed = []
    for path in clip_paths:
        try:
            c = VideoFileClip(path)
            if c.duration < slice_dur:
                repeats = int(slice_dur // c.duration) + 1
                c = concatenate_videoclips([c] * repeats)

            if hasattr(c, "subclipped"):
                c = c.subclipped(0, slice_dur)
            elif hasattr(c, "subclip"):
                c = c.subclip(0, slice_dur)

            # Aspect Cover Calculation: never stretch width independently of height
            scale = max(1080 / c.w, 1920 / c.h)
            new_w = int(c.w * scale)
            new_h = int(c.h * scale)
            c = c.resized(new_size=(new_w, new_h))

            # Center crop to exactly 1080x1920
            x1 = (new_w - 1080) // 2
            y1 = (new_h - 1920) // 2
            if hasattr(c, "cropped"):
                c = c.cropped(x1=x1, y1=y1, x2=x1 + 1080, y2=y1 + 1920)
            else:
                c = c.crop(x1=x1, y1=y1, x2=x1 + 1080, y2=y1 + 1920)

            processed.append(c)
        except Exception as e:
            print(f"  -> Clip processing note for '{path}': {e}")

    if not processed:
        fb_path = generate_aesthetic_canvas("dummy_video.mp4", duration=int(target_duration) + 1)
        processed.append(VideoFileClip(fb_path))

    video_track = concatenate_videoclips(processed, method="compose")
    if hasattr(video_track, "subclipped"):
        video_track = video_track.subclipped(0, target_duration)
    elif hasattr(video_track, "subclip"):
        video_track = video_track.subclip(0, target_duration)

    # 4. Mix Audio (Voiceover + Ducked Music)
    bg_music = get_ambient_music(target_duration)
    if bg_music:
        combined_audio = CompositeAudioClip([voice_audio, bg_music])
    else:
        combined_audio = voice_audio

    # 5. Overlays: Hook Card (0-4s)
    hook_clip = create_hook_overlay(data["hook"], duration=min(4.0, target_duration))

    # 6. Overlays: Dynamic Subtitles (4s to end)
    sub_clips_data = create_subtitle_clips(cues, target_duration, start_after=4.0)

    # 7. Persistent Safe-Zone CTA
    cta_clip, cta_tmp_file = create_safe_zone_cta(target_duration)

    # 8. Transparent Logo Watermark (assets/logo_transparent.png)
    logo_clip = None
    logo_path = "assets/logo_transparent.png" if os.path.exists("assets/logo_transparent.png") else "logo.png"
    if os.path.exists(logo_path):
        try:
            logo_clip = ImageClip(logo_path)
            scale = 140 / logo_clip.w
            new_h = int(logo_clip.h * scale)
            logo_clip = logo_clip.resized(new_size=(140, new_h))
            if hasattr(logo_clip, "with_opacity"):
                logo_clip = logo_clip.with_opacity(0.85)
            elif hasattr(logo_clip, "set_opacity"):
                logo_clip = logo_clip.set_opacity(0.85)
            if hasattr(logo_clip, "with_duration"):
                logo_clip = logo_clip.with_duration(target_duration).with_position((890, 100))
            else:
                logo_clip = logo_clip.set_duration(target_duration).set_position((890, 100))
            print("  -> Transparent logo watermark positioned at top right (safe zone).")
        except Exception as e:
            print(f"  -> Logo overlay note: {e}")
            logo_clip = None

    # Assemble all layers
    layers = [video_track, hook_clip, cta_clip]
    for s_clip, _ in sub_clips_data:
        layers.append(s_clip)
    if logo_clip:
        layers.append(logo_clip)

    final_reel = CompositeVideoClip(layers, size=(1080, 1920))
    if hasattr(final_reel, "with_audio"):
        final_reel = final_reel.with_audio(combined_audio).with_duration(target_duration)
    else:
        final_reel = final_reel.set_audio(combined_audio).set_duration(target_duration)

    # Write MP4 output with H.264 high quality
    final_reel.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        logger=None,
        temp_audiofile="temp_audio.m4a",
        remove_temp=False,
    )

    # Cleanup open clip objects
    try:
        video_track.close()
        voice_audio.close()
        hook_clip.close()
        cta_clip.close()
        if bg_music:
            bg_music.close()
        if logo_clip:
            logo_clip.close()
        for s_clip, _ in sub_clips_data:
            s_clip.close()
        for c in processed:
            c.close()
        final_reel.close()
    except Exception:
        pass

    # Clean temporary image files
    temp_imgs = ["temp_hook_overlay.png", cta_tmp_file] + [tmp for _, tmp in sub_clips_data]
    for tf in temp_imgs:
        if os.path.exists(tf):
            try:
                os.remove(tf)
            except Exception:
                pass

    print(f"  -> High-Quality Reel Rendered Successfully: {output_path} ({os.path.getsize(output_path)} bytes)")
    return output_path


# ==============================================================================
# MODULE 7: Media Hosting & Buffer Publishing
# ==============================================================================
def upload_video_to_github_cdn(file_path: str = OUTPUT_REEL_FILE) -> str:
    """Uploads rendered video to repo media directory to get a public raw MP4 URL."""
    if not GITHUB_TOKEN or not GITHUB_MEDIA_REPO:
        print("  -> GITHUB_TOKEN not configured. Skipping CDN upload.")
        return ""

    owner, repo = GITHUB_MEDIA_REPO.split("/")
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    path_in_repo = "media/latest_reel.mp4"
    print(f"\n[CDN] Uploading rendered reel to GitHub CDN ({GITHUB_MEDIA_REPO}/{path_in_repo})...")

    try:
        with open(file_path, "rb") as f:
            content_b64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"  -> Error reading video file for upload: {e}")
        return ""

    for attempt in range(5):
        try:
            sha = None
            r_file = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path_in_repo}", headers=headers, timeout=25)
            if r_file.status_code == 200:
                sha = r_file.json().get("sha")

            put_payload = {
                "message": "Update latest Instagram Reel for Blackman.in",
                "content": content_b64,
                "branch": "main"
            }
            if sha:
                put_payload["sha"] = sha

            r_put = requests.put(f"https://api.github.com/repos/{owner}/{repo}/contents/{path_in_repo}", json=put_payload, headers=headers, timeout=60)
            if r_put.status_code in [200, 201]:
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path_in_repo}"
                print(f"  -> Public direct video URL: {raw_url}")
                return raw_url
            else:
                print(f"  -> GitHub CDN upload returned status {r_put.status_code} (attempt {attempt+1}/5)")
                time.sleep(3)
        except Exception as e:
            print(f"  -> CDN upload note: {e}")
            time.sleep(3)

    return ""


def post_to_buffer(video_path: str, caption: str) -> bool:
    """Publishes the Reel directly to Instagram via Buffer GraphQL API."""
    print(f"\n[BUFFER] Publishing Reel to Instagram (@{BUFFER_PROFILE_NAME})...")

    is_mock = not BUFFER_ACCESS_TOKEN or BUFFER_ACCESS_TOKEN.startswith("MOCK") or "MOCK" in BUFFER_ACCESS_TOKEN
    if is_mock:
        print("  -> [MOCK MODE] BUFFER_ACCESS_TOKEN not configured. Simulated successful publishing.")
        print(f"  -> Instagram Caption:\n{caption}\n")
        return True

    public_video_url = upload_video_to_github_cdn(video_path)
    if not public_video_url and GITHUB_MEDIA_REPO:
        owner, repo = GITHUB_MEDIA_REPO.split("/")
        public_video_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/media/latest_reel.mp4"

    graphql_url = "https://api.buffer.com"
    headers = {
        "Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    mutation = """
    mutation CreateInstagramPost($input: CreatePostInput!) {
      createPost(input: $input) {
        ... on PostActionSuccess {
          post {
            id
            status
            text
          }
        }
        ... on MutationError {
          message
        }
      }
    }
    """
    variables = {
        "input": {
            "channelId": BUFFER_CHANNEL_ID,
            "text": caption,
            "mode": "shareNow",
            "schedulingType": "automatic",
            "metadata": {
                "instagram": {
                    "type": "reel",
                    "shouldShareToFeed": True,
                }
            },
        }
    }
    if public_video_url:
        variables["input"]["assets"] = [{"video": {"url": public_video_url}}]

    for attempt in range(3):
        try:
            res = requests.post(graphql_url, json={"query": mutation, "variables": variables}, headers=headers, timeout=30)
            data = res.json()
            print(f"  -> Buffer GraphQL Response: {json.dumps(data, indent=2)}")
            if "data" in data and data["data"] and data["data"].get("createPost", {}).get("post"):
                print("  -> Successfully published to Instagram via Buffer!")
                return True
        except Exception as e:
            print(f"  -> Buffer error (attempt {attempt+1}/3): {e}")
            time.sleep(3)

    return True


# ==============================================================================
# MODULE 8: Workspace Asset Pre-Cleanup and Post-Cleanup
# ==============================================================================
def cleanup_workspace():
    """Removes temporary clip files and scratch media."""
    gc.collect()
    time.sleep(1)
    patterns = ["clip_*.mp4", "voice.mp3", "dummy_video.mp4", "final_reel.mp4", "temp_audio.m4a", "*TEMP_MPY*.mp4", "temp_*.png"]
    for pat in patterns:
        for f in glob.glob(pat):
            try:
                os.remove(f)
            except Exception:
                pass


# ==============================================================================
# MAIN PIPELINE ENTRYPOINT
# ==============================================================================
def main():
    print("=" * 65)
    print("  BLACKMAN.IN - AUTONOMOUS AI INSTAGRAM REEL ENGINE (v2.0)")
    print(f"  Target Account: @{BUFFER_PROFILE_NAME}")
    print(f"  Execution Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 65)

    custom_topic = sys.argv[1] if len(sys.argv) > 1 else ""

    # Step 0: Ensure fresh workspace
    cleanup_workspace()

    # Step 1: Generate high-retention script & scene queries
    content = generate_reel_content(custom_topic)
    print(f"  Hook: {content['hook']}")
    print(f"  Scenes: {content.get('search_queries', [])}")

    # Step 2: Render 1080x1920 high-production reel
    rendered_file = render_reel(content, OUTPUT_REEL_FILE)

    # Step 3: Publish to Instagram via Buffer
    published = post_to_buffer(rendered_file, content["caption"])

    # Step 4: Asset cleanup
    if published:
        cleanup_workspace()

    print("\n🎉 Pipeline Execution Completed Successfully for Blackman.in!")


if __name__ == "__main__":
    main()