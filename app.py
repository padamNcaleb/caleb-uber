import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="CALEB DISPATCH V2", layout="wide")

# STYLE CYBER-DARK
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #00ffc8; }
    h1, h2, h3 { color: #00ffc8 !important; }
    .stButton>button { background-color: #00ffc8; color: #0b0e14; border-radius: 5px; width: 100%; }
    .stTextArea>div>div>textarea { background-color: #1a1f29; color: #ffffff; border: 1px solid #00ffc8; }
    .success-text { color: #00ff00; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚚 CALEB DISPATCH PRO")
st.subheader("Optimiseur de route mobile - Sherbrooke Edition")

# Initialisation du géocodeur
geolocator = Nominatim(user_agent="caleb_dispatch_v2")

# --- Saisie des adresses ---
with st.sidebar:
    st.write("### 📍 Vos arrêts du jour")
    adresses_raw = st.text_area("Une adresse par ligne :", height=200, placeholder="Ex: 5073 rue Bertrand-Fabi, Sherbrooke, QC")
    btn_optimiser = st.button("🚀 TRACER L'ITINÉRAIRE")

if btn_optimiser and adresses_raw:
    adresses = [a.strip() for a in adresses_raw.split('\n') if a.strip()]
    
    if len(adresses) > 1:
        points = []
        with st.spinner('Géolocalisation des arrêts...'):
            for addr in adresses:
                location = geolocator.geocode(addr)
                if location:
                    points.append({"nom": addr, "coord": (location.latitude, location.longitude)})
        
        if len(points) > 1:
            # Algorithme simple (Plus proche voisin)
            route_optimisee = [points[0]]
            points_restants = points[1:]
            total_distance = 0
            
            while points_restants:
                dernier_point = route_optimisee[-1]
                proche_voisin = min(points_restants, key=lambda p: geodesic(dernier_point['coord'], p['coord']).km)
                total_distance += geodesic(dernier_point['coord'], proche_voisin['coord']).km
                route_optimisee.append(proche_voisin)
                points_restants.remove(proche_voisin)
            
            # --- AFFICHAGE ET CARTE ---
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"<p class='success-text'>✅ Itinéraire optimisé trouvé !</p>", unsafe_allow_html=True)
                st.metric("Distance totale estimée", f"{total_distance:.1f} km")
                for i, p in enumerate(route_optimisee):
                    icon = "🏠" if i == 0 else "📍"
                    st.write(f"**{i+1}.** {icon} {p['nom']}")

            with col2:
                # Création de la carte Folium avancée
                m = folium.Map(location=route_optimisee[0]['coord'], zoom_start=12, tiles="cartodbpositron")
                
                # Ajout des marqueurs et construction de la ligne
                route_coords = []
                for i, p in enumerate(route_optimisee):
                    route_coords.append(p['coord'])
                    color = 'green' if i == 0 else 'blue'
                    folium.Marker(p['coord'], popup=f"{i+1}. {p['nom']}", icon=folium.Icon(color=color, icon='info-sign')).add_to(m)
                
                # DESSINER LA LIGNE (Le trajet)
                folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.8).add_to(m)
                
                # Afficher la carte dans Streamlit
                st_folium(m, width=700, height=500)
    else:
        st.warning("Entrez au moins 2 adresses pour optimiser.")

st.markdown("---")
st.caption("Propulsé par le système Caleb Stratégos - 2026")
