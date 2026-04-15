import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pandas as pd

# CONFIGURATION DE LA PAGE
st.set_page_config(page_title="CALEB DISPATCH PRO", layout="centered")

# STYLE VISUEL
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #00ffc8; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚚 CALEB DISPATCH PRO")
st.subheader("Optimiseur de route - Service Mobile")

# INITIALISATION DU GPS (NOMINATIM)
geolocator = Nominatim(user_agent="caleb_dispatch_system")

# ZONE DE SAISIE DES ADRESSES
st.info("Entrez vos adresses (une par ligne). La première est votre point de départ.")
adresses_raw = st.text_area("Exemple :\n2500 Boul de l'Université, Sherbrooke, QC\n987 Rue Conseil, Sherbrooke, QC", height=200)

if st.button("🗺️ CALCULER L'ITINÉRAIRE LE PLUS COURT"):
    # Nettoyage des données
    adresses = [a.strip() for a in adresses_raw.split('\n') if a.strip()]
    
    if len(adresses) > 1:
        points = []
        with st.spinner('Analyse géographique en cours...'):
            for addr in adresses:
                try:
                    location = geolocator.geocode(addr)
                    if location:
                        points.append({
                            "nom": addr, 
                            "lat": location.latitude, 
                            "lon": location.longitude
                        })
                except Exception as e:
                    st.error(f"Erreur sur l'adresse : {addr}")

        if len(points) > 1:
            # ALGORITHME DU PLUS PROCHE VOISIN
            route_optimisee = [points[0]]
            points_restants = points[1:]
            
            while points_restants:
                dernier_point = route_optimisee[-1]
                proche_voisin = min(points_restants, 
                                    key=lambda p: geodesic((dernier_point['lat'], dernier_point['lon']), 
                                                           (p['lat'], p['lon'])).km)
                route_optimisee.append(proche_voisin)
                points_restants.remove(proche_voisin)
            
            # AFFICHAGE DES ÉTAPES
            st.success("✅ Itinéraire optimisé trouvé !")
            for i, p in enumerate(route_optimisee):
                st.write(f"📍 **Étape {i+1} :** {p['nom']}")
            
            # AFFICHAGE DE LA CARTE
            df_map = pd.DataFrame(route_optimisee)
            st.map(df_map)
            
    else:
        st.warning("Veuillez entrer au moins deux adresses (Départ + 1 client).")

st.divider()
st.caption("Propulsé par le système Caleb Stratégos - 2026")
