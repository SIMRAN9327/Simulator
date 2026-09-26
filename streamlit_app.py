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

# --- FUTURISTIC NOC DARK THEME CSS ---
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
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .alert-box {
        background-color: #1e293b;
        border-left: 4px solid #f59e0b;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 10px;
        font-family: monospace;
    }
    .success-box {
        background-color: #1e293b;
        border-left: 4px solid #10b981;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 10px;
        font-family: monospace;
    }
    .error-box {
        background-color: #1e293b;
        border-left: 4px solid #f43f5e;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 10px;
        font-family: monospace;
    }
    .terminal {
        background-color: #030712;
        border: 1px solid #1f2937;
        padding: 15px;
        border-radius: 6px;
        font-family: monospace;
        color: #34d399;
        height: 220px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True
    st.session_state['logs'] = []
    st.session_state['stats'] = {'sent': 0, 'delivered': 0, 'dropped': 0, 'latency_sum': 0}
    
    # Default Dual-Path Network
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
st.markdown("*B.Tech Computer Networking Laboratory // Interactive Topology, Routing, Failure Resilience & Protocol Stack*")

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
m3.metric("Packets Sent", sent)
m4.metric("Delivered", delivered)
m5.metric("Avg Latency", f"{avg_lat} ms")
m6.metric("Packet Loss", loss_rate)

st.markdown("---")

# --- TABS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🗺️ Topology & Media Builder",
    "📦 Packet Simulation & Routing",
    "💥 Failure & Congestion Lab",
    "🚦 TCP Handshake, UDP & ARP",
    "📚 OSI & TCP/IP Models",
    "📋 Event Log Terminal"
])

# ==========================================
# TAB 1: TOPOLOGY & MEDIA BUILDER
# ==========================================
with tab1:
    col_builder, col_preview = st.columns([1, 1])
    
    with col_builder:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("🛠️ Custom Network Layout Builder")
        
        topo_template = st.selectbox("Select Core Topology Template", [
            "Dual-Path Enterprise (Default)", 
            "Star Topology (Hub & Spoke)", 
            "Ring Topology (Token Ring style)", 
            "Fully Connected Mesh"
        ])
        
        default_media = st.selectbox("Default Transmission Media", ["Copper (UTP Cat6 - 1Gbps)", "Fiber Optic (10Gbps)", "Wireless Wi-Fi 6 (300Mbps)"])
        
        if st.button("🏗️ Build & Apply Topology Template", type="primary"):
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
            else: # Mesh
                pcs = ["PC-1", "PC-2", "PC-3", "PC-4"]
                for p in pcs: G_new.add_node(p, type="PC", ip="192.168.1.X", mac="AA:BB:CC:00:00:0X")
                for i in range(len(pcs)):
                    for j in range(i+1, len(pcs)):
                        G_new.add_edge(pcs[i], pcs[j], bandwidth=1000, latency=7, loss=0.2, status="Active", media=default_media, congested=False)
            st.session_state['G'] = G_new
            log_event(f"Built new network using template: {topo_template}")
            st.rerun()

        st.markdown("---")
        st.subheader("⚙️ Fine-Tune Link Characteristics")
        edges_list = [f"{u} ↔ {v}" for u, v, d in st.session_state['G'].edges(data=True)]
        if edges_list:
            selected_edge = st.selectbox("Select Physical Link", edges_list)
            u, v = selected_edge.split(" ↔ ")
            edata = st.session_state['G'][u][v]
            
            current_media = edata.get('media', 'Copper (UTP Cat6 - 1Gbps)')
            media_options = ["Copper (UTP Cat6 - 1Gbps)", "Fiber Optic (10Gbps)", "Wireless Wi-Fi 6 (300Mbps)"]
            default_media_idx = media_options.index(current_media) if current_media in media_options else 0
            
            link_media = st.selectbox("Transmission Media Type", media_options, index=default_media_idx)
            custom_bw = st.slider("Bandwidth Capacity (Mbps)", 10, 10000, int(edata.get('bandwidth', 100)))
            custom_lat = st.slider("Propagation Delay / Latency (ms)", 1, 100, int(edata.get('latency', 10)))
            custom_loss = st.slider("Bit Error / Packet Loss Rate (%)", 0.0, 25.0, float(edata.get('loss', 0.0)))
            
            if st.button("💾 Apply Link Properties"):
                st.session_state['G'][u][v]['media'] = link_media
                st.session_state['G'][u][v]['bandwidth'] = custom_bw
                st.session_state['G'][u][v]['latency'] = custom_lat
                st.session_state['G'][u][v]['loss'] = custom_loss
                log_event(f"Configured link {u}-{v}: Media={link_media}, BW={custom_bw}Mbps, Lat={custom_lat}ms")
                st.success("Link characteristics updated successfully!")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_preview:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("🗺️ Interactive Topology Visualization")
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
            node_hover.append(f"Node: {node}<br>Type: {ntype}<br>IP: {attrs.get('ip', 'N/A')}")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=edge_x, y=edge_y, line=dict(width=3, color='#38bdf8'), mode='lines', hoverinfo='none'))
        fig.add_trace(go.Scatter(x=node_x, y=node_y, mode='text+markers',
            marker=dict(size=26, color=node_colors, line=dict(width=2, color='#ffffff')),
            text=node_text, textposition="top center", hoverinfo='text', hovertext=node_hover))
        
        fig.update_layout(showlegend=False, xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                          yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                          template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=420)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 2: PACKET SIMULATION & ROUTING
# ==========================================
with tab2:
    st.subheader("📦 Packet Simulation & Dijkstra Routing Engine")
    col_sim_ctrl, col_sim_res = st.columns([1, 1])
    
    with col_sim_ctrl:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        nodes_list = list(st.session_state['G'].nodes())
        source_node = st.selectbox("Source Device", nodes_list, index=0)
        dest_node = st.selectbox("Destination Device", nodes_list, index=min(1, len(nodes_list)-1))
        protocol = st.selectbox("Transport Protocol", ["TCP", "UDP"])
        packet_size = st.slider("Packet Size (Bytes)", 64, 1500, 512)
        
        if st.button("▶ SEND PACKET", type="primary"):
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
                        status = "DROPPED (Link Error/Loss)"
                        log_event(f"Packet from {source_node} → {dest_node} DROPPED on path.")
                    else:
                        st.session_state['stats']['delivered'] += 1
                        st.session_state['stats']['latency_sum'] += total_lat
                        status = "DELIVERED"
                        log_event(f"Packet delivered: {source_node} → {' → '.join(path)} | Latency: {total_lat}ms")
                        
                    st.session_state['last_sim'] = {
                        'path': path, 'latency': total_lat, 'hops': hops, 'status': status,
                        'protocol': protocol, 'size': packet_size, 'dropped': dropped
                    }
                except nx.NetworkXNoPath:
                    st.error("Route Unavailable! Network partition or failed links blocking path.")
                    log_event(f"Route unavailable between {source_node} and {dest_node}.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_sim_res:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("📊 Transmission Results & Packet Inspection")
        if 'last_sim' in st.session_state:
            sim = st.session_state['last_sim']
            if sim['dropped']:
                st.markdown(f"<div class='error-box'>Status: ✗ {sim['status']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='success-box'>Status: ✓ {sim['status']}</div>", unsafe_allow_html=True)
            st.markdown(f"**Selected Route:** `{' → '.join(sim['path'])}`")
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Latency", f"{sim['latency']} ms")
            c2.metric("Hop Count", sim['hops'])
            c3.metric("Protocol", sim['protocol'])
            st.markdown("---")
            st.code(f"""
[Ethernet Frame] Src MAC: AA:BB:CC:00:00:01 | Dst MAC: CC:DD:EE:00:01:01
  └── [IP Packet]    Src IP: 192.168.1.10 | Dst IP: 192.168.1.40 | Protocol: {sim['protocol']}
        └── [Segment]  Source Port: 54321 | Dest Port: 80 | Size: {sim['size']} Bytes
              └── [Payload] Application Data Stream
            """, language="text")
        else:
            st.info("Configure parameters and click **'▶ SEND PACKET'** to observe routing.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("🧭 Computed Routing Tables")
    G = st.session_state['G']
    routers = [n for n, d in G.nodes(data=True) if d.get('type') == 'Router']
    if routers:
        selected_router = st.selectbox("Select Router to Inspect Routing Table", routers)
        rt_data = []
        for target in G.nodes():
            if target != selected_router:
                try:
                    path = nx.shortest_path(G, source=selected_router, target=target, weight=lambda u, v, d: get_link_cost(u, v, d))
                    next_hop = path[1]
                    cost = sum(get_link_cost(path[i], path[i+1], G[path[i]][path[i+1]]) for i in range(len(path)-1))
                    rt_data.append({"Destination": target, "Next Hop": next_hop, "Cost": cost, "Path": " → ".join(path)})
                except:
                    pass
        st.table(rt_data)

# ==========================================
# TAB 3: FAILURE & CONGESTION LAB
# ==========================================
with tab3:
    st.subheader("💥 Advanced Network Failure & Congestion Laboratory")
    st.markdown("Simulate link outages, congestion, and packet drops. Watch Dijkstra's algorithm instantly compute resilient alternative paths.")
    
    col_lab_ctrl, col_lab_demo = st.columns(2)
    
    with col_lab_ctrl:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("⚡ Chaos & Fault Injection Controls")
        
        edges_list = [f"{u} ↔ {v}" for u, v, d in st.session_state['G'].edges(data=True)]
        target_edge = st.selectbox("Choose Link for Chaos Test", edges_list)
        
        col_b1, col_b2, col_b3 = st.columns(3)
        if col_b1.button("💥 Fail Link"):
            u, v = target_edge.split(" ↔ ")
            st.session_state['G'][u][v]['status'] = 'Failed'
            log_event(f"CRITICAL: Link {u} ↔ {v} disconnected / failed!")
            st.rerun()
            
        if col_b2.button("🚦 Induce Heavy Congestion"):
            u, v = target_edge.split(" ↔ ")
            st.session_state['G'][u][v]['congested'] = True
            st.session_state['G'][u][v]['latency'] = st.session_state['G'][u][v].get('latency', 10) * 4
            log_event(f"WARNING: Severe traffic congestion injected on link {u} ↔ {v}.")
            st.rerun()
            
        if col_b3.button("🔄 Reset All Faults"):
            for u, v, d in st.session_state['G'].edges(data=True):
                d['status'] = 'Active'
                d['congested'] = False
                lat = d.get('latency', 10)
                d['latency'] = max(2, lat // 4 if lat > 40 else lat)
            log_event("SUCCESS: All network links restored to normal operational state.")
            st.success("Network fully recovered!")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_lab_demo:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("📊 Dynamic Resilience Analysis")
        
        G = st.session_state['G']
        try:
            path_test = nx.shortest_path(G, source="PC-1", target="PC-4", weight=lambda u, v, d: get_link_cost(u, v, d))
            lat_test = sum(G[path_test[i]][path_test[i+1]].get('latency', 10) for i in range(len(path_test)-1))
            hops_test = len(path_test) - 1
            st.markdown(f"""
            <div class='success-box'>
            <b>Active Resilient Path:</b> `{' → '.join(path_test)}`<br>
            * <b>Hop Count:</b> {hops_test}<br>
            * <b>Calculated Latency:</b> {lat_test} ms<br>
            * <b>Status:</b> Dynamic Routing Operational ✓
            </div>
            """, unsafe_allow_html=True)
        except nx.NetworkXNoPath:
            st.markdown("""
            <div class='error-box'>
            <b>Network Failure State:</b><br>
            * <b>Status:</b> Total Network Partition / Route Unavailable ✗<br>
            * <b>Action Required:</b> Click 'Reset All Faults' to restore connectivity.
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 4: TCP HANDSHAKE, UDP & ARP
# ==========================================
with tab4:
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("🤝 TCP 3-Way Handshake Visualizer")
        st.markdown("Before sending reliable data, TCP establishes a synchronized connection state:")
        
        if st.button("🚀 Simulate TCP Handshake"):
            st.markdown("""
            <div class='terminal'>
            [Client] -- (1) SYN [Seq=1000] --> [Server]<br>
            [Server] -- (2) SYN-ACK [Seq=5000, Ack=1001] --> [Client]<br>
            [Client] -- (3) ACK [Ack=5001] --> [Server]<br>
            [Status] Connection Established! Reliable Data Stream Open.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='terminal'>
            Click 'Simulate TCP Handshake' to view the connection establishment sequence.
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_t2:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("🧩 Address Resolution Protocol (ARP) Resolver")
        arp_ip = st.text_input("Target IP for ARP Resolution", "192.168.1.40")
        
        if st.button("🔍 Execute ARP Request"):
            st.markdown(f"""
            <div class='terminal'>
            [PC-1] Broadcast ARP Request: "Who has {arp_ip}?"<br>
            [Network] Broadcasted to Layer 2 MAC: FF:FF:FF:FF:FF:FF<br>
            [{arp_ip}] Unicast ARP Reply: "I have {arp_ip} at MAC AA:BB:CC:00:00:04"<br>
            [Cache] ARP Table updated successfully!
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='terminal'>
            ARP Table Cache:<br>
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
    st.subheader("📚 OSI Reference Model & TCP/IP Protocol Stack")
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
            st.markdown(f"**Protocols / Technologies:** `{protos}`")
            st.markdown(f"**Function:** {desc}")

# ==========================================
# TAB 6: EVENT LOG TERMINAL
# ==========================================
with tab6:
    st.subheader("📋 Simulation Event Log & History Terminal")
    log_text = "\n".join(st.session_state['logs']) if st.session_state['logs'] else "[00:00:00] CyberNet Simulation Laboratory Initialized."
    st.markdown(f"""
    <div class='terminal' style='height: 350px;'>
    {log_text}
    </div>
    """, unsafe_allow_html=True)
    if st.button("🗑️ Clear Logs"):
        st.session_state['logs'] = []
        st.rerun()
