import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import random
import time
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CyberNet // Advanced Computer Network Simulator",
    page_icon="🌐",
    layout="wide"
)

# --- CLEAN & SPACIOUS NOC DARK THEME CSS ---
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
    .panel-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 24px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .success-box, .error-box {
        background-color: #1e293b;
        padding: 14px;
        border-radius: 6px;
        margin-bottom: 15px;
        font-family: monospace;
    }
    .success-box { border-left: 4px solid #10b981; }
    .error-box { border-left: 4px solid #f43f5e; }
    .terminal {
        background-color: #030712;
        border: 1px solid #1f2937;
        padding: 18px;
        border-radius: 8px;
        font-family: monospace;
        color: #34d399;
        height: 240px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True
    st.session_state['logs'] = []
    st.session_state['stats'] = {'sent': 0, 'delivered': 0, 'dropped': 0, 'latency_sum': 0}
    
    G = nx.Graph()
    nodes_data = {
        "PC-1": {"type": "PC", "ip": "192.168.1.10", "mac": "AA:BB:CC:00:00:01"},
        "PC-4": {"type": "PC", "ip": "192.168.1.40", "mac": "AA:BB:CC:00:00:04"},
        "R1": {"type": "Router", "ip": "192.168.1.1", "mac": "CC:DD:EE:00:01:01"},
        "R2": {"type": "Router", "ip": "192.168.2.1", "mac": "CC:DD:EE:00:02:01"},
        "R3": {"type": "Router", "ip": "192.168.3.1", "mac": "CC:DD:EE:00:03:01"},
        "R4": {"type": "Router", "ip": "192.168.4.1", "mac": "CC:DD:EE:00:04:01"},
        "Server-X": {"type": "Server", "ip": "10.0.0.100", "mac": "FF:EE:DD:00:00:FF"}
    }
    for node, attrs in nodes_data.items(): G.add_node(node, **attrs)
    
    edges_data = [
        ("PC-1", "R1", 1000, 2, 0.0, "Active", "Copper (UTP)"),
        ("R1", "R2", 100, 15, 1.0, "Active", "Fiber Optic"),
        ("R1", "R3", 100, 25, 2.0, "Active", "Wireless"),
        ("R2", "R4", 100, 20, 1.0, "Active", "Fiber Optic"),
        ("R3", "R4", 100, 18, 1.5, "Active", "Copper (UTP)"),
        ("R4", "PC-4", 1000, 2, 0.0, "Active", "Copper (UTP)"),
        ("R4", "Server-X", 1000, 5, 0.0, "Active", "Fiber Optic")
    ]
    for u, v, bw, lat, loss, status, media in edges_data:
        G.add_edge(u, v, bandwidth=bw, latency=lat, loss=loss, status=status, media=media, congested=False)
    st.session_state['G'] = G

def log_event(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state['logs'].insert(0, f"[{timestamp}] {message}")

def get_link_cost(u, v, data):
    if data.get('status') == 'Failed':
        return float('inf')
    bw_factor = 1000.0 / max(data.get('bandwidth', 100), 1)
    util_penalty = 2.5 if data.get('congested', False) else 1.0
    cost = (data.get('latency', 10) * bw_factor * util_penalty) + (data.get('loss', 0) * 15)
    return max(1, int(cost))

# --- HEADER & METRICS ---
st.title("🌐 CyberNet: Advanced Computer Network Simulator")
st.markdown("*B.Tech Computer Networking Laboratory // Clean & Structured Control Center*")

G = st.session_state['G']
total_nodes = G.number_of_nodes()
total_links = G.number_of_edges()
failed_links = sum(1 for u, v, d in G.edges(data=True) if d.get('status') == 'Failed')
sent = st.session_state['stats']['sent']
delivered = st.session_state['stats']['delivered']
dropped = st.session_state['stats']['dropped']
avg_lat = int(st.session_state['stats']['latency_sum'] / delivered) if delivered > 0 else 0
loss_rate = f"{(dropped / sent * 100):.1f}%" if sent > 0 else "0.0%"

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Nodes", total_nodes)
m2.metric("Active Links", f"{total_links - failed_links}/{total_links}")
m3.metric("Sent", sent)
m4.metric("Delivered", delivered)
m5.metric("Avg Latency", f"{avg_lat} ms")
m6.metric("Loss Rate", loss_rate)

st.markdown("<br>", unsafe_allow_html=True)

# --- CLEAN TABS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🗺️ Topology & Media",
    "📦 Packet Simulation",
    "💥 Failure & Congestion",
    "🚦 TCP, UDP & ARP",
    "📚 OSI & TCP/IP",
    "📋 Event Logs"
])

# ==========================================
# TAB 1: TOPOLOGY & MEDIA BUILDER
# ==========================================
with tab1:
    col_builder, col_preview = st.columns([1, 1], gap="large")
    
    with col_builder:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("🛠️ Network Layout Controls")
        
        topo_template = st.selectbox("Select Topology Template", [
            "Dual-Path Enterprise (Default)", 
            "Star Topology (Hub & Spoke)", 
            "Ring Topology", 
            "Fully Connected Mesh"
        ])
        
        default_media = st.selectbox("Default Transmission Media", ["Copper (UTP Cat6 - 1Gbps)", "Fiber Optic (10Gbps)", "Wireless Wi-Fi 6 (300Mbps)"])
        
        if st.button("🏗️ Build Topology", type="primary"):
            G_new = nx.Graph()
            if "Dual-Path" in topo_template:
                nodes = {"PC-1": ("PC", "192.168.1.10"), "PC-4": ("PC", "192.168.1.40"), "R1": ("Router", "192.168.1.1"), 
                         "R2": ("Router", "192.168.2.1"), "R3": ("Router", "192.168.3.1"), "R4": ("Router", "192.168.4.1")}
                for n, (t, ip) in nodes.items(): G_new.add_node(n, type=t, ip=ip, mac="AA:BB:CC:00:00:01")
                edges = [("PC-1", "R1", 1000, 2), ("R1", "R2", 100, 15), ("R1", "R3", 100, 25), 
                         ("R2", "R4", 100, 20), ("R3", "R4", 100, 18), ("R4", "PC-4", 1000, 2)]
                for u, v, bw, lat in edges: G_new.add_edge(u, v, bandwidth=bw, latency=lat, loss=0.5, status="Active", media=default_media, congested=False)
            elif "Star" in topo_template:
                center = "Core-Switch"
                G_new.add_node(center, type="Switch", ip="10.0.0.1", mac="AA:00:00:00:00:01")
                for i in range(1, 6):
                    pc = f"PC-{i}"
                    G_new.add_node(pc, type="PC", ip=f"192.168.1.{i}", mac=f"AA:BB:CC:00:00:0{i}")
                    G_new.add_edge(center, pc, bandwidth=1000, latency=4, loss=0.0, status="Active", media=default_media, congested=False)
            elif "Ring" in topo_template:
                pcs = ["PC-1", "PC-2", "PC-3", "PC-4", "PC-5"]
                for p in pcs: G_new.add_node(p, type="PC", ip="192.168.1.X", mac="AA:BB:CC:00:00:0X")
                for i in range(len(pcs)): G_new.add_edge(pcs[i], pcs[(i+1)%len(pcs)], bandwidth=100, latency=12, loss=1.0, status="Active", media=default_media, congested=False)
            else:
                pcs = ["PC-1", "PC-2", "PC-3", "PC-4"]
                for p in pcs: G_new.add_node(p, type="PC", ip="192.168.1.X", mac="AA:BB:CC:00:00:0X")
                for i in range(len(pcs)):
                    for j in range(i+1, len(pcs)):
                        G_new.add_edge(pcs[i], pcs[j], bandwidth=1000, latency=7, loss=0.2, status="Active", media=default_media, congested=False)
            st.session_state['G'] = G_new
            log_event(f"Built network: {topo_template}")
            st.rerun()

        st.markdown("<hr style='border-color: #1f2937;'>", unsafe_allow_html=True)
        st.subheader("⚙️ Fine-Tune Link Properties")
        edges_list = [f"{u} ↔ {v}" for u, v, d in st.session_state['G'].edges(data=True)]
        if edges_list:
            selected_edge = st.selectbox("Select Physical Link", edges_list)
            u, v = selected_edge.split(" ↔ ")
            edata = st.session_state['G'][u][v]
            
            link_media = st.selectbox("Media Type", ["Copper (UTP Cat6 - 1Gbps)", "Fiber Optic (10Gbps)", "Wireless Wi-Fi 6 (300Mbps)"])
            custom_bw = st.slider("Bandwidth (Mbps)", 10, 10000, int(edata.get('bandwidth', 100)))
            custom_lat = st.slider("Latency (ms)", 1, 100, int(edata.get('latency', 10)))
            custom_loss = st.slider("Packet Loss (%)", 0.0, 25.0, float(edata.get('loss', 0.0)))
            
            if st.button("💾 Apply Link Update"):
                st.session_state['G'][u][v]['media'] = link_media
                st.session_state['G'][u][v]['bandwidth'] = custom_bw
                st.session_state['G'][u][v]['latency'] = custom_lat
                st.session_state['G'][u][v]['loss'] = custom_loss
                log_event(f"Updated link {u}-{v}")
                st.success("Updated successfully!")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_preview:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("🗺️ Live Topology Visualizer")
        G = st.session_state['G']
        pos = nx.spring_layout(G, seed=42)
        
        edge_x, edge_y, edge_colors = [], [], []
        for u, v, d in G.edges(data=True):
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            if d.get('status') == 'Failed': edge_colors.append('#f43f5e')
            elif d.get('congested', False): edge_colors.append('#f59e0b')
            else: edge_colors.append('#38bdf8')

        node_x, node_y, node_colors, node_text, node_hover = [], [], [], [], []
        for node, attrs in G.nodes(data=True):
            node_x.append(pos[node][0])
            node_y.append(pos[node][1])
            node_text.append(node)
            ntype = attrs.get('type', 'PC')
            if ntype == 'PC': node_colors.append('#38bdf8')
            elif ntype == 'Router': node_colors.append('#8b5cf6')
            elif ntype == 'Switch': node_colors.append('#10b981')
            else: node_colors.append('#f59e0b')
            node_hover.append(f"Node: {node}<br>IP: {attrs.get('ip', 'N/A')}")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=edge_x, y=edge_y, line=dict(width=3, color='#38bdf8'), mode='lines', hoverinfo='none'))
        fig.add_trace(go.Scatter(x=node_x, y=node_y, mode='text+markers',
            marker=dict(size=24, color=node_colors, line=dict(width=2, color='#ffffff')),
            text=node_text, textposition="top center", hoverinfo='text', hovertext=node_hover))
        
        fig.update_layout(showlegend=False, xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                          yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                          template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=450)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 2: PACKET SIMULATION & ROUTING
# ==========================================
with tab2:
    col_sim_ctrl, col_sim_res = st.columns([1, 1], gap="large")
    
    with col_sim_ctrl:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("📦 Packet Transmission Generator")
        nodes_list = list(st.session_state['G'].nodes())
        source_node = st.selectbox("Source Device", nodes_list, index=0)
        dest_node = st.selectbox("Destination Device", nodes_list, index=min(1, len(nodes_list)-1))
        protocol = st.selectbox("Protocol", ["TCP", "UDP"])
        packet_size = st.slider("Packet Size (Bytes)", 64, 1500, 512)
        
        if st.button("▶ SEND PACKET NOW", type="primary"):
            if source_node == dest_node:
                st.warning("Source and destination cannot be identical!")
            else:
                G = st.session_state['G']
                try:
                    path = nx.shortest_path(G, source=source_node, target=dest_node, weight=lambda u, v, d: get_link_cost(u, v, d))
                    total_lat = sum(G[path[i]][path[i+1]].get('latency', 10) for i in range(len(path)-1))
                    total_loss = max(G[path[i]][path[i+1]].get('loss', 0) for i in range(len(path)-1))
                    hops = len(path) - 1
                    dropped = random.uniform(0, 100) < total_loss
                    
                    st.session_state['stats']['sent'] += 1
                    if dropped:
                        st.session_state['stats']['dropped'] += 1
                        status = "DROPPED (Link Error)"
                        log_event(f"Packet {source_node} → {dest_node} dropped.")
                    else:
                        st.session_state['stats']['delivered'] += 1
                        st.session_state['stats']['latency_sum'] += total_lat
                        status = "DELIVERED"
                        log_event(f"Packet delivered via {' → '.join(path)}")
                        
                    st.session_state['last_sim'] = {
                        'path': path, 'latency': total_lat, 'hops': hops, 'status': status,
                        'protocol': protocol, 'size': packet_size, 'dropped': dropped
                    }
                except nx.NetworkXNoPath:
                    st.error("Route Unavailable!")
                    log_event(f"No route between {source_node} and {dest_node}.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_sim_res:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("📊 Inspection & Results")
        if 'last_sim' in st.session_state:
            sim = st.session_state['last_sim']
            if sim['dropped']:
                st.markdown(f"<div class='error-box'>Status: ✗ {sim['status']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='success-box'>Status: ✓ {sim['status']}</div>", unsafe_allow_html=True)
            st.markdown(f"**Route:** `{' → '.join(sim['path'])}`")
            c1, c2, c3 = st.columns(3)
            c1.metric("Latency", f"{sim['latency']} ms")
            c2.metric("Hops", sim['hops'])
            c3.metric("Proto", sim['protocol'])
            st.markdown("---")
            st.code(f"""
[Ethernet] Src MAC: AA:BB:CC:00:00:01 | Dst MAC: CC:DD:EE:00:01:01
  └── [IP] Src IP: 192.168.1.10 | Dst IP: 192.168.1.40 | Proto: {sim['protocol']}
        └── [Segment] Port: 54321 → 80 | Size: {sim['size']}B
            """, language="text")
        else:
            st.info("Click '▶ SEND PACKET NOW' to view simulation packet flow.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 3: FAILURE & CONGESTION LAB
# ==========================================
with tab3:
    col_lab_ctrl, col_lab_demo = st.columns([1, 1], gap="large")
    
    with col_lab_ctrl:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("⚡ Fault Injection Controls")
        
        edges_list = [f"{u} ↔ {v}" for u, v, d in st.session_state['G'].edges(data=True)]
        target_edge = st.selectbox("Select Target Link", edges_list)
        
        col_b1, col_b2, col_b3 = st.columns(3)
        if col_b1.button("💥 Fail Link"):
            u, v = target_edge.split(" ↔ ")
            st.session_state['G'][u][v]['status'] = 'Failed'
            log_event(f"Link {u} ↔ {v} failed.")
            st.rerun()
            
        if col_b2.button("🚦 Congest Link"):
            u, v = target_edge.split(" ↔ ")
            st.session_state['G'][u][v]['congested'] = True
            st.session_state['G'][u][v]['latency'] *= 4
            log_event(f"Congestion added to {u} ↔ {v}.")
            st.rerun()
            
        if col_b3.button("🔄 Reset All"):
            for u, v, d in st.session_state['G'].edges(data=True):
                d['status'] = 'Active'
                d['congested'] = False
                lat = d.get('latency', 10)
                d['latency'] = max(2, lat // 4 if lat > 40 else lat)
            log_event("All faults cleared.")
            st.success("Network reset!")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_lab_demo:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("📊 Dijkstra Re-Routing State")
        G = st.session_state['G']
        try:
            path_test = nx.shortest_path(G, source="PC-1", target="PC-4", weight=lambda u, v, d: get_link_cost(u, v, d))
            lat_test = sum(G[path_test[i]][path_test[i+1]].get('latency', 10) for i in range(len(path_test)-1))
            st.markdown(f"""
            <div class='success-box'>
            <b>Active Path:</b> `{' → '.join(path_test)}`<br>
            * <b>Hops:</b> {len(path_test)-1}<br>
            * <b>Latency:</b> {lat_test} ms<br>
            * <b>Status:</b> Resilient Path Active ✓
            </div>
            """, unsafe_allow_html=True)
        except nx.NetworkXNoPath:
            st.markdown("""
            <div class='error-box'>
            <b>Network Status:</b><br>
            * Partition / No Route Available ✗<br>
            * Action: Click 'Reset All' to restore links.
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 4: TCP HANDSHAKE, UDP & ARP
# ==========================================
with tab4:
    col_t1, col_t2 = st.columns([1, 1], gap="large")
    
    with col_t1:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("🤝 TCP 3-Way Handshake")
        if st.button("🚀 Run Handshake"):
            st.markdown("""
            <div class='terminal'>
            [Client] -- (1) SYN [Seq=1000] --> [Server]<br>
            [Server] -- (2) SYN-ACK [Seq=5000, Ack=1001] --> [Client]<br>
            [Client] -- (3) ACK [Ack=5001] --> [Server]<br>
            [Status] Connection Established!
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='terminal'>
            Click 'Run Handshake' to simulate TCP connection setup.
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_t2:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("🧩 ARP Resolution")
        arp_ip = st.text_input("Target IP", "192.168.1.40")
        if st.button("🔍 Resolve ARP"):
            st.markdown(f"""
            <div class='terminal'>
            [PC-1] Broadcast: "Who has {arp_ip}?"<br>
            [{arp_ip}] Unicast Reply: "I am at AA:BB:CC:00:00:04"<br>
            [Cache] Updated successfully.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='terminal'>
            ARP Cache Table:<br>
            ----------------------------------------<br>
            IP: 192.168.1.1   | MAC: CC:DD:EE:00:01:01<br>
            IP: 192.168.1.40  | MAC: AA:BB:CC:00:00:04
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 5: OSI & TCP/IP MODELS
# ==========================================
with tab5:
    st.subheader("📚 OSI Reference & TCP/IP Stack")
    osi_layers = [
        ("Layer 7 — Application Layer", "HTTP, HTTPS, DNS, FTP, SMTP", "Provides network services directly to user applications."),
        ("Layer 6 — Presentation Layer", "SSL/TLS, JPEG, ASCII", "Data translation, encryption, compression, and formatting."),
        ("Layer 5 — Session Layer", "NetBIOS, RPC, TLS Sessions", "Establishes, maintains, and terminates dialogs between systems."),
        ("Layer 4 — Transport Layer", "TCP, UDP, SCTP", "End-to-end communication, reliability, segmentation, and flow control."),
        ("Layer 3 — Network Layer", "IPv4, IPv6, ICMP, Routing", "Logical addressing and packet routing across multiple networks."),
        ("Layer 2 — Data Link Layer", "Ethernet, MAC, Switches, CRC", "Node-to-node physical framing and error detection."),
        ("Layer 1 — Physical Layer", "Copper UTP, Fiber Optic, Wi-Fi", "Transmission of raw bit streams over physical transmission media.")
    ]
    for layer, protos, desc in osi_layers:
        with st.expander(layer):
            st.markdown(f"**Protocols:** `{protos}`")
            st.markdown(f"**Function:** {desc}")

# ==========================================
# TAB 6: EVENT LOG TERMINAL
# ==========================================
with tab6:
    st.subheader("📋 Event Log Terminal")
    log_text = "\n".join(st.session_state['logs']) if st.session_state['logs'] else "[00:00:00] CyberNet initialized."
    st.markdown(f"""
    <div class='terminal' style='height: 380px;'>
    {log_text}
    </div>
    """, unsafe_allow_html=True)
    if st.button("🗑️ Clear Terminal"):
        st.session_state['logs'] = []
        st.rerun()
