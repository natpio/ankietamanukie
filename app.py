import streamlit as st
import datetime
import pandas as pd
import os

st.set_page_config(page_title="Manufaktura - Degustacja", layout="centered", initial_sidebar_state="collapsed")

# Zaawansowany CSS - Motyw Grafit/Marmur + Glassmorphism
st.markdown("""
<style>
    /* Tło - ciemny marmur/grafit */
    .stApp {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d3238 100%);
        color: #f1f2f6;
    }
    
    /* Ukrycie domyślnego nagłówka Streamlit */
    header {visibility: hidden;}
    
    /* Półprzezroczyste karty dla sekcji (Glassmorphism) */
    .block-container {
        padding-top: 2rem;
    }
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    }
    
    /* Animacje Hover i podświetlenie */
    div[data-testid="stVerticalBlock"] > div:hover {
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(255, 255, 255, 0.15);
    }
    
    /* Przycisk wysyłania (Glow) */
    button[kind="primary"] {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    button[kind="primary"]:hover {
        box-shadow: 0 0 15px rgba(75, 108, 183, 0.6);
        border-color: rgba(255, 255, 255, 0.5);
    }
</style>
""", unsafe_allow_html=True)

st.title("🌭 Panel Degustacyjny")
st.markdown("Oceń szczerze, to pomoże nam dopracować recepturę!")

# Wybór próbki
probka = st.radio("Którą próbkę oceniasz?", ("Próbka A", "Próbka B", "Próbka C"), horizontal=True)

st.header("Wygląd i Struktura")
wyglad = st.slider("1. Wygląd i apetyczność (1 - fatalnie, 5 - rewelacja)", 1, 5, 3)
struktura = st.slider("2. Struktura osłonki (1 - gumowata/pęka, 5 - idealna)", 1, 5, 3)

st.header("Balans Smaku (3 = Ideał)")
slonosc = st.slider("3. Poziom słoności", 1, 5, 3, help="1-mdłe, 3-w sam raz, 5-przesolone")
czosnek = st.slider("4. Intensywność przypraw", 1, 5, 3, help="1-brak, 3-w sam raz, 5-piecze")
soczystosc = st.slider("5. Soczystość mięsa", 1, 5, 3, help="1-suche, 3-idealna, 5-za tłuste")

st.header("Podsumowanie")
ocena_ogolna = st.slider("6. Ogólna ocena produktu (1-10)", 1, 10, 5)
komentarz = st.text_area("7. Co byś zmienił/a? (Opcjonalnie)")

if st.button("Wyślij ocenę 🚀", type="primary", use_container_width=True):
    # Logika zapisu lokalnie/do chmury
    dane = {
        "Data": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Próbka": [probka],
        "Wygląd": [wyglad],
        "Struktura": [struktura],
        "Słoność": [slonosc],
        "Czosnek": [czosnek],
        "Soczystość": [soczystosc],
        "Ogólna Ocena": [ocena_ogolna],
        "Komentarz": [komentarz]
    }
    
    df = pd.DataFrame(dane)
    plik_csv = 'wyniki_degustacji.csv'
    
    if not os.path.isfile(plik_csv):
        df.to_csv(plik_csv, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(plik_csv, mode='a', header=False, index=False, encoding='utf-8-sig')
        
    st.success("Dane zapisane! Możesz popić wodą i wziąć kolejny kawałek.")
