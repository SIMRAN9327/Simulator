import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import numpy as np

# Page configuration
st.set_page_config(
    page_title="CyberNet // Advanced Network Visualizer",
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
    .osi-card {
        background-color: #111827;
        border-left: 4px solid #38bdf8;
        padding: 10px 15px;
        margin-bottom: 8px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌐 CyberNet: Interactive Core Networking Visualizer")
st.markdown("""
*An advanced visual simulator for B.Tech networking fundamentals. Change the topology and media to see the network layout and performance metrics update live.*
""")

# --- SIDEBAR: CONTROLS ---
st.sidebar.header("🎛️ Network Configuration")

media = st.sidebar.selectbox(
    "Transmission Media (Layer 1)",
    ["Fiber Optic", "Copper (UTP)", "Wireless / Wi-Fi"]
)

topology = st.sidebar.selectbox(
    "Network Topology (Layer 2 & 3)",
    ["Star", "Mesh", "Bus", "Ring"]
)

architecture = st.sidebar.selectbox(
    "Network Architecture",
    ["Client-Server", "Peer-to-Peer (P2P)"]
)

# --- PERFORMANCE ENGINE ---
media_stats = {
    "Fiber Optic": {"delay": 3, "speed": 10000, "loss": 0.0},
    "Copper (UTP)": {"delay": 15, "speed": 1000, "loss": 0.4},
    "Wireless / Wi-Fi": {"delay": 40, "speed": 300, "loss": 3.5}
}

topo_multiplier = {"Star": 1.0, "Mesh": 0.8, "Bus": 2.4, "Ring": 1.6}

base_delay = media_stats[media]["delay"] * topo_multiplier[topology]
max_speed = media_stats[media]["speed"] / topo_multiplier[topology]
packet_loss = media_stats[media]["loss"] + (2.0 if topology == "Bus" else 0.0)

# --- LAYOUT: METRICS & TOPOLOGY ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Performance Metrics")
    m1, m2, m3 = st.columns(3)
    m1.metric("Latency", f"{base_delay:.1f} ms")
    m2.metric("Throughput", f"{max_speed:.0f} Mbps")
    m3.metric("Packet Loss", f"{packet_loss:.1f}%")
    
    # Visual Topology Generator using NetworkX & Plotly
    st.subheader(f"🗺️ Live Topology Map: {topology} Topology")
    
    G = nx.Graph()
    if topology == "Star":
        G.add_node("Switch / Hub (Center)")
        for i in range(1, 6): G.add_edge("Switch / Hub (Center)", f"Node PC-{i}")
        pos = nx.spring_layout(G, seed=42)
    elif topology == "Mesh":
        nodes = [f"Router-{i}" for i in range(1, 5)]
        G.add_nodes_from(nodes)
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)): G.add_edge(nodes[i], nodes[j])
        pos = nx.spring_layout(G, seed=42)
    elif topology == "Bus":
        nodes = [f"Node-{i}" for i in range(1, 6)]
        for i in range(len(nodes)-1): G.add_edge(nodes[i], nodes[i+1])
        pos = {node: (i * 2, 0) for i, node in enumerate(nodes)}
    else:  # Ring
        nodes = [f"Node-{i}" for i in range(1, 6)]
        for i in range(len(nodes)): G.add_edge(nodes[i], nodes[(i+1)%len(nodes)])
        pos = nx.circular_layout(nodes)

    # Extract coordinates for Plotly lines and nodes
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

with col2:
    st.subheader("📚 OSI & TCP/IP Model Stack with Protocols")
    st.markdown("Dynamic layer mapping based on your selections:")
    
    # Interactive OSI Stack Representation
    st.markdown("""
    <div class="osi-card"><b>Layer 7: Application</b><br><span style="color:#94a3b8;">Protocols: HTTP, HTTPS, FTP, DNS (Architecture: <b>""" + architecture + """</b>)</span></div>
    <div class="osi-card"><b>Layer 4: Transport</b><br><span style="color:#94a3b8;">Protocols: TCP (Reliable stream), UDP (Fast/Streaming)</span></div>
    <div class="osi-card"><b>Layer 3: Network</b><br><span style="color:#94a3b8;">Protocols: IPv4, IPv6, ICMP (Topology: <b>""" + topology + """</b> routing)</span></div>
    <div class="osi-card"><b>Layer 2: Data Link</b><br><span style="color:#94a3b8;">Protocols: Ethernet, MAC Addressing, Framing</span></div>
    <div class="osi-card"><b>Layer 1: Physical</b><br><span style="color:#94a3b8;">Medium: <b>""" + media + """</b> (Signals, light pulses, or radio waves)</span></div>
    """, unsafe_allow_html=True)

    st.markdown("### 📈 Traffic vs. Latency Simulation Curve")
    loads = np.linspace(10, 100, 15)
    latencies = base_delay + (loads * 0.25 * topo_multiplier[topology])
    
    curve_fig = go.Figure()
    curve_fig.add_trace(go.Scatter(x=loads, y=latencies, mode='lines+markers', line=dict(color='#38bdf8', width=3)))
    curve_fig.update_layout(xaxis_title="Network Load (%)", yaxis_title="Latency (ms)",
                            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=220)
    st.plotly_chart(curve_fig, use_container_width=True)
