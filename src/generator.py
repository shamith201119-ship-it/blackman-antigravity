import json
import os
import random
from typing import Dict, Any

FALLBACK_TEMPLATES = [
    {
        "badge": "SPEED & PERFORMANCE",
        "headline": "A 1-Second Page Delay Can Cost You 7% In Conversions.",
        "caption": (
            "⚡ Speed isn't just a technical metric — it's revenue.\n\n"
            "Here is why your website speed dictates your bottom line:\n"
            "• 47% of users expect a web page to load in 2 seconds or less.\n"
            "• Google prioritizes lightning-fast sites in search rankings.\n"
            "• Every extra second of loading causes bounce rates to spike by up to 32%.\n\n"
            "Is your site running as fast as it should? Let's turn your traffic into paying clients.\n\n"
            "👉 Visit blackman.in to supercharge your digital presence.\n"
            "🔗 Link in bio: https://blackman.in\n\n"
            "#WebDevelopment #WebDesign #SpeedOptimization #SEO #blackmanin #UXDesign #FrontendDevelopment #HighConvertingWebsites"
        )
    },
    {
        "badge": "CONVERSION DESIGN",
        "headline": "Clean UI Gets Attention. Strategic UX Closes Deals.",
        "caption": (
            "✨ Pretty websites don't sell. Purpose-built experiences do.\n\n"
            "When designing for conversion:\n"
            "1. Clarify your value proposition above the fold in under 5 seconds.\n"
            "2. Use high-contrast, singular Call-To-Actions (CTAs).\n"
            "3. Optimize mobile touch targets and navigation flow.\n\n"
            "Ready to scale your business with a custom-engineered web platform?\n\n"
            "🌐 Explore our solutions at blackman.in\n"
            "💬 DM us or visit the link in bio!\n\n"
            "#WebDesign #UXStrategy #ConversionRateOptimization #blackmanin #FullStackDev #WebsiteDevelopment #ModernWeb"
        )
    },
    {
        "badge": "MODERN STACK",
        "headline": "Stop Relying On Slow Templates. Custom Architecture Wins.",
        "caption": (
            "🚀 Generic website builders might get you started, but bespoke web engineering scales you to the next level.\n\n"
            "Why custom development outperforms:\n"
            "✓ Tailored architecture with zero bloated code\n"
            "✓ 95+ Google Lighthouse performance scores\n"
            "✓ Seamless custom API and CRM integrations\n"
            "✓ Enterprise-grade security and reliability\n\n"
            "Take your brand to the modern era with blackman.in.\n\n"
            "🔗 Link in bio: https://blackman.in\n\n"
            "#WebAgency #CustomWebsites #NextJS #ReactJS #Performance #blackmanin #TechStartup #WebEngineering"
        )
    }
]

def generate_content(api_key: str = None) -> Dict[str, Any]:
    """
    Generates high-engagement Instagram content for blackman.in using Groq LLM API.
    Falls back to curated templates if API key is not provided or API call fails.
    """
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key or key == "your_groq_api_key_here":
        print("[Generator] GROQ_API_KEY missing or placeholder. Using curated high-converting template.")
        return random.choice(FALLBACK_TEMPLATES)

    try:
        from groq import Groq
        client = Groq(api_key=key)

        topics = [
            "website conversion rate optimization",
            "mobile-first responsive design importance",
            "page load speed impact on sales",
            "modern web design psychology",
            "SEO architecture for small & medium businesses",
            "why custom web development beats standard templates",
            "UX/UI micro-interactions that boost user retention",
            "core web vitals and Google search ranking"
        ]
        chosen_topic = random.choice(topics)

        prompt = f"""You are the lead marketing and technical copywriter for 'blackman.in', a premier web development and digital agency.
Topic: {chosen_topic}

Generate a compelling, high-value Instagram post in JSON format with the following keys:
1. "badge": A short uppercase category badge (2-4 words, e.g. "CONVERSION HACK", "WEB PERFORMANCE", "UX DESIGN PRINCIPLE").
2. "headline": A punchy, bold, curiosity-inducing or authoritative 1-2 sentence headline for a 1080x1080 social media graphic (maximum 15 words).
3. "caption": A high-converting Instagram caption structured with:
   - An attention-grabbing hook emoji line
   - 3 concise bullet points explaining actionable value
   - Clear pitch connecting the value to working with blackman.in
   - Strong Call To Action directing users to visit blackman.in (link in bio)
   - 6-10 relevant hashtags including #blackmanin, #WebDevelopment, #WebDesign

Respond ONLY with valid JSON conforming to:
{{
    "badge": "string",
    "headline": "string",
    "caption": "string"
}}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional social media and web development copywriter. Always output strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=600
        )

        content_str = response.choices[0].message.content.strip()
        data = json.loads(content_str)

        # Validate required fields
        if "headline" in data and "caption" in data:
            if "badge" not in data:
                data["badge"] = "WEB INSIGHT"
            print(f"[Generator] Successfully generated content for topic: '{chosen_topic}'")
            return data
        else:
            raise ValueError("Response missing required fields")

    except Exception as e:
        print(f"[Generator] Error calling Groq API: {e}. Falling back to default template.")
        return random.choice(FALLBACK_TEMPLATES)

if __name__ == "__main__":
    content = generate_content()
    print("\n--- GENERATED CONTENT ---")
    print(f"Badge: {content['badge']}")
    print(f"Headline: {content['headline']}")
    print(f"\nCaption:\n{content['caption']}")
