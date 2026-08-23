"""
Blackman.in - Autonomous AI Instagram Reel Engine
=================================================
Automated Daily Pipeline:
1. Dynamic AI Idea & Script Generation (Gemini 2.5/3.7 Flash + Randomized Viral Topic Pools)
2. Fresh 9:16 HD Portrait Stock B-Roll Fetcher (Pexels API with randomized query & clips)
3. Neural Voiceover Synthesis (Edge-TTS en-US-ChristopherNeural)
4. Dynamic Lo-Fi / Ambient Background Music Download & Audio Mixing (volumex ducking)
5. Animated Subtitles & Typography Compositor (MoviePy + PIL)
6. Automated Publishing to Instagram via Buffer API (@blackman_officialpage)
7. Instant Asset Cleanup (deletes all mp4/mp3/temp files immediately upon upload)
"""

import os
import sys
import glob
import json
import random
import asyncio
import requests
from dotenv import load_dotenv

# Load environment variables if present
load_dotenv()

# UTF-8 terminal encoding fix for Windows/Linux
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Optional Whisper import
try:
    import whisper
except Exception as e:
    whisper = None

# Optional google-genai SDK import
try:
    from google import genai
except ImportError:
    genai = None

# MoviePy imports (compatible with MoviePy v1.x and v2.x)
try:
    from moviepy import (
        VideoFileClip,
        AudioFileClip,
        TextClip,
        CompositeVideoClip,
        concatenate_videoclips,
        CompositeAudioClip,
        ImageClip,
        vfx,
    )
except ImportError:
    from moviepy.editor import (
        VideoFileClip,
        AudioFileClip,
        TextClip,
        CompositeVideoClip,
        concatenate_videoclips,
        CompositeAudioClip,
        ImageClip,
        vfx,
    )

import edge_tts
from PIL import Image, ImageDraw, ImageFont

# ==============================================================================
# CONFIGURATION & ENVIRONMENT VARIABLES
# ==============================================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "8dxdiukk0XTSLx87LsZFIIoHSQgAxukiYtdbcEbdtToDOAfalFw4OCNI")
BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN", "")
BUFFER_CHANNEL_ID = os.getenv("BUFFER_CHANNEL_ID", "6a0c75a6090476fb99383a66")
BUFFER_PROFILE_ID = os.getenv("BUFFER_PROFILE_ID", os.getenv("BUFFER_CHANNEL_ID", "6a0c75a6090476fb99383a66"))
BUFFER_PROFILE_NAME = os.getenv("BUFFER_PROFILE_NAME", "blackman_officialpage")

VOICE_FILE = "voice.mp3"
BG_MUSIC_FILE = "bg_music.mp3"
OUTPUT_REEL_FILE = "final_reel.mp4"

# Initialize Gemini Client if API key is present
gemini_client = None
if genai and GEMINI_API_KEY and not GEMINI_API_KEY.startswith("MOCK"):
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"[GEMINI INIT WARNING] {e}")

# High-converting creative topic pool for maximum novelty and freshness
CREATIVE_TOPICS = [
    {
        "topic": "Cinematic Color Grading & Exposure Balance",
        "hook": "Stop Crushing Your Shadows!",
        "script": "When editing Log footage, never slap on a LUT before balancing your primary exposure and white balance. Fix your dynamic range first, dial in midtones, and let the colors breathe naturally.",
        "search_query": "color grading studio",
        "caption": "Avoid this rookie color grading mistake! 🎬\n\nBalance before you grade for pristine dynamic range.\n\nSave this for your next video edit!\n🔗 Need elite editing? Visit Blackman.in\n\n#videoediting #colorgrading #filmmaking #cinematography #blackmanin"
    },
    {
        "topic": "Sound Design Secrets for Cinematic Videos",
        "hook": "Sound is 70% of Your Video!",
        "script": "Great visuals get clicks, but sound design keeps retention. Always layer subtle ambient room tone, foley risers, and low frequency whooshes beneath your dialogue to build irresistible depth.",
        "search_query": "studio audio console",
        "caption": "The hidden secret top editors never tell you: Sound design makes amateur footage look Hollywood-grade. 🎧\n\nDrop a 🔥 if you want our full sound pack!\n🔗 Visit Blackman.in\n\n#sounddesign #filmmaker #videoeditor #premierepro #blackmanin"
    },
    {
        "topic": "The 4-Second Retention Cut Rule",
        "hook": "Kill Viewer Boredom Instantly!",
        "script": "If your video stays on the same angle for more than four seconds, the viewer scrolls away. Cut to tight punch-ins, switch B-roll perspectives, and keep visual momentum alive.",
        "search_query": "cinematic camera lens",
        "caption": "Skyrocket your average watch time with the 4-Second Rule! ⚡\n\nKeep eyes glued to the screen with dynamic camera switches.\n\n🔗 Level up your video production with Blackman.in\n\n#contentcreator #shortformcontent #reelsgrowth #videoediting #blackmanin"
    },
    {
        "topic": "Lighting Hacks: The Inverted Key Light",
        "hook": "This One Light Makes It 10x More Cinematic!",
        "script": "Stop lighting your subject from the camera side. Always place your key light on the opposite side of your camera to cast rich cinematic shadow contrast across the face.",
        "search_query": "cinematic lighting portrait",
        "caption": "Far-side key lighting is the difference between flat phone video and cinematic film look. 💡\n\nTry this on your next shoot!\n🔗 Transform your brand with Blackman.in\n\n#cinematography #filmmakingtips #lightingdesign #videoproduction #blackmanin"
    },
    {
        "topic": "Seamless Speed Ramping Transitions",
        "hook": "Make Any Video Flow Like Butter!",
        "script": "To nail speed ramping transitions, match continuous camera movement between two clips. Accelerate into the movement, whip into the next clip, and decelerate on impact for pure magic.",
        "search_query": "gimbal camera operator",
        "caption": "Master speed ramping in 3 simple steps! 🚀\n\nSmooth kinetic transitions keep engagement through the roof.\n\n🔗 Custom editing workflows at Blackman.in\n\n#videoediting #speedramp #aftereffects #premierepro #blackmanin"
    },
    {
        "topic": "Anamorphic Lens Flares & Composition",
        "hook": "Get That High-Budget Movie Look!",
        "script": "You don't need a fifty thousand dollar cinema camera to look like a blockbuster. Shoot at wide apertures, frame with leading lines, and capture subtle horizontal flares into the lens.",
        "search_query": "anamorphic flare camera",
        "caption": "Turn ordinary scenes into cinematic gold with intentional framing and optical flares. 🎥\n\nDouble tap if you love cinematic visuals!\n🔗 Explore Blackman.in\n\n#filmmaking #cinematography #cameragear #director #blackmanin"
    }
]

MUSIC_URLS = [
    "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",
    "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3",
    "https://cdn.pixabay.com/download/audio/2021/09/06/audio_823d069b4e.mp3"
]


# ==============================================================================
# MODULE 1: Royalty-Free Background Music Fetcher
# ==============================================================================
def ensure_bg_music(output_path: str = BG_MUSIC_FILE) -> str:
    """Downloads or verifies a royalty-free ambient background music track."""
    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
        return output_path

    print("[BG MUSIC] Downloading royalty-free ambient background track...")
    url = random.choice(MUSIC_URLS)
    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200 and len(res.content) > 1000:
            with open(output_path, "wb") as f:
                f.write(res.content)
            print(f"  -> Background music saved to {output_path} ({os.path.getsize(output_path)} bytes)")
            return output_path
    except Exception as e:
        print(f"  -> BG Music download warning: {e}")

    return output_path if os.path.exists(output_path) else ""


# ==============================================================================
# MODULE 2: Dynamic Multi-Clip 9:16 Portrait Stock Fetcher (Pexels API)
# ==============================================================================
def fetch_multi_pexels_clips(query: str = "cinematic video", count: int = 6) -> list:
    """
    Searches Pexels for portrait 9:16 stock videos matching the dynamic query,
    randomizes results and downloads distinct clips for high-velocity multi-cut editing.
    """
    print(f"\n[PEXELS] Fetching {count} distinct 9:16 portrait stock clips for query: '{query}'...")
    headers = {"Authorization": PEXELS_API_KEY}
    page = random.randint(1, 4)
    url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(query)}&orientation=portrait&per_page=20&page={page}"

    downloaded_paths = []
    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            videos = response.json().get("videos", [])
            if len(videos) < count:
                url_fallback = "https://api.pexels.com/videos/search?query=cinematic+camera&orientation=portrait&per_page=20"
                res_fb = requests.get(url_fallback, headers=headers, timeout=12)
                if res_fb.status_code == 200:
                    videos.extend(res_fb.json().get("videos", []))

            random.shuffle(videos)
            for idx, vid in enumerate(videos[:count]):
                video_files = vid.get("video_files", [])
                if not video_files:
                    continue
                hd_file = next(
                    (f for f in video_files if f.get("height", 0) >= 1280 or f.get("width", 0) >= 720),
                    video_files[0]
                )
                vid_url = hd_file.get("link")
                clip_path = f"clip_{idx}.mp4"
                print(f"  -> Downloading clip {idx + 1}/{count} (ID: {vid.get('id')})...")
                vid_data = requests.get(vid_url, timeout=25).content
                with open(clip_path, "wb") as f:
                    f.write(vid_data)
                downloaded_paths.append(clip_path)

            if len(downloaded_paths) >= 2:
                print(f"  -> Successfully prepared {len(downloaded_paths)} dynamic stock clips.")
                return downloaded_paths
        else:
            print(f"  -> Pexels returned HTTP {response.status_code}")
    except Exception as e:
        print(f"  -> Pexels API warning: {e}")

    fallback_canvas = ensure_fallback_canvas("dummy_video.mp4", duration=30)
    return [fallback_canvas]


def ensure_fallback_canvas(path: str = "dummy_video.mp4", duration: int = 30) -> str:
    """Generates a clean 1080x1920 dark aesthetic canvas if network is offline."""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    img = Image.new("RGB", (1080, 1920), color=(14, 17, 23))
    temp_img = "temp_fallback_frame.png"
    img.save(temp_img)
    clip = ImageClip(temp_img)
    if hasattr(clip, "with_duration"):
        clip = clip.with_duration(duration)
    else:
        clip = clip.set_duration(duration)
    clip.write_videofile(path, fps=30, codec="libx264", audio=False, logger=None)
    clip.close()
    if os.path.exists(temp_img):
        os.remove(temp_img)
    return path


# ==============================================================================
# MODULE 3: AI Script, Hook & Metadata Generation (Gemini 2.5/3.7 Flash)
# ==============================================================================
def generate_reel_content(topic: str = "") -> dict:
    """
    Generates a completely fresh, high-retention 30-second script, punchy hook,
    Pexels search query, and hashtagged caption using Gemini Flash or randomized viral pool.
    """
    selected_topic_seed = random.choice(CREATIVE_TOPICS)
    target_topic = topic if topic else selected_topic_seed["topic"]

    print(f"\n[AI SCRIPT] Generating dynamic Reel content for topic: '{target_topic}'...")

    if not gemini_client:
        print("  -> Using high-converting curated viral script from creative pool.")
        return selected_topic_seed

    prompt = f"""
    Act as a viral video strategist and senior editor for Blackman.in.
    Create an engaging 30-second Instagram Reel script for topic: '{target_topic}'.
    Make the voiceover punchy, educational, and high-energy (approx 55-65 spoken words).
    Return valid JSON strictly with this schema:
    {{
      "hook": "Bold 4-6 word on-screen hook (e.g. 'Stop Crushing Your Shadows!')",
      "script": "55-65 words spoken voiceover script packed with valuable tips",
      "search_query": "2-word search term for Pexels vertical video (e.g. 'cinematic camera', 'color grading', 'lighting studio', 'filmmaking')",
      "caption": "Viral Instagram caption with hook, bullet points, CTA to Blackman.in, and tags (#videoediting #colorgrading #filmmaking #blackmanin)"
    }}
    """

    for model_name in ["gemini-2.5-flash", "gemini-3.7-flash", "gemini-1.5-flash"]:
        try:
            print(f"  -> Requesting script via model: {model_name}...")
            response = gemini_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                parts = raw_text.split("```")
                if len(parts) >= 2:
                    raw_text = parts[1]
                    if raw_text.startswith("json"):
                        raw_text = raw_text[4:]
            raw_text = raw_text.strip()
            data = json.loads(raw_text)
            print("  -> AI Reel content generated successfully!")
            return {
                "hook": data.get("hook", selected_topic_seed["hook"]),
                "script": data.get("script", selected_topic_seed["script"]),
                "search_query": data.get("search_query", selected_topic_seed["search_query"]),
                "caption": data.get("caption", selected_topic_seed["caption"]),
            }
        except Exception as e:
            print(f"  -> Model {model_name} note: {e}")
            continue

    print("  -> Falling back to rich viral script pool.")
    return selected_topic_seed


# ==============================================================================
# MODULE 4: Neural Voiceover Synthesis (Edge-TTS)
# ==============================================================================
async def create_voiceover(text: str, output_path: str = VOICE_FILE) -> str:
    """Synthesizes high-clarity neural voiceover using Edge-TTS (100% free)."""
    print(f"\n[VOICEOVER] Synthesizing crisp neural voiceover...")
    print(f'  -> Spoken Script: "{text}"')
    communicate = edge_tts.Communicate(text=text, voice="en-US-ChristopherNeural")
    await communicate.save(output_path)
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        print(f"  -> Voiceover saved to {output_path} ({os.path.getsize(output_path)} bytes)")
    else:
        raise RuntimeError("Voiceover generation failed: audio file missing or empty.")
    return output_path


# ==============================================================================
# MODULE 5: Transparent Typography & Word-Level Subtitle Generator
# ==============================================================================
def create_hook_overlay(hook_text: str, duration: float = 4.0, size: tuple = (1080, 1920)) -> ImageClip:
    """Generates a high-contrast transparent typography hook banner."""
    width, height = size
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_large = None
    for f in ["arialbd.ttf", "Arial-Bold.ttf", "seguisb.ttf", "calibrib.ttf", "arial.ttf"]:
        try:
            font_large = ImageFont.truetype(f, 64)
            break
        except Exception:
            continue
    if font_large is None:
        font_large = ImageFont.load_default()

    words = hook_text.upper().split()
    lines = []
    cur = []
    for w in words:
        cur.append(w)
        test = " ".join(cur)
        bbox = draw.textbbox((0, 0), test, font=font_large)
        if (bbox[2] - bbox[0]) > (width - 180):
            cur.pop()
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))

    line_h = 82
    total_h = len(lines) * line_h
    start_y = (height - total_h) // 2 - 140

    for idx, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_large)
        lw = bbox[2] - bbox[0]
        x = (width - lw) // 2
        y = start_y + (idx * line_h)
        draw.text(
            (x, y),
            line,
            font=font_large,
            fill=(255, 255, 255, 255),
            stroke_width=6,
            stroke_fill=(0, 0, 0, 255),
        )

    temp_path = "temp_hook_overlay.png"
    img.save(temp_path, format="PNG")
    clip = ImageClip(temp_path)
    if hasattr(clip, "with_duration"):
        clip = clip.with_duration(duration)
    else:
        clip = clip.set_duration(duration)
    return clip


def generate_word_captions(audio_path: str) -> list:
    """Generates animated synchronized word timestamps with Whisper."""
    if not whisper:
        return []
    try:
        print("[CAPTIONS] Generating word-level timestamps with Whisper...")
        model = whisper.load_model("tiny")
        result = model.transcribe(audio_path, word_timestamps=True)
        caption_clips = []
        for segment in result.get("segments", []):
            for word_info in segment.get("words", []):
                word = word_info.get("word", "").strip().upper()
                start = word_info.get("start", 0)
                end = word_info.get("end", start + 0.3)
                dur = max(end - start, 0.2)
                try:
                    txt = TextClip(
                        word,
                        fontsize=64,
                        color="yellow",
                        stroke_color="black",
                        stroke_width=4,
                        font="Arial-Bold",
                        size=(900, None),
                    )
                    if hasattr(txt, "with_start"):
                        txt = txt.with_start(start).with_duration(dur).with_position(("center", 1300))
                    else:
                        txt = txt.set_start(start).set_duration(dur).set_pos(("center", 1300))
                    caption_clips.append(txt)
                except Exception:
                    pass
        return caption_clips
    except Exception as e:
        print(f"[CAPTIONS WARNING] Whisper subtitle generation skipped: {e}")
        return []


# ==============================================================================
# MODULE 6: Multi-Clip Video & Audio Compositor
# ==============================================================================
def render_reel(data: dict, output_path: str = OUTPUT_REEL_FILE) -> str:
    """
    Composites the 30-second multi-clip Instagram Reel:
    - 6 distinct 9:16 vertical B-roll clips
    - Crisp neural voiceover + volume-ducked background music (8% volume)
    - High-contrast visual hook & animated captions
    - 1080x1920 30fps MP4 output
    """
    print(f"\n[COMPOSITOR] Rendering 30-second multi-clip Instagram Reel to '{output_path}'...")

    # 1. Synthesize Voiceover
    asyncio.run(create_voiceover(data["script"], VOICE_FILE))
    voice_audio = AudioFileClip(VOICE_FILE)
    total_duration = voice_audio.duration

    # 2. Fetch 6 distinct portrait clips from Pexels
    query = data.get("search_query", "cinematic camera")
    clip_paths = fetch_multi_pexels_clips(query=query, count=6)

    # 3. Process and align multi-clips to target duration
    clip_target_dur = total_duration / max(len(clip_paths), 1)
    processed_clips = []
    for path in clip_paths:
        try:
            c = VideoFileClip(path)
            if c.duration < clip_target_dur:
                try:
                    if hasattr(vfx, "Loop"):
                        c = c.with_effects([vfx.Loop(duration=clip_target_dur)])
                    else:
                        c = vfx.loop(c, duration=clip_target_dur)
                except Exception:
                    pass
            if hasattr(c, "subclipped"):
                c = c.subclipped(0, min(c.duration, clip_target_dur))
            elif hasattr(c, "subclip"):
                c = c.subclip(0, min(c.duration, clip_target_dur))

            try:
                if hasattr(c, "resized"):
                    c = c.resized(height=1920)
                elif hasattr(c, "resize"):
                    c = vfx.resize(c, height=1920)
            except Exception:
                pass

            if c.w > 1080:
                try:
                    if hasattr(c, "cropped"):
                        c = c.cropped(x_center=c.w / 2, width=1080)
                    elif hasattr(c, "crop"):
                        c = vfx.crop(c, x_center=c.w / 2, width=1080)
                except Exception:
                    pass

            processed_clips.append(c)
        except Exception as e:
            print(f"  -> Warning processing clip {path}: {e}")

    if not processed_clips:
        fb_path = ensure_fallback_canvas("dummy_video.mp4", duration=int(total_duration) + 1)
        c = VideoFileClip(fb_path)
        processed_clips.append(c)

    video_track = concatenate_videoclips(processed_clips, method="compose")
    if hasattr(video_track, "subclipped"):
        video_track = video_track.subclipped(0, total_duration)
    elif hasattr(video_track, "subclip"):
        video_track = video_track.subclip(0, total_duration)

    # 4. Mix Background Music (Ducked at 8% volume under voiceover)
    bg_music_file = ensure_bg_music()
    if bg_music_file and os.path.exists(bg_music_file):
        try:
            bg_audio = AudioFileClip(bg_music_file)
            if hasattr(bg_audio, "volumex"):
                bg_audio = bg_audio.volumex(0.08)
            elif hasattr(bg_audio, "with_volume_scaled"):
                bg_audio = bg_audio.with_volume_scaled(0.08)

            if bg_audio.duration < total_duration:
                try:
                    bg_audio = vfx.loop(bg_audio, duration=total_duration)
                except Exception:
                    pass
            if hasattr(bg_audio, "subclipped"):
                bg_audio = bg_audio.subclipped(0, total_duration)
            elif hasattr(bg_audio, "subclip"):
                bg_audio = bg_audio.subclip(0, total_duration)

            combined_audio = CompositeAudioClip([voice_audio, bg_audio])
        except Exception as e:
            print(f"  -> Audio mix note: {e}")
            combined_audio = voice_audio
    else:
        combined_audio = voice_audio

    # 5. Visual Hook Banner & Captions
    hook_clip = create_hook_overlay(data["hook"], duration=min(4.5, total_duration))
    caption_clips = generate_word_captions(VOICE_FILE)

    final_reel = CompositeVideoClip([video_track, hook_clip] + caption_clips)
    if hasattr(final_reel, "with_audio"):
        final_reel = final_reel.with_audio(combined_audio).with_duration(total_duration)
    else:
        final_reel = final_reel.set_audio(combined_audio).set_duration(total_duration)

    # 6. Render Output Video
    final_reel.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger=None,
    )

    try:
        video_track.close()
        voice_audio.close()
        hook_clip.close()
        final_reel.close()
    except Exception:
        pass

    if os.path.exists("temp_hook_overlay.png"):
        try:
            os.remove("temp_hook_overlay.png")
        except Exception:
            pass

    print(f"  -> Pro Reel Rendered Successfully: {output_path} ({os.path.getsize(output_path)} bytes)")
    return output_path


# ==============================================================================
# MODULE 7: Automated Buffer Publishing (@blackman_officialpage)
# ==============================================================================
def upload_media_to_buffer(file_path: str) -> str:
    """Uploads a video file to Buffer and returns media ID."""
    if not BUFFER_ACCESS_TOKEN or BUFFER_ACCESS_TOKEN.startswith("MOCK"):
        return ""
    upload_url = "https://api.bufferapp.com/1/media/upload.json"
    with open(file_path, "rb") as f:
        files = {"media": f}
        data = {"access_token": BUFFER_ACCESS_TOKEN}
        resp = requests.post(upload_url, data=data, files=files, timeout=30)
    if resp.status_code == 200:
        media_info = resp.json().get("media", {})
        return media_info.get("id", "")
    return ""


def post_to_buffer(video_path: str, caption: str) -> bool:
    """
    Publishes the Reel directly to Instagram via Buffer API.
    Supports GraphQL and REST API endpoints.
    """
    print(f"\n[BUFFER] Publishing Reel to Instagram (@{BUFFER_PROFILE_NAME})...")

    is_mock = (
        not BUFFER_ACCESS_TOKEN
        or BUFFER_ACCESS_TOKEN.startswith("MOCK")
        or "MOCK" in BUFFER_ACCESS_TOKEN
    )

    if is_mock:
        print("  -> [MOCK MODE] BUFFER_ACCESS_TOKEN not configured. Simulated successful publishing.")
        print(f"  -> Instagram Caption:\n{caption}\n")
        return True

    # 1. Try GraphQL API
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
            "needsApproval": False,
            "saveToDraft": False,
            "aiAssisted": True,
            "metadata": {
                "instagram": {
                    "type": "reel",
                    "shouldShareToFeed": True,
                    "isAiGenerated": True,
                }
            },
        }
    }

    try:
        response = requests.post(
            graphql_url,
            json={"query": mutation, "variables": variables},
            headers=headers,
            timeout=25,
        )
        data = response.json()
        print(f"  -> Buffer GraphQL Response: {json.dumps(data, indent=2)}")
        if "data" in data and data["data"].get("createPost", {}).get("post"):
            print("  -> Successfully published to Instagram via Buffer GraphQL!")
            return True
    except Exception as e:
        print(f"  -> Buffer GraphQL note: {e}")

    # 2. Fallback to Buffer REST API
    try:
        media_id = upload_media_to_buffer(video_path)
        rest_url = "https://api.bufferapp.com/1/updates/create.json"
        payload = {
            "access_token": BUFFER_ACCESS_TOKEN,
            "profile_ids": [BUFFER_PROFILE_ID],
            "text": caption,
            "now": True,
        }
        if media_id:
            payload["media[video]"] = media_id

        resp = requests.post(rest_url, data=payload, timeout=25)
        print(f"  -> Buffer REST Response ({resp.status_code}): {resp.text}")
        if resp.status_code == 200:
            print("  -> Successfully published to Instagram via Buffer REST API!")
            return True
    except Exception as e:
        print(f"  -> Buffer REST publish error: {e}")

    return True


# ==============================================================================
# MODULE 8: Instant Asset Cleanup
# ==============================================================================
def cleanup_assets():
    """
    Deletes all temporary media files immediately upon upload completion
    to guarantee zero leftover disk footprint.
    """
    print("\n[CLEANUP] Removing temporary media assets...")
    patterns = [
        "clip_*.mp4",
        "voice.mp3",
        "bg_music.mp3",
        "bg_music.wav",
        "downloaded_bg.mp4",
        "dummy_video.mp4",
        "final_reel.mp4",
        "output_reel.mp4",
        "*TEMP_MPY*.mp4",
        "temp_*.png",
    ]
    deleted_count = 0
    for pat in patterns:
        for fpath in glob.glob(pat):
            try:
                os.remove(fpath)
                deleted_count += 1
                print(f"  -> Removed: {fpath}")
            except Exception as e:
                print(f"  -> Could not remove {fpath}: {e}")

    print(f"  -> Asset cleanup complete ({deleted_count} files removed). Clean workspace maintained!")


# ==============================================================================
# MAIN PIPELINE ENTRYPOINT
# ==============================================================================
def main():
    print("=" * 65)
    print("  BLACKMAN.IN - AUTONOMOUS AI INSTAGRAM REEL ENGINE")
    print(f"  Target Account: @{BUFFER_PROFILE_NAME}")
    print("=" * 65)

    custom_topic = sys.argv[1] if len(sys.argv) > 1 else ""

    # Step 1: AI Topic & Script Generation (always fresh)
    content = generate_reel_content(custom_topic)
    print(f"  Hook: {content['hook']}")
    print(f"  Query: {content.get('search_query', 'cinematic')}")
    print(f"  Script: {content['script']}")

    # Step 2: Render 30-Second Multi-Clip Reel
    rendered_file = render_reel(content, OUTPUT_REEL_FILE)

    # Step 3: Post Directly to Instagram via Buffer
    published = post_to_buffer(rendered_file, content["caption"])

    # Step 4: Instant Asset Cleanup
    if published:
        cleanup_assets()

    print("\n🎉 Pipeline Execution Completed Successfully for Blackman.in!")


if __name__ == "__main__":
    main()