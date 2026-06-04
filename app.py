import os
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="OOOtomasyon Radar",
    page_icon="🧲",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()


def get_openai_key() -> Optional[str]:
    key = None
    try:
        key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        key = None

    if not key:
        key = os.getenv("OPENAI_API_KEY")

    return str(key).strip() if key else None


OPENAI_API_KEY = get_openai_key()
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


# =========================================================
# SESSION
# =========================================================

if "radar_results" not in st.session_state:
    st.session_state.radar_results = []

if "selected_repo" not in st.session_state:
    st.session_state.selected_repo = None

if "selected_analysis" not in st.session_state:
    st.session_state.selected_analysis = None

if "founder_result" not in st.session_state:
    st.session_state.founder_result = None

if "launch_pack" not in st.session_state:
    st.session_state.launch_pack = None

if "last_scan" not in st.session_state:
    st.session_state.last_scan = None


# =========================================================
# STYLE
# =========================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(255, 214, 102, 0.22), transparent 25%),
        radial-gradient(circle at top right, rgba(102, 190, 255, 0.22), transparent 28%),
        linear-gradient(180deg, #F7F3EA 0%, #F8F5EF 45%, #FFFFFF 100%);
    color: #121212;
}

.block-container {
    max-width: 1320px;
    padding-top: 2.2rem;
    padding-bottom: 5rem;
}

[data-testid="stSidebar"] {
    background: #111111;
    border-right: 1px solid rgba(255,255,255,0.08);
}

[data-testid="stSidebar"] * {
    color: #F5F5F5;
}

h1, h2, h3 {
    letter-spacing: -0.06em;
}

.stButton > button {
    width: 100%;
    height: 48px;
    border-radius: 999px;
    border: 0;
    color: #111111;
    font-weight: 900;
    background: linear-gradient(135deg, #FFE37A, #FFFFFF);
    box-shadow: 0 12px 28px rgba(0,0,0,0.12);
}

.stButton > button:hover {
    color: #111111;
    filter: brightness(1.03);
    border: 0;
}

.stDownloadButton > button {
    border-radius: 999px;
    font-weight: 800;
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.74);
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 22px;
    padding: 16px;
    box-shadow: 0 16px 45px rgba(0,0,0,0.06);
}

[data-testid="stMetricValue"] {
    color: #111111;
    font-weight: 900;
}

[data-testid="stMetricLabel"] {
    color: #727272;
    font-weight: 700;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 46px 48px;
    border-radius: 36px;
    background:
        linear-gradient(135deg, rgba(255,255,255,0.82), rgba(255,255,255,0.38)),
        radial-gradient(circle at 78% 38%, rgba(255,226,120,0.75), transparent 22%),
        radial-gradient(circle at 95% 10%, rgba(110,195,255,0.35), transparent 28%);
    border: 1px solid rgba(0,0,0,0.08);
    box-shadow: 0 28px 90px rgba(0,0,0,0.10);
    margin-bottom: 28px;
}

.hero-grid {
    display: grid;
    grid-template-columns: 1.25fr 0.75fr;
    gap: 34px;
    align-items: center;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    border-radius: 999px;
    background: #111111;
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 900;
    margin-bottom: 18px;
}

.hero-title {
    font-size: 60px;
    line-height: 0.97;
    font-weight: 900;
    color: #111111;
    letter-spacing: -0.075em;
    margin-bottom: 18px;
    max-width: 860px;
}

.hero-subtitle {
    color: #4B4B4B;
    font-size: 17px;
    line-height: 1.72;
    max-width: 760px;
    font-weight: 500;
}

.visual-card {
    position: relative;
    min-height: 330px;
    border-radius: 34px;
    background:
        linear-gradient(180deg, rgba(255,255,255,0.44), rgba(255,255,255,0.20)),
        url("https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80");
    background-size: cover;
    background-position: center;
    border: 8px solid rgba(255,255,255,0.82);
    box-shadow: 0 28px 70px rgba(0,0,0,0.18);
    overflow: hidden;
}

.visual-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, rgba(255,255,255,0.18), rgba(0,0,0,0.14));
}

.visual-pill {
    position: absolute;
    padding: 11px 14px;
    border-radius: 999px;
    background: rgba(255,255,255,0.82);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.65);
    color: #111111;
    font-size: 13px;
    font-weight: 900;
    box-shadow: 0 14px 35px rgba(0,0,0,0.12);
}

.pill-1 { left: 24px; bottom: 32px; }
.pill-2 { right: 24px; bottom: 82px; }
.pill-3 { right: 28px; top: 24px; }

.step-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin: 28px 0;
}

.step-card {
    padding: 22px;
    border-radius: 28px;
    background: rgba(255,255,255,0.70);
    border: 1px solid rgba(0,0,0,0.08);
    box-shadow: 0 18px 50px rgba(0,0,0,0.07);
}

.step-active {
    background: linear-gradient(135deg, #111111, #2B2B2B);
    color: white;
}

.step-icon {
    font-size: 40px;
    line-height: 1;
    margin-bottom: 14px;
}

.step-title {
    font-size: 17px;
    font-weight: 900;
    letter-spacing: -0.035em;
    margin-bottom: 7px;
}

.step-desc {
    font-size: 13px;
    line-height: 1.55;
    color: #606060;
    font-weight: 600;
}

.step-active .step-desc {
    color: #D6D6D6;
}

.panel {
    padding: 28px;
    border-radius: 32px;
    background: rgba(255,255,255,0.74);
    border: 1px solid rgba(0,0,0,0.08);
    box-shadow: 0 20px 70px rgba(0,0,0,0.07);
    margin-bottom: 22px;
}

.repo-card {
    padding: 26px;
    border-radius: 32px;
    background: rgba(255,255,255,0.82);
    border: 1px solid rgba(0,0,0,0.08);
    box-shadow: 0 20px 70px rgba(0,0,0,0.08);
    margin-bottom: 22px;
}

.repo-title {
    color: #111111;
    font-size: 25px;
    font-weight: 900;
    letter-spacing: -0.055em;
    margin-bottom: 8px;
}

.repo-desc {
    color: #555555;
    font-size: 14px;
    line-height: 1.62;
    margin-bottom: 14px;
    font-weight: 500;
}

.tag {
    display: inline-flex;
    align-items: center;
    padding: 7px 12px;
    border-radius: 999px;
    background: #F2F2F2;
    color: #111111;
    border: 1px solid rgba(0,0,0,0.06);
    font-size: 12px;
    font-weight: 900;
    margin-right: 7px;
    margin-bottom: 7px;
}

.tag-dark {
    background: #111111;
    color: white;
}

.tag-green {
    background: #DDFBEF;
    color: #0B7049;
}

.tag-yellow {
    background: #FFF1C8;
    color: #775600;
}

.tag-red {
    background: #FFE0E0;
    color: #8C1F1F;
}

.sub-title {
    font-size: 16px;
    font-weight: 900;
    letter-spacing: -0.035em;
    color: #111111;
    margin: 18px 0 8px;
}

.text-muted {
    color: #5D5D5D;
    line-height: 1.68;
    font-size: 14px;
}

.inner-card {
    padding: 18px;
    border-radius: 24px;
    background: #FAFAFA;
    border: 1px solid rgba(0,0,0,0.06);
    height: 100%;
}

.post-box {
    padding: 18px;
    border-radius: 22px;
    background: #111111;
    color: #F7F7F7;
    line-height: 1.75;
    white-space: pre-wrap;
    font-size: 14px;
}

.big-score {
    font-size: 48px;
    font-weight: 900;
    letter-spacing: -0.08em;
    line-height: 1;
    color: #111111;
}

.small {
    color: #6B6B6B;
    font-size: 13px;
    line-height: 1.55;
    font-weight: 600;
}

.info-box {
    padding: 16px 18px;
    border-radius: 22px;
    background: #111111;
    color: white;
    font-weight: 700;
    line-height: 1.55;
}

hr {
    border-color: rgba(0,0,0,0.08);
}

@media (max-width: 900px) {
    .hero-grid { grid-template-columns: 1fr; }
    .hero-title { font-size: 42px; }
    .step-row { grid-template-columns: 1fr; }
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# DATA
# =========================================================

RADAR_MODES = {
    "AI Agents": "ai agent autonomous agent stars:>500",
    "Content Machines": "ai content automation content generation stars:>100",
    "Video Automation": "ai video generation video automation stars:>100",
    "Shorts / Reels Factory": "shorts generator reels automation ai stars:>50",
    "YouTube Automation": "youtube automation ai video stars:>50",
    "UGC / Ad Creative": "ai ugc ad creative generation stars:>50",
    "Browser Automation": "browser automation ai agent stars:>100",
    "Web Scraping / Data": "web scraping ai crawler extraction stars:>100",
    "Lead Generation": "lead generation automation ai scraper stars:>50",
    "Marketing Automation": "marketing automation ai campaign stars:>50",
    "Sales Agents": "sales agent ai outreach automation stars:>50",
    "Customer Support AI": "customer support chatbot ai agent stars:>100",
    "RAG / Knowledge Base": "rag knowledge base ai chatbot stars:>500",
    "Local AI / Open Source ChatGPT": "local llm chatgpt open source stars:>500",
    "Workflow Automation": "workflow automation ai no code stars:>100",
    "MCP Servers": "mcp server ai tools stars:>50",
    "Voice Agents": "voice agent ai speech automation stars:>50",
    "Image Generation Workflows": "ai image generation workflow stars:>100",
    "Research Agents": "research agent ai deep research stars:>50",
    "Coding Agents": "coding agent ai developer stars:>500",
    "E-commerce Automation": "ecommerce automation ai product stars:>50",
    "Social Media Automation": "social media automation ai content stars:>50",
    "No-Code AI Builders": "no code ai app builder stars:>100",
}

BUSINESS_FOCUS_OPTIONS = [
    "İçerik üretim sistemi",
    "Lead generation sistemi",
    "Ajans hizmeti",
    "Micro SaaS",
    "Yerel işletmelere satılacak sistem",
    "Creator / influencer aracı",
    "E-ticaret otomasyonu",
    "B2B operasyon otomasyonu",
    "AI eğitim / template ürünü",
]


# =========================================================
# HELPERS
# =========================================================

def tag_class(decision: str) -> str:
    d = str(decision).lower()
    if "paylaş" in d or "evet" in d:
        return "tag tag-green"
    if "beklet" in d or "şüpheli" in d:
        return "tag tag-yellow"
    return "tag tag-red"


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def safe_get(d: Any, key: str, default: str = "-") -> str:
    if isinstance(d, dict):
        return d.get(key, default)
    return default


def extract_json(text: str) -> Dict[str, Any]:
    if not text:
        return {"_error": "Boş cevap döndü."}

    cleaned = text.strip()

    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except Exception:
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(cleaned[start:end + 1])
            except Exception:
                pass

    return {
        "_error": "JSON parse edilemedi.",
        "_raw": text,
    }


def call_ai_json(prompt: str, system: str, temperature: float = 0.55) -> Dict[str, Any]:
    if not client:
        return {
            "_error": "OPENAI_API_KEY bulunamadı. Streamlit Secrets kısmına OPENAI_API_KEY ekle.",
        }

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )

        return extract_json(response.choices[0].message.content)

    except Exception as e:
        return {
            "_error": f"{e.__class__.__name__}: {str(e)}",
        }


def calculate_ooo_score(analysis: Dict[str, Any]) -> float:
    money = safe_int(analysis.get("money_potential"))
    system = safe_int(analysis.get("system_potential"))
    virality = safe_int(analysis.get("virality"))
    timing = safe_int(analysis.get("market_timing"))
    demand = safe_int(analysis.get("demand"))
    ease = safe_int(analysis.get("ease_of_sale"))
    mvp = safe_int(analysis.get("mvp_speed"))
    difficulty = safe_int(analysis.get("difficulty"))

    score = (
        money * 0.22
        + system * 0.18
        + virality * 0.14
        + timing * 0.16
        + demand * 0.14
        + ease * 0.10
        + mvp * 0.10
        - difficulty * 0.04
    )

    return round(max(0, min(10, score)), 1)


@st.cache_data(ttl=900)
def github_search(query: str, limit: int, sort_mode: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    url = "https://api.github.com/search/repositories"

    params = {
        "q": query,
        "sort": sort_mode,
        "order": "desc",
        "per_page": limit,
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers={"Accept": "application/vnd.github+json"},
            timeout=25,
        )

        data = response.json()

        if "items" not in data:
            return [], data.get("message", "GitHub API hatası.")

        repos = []

        for item in data.get("items", []):
            repos.append(
                {
                    "name": item.get("full_name", "-"),
                    "description": item.get("description") or "Açıklama yok",
                    "stars": item.get("stargazers_count", 0),
                    "forks": item.get("forks_count", 0),
                    "issues": item.get("open_issues_count", 0),
                    "language": item.get("language") or "Bilinmiyor",
                    "url": item.get("html_url", ""),
                    "created_at": item.get("created_at", "-"),
                    "updated_at": item.get("updated_at", "-"),
                }
            )

        return repos, None

    except Exception as e:
        return [], str(e)


def flatten_radar_results(results: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []

    for item in results:
        repo = item.get("repo", {})
        analysis = item.get("analysis", {})
        business = analysis.get("business_idea", {})

        rows.append(
            {
                "OOO Score": item.get("ooo_score", 0),
                "Repo": repo.get("name", "-"),
                "Decision": analysis.get("share_decision", "-"),
                "What to sell": analysis.get("what_to_sell", "-"),
                "Buyer": analysis.get("who_buys", "-"),
                "Price": analysis.get("price_range", "-"),
                "Business": business.get("name", "-"),
                "URL": repo.get("url", "-"),
            }
        )

    return pd.DataFrame(rows)


# =========================================================
# AI PROMPTS
# =========================================================

def analyze_repo(repo: Dict[str, Any], business_focus: str) -> Dict[str, Any]:
    system = """
Sen OOOtomasyon Radar'ın ürün stratejistisin.
Görevin GitHub repolarını açıklamak değil, onlardan gerçek fırsat çıkarmak.
Gerektiğinde "Çöp" diyebilirsin.
Türkçe, net, pratik ve iş modeli odaklı yaz.
Cevabı sadece geçerli JSON olarak ver.
"""

    prompt = f"""
Aşağıdaki repo için profesyonel fırsat analizi yap.

REPO:
{json.dumps(repo, ensure_ascii=False, indent=2)}

İş odağı:
{business_focus}

Analiz mantığı:
1. Bu repo ile gerçek hayatta ne satılır?
2. Kim satın alır?
3. 30 gün içinde ilk para nasıl gelir?
4. İçerik üreticisi / ajans / solo founder için nasıl sistemleşir?
5. Bu gerçekten fırsat mı, yoksa oyuncak mı?

JSON FORMAT:
{{
  "share_decision": "Paylaş / Beklet / Çöp",
  "short_verdict": "tek cümlelik net karar",
  "system_potential": 1,
  "money_potential": 1,
  "virality": 1,
  "difficulty": 1,
  "market_timing": 1,
  "demand": 1,
  "ease_of_sale": 1,
  "mvp_speed": 1,
  "what_it_really_is": "repo aslında ne",
  "why_interesting": "neden ilginç",
  "what_to_sell": "bununla satılacak net şey",
  "who_buys": "kim satın alır",
  "price_range": "fiyat aralığı",
  "business_idea": {{
    "name": "iş fikri adı",
    "one_liner": "tek cümle",
    "target_customer": "hedef müşteri",
    "pain": "çözdüğü acı",
    "offer": "satılacak teklif",
    "delivery_model": "done-for-you / template / SaaS / danışmanlık / eğitim"
  }},
  "system_blueprint": {{
    "system_name": "sistem adı",
    "input": "sisteme ne girer",
    "process": ["adım 1", "adım 2", "adım 3", "adım 4"],
    "output": "sistem ne üretir",
    "mvp": "1 günde yapılacak MVP"
  }},
  "first_customer": {{
    "who": "ilk müşteri tipi",
    "where_to_find": "nereden bulunur",
    "outreach_message": "kısa satış mesajı"
  }},
  "30_day_money_plan": ["hafta 1", "hafta 2", "hafta 3", "hafta 4"],
  "use_cases": [
    {{"scenario": "senaryo 1", "example": "somut örnek"}},
    {{"scenario": "senaryo 2", "example": "somut örnek"}},
    {{"scenario": "senaryo 3", "example": "somut örnek"}}
  ],
  "risk": "en büyük risk",
  "content_angles": ["içerik açısı 1", "içerik açısı 2", "içerik açısı 3", "içerik açısı 4"],
  "x_post": "insan gibi yazılmış, kısa ve vurucu X postu"
}}
"""

    analysis = call_ai_json(prompt, system)
    if "_error" not in analysis:
        analysis["ooo_score"] = calculate_ooo_score(analysis)
    return analysis


def run_founder_os(repo: Dict[str, Any], repo_analysis: Dict[str, Any], profile: Dict[str, str]) -> Dict[str, Any]:
    system = """
Sen OOOtomasyon Radar'ın Founder OS stratejistisin.
Görevin seçilen repoyu kullanıcının varlıklarına göre gerçek bir iş modeline çevirmek.
Kullanıcıya 500 soru sorma. Mevcut repo + 3 kısa profil bilgisinden net plan çıkar.
Türkçe yaz. Net, sert, uygulanabilir ol. Cevabı sadece geçerli JSON ver.
"""

    prompt = f"""
Seçilen repo:
{json.dumps(repo, ensure_ascii=False, indent=2)}

Repo Radar analizi:
{json.dumps(repo_analysis, ensure_ascii=False, indent=2)}

Founder profili:
{json.dumps(profile, ensure_ascii=False, indent=2)}

Bu üç parçayı birleştirerek Founder OS analizi yap.

JSON FORMAT:
{{
  "founder_fit_score": 1,
  "positioning": "bu founder bu fırsatı nasıl konumlamalı",
  "main_warning": "en büyük hata riski",
  "best_business_model": {{
    "name": "iş modeli adı",
    "one_liner": "tek cümle",
    "why_fit": "bu foundera neden uyuyor",
    "target_customer": "kim satın alır",
    "offer": "net teklif",
    "price_range": "fiyat aralığı",
    "delivery_model": "servis / template / SaaS / eğitim / topluluk",
    "first_customer_source": "ilk müşteri nereden bulunur",
    "outreach_message": "kısa satış mesajı"
  }},
  "productized_offer": {{
    "name": "ürünleştirilmiş teklif adı",
    "promise": "müşteriye vaat",
    "deliverables": ["çıktı 1", "çıktı 2", "çıktı 3"],
    "setup_time": "kurulum süresi",
    "price": "fiyat"
  }},
  "first_7_days": ["gün 1", "gün 2", "gün 3", "gün 4", "gün 5", "gün 6", "gün 7"],
  "first_30_days": ["hafta 1", "hafta 2", "hafta 3", "hafta 4"],
  "content_strategy": {{
    "positioning_line": "X bio/konumlanma cümlesi",
    "content_pillars": ["kolon 1", "kolon 2", "kolon 3"],
    "next_7_posts": ["post 1", "post 2", "post 3", "post 4", "post 5", "post 6", "post 7"]
  }},
  "should_build": "Evet / Hayır / Önce sat",
  "final_verdict": "net karar"
}}
"""

    return call_ai_json(prompt, system)


def generate_launch_pack(repo: Dict[str, Any], opportunity: Dict[str, Any]) -> Dict[str, Any]:
    system = """
Sen OOOtomasyon Radar'ın launch stratejistisin.
Görevin seçilmiş fırsat için pazara çıkış paketi üretmek.
Türkçe, kısa, net ve satılabilir yaz. Cevabı sadece geçerli JSON ver.
"""

    prompt = f"""
Repo:
{json.dumps(repo, ensure_ascii=False, indent=2)}

Founder OS / Opportunity:
{json.dumps(opportunity, ensure_ascii=False, indent=2)}

Bu fırsatı satmak için launch pack üret.

JSON FORMAT:
{{
  "landing_headline": "landing page başlığı",
  "landing_subheadline": "alt başlık",
  "offer_stack": ["madde 1", "madde 2", "madde 3", "madde 4"],
  "pricing": "önerilen fiyatlandırma",
  "cta": "CTA metni",
  "cold_dm": "kısa DM mesajı",
  "x_thread": ["tweet 1", "tweet 2", "tweet 3", "tweet 4", "tweet 5"],
  "demo_script": "ekran kaydı demosunda ne anlatılacak",
  "validation_test": "inşa etmeden önce nasıl test edilir",
  "next_action": "şu an yapılacak tek sonraki adım"
}}
"""

    return call_ai_json(prompt, system)


# =========================================================
# UI FUNCTIONS
# =========================================================

def render_hero():
    st.markdown(
        """
<div class="hero">
    <div class="hero-grid">
        <div>
            <div class="hero-badge">🧲 OOOTOMASYON RADAR</div>
            <div class="hero-title">Repo değil, satılabilir fırsat bul.</div>
            <div class="hero-subtitle">
                GitHub'daki yeni projeleri tarar, işe yarayanları ayıklar, seçtiğin repoyu Founder OS ile
                iş modeline çevirir ve sonunda launch için kullanabileceğin içerik + satış paketini üretir.
            </div>
        </div>
        <div class="visual-card">
            <div class="visual-overlay"></div>
            <div class="visual-pill pill-1">🧠 Opportunity Score</div>
            <div class="visual-pill pill-2">💸 First Customer</div>
            <div class="visual-pill pill-3">🚀 Launch Pack</div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_stepbar(active: int):
    steps = [
        ("🧲", "1. Repo Radar", "Önce yeni repolar taranır ve fırsat skoru çıkarılır."),
        ("🧠", "2. Founder OS", "Seçilen repo senin varlıklarına göre iş modeline çevrilir."),
        ("🚀", "3. Launch Pack", "Satış mesajı, X thread, landing başlığı ve demo planı üretilir."),
    ]

    cols = st.columns(3)

    for idx, (icon, title, desc) in enumerate(steps, start=1):
        active_class = "step-card step-active" if idx == active else "step-card"
        with cols[idx - 1]:
            st.markdown(
                f"""
<div class="{active_class}">
    <div class="step-icon">{icon}</div>
    <div class="step-title">{title}</div>
    <div class="step-desc">{desc}</div>
</div>
""",
                unsafe_allow_html=True,
            )


def render_error(error: str):
    st.error(error)

    if "AuthenticationError" in error or "Incorrect API key" in error or "invalid_api_key" in error:
        st.info(
            "OpenAI key hatası. Streamlit Cloud > Manage app > Settings > Secrets içine "
            '`OPENAI_API_KEY="sk-proj-..."` formatında ekle ve app’i reboot et.'
        )


def render_repo_card(item: Dict[str, Any], index: int):
    repo = item["repo"]
    analysis = item["analysis"]
    decision = analysis.get("share_decision", "-")
    ooo_score = item.get("ooo_score", analysis.get("ooo_score", 0))
    business = analysis.get("business_idea", {})
    first_customer = analysis.get("first_customer", {})

    st.markdown('<div class="repo-card">', unsafe_allow_html=True)

    left, right = st.columns([4, 1])

    with left:
        st.markdown(f'<div class="repo-title">{repo.get("name")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="repo-desc">{repo.get("description")}</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
<span class="tag tag-dark">OOO Score {ooo_score}/10</span>
<span class="{tag_class(decision)}">{decision}</span>
<span class="tag">⭐ {repo.get("stars", 0)}</span>
<span class="tag">Fork {repo.get("forks", 0)}</span>
<span class="tag">{repo.get("language", "-")}</span>
""",
            unsafe_allow_html=True,
        )

    with right:
        st.link_button("GitHub", repo.get("url", ""))
        if st.button("Bu repoyu seç", key=f"select_repo_{index}"):
            st.session_state.selected_repo = repo
            st.session_state.selected_analysis = analysis
            st.session_state.founder_result = None
            st.session_state.launch_pack = None
            st.rerun()

    st.divider()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Para", analysis.get("money_potential", 0))
    c2.metric("Sistem", analysis.get("system_potential", 0))
    c3.metric("Viral", analysis.get("virality", 0))
    c4.metric("Timing", analysis.get("market_timing", 0))
    c5.metric("Zorluk", analysis.get("difficulty", 0))

    st.markdown('<div class="sub-title">Net karar</div>', unsafe_allow_html=True)
    st.write(analysis.get("short_verdict", "-"))

    a, b, c = st.columns(3)

    with a:
        st.markdown('<div class="inner-card">', unsafe_allow_html=True)
        st.markdown("**Ne satılır?**")
        st.write(analysis.get("what_to_sell", "-"))
        st.markdown("**Fiyat**")
        st.write(analysis.get("price_range", "-"))
        st.markdown("</div>", unsafe_allow_html=True)

    with b:
        st.markdown('<div class="inner-card">', unsafe_allow_html=True)
        st.markdown("**Kim satın alır?**")
        st.write(analysis.get("who_buys", "-"))
        st.markdown("**İlk müşteri**")
        st.write(safe_get(first_customer, "who"))
        st.markdown("</div>", unsafe_allow_html=True)

    with c:
        st.markdown('<div class="inner-card">', unsafe_allow_html=True)
        st.markdown("**İş fikri**")
        st.write(safe_get(business, "name"))
        st.markdown("**Model**")
        st.write(safe_get(business, "delivery_model"))
        st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Detaylı analiz"):
        st.write("**Aslında ne?**", analysis.get("what_it_really_is", "-"))
        st.write("**Neden ilginç?**", analysis.get("why_interesting", "-"))
        st.write("**Risk:**", analysis.get("risk", "-"))

    with st.expander("30 günlük para planı"):
        for item in analysis.get("30_day_money_plan", []):
            st.write(f"• {item}")

    with st.expander("X postu"):
        st.markdown(f'<div class="post-box">{analysis.get("x_post", "-")}</div>', unsafe_allow_html=True)
        st.code(analysis.get("x_post", "-"))

    st.markdown("</div>", unsafe_allow_html=True)


def render_selected_summary():
    repo = st.session_state.selected_repo
    analysis = st.session_state.selected_analysis

    if not repo or not analysis:
        return

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<span class="tag tag-dark">✅ Seçilen fırsat</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="repo-title">{repo.get("name")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="repo-desc">{repo.get("description")}</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("OOO Score", analysis.get("ooo_score", "-"))
    c2.metric("Para", analysis.get("money_potential", 0))
    c3.metric("Sistem", analysis.get("system_potential", 0))
    c4.metric("Zorluk", analysis.get("difficulty", 0))

    st.write("**Ne satılır?**", analysis.get("what_to_sell", "-"))
    st.write("**Kim satın alır?**", analysis.get("who_buys", "-"))

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("## 🧲 Radar Panel")
    st.caption(f"OpenAI API: {'Bağlı' if OPENAI_API_KEY else 'Eksik'}")

    st.divider()

    page = st.radio(
        "Akış",
        [
            "1 · Repo Radar",
            "2 · Founder OS",
            "3 · Launch Pack",
        ],
        index=0,
    )

    st.divider()

    if st.button("Seçimi sıfırla"):
        st.session_state.selected_repo = None
        st.session_state.selected_analysis = None
        st.session_state.founder_result = None
        st.session_state.launch_pack = None
        st.rerun()


# =========================================================
# APP
# =========================================================

render_hero()

if page.startswith("1"):
    render_stepbar(1)

    left, right = st.columns([1.35, 0.65])

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Radar ayarları</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:
            category = st.selectbox("Kategori", list(RADAR_MODES.keys()))
            business_focus = st.selectbox("İş odağı", BUSINESS_FOCUS_OPTIONS)

        with c2:
            sort_label = st.selectbox("Sıralama", ["Güncel", "Yıldız", "Fork"])
            limit = st.slider("Taranacak repo sayısı", 3, 20, 6)

        custom_query = st.text_input(
            "Özel GitHub araması",
            placeholder="Örn: ai content machine stars:>100",
        )

        st.markdown(
            '<div class="small">Öneri: İlk taramada 5-8 repo seç. Çok yüksek sayı hem yavaşlatır hem API maliyetini artırır.</div>',
            unsafe_allow_html=True,
        )

        run_radar = st.button("Radar'ı Çalıştır")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Bu aşamada ne oluyor?</div>', unsafe_allow_html=True)
        st.write(
            "Radar GitHub’daki projeleri çeker, her birini iş fırsatı olarak analiz eder ve "
            "hangilerinin içerik / ürün / servis fikrine dönüşebileceğini skorlar."
        )
        st.markdown('<div class="info-box">Çıktı: OOO Score, ne satılır, kim alır, ilk müşteri ve 30 günlük para planı.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if run_radar:
        sort_map = {
            "Güncel": "updated",
            "Yıldız": "stars",
            "Fork": "forks",
        }

        query = custom_query.strip() if custom_query.strip() else RADAR_MODES[category]
        repos, error = github_search(query, limit, sort_map[sort_label])

        if error:
            st.error(error)

        elif not repos:
            st.warning("Repo bulunamadı.")

        else:
            st.session_state.radar_results = []
            st.session_state.last_scan = datetime.now().strftime("%d.%m.%Y %H:%M")

            progress = st.progress(0)
            status = st.empty()

            for idx, repo in enumerate(repos, start=1):
                status.write(f"Analiz ediliyor: {repo['name']}")

                analysis = analyze_repo(repo, business_focus)

                if "_error" in analysis:
                    render_error(analysis["_error"])
                    break

                ooo_score = analysis.get("ooo_score", calculate_ooo_score(analysis))
                analysis["ooo_score"] = ooo_score

                st.session_state.radar_results.append(
                    {
                        "repo": repo,
                        "analysis": analysis,
                        "ooo_score": ooo_score,
                    }
                )

                progress.progress(idx / len(repos))
                time.sleep(0.15)

            status.write("Analiz tamamlandı.")

    results = sorted(
        st.session_state.radar_results,
        key=lambda x: x.get("ooo_score", 0),
        reverse=True,
    )

    if results:
        st.divider()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Bulunan fırsat", len(results))
        c2.metric("En yüksek skor", max(x.get("ooo_score", 0) for x in results))
        c3.metric("Son tarama", st.session_state.last_scan or "-")
        c4.metric("Seçilen repo", st.session_state.selected_repo.get("name", "-") if st.session_state.selected_repo else "-")

        df = flatten_radar_results(results)

        with st.expander("Radar tablosu"):
            st.dataframe(df, use_container_width=True)
            st.download_button(
                "CSV indir",
                df.to_csv(index=False).encode("utf-8-sig"),
                "oootomasyon_radar.csv",
                "text/csv",
            )

        for idx, item in enumerate(results):
            render_repo_card(item, idx)

    else:
        st.info("Radar'ı çalıştırınca analiz edilen repolar burada görünecek.")


elif page.startswith("2"):
    render_stepbar(2)

    if not st.session_state.selected_repo:
        st.warning("Önce Repo Radar aşamasında bir repo seçmelisin.")

    else:
        render_selected_summary()

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Founder OS</div>', unsafe_allow_html=True)
        st.write(
            "Burada uzun form yok. Seçtiğin repo zaten ana veri. Sen sadece kitleni, varlıklarını ve hedefini kısaca söylüyorsun."
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            audience = st.text_area(
                "Kitle / müşteri tipi",
                value="AI, otomasyon, internetten para kazanma ve içerik üretimiyle ilgilenen kişiler",
                height=125,
            )

        with c2:
            assets = st.text_area(
                "Mevcut varlıkların",
                value="11k X hesabı, OOOtomasyon markası, AI/otomasyon kitlesi, içerik üretme tecrübesi",
                height=125,
            )

        with c3:
            goal = st.text_area(
                "Hedef",
                value="İlk 30-60 günde satılabilir bir sistem veya dijital ürün çıkarmak",
                height=125,
            )

        run_founder = st.button("Bu repodan iş modeli çıkar")
        st.markdown("</div>", unsafe_allow_html=True)

        if run_founder:
            profile = {
                "audience": audience,
                "assets": assets,
                "goal": goal,
            }

            with st.spinner("Founder OS seçilen repoyu iş modeline çeviriyor..."):
                result = run_founder_os(
                    st.session_state.selected_repo,
                    st.session_state.selected_analysis,
                    profile,
                )

            if "_error" in result:
                render_error(result["_error"])
            else:
                st.session_state.founder_result = result
                st.session_state.launch_pack = None
                st.rerun()

        result = st.session_state.founder_result

        if result:
            st.markdown('<div class="panel">', unsafe_allow_html=True)

            st.markdown('<span class="tag tag-dark">🧠 Founder Fit</span>', unsafe_allow_html=True)

            c1, c2 = st.columns([1, 3])

            with c1:
                st.markdown(f'<div class="big-score">{result.get("founder_fit_score", "-")}/10</div>', unsafe_allow_html=True)
                st.markdown('<div class="small">Founder Fit Score</div>', unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="sub-title">Konumlanma</div>', unsafe_allow_html=True)
                st.write(result.get("positioning", "-"))
                st.markdown('<div class="sub-title">Net karar</div>', unsafe_allow_html=True)
                st.write(result.get("final_verdict", "-"))

            st.divider()

            model = result.get("best_business_model", {})
            product = result.get("productized_offer", {})

            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown('<div class="inner-card">', unsafe_allow_html=True)
                st.markdown("**İş modeli**")
                st.write(safe_get(model, "name"))
                st.markdown("**Tek cümle**")
                st.write(safe_get(model, "one_liner"))
                st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="inner-card">', unsafe_allow_html=True)
                st.markdown("**Teklif**")
                st.write(safe_get(model, "offer"))
                st.markdown("**Fiyat**")
                st.write(safe_get(model, "price_range"))
                st.markdown("</div>", unsafe_allow_html=True)

            with c3:
                st.markdown('<div class="inner-card">', unsafe_allow_html=True)
                st.markdown("**İlk müşteri**")
                st.write(safe_get(model, "first_customer_source"))
                st.markdown("**Model**")
                st.write(safe_get(model, "delivery_model"))
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="sub-title">Ürünleştirilmiş teklif</div>', unsafe_allow_html=True)
            st.write("**Ad:**", safe_get(product, "name"))
            st.write("**Vaat:**", safe_get(product, "promise"))
            st.write("**Fiyat:**", safe_get(product, "price"))
            st.write("**Kurulum süresi:**", safe_get(product, "setup_time"))

            with st.expander("Deliverables"):
                for item in product.get("deliverables", []):
                    st.write(f"• {item}")

            with st.expander("İlk 7 gün"):
                for item in result.get("first_7_days", []):
                    st.write(f"• {item}")

            with st.expander("İlk 30 gün"):
                for item in result.get("first_30_days", []):
                    st.write(f"• {item}")

            with st.expander("İçerik stratejisi"):
                content = result.get("content_strategy", {})
                st.write("**Konumlanma:**", safe_get(content, "positioning_line"))

                st.write("**İçerik kolonları:**")
                for item in content.get("content_pillars", []):
                    st.write(f"• {item}")

                st.write("**Sonraki 7 post:**")
                for item in content.get("next_7_posts", []):
                    st.write(f"• {item}")

            st.code(safe_get(model, "outreach_message"))

            st.markdown("</div>", unsafe_allow_html=True)


else:
    render_stepbar(3)

    if not st.session_state.selected_repo:
        st.warning("Önce Repo Radar aşamasında bir repo seçmelisin.")

    elif not st.session_state.founder_result:
        st.warning("Önce Founder OS aşamasında seçilen repoyu iş modeline çevirmelisin.")

    else:
        render_selected_summary()

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Launch Pack</div>', unsafe_allow_html=True)
        st.write(
            "Bu aşama seçilen fırsatı satışa hazır hale getirir: landing başlığı, teklif paketi, DM mesajı, X thread ve demo script."
        )

        run_launch = st.button("Launch Pack üret")
        st.markdown("</div>", unsafe_allow_html=True)

        if run_launch:
            with st.spinner("Launch Pack hazırlanıyor..."):
                launch = generate_launch_pack(
                    st.session_state.selected_repo,
                    st.session_state.founder_result,
                )

            if "_error" in launch:
                render_error(launch["_error"])
            else:
                st.session_state.launch_pack = launch
                st.rerun()

        launch = st.session_state.launch_pack

        if launch:
            st.markdown('<div class="panel">', unsafe_allow_html=True)

            st.markdown('<span class="tag tag-dark">🚀 Launch Pack</span>', unsafe_allow_html=True)

            st.markdown('<div class="sub-title">Landing başlığı</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="repo-title">{launch.get("landing_headline", "-")}</div>', unsafe_allow_html=True)
            st.write(launch.get("landing_subheadline", "-"))

            c1, c2 = st.columns(2)

            with c1:
                st.markdown('<div class="inner-card">', unsafe_allow_html=True)
                st.markdown("**Fiyatlandırma**")
                st.write(launch.get("pricing", "-"))
                st.markdown("**CTA**")
                st.write(launch.get("cta", "-"))
                st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="inner-card">', unsafe_allow_html=True)
                st.markdown("**Sıradaki aksiyon**")
                st.write(launch.get("next_action", "-"))
                st.markdown("**Validation testi**")
                st.write(launch.get("validation_test", "-"))
                st.markdown("</div>", unsafe_allow_html=True)

            with st.expander("Offer Stack"):
                for item in launch.get("offer_stack", []):
                    st.write(f"• {item}")

            with st.expander("Cold DM"):
                st.code(launch.get("cold_dm", "-"))

            with st.expander("X Thread"):
                for item in launch.get("x_thread", []):
                    st.write(item)
                    st.divider()

            with st.expander("Demo Script"):
                st.write(launch.get("demo_script", "-"))

            st.download_button(
                "Launch Pack JSON indir",
                json.dumps(launch, ensure_ascii=False, indent=2).encode("utf-8"),
                file_name="launch_pack.json",
                mime="application/json",
            )

            st.markdown("</div>", unsafe_allow_html=True)
