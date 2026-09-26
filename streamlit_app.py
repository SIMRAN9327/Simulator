import streamlit as st
import plotly.graph_objects as go
import networkx as nx

# Page configuration
st.set_page_config(
    page_title="CyberNet // Core Networking Fundamentals",
    page_icon="🌐",
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
    .osi-card {
        background-color: #1e293b;
        border-left: 4px solid #38bdf8;
        padding: 10px 15px;
        margin-bottom: 8px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌐 CyberNet: Core Networking Fundamentals Visualizer")
st.markdown("""
*An interactive simulation tool built for second-year computer networking students. Change transmission media, topologies, and networking devices to see how physical and logical layers impact performance.*
""")

# --- SIDEBAR: CORE NETWORKING OPTIONS ---
st.sidebar.header("🎛️ Network Parameters")

topology = st.sidebar.selectbox(
    "1. Network Topology (Layer 3)",
    ["Star", "Mesh", "Ring", "Bus"]
)

media = st.sidebar.selectbox(
    "2. Transmission Media (Layer 1)",
    ["Copper (UTP Cat6)", "Fiber Optic", "Wireless / Wi-Fi"]
)

device = st.sidebar.selectbox(
    "3. Core Networking Device",
    ["Layer 2 Switch (Smart Forwarding)", "Layer 3 Router (Packet Routing)", "Traditional Hub (Dumb Broadcast)"]
)

architecture = st.sidebar.selectbox(
    "4. Network Architecture",
    ["Client-Server", "Peer-to-Peer (P2P)"]
)

# --- PERFORMANCE ENGINE ---
media_speed = {"Fiber Optic": 10000, "Copper (UTP Cat6)": 1000, "Wireless / Wi-Fi": 300}[media]
base_latency = {"Fiber Optic": 3, "Copper (UTP Cat6)": 10, "Wireless / Wi-Fi": 35}[media]

# Device impact
if "Hub" in device:
    base_latency *= 2.5
    collision_risk = "High (Collision Domain)"
elif "Switch" in device:
    collision_risk = "None (Separated Collision Domains)"
else:
    collision_risk = "None (Routed Subnets)"

# Topology multiplier
topo_multiplier = {"Star": 1.0, "Mesh": 0.8, "Ring": 1.4, "Bus": 2.2}[topology]
final_latency = base_latency * topo_multiplier
final_throughput = media_speed / topo_multiplier

# --- TABS FOR CLEAN PRESENTATION ---
tab1, tab2 = st.tabs(["🗺️ Visual Topology & Performance", "📚 OSI / TCP Model Protocol Stack"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 Performance Metrics")
        m1, m2, m3 = st.columns(3)
        m1.metric("Calculated Latency", f"{final_latency:.1f} ms")
        m2.metric("Effective Throughput", f"{final_throughput:.0f} Mbps")
        m3.metric("Collision Domain", collision_risk)
        
        st.markdown(f"""
        <div class="card">
        <b>Syllabus Concept Analysis:</b><br>
        * <b>Topology ({topology}):</b> Defines how nodes are physically and logically interconnected.<br>
        * <b>Media ({media}):</b> Determines signal attenuation and maximum bandwidth capabilities.<br>
        * <b>Device ({device}):</b> Dictates whether traffic is intelligently switched or blindly broadcasted.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.subheader(f"🗺️ Live Topology Rendering: {topology}")
        
        G = nx.Graph()
        if topology == "Star":
            center = "Central Switch/Hub"
            G.add_node(center)
            for i in range(1, 5): G.add_edge(center, f"PC-{i}")
            pos = nx.spring_layout(G, seed=42)
            pos[center] = (0, 0)
            pos["PC-1"] = (-1, 1)
            pos["PC-2"] = (1, 1)
            pos["PC-3"] = (-1, -1)
            pos["PC-4"] = (1, -1)
        elif topology == "Mesh":
            nodes = ["PC-1", "PC-2", "PC-3", "PC-4"]
            G.add_nodes_from(nodes)
            for i in range(len(nodes)):
                for j in range(i+1, len(nodes)): G.add_edge(nodes[i], nodes[j])
            pos = nx.spring_layout(G, seed=42)
        elif topology == "Bus":
            nodes = ["Term-1", "PC-1", "PC-2", "PC-3", "PC-4", "Term-2"]
            for i in range(len(nodes)-1): G.add_edge(nodes[i], nodes[i+1])
            pos = {n: (i * 1.5, 0) for i, n in enumerate(nodes)}
        else: # Ring
            nodes = ["PC-1", "PC-2", "PC-3", "PC-4"]
            for i in range(len(nodes)): G.add_edge(nodes[i], nodes[(i+1)%len(nodes)])
            pos = nx.circular_layout(nodes)

        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        node_text = list(G.nodes())

        topo_fig = go.Figure()
        topo_fig.add_trace(go.Scatter(x=edge_x, y=edge_y, line=dict(width=2, color='#38bdf8'), mode='lines'))
        topo_fig.add_trace(go.Scatter(x=node_x, y=node_y, mode='text+markers',
            marker=dict(size=18, color='#f43f5e', line=dict(width=2, color='#ffffff')),
            text=node_text, textposition="top center"))
        
        topo_fig.update_layout(showlegend=False, xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=320)
        st.plotly_chart(topo_fig, use_container_width=True)

with tab2:
    st.subheader("📚 OSI Model & Protocol Stack Mapping")
    st.markdown(f"Dynamic layer breakdown based on your active network choices:")

    st.markdown(f"""
    <div class="osi-card"><b>Layer 7: Application Layer</b><br><span style="color:#94a3b8;">Protocols: HTTP, HTTPS, DNS, FTP | Architecture: <b>{architecture}</b></span></div>
    <div class="osi-card"><b>Layer 4: Transport Layer</b><br><span style="color:#94a3b8;">Protocols: TCP (Connection-oriented, reliable) & UDP (Connectionless, fast stream)</span></div>
    <div class="osi-card"><b>Layer 3: Network Layer</b><br><span style="color:#94a3b8;">Protocols: IPv4, IPv6, ICMP | Routing across <b>{topology}</b> topology via <b>{device}</b></span></div>
    <div class="osi-card"><b>Layer 2: Data Link Layer</b><br><span style="color:#94a3b8;">Protocols: Ethernet MAC addressing, Framing, Error detection (CRC)</span></div>
    <div class="osi-card"><b>Layer 1: Physical Layer</b><br><span style="color:#94a3b8;">Transmission Media: <b>{media}</b> (Converts data bits into electrical signals, light pulses, or RF waves)</span></div>
    """, unsafe_allow_html=True)
