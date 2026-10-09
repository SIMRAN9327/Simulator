import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import numpy as np
import random

# Page configuration
st.set_page_config(
    page_title="CyberNet // Core Networking Fundamentals",
    page_icon="🌐",
    layout="wide"
)

# --- HIGH-CONTRAST FUTURISTIC DARK THEME CSS ---
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    h1, h2, h3 {
        color: #38bdf8 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .card {
        background-color: #111827;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .metric-card {
        background-color: #111827;
        border: 1px solid #334155;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 15px;
    }
    .osi-card {
        background-color: #1e293b;
        border-left: 4px solid #38bdf8;
        padding: 12px 18px;
        margin-bottom: 10px;
        border-radius: 4px;
    }
    .success-box {
        background-color: #022c22;
        border-left: 4px solid #34d399;
        padding: 15px;
        border-radius: 6px;
        font-family: monospace;
        margin-top: 10px;
        color: #a7f3d0;
    }
    .error-box {
        background-color: #450a0a;
        border-left: 4px solid #fb7185;
        padding: 15px;
        border-radius: 6px;
        font-family: monospace;
        margin-top: 10px;
        color: #fecdd3;
    }
    .ai-badge {
        background-color: #17153a;
        border: 1px solid #6366f1;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
    }
    .disadvantage-box {
        background-color: #18181b;
        border: 1px solid #3f3f46;
        border-left: 4px solid #f59e0b;
        padding: 15px;
        border-radius: 6px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌐 CyberNet: AI-Powered Networking & Topology Analyzer")
st.markdown("""
*An advanced interactive simulation tool built for computer networking students. Configure up to **100 nodes** and span distances **up to 20,000 km (WAN/Global)** with high-visibility graphics.*
""")

# --- SIDEBAR: PARAMETERS & AI RECOMMENDATIONS ---
st.sidebar.header("🎛️ Network Parameters")

num_nodes = st.sidebar.slider("Number of Nodes", min_value=3, max_value=100, value=12, help="Total client endpoints in the network.")
distance_m = st.sidebar.number_input("Maximum Distance Span (meters)", min_value=10, max_value=20000000, value=500000, step=1000, help="Longest physical distance between nodes (up to 20,000 km).")

if distance_m >= 1000:
    dist_str = f"{distance_m / 1000:,.1f} km"
else:
    dist_str = f"{distance_m:,} meters"

# --- SCALED AI RECOMMENDATION LOGIC ---
if distance_m > 500000:
    rec_topo = "Mesh"
    topo_reason = "Long-haul WAN/Global scale requires Mesh for multi-path redundancy."
elif num_nodes <= 24:
    rec_topo = "Star"
    topo_reason = "Ideal for standard switch port densities with centralized management."
elif num_nodes <= 60:
    rec_topo = "Ring"
    topo_reason = "Efficient for medium-large node counts with deterministic token passing."
else:
    rec_topo = "Mesh"
    topo_reason = "High node count requires redundant paths for fault tolerance."

if distance_m <= 100:
    rec_media = "Copper (UTP Cat6)"
    media_reason = "Ideal for short distances (<100m)."
elif distance_m <= 100000:
    rec_media = "Fiber Optic"
    media_reason = "Essential for medium-to-long campus and MAN distances."
else:
    rec_media = "Satellite / Intercontinental WAN Link"
    media_reason = "Mandatory for extreme long-distance intercontinental transmissions."

# Enhanced high-contrast AI Recommendation Card
st.sidebar.markdown(f"""
<div class="ai-badge">
    <b style="color: #f8fafc; font-size: 1rem;">🤖 AI Advisor Recommendations</b><br>
    <hr style="border: 0; border-top: 1px solid #3730a3; margin: 8px 0;">
    <span style="color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; font-weight: 600;">Distance Span</span><br>
    <span style="color:#38bdf8; font-weight:bold; font-size: 1.05rem;">{dist_str}</span><br><br>
    
    <span style="color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; font-weight: 600;">Recommended Topology</span><br>
    <span style="color:#c084fc; font-weight:bold; font-size: 1.05rem;">{rec_topo}</span><br>
    <small style="color:#cbd5e1; font-style: italic;">{topo_reason}</small><br><br>
    
    <span style="color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; font-weight: 600;">Recommended Media</span><br>
    <span style="color:#34d399; font-weight:bold; font-size: 1.05rem;">{rec_media}</span><br>
    <small style="color:#cbd5e1; font-style: italic;">{media_reason}</small>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

topology = st.sidebar.selectbox(
    "1. Select Network Topology",
    ["Star", "Mesh", "Ring", "Bus"],
    index=["Star", "Mesh", "Ring", "Bus"].index(rec_topo) if rec_topo in ["Star", "Mesh", "Ring", "Bus"] else 0
)

media = st.sidebar.selectbox(
    "2. Select Transmission Media (Layer 1)",
    ["Copper (UTP Cat6)", "Fiber Optic", "Wireless / Wi-Fi", "Satellite / WAN Link"],
    index=1 if distance_m > 100 else 0
)

device = st.sidebar.selectbox(
    "3. Core Networking Device",
    ["Layer 3 Router (WAN / Packet Routing)", "Layer 2 Switch (Smart Forwarding)", "Traditional Hub (Dumb Broadcast)"]
)

architecture = st.sidebar.selectbox(
    "4. Network Architecture",
    ["Client-Server", "Peer-to-Peer (P2P)", "Cloud / Hybrid WAN"]
)

if 'prev_topo' not in st.session_state or st.session_state['prev_topo'] != topology:
    st.session_state['link_failed'] = False
    st.session_state['last_packet'] = None
    st.session_state['prev_topo'] = topology

if 'link_failed' not in st.session_state:
    st.session_state['link_failed'] = False
if 'last_packet' not in st.session_state:
    st.session_state['last_packet'] = None

# --- PERFORMANCE & PROPAGATION ENGINE ---
media_speed_map = {"Copper (UTP Cat6)": 1000, "Fiber Optic": 10000, "Wireless / Wi-Fi": 300, "Satellite / WAN Link": 150}
media_speed = media_speed_map.get(media, 1000)

if "Fiber" in media:
    prop_velocity = 200000000
elif "Satellite" in media:
    prop_velocity = 299792458
else:
    prop_velocity = 200000000

propagation_latency_ms = (distance_m / prop_velocity) * 1000
base_processing_latency = 5

if "Hub" in device:
    base_processing_latency *= 2.5
    collision_risk = "High (Collision Domain)"
elif "Switch" in device:
    collision_risk = "None (Separated)"
else:
    collision_risk = "None (Routed)"

topo_multiplier = {"Star": 1.0, "Mesh": 0.8, "Ring": 1.4, "Bus": 2.2}[topology]
final_latency = base_processing_latency + (propagation_latency_ms * topo_multiplier)
final_throughput = max(10, media_speed / (topo_multiplier * (1 + num_nodes/200)))

# --- BUILD DYNAMIC NETWORK GRAPH ---
G = nx.Graph()
node_names = [f"PC-{i+1}" for i in range(num_nodes)]

if topology == "Star":
    center = "Central Gateway / Switch"
    G.add_node(center)
    for n in node_names:
        G.add_edge(center, n)
    pos = nx.spring_layout(G, seed=42, k=1.5/np.sqrt(num_nodes))
    pos[center] = (0, 0)
elif topology == "Mesh":
    G.add_nodes_from(node_names)
    if num_nodes > 30:
        for i in range(len(node_names)):
            for j in range(i+1, min(i+6, len(node_names))):
                G.add_edge(node_names[i], node_names[j])
    else:
        for i in range(len(node_names)):
            for j in range(i+1, len(node_names)):
                G.add_edge(node_names[i], node_names[j])
    pos = nx.spring_layout(G, seed=42)
elif topology == "Bus":
    bus_nodes = ["Term-1"] + node_names + ["Term-2"]
    for i in range(len(bus_nodes)-1):
        G.add_edge(bus_nodes[i], bus_nodes[i+1])
    pos = {n: (i * 0.8, 0) for i, n in enumerate(bus_nodes)}
else: # Ring
    G.add_nodes_from(node_names)
    for i in range(len(node_names)):
        G.add_edge(node_names[i], node_names[(i+1)%len(node_names)])
    pos = nx.circular_layout(node_names)

# --- TABS FOR PRESENTATION ---
tab1, tab2, tab3 = st.tabs(["🗺️ Visual Topology & Packet Simulator", "📦 Frame Transmission & Medium Visuals", "📚 OSI & Topology Trade-offs"])

with tab1:
    col_metrics, col_viz = st.columns([1, 1], gap="large")
    
    with col_metrics:
        st.subheader("📊 Performance Metrics")
        m1, m2, m3 = st.columns(3)
        
        m1.markdown(f"""
        <div class="metric-card">
            <span style="color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">Calculated Latency</span><br>
            <span style="color: #38bdf8; font-size: 1.35rem; font-weight: bold;">{final_latency:.1f} ms</span>
        </div>
        """, unsafe_allow_html=True)
        
        m2.markdown(f"""
        <div class="metric-card">
            <span style="color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">Throughput</span><br>
            <span style="color: #34d399; font-size: 1.35rem; font-weight: bold;">{final_throughput:.0f} Mbps</span>
        </div>
        """, unsafe_allow_html=True)
        
        m3.markdown(f"""
        <div class="metric-card">
            <span style="color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">Collision Domain</span><br>
            <span style="color: #f59e0b; font-size: 1.05rem; font-weight: bold;">{collision_risk}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # --- PACKET TRANSMISSION SIMULATOR ---
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📦 Packet Transmission Simulation")
        
        pc_nodes = [n for n in G.nodes() if "PC" in n]
        if len(pc_nodes) >= 2:
            col_s, col_d = st.columns(2)
            source_node = col_s.selectbox("SOURCE", pc_nodes, index=0)
            dest_node = col_d.selectbox("DESTINATION", pc_nodes, index=min(1, len(pc_nodes)-1))
            
            protocol = st.radio("Protocol:", ["TCP", "UDP"], horizontal=True)
            
            col_btn1, col_btn2 = st.columns(2)
            send_clicked = col_btn1.button("🚀 SEND PACKET", type="primary")
            fail_clicked = col_btn2.button("💥 Simulate Link Failure")
            
            if fail_clicked:
                st.session_state['link_failed'] = not st.session_state['link_failed']
                st.rerun()
                
            if send_clicked:
                if source_node == dest_node:
                    st.warning("Source and destination cannot be the same!")
                else:
                    if st.session_state['link_failed']:
                        st.session_state['last_packet'] = {
                            'status': 'FAILED', 'reason': 'Destination unreachable due to simulated link failure.',
                            'source': source_node, 'dest': dest_node, 'proto': protocol
                        }
                    else:
                        try:
                            path = nx.shortest_path(G, source=source_node, target=dest_node)
                            hops = len(path) - 1
                            st.session_state['last_packet'] = {
                                'status': 'DELIVERED', 'path': path, 'hops': hops, 
                                'latency': f"{final_latency:.1f} ms", 'source': source_node, 'dest': dest_node, 'proto': protocol
                            }
                        except nx.NetworkXNoPath:
                            st.session_state['last_packet'] = {'status': 'FAILED', 'reason': 'No route available across network.'}
            
            if st.session_state['last_packet']:
                pkt = st.session_state['last_packet']
                if pkt['status'] == 'DELIVERED':
                    path_preview = " ── ".join(pkt['path'][:4]) + ("..." if len(pkt['path']) > 4 else "")
                    st.markdown(f"""
                    <div class='success-box'>
                    <b>PACKET INFORMATION</b><br>
                    <b>Source:</b> <span style="color:#34d399; font-weight:bold;">{pkt['source']}</span> &nbsp;&nbsp;|&nbsp;&nbsp; <b>Destination:</b> <span style="color:#34d399; font-weight:bold;">{pkt['dest']}</span><br>
                    <b>Protocol:</b> <span style="color:#34d399; font-weight:bold;">{pkt['proto']}</span> &nbsp;&nbsp;|&nbsp;&nbsp; <b>Distance:</b> <span style="color:#34d399; font-weight:bold;">{dist_str}</span><br>
                    <b>Latency:</b> <span style="color:#34d399; font-weight:bold;">{pkt['latency']}</span> &nbsp;&nbsp;|&nbsp;&nbsp; <b>Route:</b> {path_preview}<br>
                    <b>Status:</b> ✓ Delivered Successfully
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='error-box'>
                    <b>PACKET TRANSMISSION FAILED</b><br>
                    Network Status: {pkt['reason']}<br>
                    <i>(Tip: Click 'Simulate Link Failure' again to restore connection).</i>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Not enough client endpoints available.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_viz:
        st.subheader(f"🗺️ Live Topology Rendering: {topology} ({num_nodes} Nodes)")
        
        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        node_text = list(G.nodes()) if num_nodes <= 30 else [n if "PC-1" in n or "Gateway" in n else "" for n in G.nodes()]
        
        node_colors = []
        for node in G.nodes():
            if st.session_state['link_failed'] and node == "PC-1":
                node_colors.append('#fb7185')  # Bright red for failure
            elif "PC" in node:
                node_colors.append('#00ffff')  # High-visibility electric cyan
            else:
                node_colors.append('#c084fc')  # Vibrant neon purple for hubs/switches

        topo_fig = go.Figure()
        topo_fig.add_trace(go.Scatter(x=edge_x, y=edge_y, line=dict(width=2 if num_nodes > 30 else 3, color='#fb7185' if st.session_state['link_failed'] else '#38bdf8'), mode='lines'))
        topo_fig.add_trace(go.Scatter(x=node_x, y=node_y, mode='text+markers',
            marker=dict(size=14 if num_nodes > 30 else 24, color=node_colors, line=dict(width=2, color='#ffffff')),
            text=node_text, textposition="top center", textfont=dict(color="#f8fafc", size=12)))
        
        topo_fig.update_layout(
            showlegend=False, 
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            paper_bgcolor='#0b0f19', 
            plot_bgcolor='#111827', 
            height=480,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(topo_fig, use_container_width=True)

with tab2:
    st.subheader("📦 Layer 2 Frame Encapsulation & Medium Transmission Visuals")
    st.markdown(f"Active Medium: <span style='color:#38bdf8; font-weight:bold;'>{media}</span> | Span: <span style='color:#38bdf8; font-weight:bold;'>{dist_str}</span>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card">
        <h3>Ethernet II Frame Structure</h3>
        <ul>
            <li><b>Preamble & SFD (8 Bytes):</b> Synchronization.</li>
            <li><b>Destination MAC (6 Bytes):</b> Target physical address.</li>
            <li><b>Source MAC (6 Bytes):</b> Sender physical address.</li>
            <li><b>EtherType (2 Bytes):</b> Upper protocol indicator.</li>
            <li><b>Payload (46–1500 Bytes):</b> Encapsulated data packet.</li>
            <li><b>FCS / CRC (4 Bytes):</b> Frame Check Sequence for error detection.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
        <h3>Medium Characteristics</h3>
        <ul>
            <li><b>Bandwidth Cap:</b> <span style="color:#34d399; font-weight:bold;">{media_speed} Mbps</span></li>
            <li><b>Propagation Delay:</b> <span style="color:#38bdf8; font-weight:bold;">{propagation_latency_ms:.1f} ms</span></li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📊 Transmission Signal Waveform Visualization")
    x_vals = np.linspace(0, 50, 500)
    if "Copper" in media:
        y_vals = np.sin(x_vals) * np.exp(-0.02 * x_vals)
        wave_title = "Electrical Voltage Pulses (Square/Sine Wave with Attenuation)"
    elif "Fiber" in media:
        y_vals = np.sin(x_vals * 1.5)
        wave_title = "Optical Light Pulses (High Frequency / Low Attenuation)"
    elif "Satellite" in media:
        y_vals = np.sin(x_vals * 0.5) * (1 + 0.8 * np.sin(x_vals * 0.1))
        wave_title = "Satellite RF Link Waveform (High Delay / Atmospheric Scatter)"
    else:
        y_vals = np.sin(x_vals) * (1 + 0.5 * np.sin(x_vals * 0.3))
        wave_title = "RF Electromagnetic Wave (Subject to Noise)"

    wave_fig = go.Figure()
    wave_fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', line=dict(color='#00ffff', width=3)))
    wave_fig.update_layout(
        title=dict(text=wave_title, font=dict(color="#38bdf8")),
        xaxis_title="Distance along Transmission Line",
        yaxis_title="Signal Amplitude",
        paper_bgcolor='#0b0f19',
        plot_bgcolor='#111827',
        font=dict(color="#f8fafc"),
        height=300
    )
    st.plotly_chart(wave_fig, use_container_width=True)

with tab3:
    st.subheader("📚 OSI Model Stack & Topology Disadvantage Analysis")
    
    st.markdown(f"""
    <div class="osi-card"><b>Layer 7: Application Layer</b> | HTTP, HTTPS, DNS, FTP (Architecture: <b>{architecture}</b>)</div>
    <div class="osi-card"><b>Layer 6: Presentation Layer</b> | Data formatting, encryption, compression.</div>
    <div class="osi-card"><b>Layer 5: Session Layer</b> | Dialog control & session management.</div>
    <div class="osi-card"><b>Layer 4: Transport Layer</b> | TCP (Reliable) & UDP (Fast Stream)</div>
    <div class="osi-card"><b>Layer 3: Network Layer</b> | Routing across <b>{topology}</b> for <b>{num_nodes} nodes</b> via <b>{device}</b></div>
    <div class="osi-card"><b>Layer 2: Data Link Layer</b> | Ethernet MAC addressing, Framing, CRC/FCS</div>
    <div class="osi-card"><b>Layer 1: Physical Layer</b> | <b>{media}</b> spanning <b>{dist_str}</b></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="disadvantage-box">
    <h3>⚠️ Disadvantages of Other Network Topologies</h3>
    <p>Every topology has trade-offs depending on scalability, cost, and fault tolerance:</p>
    <ul>
        <li><b>Star Topology Disadvantages:</b>
            <ul>
                <li><b>Single Point of Failure:</b> If the central switch/hub fails, the entire network goes down.</li>
                <li><b>Cabling Cost:</b> Requires a dedicated cable run from every node back to the central hub/switch, increasing wiring expenses for large networks.</li>
            </ul>
        </li>
        <li><b>Mesh Topology Disadvantages:</b>
            <ul>
                <li><b>Extremely High Cost:</b> Requires a vast amount of cabling and multiple interface ports per device, making it very expensive to implement.</li>
                <li><b>Complex Installation:</b> Configuration, wiring management, and troubleshooting can become overwhelmingly complex as node count increases.</li>
            </ul>
        </li>
        <li><b>Ring Topology Disadvantages:</b>
            <ul>
                <li><b>Single Break Vulnerability:</b> In a simple ring, a single cable break disrupts data circulation across the entire loop.</li>
                <li><b>Latency Accumulation:</b> Data often must pass through intermediate nodes, which can increase overall transmission delay in large rings.</li>
            </ul>
        </li>
        <li><b>Bus Topology Disadvantages:</b>
            <ul>
                <li><b>Scalability Bottleneck:</b> Adding new nodes degrades performance severely and increases data collision risks.</li>
                <li><b>Difficult Fault Isolation:</b> A break anywhere along the main backbone cable disables the entire segment, and pinpointing the failure point is difficult.</li>
            </ul>
        </li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
