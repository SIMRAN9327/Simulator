import streamlit as st
import plotly.graph_objects as go
import numpy as np
import math

# Page configuration
st.set_page_config(
    page_title="CyberNet // Global WAN & OSI Simulator",
    page_icon="🌍",
    layout="wide"
)

# --- FUTURISTIC DARK THEME CSS ---
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    h1, h2, h3 {
        color: #38bdf8 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .card {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .osi-step {
        background-color: #1e293b;
        border-left: 4px solid #38bdf8;
        padding: 8px 12px;
        margin: 5px 0;
        font-size: 14px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌍 CyberNet: Global WAN, Routing & OSI Packet Journey")
st.markdown("""
*Simulate intercontinental data transmission across global coordinates. Track physics-based latency, submarine fiber/satellite degradation, and step-by-step OSI packet encapsulation.*
""")

# --- COUNTRY COORDINATES & DATABASE ---
locations = {
    "India (Mumbai)": {"lat": 19.0760, "lon": 72.8777},
    "USA (New York)": {"lat": 40.7128, "lon": -74.0060},
    "Germany (Frankfurt)": {"lat": 50.1109, "lon": 8.6821},
    "Japan (Tokyo)": {"lat": 35.6762, "lon": 139.6503},
    "Australia (Sydney)": {"lat": -33.8688, "lon": 151.2093},
    "Brazil (São Paulo)": {"lat": -23.5505, "lon": -46.6333}
}

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🌐 Global Routing Parameters")

source_country = st.sidebar.selectbox("Source Country (Sender)", list(locations.keys()), index=0)
dest_country = st.sidebar.selectbox("Destination Country (Receiver)", list(locations.keys()), index=1)

transmission_medium = st.sidebar.selectbox(
    "Long-Haul Transmission Medium", 
    ["Submarine Fiber Optic Cable", "Geostationary Satellite Link"]
)

traffic_congestion = st.sidebar.slider("Router Queue Congestion (%)", 0, 100, 15)

# --- HAVERSINE DISTANCE CALCULATION ---
def get_distance(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

lat1, lon1 = locations[source_country]["lat"], locations[source_country]["lon"]
lat2, lon2 = locations[dest_country]["lat"], locations[dest_country]["lon"]
distance_km = get_distance(lat1, lon1, lat2, lon2)

# --- PHYSICS & NETWORK CALCULATIONS ---
# Speed of light in fiber ~ 200,000 km/s. In Satellite ~ 300,000 km/s (but travels 36,000km up & down twice)
if "Fiber" in transmission_medium:
    propagation_delay = (distance_km / 200000.0) * 1000  # in ms (round trip or one-way factor)
    base_loss = 0.05
else: # Satellite
    propagation_delay = 550.0 + (distance_km / 300000.0) * 1000 # High fixed satellite latency
    base_loss = 2.5

congestion_delay = traffic_congestion * 0.8
total_latency = (propagation_delay * 1.5) + congestion_delay
packet_loss_rate = base_loss + (traffic_congestion * 0.08)
if source_country == dest_country:
    total_latency = 2.0
    packet_loss_rate = 0.0
    distance_km = 0

# --- TABS FOR STRUCTURED PRESENTATION ---
tab1, tab2 = st.tabs(["🗺️ Global Map & WAN Performance", "📦 OSI Model Packet Encapsulation & Journey"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 Global Transmission Metrics")
        m1, m2, m3 = st.columns(3)
        m1.metric("Geographic Distance", f"{distance_km:,.0f} km")
        m2.metric("Total Latency (RTT)", f"{total_latency:.1f} ms")
        m3.metric("Packet Loss Rate", f"{packet_loss_rate:.2f}%")
        
        if packet_loss_rate < 1.0:
            st.success("🟢 **WAN Link Status: Excellent Transmission Quality**")
        elif 1.0 <= packet_loss_rate < 5.0:
            st.warning("🟡 **WAN Link Status: Moderate Jitter & Latency**")
        else:
            st.error("🔴 **WAN Link Status: High Packet Loss / Congestion Drop**")

        st.markdown(f"""
        <div class="card">
        <b>Physics Behind the Link:</b><br>
        * <b>Medium ({transmission_medium}):</b> Light travels slower through glass fiber (~200,000 km/s) than a vacuum. Satellites require signals to travel to space and back, causing high fixed delay (~500ms+).<br>
        * <b>Congestion Impact:</b> Router buffers fill up when traffic hits {traffic_congestion}%, causing queue delays.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.subheader(f"🗺️ Active Fiber Arc: {source_country} ➔ {dest_country}")
        
        # Plotly Geo Map
        fig = go.Figure(go.Scattergeo(
            lat=[lat1, lat2],
            lon=[lon1, lon2],
            mode='lines+markers',
            line=dict(width=3, color='#38bdf8' if "Fiber" in transmission_medium else '#f43f5e'),
            marker=dict(size=10, color='#f43f5e')
        ))
        
        fig.update_geos(
            projection_type="orthographic",
            showland=True, landcolor="#111827",
            showocean=True, oceancolor="#030712",
            showcountries=True, countrycolor="#1f2937"
        )
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📦 Step-by-Step OSI Packet Encapsulation & Transmission")
    st.markdown(f"Simulating a data packet traveling from **{source_country}** to **{dest_country}**:")

    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.markdown("### 📤 Sender Side (Encapsulation)")
        st.markdown("""
        <div class="osi-step"><b>1. Application (Layer 7):</b> User creates HTTP GET request payload.</div>
        <div class="osi-step"><b>2. Presentation/Session (Layers 6-5):</b> Data is encrypted (TLS) and session is established.</div>
        <div class="osi-step"><b>3. Transport (Layer 4):</b> Payload broken into TCP Segments + Ports added.</div>
        <div class="osi-step"><b>4. Network (Layer 3):</b> Source & Destination IP headers attached (IPv4/IPv6).</div>
        <div class="osi-step"><b>5. Data Link (Layer 2):</b> MAC addresses and frame checksum added.</div>
        <div class="osi-step"><b>6. Physical (Layer 1):</b> Converted to light pulses for <b>""" + transmission_medium + """</b>.</div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("### 📥 Receiver Side (Decapsulation & Delivery)")
        st.markdown(f"""
        <div class="osi-step"><b>Transit:</b> Traveled {distance_km:,.0f} km across international borders via undersea cables/satellites.</div>
        <div class="osi-step"><b>Packet Loss Check:</b> {packet_loss_rate:.2f}% chance of bit corruption/drop due to distance and congestion.</div>
        <div class="osi-step"><b>Layer 1-3 Stripping:</b> Physical signals decoded, MAC frames checked, IP destination verified.</div>
        <div class="osi-step"><b>Layer 4 Verification:</b> TCP sends ACK back to sender. If packets dropped, retransmission triggered.</div>
        <div class="osi-step"><b>Layer 7 Delivery:</b> Data reassembled and rendered on the destination application screen!</div>
        """, unsafe_allow_html=True)
