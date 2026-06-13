import streamlit as st
import time
import random

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
# 2. CORE SYSTEM PROMPT & API SIMULATION
# ==========================================
def call_gemini_api(prompt_type, input_data, difficulty="Orta"):
    """
    Simulated Gemini API Call with high temperature, random seeds, and 
    strict instructions to prioritize actual past KPSS exam questions and ÖSYM formats.
    """
    # Sonsuz soru çeşitliliği için yüksek sıcaklık (temperature) ve dinamik seed simülasyonu
    random.seed(time.time() + random.random())
    
    # GERÇEK ENTEGRASYONDA BU METİN GEMINI SYSTEM PROMPT / DEVELOPER INSTRUCTION OLARAK VERİLMELİDİR:
    system_instruction = """
    Sen uzman bir KPSS ve ÖSYM soru hazırlama komisyonu üyesisin. 
    Girdi olarak verilen konularda soru üretirken MÜHENDİSLİK ve AKADEMİK titizlikle yaklaşmalı, 
    ÖNCELİKLE actual past KPSS exam questions (ÖSYM'nin geçmiş yıllarda sorduğu gerçek çıkmış sorular) 
    ve güncel ÖSYM formatlarını (Ales, Dgs, Kpss güncel mantığı) birincil referans (primary reference) almalısın.
    Asla birbirini tekrar eden cümle senaryoları, kalıplar veya aynı şıkları üretme (Endless Question Variety). 
    Soru başına mutlaka 5 seçenek (A, B, C, D, E) üret.
    """
    
    if prompt_type == "quiz":
        questions = []
        # Sınav formatına tam uyumlu 5 soru simülasyonu
        for i in range(1, 6):
            choices = {
                "A": f"ÖSYM'nin en çok kullandığı çeldirici {random.randint(100,999)}",
                "B": f"Geçmiş KPSS çıkmış soru paralelindeki B seçeneği",
                "C": f"Doğru yapılandırılmış mantıksal öncül şıkkı",
                "D": f"Net bilgi içeren net şık {random.randint(100,999)}",
                "E": f"Güncel ÖSYM formatına uygun E seçeneği"
            }
            correct_letter = random.choice(["A", "B", "C", "D", "E"])
            
            questions.append({
                "id": i,
                "soru": f"💡 [ÇIKMIŞ KPSS PARALELİ] ÖSYM'nin geçmiş yıllarda sorduğu gerçek sınav soruları ve güncel formatı esas alınarak hazırlanmış, {difficulty} zorluk seviyesindeki özgün {input_data} sorusu {i}?",
                "secenekler": choices,
                "dogru_cevap": correct_letter,
                "ipucu": f"İpucu: Bu soruyu çözerken ÖSYM'nin çıkmış sorularındaki ana mantığı ve {input_data} konusunun en temel uç istisnasını hatırlayın.",
                "aciklama": f"Bu konunun KPSS'deki soru kalıpları incelendiğinde {input_data} kuralının doğrudan test edildiği görülür. ÖSYM standartlarında analiz yapıldığında doğru sonuca ulaşılır."
            })
        return questions
        
    elif prompt_type == "summary":
        return f"""
# 📄 {input_data} - KPSS / ÖSYM Odaklı Ders Özet Notu

### 📌 Temel Kavramlar ve Tanımlar
* **ÖSYM'nin Tanımı:** Çıkmış sorularda {input_data} konusu işlenirken kullanılan resmi akademik tanımlar.
* **Anahtar Kelimeler:** Soru kökünde "özellikle", "kesinlikle" ibaresiyle geçen kritik ipuçları.

### 📐 Kurallar, Formüller ve İstisnalar
* **KPSS Altın Kuralı:** Geçmiş sınavlarda en az 3 defa yoklanmış olan ana kurallar.
* **Uç Noktalar:** ÖSYM'nin çeldirici olarak şıklara koymayı en çok sevdiği istisnai örnekler.

### 💡 Hap Bilgiler
* ÖSYM'nin son yıllardaki soru eğilimlerine göre derlenmiş 5 nokta atışı pratik bilgi.
* Hafıza teknikleri ve KPSS formatına uygun kısa formüller.

### 🔑 Sınav İpuçları
* **Tuzaklar:** Çıkmış KPSS sorularında adayların en çok düştüğü yanıltıcı şık tasarımları.
* **Soru Dağılımı:** Bu konu başlığından sınavda doğrudan gelebilecek soru tiplerinin analizi.
"""

# ==========================================
# 3. GLOBAL THEME DESIGN & CUSTOM CSS INJECTION
# ==========================================
def inject_theme():
    # Temel renk paletleri belirleniyor
    if st.session_state.gece_modu:
        bg_color = "#000000"
        text_color = "#FFFFFF"
    else:
        bg_color = "#FFFFFF"
        text_color = "#000000"

    css = f"""
    <style>
        /* Global Ekran ve Yazı Renklerinin Zorlanması */
        .stApp {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, span, div, .stRadio {{
            color: {text_color} !important;
        }}
        
        /* İSTEK 1: Gece Modu Butonu - Light Mode'da (Gece Modu OFF iken) Kapkara ve Kalın Beyaz Yazı */
        {"div.stButton > button:has(div[data-testid='stMarkdownContainer'] p:contains('Gece Modu')) {"
         "background-color: #000000 !important;"
         "color: #FFFFFF !important;"
         "font-weight: bold !important;"
         "border: 2px solid #000000 !important;"
         "}" if not st.session_state.gece_modu else ""}

        /* Gece Modu AÇIK iken Butonun Gündüz Moduna Dönüşme Stili */
        {"div.stButton > button:has(div[data-testid='stMarkdownContainer'] p:contains('Gündüz Modu')) {"
         "background-color: #FFFFFF !important;"
         "color: #000000 !important;"
         "font-weight: bold !important;"
         "border: 2px solid #FFFFFF !important;"
         "}" if st.session_state.gece_modu else ""}

        /* İSTEK 3: Yeşil Buton CSS Enjeksiyonu (Konu Özeti Oluştur) */
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

        /* Sınav Oluştur Kırmızı/Primary Buton CSS */
        div:has(.sinav-marker) + div button {{
            background-color: #dc3545 !important;
            color: white !important;
            font-weight: bold !important;
            border: none !important;
        }}

        /* Mobil Duyarlılık (Responsive Layout) */
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
    st.markdown(css, unsafe_transform=True)

# CSS enjeksiyonunu başlat
inject_theme()

# ==========================================
# 4. PERSISTENT HEADER (Timer & Mode Toggles)
# ==========================================
col_header_left, col_header_right = st.columns([3, 1])

with col_header_left:
    # Sol üst köşede her zaman aktif olan "Geri Dön" butonu (Giriş ekranı hariç)
    if st.session_state.screen in ["quiz", "results", "summary"]:
        if st.button("← Geri Dön", key="global_back_btn"):
            st.session_state.screen = "input"
            st.rerun()

with col_header_right:
    # Global Gece Modu Değiştirici Buton
    theme_label = "🌙 Gece Modu" if not st.session_state.gece_modu else "☀️ Gündüz Modu"
    if st.button(theme_label, key="theme_toggle"):
        st.session_state.gece_modu = not st.session_state.gece_modu
        st.rerun()

# Kalıcı Kronometre/Zamanlayıcı (Sadece Quiz çözülürken en üstte sabit kalır ve resetlenmez)
if st.session_state.screen == "quiz" and st.session_state.start_time is not None:
    elapsed_time = int(time.time() - st.session_state.start_time)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    st.markdown(f"<div style='text-align: center; font-size: 20px; font-weight: bold;'>⏱️ Toplam Geçen Süre: {minutes:02d}:{seconds:02d}</div>", unsafe_transform=True)
    st.write("---")

# ==========================================
# 5. SCREEN APPLICATION MANAGER
# ==========================================

# --- EKRAN 1: INPUT MODULÜ ---
if st.session_state.screen == "input":
    st.title("🎯 KPSS & ÖSYM Odaklı Sınav ve Özet Hazırlama Merkezi")
    st.write("ÖSYM'nin geçmiş yıllardaki gerçek çıkmış sorularını temel alan akıllı hazırlık modülü.")

    # İki Giriş Seçeneği (PDF ve Ders Notu/Dersin Konusu)
    input_type = st.radio("İçerik Kaynağı Seçiniz:", ["Ders Notu / Dersin Konusu", "PDF İçeriğinden"], horizontal=True)
    
    selected_topic = ""
    if input_type == "Ders Notu / Dersin Konusu":
        selected_topic = st.text_input("Eğitim Konusunu Yazın (Örn: Ünlü Düşmesi):", placeholder="Örnek: Ünlü Düşmesi, İklim Tipleri, İslamiyet Öncesi Türk Tarihi...")
    else:
        uploaded_file = st.file_uploader("PDF Dosyanızı Yükleyin:", type=["pdf"])
        if uploaded_file is not None:
            selected_topic = f"Yüklenen PDF: {uploaded_file.name}"

    # Zorluk Seviyesi Seçici
    difficulty = st.selectbox("Zorluk Seviyesi Seçin:", ["Kolay", "Orta", "Zor"], index=1)

    st.write("")
    
    # Butonların Yan Yana Konumlandırılması ve CSS İşaretleyicileri
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        st.markdown('<div class="sinav-marker"></div>', unsafe_transform=True)
        if st.button("✨ Sınav Oluştur", key="btn_sinav_olustur", use_container_width=True):
            if selected_topic:
                st.session_state.active_topic = selected_topic
                st.session_state.generated_quiz = call_gemini_api("quiz", selected_topic, difficulty)
                st.session_state.current_question_idx = 0
                st.session_state.user_answers = {}
                st.session_state.start_time = time.time()
                st.session_state.screen = "quiz"
                st.rerun()
            else:
                st.warning("Lütfen bir konu başlığı girin veya bir PDF dosyası yükleyin!")

    with col_btn2:
        st.markdown('<div class="ozet-marker"></div>', unsafe_transform=True)
        if st.button("📝 Konu Özeti Oluştur", key="btn_ozet_olustur", use_container_width=True):
            if selected_topic:
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
        
        # Soru Metni Üst Alanı
        st.subheader(f"Soru {idx + 1} / {len(questions)}")
        st.markdown(f"**{current_q['soru']}**")
        
        # Seçeneklerin Listelenmesi (Tam Olarak 5 Şık: A, B, C, D, E + Boş Bırak Seçeneği)
        options_list = []
        options_mapping = {}
        for letter, text in current_q["secenekler"].items():
            display_text = f"{letter}) {text}"
            options_list.append(display_text)
            options_mapping[display_text] = letter
            
        options_list.append("⚪ Bu Soruyu Boş Bırak")
        options_mapping["⚪ Bu Soruyu Boş Bırak"] = "BOS"

        # Kullanıcının daha önceki sayfalamada verdiği yanıtı hatırlama mantığı
        current_saved_ans = st.session_state.user_answers.get(idx, None)
        default_index = len(options_list) - 1  # Varsayılan seçim Boş Bırak olsun
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

        # "İpucu Al" Buton ve Açılır Kutu Yapısı (Sorunsuz Dinamik Veri Çekimi)
        with st.expander("💡 İpucu Al"):
            st.info(current_q["ipucu"])

        st.write("---")
        
        # Merkezlenmiş ve Hizalanmış Tek Soru Navigasyon Butonları
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
            
    # Sonuç Metrik Paneli
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat1.metric("Doğru Sayısı", correct_count)
    col_stat2.metric("Yanlış Sayısı", wrong_count)
    col_stat3.metric("Boş Sayısı", skipped_count)
    
    st.write("---")
    st.subheader("🔍 Soru Bazlı Değerlendirme")
    
    for i, q in enumerate(questions):
        ans = user_answers.get(i, "BOS")
        st.markdown(f"**Soru {i+1}:** {q['soru']}")
        
        if ans == "BOS":
            st.markdown("⚠️ *Bu soruyu boş bıraktınız.*")
            st.markdown(f"**Doğru Cevap:** {q['dogru_cevap']} Şıkkı")
            st.markdown(f"**Kısa Çözüm:** Doğru şık bu, mesela {q['dogru_cevap']}. Cevap o şıkdaki doğrusu şudur: {q['aciklama']}")
        elif ans == q["dogru_cevap"]:
            st.markdown(f"✅ *Doğru Cevap Verdiniz.* (Seçiminiz: {ans})")
            st.markdown(f"**Kısa Çözüm:** Doğru şık bu, mesela {q['dogru_cevap']}. Cevap o şıkdaki doğrusu şudur: {q['aciklama']}")
        else:
            st.markdown(f"❌ *Bu soruda hata yaptınız.* (Seçiminiz: {ans})")
            # İSTEK 3: Tam Şablon Formatı Korunumu ("Doğru şık bu, mesela...")
            st.markdown(f"**Doğru Cevap:** {q['dogru_cevap']} Şıkkı")
            st.markdown(f"**Kısa Çözüm:** Doğru şık bu, mesela {q['dogru_cevap']}. Cevap o şıkdaki doğrusu şudur: {q['aciklama']}")
            
        st.write("---")


# --- EKRAN 4: YAPILANDIRILMIŞ ÖZET NOTU EKRANI ---
elif st.session_state.screen == "summary":
    st.subheader(f"📖 Konu Analiz Özeti: {st.session_state.active_topic}")
    
    # Markdown formatındaki yapılandırılmış özet temiz bir biçimde render edilir
    st.markdown(st.session_state.generated_summary)
    
    st.write("---")
    # Özet Sayfası Altındaki Hızlı Sınav Başlatma Özelliği
    st.markdown("<p style='text-align: center; font-weight: bold;'>Konuyu pekiştirmek için çıkmış kpss paralelindeki soruları hemen çözün!</p>", unsafe_transform=True)
    if st.button("🚀 Hazırım, Sınav Oluştur", use_container_width=True):
        st.session_state.generated_quiz = call_gemini_api("quiz", st.session_state.active_topic)
        st.session_state.current_question_idx = 0
        st.session_state.user_answers = {}
        st.session_state.start_time = time.time()
        st.session_state.screen = "quiz"
        st.rerun()
