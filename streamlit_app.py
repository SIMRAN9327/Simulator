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
</style>
""", unsafe_allow_html=True)

st.title("🌐 CyberNet: Core Networking Fundamentals & Simulation Visualizer")
st.markdown("""
*An interactive simulation tool built for computer networking students. Change transmission media, topologies, 
and networking devices to see how physical and logical layers impact performance and packet delivery.*
""")

# --- SESSION STATE INITIALIZATION ---
if 'link_failed' not in st.session_state:
    st.session_state['link_failed'] = False
if 'last_packet' not in st.session_state:
    st.session_state['last_packet'] = None

# --- SIDEBAR: CORE NETWORKING OPTIONS ---
st.sidebar.header("🎛️ Network Parameters")

topology = st.sidebar.selectbox(
    "1. Network Topology",
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

# Reset failure state when topology changes
if 'prev_topo' not in st.session_state or st.session_state['prev_topo'] != topology:
    st.session_state['link_failed'] = False
    st.session_state['last_packet'] = None
    st.session_state['prev_topo'] = topology

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

# --- BUILD NETWORK GRAPH ---
G = nx.Graph()
if topology == "Star":
    center = "Central Switch"
    G.add_node(center)
    for i in range(1, 5): 
        G.add_edge(center, f"PC-{i}")
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
        for j in range(i+1, len(nodes)): 
            G.add_edge(nodes[i], nodes[j])
    pos = nx.spring_layout(G, seed=42)
elif topology == "Bus":
    nodes = ["Term-1", "PC-1", "PC-2", "PC-3", "PC-4", "Term-2"]
    for i in range(len(nodes)-1): 
        G.add_edge(nodes[i], nodes[i+1])
    pos = {n: (i * 1.5, 0) for i, n in enumerate(nodes)}
else: # Ring
    nodes = ["PC-1", "PC-2", "PC-3", "PC-4"]
    for i in range(len(nodes)): 
        G.add_edge(nodes[i], nodes[(i+1)%len(nodes)])
    pos = nx.circular_layout(nodes)

# --- TABS FOR PRESENTATION ---
tab1, tab2 = st.tabs(["🗺️ Visual Topology & Packet Simulator", "📚 OSI & TCP/IP Model Stack"])

with tab1:
    col_metrics, col_viz = st.columns([1, 1], gap="large")
    
    with col_metrics:
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
        * <b>Device ({device}):</b> Dictates whether traffic is intelligently switched or broadcasted.
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
                            'status': 'FAILED', 'reason': 'Destination currently unreachable because the selected path has failed.',
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
            
            # Display Packet Info Result
            if st.session_state['last_packet']:
                pkt = st.session_state['last_packet']
                if pkt['status'] == 'DELIVERED':
                    path_str = " ── ".join([f"🔵 {n}" if n not in [pkt['source'], pkt['dest']] else f"<b>{n}</b>" for n in pkt['path']])
                    st.markdown(f"""
                    <div class='success-box'>
                    <b>PACKET INFORMATION</b><br>
                    <b>Source:</b> {pkt['source']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Destination:</b> {pkt['dest']}<br>
                    <b>Protocol:</b> {pkt['proto']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Hops:</b> {pkt['hops']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Latency:</b> {pkt['latency']}<br>
                    <b>Route:</b> {path_str}<br>
                    <b>Status:</b> ✓ Delivered Successfully
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='error-box'>
                    <b>PACKET TRANSMISSION FAILED</b><br>
                    Network Status: {pkt['reason']}<br>
                    <i>(Tip: Click 'Simulate Link Failure' again to restore the link and retry).</i>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Not enough client endpoints available in this topology.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_viz:
        st.subheader(f"🗺️ Live Topology Rendering: {topology}")
        
        edge_x, edge_y, edge_colors = [], [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            # Check if link failure is active on a primary edge
            if st.session_state['link_failed'] and (edge[0] == "PC-1" or edge[1] == "PC-1"):
                edge_colors.extend(['#f43f5e', '#f43f5e', '#f43f5e']) # Red for failed link
            else:
                edge_colors.extend(['#38bdf8', '#38bdf8', '#38bdf8'])

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
            marker=dict(size=24, color=node_colors, line=dict(width=2, color='#ffffff')),
            text=node_text, textposition="top center"))
        
        topo_fig.update_layout(showlegend=False, xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=480)
        st.plotly_chart(topo_fig, use_container_width=True)

with tab2:
    st.subheader("📚 OSI Model & Protocol Stack Mapping")
    st.markdown("Dynamic layer breakdown based on your active network choices:")

    st.markdown(f"""
    <div class="osi-card"><b>Layer 7: Application Layer</b><br><span style="color:#94a3b8;">Protocols: HTTP, HTTPS, DNS, FTP | Architecture: <b>{architecture}</b></span></div>
    <div class="osi-card"><b>Layer 6: Presentation Layer</b><br><span style="color:#94a3b8;">Data formatting, encryption, compression, and character set conversion.</span></div>
    <div class="osi-card"><b>Layer 5: Session Layer</b><br><span style="color:#94a3b8;">Manages dialog control, establishing, maintaining, and terminating sessions between applications.</span></div>
    <div class="osi-card"><b>Layer 4: Transport Layer</b><br><span style="color:#94a3b8;">Protocols: TCP (Connection-oriented, reliable) & UDP (Connectionless, fast stream)</span></div>
    <div class="osi-card"><b>Layer 3: Network Layer</b><br><span style="color:#94a3b8;">Protocols: IPv4, IPv6, ICMP | Routing across <b>{topology}</b> topology via <b>{device}</b></span></div>
    <div class="osi-card"><b>Layer 2: Data Link Layer</b><br><span style="color:#94a3b8;">Protocols: Ethernet MAC addressing, Framing, Error detection (CRC)</span></div>
    <div class="osi-card"><b>Layer 1: Physical Layer</b><br><span style="color:#94a3b8;">Transmission Media: <b>{media}</b> (Converts data bits into electrical signals, light pulses, or RF waves)</span></div>
    """, unsafe_allow_html=True)
