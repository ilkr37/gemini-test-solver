İmport streamlit as st
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
    # API anahtarını kodun içinden değil, Streamlit'in gizli kasasından oku
    api_key = st.secrets.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("⚠️ Streamlit Secrets panelinde GEMINI_API_KEY tanımlanmamış!")
        st.stop()
        
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"İstemci başlatılamadı, API anahtarınızı kontrol edin: {e}")
        st.stop()

    # Uzman ÖSYM Komisyon Üyesi Rol Tanımı
    system_instruction = (
        "Sen uzman bir KPSS og ÖSYM soru hazırlama komisyonu üyesisin. "
        "Girdi olarak verilen konularda içerik üretirken akademik titizlikle yaklaşmalı, "
        "ÖNCELİKLE ÖSYM'nin geçmiş yıllarda sorduğu gerçek KPSS, ALES, DGS sorularını ve "
        "güncel ÖSYM mantığını birincil referans almalısın. Asla birbirini tekrar eden kalıplar kullanma."
    )
    
    # En stabil ve hızlı çalışan metin modeli
    model_name = "gemini-2.5-flash"

    if prompt_type == "quiz":
        quiz_prompt = f"""
        '{input_data}' konusu hakkında, {difficulty} zorluk seviyesinde, KPSS Ortaöğretim formatına tam uyumlu, 
        çeldiricileri güçlü ve özgün tam {question_count} adet test sorusu hazırla. 
        Her soru kesinlikle 5 seçenekli (A, B, C, D, E) olmalıdır.
        
        Senden çıktıyı kesinlikle aşağıdaki JSON şemasına birebir uyacak şekilde ham bir JSON listesi olarak istiyorum. 
        Asla başına veya sonuna markdown (```json gibi) ekleme, sadece saf JSON metni döndür:
        
        [
          {{
            "id": 1,
            "soru": "[ÇIKMIŞ KPSS PARALELİ] Soru metni...",
            "secenekler": {{
              "A": "A seçeneği",
              "B": "B seçeneği",
              "C": "C seçeneği",
              "D": "D seçeneği",
              "E": "E seçeneği"
            }},
            "dogru_cevap": "C",
            "ipucu": "ÖSYM tarzı ipucu...",
            "aciklama": "Doğru cevabın gerekçesi ve kural analizi..."
          }}
        ]
        """
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=quiz_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.75,  # Her seferinde benzersiz sorular için dengeli yaratıcılık
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            st.error(f"Yapay zeka soru üretirken bir hata oluştu: {e}")
            return []
        
    elif prompt_type == "summary":
        summary_prompt = f"""
        '{input_data}' konusu hakkında KPSS Ortaöğretim sınavına hazırlanan bir adayın mutlaka bilmesi gereken, 
        ÖSYM formatına uygun, detaylı, akademik og taktiksel bir ders özeti hazırla.
        Özet içerisinde şu başlıklar mutlaka Markdown formatında bulunsun:
        - 📌 Temel Kavramlar ve Tanımlar
        - 📐 Kurallar, Formüller ve İstisnalar (ÖSYM'nin en çok sorduğu uç noktalar)
        - 💡 Hap Bilgiler ve Pratik Formüller
        - 🔑 Sınav İpuçları (Adayların en çok düştüğü şık tuzakları)
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
            st.error(f"Yapay zeka özet üretirken bir hata oluştu: {e}")
            return "Özet oluşturulamadı."

# ==========================================
# 3. GLOBAL THEME DESIGN & CUSTOM CSS INJECTION
# ==========================================
def inject_theme():
    if st.session_state.gece_modu:
        bg_color = "#000000"
        text_color = "#FFFFFF"
        sidebar_bg = "#111111"
        box_bg = "#333333" 
        input_text_color = "#FFFFFF"
        label_bg = "#222222"
        label_text_color = "#FFFFFF"
    else:
        # Gündüz modu için okunabilir açık renk ayarları
        bg_color = "#FFFFFF"
        text_color = "#131722"
        sidebar_bg = "#F8F9FA"
        box_bg = "#F0F2F6"          # Girdi kutuları için görünür açık gri arka plan
        input_text_color = "#31333F" # Kutuların içindeki yazıların rengi (Koyu)
        label_bg = "#E9ECEF"        # Başlık etiketlerinin arkası
        label_text_color = "#131722"

    css = f"""
    <style>
        /* Ana Uygulama Gövde ve Metin Zıtlık Ayarları */
        .stApp, [data-testid="stAppViewContainer"] {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}
        
        /* Genel Metin Yapıları */
        h1, h2, h3, h4, h5, h6, p, .stMarkdown, [data-testid="stWidgetLabel"] p {{
            color: {text_color} !important;
        }}

        /* Düzenlenen Kısım: Form etiketlerinin hem gece hem gündüz modunda okunabilir olması sağlandı */
        div[data-testid="stWidgetLabel"] > label > div > p {{
            background-color: {label_bg} !important;
            color: {label_text_color} !important;
            padding: 6px 12px !important;
            border-radius: 4px !important;
            display: inline-block !important;
            width: auto !important;
            font-weight: bold !important;
            margin-bottom: 4px !important;
        }}

        /* Yan Menü (Sidebar) Arka Plan Dengesi */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
        }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{
            color: {text_color} !important;
        }}

        /* Girdi Kutularının Dinamik Arka Plan Ayarları */
        div[data-baseweb="select"], div[data-baseweb="input"], .stNumberInput div, .stTextInput div {{
            background-color: {box_bg} !important;
            border-radius: 8px !important;
            border: 1px solid #ced4da !important;
        }}
        
        /* Kutuların İçindeki Yazıların Temaya Göre Değişimi */
        input, .stSelectbox span, div[data-baseweb="select"] div, .stNumberInput input, .stTextInput input {{
            color: {input_text_color} !important;
            -webkit-text-fill-color: {input_text_color} !important;
        }}
        
        /* Gündüz modunda placeholder (ipucu) metninin okunabilirliği */
        input::placeholder, textarea::placeholder {{
            color: #6c757d !important;
            -webkit-text-fill-color: #6c757d !important;
            opacity: 1 !important;
        }}

        /* Açılır menü listesi eleman rengi */
        ul[role="listbox"] li {{
            color: #000000 !important;
        }}

        /* Radyo Butonlarındaki Seçenek Metinleri */
        [data-testid="stRadio"] label span, [data-testid="stRadio"] p {{
            color: {text_color} !important;
        }}
        
        div[data-testid="stMarkdownContainer"] p {{
            color: {text_color} !important;
        }}
        
        /* Tema Değiştirme Butonlarının Özel Gece/Gündüz Boyamaları */
        {"div.stButton > button:has(div[data-testid='stMarkdownContainer'] p:contains('Gece Modu')) {"
         "background-color: #000000 !important;"
         "color: #FFFFFF !important;"
         "font-weight: bold !important;"
         "border: 2px solid #FFFFFF !important;"
         "}" if not st.session_state.gece_modu else ""}

        {"div.stButton > button:has(div[data-testid='stMarkdownContainer'] p:contains('Gündüz Modu')) {"
         "background-color: #FFFFFF !important;"
         "color: #000000 !important;"
         "font-weight: bold !important;"
         "border: 2px solid #000000 !important;"
         "}" if st.session_state.gece_modu else ""}

        /* Yeşil Özet Oluşturma Buton Stili */
        div:has(.ozet-marker) + div button {{
            background-color: #28a745 !important;
            color: white !important;
            font-weight: bold !important;
            border: none !important;
        }}
        div:has(.ozet-marker) + div button:hover {{
            background-color: #218838 !important;
            color: white !important;
        }}

        /* Kırmızı Sınav Oluşturma Buton Stili */
        div:has(.sinav-marker) + div button {{
            background-color: #dc3545 !important;
            color: white !important;
            font-weight: bold !important;
            border: none !important;
        }}
        div:has(.sinav-marker) + div button:hover {{
            background-color: #bd2130 !important;
            color: white !important;
            }}

        @media (max-width: 768px) {{
            .stButton button {{
                width: 100% !important;
            }}
            .stMainBlockContainer {{
                padding: 1rem !important;
            }}
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_theme()

# ==========================================
# 4. SIDEBAR - EMPTY CONTROL (Temizlendi)
# ==========================================
with st.sidebar:
    st.write("✨ KPSS Soru Merkezi v2.0")

# ==========================================
# 5. PERSISTENT HEADER (Timer & Mode Toggles)
# ==========================================
col_header_left, col_header_right = st.columns([3, 1])

with col_header_left:
    if st.session_state.screen in ["quiz", "results", "summary"]:
        if st.button("← Geri Dön", key="global_back_btn"):
            st.session_state.screen = "input"
            st.rerun()

with col_header_right:
    theme_label = "🌙 Gece Modu" if not st.session_state.gece_modu else "☀️ Gündüz Modu"
    if st.button(theme_label, key="theme_toggle"):
        st.session_state.gece_modu = not st.session_state.gece_modu
        st.rerun()

if st.session_state.screen == "quiz" and st.session_state.start_time is not None:
    elapsed_time = int(time.time() - st.session_state.start_time)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    st.markdown(f"<div style='text-align: center; font-size: 20px; font-weight: bold;'>⏱️ Toplam Geçen Süre: {minutes:02d}:{seconds:02d}</div>", unsafe_allow_html=True)
    st.write("---")

# ==========================================
# 6. SCREEN APPLICATION MANAGER
# ==========================================

# --- EKRAN 1: INPUT MODULÜ ---
if st.session_state.screen == "input":
    st.title("🎯 KPSS & ÖSYM Odaklı Sınav ve Özet Hazırlama Merkezi")
    st.write("Google Gemini ile ÖSYM'nin geçmiş yıllardaki gerçek çıkmış sorularını temel alan akıllı hazırlık modülü.")

    input_type = st.radio("İçerik Kaynağı Seçiniz:", ["Ders Notu / Dersin Konusu", "PDF İçeriğinden"], horizontal=True)
    
    selected_topic = ""
    if input_type == "Ders Notu / Dersin Konusu":
        selected_topic = st.text_input("Eğitim Konusunu Yazın (Örn: Ünlü Düşmesi):", placeholder="Örnek: Ünlü Düşmesi, İklim Tipleri, İslamiyet Öncesi Türk Tarihi...")
    else:
        uploaded_file = st.file_uploader("PDF Dosyanızı Yükleyin:", type=["pdf"])
        if uploaded_file is not None:
            selected_topic = f"Yüklenen PDF İçeriği: {uploaded_file.name}"

    difficulty = st.selectbox("Zorluk Seviyesi Seçin:", ["Kolay", "Orta", "Zor"], index=1)
    
    # Soru Sayısı Ayarı Yan Menüden (Sidebar) Ana Ekrana Alındı
    q_count = st.number_input("Testteki Soru Sayısı:", min_value=1, max_value=200, value=20, step=1)

    st.write("")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        st.markdown('<div class="sinav-marker"></div>', unsafe_allow_html=True)
        if st.button("✨ Sınav Oluştur", key="btn_sinav_olustur", use_container_width=True):
            if selected_topic:
                with st.spinner("🚀 Gemini gerçek zamanlı ÖSYM soruları üretiyor, lütfen bekleyin..."):
                    st.session_state.active_topic = selected_topic
                    st.session_state.generated_quiz = call_gemini_api("quiz", selected_topic, difficulty, q_count)
                    if st.session_state.generated_quiz:
                        st.session_state.current_question_idx = 0
                        st.session_state.user_answers = {}
                        st.session_state.start_time = time.time()
                        st.session_state.screen = "quiz"
                        st.rerun()
            else:
                st.warning("Lütfen bir konu başlığı girin veya bir PDF dosyası yükleyin!")

    with col_btn2:
        st.markdown('<div class="ozet-marker"></div>', unsafe_allow_html=True)
        if st.button("📝 Konu Özeti Oluştur", key="btn_ozet_olustur", use_container_width=True):
            if selected_topic:
                with st.spinner("📖 Gemini konuyu analiz ediyor ve özet not çıkarıyor..."):
                    st.session_state.active_topic = selected_topic
                    st.session_state.generated_summary = call_gemini_api("summary", selected_topic, difficulty)
                    st.session_state.screen = "summary"
                    st.rerun()
            else:
                st.warning("Lütfen bir konu başlığı girin veya bir PDF dosyası yükleyin!")


# --- EKRAN 2: TEK SORU SAYFALAMA YAPILI QUIZ MODULÜ ---
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
        if current_saved_ans:
            if current_saved_ans == "BOS":
                default_index = len(options_list) - 1
            else:
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
                if st.button("⬅️ Önceki Soru", use_container_width=True):
                    st.session_state.current_question_idx -= 1
                    st.rerun()
                    
        with col_nav_right:
            if idx < len(questions) - 1:
                if st.button("Sonraki Soru ➡️", use_container_width=True):
                    st.session_state.current_question_idx += 1
                    st.rerun()
                    
        with col_nav_mid:
            if idx == len(questions) - 1:
                if st.button("🎯 Yanıtları Gönder", use_container_width=True):
                    st.session_state.screen = "results"
                    st.rerun()


# --- EKRAN 3: DETAYLI SONUÇ RAPORU MODULÜ ---
elif st.session_state.screen == "results":
    st.title("📊 KPSS Deneme Sonuç Raporu")
    
    questions = st.session_state.generated_quiz
    user_answers = st.session_state.user_answers
    
    correct_count = 0
    wrong_count = 0
    skipped_count = 0
    
    for i, q in enumerate(questions):
        ans = user_answers.get(i, "BOS")
        if ans == "BOS":
            skipped_count += 1
        elif ans == q["dogru_cevap"]:
            correct_count += 1
        else:
            wrong_count += 1
            
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat1.metric("Doğru Sayısı", correct_count)
    col_stat2.metric("Yanlış Sayısı", wrong_count)
    col_stat3.metric("Boş Sayısı", skipped_count)
    
    st.write("---")
    st.subheader("🔍 Soru Bazlı Değerlendirme")
    
    for i, q in enumerate(questions):
        ans = user_answers.get(i, "BOS")
        st.markdown(f"**Soru {i+1}:** {q['soru']}")
        
        for letter, text in q["secenekler"].items():
            st.write(f"{letter}) {text}")
        
        if ans == "BOS":
            st.markdown("⚠️ *Bu soruyu boş bıraktınız.*")
        elif ans == q["dogru_cevap"]:
            st.markdown(f"✅ *Doğru Cevap Verdiniz.* (Seçiminiz: {ans})")
        else:
            st.markdown(f"❌ *Bu soruda hata yaptınız.* (Seçiminiz: {ans})")
            
        st.markdown(f"**Doğru Cevap:** {q['dogru_cevap']} Şıkkı")
        st.markdown(f"**Kısa Çözüm:** {q['aciklama']}")
            
        st.write("---")


# --- EKRAN 4: YAPILANDIRILMIŞ ÖZET NOTU EKRANI ---
elif st.session_state.screen == "summary":
    st.subheader(f"📖 Konu Analiz Özeti: {st.session_state.active_topic}")
    
    st.markdown(st.session_state.generated_summary)
    
    st.write("---")
    st.markdown("<p style='text-align: center; font-weight: bold;'>Konuyu pekiştirmek için çıkmış kpss paralelindeki soruları hemen çözün!</p>", unsafe_allow_html=True)
    if st.button("🚀 Hazırım, Sınav Oluştur", use_container_width=True):
        with st.spinner("🚀 Gemini bu özetten yola çıkarak sorular hazırlıyor..."):
            st.session_state.generated_quiz = call_gemini_api("quiz", st.session_state.active_topic, question_count=q_count)
            if st.session_state.generated_quiz:
                st.session_state.current_question_idx = 0
                st.session_state.user_answers = {}
                st.session_state.start_time = time.time()
                st.session_state.screen = "quiz"
                st.rerun()






