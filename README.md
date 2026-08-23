# 🚀 Blackman.in AI Instagram Reel Engine (100% Free & Cardless)

An automated, end-to-end Python pipeline designed for **Blackman.in** to generate and publish viral, high-contrast 9:16 Instagram Reels on complete autopilot without requiring paid APIs, credit cards, or SaaS subscriptions.

---

## 🌟 Key Features & Tech Stack

| Feature | Technology / Provider | Cost | Card Required? |
| :--- | :--- | :--- | :--- |
| **AI Script & Hook** | Google Gemini 2.5 Flash (`google-genai`) | **Free Tier** | ❌ No |
| **Neural Voiceover** | Edge-TTS (`en-US-ChristopherNeural`) | **100% Free & Unlimited** | ❌ No |
| **9:16 Canvas & Compositor**| MoviePy & Pillow | **Open Source** | ❌ No |
| **Instagram Publishing** | Buffer REST API / GitHub Actions Cron | **Free Plan** | ❌ No |

---

## 📂 Project Structure

```
.
├── main.py                     # Main pipeline orchestrator with 5 self-contained modules
├── dummy_video.mp4             # 9:16 1080x1920 base canvas (auto-generated)
├── requirements.txt            # Project dependencies
├── README.md                   # Setup and API configuration guide
└── .github/
    └── workflows/
        └── daily_reel.yml      # Automated GitHub Actions workflow (09:00 UTC daily)
```

---

## ⚡ Quickstart: Local Execution (Zero-Config Mock Mode)

The pipeline is pre-configured with safe mock fallbacks so you can test and inspect the full generation pipeline immediately without setting any environment variables.

### 1. Clone & Setup Virtual Environment
```bash
# Clone the repository and navigate into directory
git clone <YOUR_REPO_URL>
cd instagram-reel-engine

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Engine
```bash
python main.py
```

### 3. Expected Output
1. Generates the structured script and viral hook.
2. Synthesizes `voice.mp3` using Microsoft Edge's neural voice model.
3. Automatically generates the base 9:16 canvas `dummy_video.mp4` (if missing).
4. Renders the composited `output_reel.mp4` with high-contrast text overlay cards.
5. Prints the mock Buffer publishing confirmation and formatted Instagram caption.

---

## 🔑 Transitioning to Live Production (Free API Keys)

Follow these simple steps to activate live AI generation and automated Instagram posting:

### Step 1: Google Gemini API (Free Script Generation)
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with any standard Google account (no credit card required).
3. Click **"Get API Key"** -> **"Create API Key"**.
4. Copy your API key.

### Step 2: Buffer API (Free Instagram Scheduling & Publishing)
1. Register a free account at [Buffer.com](https://buffer.com/) and connect your Instagram Business/Creator profile.
2. Head to the [Buffer Developer Portal](https://buffer.com/developers/apps/create) to create an application.
3. Retrieve your **Access Token** (`BUFFER_ACCESS_TOKEN`) and find your Instagram **Profile ID** (`BUFFER_PROFILE_ID`).

### Step 3: Local Environment Variables
Create a `.env` file or export environment variables:
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your_actual_gemini_key"
$env:BUFFER_ACCESS_TOKEN="your_actual_buffer_token"
$env:BUFFER_PROFILE_ID="your_actual_buffer_profile_id"

# Linux / macOS
export GEMINI_API_KEY="your_actual_gemini_key"
export BUFFER_ACCESS_TOKEN="your_actual_buffer_token"
export BUFFER_PROFILE_ID="your_actual_buffer_profile_id"
```

### Step 4: GitHub Actions Deployment (Automatic Daily Posting)
1. Push your repository to GitHub.
2. In your GitHub repository, navigate to **Settings** > **Secrets and variables** > **Actions**.
3. Click **New repository secret** and add the following 3 secrets:
   - `GEMINI_API_KEY`
   - `BUFFER_ACCESS_TOKEN`
   - `BUFFER_PROFILE_ID`
4. The workflow in `.github/workflows/daily_reel.yml` will automatically trigger every day at **09:00 UTC** (or manually via **Actions** -> **Run workflow**).

---

## 🎨 Branding & Customization for Blackman.in
- To edit branding tags or font colors, customize `create_text_overlay_image()` in `main.py`.
- To adjust topics or video pacing, update `DEFAULT_TOPIC` and `total_duration` in `render_reel()`.

Enjoy automated, zero-cost video content creation for [Blackman.in](https://blackman.in)!
