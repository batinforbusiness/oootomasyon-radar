import os
import json
import time
from datetime import datetime
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="OOOtomasyon Radar", page_icon="🛰️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background:
        radial-gradient(circle at top left, rgba(34,90,255,.22), transparent 30%),
        radial-gradient(circle at top right, rgba(0,255,209,.10), transparent 28%),
        linear-gradient(180deg,#050711 0%,#080D19 45%,#060914 100%);
    color:#F7F9FC;
}
.block-container { padding-top:2rem; padding-bottom:5rem; max-width:1500px; }
[data-testid="stSidebar"] { background:rgba(7,11,24,.88); border-right:1px solid rgba(255,255,255,.08); }
h1,h2,h3 { letter-spacing:-.045em; }
.hero {
    padding:34px 38px; border:1px solid rgba(255,255,255,.10); border-radius:30px;
    background:linear-gradient(135deg,rgba(255,255,255,.105),rgba(255,255,255,.035));
    box-shadow:0 28px 90px rgba(0,0,0,.35); margin-bottom:24px;
}
.hero-badge {
    display:inline-flex; padding:7px 12px; border-radius:999px;
    background:rgba(78,124,255,.16); color:#BFD0FF; font-size:13px; font-weight:800;
    border:1px solid rgba(78,124,255,.30); margin-bottom:16px;
}
.hero-title { font-size:48px; line-height:1.02; font-weight:900; margin-bottom:14px; color:white; }
.hero-subtitle { font-size:17px; line-height:1.65; color:#AEB8CA; max-width:920px; }
.card {
    padding:26px; border-radius:28px;
    background:linear-gradient(135deg,rgba(255,255,255,.075),rgba(255,255,255,.035));
    border:1px solid rgba(255,255,255,.10); box-shadow:0 24px 80px rgba(0,0,0,.28);
    margin-bottom:24px;
}
.title { font-size:25px; font-weight:900; color:white; letter-spacing:-.04em; margin-bottom:6px; }
.desc { color:#AEB8CA; font-size:14px; line-height:1.6; margin-bottom:14px; }
.tag {
    display:inline-flex; padding:6px 10px; border-radius:999px; background:rgba(255,255,255,.07);
    color:#DEE7F6; font-size:12px; font-weight:700; margin-right:7px; margin-bottom:7px;
    border:1px solid rgba(255,255,255,.09);
}
.section { color:white; font-size:15px; font-weight:900; margin-top:18px; margin-bottom:8px; }
.panel {
    padding:17px; border-radius:20px; background:rgba(0,0,0,.20);
    border:1px solid rgba(255,255,255,.08); height:100%;
}
.post {
    padding:18px; border-radius:18px; background:rgba(0,0,0,.27);
    border:1px solid rgba(255,255,255,.09); color:#DEE7F6; line-height:1.75; white-space:pre-wrap;
}
.stButton > button {
    width:100%; border-radius:16px; height:48px; font-weight:900;
    background:linear-gradient(135deg,#5A82FF,#27E2CA); color:#04101E; border:none;
}
.stButton > button:hover { filter:brightness(1.08); color:#04101E; border:none; }
.stSelectbox label,.stSlider label,.stTextInput label,.stTextArea label,.stNumberInput label,.stCheckbox label {
    color:#DDE6F5!important; font-weight:800;
}
[data-testid="stMetric"] {
    padding:15px; border-radius:20px; background:rgba(255,255,255,.05);
    border:1px solid rgba(255,255,255,.08);
}
[data-testid="stMetricValue"] { color:white; font-weight:900; }
[data-testid="stMetricLabel"] { color:#9DA8BA; }
</style>
""", unsafe_allow_html=True)

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

if "radar_results" not in st.session_state:
    st.session_state.radar_results = []
if "founder_result" not in st.session_state:
    st.session_state.founder_result = None
if "opportunity_result" not in st.session_state:
    st.session_state.opportunity_result = None

def safe_json(text):
    try:
        return json.loads(text)
    except Exception:
        cleaned = text.strip().replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return {"error": text}

def call_ai(prompt, system="Sen gerçekçi bir AI iş modeli stratejistisin. Jenerik konuşmazsın. Türkçe yazarsın."):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        temperature=0.62,
    )
    return safe_json(response.choices[0].message.content)

def github_search(query, limit, sort):
    url = "https://api.github.com/search/repositories"
    params = {"q": query, "sort": sort, "order": "desc", "per_page": limit}
    r = requests.get(url, params=params, headers={"Accept": "application/vnd.github+json"}, timeout=20)
    data = r.json()
    if "items" not in data:
        return [], data.get("message", "GitHub API hatası")
    repos = []
    for item in data["items"]:
        repos.append({
            "name": item["full_name"],
            "description": item.get("description") or "Açıklama yok",
            "stars": item.get("stargazers_count", 0),
            "forks": item.get("forks_count", 0),
            "issues": item.get("open_issues_count", 0),
            "language": item.get("language") or "Bilinmiyor",
            "url": item["html_url"],
            "updated_at": item.get("updated_at", "-"),
            "created_at": item.get("created_at", "-"),
        })
    return repos, None

def score(a):
    return round(
        int(a.get("system_potential", 0))*0.22 +
        int(a.get("money_potential", 0))*0.24 +
        int(a.get("virality", 0))*0.18 +
        int(a.get("market_timing", 0))*0.16 +
        int(a.get("ease_of_sale", 0))*0.14 -
        int(a.get("difficulty", 0))*0.06, 1
    )

def analyze_repo(repo, focus):
    prompt = f"""
Repoyu fırsat olarak analiz et.

Repo: {repo}
Odak: {focus}

Repo açıklaması yapma. Gerçek hayatta neye dönüşür onu çıkar.
Cevabı SADECE JSON ver.

Format:
{{
 "share_decision":"Paylaş / Beklet / Çöp",
 "system_potential":1,
 "money_potential":1,
 "virality":1,
 "difficulty":1,
 "market_timing":1,
 "ease_of_sale":1,
 "demand":1,
 "competition":1,
 "short_verdict":"net karar",
 "what_it_really_is":"sade açıklama",
 "opportunity_summary":"fırsat özeti",
 "what_to_sell":"bununla satılacak net şey",
 "who_buys":"kim satın alır",
 "price_range":"fiyat aralığı",
 "first_customer":"ilk müşteri tipi",
 "first_customer_source":"nereden bulunur",
 "first_outreach_message":"kısa satış mesajı",
 "30_day_money_plan":["hafta 1","hafta 2","hafta 3","hafta 4"],
 "system_blueprint":{{"input":"", "process":["adım 1","adım 2","adım 3","adım 4"], "output":"", "mvp":"1 günlük MVP"}},
 "use_cases":[{{"scenario":"", "example":""}}, {{"scenario":"", "example":""}}, {{"scenario":"", "example":""}}],
 "risks":"risk",
 "content_angles":["açı 1","açı 2","açı 3","açı 4","açı 5"],
 "x_post_1":"insan gibi, kısa X postu",
 "x_post_2":"anti-hype X postu",
 "x_post_3":"iş fikri odaklı X postu"
}}
"""
    return call_ai(prompt, "Sen OOOtomasyon Radar için çalışan gerçekçi ürün ve fırsat analistisin. Gerektiğinde 'çöp' dersin.")

def founder_os(profile):
    prompt = f"""
Bu founder profiline göre 5 uygulanabilir iş modeli çıkar.

Profil:
{profile}

Motivasyon konuşması yapma. İlk para, ilk müşteri ve uygulanabilirlik odaklı ol.
Cevabı SADECE JSON ver.

Format:
{{
 "positioning":"piyasada nasıl konumlanmalı",
 "main_warning":"en büyük hata riski",
 "best_bet":"en mantıklı ana yön",
 "90_day_strategy":"90 günlük strateji",
 "first_thing_to_build":{{"name":"","why":"","mvp":"","sell_before_building":""}},
 "business_ideas":[
  {{
   "rank":1,
   "name":"",
   "one_liner":"",
   "why_fit":"",
   "target_customer":"",
   "pain":"",
   "offer":"",
   "price_range":"",
   "delivery_model":"",
   "first_customer_source":"",
   "outreach_message":"",
   "first_7_days":["","",""],
   "first_30_days":["hafta 1","hafta 2","hafta 3","hafta 4"],
   "content_strategy":["","",""],
   "risks":"",
   "score":1
  }}
 ],
 "x_content_plan":{{"positioning_line":"","next_10_posts":["","","","","","","","","",""]}}
}}
"""
    return call_ai(prompt, "Sen acımasız ama faydalı bir internet iş modeli stratejistisin.")

def opportunity_engine(idea):
    prompt = f"""
Aşağıdaki fikri Opportunity Engine gibi analiz et.

Fikir / repo / trend:
{idea}

Cevabı SADECE JSON ver.

Format:
{{
 "is_real_opportunity":"Evet / Hayır / Şüpheli",
 "opportunity_score":1,
 "what_to_sell":"bununla ne satılır",
 "who_buys":"kim satın alır",
 "why_now":"neden şimdi",
 "pricing":"kaça satılır",
 "first_customer":"ilk müşteri kim",
 "first_customer_source":"nereden bulunur",
 "first_sale_script":"ilk satış mesajı",
 "30_day_plan":["hafta 1","hafta 2","hafta 3","hafta 4"],
 "mvp":"en basit çalışan versiyon",
 "risks":"riskler",
 "content_strategy":["post 1","post 2","post 3","post 4","post 5"],
 "verdict":"net karar"
}}
"""
    return call_ai(prompt)

def render_list(items):
    for item in items or []:
        st.write(f"• {item}")

def render_post(label, text):
    st.markdown(f"### {label}")
    st.markdown(f'<div class="post">{text}</div>', unsafe_allow_html=True)
    st.code(text)

mode = st.sidebar.radio("Mod", ["Repo Radar", "Opportunity Engine", "Founder OS"])

st.markdown("""
<div class="hero">
    <div class="hero-badge">OOOTOMASYON RADAR</div>
    <div class="hero-title">Fırsatları erken gör. Sisteme çevir. Satılabilir hale getir.</div>
    <div class="hero-subtitle">
        Repo Radar, Opportunity Engine ve Founder OS tek panelde. Yeni teknolojileri tarar,
        iş fikrine dönüştürür, ilk müşteri ve 30 günlük para planı çıkarır.
    </div>
</div>
""", unsafe_allow_html=True)

if mode == "Repo Radar":
    with st.sidebar:
        category = st.selectbox("Radar modu", list(RADAR_MODES.keys()))
        focus = st.selectbox("İş odağı", ["İçerik üretim sistemi", "Lead generation", "Ajans hizmeti", "Micro SaaS", "Yerel işletme sistemi", "Creator aracı", "E-ticaret otomasyonu"])
        sort_label = st.selectbox("Sıralama", ["Güncel", "Yıldız", "Fork"])
        sort_map = {"Güncel": "updated", "Yıldız": "stars", "Fork": "forks"}
        limit = st.slider("Repo sayısı", 3, 20, 6)
        custom_query = st.text_input("Özel GitHub query")
        run = st.button("Radar'ı Çalıştır")

    if run:
        q = custom_query.strip() or RADAR_MODES[category]
        repos, err = github_search(q, limit, sort_map[sort_label])
        if err:
            st.error(err)
        else:
            st.session_state.radar_results = []
            progress = st.progress(0)
            for i, repo in enumerate(repos):
                st.write(f"Analiz ediliyor: {repo['name']}")
                a = analyze_repo(repo, focus)
                a["ooo_score"] = score(a)
                st.session_state.radar_results.append({"repo": repo, "analysis": a})
                progress.progress((i+1)/len(repos))
                time.sleep(0.15)

    results = sorted(st.session_state.radar_results, key=lambda x: x["analysis"].get("ooo_score", 0), reverse=True)

    if results:
        df = pd.DataFrame([{
            "score": r["analysis"].get("ooo_score"),
            "repo": r["repo"]["name"],
            "decision": r["analysis"].get("share_decision"),
            "sell": r["analysis"].get("what_to_sell"),
            "buyer": r["analysis"].get("who_buys"),
            "price": r["analysis"].get("price_range"),
            "url": r["repo"]["url"],
        } for r in results])
        st.dataframe(df, use_container_width=True)
        st.download_button("CSV indir", df.to_csv(index=False).encode("utf-8-sig"), "oootomasyon_radar.csv", "text/csv")

        for r in results:
            repo, a = r["repo"], r["analysis"]
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f'<div class="title">{repo["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="desc">{repo["description"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<span class="tag">OOO Score {a.get("ooo_score")}/10</span><span class="tag">⭐ {repo["stars"]}</span><span class="tag">{repo["language"]}</span><span class="tag">{a.get("share_decision")}</span>', unsafe_allow_html=True)
            st.link_button("GitHub'da Aç", repo["url"])

            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("Para", a.get("money_potential", 0))
            c2.metric("Sistem", a.get("system_potential", 0))
            c3.metric("Viral", a.get("virality", 0))
            c4.metric("Timing", a.get("market_timing", 0))
            c5.metric("Zorluk", a.get("difficulty", 0))

            st.markdown('<div class="section">Net karar</div>', unsafe_allow_html=True)
            st.write(a.get("short_verdict", "-"))

            c1,c2,c3 = st.columns(3)
            with c1:
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                st.markdown("**Ne satılır?**")
                st.write(a.get("what_to_sell", "-"))
                st.markdown("**Kaça?**")
                st.write(a.get("price_range", "-"))
                st.markdown("</div>", unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                st.markdown("**Kim satın alır?**")
                st.write(a.get("who_buys", "-"))
                st.markdown("**İlk müşteri**")
                st.write(a.get("first_customer", "-"))
                st.markdown("</div>", unsafe_allow_html=True)
            with c3:
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                st.markdown("**Nereden bulunur?**")
                st.write(a.get("first_customer_source", "-"))
                st.markdown("**Risk**")
                st.write(a.get("risks", "-"))
                st.markdown("</div>", unsafe_allow_html=True)

            with st.expander("30 günlük para planı"):
                render_list(a.get("30_day_money_plan"))
            with st.expander("Sistem blueprint"):
                bp = a.get("system_blueprint", {})
                st.write("Input:", bp.get("input", "-"))
                render_list(bp.get("process"))
                st.write("Output:", bp.get("output", "-"))
                st.write("MVP:", bp.get("mvp", "-"))
            with st.expander("Kullanım senaryoları"):
                for u in a.get("use_cases", []):
                    st.write(f"**{u.get('scenario','-')}** — {u.get('example','-')}")
            with st.expander("İçerik açıları"):
                render_list(a.get("content_angles"))
            with st.expander("X postları"):
                render_post("Kişisel", a.get("x_post_1", "-"))
                render_post("Anti-hype", a.get("x_post_2", "-"))
                render_post("İş fikri", a.get("x_post_3", "-"))
            st.markdown("</div>", unsafe_allow_html=True)

elif mode == "Opportunity Engine":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">Opportunity Engine</div>', unsafe_allow_html=True)
    idea = st.text_area("Fikir, repo, trend veya araç yaz", height=160, placeholder="Örn: Browser-use ile yerel işletmeler için otomatik rakip analizi sistemi...")
    if st.button("Fırsatı Analiz Et"):
        with st.spinner("Fırsat analiz ediliyor..."):
            st.session_state.opportunity_result = opportunity_engine(idea)
    st.markdown("</div>", unsafe_allow_html=True)

    o = st.session_state.opportunity_result
    if o:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        c1,c2 = st.columns([1,3])
        c1.metric("Opportunity Score", o.get("opportunity_score", 0))
        c2.write(o.get("verdict", "-"))
        c1,c2,c3 = st.columns(3)
        c1.write("**Ne satılır?**"); c1.write(o.get("what_to_sell", "-"))
        c2.write("**Kim satın alır?**"); c2.write(o.get("who_buys", "-"))
        c3.write("**Fiyat**"); c3.write(o.get("pricing", "-"))
        st.write("**Neden şimdi?**", o.get("why_now", "-"))
        st.write("**İlk müşteri:**", o.get("first_customer", "-"))
        st.write("**Nereden bulunur:**", o.get("first_customer_source", "-"))
        st.code(o.get("first_sale_script", "-"))
        with st.expander("30 günlük plan"):
            render_list(o.get("30_day_plan"))
        with st.expander("İçerik stratejisi"):
            render_list(o.get("content_strategy"))
        st.write("**MVP:**", o.get("mvp", "-"))
        st.write("**Risk:**", o.get("risks", "-"))
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">Founder OS</div>', unsafe_allow_html=True)
    with st.form("founder"):
        c1,c2 = st.columns(2)
        with c1:
            followers = st.number_input("Takipçi", min_value=0, value=11000)
            audience = st.text_input("Kitle", value="Yapay zeka, otomasyon, internetten para kazanma")
            skills = st.text_area("Yetenekler", value="n8n, AI otomasyon, içerik üretimi, X büyütme, basit Python/Streamlit")
            assets = st.text_area("Varlıklar", value="11k X hesabı, OOOtomasyon markası, AI kitlesi, daha önce satılmış şablonlar")
        with c2:
            budget = st.text_input("Bütçe", value="500-1000$")
            weekly_hours = st.text_input("Haftalık süre", value="20 saat")
            income_goal = st.text_input("Hedef gelir", value="İlk 30-60 günde ilk satış, sonra aylık 3000-10000$")
            dislikes = st.text_area("Sevmediğin işler", value="Soğuk satış, çok teknik SaaS, uzun süre sonuç vermeyen işler")
        notes = st.text_area("Ek not", value="Kısa yoldan gerçek para kazandıracak, içerik ile satılabilecek iş modelleri istiyorum.")
        submitted = st.form_submit_button("Bana İş Kur")
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        profile = {
            "followers": followers, "audience": audience, "skills": skills, "assets": assets,
            "budget": budget, "weekly_hours": weekly_hours, "income_goal": income_goal,
            "dislikes": dislikes, "notes": notes
        }
        with st.spinner("Founder OS çalışıyor..."):
            st.session_state.founder_result = founder_os(profile)

    f = st.session_state.founder_result
    if f:
        if "error" in f:
            st.error("JSON parse hatası")
            st.write(f["error"])
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="title">Konumlanma</div>', unsafe_allow_html=True)
            st.write(f.get("positioning", "-"))
            st.write("**Ana uyarı:**", f.get("main_warning", "-"))
            st.write("**En mantıklı yön:**", f.get("best_bet", "-"))
            st.write("**90 gün:**", f.get("90_day_strategy", "-"))
            st.markdown("</div>", unsafe_allow_html=True)

            build = f.get("first_thing_to_build", {})
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="title">İlk Yapılacak Şey</div>', unsafe_allow_html=True)
            st.write("**İsim:**", build.get("name", "-"))
            st.write("**Neden:**", build.get("why", "-"))
            st.write("**MVP:**", build.get("mvp", "-"))
            st.write("**Önce satma testi:**", build.get("sell_before_building", "-"))
            st.markdown("</div>", unsafe_allow_html=True)

            for idea in f.get("business_ideas", []):
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f'<div class="title">#{idea.get("rank")} — {idea.get("name")}</div>', unsafe_allow_html=True)
                st.write(idea.get("one_liner", "-"))
                c1,c2,c3 = st.columns(3)
                c1.metric("Skor", idea.get("score", 0))
                c1.write("**Hedef müşteri**"); c1.write(idea.get("target_customer", "-"))
                c2.write("**Teklif**"); c2.write(idea.get("offer", "-"))
                c2.write("**Fiyat**"); c2.write(idea.get("price_range", "-"))
                c3.write("**İlk müşteri kaynağı**"); c3.write(idea.get("first_customer_source", "-"))
                c3.code(idea.get("outreach_message", "-"))
                with st.expander("İlk 7 gün"):
                    render_list(idea.get("first_7_days"))
                with st.expander("İlk 30 gün"):
                    render_list(idea.get("first_30_days"))
                with st.expander("İçerik stratejisi"):
                    render_list(idea.get("content_strategy"))
                st.write("**Risk:**", idea.get("risks", "-"))
                st.markdown("</div>", unsafe_allow_html=True)

            xp = f.get("x_content_plan", {})
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="title">X İçerik Planı</div>', unsafe_allow_html=True)
            st.write("**Konumlanma:**", xp.get("positioning_line", "-"))
            render_list(xp.get("next_10_posts"))
            st.markdown("</div>", unsafe_allow_html=True)
