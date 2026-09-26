import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import numpy as np

# Page configuration
st.set_page_config(
    page_title="CyberNet // Enterprise Architect & OSI Engine",
    page_icon="🧠",
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
</style>
""", unsafe_allow_html=True)

st.title("🧠 CyberNet: Smart Network Architect & Protocol Analyzer")
st.markdown("""
*An intelligent simulation tool for designing enterprise networks. Define your constraints (nodes, distance, budget) and let the engine recommend the optimal topology, transmission media, and analyze OSI layer encapsulation.*
""")

# --- SIDEBAR: SCENARIO CONSTRAINTS ---
st.sidebar.header("🏢 Project Constraints & Goals")

num_nodes = st.sidebar.slider("Number of Computers / Nodes", 2, 50, 10)
scale = st.sidebar.selectbox("Deployment Scale", ["Single Room / Lab", "Office Building", "City-Wide WAN"])
budget = st.sidebar.selectbox("Budget Constraint", ["Low-Cost (Budget)", "Moderate", "Enterprise (Unlimited)"])
priority = st.sidebar.selectbox("Primary Optimization Goal", ["Maximum Speed / Bandwidth", "High Reliability / Redundancy", "Lowest Cost"])

# --- INTELLIGENT RECOMMENDATION ENGINE ---
rec_media = "Fiber Optic" if scale == "City-Wide WAN" or (priority == "Maximum Speed / Bandwidth" and budget != "Low-Cost (Budget)") else ("Copper (UTP)" if budget != "Enterprise (Unlimited)" else "Wireless / Wi-Fi")
rec_topo = "Mesh" if priority == "High Reliability / Redundancy" else ("Star" if num_nodes <= 30 else "Bus")

st.sidebar.markdown("---")
st.sidebar.subheader("💡 AI Architect Recommendation")
st.sidebar.success(f"**Recommended Media:** {rec_media}\n\n**Recommended Topology:** {rec_topo}")

# Allow manual override or use AI choice
use_ai = st.sidebar.checkbox("Use AI Recommendation", value=True)
if use_ai:
    media = rec_media
    topology = rec_topo
else:
    media = st.sidebar.selectbox("Manual Media Override", ["Fiber Optic", "Copper (UTP)", "Wireless / Wi-Fi"])
    topology = st.sidebar.selectbox("Manual Topology Override", ["Star", "Mesh", "Bus", "Ring"])

# --- PERFORMANCE & COST CALCULATION ---
cost_factor = {"Fiber Optic": 3.0, "Copper (UTP)": 1.0, "Wireless / Wi-Fi": 0.5}[media]
topo_cost = {"Star": 1.5, "Mesh": 3.5, "Bus": 0.8, "Ring": 2.0}[topology]
estimated_cost = int(num_nodes * cost_factor * topo_cost * 120)

bandwidth = 10000 if media == "Fiber Optic" else (1000 if media == "Copper (UTP)" else 300)
latency = 2 if media == "Fiber Optic" else (12 if media == "Copper (UTP)" else 45)
if topology == "Bus": latency *= 2.5

# --- TABS FOR STRUCTURED PRESENTATION ---
tab1, tab2 = st.tabs(["🌐 Network Topology & Cost Analysis", "📚 OSI Model & Packet Encapsulation Engine"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 Scenario Evaluation & Trade-offs")
        m1, m2, m3 = st.columns(3)
        m1.metric("Est. Setup Cost", f"${estimated_cost:,}")
        m2.metric("Latency", f"{latency} ms")
        m3.metric("Bandwidth", f"{bandwidth} Mbps")
        
        # Scenario feedback based on real constraints
        if scale == "Single Room / Lab" and media == "Fiber Optic":
            st.warning("⚠️ **Over-engineered:** Fiber optic is expensive and unnecessary for a single room. Copper UTP is recommended.")
        elif scale == "City-Wide WAN" and media == "Copper (UTP)":
            st.error("🚨 **Deployment Failure:** Copper cables suffer from signal attenuation beyond 100 meters. Fiber is mandatory.")
        else:
            st.success("✅ **Configuration matches constraints successfully!**")

        st.markdown(f"""
        <div class="card">
        <b>Why this setup?</b><br>
        * <b>Topology ({topology}):</b> Chosen for {priority.lower()} across {num_nodes} nodes.<br>
        * <b>Media ({media}):</b> Fits your {budget.lower()} tier while handling {scale.lower()} distances.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.subheader(f"🗺️ Visualizing {num_nodes} Nodes in {topology} Topology")
        
        G = nx.Graph()
        if topology == "Star":
            G.add_node("Central Switch")
            for i in range(1, min(num_nodes+1, 15)): G.add_edge("Central Switch", f"PC-{i}")
            pos = nx.spring_layout(G, seed=42)
        elif topology == "Mesh":
            nodes = [f"Router-{i}" for i in range(1, min(num_nodes+1, 8))]
            G.add_nodes_from(nodes)
            for i in range(len(nodes)):
                for j in range(i+1, len(nodes)): G.add_edge(nodes[i], nodes[j])
            pos = nx.spring_layout(G, seed=42)
        elif topology == "Bus":
            nodes = [f"Node-{i}" for i in range(1, min(num_nodes+1, 10))]
            for i in range(len(nodes)-1): G.add_edge(nodes[i], nodes[i+1])
            pos = {node: (i * 2, 0) for i, node in enumerate(nodes)}
        else:  # Ring
            nodes = [f"Node-{i}" for i in range(1, min(num_nodes+1, 10))]
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
            marker=dict(size=14, color='#f43f5e', line=dict(width=2, color='#ffffff')),
            text=node_text, textposition="top center"))
        
        topo_fig.update_layout(showlegend=False, xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=320)
        st.plotly_chart(topo_fig, use_container_width=True)

with tab2:
    st.subheader("📚 Dynamic OSI Encapsulation & Protocol Stack")
    st.markdown("See how data passes through the OSI model using your selected parameters:")

    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.markdown("""
        <div class="card">
        <b>Layer 7: Application Layer</b><br>
        <span style="color:#94a3b8;">User interaction protocols: HTTP, HTTPS, DNS, FTP. Data originates here.</span>
        </div>
        <div class="card">
        <b>Layer 6 & 5: Presentation & Session</b><br>
        <span style="color:#94a3b8;">Handles SSL/TLS encryption, data compression, and session dialog management.</span>
        </div>
        <div class="card">
        <b>Layer 4: Transport Layer</b><br>
        <span style="color:#94a3b8;">Protocols: TCP (Reliable stream with acknowledgment) or UDP (Unreliable speed). Breaks data into segments.</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col_b:
        st.markdown(f"""
        <div class="card">
        <b>Layer 3: Network Layer (Routing)</b><br>
        <span style="color:#38bdf8;">Active Protocol: IPv4 / IPv6. Handles logical packet addressing across <b>{topology}</b> topology.</span>
        </div>
        <div class="card">
        <b>Layer 2: Data Link Layer (Framing)</b><br>
        <span style="color:#38bdf8;">Active Framing: Ethernet MAC headers and switches controlling frame collisions.</span>
        </div>
        <div class="card">
        <b>Layer 1: Physical Layer (Transmission Media)</b><br>
        <span style="color:#38bdf8;">Active Medium: <b>{media}</b> translating bits into light pulses, electrical voltage, or RF waves.</span>
        </div>
        """, unsafe_allow_html=True)
