import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="CALEB DISPATCH V2.1", layout="wide")

# STYLE CYBER-DARK
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #00ffc8; }
    h1, h2, h3 { color: #00ffc8 !important; }
    .stButton>button { background-color: #00ffc8; color: #0b0e14; font-weight: bold; border-radius: 5px; }
    .stTextArea>div>div>textarea { background-color: #1a1f29; color: #ffffff; border: 1px solid #00ffc8; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS CACHÉES (Pour éviter les bugs de disparition) ---
@st.cache_data
def get_coordinates(address_list):
    """Transforme les adresses en coordonnées GPS et les garde en mémoire."""
    geolocator = Nominatim(user_agent="caleb_dispatch_final")
    results = []
    for addr in address_list:
        try:
            location = geolocator.geocode(addr, timeout=10)
            if location:
                results.append({"nom": addr, "coord": (location.latitude, location.longitude)})
        except:
            continue
    return results

st.title("🚚 CALEB DISPATCH PRO")
st.subheader("Optimiseur de route - Version Stable")

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.write("### 📍 Entrez les adresses")
    adresses_raw = st.text_area("Une adresse par ligne :", height=200, placeholder="Ex: 5073 rue Bertrand-Fabi, Sherbrooke, QC")
    btn_optimiser = st.button("🚀 TRACER L'ITINÉRAIRE")

# --- LOGIQUE PRINCIPALE ---
if adresses_raw:
    liste_adresses = [a.strip() for a in adresses_raw.split('\n') if a.strip()]
    
    if btn_optimiser and len(liste_adresses) > 1:
        # 1. Récupération des points (avec cache)
        points = get_coordinates(liste_adresses)
        
        if len(points) > 1:
            # 2. Algorithme du plus proche voisin
            route_optimisee = [points[0]]
            points_restants = points[1:]
            dist_totale = 0
            
            while points_restants:
                dernier = route_optimisee[-1]
                proche = min(points_restants, key=lambda p: geodesic(dernier['coord'], p['coord']).km)
                dist_totale += geodesic(dernier['coord'], proche['coord']).km
                route_optimisee.append(proche)
                points_restants.remove(proche)
            
            # 3. Affichage des résultats
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.success(f"Itinéraire : {dist_totale:.1f} km")
                for i, p in enumerate(route_optimisee):
                    st.write(f
