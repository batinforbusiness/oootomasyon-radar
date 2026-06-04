import os
import json
import time
import hashlib
from datetime import datetime
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="OOOtomasyon Radar",
    page_icon="🛰️",
    layout="wide"
)

# =========================
# STYLE
# =========================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(34, 90, 255, 0.20), transparent 30%),
        radial-gradient(circle at top right, rgba(0, 255, 209, 0.10), transparent 28%),
        radial-gradient(circle at bottom left, rgba(255, 255, 255, 0.05), transparent 25%),
        linear-gradient(180deg, #050711 0%, #080D19 45%, #060914 100%);
    color: #F7F9FC;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 5rem;
    max-width: 1500px;
}

[data-testid="stSidebar"] {
    background: rgba(7, 11, 24, 0.86);
    border-right: 1px solid rgba(255,255,255,0.08);
}

h1, h2, h3 {
    letter-spacing: -0.045em;
}

.hero {
    padding: 34px 38px;
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 30px;
    background:
        linear-gradient(135deg, rgba(255,255,255,0.105), rgba(255,255,255,0.035));
    box-shadow: 0 28px 90px rgba(0,0,0,0.35);
    margin-bottom: 24px;
}

.hero-badge {
    display: inline-flex;
    padding: 7px 12px;
    border-radius: 999px;
    background: rgba(78, 124, 255, 0.16);
    color: #BFD0FF;
    font-size: 13px;
    font-weight: 800;
    border: 1px solid rgba(78, 124, 255, 0.30);
    margin-bottom: 16px;
}

.hero-title {
    font-size: 48px;
    line-height: 1.02;
    font-weight: 900;
    margin-bottom: 14px;
    color: #FFFFFF;
}

.hero-subtitle {
    font-size: 17px;
    line-height: 1.65;
    color: #AEB8CA;
    max-width: 920px;
}

.premium-card {
    padding: 26px;
    border-radius: 28px;
    background:
        linear-gradient(135deg, rgba(255,255,255,0.075), rgba(255,255,255,0.035));
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 24px 80px rgba(0,0,0,0.28);
    margin-bottom: 24px;
}

.repo-title {
    font-size: 25px;
    font-weight: 900;
    color: #FFFFFF;
    letter-spacing: -0.04em;
    margin-bottom: 6px;
}

.repo-desc {
    color: #AEB8CA;
    font-size: 14px;
    line-height: 1.6;
    margin-bottom: 14px;
}

.tag {
    display: inline-flex;
    padding: 6px 10px;
    border-radius: 999px;
    background: rgba(255,255,255,0.07);
    color: #DEE7F6;
    font-size: 12px;
    font-weight: 700;
    margin-right: 7px;
    margin-bottom: 7px;
    border: 1px solid rgba(255,255,255,0.09);
}

.decision-share {
    display: inline-flex;
    padding: 8px 13px;
    border-radius: 999px;
    background: rgba(40, 255, 178, 0.12);
    color: #7DFFD4;
    border: 1px solid rgba(40, 255, 178, 0.28);
    font-size: 13px;
    font-weight: 900;
}

.decision-wait {
    display: inline-flex;
    padding: 8px 13px;
    border-radius: 999px;
    background: rgba(255, 198, 64, 0.13);
    color: #FFD66E;
    border: 1px solid rgba(255, 198, 64, 0.28);
    font-size: 13px;
    font-weight: 900;
}

.decision-trash {
    display: inline-flex;
    padding: 8px 13px;
    border-radius: 999px;
    background: rgba(255, 82, 82, 0.13);
    color: #FF9797;
    border: 1px solid rgba(255, 82, 82, 0.28);
    font-size: 13px;
    font-weight: 900;
}

.section-title {
    color: #FFFFFF;
    font-size: 15px;
    font-weight: 900;
    margin-top: 18px;
    margin-bottom: 8px;
    letter-spacing: -0.02em;
}

.body-text {
    color: #CAD3E2;
    line-height: 1.7;
    font-size: 14px;
}

.mini-panel {
    padding: 17px;
    border-radius: 20px;
    background: rgba(0,0,0,0.20);
    border: 1px solid rgba(255,255,255,0.08);
    height: 100%;
}

.post-box {
    padding: 18px;
    border-radius: 18px;
    background: rgba(0,0,0,0.27);
    border: 1px solid rgba(255,255,255,0.09);
    color: #DEE7F6;
    line-height: 1.75;
    white-space: pre-wrap;
}

hr {
    border-color: rgba(255,255,255,0.08);
}

.stButton > button {
    width: 100%;
    border-radius: 16px;
    height: 48px;
    font-weight: 900;
    background: linear-gradient(135deg, #5A82FF, #27E2CA);
    color: #04101E;
    border: none;
}

.stButton > button:hover {
    filter: brightness(1.08);
    color: #04101E;
    border: none;
}

.stDownloadButton > button {
    border-radius: 14px;
    font-weight: 800;
}

.stSelectbox label, .stSlider label, .stTextInput label, .stCheckbox label {
    color: #DDE6F5 !important;
    font-weight: 800;
}

[data-testid="stMetric"] {
    padding: 15px;
    border-radius: 20px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
}

[data-testid="stMetricValue"] {
    color: #FFFFFF;
    font-weight: 900;
}

[data-testid="stMetricLabel"] {
    color: #9DA8BA;
}

.streamlit-expanderHeader {
    font-weight: 900;
    color: #FFFFFF;
}
</style>
""", unsafe_allow_html=True)


# =========================
# CONFIG
# =========================

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
    "Design Automation": "design automation ai content stars:>50",
    "Research Agents": "research agent ai deep research stars:>50",
    "Coding Agents": "coding agent ai developer stars:>500",
    "E-commerce Automation": "ecommerce automation ai product stars:>50",
    "Social Media Automation": "social media automation ai content stars:>50",
    "Data Analysis Agents": "data analysis ai agent dashboard stars:>50",
    "AI Search Engines": "ai search engine answer engine stars:>100",
    "Newsletter / Curation Tools": "newsletter curation ai content stars:>50",
    "No-Code AI Builders": "no code ai app builder stars:>100",
    "AI Productivity Tools": "ai productivity automation assistant stars:>100",
    "Prompt / Agent Ops": "prompt management agent ops ai stars:>50",
}

BUSINESS_FOCUSES = [
    "İçerik üretim sistemi",
    "Lead generation sistemi",
    "Ajans hizmeti",
    "Micro SaaS",
    "Yerel işletmelere satılacak sistem",
    "Creator / influencer aracı",
    "E-ticaret otomasyonu",
    "B2B operasyon otomasyonu",
    "X içerik araştırma sistemi",
    "AI eğitim / template ürünü",
]

WRITING_STYLES = [
    "Batın tarzı: samimi, net, hafif sokak dili, yapay zeka kokmayan",
    "Build in public: bugün denedim, şunu fark ettim",
    "Anti-hype: herkes yanlış yerden bakıyor",
    "İş fikri odaklı: bununla nasıl para kazanılır",
    "Tek kişilik medya şirketi: içerik fabrikası bakışı",
]


# =========================
# STATE
# =========================

if "results" not in st.session_state:
    st.session_state.results = []

if "last_run_at" not in st.session_state:
    st.session_state.last_run_at = None


# =========================
# HELPERS
# =========================

def safe_get(d, key, default="-"):
    return d.get(key, default) if isinstance(d, dict) else default


def decision_class(decision):
    text = str(decision).lower()
    if "paylaş" in text:
        return "decision-share"
    if "beklet" in text:
        return "decision-wait"
    return "decision-trash"


def radar_score(analysis):
    system = int(analysis.get("system_potential", 0) or 0)
    money = int(analysis.get("money_potential", 0) or 0)
    viral = int(analysis.get("virality", 0) or 0)
    mvp = int(analysis.get("mvp_speed", 0) or 0)
    difficulty = int(analysis.get("difficulty", 0) or 0)

    score = (system * 0.28) + (money * 0.28) + (viral * 0.22) + (mvp * 0.16) - (difficulty * 0.06)
    return round(score, 1)


def cache_key(repo, category, business_focus, writing_style):
    raw = f"{repo['name']}|{repo['description']}|{category}|{business_focus}|{writing_style}"
    return hashlib.md5(raw.encode()).hexdigest()


@st.cache_data(ttl=900)
def github_search(query, limit, sort_mode):
    url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": sort_mode,
        "order": "desc",
        "per_page": limit,
    }

    response = requests.get(
        url,
        params=params,
        headers={"Accept": "application/vnd.github+json"},
        timeout=20
    )

    data = response.json()

    if "message" in data and "items" not in data:
        return [], data["message"]

    repos = []

    for item in data.get("items", []):
        repos.append({
            "name": item["full_name"],
            "description": item.get("description") or "Açıklama yok",
            "stars": item.get("stargazers_count", 0),
            "url": item["html_url"],
            "language": item.get("language") or "Bilinmiyor",
            "updated_at": item.get("updated_at", "-"),
            "created_at": item.get("created_at", "-"),
            "forks": item.get("forks_count", 0),
            "issues": item.get("open_issues_count", 0),
            "watchers": item.get("watchers_count", 0),
        })

    return repos, None


def analyze_repo(repo, category, writing_style, business_focus):
    prompt = f"""
Aşağıdaki GitHub reposunu profesyonel ürün stratejisti gibi analiz et.

Repo: {repo["name"]}
Açıklama: {repo["description"]}
Yıldız: {repo["stars"]}
Fork: {repo["forks"]}
Açık issue: {repo["issues"]}
Dil: {repo["language"]}
Oluşturulma: {repo["created_at"]}
Güncellenme: {repo["updated_at"]}
Kategori: {category}
İş fikri odağı: {business_focus}
Link: {repo["url"]}
Yazı stili: {writing_style}

Senin görevin repo açıklamak değil.
Senin görevin bu repodan gerçek hayatta çalışabilecek iş fikri, sistem fikri ve içerik açısı çıkarmak.

Ana felsefe:
İnsanlar artık sadece içerik üretmek istemiyor.
İnsanlar kendileri için içerik, lead, araştırma, satış veya operasyon üreten makineler istiyor.

Her repo için profesyonelce düşün:
1. Bu repo gerçekten bir iş fırsatına dönüşebilir mi?
2. Hangi acıyı çözer?
3. Hangi müşteri para öder?
4. 1 günde MVP çıkar mı?
5. Hizmet olarak mı satılır, SaaS olarak mı, template olarak mı?
6. İlk para 30 gün içinde nasıl kazanılır?
7. X'te içerik olarak paylaşılır mı?
8. Zayıfsa neden zayıf?

Çok önemli kurallar:
- Abartma.
- Her repodan SaaS çıkarma.
- Eğer iş çıkmazsa net şekilde "Çöp" de.
- Fiyat aralığını gerçekçi ver.
- Türkiye'de uygulanabilecek örnek düşün.
- Kullanım senaryoları somut olsun.
- "Otomasyon yapılabilir" gibi boş cümle kurma.
- Sistemin input-process-output mantığını açıkla.
- X postları insan gibi yazılsın, yapay zeka kokmasın.
- X postları Batın'ın dilinde olsun: kısa, net, hafif sokak dili, fikir odaklı.

X post kuralları:
- "Bu repo..." diye başlama.
- "Yapay zeka dünyasında..." deme.
- Emoji, hashtag kullanma.
- Gereksiz cilalı yazma.
- Hook güçlü olsun.
- Araç değil fırsat sat.
- Hype değil farkındalık ver.
- En az bir postta "Twitter'a düştüğünde geç kalmış oluyorsunuz" fikrine yakın bir açı kullanılabilir.

Cevabı SADECE geçerli JSON olarak ver.
JSON dışında hiçbir şey yazma.

Format:
{{
  "share_decision": "Paylaş / Beklet / Çöp",
  "system_potential": 1,
  "money_potential": 1,
  "virality": 1,
  "difficulty": 1,
  "mvp_speed": 1,
  "short_verdict": "tek cümlelik net karar",
  "what_it_really_is": "repo aslında ne işe yarıyor, sade açıklama",
  "why_interesting": "bu repoyu ilginç yapan şey",
  "real_business_idea": {{
    "name": "iş fikrinin adı",
    "one_liner": "tek cümlelik iş fikri",
    "target_customer": "kim satın alır",
    "pain": "hangi acıyı çözer",
    "offer": "müşteriye satılacak net teklif",
    "price_range": "tahmini fiyat",
    "delivery_model": "done-for-you / template / SaaS / danışmanlık / eğitim"
  }},
  "working_system_blueprint": {{
    "system_name": "kurulacak sistemin adı",
    "input": "sisteme ne girer",
    "process": ["adım 1", "adım 2", "adım 3", "adım 4", "adım 5"],
    "output": "sistem ne üretir",
    "tools_needed": ["araç 1", "araç 2", "araç 3"],
    "first_mvp": "1 günde yapılabilecek ilk basit versiyon"
  }},
  "use_cases": [
    {{"scenario": "kullanım senaryosu 1", "user": "kim kullanır", "example": "somut örnek"}},
    {{"scenario": "kullanım senaryosu 2", "user": "kim kullanır", "example": "somut örnek"}},
    {{"scenario": "kullanım senaryosu 3", "user": "kim kullanır", "example": "somut örnek"}}
  ],
  "first_customer": {{
    "who": "ilk müşteri tipi",
    "where_to_find": "nereden bulunur",
    "outreach_message": "çok kısa Türkçe satış mesajı"
  }},
  "risk": "bu fikrin riski",
  "setup_difficulty_reason": "kurulum neden kolay/zor",
  "content_angles": ["içerik açısı 1", "içerik açısı 2", "içerik açısı 3", "içerik açısı 4", "içerik açısı 5"],
  "x_post_1": "kişisel keşif gibi yazılmış kısa X postu",
  "x_post_2": "anti-hype açıyla yazılmış kısa X postu",
  "x_post_3": "iş fikri / sistem kurma açısından yazılmış kısa X postu"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "Sen OOOtomasyon için çalışan gerçekçi bir AI sistemleri ve internet iş modeli stratejistisin. Jenerik AI dili kullanmazsın. Gerektiğinde sertçe 'bu çöp' dersin."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.62
    )

    text = response.choices[0].message.content

    try:
        return json.loads(text)
    except Exception:
        return {
            "share_decision": "Hata",
            "system_potential": 0,
            "money_potential": 0,
            "virality": 0,
            "difficulty": 0,
            "mvp_speed": 0,
            "short_verdict": "JSON parse edilemedi.",
            "what_it_really_is": text,
            "why_interesting": "-",
            "real_business_idea": {},
            "working_system_blueprint": {},
            "use_cases": [],
            "first_customer": {},
            "risk": "-",
            "setup_difficulty_reason": "-",
            "content_angles": [],
            "x_post_1": "-",
            "x_post_2": "-",
            "x_post_3": "-",
        }


def flatten_results(results):
    rows = []
    for item in results:
        repo = item["repo"]
        analysis = item["analysis"]
        business = analysis.get("real_business_idea", {})
        blueprint = analysis.get("working_system_blueprint", {})

        rows.append({
            "radar_score": item.get("radar_score", 0),
            "repo": repo.get("name", ""),
            "url": repo.get("url", ""),
            "description": repo.get("description", ""),
            "stars": repo.get("stars", 0),
            "language": repo.get("language", ""),
            "decision": analysis.get("share_decision", ""),
            "system": analysis.get("system_potential", 0),
            "money": analysis.get("money_potential", 0),
            "viral": analysis.get("virality", 0),
            "difficulty": analysis.get("difficulty", 0),
            "mvp_speed": analysis.get("mvp_speed", 0),
            "verdict": analysis.get("short_verdict", ""),
            "business_name": business.get("name", ""),
            "offer": business.get("offer", ""),
            "price": business.get("price_range", ""),
            "system_name": blueprint.get("system_name", ""),
            "x_post_1": analysis.get("x_post_1", ""),
            "x_post_2": analysis.get("x_post_2", ""),
            "x_post_3": analysis.get("x_post_3", ""),
        })

    return pd.DataFrame(rows)


# =========================
# SIDEBAR
# =========================

with st.sidebar:
    st.markdown("## OOO Radar Controls")

    category = st.selectbox("Radar modu", list(RADAR_MODES.keys()))

    business_focus = st.selectbox("İş fikri odağı", BUSINESS_FOCUSES)

    writing_style = st.selectbox("X yazı stili", WRITING_STYLES)

    sort_mode_label = st.selectbox(
        "GitHub sıralama",
        ["Güncel güncellenenler", "En çok yıldız", "En çok fork"]
    )

    sort_map = {
        "Güncel güncellenenler": "updated",
        "En çok yıldız": "stars",
        "En çok fork": "forks",
    }

    limit = st.slider("Repo sayısı", 3, 30, 8)

    min_score_filter = st.slider("Minimum Radar Score", 0.0, 10.0, 0.0, 0.5)

    only_share = st.checkbox("Sadece paylaşılabilirleri göster", value=False)

    custom_query = st.text_input(
        "Özel GitHub araması",
        placeholder="Örn: ai content machine stars:>100"
    )

    run = st.button("Radar'ı Çalıştır")

    if st.session_state.results:
        st.markdown("---")
        st.markdown("### Export")
        df_export = flatten_results(st.session_state.results)

        st.download_button(
            "CSV indir",
            df_export.to_csv(index=False).encode("utf-8-sig"),
            file_name="oootomasyon_radar.csv",
            mime="text/csv"
        )

        st.download_button(
            "JSON indir",
            json.dumps(st.session_state.results, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name="oootomasyon_radar.json",
            mime="application/json"
        )


# =========================
# HERO
# =========================

st.markdown("""
<div class="hero">
    <div class="hero-badge">OOOTOMASYON RADAR</div>
    <div class="hero-title">GitHub'daki fırsatları iş fikrine çevir.</div>
    <div class="hero-subtitle">
        Yeni AI projelerini tarar. Potansiyelli repoları filtreler.
        Her projeden gerçek iş fikri, sistem blueprint’i, ilk müşteri, satış mesajı ve X içeriği çıkarır.
    </div>
</div>
""", unsafe_allow_html=True)


# =========================
# RUN
# =========================

if run:
    query = custom_query.strip() if custom_query.strip() else RADAR_MODES[category]
    repos, error = github_search(query, limit, sort_map[sort_mode_label])

    if error:
        st.error(error)
    elif not repos:
        st.warning("Repo bulunamadı.")
    else:
        st.session_state.results = []
        progress = st.progress(0)
        status = st.empty()

        for index, repo in enumerate(repos):
            status.write(f"Analiz ediliyor: {repo['name']}")

            try:
                analysis = analyze_repo(repo, category, writing_style, business_focus)
                score = radar_score(analysis)

                st.session_state.results.append({
                    "repo": repo,
                    "analysis": analysis,
                    "radar_score": score,
                    "analyzed_at": datetime.now().isoformat()
                })

                time.sleep(0.2)
                progress.progress((index + 1) / len(repos))

            except Exception as e:
                st.error(f"{repo['name']} analiz edilirken hata oluştu: {e}")

        st.session_state.last_run_at = datetime.now().strftime("%d.%m.%Y %H:%M")
        status.write("Analiz tamamlandı.")


# =========================
# SUMMARY
# =========================

results = st.session_state.results

if results:
    filtered = []

    for item in results:
        decision = item["analysis"].get("share_decision", "")
        score = item.get("radar_score", 0)

        if score < min_score_filter:
            continue

        if only_share and "paylaş" not in str(decision).lower():
            continue

        filtered.append(item)

    filtered = sorted(filtered, key=lambda x: x.get("radar_score", 0), reverse=True)

    top_count = len(filtered)
    share_count = sum(1 for x in filtered if "paylaş" in str(x["analysis"].get("share_decision", "")).lower())
    avg_score = round(sum(x["radar_score"] for x in filtered) / max(len(filtered), 1), 1)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bulunan fırsat", top_count)
    c2.metric("Paylaşılabilir", share_count)
    c3.metric("Ortalama skor", avg_score)
    c4.metric("Son tarama", st.session_state.last_run_at or "-")

    st.divider()

    df = flatten_results(filtered)
    with st.expander("Radar tablosu"):
        st.dataframe(
            df[[
                "radar_score", "repo", "decision", "system", "money", "viral",
                "difficulty", "mvp_speed", "business_name", "offer"
            ]],
            use_container_width=True
        )

    # =========================
    # CARDS
    # =========================

    for item in filtered:
        repo = item["repo"]
        analysis = item["analysis"]
        business = analysis.get("real_business_idea", {})
        blueprint = analysis.get("working_system_blueprint", {})
        first_customer = analysis.get("first_customer", {})
        score = item.get("radar_score", 0)
        decision = analysis.get("share_decision", "-")

        st.markdown('<div class="premium-card">', unsafe_allow_html=True)

        left, right = st.columns([3.4, 1])

        with left:
            st.markdown(f'<div class="repo-title">{repo["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="repo-desc">{repo["description"]}</div>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <span class="tag">Radar Score {score}/10</span>
                <span class="tag">⭐ {repo['stars']}</span>
                <span class="tag">Fork {repo['forks']}</span>
                <span class="tag">{repo['language']}</span>
                <span class="tag">Issues {repo['issues']}</span>
                """,
                unsafe_allow_html=True
            )

        with right:
            st.markdown(
                f'<div class="{decision_class(decision)}">{decision}</div>',
                unsafe_allow_html=True
            )
            st.link_button("GitHub'da Aç", repo["url"])

        st.divider()

        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Radar", score)
        m2.metric("Sistem", analysis.get("system_potential", 0))
        m3.metric("Para", analysis.get("money_potential", 0))
        m4.metric("Viral", analysis.get("virality", 0))
        m5.metric("Zorluk", analysis.get("difficulty", 0))
        m6.metric("MVP Hızı", analysis.get("mvp_speed", 0))

        st.markdown('<div class="section-title">Net karar</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="body-text">{analysis.get("short_verdict", "-")}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Aslında ne?</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="body-text">{analysis.get("what_it_really_is", "-")}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Neden ilginç?</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="body-text">{analysis.get("why_interesting", "-")}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Gerçek iş fikri</div>', unsafe_allow_html=True)

        b1, b2, b3 = st.columns(3)
        with b1:
            st.markdown('<div class="mini-panel">', unsafe_allow_html=True)
            st.markdown("**İsim**")
            st.write(safe_get(business, "name"))
            st.markdown("**Tek cümle**")
            st.write(safe_get(business, "one_liner"))
            st.markdown('</div>', unsafe_allow_html=True)

        with b2:
            st.markdown('<div class="mini-panel">', unsafe_allow_html=True)
            st.markdown("**Hedef müşteri**")
            st.write(safe_get(business, "target_customer"))
            st.markdown("**Acı**")
            st.write(safe_get(business, "pain"))
            st.markdown('</div>', unsafe_allow_html=True)

        with b3:
            st.markdown('<div class="mini-panel">', unsafe_allow_html=True)
            st.markdown("**Teklif**")
            st.write(safe_get(business, "offer"))
            st.markdown("**Fiyat / Model**")
            st.write(safe_get(business, "price_range"))
            st.write(safe_get(business, "delivery_model"))
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Çalışan sistem blueprint</div>', unsafe_allow_html=True)

        s1, s2 = st.columns([1, 1])
        with s1:
            st.markdown('<div class="mini-panel">', unsafe_allow_html=True)
            st.markdown("**Sistem adı**")
            st.write(safe_get(blueprint, "system_name"))
            st.markdown("**Input**")
            st.write(safe_get(blueprint, "input"))
            st.markdown("**Output**")
            st.write(safe_get(blueprint, "output"))
            st.markdown("**İlk MVP**")
            st.write(safe_get(blueprint, "first_mvp"))
            st.markdown('</div>', unsafe_allow_html=True)

        with s2:
            st.markdown('<div class="mini-panel">', unsafe_allow_html=True)
            st.markdown("**Süreç**")
            for step in blueprint.get("process", []):
                st.write(f"• {step}")

            st.markdown("**Gerekli araçlar**")
            for tool in blueprint.get("tools_needed", []):
                st.write(f"• {tool}")
            st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("Kullanım senaryoları"):
            for case in analysis.get("use_cases", []):
                st.markdown(f"**{case.get('scenario', '-')}**")
                st.write(f"Kim kullanır: {case.get('user', '-')}")
                st.write(f"Örnek: {case.get('example', '-')}")
                st.divider()

        with st.expander("İlk müşteri ve satış"):
            st.write("İlk müşteri:", first_customer.get("who", "-"))
            st.write("Nereden bulunur:", first_customer.get("where_to_find", "-"))
            st.code(first_customer.get("outreach_message", "-"))

        with st.expander("Risk ve kurulum"):
            st.write("Risk:", analysis.get("risk", "-"))
            st.write("Kurulum:", analysis.get("setup_difficulty_reason", "-"))

        with st.expander("İçerik açıları"):
            for idea in analysis.get("content_angles", []):
                st.write(f"• {idea}")

        with st.expander("X postları"):
            st.markdown("### Varyasyon 1 — Kişisel")
            st.markdown(f'<div class="post-box">{analysis.get("x_post_1", "-")}</div>', unsafe_allow_html=True)
            st.code(analysis.get("x_post_1", "-"))

            st.markdown("### Varyasyon 2 — Anti-hype")
            st.markdown(f'<div class="post-box">{analysis.get("x_post_2", "-")}</div>', unsafe_allow_html=True)
            st.code(analysis.get("x_post_2", "-"))

            st.markdown("### Varyasyon 3 — İş fikri")
            st.markdown(f'<div class="post-box">{analysis.get("x_post_3", "-")}</div>', unsafe_allow_html=True)
            st.code(analysis.get("x_post_3", "-"))

        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Sol menüden radar modunu seçip OOOtomasyon Radar'ı çalıştır.")