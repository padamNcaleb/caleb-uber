import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium

# Configuration de la page
st.set_page_config(page_title="CALEB DISPATCH V2", layout="wide")

# STYLE CYBER-DARK
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #00ffc8; }
    h1, h2, h3 { color: #00ffc8 !important; }
    .stButton>button { background-color: #00ffc8; color: #0b0e14; border-radius: 5px; width: 100%; font-weight: bold; }
    .stTextArea>div>div>textarea { background-color: #1a1f29; color: #ffffff; border: 1px solid #00ffc8; }
    .success-text { color: #00ff00; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚚 CALEB DISPATCH PRO")
st.subheader("Optimiseur de route mobile - Sherbrooke Edition")

# Initialisation du géocodeur (Nominatim)
geolocator = Nominatim(user_agent="caleb_dispatch_final")

# --- BARRE LATÉRALE : SAISIE ---
with st.sidebar:
    st.write("### 📍 Vos arrêts du jour")
    st.caption("La première adresse est votre point de départ.")
    adresses_raw = st.text_area("Une adresse par ligne :", height=250, placeholder="Ex: 2500 Boul de l'Université, Sherbrooke, QC")
    btn_optimiser = st.button("🚀 TRACER L'ITINÉRAIRE")

# --- LOGIQUE DE CALCUL ---
if btn_optimiser and adresses_raw:
    adresses = [a.strip() for a in adresses_raw.split('\n') if a.strip()]
    
    if len(adresses) > 1:
        points = []
        with st.spinner('Géolocalisation des adresses en cours...'):
            for addr in adresses:
                try:
                    location = geolocator.geocode(addr)
                    if location:
                        points.append({"nom": addr, "coord": (location.latitude, location.longitude)})
                except:
                    continue
        
        if len(points) > 1:
            # Algorithme du "Plus proche voisin"
            route_optimisee = [points[0]]
            points_restants = points[1:]
            total_distance = 0
            
            while points_restants:
                dernier_point = route_optimisee[-1]
                proche_voisin = min(points_restants, key=lambda p: geodesic(dernier_point['coord'], p['coord']).km)
                total_distance += geodesic(dernier_point['coord'], proche_voisin['coord']).km
                route_optimisee.append(proche_voisin)
                points_restants.remove(proche_voisin)
            
            # --- AFFICHAGE DES RÉSULTATS ---
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("<p class='success-text'>✅ Itinéraire optimisé trouvé !</p>", unsafe_allow_html=True)
                st.metric("Distance totale", f"{total_distance:.2f} km")
                
                st.write("### Ordre des arrêts :")
                for i, p in enumerate(route_optimisee):
                    emoji = "🏠" if i == 0 else "📍"
                    st.write(f"**{i+1}.** {emoji} {p['nom']}")

            with col2:
                # Création de la carte
                m = folium.Map(location=route_optimisee[0]['coord'], zoom_start=12)
                
                route_coords = []
                for i, p in enumerate(route_optimisee):
                    route_coords.append(p['coord'])
                    color = 'green' if i == 0 else 'blue'
                    folium.Marker(
                        location=p['coord'],
                        popup=f"Arrêt {i+1}",
                        icon=folium.Icon(color=color, icon='info-sign')
                    ).add_to(m)
                
                folium.PolyLine(route_coords, color="blue", weight=4, opacity=0.7).add_to(m)
                
                # LA MODIFICATION EST ICI : on ajoute key="dispatch_map"
                st_folium(m, width="100%", height=500, key="dispatch_map")
        else:
            st.error("Impossible de géolocaliser ces adresses. Vérifiez l'orthographe ou précisez 'Sherbrooke, QC'.")
    else:
        st.warning("Veuillez entrer au moins deux adresses.")

st.markdown("---")
st.caption("Caleb Dispatch Engine v2.0 - Propulsé par Python & Streamlit")
