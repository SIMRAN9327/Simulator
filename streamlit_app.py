import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import time

# Page configuration
st.set_page_config(
    page_title="CyberNet // Hop-by-Hop Packet Tracer",
    page_icon="🚀",
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
    .hop-box {
        background-color: #1e293b;
        border-left: 4px solid #f43f5e;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 CyberNet: Interactive Topology & Hop-by-Hop Packet Tracer")
st.markdown("""
*Configure your network topology, transmission media, and core devices. Click **Send Packet** to watch data hop across computers, switches, and routers in real-time while analyzing OSI layer behaviors.*
""")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🎛️ Network Architecture Setup")

topology = st.sidebar.selectbox("Network Topology", ["Star", "Mesh", "Ring", "Bus"])
media = st.sidebar.selectbox("Transmission Media (Layer 1)", ["Copper (UTP Cat6)", "Fiber Optic", "Wireless Wi-Fi 6"])
device_type = st.sidebar.selectbox("Core Networking Device", ["Layer 2 Switch", "Layer 3 Router", "Traditional Hub"])

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Packet Simulation Control")
source_node = st.sidebar.selectbox("Sender Computer", ["PC-A", "PC-B", "PC-C", "PC-D"])
dest_node = st.sidebar.selectbox("Receiver Computer", ["PC-D", "PC-C", "PC-B", "PC-A"])

# --- TOPOLOGY GRAPH GENERATION ---
G = nx.Graph()
if topology == "Star":
    center = "Core Switch / Router"
    nodes = ["PC-A", "PC-B", "PC-C", "PC-D"]
    G.add_node(center)
    for n in nodes: G.add_edge(center, n)
    pos = nx.spring_layout(G, seed=42)
    pos[center] = (0, 0)
    pos["PC-A"] = (-1, 1)
    pos["PC-B"] = (1, 1)
    pos["PC-C"] = (-1, -1)
    pos["PC-D"] = (1, -1)
elif topology == "Mesh":
    nodes = ["PC-A", "PC-B", "PC-C", "PC-D"]
    G.add_nodes_from(nodes)
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)): G.add_edge(nodes[i], nodes[j])
    pos = nx.spring_layout(G, seed=42)
elif topology == "Ring":
    nodes = ["PC-A", "PC-B", "PC-C", "PC-D"]
    for i in range(len(nodes)): G.add_edge(nodes[i], nodes[(i+1)%len(nodes)])
    pos = nx.circular_layout(nodes)
else: # Bus
    nodes = ["Terminator-1", "PC-A", "PC-B", "PC-C", "PC-D", "Terminator-2"]
    for i in range(len(nodes)-1): G.add_edge(nodes[i], nodes[i+1])
    pos = {n: (i*2, 0) for i, n in enumerate(nodes)}

# --- TABS ---
tab1, tab2 = st.tabs(["🗺️ Live Network Map & Packet Animation", "📦 OSI Layer & Device Interaction Log"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎮 Live Control Panel")
        
        # Trigger packet simulation
        if st.button("🚀 Send Packet (Start Hop Simulation)", type="primary"):
            if source_node == dest_node:
                st.warning("Source and destination cannot be the same computer!")
            else:
                st.session_state['animating'] = True
        
        # Performance metric calculations
        base_lat = 5 if "Fiber" in media else (15 if "Copper" in media else 40)
        if device_type == "Traditional Hub": base_lat *= 2 # Hubs cause collision delays
        loss = 0.0 if "Fiber" in media else (0.5 if "Copper" in media else 3.5)
        if topology == "Bus": loss += 2.0

        st.metric("Estimated Hop Latency", f"{base_lat * 2} ms")
        st.metric("Packet Delivery Health", f"{max(0, 100 - loss):.1f}%")

        st.markdown(f"""
        <div class="card">
        <b>Active Setup Rules:</b><br>
        * <b>Media:</b> {media} (Layer 1 signals)<br>
        * <b>Device:</b> {device_type} ({'Broadcasts all traffic' if device_type=='Traditional Hub' else 'Smart packet forwarding'})<br>
        * <b>Path:</b> {source_node} ➔ {topology} Network ➔ {dest_node}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.subheader(f"🗺️ Visual Topology: {topology}")
        
        # Draw NetworkX graph using Plotly
        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        node_text = list(G.nodes())

        net_fig = go.Figure()
        net_fig.add_trace(go.Scatter(x=edge_x, y=edge_y, line=dict(width=2, color='#38bdf8'), mode='lines'))
        net_fig.add_trace(go.Scatter(x=node_x, y=node_y, mode='text+markers',
            marker=dict(size=20, color='#f43f5e', line=dict(width=2, color='#ffffff')),
            text=node_text, textposition="top center"))
        
        net_fig.update_layout(showlegend=False, xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(net_fig, use_container_width=True)

with tab2:
    st.subheader("📦 Live Packet Journey & OSI Device Processing")
    
    if st.session_state.get('animating', False):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        hops = [
            f"Step 1: [{source_node}] Layer 7-4 -> Application data created, wrapped in TCP segments & IP packets.",
            f"Step 2: [{source_node}] Layer 2-1 -> Encapsulated into Ethernet Frames and transmitted via {media}.",
            f"Step 3: [Core Device: {device_type}] Layer 2/3 Processing -> Inspecting MAC/IP destination headers.",
            f"Step 4: [Network Transit] Packet moving across {topology} topology links without collisions.",
            f"Step 5: [{dest_node}] Layer 1-7 Decapsulation -> Stripping headers, verifying CRC, delivering payload."
        ]
        
        for i, hop in enumerate(hops):
            status_text.markdown(f"<div class='hop-box'>⚡ {hop}</div>", unsafe_allow_html=True)
            progress_bar.progress((i + 1) * 20)
            time.sleep(0.8)
            
        st.success(f"✅ Packet successfully transmitted from {source_node} to {dest_node}!")
        st.session_state['animating'] = False
    else:
        st.info("👈 Go to the first tab, configure your network, and click **'🚀 Send Packet'** to watch the packet hop-by-hop traversal log!")

        st.markdown("""
        <div class="card">
        <b>What this demonstrates for your evaluation:</b><br>
        * <b>Device Role:</b> Shows the difference between a dumb <i>Hub</i> (broadcasts everything) vs a smart <i>Switch/Router</i>.<br>
        * <b>Encapsulation:</b> Displays how computers wrap data before sending it across physical media.
        </div>
        """, unsafe_allow_html=True)
