import streamlit as st
import time
import json
import os
# Resmi en güncel Google GenAI SDK kütüphanesi
from google import genai
from google.genai import types

# ==========================================
# 1. INITIAL SESSION STATE SETUP
# ==========================================
if "screen" not in st.session_state:
    st.session_state.screen = "input"  # input, quiz, results, summary
if "gece_modu" not in st.session_state:
    st.session_state.gece_modu = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "current_question_idx" not in st.session_state:
    st.session_state.current_question_idx = 0
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}  # {question_idx: choice_letter}
if "generated_quiz" not in st.session_state:
    st.session_state.generated_quiz = []
if "generated_summary" not in st.session_state:
    st.session_state.generated_summary = ""
if "active_topic" not in st.session_state:
    st.session_state.active_topic = ""

# ==========================================
# 2. GERÇEK GEMINI API ENTEGRASYONU
# ==========================================
def call_gemini_api(prompt_type, input_data, difficulty="Orta", question_count=20):
    """
    Canlı Google Gemini modeline bağlanır.
    İstediğin adet kadar (Sınırsız Soru Desteği) tamamen özgün ÖSYM formatında soru üretir.
    """
    # API Anahtarını almanın güvenli ve çoklu yöntemi
    api_key = None
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        st.error("⚠️ HATA: API Anahtarı bulunamadı! Lütfen Replit'te 'Secrets' kısmına GEMINI_API_KEY ekleyin.")
        st.stop()
        
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"İstemci başlatılamadı, API anahtarınızı kontrol edin: {e}")
        st.stop()

    system_instruction = (
        "Sen uzman bir KPSS ve ÖSYM soru hazırlama komisyonu üyesisin. "
        "Girdi olarak verilen konularda içerik üretirken akademik titizlikle yaklaşmalı, "
        "ÖSYM'nin mantığını referans almalısın. Asla birbirini tekrar eden kalıplar kullanma."
    )
    
    model_name = "gemini-2.5-flash"

    if prompt_type == "quiz":
        quiz_prompt = f"""
        '{input_data}' konusu hakkında, {difficulty} zorluk seviyesinde, KPSS formatına uygun, 
        tam {question_count} adet test sorusu hazırla. Her soru kesinlikle 5 seçenekli olmalıdır.
        
        Senden çıktıyı sadece ham bir JSON listesi olarak istiyorum. Asla markdown ekleme:
        [
          {{
            "id": 1,
            "soru": "Soru metni...",
            "secenekler": {{"A": "Seçenek 1", "B": "Seçenek 2", "C": "Seçenek 3", "D": "Seçenek 4", "E": "Seçenek 5"}},
            "dogru_cevap": "C",
            "ipucu": "İpucu metni...",
            "aciklama": "Çözüm..."
          }}
        ]
        """
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=quiz_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            st.error(f"Yapay zeka soru üretirken hata oluştu: {e}")
            return []
        
    elif prompt_type == "summary":
        summary_prompt = f"""
        '{input_data}' konusu hakkında KPSS sınavına hazırlanan bir adayın mutlaka bilmesi gereken 
        detaylı ve taktiksel bir ders özeti hazırla. Markdown formatı kullan.
        """
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=summary_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3
                )
            )
            return response.text
        except Exception as e:
            st.error(f"Yapay zeka özet üretirken hata oluştu: {e}")
            return "Özet oluşturulamadı."

# ==========================================
# 3. GLOBAL THEME DESIGN & CUSTOM CSS
# ==========================================
def inject_theme():
    # Gece ve Gündüz modları için net ve zıt renk tanımları
    if st.session_state.gece_modu:
        bg_main = "#121212"
        bg_sidebar = "#1E1E1E"
        text_color = "#FFFFFF"
        box_bg = "#2D2D2D"
        box_text = "#FFFFFF"
        accent_color = "#BB86FC"
    else:
        bg_main = "#FFFFFF"
        bg_sidebar = "#F0F2F6"
        text_color = "#000000"
        box_bg = "#FFFFFF"
        box_text = "#000000"
        accent_color = "#0068C9"

    css = f"""
    <style>
        /* Ana Gövde ve Yan Menü */
        .stApp {{
            background-color: {bg_main};
            color: {text_color};
        }}
        [data-testid="stSidebar"] {{
            background-color: {bg_sidebar};
        }}
        
        /* Genel Metinler, Başlıklar ve Markdown İçerikleri */
        h1, h2, h3, h4, h5, h6, p, li, span, label, .stMarkdown p {{
            color: {text_color} !important;
        }}

        /* Girdi Kutuları (Text, Number, Selectbox) */
        .stTextInput > div > div > input, 
        .stNumberInput > div > div > input, 
        .stSelectbox > div > div > div {{
            background-color: {box_bg} !important;
            color: {box_text} !important;
            border: 1px solid #888888 !important;
        }}

        /* Radio Butonları (Seçenekler) */
        div[role="radiogroup"] label {{
            background-color: {box_bg} !important;
            color: {box_text} !important;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #888888;
            margin-bottom: 5px;
        }}
        
        div[role="radiogroup"] label p {{
            color: {box_text} !important;
        }}

        /* İpucu (Expander) Arka Planı */
        .streamlit-expanderHeader {{
            background-color: {box_bg} !important;
            color: {text_color} !important;
        }}
        .streamlit-expanderContent {{
            background-color: {bg_sidebar} !important;
            color: {text_color} !important;
        }}

        /* İpucu içindeki INFO kutuları */
        .stAlert {{
            background-color: {bg_sidebar} !important;
            color: {text_color} !important;
        }}

        /* Gece/Gündüz Butonu Özel Stili */
        .theme-btn-container button {{
            border: 2px solid {accent_color} !important;
            border-radius: 20px !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_theme()

# ==========================================
# 4. SIDEBAR
# ==========================================
with st.sidebar:
    st.write("✨ KPSS Soru Merkezi v2.0")
    if st.session_state.screen == "input":
        q_count = st.number_input("Testteki Soru Sayısı:", min_value=1, max_value=50, value=10, step=1)
    else:
        st.write("Sınav devam ediyor...")

# ==========================================
# 5. PERSISTENT HEADER (Timer & Mode Toggles)
# ==========================================
col_header_left, col_header_right = st.columns([3, 1])

with col_header_left:
    if st.session_state.screen in ["quiz", "results", "summary"]:
        if st.button("← Ana Ekrana Dön", key="global_back_btn"):
            st.session_state.screen = "input"
            st.rerun()

with col_header_right:
    theme_label = "☀️ Gündüz Modu" if st.session_state.gece_modu else "🌙 Gece Modu"
    st.markdown('<div class="theme-btn-container">', unsafe_allow_html=True)
    if st.button(theme_label, key="theme_toggle"):
        st.session_state.gece_modu = not st.session_state.gece_modu
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.screen == "quiz" and st.session_state.start_time is not None:
    elapsed_time = int(time.time() - st.session_state.start_time)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    st.markdown(f"<div style='text-align: center; font-size: 20px; font-weight: bold;'>⏱️ Geçen Süre: {minutes:02d}:{seconds:02d}</div>", unsafe_allow_html=True)
    st.write("---")

# ==========================================
# 6. SCREEN APPLICATION MANAGER
# ==========================================

# --- EKRAN 1: INPUT MODULÜ ---
if st.session_state.screen == "input":
    st.title("🎯 KPSS Sınav ve Özet Merkezi")
    st.write("Sınırsız soru oluşturma ve konu çalışma ekranı.")

    input_type = st.radio("İçerik Kaynağı:", ["Ders Konusu Yaz", "PDF Yükle"], horizontal=True)
    
    selected_topic = ""
    if input_type == "Ders Konusu Yaz":
        selected_topic = st.text_input("Eğitim Konusunu Yazın:", placeholder="Örnek: Coğrafi Konum")
    else:
        uploaded_file = st.file_uploader("PDF Dosyanızı Yükleyin (Geliştirme Aşamasında):", type=["pdf"])
        if uploaded_file is not None:
            selected_topic = f"PDF: {uploaded_file.name}"

    difficulty = st.selectbox("Zorluk Seviyesi:", ["Kolay", "Orta", "Zor"], index=1)
    
    st.write("")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("✨ Sınav Oluştur", key="btn_sinav_olustur", use_container_width=True, type="primary"):
            if selected_topic:
                with st.spinner("🚀 Sorular üretiliyor..."):
                    st.session_state.active_topic = selected_topic
                    st.session_state.generated_quiz = call_gemini_api("quiz", selected_topic, difficulty, q_count)
                    if st.session_state.generated_quiz:
                        st.session_state.current_question_idx = 0
                        st.session_state.user_answers = {}
                        st.session_state.start_time = time.time()
                        st.session_state.screen = "quiz"
                        st.rerun()
            else:
                st.warning("Lütfen bir konu başlığı girin!")

    with col_btn2:
        if st.button("📝 Konu Özeti Çıkar", key="btn_ozet_olustur", use_container_width=True, type="secondary"):
            if selected_topic:
                with st.spinner("📖 Özet çıkarılıyor..."):
                    st.session_state.active_topic = selected_topic
                    st.session_state.generated_summary = call_gemini_api("summary", selected_topic, difficulty)
                    st.session_state.screen = "summary"
                    st.rerun()
            else:
                st.warning("Lütfen bir konu başlığı girin!")

# --- EKRAN 2: QUIZ MODULÜ ---
elif st.session_state.screen == "quiz":
    questions = st.session_state.generated_quiz
    idx = st.session_state.current_question_idx
    
    if questions:
        current_q = questions[idx]
        
        st.subheader(f"Soru {idx + 1} / {len(questions)}")
        st.markdown(f"**{current_q['soru']}**")
        
        options_list = []
        options_mapping = {}
        for letter, text in current_q["secenekler"].items():
            display_text = f"{letter}) {text}"
            options_list.append(display_text)
            options_mapping[display_text] = letter
            
        options_list.append("⚪ Bu Soruyu Boş Bırak")
        options_mapping["⚪ Bu Soruyu Boş Bırak"] = "BOS"

        current_saved_ans = st.session_state.user_answers.get(idx, None)
        default_index = len(options_list) - 1
        if current_saved_ans and current_saved_ans != "BOS":
            for i, opt in enumerate(options_list):
                if opt.startswith(current_saved_ans + ")"):
                    default_index = i
                    break

        user_choice = st.radio("Seçeneğiniz:", options_list, index=default_index, key=f"q_radio_{idx}")
        st.session_state.user_answers[idx] = options_mapping[user_choice]

        with st.expander("💡 İpucu Al"):
            st.info(current_q["ipucu"])

        st.write("---")
        col_nav_left, col_nav_mid, col_nav_right = st.columns([1, 2, 1])
        
        with col_nav_left:
            if idx > 0:
                if st.button("⬅️ Önce", use_container_width=True):
                    st.session_state.current_question_idx -= 1
                    st.rerun()
        with col_nav_right:
            if idx < len(questions) - 1:
                if st.button("Sonra ➡️", use_container_width=True):
                    st.session_state.current_question_idx += 1
                    st.rerun()
        with col_nav_mid:
            if idx == len(questions) - 1:
                if st.button("🎯 Testi Bitir", use_container_width=True, type="primary"):
                    st.session_state.screen = "results"
                    st.rerun()

# --- EKRAN 3: SONUÇ RAPORU MODULÜ ---
elif st.session_state.screen == "results":
    st.title("📊 Sınav Sonucu")
    questions = st.session_state.generated_quiz
    user_answers = st.session_state.user_answers
    
    correct, wrong, skipped = 0, 0, 0
    for i, q in enumerate(questions):
        ans = user_answers.get(i, "BOS")
        if ans == "BOS": skipped += 1
        elif ans == q["dogru_cevap"]: correct += 1
        else: wrong += 1
            
    c1, c2, c3 = st.columns(3)
    c1.metric("Doğru", correct)
    c2.metric("Yanlış", wrong)
    c3.metric("Boş", skipped)
    
    st.write("---")
    for i, q in enumerate(questions):
        ans = user_answers.get(i, "BOS")
        st.markdown(f"**Soru {i+1}:** {q['soru']}")
        for letter, text in q["secenekler"].items():
            st.write(f"{letter}) {text}")
        
        if ans == "BOS": st.warning("⚠️ Boş bıraktınız.")
        elif ans == q["dogru_cevap"]: st.success(f"✅ Doğru! (Seçim: {ans})")
        else: st.error(f"❌ Yanlış! (Seçim: {ans} | Doğru Cevap: {q['dogru_cevap']})")
            
        st.info(f"**Çözüm:** {q['aciklama']}")
        st.write("---")

# --- EKRAN 4: ÖZET EKRANI ---
elif st.session_state.screen == "summary":
    st.subheader(f"📖 Konu Özeti: {st.session_state.active_topic}")
    st.markdown(st.session_state.generated_summary)
