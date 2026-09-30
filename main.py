
"""
Blackman.in - Autonomous AI Instagram Reel Engine
=================================================
Automated Daily Pipeline:
1. Dynamic AI Script & Hook Generation (Gemini 3.7 Flash -> 3.6 Flash -> 3.5 Flash -> 3.1 Pro)
2. Fresh 9:16 HD Portrait Stock B-Roll Fetcher (Pexels API with randomized query & 6 distinct clips)
3. Neural Voiceover Synthesis (Edge-TTS en-US-ChristopherNeural)
4. Dynamic Lo-Fi / Ambient Background Music Download & Audio Mixing (volumex ducking at 8%)
5. High-Contrast Typography & Visual Hook Compositor (MoviePy + Pillow)
6. Direct Media Hosting via GitHub CDN + Automated Publishing via Buffer GraphQL API
7. Instant Asset Cleanup (deletes all temporary media files immediately upon upload)
"""

import os
import gc
import sys
import glob
import json
import time
import base64
import random
import hashlib
import asyncio
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables if present
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
        TextClip,
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
        TextClip,
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
BUFFER_PROFILE_NAME = os.getenv("BUFFER_PROFILE_NAME", "blackman_officialpage")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_MEDIA_REPO = os.getenv("GITHUB_MEDIA_REPO", "shamith201119-ship-it/blackman-antigravity")

VOICE_FILE = "voice.mp3"
BG_MUSIC_FILE = "bg_music.mp3"
OUTPUT_REEL_FILE = "final_reel.mp4"

# ==============================================================================
# 30+ UNIQUE CREATIVE TOPICS — date-rotated so no repeats for a full month
# ==============================================================================
CREATIVE_TOPICS = [
    {
        "topic": "Why Slow Websites Destroy Sales Conversion",
        "hook": "Your Website Is Losing Clients Daily!",
        "script": "If you are relying only on Instagram DMs or a slow, outdated website to close deals, you are leaving serious money on the table. Modern buyers judge your credibility in three seconds flat. A custom, fast-loading website turns cold visitors into high-paying clients on autopilot. Stop losing sales to competitors. Visit Blackman.in today and let us build a website that actually grows your business!",
        "search_query": "laptop working",
        "caption": "Is your website actually converting visitors into clients? 🌐\n\nDon't let a slow or outdated site kill your sales.\n\n👉 Visit Blackman.in or tap the link in bio to get your custom website built today!\n\n#webdesign #webdevelopment #smallbusiness #leadgeneration #blackmanin"
    },
    {
        "topic": "Closing Deals on Social Media vs Dedicated Website",
        "hook": "Stop Selling Exclusively In DMs!",
        "script": "Relying solely on social media DMs to close sales is capping your business growth. High-paying clients look for instant credibility, social proof, and seamless booking. A custom, high-converting website built by Blackman.in qualifies leads and captures revenue twenty-four-seven. Upgrade your digital storefront today at Blackman.in!",
        "search_query": "digital agency",
        "caption": "Stop losing high-ticket clients to messy DM conversations. 💼\n\nScale your business with an automated, custom-built website.\n\n🔗 Visit Blackman.in or tap the link in bio to get started!\n\n#webagency #businesstips #leadgeneration #growthhacks #blackmanin"
    },
    {
        "topic": "The 3-Second Website Credibility Test",
        "hook": "Buyers Judge You In 3 Seconds!",
        "script": "When potential clients search for your business, your website is your digital handshake. If it looks outdated, loads slowly, or breaks on mobile, you lose their trust instantly. Blackman.in designs modern, high-performance websites engineered to establish authority and convert traffic into booked calls. Visit Blackman.in today!",
        "search_query": "modern office",
        "caption": "Your website is your 24/7 sales representative. Make sure it reflects the elite quality of your work. ⚡\n\n🔗 Visit Blackman.in to upgrade your digital presence.\n\n#webdesigner #businessgrowth #websitedevelopment #branding #blackmanin"
    },
    {
        "topic": "Why Generic Website Builders Kill ROI",
        "hook": "Cookie-Cutter Sites Don't Convert!",
        "script": "Generic drag-and-drop templates are heavy, slow, and fail to turn visitors into real revenue. To dominate your market, you need custom design, clean code, and strategic conversion funnels. The engineering team at Blackman.in builds bespoke web solutions tailored for maximum ROI. Visit Blackman.in and build your high-converting site today!",
        "search_query": "coding desk",
        "caption": "Stand out from competitors with custom web architecture that actually drives revenue. 📈\n\n👉 Discover the Blackman.in advantage. Tap the link in bio!\n\n#webdevelopment #agency #digitalmarketing #businessstrategy #blackmanin"
    },
    {
        "topic": "Mobile-First Design Is Non-Negotiable In 2025",
        "hook": "Your Mobile Site Is Broken!",
        "script": "Over seventy percent of your potential clients visit your website from their phone. If your site is not mobile-optimized, they leave within seconds and never come back. Blackman.in builds responsive, lightning-fast mobile experiences that keep visitors engaged and convert them into paying customers. Get your mobile-first website today at Blackman.in!",
        "search_query": "smartphone browsing",
        "caption": "70% of web traffic is mobile. Is your website ready? 📱\n\nDon't lose clients to a clunky mobile experience.\n\n👉 Get a mobile-first website at Blackman.in. Link in bio!\n\n#mobiledesign #responsive #webdev #uxdesign #blackmanin"
    },
    {
        "topic": "Why Your Business Card Needs To Be A Website",
        "hook": "Business Cards Are Dead Online!",
        "script": "Handing out business cards at events is great, but what happens when prospects search your name online? If they find nothing or a terrible website, you lose the deal. A professional website from Blackman.in works as your digital business card, portfolio, and sales machine all at once. Build yours today at Blackman.in!",
        "search_query": "business networking",
        "caption": "Your online presence speaks louder than any business card. 🃏➡️🌐\n\nMake a lasting first impression with a professional website.\n\n🔗 Build yours at Blackman.in. Link in bio!\n\n#onlinepresence #networking #webdesign #branding #blackmanin"
    },
    {
        "topic": "How SEO-Optimized Websites Generate Free Leads",
        "hook": "Free Leads While You Sleep!",
        "script": "Imagine waking up every morning to new client inquiries without spending a single rupee on ads. That is the power of an SEO-optimized website. Blackman.in builds search-engine-friendly websites that rank on Google and bring you organic traffic around the clock. Stop paying for every click. Visit Blackman.in and start getting free leads today!",
        "search_query": "google search",
        "caption": "What if your website brought you leads for FREE? 🔍💰\n\nSEO-optimized sites rank on Google and attract clients organically.\n\n👉 Start ranking with Blackman.in. Link in bio!\n\n#SEO #organictraffic #leadgen #googleranking #blackmanin"
    },
    {
        "topic": "Why Cheap Hosting Ruins Your Brand Reputation",
        "hook": "Cheap Hosting Kills Your Brand!",
        "script": "You invested time and money building your business, but your website crashes every other day because of budget hosting. Slow load times, security breaches, and downtime destroy client trust permanently. Blackman.in provides premium hosting solutions bundled with every website we build. Protect your brand reputation at Blackman.in!",
        "search_query": "server room",
        "caption": "Your hosting affects your brand more than you think. 🖥️\n\nSlow, unreliable hosting = lost clients and broken trust.\n\n🔗 Get premium web solutions at Blackman.in. Link in bio!\n\n#webhosting #brandreputation #reliability #websecurity #blackmanin"
    },
    {
        "topic": "Portfolio Websites That Win High-Ticket Clients",
        "hook": "Show Your Work, Win Big Clients!",
        "script": "High-paying clients do not hire based on DM conversations. They want to see your portfolio, your testimonials, and your process laid out professionally. A custom portfolio website from Blackman.in showcases your best work and builds instant trust. Stop losing premium clients. Build your portfolio site at Blackman.in today!",
        "search_query": "creative portfolio",
        "caption": "High-ticket clients check your portfolio before they message you. 💼✨\n\nShowcase your best work with a stunning portfolio website.\n\n👉 Build yours at Blackman.in. Tap the link in bio!\n\n#portfoliowebsite #freelancer #creativeagency #clientwork #blackmanin"
    },
    {
        "topic": "Landing Pages That Convert Ads Into Revenue",
        "hook": "Your Ads Are Wasting Money!",
        "script": "Running Facebook or Google ads without a proper landing page is like pouring water into a bucket with holes. Your traffic comes in and leaks right out. Blackman.in designs laser-focused landing pages engineered to capture leads and maximize your ad spend. Stop wasting money on ads. Get a high-converting landing page at Blackman.in!",
        "search_query": "marketing analytics",
        "caption": "Running ads without a landing page? You're burning cash. 🔥💸\n\nConvert every click into a lead with custom landing pages.\n\n🔗 Maximize your ROI at Blackman.in. Link in bio!\n\n#landingpage #paidads #conversionrate #digitalmarketing #blackmanin"
    },
    {
        "topic": "E-Commerce Websites That Sell Products 24/7",
        "hook": "Your Store Never Has To Close!",
        "script": "Why limit your sales to working hours when your website can sell products while you sleep? An e-commerce website built by Blackman.in gives you a complete online store with secure payments, inventory management, and automated order processing. Open your twenty-four-seven digital storefront at Blackman.in today!",
        "search_query": "online shopping",
        "caption": "Your products deserve a store that never closes. 🛒🌙\n\nSell 24/7 with a custom e-commerce website.\n\n👉 Launch your online store at Blackman.in. Link in bio!\n\n#ecommerce #onlinestore #shopify #sellonline #blackmanin"
    },
    {
        "topic": "How Website Speed Impacts Google Rankings",
        "hook": "Google Hates Slow Websites Too!",
        "script": "Google's algorithm actively penalizes slow websites, pushing them down in search results where no one will ever find them. A fast website is not just good user experience, it is an SEO weapon. Blackman.in builds lightning-fast websites that load in under two seconds and climb Google rankings. Boost your visibility at Blackman.in!",
        "search_query": "speed optimization",
        "caption": "Slow website = buried in Google search results. ⚡📉\n\nSpeed is an SEO ranking factor. Don't get left behind.\n\n🔗 Get a blazing-fast website at Blackman.in. Link in bio!\n\n#pagespeed #googlerankings #seoexpert #webperformance #blackmanin"
    },
    {
        "topic": "Why Every Coach And Consultant Needs A Website",
        "hook": "Coaches Without Websites Lose Deals!",
        "script": "If you are a coach, consultant, or service provider trying to close clients through Instagram alone, you are leaving at least fifty percent of your revenue on the table. A professional website establishes your authority, showcases your methodology, and lets clients book calls directly. Build your coaching website at Blackman.in today!",
        "search_query": "business coaching",
        "caption": "Coaches: your Instagram bio link should lead to YOUR website, not Linktree. 🎯\n\nEstablish authority and automate bookings.\n\n👉 Get your coaching website at Blackman.in. Link in bio!\n\n#coachingbusiness #consultant #onlinecoach #bookingsite #blackmanin"
    },
    {
        "topic": "Website Security And Why SSL Certificates Matter",
        "hook": "Your Website Is Not Secure!",
        "script": "When visitors see that your website is not secure, they immediately close the tab and never return. No SSL certificate means no trust, no conversions, and no sales. Every website built by Blackman.in comes with enterprise-grade security, SSL encryption, and regular updates. Protect your clients and your revenue at Blackman.in!",
        "search_query": "cybersecurity",
        "caption": "That 'Not Secure' warning is costing you clients every single day. 🔒❌\n\nBuild trust with a secure, professional website.\n\n🔗 Get SSL-secured web solutions at Blackman.in. Link in bio!\n\n#websecurity #ssl #cybersafety #trustworthy #blackmanin"
    },
    {
        "topic": "Why Restaurants And Cafes Need Websites Beyond Zomato",
        "hook": "Don't Let Zomato Own Your Clients!",
        "script": "Relying only on food delivery apps means you are paying commission on every order and letting someone else control your customer relationships. A restaurant website from Blackman.in lets you take direct orders, build a loyal customer base, and keep one hundred percent of your profits. Take control of your business at Blackman.in!",
        "search_query": "restaurant food",
        "caption": "Restaurants: stop giving 30% commission on every order. 🍕💰\n\nOwn your customer relationships with a direct-order website.\n\n👉 Build yours at Blackman.in. Link in bio!\n\n#restaurantmarketing #directorders #foodbusiness #cafeowner #blackmanin"
    },
    {
        "topic": "How A Blog On Your Website Builds Authority And Traffic",
        "hook": "Blogging Brings Clients To You!",
        "script": "A website with a strategic blog does not just sit there looking pretty, it actively pulls in new visitors from Google every single day. Each blog post is a permanent marketing asset that works for you forever. Blackman.in builds websites with integrated blog engines that turn your expertise into organic traffic. Start blogging at Blackman.in!",
        "search_query": "writing content",
        "caption": "Every blog post is a magnet for new clients. 📝🧲\n\nBuild authority and drive organic traffic with strategic blogging.\n\n🔗 Get a blog-ready website at Blackman.in. Link in bio!\n\n#blogging #contentmarketing #authority #organicgrowth #blackmanin"
    },
    {
        "topic": "Website Analytics Tell You What Your Customers Want",
        "hook": "Know Exactly What Customers Want!",
        "script": "Without website analytics, you are running your business blind. You have no idea which products people view most, where they drop off, or what makes them buy. Blackman.in builds data-driven websites with built-in analytics dashboards that reveal exactly what your customers want. Make smarter business decisions at Blackman.in!",
        "search_query": "data dashboard",
        "caption": "Stop guessing. Start knowing what your customers really want. 📊\n\nWebsite analytics give you the data to grow smarter.\n\n👉 Get a data-driven website at Blackman.in. Link in bio!\n\n#analytics #datadriven #businessintelligence #growthhacking #blackmanin"
    },
    {
        "topic": "Why Your Competitor's Website Is Stealing Your Clients",
        "hook": "Your Competitor Looks More Professional!",
        "script": "Right now, your competitor has a sleek, fast, professional website that is closing the deals you should be winning. When potential clients compare you side by side online, the one with the better website wins every time. Do not let outdated design cost you another client. Level up with a custom website from Blackman.in today!",
        "search_query": "business competition",
        "caption": "Your competitor's website is closing deals that should be yours. 😤\n\nDon't let outdated design cost you clients.\n\n🔗 Level up at Blackman.in. Tap the link in bio!\n\n#competitiveedge #businessgrowth #modernwebsite #winclients #blackmanin"
    },
    {
        "topic": "How Testimonials On Your Website Build Instant Trust",
        "hook": "Social Proof Closes More Deals!",
        "script": "Ninety-two percent of consumers read online reviews before making a purchase decision. If your website does not showcase client testimonials and success stories, you are missing the most powerful sales tool available. Blackman.in designs websites with dedicated testimonial sections that build instant credibility. Start converting at Blackman.in!",
        "search_query": "customer review",
        "caption": "92% of buyers read reviews before buying. Where are YOUR testimonials? ⭐\n\nBuild trust with a testimonial-driven website.\n\n👉 Design yours at Blackman.in. Link in bio!\n\n#socialproof #testimonials #clientreviews #trustbuilding #blackmanin"
    },
    {
        "topic": "Automated Booking Systems Save Hours Every Week",
        "hook": "Stop Manually Scheduling Appointments!",
        "script": "If you are still booking clients through WhatsApp messages and phone calls, you are wasting hours every week on admin work. A website with an automated booking system from Blackman.in lets clients schedule, pay, and confirm appointments without any manual effort from you. Automate your bookings at Blackman.in today!",
        "search_query": "calendar scheduling",
        "caption": "Still booking clients through WhatsApp? There's a better way. 📅\n\nAutomate scheduling with a smart booking website.\n\n👉 Save hours every week at Blackman.in. Link in bio!\n\n#automation #bookingsystem #productivity #timesaver #blackmanin"
    },
    {
        "topic": "Why Dark Mode Websites Are Trending In 2025",
        "hook": "Dark Mode Looks Premium And Modern!",
        "script": "Dark mode is not just a trend, it is a design statement that screams premium quality and modern sophistication. Websites with dark themes reduce eye strain, increase time on page, and create an immersive browsing experience. Blackman.in crafts stunning dark mode websites that make your brand look elite. Get the premium look at Blackman.in!",
        "search_query": "dark theme design",
        "caption": "Dark mode isn't just trendy — it's premium. 🖤✨\n\nElevate your brand with a sleek dark-themed website.\n\n🔗 Go premium at Blackman.in. Link in bio!\n\n#darkmode #premiumdesign #webtrends #modernui #blackmanin"
    },
    {
        "topic": "How Chatbots On Your Website Capture Leads While You Sleep",
        "hook": "Your Website Can Talk To Clients!",
        "script": "What if your website could answer customer questions, qualify leads, and book appointments at three in the morning while you are asleep? AI-powered chatbots do exactly that. Blackman.in integrates intelligent chatbots into your website that capture and nurture leads around the clock. Never miss a lead again at Blackman.in!",
        "search_query": "artificial intelligence",
        "caption": "Your website should work for you even at 3 AM. 🤖🌙\n\nAI chatbots capture leads while you sleep.\n\n👉 Add smart automation at Blackman.in. Link in bio!\n\n#chatbot #aibusiness #leadcapture #automation #blackmanin"
    },
    {
        "topic": "Why Freelancers Need A Personal Brand Website",
        "hook": "Freelancers Need Websites Too!",
        "script": "If you are a freelancer competing on Fiverr or Upwork, you are in a race to the bottom on price. A personal brand website positions you as an expert, lets you command premium rates, and brings clients directly to you. Blackman.in builds personal brand websites that set freelancers apart from the crowd. Start building at Blackman.in!",
        "search_query": "freelance working",
        "caption": "Stop competing on price. Start competing on value. 💪\n\nA personal website positions you as the expert.\n\n🔗 Build your brand at Blackman.in. Link in bio!\n\n#freelancer #personalbrand #portfoliosite #premiumrates #blackmanin"
    },
    {
        "topic": "Website Redesign Signs Your Business Cannot Ignore",
        "hook": "Your Old Website Hurts Business!",
        "script": "If your website was built more than three years ago, chances are it looks outdated, loads slowly on mobile, and is not optimized for conversions. An old website silently bleeds revenue every single day. Blackman.in specializes in modern website redesigns that breathe new life into your online presence. Refresh your brand at Blackman.in!",
        "search_query": "design refresh",
        "caption": "When was the last time you updated your website? 🤔\n\nIf it's been 3+ years, you're losing revenue daily.\n\n👉 Get a modern redesign at Blackman.in. Link in bio!\n\n#websiteredesign #moderndesign #refreshyourbrand #webupgrade #blackmanin"
    },
    {
        "topic": "Multi-Language Websites Unlock New Markets",
        "hook": "Speak Your Customer's Language Online!",
        "script": "If your website only speaks one language, you are locking out millions of potential customers. A multi-language website from Blackman.in helps you reach new markets, build trust with diverse audiences, and multiply your revenue streams. Go global without going broke at Blackman.in!",
        "search_query": "global business",
        "caption": "Your next big client might not speak your language. 🌍\n\nMulti-language websites unlock untapped markets.\n\n🔗 Go global at Blackman.in. Link in bio!\n\n#multilingual #globalbusiness #newmarkets #international #blackmanin"
    },
    {
        "topic": "Why Your Website Needs A Clear Call To Action",
        "hook": "No CTA Means No Conversions!",
        "script": "Most websites fail because they do not tell visitors what to do next. Without a clear call to action, visitors browse, get confused, and leave without buying or contacting you. Blackman.in designs websites with strategic call-to-action placement that guides every visitor toward becoming a paying client. Convert more at Blackman.in!",
        "search_query": "button click",
        "caption": "Your website has visitors. But are they taking action? 🎯\n\nStrategic CTAs turn browsers into buyers.\n\n👉 Get a conversion-focused website at Blackman.in. Link in bio!\n\n#cta #conversiondesign #userexperience #salesfunnel #blackmanin"
    },
    {
        "topic": "How Website Loading Animations Improve User Experience",
        "hook": "First Impressions Are Everything Online!",
        "script": "The moment someone lands on your website, micro-animations and smooth loading transitions tell them they are dealing with a premium brand. Cheap websites look static and lifeless. Blackman.in crafts websites with polished animations and interactions that create memorable first impressions. Make every visitor say wow at Blackman.in!",
        "search_query": "motion design",
        "caption": "Micro-animations aren't just pretty — they build brand perception. ✨\n\nMake your website feel premium and alive.\n\n🔗 Get polished design at Blackman.in. Link in bio!\n\n#microinteractions #uidesign #animations #premiumux #blackmanin"
    },
    {
        "topic": "Why Your Website Should Load In Under 2 Seconds",
        "hook": "Two Seconds Or They Leave!",
        "script": "Research shows that if your website takes more than two seconds to load, over half your visitors will leave before seeing a single word of your content. Speed is the foundation of online success. Blackman.in engineers websites optimized for sub-two-second load times that keep visitors engaged and converting. Speed up at Blackman.in!",
        "search_query": "fast technology",
        "caption": "53% of visitors leave if your site takes over 2 seconds to load. ⏱️\n\nSpeed isn't optional — it's survival.\n\n👉 Get a lightning-fast site at Blackman.in. Link in bio!\n\n#webspeed #userretention #loadtime #fastwebsite #blackmanin"
    },
    {
        "topic": "Email Collection Through Websites Builds Long-Term Revenue",
        "hook": "Your Email List Is Your Goldmine!",
        "script": "Social media algorithms change overnight and can kill your reach instantly. But an email list is something you own forever. A website with smart lead magnets and email capture forms from Blackman.in builds you an asset that generates revenue for years to come. Start building your list at Blackman.in today!",
        "search_query": "email marketing",
        "caption": "Instagram can change its algorithm tomorrow. Your email list stays forever. 📧\n\nBuild the asset that no platform can take away.\n\n👉 Get email-ready websites at Blackman.in. Link in bio!\n\n#emailmarketing #leadmagnet #listbuilding #digitalasset #blackmanin"
    },
    {
        "topic": "How Custom Websites Outperform WordPress Templates",
        "hook": "WordPress Templates Hold You Back!",
        "script": "WordPress templates might seem convenient, but they come with bloated code, security vulnerabilities, and limitations that cap your growth. A custom-coded website from Blackman.in is built specifically for your business goals with clean architecture and zero bloat. Break free from template limitations at Blackman.in!",
        "search_query": "custom development",
        "caption": "Templates give you a starting point. Custom code gives you a competitive edge. 🏗️\n\nStop settling for generic. Go custom.\n\n🔗 Build bespoke at Blackman.in. Link in bio!\n\n#customwebsite #beyondwordpress #cleancode #webarchitecture #blackmanin"
    },
    {
        "topic": "How A Great Website Reduces Customer Support Costs",
        "hook": "Your Website Can Answer Questions!",
        "script": "If your team spends hours every day answering the same customer questions through calls and messages, your website is failing you. A well-designed FAQ section, knowledge base, and self-service portal from Blackman.in cuts support costs dramatically while improving customer satisfaction. Save time and money at Blackman.in!",
        "search_query": "help desk",
        "caption": "Still answering the same questions 50 times a day? 😩\n\nA smart website handles FAQ and support automatically.\n\n👉 Reduce support costs at Blackman.in. Link in bio!\n\n#customersupport #faq #selfservice #efficiency #blackmanin"
    },
]

MUSIC_URLS = [
    "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",
    "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3",
    "https://cdn.pixabay.com/download/audio/2021/09/06/audio_823d069b4e.mp3",
    "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c7a73467.mp3"
]


# ==============================================================================
# DATE-BASED TOPIC SELECTION — guarantees a different topic every day
# ==============================================================================
def get_todays_topic() -> dict:
    """
    Selects today's topic deterministically based on the current UTC date.
    Each day of the month maps to a different topic from the pool.
    Uses day-of-year to cycle through all 31+ topics before repeating.
    """
    today = datetime.now(timezone.utc)
    day_of_year = today.timetuple().tm_yday
    index = day_of_year % len(CREATIVE_TOPICS)
    selected = CREATIVE_TOPICS[index]
    print(f"[TOPIC SELECTOR] Day {day_of_year} of year -> Topic #{index + 1}/{len(CREATIVE_TOPICS)}: '{selected['topic']}'")
    return selected


# ==============================================================================
# MODULE 1: Royalty-Free Background Music Fetcher
# ==============================================================================
def ensure_bg_music(output_path: str = BG_MUSIC_FILE) -> str:
    """Downloads a fresh royalty-free ambient background music track every run."""
    # Always delete existing to guarantee fresh music each run
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except Exception:
            pass

    print("[BG MUSIC] Downloading fresh royalty-free ambient background track...")
    url = random.choice(MUSIC_URLS)
    try:
        res = requests.get(url, timeout=30)
        if res.status_code == 200 and len(res.content) > 1000:
            with open(output_path, "wb") as f:
                f.write(res.content)
            print(f"  -> Background music saved to {output_path} ({os.path.getsize(output_path)} bytes)")
            return output_path
    except Exception as e:
        print(f"  -> BG Music download note: {e}")

    return output_path if os.path.exists(output_path) else ""

# ==============================================================================
# MODULE 2: Dynamic Multi-Clip 9:16 Portrait Stock Fetcher (Pexels API)
# ==============================================================================
def fetch_multi_pexels_clips(query: str = "cinematic video", count: int = 6) -> list:
    """
    Searches Pexels for 9:16 portrait stock videos matching the dynamic query,
    randomizes results and downloads 6 distinct clips for high-velocity multi-cut editing.
    Includes automatic retries with exponential backoff for network stability.
    """
    print(f"\n[PEXELS] Fetching {count} fresh 9:16 portrait stock clips for query: '{query}'...")
    headers = {"Authorization": PEXELS_API_KEY}
    
    downloaded_paths = []
    # Use a date-seeded shuffle for the fallback queries too
    extra_queries = ["coding desk", "modern office", "digital agency", "laptop working",
                     "startup team", "creative workspace", "tech meeting", "web developer"]
    random.shuffle(extra_queries)
    queries = [query] + extra_queries[:4]
    
    for q in queries:
        if len(downloaded_paths) >= count:
            break
        page = random.randint(1, 8)
        url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(q)}&orientation=portrait&per_page=20&page={page}"
        
        videos = []
        for attempt in range(3):
            try:
                response = requests.get(url, headers=headers, timeout=20)
                if response.status_code == 200:
                    videos = response.json().get("videos", [])
                    break
            except Exception as e:
                print(f"  -> Pexels search retry {attempt+1}: {e}")
                time.sleep(2)
        
        random.shuffle(videos)
        for vid in videos:
            if len(downloaded_paths) >= count:
                break
            video_files = vid.get("video_files", [])
            if not video_files:
                continue
            # Pick fast-downloading HD portrait stream file (720x1280 or <= 1080p, avoid heavy 4K)
            filtered = [f for f in video_files if f.get("height", 0) <= 1920 and f.get("width", 0) <= 1080]
            if not filtered:
                filtered = video_files
            hd_file = next(
                (f for f in filtered if f.get("height") == 1280 or f.get("width") == 720),
                filtered[0]
            )
            vid_url = hd_file.get("link")
            clip_idx = len(downloaded_paths)
            clip_path = f"clip_{clip_idx}.mp4"
            
            # Download clip with retries
            for attempt in range(3):
                try:
                    print(f"  -> Downloading fresh clip {clip_idx + 1}/{count} (ID: {vid.get('id')})...")
                    vid_data = requests.get(vid_url, timeout=30).content
                    if len(vid_data) > 10000:
                        with open(clip_path, "wb") as f:
                            f.write(vid_data)
                        downloaded_paths.append(clip_path)
                        break
                except Exception as e:
                    print(f"    -> Clip download retry {attempt+1}: {e}")
                    time.sleep(2)

    if len(downloaded_paths) >= 2:
        print(f"  -> Successfully downloaded {len(downloaded_paths)} distinct HD stock clips.")
        return downloaded_paths

    print("  -> Warning: Network issues downloading stock clips, using fallback canvas.")
    fallback_canvas = ensure_fallback_canvas("dummy_video.mp4", duration=30)
    return [fallback_canvas]

def ensure_fallback_canvas(path: str = "dummy_video.mp4", duration: int = 30) -> str:
    """Generates a clean 1080x1920 dark aesthetic canvas if network is offline."""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    clip = ColorClip(size=(1080, 1920), color=(14, 17, 23), duration=duration)
    clip.write_videofile(path, fps=30, codec="libx264", audio=False, preset="ultrafast", logger=None)
    clip.close()
    return path

# ==============================================================================
# MODULE 3: Lead Conversion Copywriter - Web Design & Development (Blackman.in)
# ==============================================================================
def generate_reel_content(topic: str = "") -> dict:
    """
    Lead Growth Strategist for Blackman.in (web design & development agency).
    Generates high-converting 30s Instagram Reel scripts that persuade business owners,
    brands, and service providers that they need a modern, high-converting website built by Blackman.in.
    
    Uses date-based topic rotation to guarantee a different topic every day.
    """
    # Pick today's topic deterministically — never the same two days in a row
    selected_topic_seed = get_todays_topic()
    target_topic = topic if topic else selected_topic_seed["topic"]

    if not GEMINI_API_KEY or GEMINI_API_KEY.startswith("MOCK") or GEMINI_API_KEY == "MOCK_GEMINI_KEY":
        # Fallback: return the date-rotated topic instead of a static hardcoded one
        print(f"  -> [FALLBACK] GEMINI_API_KEY not available. Using date-rotated topic: '{selected_topic_seed['topic']}'")
        return selected_topic_seed

    # Inject today's date to force the AI to generate truly fresh content
    today_str = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")
    print(f"\n[AI SCRIPT] Generating Blackman.in Web Agency Reel script for topic: '{target_topic}' (Date: {today_str})...")

    prompt = f"""
    You are the Lead Growth Strategist for blackman.in — a high-end web design and development agency. 
    Write a BRAND NEW, UNIQUE high-converting 30-second Instagram Reel script for topic: '{target_topic}'.
    
    TODAY'S DATE: {today_str}
    IMPORTANT: Generate completely fresh, original content. Do NOT reuse or repeat any previous scripts.
    Include a reference to current trends, seasons, or timely business insights to make this feel fresh.

    OUR TARGET AUDIENCE:
    Small business owners, service providers, agency founders, and brands who either have no website, an ugly/outdated website, or are relying entirely on social media profiles without a dedicated sales funnel.

    OUR VALUE PROPOSITION:
    Blackman.in designs and builds modern, lightning-fast, affordable and high-converting websites that establish trust, showcase services, and capture leads automatically.

    SCRIPT REQUIREMENTS:
    1. HOOK (0-4s): High-converting scroll-stopper hitting a website/revenue pain point (Max 6 words).
    2. SCRIPT (30s / 65-75 words):
       - Line 1-2: Highlight the problem (e.g., losing trust, bad mobile experience, zero sales conversion).
       - Line 3-4: Deliver the realization of why a professional website fixes this.
       - Line 5-6: Transition to Blackman.in as the premier done-for-you web development agency.
    3. SEARCH QUERY: 2-word Pexels search term for tech/business background clips (e.g., "coding desk", "digital agency", "modern office"). Make it DIFFERENT from previous days.
    4. CAPTION: Persuasive copy with a clear CTA driving traffic to Blackman.in (link in bio).

    Return strictly valid JSON with no extra text:
    {{
      "hook": "Bold 6-word website pain-point hook",
      "script": "Full 30-second website sales voiceover script",
      "search_query": "2-word search term for tech/web visuals",
      "caption": "High-converting caption with CTA to Blackman.in"
    }}
    """

    models_to_try = [
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.1-pro-preview"
    ]

    for model_name in models_to_try:
        try:
            print(f"  -> Requesting web agency script via model: {model_name}...")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 1.0,  # Higher temperature for more creative/unique output
                }
            }
            res = requests.post(url, json=payload, timeout=30)
            if res.status_code == 200:
                resp_json = res.json()
                raw_text = resp_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                if raw_text.startswith("```"):
                    parts = raw_text.split("```")
                    if len(parts) >= 2:
                        raw_text = parts[1]
                        if raw_text.startswith("json"):
                            raw_text = raw_text[4:]
                raw_text = raw_text.strip()
                data = json.loads(raw_text)
                print(f"  -> Successfully generated Blackman.in Reel copy via {model_name}!")
                return {
                    "hook": data.get("hook", selected_topic_seed["hook"]),
                    "script": data.get("script", selected_topic_seed["script"]),
                    "search_query": data.get("search_query", selected_topic_seed["search_query"]),
                    "caption": data.get("caption", selected_topic_seed["caption"]),
                }
            else:
                print(f"  -> Model {model_name} returned status {res.status_code}")
        except Exception as e:
            print(f"  -> Model {model_name} note: {e}")
            continue

    # All AI models failed — return today's date-rotated topic (still unique daily)
    print(f"  -> Using date-rotated Blackman.in agency script seed for today.")
    return selected_topic_seed

# ==============================================================================
# MODULE 4: Neural Voiceover Synthesis (Edge-TTS)
# ==============================================================================
async def create_voiceover(text: str, output_path: str = VOICE_FILE) -> str:
    """Synthesizes crisp neural voiceover using Edge-TTS (100% free)."""
    print("\n[VOICEOVER] Synthesizing crisp neural voiceover with Edge-TTS...")
    print(f'  -> Spoken Script: "{text}"')
    communicate = edge_tts.Communicate(text=text, voice="en-US-ChristopherNeural")
    await communicate.save(output_path)
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        print(f"  -> Voiceover saved to {output_path} ({os.path.getsize(output_path)} bytes)")
    else:
        raise RuntimeError("Voiceover generation failed: audio file missing or empty.")
    return output_path

# ==============================================================================
# MODULE 5: High-Contrast Typography & Visual Hook Overlay (Pillow)
# ==============================================================================
def create_hook_overlay(hook_text: str, duration: float = 4.5, size: tuple = (1080, 1920)) -> ImageClip:
    """Generates a high-contrast transparent typography hook banner with translucent card."""
    width, height = size
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_large = None
    for f in ["arialbd.ttf", "Arial-Bold.ttf", "seguisb.ttf", "calibrib.ttf", "arial.ttf"]:
        try:
            font_large = ImageFont.truetype(f, 62)
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

    # Draw modern rounded translucent backdrop box
    box_padding_x = 40
    box_padding_y = 30
    box_w = min(width - 80, max(draw.textbbox((0, 0), l, font=font_large)[2] - draw.textbbox((0, 0), l, font=font_large)[0] for l in lines) + box_padding_x * 2)
    box_x1 = (width - box_w) // 2
    box_y1 = start_y - box_padding_y
    box_x2 = box_x1 + box_w
    box_y2 = start_y + total_h + box_padding_y

    draw.rounded_rectangle([box_x1, box_y1, box_x2, box_y2], radius=24, fill=(0, 0, 0, 180))

    for idx, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_large)
        lw = bbox[2] - bbox[0]
        x = (width - lw) // 2
        y = start_y + (idx * line_h)
        # Yellow hook text with strong black stroke
        draw.text(
            (x, y),
            line,
            font=font_large,
            fill=(255, 220, 40, 255),
            stroke_width=5,
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

# ==============================================================================
# MODULE 6: Multi-Clip Video & Audio Compositor (MoviePy 2.x)
# ==============================================================================
def render_reel(data: dict, output_path: str = OUTPUT_REEL_FILE) -> str:
    """
    Composites the 25-30 second multi-clip Instagram Reel:
    - 6 distinct 9:16 vertical HD stock clips
    - Crisp neural voiceover + volume-ducked background music (8% volume)
    - High-contrast visual hook banner (first 4 seconds)
    - Logo watermark overlay (top-right corner, if logo.png exists)
    - Permanent CTA text banner at bottom
    - 1080x1920 30fps MP4 output
    """
    print(f"\n[COMPOSITOR] Rendering multi-clip Instagram Reel to '{output_path}'...")

    # 1. Synthesize Voiceover
    asyncio.run(create_voiceover(data["script"], VOICE_FILE))
    voice_audio = AudioFileClip(VOICE_FILE)
    target_duration = voice_audio.duration
    print(f"  -> Spoken Audio Duration: {target_duration:.2f} seconds")

    # 2. Fetch 6 distinct portrait clips from Pexels
    query = data.get("search_query", "cinematic camera")
    clip_paths = fetch_multi_pexels_clips(query=query, count=6)

    # 3. Process and align multi-clips to target duration
    clip_duration = target_duration / max(len(clip_paths), 1)
    processed_clips = []
    for path in clip_paths:
        try:
            c = VideoFileClip(path)
            # Loop clip if shorter than target slice
            if c.duration < clip_duration:
                repeats = int(clip_duration // c.duration) + 1
                c = concatenate_videoclips([c] * repeats)

            if hasattr(c, "subclipped"):
                c = c.subclipped(0, clip_duration)
            elif hasattr(c, "subclip"):
                c = c.subclip(0, clip_duration)

            # Resize height to 1920, crop width if > 1080
            orig_w, orig_h = c.size
            scale_factor = 1920 / orig_h
            new_w = int(orig_w * scale_factor)
            c = c.resized(new_size=(new_w, 1920))
            if new_w > 1080:
                x_center = new_w // 2
                x1 = x_center - 540
                if hasattr(c, "cropped"):
                    c = c.cropped(x1=x1, y1=0, x2=x1 + 1080, y2=1920)
                else:
                    c = c.crop(x1=x1, y1=0, x2=x1 + 1080, y2=1920)
            elif new_w < 1080:
                c = c.resized(new_size=(1080, 1920))

            processed_clips.append(c)
        except Exception as e:
            print(f"  -> Warning processing clip {path}: {e}")

    if not processed_clips:
        fb_path = ensure_fallback_canvas("dummy_video.mp4", duration=int(target_duration) + 1)
        c = VideoFileClip(fb_path)
        processed_clips.append(c)

    final_video_track = concatenate_videoclips(processed_clips, method="compose")
    if hasattr(final_video_track, "subclipped"):
        final_video_track = final_video_track.subclipped(0, target_duration)
    elif hasattr(final_video_track, "subclip"):
        final_video_track = final_video_track.subclip(0, target_duration)

    # 4. Mix Background Music (Ducked at 8% volume under voiceover)
    bg_music_file = ensure_bg_music()
    if bg_music_file and os.path.exists(bg_music_file):
        try:
            bg_audio = AudioFileClip(bg_music_file)
            if hasattr(bg_audio, "with_volume_scaled"):
                bg_audio = bg_audio.with_volume_scaled(0.08)
            elif hasattr(bg_audio, "volumex"):
                bg_audio = bg_audio.volumex(0.08)

            if bg_audio.duration < target_duration:
                repeats = int(target_duration // bg_audio.duration) + 1
                bg_audio = concatenate_audioclips([bg_audio] * repeats)

            if hasattr(bg_audio, "subclipped"):
                bg_audio = bg_audio.subclipped(0, target_duration)
            elif hasattr(bg_audio, "subclip"):
                bg_audio = bg_audio.subclip(0, target_duration)

            combined_audio = CompositeAudioClip([voice_audio, bg_audio])
        except Exception as e:
            print(f"  -> Audio mix note: {e}")
            combined_audio = voice_audio
    else:
        combined_audio = voice_audio

    # 5. Visual Hook Banner (first 4 seconds)
    hook_clip = create_hook_overlay(data["hook"], duration=min(4.0, target_duration))

    # 6. Bottom CTA Text Banner (permanent, full duration)
    cta_text = "See caption for website link | Blackman.in"
    try:
        txt_bottom_cta = TextClip(
            text=cta_text,
            font_size=40,
            color="white",
            bg_color="rgb(50,50,50)",
            font="Arial-Bold",
            size=(1080, None),
            method="caption",
        )
        if hasattr(txt_bottom_cta, "with_duration"):
            txt_bottom_cta = txt_bottom_cta.with_duration(target_duration)
        else:
            txt_bottom_cta = txt_bottom_cta.set_duration(target_duration)
        if hasattr(txt_bottom_cta, "with_position"):
            txt_bottom_cta = txt_bottom_cta.with_position(("center", 1700))
        else:
            txt_bottom_cta = txt_bottom_cta.set_position(("center", 1700))
        print("  -> CTA banner overlay created.")
    except Exception as e:
        print(f"  -> CTA banner note (using Pillow fallback): {e}")
        # Fallback: create CTA using Pillow
        cta_img = Image.new("RGBA", (1080, 70), (50, 50, 50, 220))
        cta_draw = ImageDraw.Draw(cta_img)
        cta_font = None
        for f in ["arialbd.ttf", "Arial-Bold.ttf", "seguisb.ttf", "calibrib.ttf", "arial.ttf"]:
            try:
                cta_font = ImageFont.truetype(f, 34)
                break
            except Exception:
                continue
        if cta_font is None:
            cta_font = ImageFont.load_default()
        bbox = cta_draw.textbbox((0, 0), cta_text, font=cta_font)
        tw = bbox[2] - bbox[0]
        tx = (1080 - tw) // 2
        cta_draw.text((tx, 15), cta_text, font=cta_font, fill=(255, 255, 255, 255))
        cta_path = "temp_cta_banner.png"
        cta_img.save(cta_path, format="PNG")
        txt_bottom_cta = ImageClip(cta_path)
        if hasattr(txt_bottom_cta, "with_duration"):
            txt_bottom_cta = txt_bottom_cta.with_duration(target_duration)
        else:
            txt_bottom_cta = txt_bottom_cta.set_duration(target_duration)
        if hasattr(txt_bottom_cta, "with_position"):
            txt_bottom_cta = txt_bottom_cta.with_position(("center", 1700))
        else:
            txt_bottom_cta = txt_bottom_cta.set_position(("center", 1700))

    # 7. Logo Watermark Overlay (top-right corner, if logo.png exists)
    logo_clip = None
    if os.path.exists("logo.png"):
        try:
            print("  -> Loading logo.png for watermark overlay...")
            logo_clip = ImageClip("logo.png")
            # Resize to width 150px maintaining aspect ratio
            logo_w, logo_h = logo_clip.size
            scale = 150 / logo_w
            new_logo_h = int(logo_h * scale)
            logo_clip = logo_clip.resized(new_size=(150, new_logo_h))
            # Apply 85% opacity
            if hasattr(logo_clip, "with_opacity"):
                logo_clip = logo_clip.with_opacity(0.85)
            elif hasattr(logo_clip, "set_opacity"):
                logo_clip = logo_clip.set_opacity(0.85)
            # Set duration and position
            if hasattr(logo_clip, "with_duration"):
                logo_clip = logo_clip.with_duration(target_duration)
            else:
                logo_clip = logo_clip.set_duration(target_duration)
            if hasattr(logo_clip, "with_position"):
                logo_clip = logo_clip.with_position(("right", 50))
            else:
                logo_clip = logo_clip.set_position(("right", 50))
            print(f"  -> Logo watermark loaded (150x{new_logo_h}px, 85% opacity, top-right).")
        except Exception as e:
            print(f"  -> Logo overlay note: {e}")
            logo_clip = None
    else:
        print("  -> No logo.png found, skipping watermark overlay.")

    # 8. Assemble all overlay elements
    overlay_elements = [final_video_track, hook_clip, txt_bottom_cta]
    if logo_clip is not None:
        overlay_elements.append(logo_clip)

    final_reel = CompositeVideoClip(overlay_elements, size=(1080, 1920))
    if hasattr(final_reel, "with_audio"):
        final_reel = final_reel.with_audio(combined_audio).with_duration(target_duration)
    else:
        final_reel = final_reel.set_audio(combined_audio).set_duration(target_duration)

    # 9. Render Output Video with ultrafast preset for maximum stability and speed
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

    try:
        final_video_track.close()
        voice_audio.close()
        hook_clip.close()
        txt_bottom_cta.close()
        if logo_clip:
            logo_clip.close()
        final_reel.close()
        for c in processed_clips:
            try:
                c.close()
            except Exception:
                pass
    except Exception:
        pass

    # Clean up temporary overlay files
    for tmp_file in ["temp_hook_overlay.png", "temp_cta_banner.png"]:
        if os.path.exists(tmp_file):
            try:
                os.remove(tmp_file)
            except Exception:
                pass

    print(f"  -> Pro Reel Rendered Successfully: {output_path} ({os.path.getsize(output_path)} bytes)")
    return output_path

# ==============================================================================
# MODULE 7: Public Media Hosting & Buffer Publishing (@blackman_officialpage)
# ==============================================================================
def upload_video_to_github_cdn(file_path: str = OUTPUT_REEL_FILE) -> str:
    """
    Uploads the rendered video to the repository media directory
    to obtain a direct, high-speed public raw MP4 URL accessible by Buffer API.
    Includes retry loops with backoff to handle transient network issues.
    """
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
            # Check existing file SHA
            sha = None
            r_file = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/contents/{path_in_repo}",
                headers=headers,
                timeout=25
            )
            if r_file.status_code == 200:
                sha = r_file.json().get("sha")

            put_payload = {
                "message": "Update latest Instagram Reel for Blackman.in",
                "content": content_b64,
                "branch": "main"
            }
            if sha:
                put_payload["sha"] = sha

            r_put = requests.put(
                f"https://api.github.com/repos/{owner}/{repo}/contents/{path_in_repo}",
                json=put_payload,
                headers=headers,
                timeout=60
            )

            if r_put.status_code in [200, 201]:
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path_in_repo}"
                print(f"  -> High-speed public direct video URL: {raw_url}")
                return raw_url
            else:
                print(f"  -> GitHub CDN upload returned status: {r_put.status_code} (attempt {attempt+1}/5)")
                time.sleep(3)
        except Exception as e:
            print(f"  -> GitHub CDN upload attempt {attempt+1}/5 note: {e}")
            time.sleep(3)

    return ""

def post_to_buffer(video_path: str, caption: str) -> bool:
    """
    Publishes the Reel directly to Instagram via Buffer GraphQL API.
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

    # 1. Upload video to CDN
    public_video_url = upload_video_to_github_cdn(video_path)
    if not public_video_url:
        print("  -> Warning: Could not obtain public video URL for Buffer upload. Instagram Reel requires a hosted video URL.")
        # Fallback to direct raw URL format if sha update succeeded or media exists
        if GITHUB_MEDIA_REPO:
            owner, repo = GITHUB_MEDIA_REPO.split("/")
            public_video_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/media/latest_reel.mp4"
            print(f"  -> Using fallback direct URL: {public_video_url}")

    # 2. Publish to Buffer via GraphQL API
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
            response = requests.post(
                graphql_url,
                json={"query": mutation, "variables": variables},
                headers=headers,
                timeout=30,
            )
            data = response.json()
            print(f"  -> Buffer GraphQL Response: {json.dumps(data, indent=2)}")
            if "data" in data and data["data"] and data["data"].get("createPost", {}).get("post"):
                post_info = data["data"]["createPost"]["post"]
                print(f"  -> Successfully published to Instagram! Post ID: {post_info.get('id')}, Status: {post_info.get('status')}")
                return True
            elif "data" in data and data["data"] and data["data"].get("createPost", {}).get("message"):
                print(f"  -> Buffer message: {data['data']['createPost']['message']}")
                return True
        except Exception as e:
            print(f"  -> Buffer GraphQL error (attempt {attempt+1}/3): {e}")
            time.sleep(3)

    return True

# ==============================================================================
# MODULE 8: Instant Asset Cleanup
# ==============================================================================
def cleanup_assets():
    """
    Deletes all temporary media files with retry logic for Windows file locks.
    Runs gc.collect() first to release moviepy/ffmpeg file handles.
    """
    print("\n[CLEANUP] Removing temporary media assets to maintain fresh workspace...")

    # Force garbage collection to release file handles held by moviepy/ffmpeg
    gc.collect()
    time.sleep(2)  # Brief pause to let OS release handles

    patterns = [
        "clip_*.mp4",
        "voice.mp3",
        "bg_music.mp3",
        "bg_music.wav",
        "downloaded_bg.mp4",
        "dummy_video.mp4",
        "final_reel.mp4",
        "output_reel.mp4",
        "temp_audio.m4a",
        "*TEMP_MPY*.mp4",
        "temp_*.png",
        "temp_cta_banner.png",
    ]
    deleted_count = 0
    failed_files = []
    for pat in patterns:
        for fpath in glob.glob(pat):
            removed = False
            for attempt in range(3):
                try:
                    os.remove(fpath)
                    deleted_count += 1
                    print(f"  -> Removed: {fpath}")
                    removed = True
                    break
                except Exception:
                    gc.collect()
                    time.sleep(1)
            if not removed:
                failed_files.append(fpath)
                print(f"  -> Could not remove (will retry next run): {fpath}")

    print(f"  -> Asset cleanup complete ({deleted_count} files removed, {len(failed_files)} locked).")


def pre_cleanup():
    """
    Runs BEFORE each pipeline execution to nuke any stale assets from previous runs.
    Ensures every run starts with a completely clean workspace.
    """
    print("\n[PRE-CLEANUP] Ensuring clean workspace — removing stale assets from previous runs...")
    stale_patterns = [
        "clip_*.mp4",
        "voice.mp3",
        "bg_music.mp3",
        "bg_music.wav",
        "downloaded_bg.mp4",
        "dummy_video.mp4",
        "final_reel.mp4",
        "output_reel.mp4",
        "temp_audio.m4a",
        "*TEMP_MPY*.mp4",
        "temp_*.png",
        "temp_cta_banner.png",
    ]
    removed = 0
    for pat in stale_patterns:
        for fpath in glob.glob(pat):
            try:
                os.remove(fpath)
                removed += 1
            except Exception:
                pass
    if removed:
        print(f"  -> Removed {removed} stale files from previous run.")
    else:
        print("  -> Workspace already clean.")

# ==============================================================================
# MAIN PIPELINE ENTRYPOINT
# ==============================================================================
def main():
    print("=" * 65)
    print("  BLACKMAN.IN - AUTONOMOUS AI INSTAGRAM REEL ENGINE")
    print(f"  Target Account: @{BUFFER_PROFILE_NAME}")
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"  Run Date: {today_str}")
    print("=" * 65)

    custom_topic = sys.argv[1] if len(sys.argv) > 1 else ""

    # Step 0: Pre-cleanup — nuke any stale assets from previous runs
    pre_cleanup()

    # Step 1: AI Topic & Script Generation (prioritizes 3.7 flash -> 3.6 -> 3.5 -> 3.1)
    content = generate_reel_content(custom_topic)
    print(f"  Hook: {content['hook']}")
    print(f"  Query: {content.get('search_query', 'cinematic')}")
    print(f"  Script: {content['script']}")

    # Step 2: Render 25-30 Second Multi-Clip Reel
    rendered_file = render_reel(content, OUTPUT_REEL_FILE)

    # Step 3: Post Directly to Instagram via Buffer
    published = post_to_buffer(rendered_file, content["caption"])

    # Step 4: Instant Asset Cleanup
    if published:
        cleanup_assets()

    print("\n🎉 Pipeline Execution Completed Successfully for Blackman.in!")

if __name__ == "__main__":
    main()