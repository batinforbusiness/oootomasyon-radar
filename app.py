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
# APP CONFIG
# =========================================================

st.set_page_config(
    page_title="OOOtomasyon Radar",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()


# =========================================================
# API KEY HANDLING
# =========================================================

def get_openai_key() -> Optional[str]:
    key = None

    try:
        key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        key = None

    if not key:
        key = os.getenv("OPENAI_API_KEY")

    if key:
        return str(key).strip()

    return None


OPENAI_API_KEY = get_openai_key()
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


# =========================================================
# GLOBAL STATE
# =========================================================

DEFAULT_STATE = {
    "radar_results": [],
    "selected_repo": None,
    "selected_repo_analysis": None,
    "founder_profile": {
        "audience": "AI, otomasyon, internetten para kazanma ve içerik üretimiyle ilgilenen kişiler",
        "assets": "11k X hesabı, OOOtomasyon markası, AI/otomasyon kitlesi, içerik üretme tecrübesi",
        "goal": "İlk 30-60 günde satılabilir bir sistem veya dijital ürün çıkarmak",
    },
    "opportunity_result": None,
    "launch_pack": None,
    "last_scan": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# DESIGN SYSTEM
# =========================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
    --bg: #050711;
    --panel: rgba(255,255,255,0.055);
    --panel-2: rgba(255,255,255,0.085);
    --stroke: rgba(255,255,255,0.10);
    --muted: #9CA7BA;
    --text: #F7FAFF;
    --blue: #5A82FF;
    --cyan: #27E2CA;
    --green: #77FFD0;
    --yellow: #FFD76E;
    --red: #FF8B8B;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(54, 98, 255, 0.24), transparent 32%),
        radial-gradient(circle at top right, rgba(39, 226, 202, 0.13), transparent 28%),
        radial-gradient(circle at bottom left, rgba(151, 86, 255, 0.10), transparent 30%),
        linear-gradient(180deg, #050711 0%, #080D19 48%, #050711 100%);
    color: var(--text);
}

.block-container {
    max-width: 1520px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

[data-testid="stSidebar"] {
    background: rgba(5, 8, 18, 0.92);
    border-right: 1px solid rgba(255,255,255,0.08);
}

h1, h2, h3 {
    letter-spacing: -0.055em;
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 20px;
    padding: 16px;
}

div[data-testid="stMetricLabel"] {
    color: #9CA7BA;
}

div[data-testid="stMetricValue"] {
    color: white;
    font-weight: 900;
}

.stButton > button {
    width: 100%;
    height: 48px;
    border-radius: 16px;
    border: 0;
    background: linear-gradient(135deg, #5A82FF, #27E2CA);
    color: #04101E;
    font-weight: 900;
    box-shadow: 0 14px 34px rgba(39, 226, 202, 0.14);
}

.stButton > button:hover {
    filter: brightness(1.08);
    color: #04101E;
    border: 0;
}

.stDownloadButton > button {
    border-radius: 14px;
    font-weight: 800;
}

.stSelectbox label,
.stTextInput label,
.stTextArea label,
.stSlider label,
.stNumberInput label,
.stRadio label,
.stCheckbox label {
    color: #DCE7F8 !important;
    font-weight: 800;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 38px 40px;
    border-radius: 34px;
    border: 1px solid rgba(255,255,255,0.11);
    background:
        linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.035)),
        radial-gradient(circle at 85% 20%, rgba(39,226,202,0.25), transparent 25%);
    box-shadow: 0 28px 90px rgba(0,0,0,0.34);
    margin-bottom: 24px;
}

.hero:before {
    content: "";
    position: absolute;
    width: 360px;
    height: 360px;
    right: -90px;
    top: -120px;
    border-radius: 999px;
    background: radial-gradient(circle, rgba(90,130,255,0.35), transparent 65%);
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 13px;
    border-radius: 999px;
    background: rgba(90,130,255,0.17);
    border: 1px solid rgba(90,130,255,0.32);
    color: #C8D6FF;
    font-size: 13px;
    font-weight: 900;
    margin-bottom: 16px;
}

.hero-title {
    font-size: 52px;
    line-height: 1.01;
    font-weight: 900;
    max-width: 920px;
    color: white;
    letter-spacing: -0.065em;
    margin-bottom: 16px;
}

.hero-subtitle {
    color: #AEB8CA;
    font-size: 17px;
    line-height: 1.7;
    max-width: 860px;
}

.stepbar {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin: 18px 0 26px;
}

.step {
    padding: 18px;
    border-radius: 24px;
    background: rgba(255,255,255,0.052);
    border: 1px solid rgba(255,255,255,0.095);
}

.step-active {
    background:
        linear-gradient(135deg, rgba(90,130,255,0.20), rgba(39,226,202,0.08));
    border: 1px solid rgba(90,130,255,0.32);
}

.step-icon {
    font-size: 32px;
    line-height: 1;
    margin-bottom: 10px;
    filter: drop-shadow(0 10px 16px rgba(0,0,0,.30));
}

.step-title {
    font-weight: 900;
    color: white;
    font-size: 15px;
    margin-bottom: 5px;
}

.step-desc {
    color: #9CA7BA;
    font-size: 13px;
    line-height: 1.45;
}

.card {
    padding: 26px;
    border-radius: 28px;
    background:
        linear-gradient(135deg, rgba(255,255,255,0.078), rgba(255,255,255,0.035));
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 24px 80px rgba(0,0,0,0.28);
    margin-bottom: 22px;
}

.card-soft {
    padding: 20px;
    border-radius: 24px;
    background: rgba(0,0,0,0.20);
    border: 1px solid rgba(255,255,255,0.08);
    height: 100%;
}

.repo-title {
    color: white;
    font-weight: 900;
    font-size: 24px;
    letter-spacing: -0.045em;
    margin-bottom: 7px;
}

.repo-desc {
    color: #AEB8CA;
    font-size: 14px;
    line-height: 1.58;
    margin-bottom: 14px;
}

.tag {
    display: inline-flex;
    align-items: center;
    padding: 7px 11px;
    border-radius: 999px;
    background: rgba(255,255,255,0.07);
    color: #DEE7F6;
    border: 1px solid rgba(255,255,255,0.09);
    font-size: 12px;
    font-weight: 800;
    margin-right: 7px;
    margin-bottom: 7px;
}

.tag-green {
    background: rgba(42,255,180,0.12);
    color: #7DFFD4;
    border-color: rgba(42,255,180,0.28);
}

.tag-yellow {
    background: rgba(255,198,64,0.13);
    color: #FFD76E;
    border-color: rgba(255,198,64,0.28);
}

.tag-red {
    background: rgba(255,82,82,0.13);
    color: #FF9A9A;
    border-color: rgba(255,82,82,0.28);
}

.section-title {
    font-size: 16px;
    font-weight: 900;
    color: white;
    margin: 18px 0 8px;
    letter-spacing: -0.025em;
}

.body {
    color: #CAD3E2;
    line-height: 1.72;
    font-size: 14px;
}

.big-score {
    font-size: 44px;
    font-weight: 900;
    letter-spacing: -0.06em;
    color: white;
    line-height: 1;
}

.small-muted {
    color: #96A2B7;
    font-size: 13px;
    line-height: 1.55;
}

.post-box {
    padding: 18px;
    border-radius: 18px;
    background: rgba(0,0,0,0.28);
    border: 1px solid rgba(255,255,255,0.09);
    color: #DEE7F6;
    line-height: 1.72;
    white-space: pre-wrap;
}

hr {
    border-color: rgba(255,255,255,0.08);
}

[data-testid="stTabs"] button {
    font-weight: 900;
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
    "AI Search Engines": "ai search engine answer engine stars:>100",
    "Newsletter / Curation": "newsletter curation ai content stars:>50",
    "Prompt / Agent Ops": "prompt management agent ops ai stars:>50",
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

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "", 1).strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "", 1).strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

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


def call_ai_json(prompt: str, system: str, temperature: float = 0.58) -> Dict[str, Any]:
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

        content = response.choices[0].message.content
        return extract_json(content)

    except Exception as e:
        error_name = e.__class__.__name__
        return {
            "_error": f"{error_name}: {str(e)}",
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
                    "topics": item.get("topics", []),
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
Gerektiğinde "Çöp" diyebilirsin. Abartı, hype ve jenerik AI dili kullanma.
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

Kurallar:
- Her repodan SaaS çıkarma.
- Uygulanabilir değilse "Çöp" de.
- Fiyat aralığı gerçekçi olsun.
- İlk müşteri somut olsun.
- Sistemin input-process-output mantığı olsun.
- Türkiye'de de uygulanabilecek örnekler düşün.

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

Amaç:
Bu repo kullanılarak bu founder için gerçek bir iş modeli kurulabilir mi?
Kurulabilirse nasıl satılır?
İlk 30 günde nasıl para kazanılır?

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
# UI COMPONENTS
# =========================================================

def render_hero():
    st.markdown(
        """
<div class="hero">
    <div class="badge">🛰️ OOOTOMASYON RADAR</div>
    <div class="hero-title">Repo değil, satılabilir fırsat bul.</div>
    <div class="hero-subtitle">
        GitHub'daki yeni projeleri tarar, işe yarayanları ayıklar, seçtiğin repoyu Founder OS ile iş modeline çevirir
        ve sonunda launch için kullanabileceğin içerik + satış paketini üretir.
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

    html = '<div class="stepbar">'
    for idx, (icon, title, desc) in enumerate(steps, start=1):
        cls = "step step-active" if idx == active else "step"
        html += f"""
        <div class="{cls}">
            <div class="step-icon">{icon}</div>
            <div class="step-title">{title}</div>
            <div class="step-desc">{desc}</div>
        </div>
        """
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


def render_error_box(error: str):
    st.error(error)

    if "AuthenticationError" in error or "Incorrect API key" in error or "401" in error:
        st.info(
            "OpenAI key hatası. Streamlit Cloud > Manage app > Settings > Secrets içine "
            '`OPENAI_API_KEY="sk-proj-..."` formatında ekle ve app’i reboot et.'
        )


def render_repo_card(item: Dict[str, Any], index: int):
    repo = item["repo"]
    analysis = item["analysis"]
    decision = analysis.get("share_decision", "-")
    ooo_score = item.get("ooo_score", analysis.get("ooo_score", 0))

    st.markdown('<div class="card">', unsafe_allow_html=True)

    top_left, top_right = st.columns([4, 1])

    with top_left:
        st.markdown(f'<div class="repo-title">{repo.get("name")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="repo-desc">{repo.get("description")}</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <span class="tag">OOO Score {ooo_score}/10</span>
            <span class="{tag_class(decision)}">{decision}</span>
            <span class="tag">⭐ {repo.get("stars", 0)}</span>
            <span class="tag">Fork {repo.get("forks", 0)}</span>
            <span class="tag">{repo.get("language", "-")}</span>
            """,
            unsafe_allow_html=True,
        )

    with top_right:
        st.link_button("GitHub", repo.get("url", ""))
        if st.button("Bu repoyu seç", key=f"select_repo_{index}"):
            st.session_state.selected_repo = repo
            st.session_state.selected_repo_analysis = analysis
            st.session_state.opportunity_result = None
            st.session_state.launch_pack = None
            st.rerun()

    st.divider()

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Para", analysis.get("money_potential", 0))
    m2.metric("Sistem", analysis.get("system_potential", 0))
    m3.metric("Viral", analysis.get("virality", 0))
    m4.metric("Timing", analysis.get("market_timing", 0))
    m5.metric("Zorluk", analysis.get("difficulty", 0))

    st.markdown('<div class="section-title">Net karar</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="body">{analysis.get("short_verdict", "-")}</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown('<div class="card-soft">', unsafe_allow_html=True)
        st.markdown("**Ne satılır?**")
        st.write(analysis.get("what_to_sell", "-"))
        st.markdown("**Fiyat**")
        st.write(analysis.get("price_range", "-"))
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card-soft">', unsafe_allow_html=True)
        st.markdown("**Kim satın alır?**")
        st.write(analysis.get("who_buys", "-"))
        st.markdown("**İlk müşteri**")
        first_customer = analysis.get("first_customer", {})
        st.write(safe_get(first_customer, "who"))
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="card-soft">', unsafe_allow_html=True)
        st.markdown("**İş fikri**")
        business = analysis.get("business_idea", {})
        st.write(safe_get(business, "name"))
        st.markdown("**Model**")
        st.write(safe_get(business, "delivery_model"))
        st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Detaylı analiz"):
        st.write("**Aslında ne?**", analysis.get("what_it_really_is", "-"))
        st.write("**Neden ilginç?**", analysis.get("why_interesting", "-"))
        st.write("**Risk:**", analysis.get("risk", "-"))

    with st.expander("30 günlük para planı"):
        for step in analysis.get("30_day_money_plan", []):
            st.write(f"• {step}")

    with st.expander("X postu"):
        st.markdown(f'<div class="post-box">{analysis.get("x_post", "-")}</div>', unsafe_allow_html=True)
        st.code(analysis.get("x_post", "-"))

    st.markdown("</div>", unsafe_allow_html=True)


def render_selected_repo_summary():
    repo = st.session_state.selected_repo
    analysis = st.session_state.selected_repo_analysis

    if not repo or not analysis:
        return

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="badge">✅ SEÇİLEN FIRSAT</div>', unsafe_allow_html=True)
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
    st.markdown("## 🛰️ Radar Panel")

    api_status = "Bağlı" if OPENAI_API_KEY else "Eksik"
    st.caption(f"OpenAI API: {api_status}")

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
        st.session_state.selected_repo_analysis = None
        st.session_state.opportunity_result = None
        st.session_state.launch_pack = None
        st.rerun()


# =========================================================
# PAGE RENDER
# =========================================================

render_hero()

if page.startswith("1"):
    render_stepbar(1)

    left, right = st.columns([1.4, 1])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Radar ayarları</div>', unsafe_allow_html=True)

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
            '<div class="small-muted">Öneri: İlk taramada 5-8 repo seç. Çok yüksek sayı hem yavaşlatır hem API maliyetini artırır.</div>',
            unsafe_allow_html=True,
        )

        run_radar = st.button("Radar'ı Çalıştır")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Bu aşamada ne oluyor?</div>', unsafe_allow_html=True)
        st.write(
            "Radar GitHub’daki projeleri çeker, her birini iş fırsatı olarak analiz eder ve "
            "hangilerinin içerik / ürün / servis fikrine dönüşebileceğini skorlar."
        )
        st.write("Çıktı: OOO Score, ne satılır, kim alır, ilk müşteri ve 30 günlük para planı.")
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
                    render_error_box(analysis["_error"])
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
        render_selected_repo_summary()

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Founder OS</div>', unsafe_allow_html=True)
        st.write(
            "Burada uzun form yok. Seçtiğin repo zaten ana veri. Sen sadece kitleni, varlıklarını ve hedefini kısaca söylüyorsun."
        )

        profile = st.session_state.founder_profile

        c1, c2, c3 = st.columns(3)

        with c1:
            audience = st.text_area("Kitle / müşteri tipi", value=profile["audience"], height=120)

        with c2:
            assets = st.text_area("Mevcut varlıkların", value=profile["assets"], height=120)

        with c3:
            goal = st.text_area("Hedef", value=profile["goal"], height=120)

        run_founder = st.button("Bu repodan iş modeli çıkar")

        st.markdown("</div>", unsafe_allow_html=True)

        if run_founder:
            st.session_state.founder_profile = {
                "audience": audience,
                "assets": assets,
                "goal": goal,
            }

            with st.spinner("Founder OS seçilen repoyu iş modeline çeviriyor..."):
                result = run_founder_os(
                    st.session_state.selected_repo,
                    st.session_state.selected_repo_analysis,
                    st.session_state.founder_profile,
                )

            if "_error" in result:
                render_error_box(result["_error"])
            else:
                st.session_state.opportunity_result = result
                st.session_state.launch_pack = None
                st.rerun()

        opportunity = st.session_state.opportunity_result

        if opportunity:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.markdown('<div class="badge">🧠 FOUNDER FIT</div>', unsafe_allow_html=True)

            c1, c2 = st.columns([1, 3])
            with c1:
                st.markdown(f'<div class="big-score">{opportunity.get("founder_fit_score", "-")}/10</div>', unsafe_allow_html=True)
                st.markdown('<div class="small-muted">Founder Fit Score</div>', unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="section-title">Konumlanma</div>', unsafe_allow_html=True)
                st.write(opportunity.get("positioning", "-"))
                st.markdown('<div class="section-title">Net karar</div>', unsafe_allow_html=True)
                st.write(opportunity.get("final_verdict", "-"))

            st.divider()

            model = opportunity.get("best_business_model", {})
            product = opportunity.get("productized_offer", {})

            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown('<div class="card-soft">', unsafe_allow_html=True)
                st.markdown("**İş modeli**")
                st.write(safe_get(model, "name"))
                st.markdown("**Tek cümle**")
                st.write(safe_get(model, "one_liner"))
                st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="card-soft">', unsafe_allow_html=True)
                st.markdown("**Teklif**")
                st.write(safe_get(model, "offer"))
                st.markdown("**Fiyat**")
                st.write(safe_get(model, "price_range"))
                st.markdown("</div>", unsafe_allow_html=True)

            with c3:
                st.markdown('<div class="card-soft">', unsafe_allow_html=True)
                st.markdown("**İlk müşteri**")
                st.write(safe_get(model, "first_customer_source"))
                st.markdown("**Model**")
                st.write(safe_get(model, "delivery_model"))
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="section-title">Ürünleştirilmiş teklif</div>', unsafe_allow_html=True)
            st.write("**Ad:**", safe_get(product, "name"))
            st.write("**Vaat:**", safe_get(product, "promise"))
            st.write("**Fiyat:**", safe_get(product, "price"))
            st.write("**Kurulum süresi:**", safe_get(product, "setup_time"))

            with st.expander("Deliverables"):
                for item in product.get("deliverables", []):
                    st.write(f"• {item}")

            with st.expander("İlk 7 gün"):
                for item in opportunity.get("first_7_days", []):
                    st.write(f"• {item}")

            with st.expander("İlk 30 gün"):
                for item in opportunity.get("first_30_days", []):
                    st.write(f"• {item}")

            with st.expander("İçerik stratejisi"):
                content = opportunity.get("content_strategy", {})
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
    elif not st.session_state.opportunity_result:
        st.warning("Önce Founder OS aşamasında seçilen repoyu iş modeline çevirmelisin.")
    else:
        render_selected_repo_summary()

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Launch Pack</div>', unsafe_allow_html=True)
        st.write(
            "Bu aşama seçilen fırsatı satışa hazır hale getirir: landing başlığı, teklif paketi, DM mesajı, X thread ve demo script."
        )

        run_launch = st.button("Launch Pack üret")

        st.markdown("</div>", unsafe_allow_html=True)

        if run_launch:
            with st.spinner("Launch Pack hazırlanıyor..."):
                launch = generate_launch_pack(
                    st.session_state.selected_repo,
                    st.session_state.opportunity_result,
                )

            if "_error" in launch:
                render_error_box(launch["_error"])
            else:
                st.session_state.launch_pack = launch
                st.rerun()

        launch = st.session_state.launch_pack

        if launch:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.markdown('<div class="badge">🚀 LAUNCH PACK</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-title">Landing başlığı</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="repo-title">{launch.get("landing_headline", "-")}</div>', unsafe_allow_html=True)
            st.write(launch.get("landing_subheadline", "-"))

            c1, c2 = st.columns(2)

            with c1:
                st.markdown('<div class="card-soft">', unsafe_allow_html=True)
                st.markdown("**Fiyatlandırma**")
                st.write(launch.get("pricing", "-"))
                st.markdown("**CTA**")
                st.write(launch.get("cta", "-"))
                st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="card-soft">', unsafe_allow_html=True)
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
