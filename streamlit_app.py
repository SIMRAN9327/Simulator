import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import random

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
        padding: 20px;
        border-radius: 8px;
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
        background-color: #064e3b;
        border-left: 4px solid #10b981;
        padding: 15px;
        border-radius: 6px;
        font-family: monospace;
        margin-top: 10px;
    }
    .error-box {
        background-color: #7f1d1d;
        border-left: 4px solid #f43f5e;
        padding: 15px;
        border-radius: 6px;
        font-family: monospace;
        margin-top: 10px;
    }
    .ai-badge {
        background-color: #1e1b4b;
        border: 1px solid #6366f1;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌐 CyberNet: AI-Powered Networking & Frame Simulator")
st.markdown("""
*An advanced simulation tool built for computer networking students. Enter your network constraints, let the AI recommend the ideal topology and media, and inspect live frame transmissions.*
""")

# --- SIDEBAR: PARAMETERS & AI RECOMMENDATIONS ---
st.sidebar.header("🎛️ Network Parameters")

# 1. User inputs for AI recommendations
num_nodes = st.sidebar.slider("Number of Nodes", min_value=3, max_value=12, value=5, help="Total client endpoints in the network.")
distance_m = st.sidebar.number_input("Maximum Distance Span (meters)", min_value=5, max_value=50000, value=75, help="Longest physical distance between nodes.")

# --- AI RECOMMENDATION LOGIC ---
if num_nodes <= 5:
    rec_topo = "Star"
    topo_reason = "Best for small node counts: centralized management and easy fault isolation."
elif num_nodes <= 8:
    rec_topo = "Ring"
    topo_reason = "Good balance for moderate node counts with deterministic token passing."
else:
    rec_topo = "Mesh"
    topo_reason = "High node count requires redundant paths for fault tolerance and high availability."

if distance_m <= 100:
    rec_media = "Copper (UTP Cat6)"
    media_reason = "Ideal for short distances (<100m), offering high gigabit speeds at low cost."
elif distance_m <= 500:
    rec_media = "Wireless / Wi-Fi"
    media_reason = "Provides flexible medium-range coverage without physical cable clutter."
else:
    rec_media = "Fiber Optic"
    media_reason = "Essential for long distances (>500m) due to immunity from electromagnetic interference and low attenuation."

st.sidebar.markdown(f"""
<div class="ai-badge">
<b>🤖 AI Advisor Recommendations:</b><br>
• Recommended Topology: <span style="color:#38bdf8; font-weight:bold;">{rec_topo}</span><br>
<small style="color:#94a3b8;">{topo_reason}</small><br><br>
• Recommended Media: <span style="color:#38bdf8; font-weight:bold;">{rec_media}</span><br>
<small style="color:#94a3b8;">{media_reason}</small>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

topology = st.sidebar.selectbox(
    "1. Select Network Topology",
    ["Star", "Mesh", "Ring", "Bus"],
    index=["Star", "Mesh", "Ring", "Bus"].index(rec_topo)
)

media = st.sidebar.selectbox(
    "2. Select Transmission Media (Layer 1)",
    ["Copper (UTP Cat6)", "Fiber Optic", "Wireless / Wi-Fi"],
    index=["Copper (UTP Cat6)", "Fiber Optic", "Wireless / Wi-Fi"].index(rec_media)
)

device = st.sidebar.selectbox(
    "3. Core Networking Device",
    ["Layer 2 Switch (Smart Forwarding)", "Layer 3 Router (Packet Routing)", "Traditional Hub (Dumb Broadcast)"]
)

architecture = st.sidebar.selectbox(
    "4. Network Architecture",
    ["Client-Server", "Peer-to-Peer (P2P)"]
)

# Reset state when topology changes
if 'prev_topo' not in st.session_state or st.session_state['prev_topo'] != topology:
    st.session_state['link_failed'] = False
    st.session_state['last_packet'] = None
    st.session_state['prev_topo'] = topology

if 'link_failed' not in st.session_state:
    st.session_state['link_failed'] = False
if 'last_packet' not in st.session_state:
    st.session_state['last_packet'] = None

# --- PERFORMANCE ENGINE ---
media_speed = {"Fiber Optic": 10000, "Copper (UTP Cat6)": 1000, "Wireless / Wi-Fi": 300}[media]
base_latency = {"Fiber Optic": 3, "Copper (UTP Cat6)": 10, "Wireless / Wi-Fi": 35}[media]

if "Hub" in device:
    base_latency *= 2.5
    collision_risk = "High (Collision Domain)"
elif "Switch" in device:
    collision_risk = "None (Separated Collision Domains)"
else:
    collision_risk = "None (Routed Subnets)"

topo_multiplier = {"Star": 1.0, "Mesh": 0.8, "Ring": 1.4, "Bus": 2.2}[topology]
final_latency = base_latency * topo_multiplier
final_throughput = media_speed / topo_multiplier

# --- BUILD DYNAMIC NETWORK GRAPH ---
G = nx.Graph()
node_names = [f"PC-{i+1}" for i in range(num_nodes)]

if topology == "Star":
    center = "Central Switch"
    G.add_node(center)
    for n in node_names:
        G.add_edge(center, n)
    pos = nx.spring_layout(G, seed=42)
    pos[center] = (0, 0)
elif topology == "Mesh":
    G.add_nodes_from(node_names)
    for i in range(len(node_names)):
        for j in range(i+1, len(node_names)):
            G.add_edge(node_names[i], node_names[j])
    pos = nx.spring_layout(G, seed=42)
elif topology == "Bus":
    bus_nodes = ["Term-1"] + node_names + ["Term-2"]
    for i in range(len(bus_nodes)-1):
        G.add_edge(bus_nodes[i], bus_nodes[i+1])
    pos = {n: (i * 1.2, 0) for i, n in enumerate(bus_nodes)}
else: # Ring
    G.add_nodes_from(node_names)
    for i in range(len(node_names)):
        G.add_edge(node_names[i], node_names[(i+1)%len(node_names)])
    pos = nx.circular_layout(node_names)

# --- TABS FOR PRESENTATION ---
tab1, tab2, tab3 = st.tabs(["🗺️ Visual Topology & Packet Simulator", "📦 Frame Transmission & Medium Visuals", "📚 OSI & TCP/IP Model Stack"])

with tab1:
    col_metrics, col_viz = st.columns([1, 1], gap="large")
    
    with col_metrics:
        st.subheader("📊 Performance Metrics")
        m1, m2, m3 = st.columns(3)
        m1.metric("Calculated Latency", f"{final_latency:.1f} ms")
        m2.metric("Effective Throughput", f"{final_throughput:.0f} Mbps")
        m3.metric("Collision Domain", collision_risk)
        
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
                                'latency': f"{final_latency:.0f} ms", 'source': source_node, 'dest': dest_node, 'proto': protocol
                            }
                        except nx.NetworkXNoPath:
                            st.session_state['last_packet'] = {'status': 'FAILED', 'reason': 'No route available.'}
            
            # Display Packet Result
            if st.session_state['last_packet']:
                pkt = st.session_state['last_packet']
                if pkt['status'] == 'DELIVERED':
                    path_str = " ── ".join([f"<span style='color:#38bdf8;'><b>{n}</b></span>" for n in pkt['path']])
                    st.markdown(f"""
                    <div class='success-box'>
                    <b>PACKET INFORMATION</b><br>
                    <b>Source:</b> {pkt['source']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Destination:</b> {pkt['dest']}<br>
                    <b>Protocol:</b> {pkt['proto']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Hops:</b> {pkt['hops']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Latency:</b> {pkt['latency']}<br>
                    <b>Route:</b> {path_str}<br>
                    <b>Status:</b> <span style="color:#34d399; font-weight:bold;">✓ Delivered Successfully</span>
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
        node_text = list(G.nodes())
        
        node_colors = []
        for node in G.nodes():
            if st.session_state['link_failed'] and node == "PC-1":
                node_colors.append('#f43f5e')
            elif "PC" in node:
                node_colors.append('#38bdf8')
            else:
                node_colors.append('#8b5cf6')

        topo_fig = go.Figure()
        topo_fig.add_trace(go.Scatter(x=edge_x, y=edge_y, line=dict(width=3, color='#f43f5e' if st.session_state['link_failed'] else '#38bdf8'), mode='lines'))
        topo_fig.add_trace(go.Scatter(x=node_x, y=node_y, mode='text+markers',
            marker=dict(size=22, color=node_colors, line=dict(width=2, color='#ffffff')),
            text=node_text, textposition="top center"))
        
        topo_fig.update_layout(showlegend=False, xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=480)
        st.plotly_chart(topo_fig, use_container_width=True)

with tab2:
    st.subheader("📦 Layer 2 Frame Encapsulation & Medium Transmission Visuals")
    st.markdown("Inspect how data is wrapped into frames at the Data Link layer and transmitted across your selected medium: <span style='color:#38bdf8; font-weight:bold;'>{media}</span>.", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card">
        <h3>Ethernet II Frame Structure</h3>
        <p>Before bits travel across the physical medium, they are packaged into frames:</p>
        <ul>
            <li><b>Preamble & SFD (8 Bytes):</b> Synchronization and clock recovery.</li>
            <li><b>Destination MAC (6 Bytes):</b> Physical address of the receiving node.</li>
            <li><b>Source MAC (6 Bytes):</b> Physical address of the sending node.</li>
            <li><b>EtherType (2 Bytes):</b> Identifies the upper-layer protocol (e.g., IPv4).</li>
            <li><b>Payload (46–1500 Bytes):</b> Encapsulated packet data.</li>
            <li><b>FCS / CRC (4 Bytes):</b> Frame Check Sequence for error detection.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
        <h3>Transmission Medium Characteristics</h3>
        <p>Active Medium: <span style="color:#38bdf8; font-weight:bold;">{media}</span></p>
        <ul>
            <li><b>Bandwidth Cap:</b> <span style="color:#34d399; font-weight:bold;">{media_speed} Mbps</span></li>
            <li><b>Signal Representation:</b> {"Electrical Voltage Pulses (Copper wire)" if "Copper" in media else "Light Pulses / Photons (Glass Core)" if "Fiber" in media else "Radio Frequency (RF) Electromagnetic Waves"}</li>
            <li><b>Attenuation Risk:</b> {"Moderate (Resistance loss over distance)" if "Copper" in media else "Very Low (Minimal signal loss)" if "Fiber" in media else "High (Path loss and interference)"}</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    # Transmission Medium Signal Graph Simulation
    st.markdown("### 📊 Transmission Medium Signal Waveform Visualization")
    
    # Generate sample waveform based on media type
    import numpy as np
    x_vals = np.linspace(0, 50, 500)
    if "Copper" in media:
        y_vals = np.sin(x_vals) * np.exp(-0.02 * x_vals) # Attenuating electrical wave
        wave_title = "Electrical Voltage Pulses (Square/Sine Wave with Attenuation)"
    elif "Fiber" in media:
        y_vals = np.sin(x_vals * 1.5) # Clean light pulses with high amplitude
        wave_title = "Optical Light Pulses (High Frequency / Low Attenuation)"
    else:
        y_vals = np.sin(x_vals) * (1 + 0.5 * np.sin(x_vals * 0.3)) # RF wave with noise fluctuation
        wave_title = "RF Electromagnetic Wave (Subject to Noise / Atmospheric Scatter)"

    wave_fig = go.Figure()
    wave_fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', line=dict(color='#38bdf8', width=3)))
    wave_fig.update_layout(
        title=wave_title,
        xaxis_title="Distance along Transmission Line",
        yaxis_title="Signal Amplitude",
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300
    )
    st.plotly_chart(wave_fig, use_container_width=True)

with tab3:
    st.subheader("📚 OSI Model & Protocol Stack Mapping")
    st.markdown("Dynamic layer breakdown based on your active network choices:")

    st.markdown(f"""
    <div class="osi-card"><b>Layer 7: Application Layer</b><br><span style="color:#94a3b8;">Protocols: HTTP, HTTPS, DNS, FTP | Architecture: <span style="color:#38bdf8; font-weight:bold;">{architecture}</span></span></div>
    <div class="osi-card"><b>Layer 6: Presentation Layer</b><br><span style="color:#94a3b8;">Data formatting, encryption, compression, and character set conversion.</span></div>
    <div class="osi-card"><b>Layer 5: Session Layer</b><br><span style="color:#94a3b8;">Manages dialog control, establishing, maintaining, and terminating sessions.</span></div>
    <div class="osi-card"><b>Layer 4: Transport Layer</b><br><span style="color:#94a3b8;">Protocols: TCP (Connection-oriented, reliable) & UDP (Connectionless, fast stream)</span></div>
    <div class="osi-card"><b>Layer 3: Network Layer</b><br><span style="color:#94a3b8;">Protocols: IPv4, IPv6, ICMP | Routing across <span style="color:#38bdf8; font-weight:bold;">{topology}</span> topology via <span style="color:#38bdf8; font-weight:bold;">{device}</span></span></div>
    <div class="osi-card"><b>Layer 2: Data Link Layer</b><br><span style="color:#94a3b8;">Protocols: Ethernet MAC addressing, Framing, Error detection (CRC/FCS)</span></div>
    <div class="osi-card"><b>Layer 1: Physical Layer</b><br><span style="color:#94a3b8;">Transmission Media: <span style="color:#38bdf8; font-weight:bold;">{media}</span> (Converts frames into physical signals over {distance_m}m span)</span></div>
    """, unsafe_allow_html=True)
