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
def call_gemini_api(prompt_type, input_data, question_count=10):
    # API Anahtarını al
    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ HATA: API Anahtarı bulunamadı!")
        st.stop()
        
    client = genai.Client(api_key=api_key)
    system_instruction = (
        "Sen uzman bir KPSS ve ÖSYM soru hazırlama komisyonu üyesisin. "
        "Akademik titizlikle yaklaşmalı ve ÖSYM mantığına göre soru üretmelisin."
    )
    model_name = "gemini-2.5-flash"

    if prompt_type == "quiz":
        quiz_prompt = f"'{input_data}' konusu hakkında {question_count} adet, 5 seçenekli test sorusu hazırla. Sadece JSON listesi döndür."
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
            st.error(f"Soru üretme hatası: {e}")
            return []
        
    elif prompt_type == "summary":
        summary_prompt = f"'{input_data}' hakkında detaylı özet hazırla (Markdown formatında)."
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
            st.error(f"Özet üretme hatası: {e}")
            return "Özet oluşturulamadı."

# ==========================================
# 3. GLOBAL THEME DESIGN
# ==========================================
def inject_theme():
    css = """
    <style>
        .stApp {background-color: #FFFFFF !important;}
        [data-testid="stSidebar"] {background-color: #F4F6F9 !important;}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_theme()

# ==========================================
# 4. SIDEBAR & HEADER
# ==========================================
with st.sidebar:
    st.write("✨ KPSS Soru Merkezi v2.0")

# Ana Ekran Dönüş Butonu
if st.session_state.screen in ["quiz", "results", "summary"]:
    if st.button("← Ana Ekrana Dön"):
        st.session_state.screen = "input"
        st.rerun()

# ==========================================
# 5. SCREEN MANAGER
# ==========================================

# --- EKRAN 1: INPUT ---
if st.session_state.screen == "input":
    st.title("🎯 KPSS Sınav ve Özet Merkezi")
    selected_topic = st.text_input("Konu Girin:", placeholder="Örnek: Coğrafi Konum")
    q_count = st.number_input("Soru Sayısı:", min_value=1, max_value=50, value=10)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✨ Sınav Oluştur", type="primary"):
            if selected_topic:
                st.session_state.active_topic = selected_topic
                st.session_state.generated_quiz = call_gemini_api("quiz", selected_topic, q_count)
                st.session_state.current_question_idx = 0
                st.session_state.user_answers = {}
                st.session_state.screen = "quiz"
                st.rerun()
    with col2:
        if st.button("📝 Konu Özeti"):
            if selected_topic:
                st.session_state.active_topic = selected_topic
                st.session_state.generated_summary = call_gemini_api("summary", selected_topic)
                st.session_state.screen = "summary"
                st.rerun()

# --- EKRAN 2: QUIZ ---
elif st.session_state.screen == "quiz":
    questions = st.session_state.generated_quiz
    idx = st.session_state.current_question_idx
    
    if questions:
        current_q = questions[idx]
        st.subheader(f"Soru {idx + 1} / {len(questions)}")
        st.markdown(f"**{current_q['soru']}**")
        
        options = [f"{k}) {v}" for k, v in current_q["secenekler"].items()]
        # Radio seçimi
        user_choice = st.radio("Seçeneğiniz:", options, key=f"q_{idx}")
        st.session_state.user_answers[idx] = user_choice[0]
        
        with st.expander("💡 İpucu"):
            st.info(current_q["ipucu"])
            
        if st.button("Sonraki / Bitir"):
            if idx < len(questions) - 1:
                st.session_state.current_question_idx += 1
                st.rerun()
            else:
                st.session_state.screen = "results"
                st.rerun()

# --- EKRAN 3: RESULTS ---
elif st.session_state.screen == "results":
    st.title("📊 Sınav Sonucu")
    for i, q in enumerate(st.session_state.generated_quiz):
        ans = st.session_state.user_answers.get(i)
        st.markdown(f"**Soru {i+1}:** {q['soru']}")
        st.success(f"Doğru Cevap: {q['dogru_cevap']}")
        st.info(f"Çözüm: {q['aciklama']}")
        st.write("---")

# --- EKRAN 4: SUMMARY ---
elif st.session_state.screen == "summary":
    st.subheader(f"📖 Konu Özeti: {st.session_state.active_topic}")
    st.markdown(st.session_state.generated_summary)
    
