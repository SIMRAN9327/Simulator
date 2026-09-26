import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import random
import time
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CyberNet // Interactive Computer Network Simulator",
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
    .metric-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
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
    st.session_state['stats'] = {
        'sent': 0, 'delivered': 0, 'dropped': 0, 'latency_sum': 0
    }
    
    # Initialize Default Network Graph (Demo Scenario 1: PC1 -> R1 -> R2/R3 -> R4 -> PC4)
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
    
    for node, attrs in nodes_data.items():
        G.add_node(node, **attrs)
        
    # Edges with properties: (u, v, bandwidth_mbps, latency_ms, loss_pct, status)
    edges_data = [
        ("PC-1", "R1", 1000, 2, 0.0, "Active"),
        ("R1", "R2", 100, 15, 1.0, "Active"),
        ("R1", "R3", 100, 25, 2.0, "Active"),
        ("R2", "R4", 100, 20, 1.0, "Active"),
        ("R3", "R4", 100, 18, 1.5, "Active"),
        ("R4", "PC-4", 1000, 2, 0.0, "Active"),
        ("R4", "Server-X", 1000, 5, 0.0, "Active")
    ]
    
    for u, v, bw, lat, loss, status in edges_data:
        G.add_edge(u, v, bandwidth=bw, latency=lat, loss=loss, status=status, congested=False, utilization=25)
        
    st.session_state['G'] = G

def log_event(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state['logs'].insert(0, f"[{timestamp}] {message}")

# Helper: Compute Dijkstra Cost based on Link Properties
def get_link_cost(u, v, data):
    if data['status'] == 'Failed':
        return float('inf')
    # Cost formula factoring in latency, bandwidth, and congestion penalty
    bw_factor = 1000.0 / max(data['bandwidth'], 1)
    util_penalty = 2.0 if data.get('congested', False) else 1.0
    cost = (data['latency'] * bw_factor * util_penalty) + (data['loss'] * 10)
    return max(1, int(cost))

# --- HEADER & DASHBOARD METRICS ---
st.title("🌐 CyberNet: Interactive Computer Network Simulator")
st.markdown("*B.Tech Computer Networking Laboratory // Real-Time Routing, Failure Simulation & OSI Protocol Visualizer*")

# Live Metrics Calculation
G = st.session_state['G']
total_nodes = G.number_of_nodes()
total_links = G.number_of_edges()
failed_links = sum(1 for u, v, d in G.edges(data=True) if d['status'] == 'Failed')
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

# --- MAIN NAVIGATION TABS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🗺️ Network Builder & Topology",
    "📦 Packet Simulation & Routing",
    "💥 Failure & Congestion Lab",
    "🚦 TCP vs UDP & ARP",
    "📚 OSI & TCP/IP Models",
    "📋 Event Log & History"
])

# ==========================================
# TAB 1: NETWORK BUILDER & TOPOLOGY
# ==========================================
with tab1:
    col_ctrl, col_viz = st.columns([1, 2])
    
    with col_ctrl:
        st.subheader("🛠️ Topology & Preset Manager")
        preset = st.selectbox("Load Network Preset", ["Standard Dual-Path (Demo 1)", "Star Topology", "Ring Topology", "Mesh Topology"])
        
        if st.button("🔄 Apply Preset Topology"):
            G_new = nx.Graph()
            if "Dual-Path" in preset:
                nodes = {"PC-1": ("PC", "192.168.1.10"), "PC-4": ("PC", "192.168.1.40"), "R1": ("Router", "192.168.1.1"), 
                         "R2": ("Router", "192.168.2.1"), "R3": ("Router", "192.168.3.1"), "R4": ("Router", "192.168.4.1")}
                for n, (t, ip) in nodes.items(): G_new.add_node(n, type=t, ip=ip, mac="AA:BB:CC:00:00:01")
                edges = [("PC-1", "R1", 1000, 2), ("R1", "R2", 100, 15), ("R1", "R3", 100, 25), 
                         ("R2", "R4", 100, 20), ("R3", "R4", 100, 18), ("R4", "PC-4", 1000, 2)]
                for u, v, bw, lat in edges: G_new.add_edge(u, v, bandwidth=bw, latency=lat, loss=0.5, status="Active", congested=False)
            elif "Star" in preset:
                center = "Core-Switch"
                G_new.add_node(center, type="Switch", ip="10.0.0.1", mac="AA:00:00:00:00:01")
                for i in range(1, 5):
                    pc = f"PC-{i}"
                    G_new.add_node(pc, type="PC", ip=f"192.168.1.{i}", mac=f"AA:BB:CC:00:00:0{i}")
                    G_new.add_edge(center, pc, bandwidth=1000, latency=5, loss=0.0, status="Active", congested=False)
            elif "Ring" in preset:
                pcs = ["PC-1", "PC-2", "PC-3", "PC-4"]
                for p in pcs: G_new.add_node(p, type="PC", ip="192.168.1.X", mac="AA:BB:CC:00:00:0X")
                for i in range(len(pcs)): G_new.add_edge(pcs[i], pcs[(i+1)%len(pcs)], bandwidth=100, latency=10, loss=1.0, status="Active", congested=False)
            else: # Mesh
                pcs = ["PC-1", "PC-2", "PC-3", "PC-4"]
                for p in pcs: G_new.add_node(p, type="PC", ip="192.168.1.X", mac="AA:BB:CC:00:00:0X")
                for i in range(len(pcs)):
                    for j in range(i+1, len(pcs)):
                        G_new.add_edge(pcs[i], pcs[j], bandwidth=1000, latency=8, loss=0.2, status="Active", congested=False)
            st.session_state['G'] = G_new
            log_event(f"Loaded network preset: {preset}")
            st.rerun()

        st.markdown("---")
        st.subheader("⚙️ Selected Link Inspector")
        edges_list = [f"{u} ↔ {v}" for u, v, d in st.session_state['G'].edges(data=True)]
        if edges_list:
            selected_edge = st.selectbox("Choose Link", edges_list)
            u, v = selected_edge.split(" ↔ ")
            edge_data = st.session_state['G'][u][v]
            
            new_bw = st.slider("Bandwidth (Mbps)", 10, 10000, int(edge_data['bandwidth']))
            new_lat = st.slider("Latency (ms)", 1, 100, int(edge_data['latency']))
            new_loss = st.slider("Packet Loss (%)", 0.0, 20.0, float(edge_data['loss']))
            
            if st.button("💾 Update Link Properties"):
                st.session_state['G'][u][v]['bandwidth'] = new_bw
                st.session_state['G'][u][v]['latency'] = new_lat
                st.session_state['G'][u][v]['loss'] = new_loss
                log_event(f"Updated link {u}-{v}: BW={new_bw}Mbps, Latency={new_lat}ms")
                st.success("Link properties updated successfully!")

    with col_viz:
        st.subheader("🗺️ Live Network Topology Graph")
        G = st.session_state['G']
        pos = nx.spring_layout(G, seed=42)
        
        # Plotly Graph Trace Generation
        edge_x, edge_y, edge_colors, edge_texts = [], [], [], []
        for u, v, d in G.edges(data=True):
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            if d['status'] == 'Failed':
                edge_colors.append('#f43f5e') # Red
                edge_texts.append(f"{u}-{v} [FAILED]")
            elif d.get('congested', False):
                edge_colors.append('#f59e0b') # Orange
                edge_texts.append(f"{u}-{v} [CONGESTED]")
            else:
                edge_colors.append('#38bdf8') # Blue
                edge_texts.append(f"{u}-{v} ({d['latency']}ms)")

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

# ==========================================
# TAB 2: PACKET SIMULATION & ROUTING ENGINE
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
                    # Dijkstra shortest path using calculated link costs
                    path = nx.shortest_path(G, source=source_node, target=dest_node, weight=lambda u, v, d: get_link_cost(u, v, d))
                    
                    # Calculate path metrics
                    total_lat = sum(G[path[i]][path[i+1]]['latency'] for i in range(len(path)-1))
                    total_loss = max(G[path[i]][path[i+1]]['loss'] for i in range(len(path)-1))
                    hops = len(path) - 1
                    
                    # Packet drop check based on probability
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
            st.markdown("#### 🔬 Simulated Packet Header & Payload")
            st.code(f"""
[Ethernet Frame] Src MAC: AA:BB:CC:00:00:01 | Dst MAC: CC:DD:EE:00:01:01
  └── [IP Packet]    Src IP: 192.168.1.10 | Dst IP: 192.168.1.40 | Protocol: {sim['protocol']}
        └── [Segment]  Source Port: 54321 | Dest Port: 80 | Size: {sim['size']} Bytes
              └── [Payload] HTTP GET /index.html (Simulated Data Stream)
            """, language="text")
        else:
            st.info("Configure parameters and click **'▶ SEND PACKET'** to observe routing and packet traversal.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Routing Table Display
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
# TAB 3: FAILURE & CONGESTION LABORATORY
# ==========================================
with tab3:
    st.subheader("💥 Network Failure Laboratory & Resilience Testing")
    st.markdown("Simulate link failures, router outages, or sudden traffic congestion to test dynamic re-routing using Dijkstra's algorithm.")
    
    col_lab1, col_lab2 = st.columns(2)
    
    with col_lab1:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("🔧 Fault Injection Controls")
        
        edges_list = [f"{u} ↔ {v}" for u, v, d in st.session_state['G'].edges(data=True)]
        target_edge = st.selectbox("Target Link for Failure/Congestion", edges_list)
        
        c_btn1, c_btn2, c_btn3 = st.columns(3)
        if c_btn1.button("💥 Fail Link"):
            u, v = target_edge.split(" ↔ ")
            st.session_state['G'][u][v]['status'] = 'Failed'
            log_event(f"ALERT: Link {u} ↔ {v} FAILED!")
            st.rerun()
            
        if c_btn2.button("🚦 Induce Congestion"):
            u, v = target_edge.split(" ↔ ")
            st.session_state['G'][u][v]['congested'] = True
            st.session_state['G'][u][v]['latency'] *= 3
            log_event(f"WARNING: Congestion induced on link {u} ↔ {v}.")
            st.rerun()
            
        if c_btn3.button("🔄 Restore All Links"):
            for u, v, d in st.session_state['G'].edges(data=True):
                d['status'] = 'Active'
                d['congested'] = False
                d['latency'] = max(2, d['latency'] // 3 if d['latency'] > 30 else d['latency'])
            log_event("SUCCESS: All network links restored to active status.")
            st.success("Network restored successfully!")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_lab2:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("📈 Dynamic Resilience & Before/After Comparison")
        
        st.markdown("""
        <div class='alert-box'>
        <b>Scenario Demonstration (Demo 2):</b><br>
        When primary link <b>R1 ↔ R2</b> or <b>R2 ↔ R4</b> fails, the routing engine automatically recalculates and shifts traffic through <b>R3</b>.
        </div>
        """, unsafe_allow_html=True)
        
        G = st.session_state['G']
        try:
            path_test = nx.shortest_path(G, source="PC-1", target="PC-4", weight=lambda u, v, d: get_link_cost(u, v, d))
            lat_test = sum(G[path_test[i]][path_test[i+1]]['latency'] for i in range(len(path_test)-1))
            st.success(f"✓ Current Active Route: `{' → '.join(path_test)}` (Latency: {lat_test} ms)")
        except:
            st.error("✗ Network Partitioned! No path available between PC-1 and PC-4.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 4: TCP vs UDP & ARP SIMULATION
# ==========================================
with tab4:
    col_tcp, col_arp = st.columns(2)
    
    with col_tcp:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("🚦 TCP vs. UDP Protocol Comparison")
        proto_choice = st.radio("Select Protocol for Comparison", ["TCP (Transmission Control Protocol)", "UDP (User Datagram Protocol)"])
        
        if "TCP" in proto_choice:
            st.markdown("""
            * **Connection-Oriented:** Establishes 3-way handshake (SYN, SYN-ACK, ACK).
            * **Reliability:** Guarantees packet delivery with acknowledgments (ACKs).
            * **Error Control:** Retransmits lost or corrupted segments.
            * **Flow Control:** Uses sliding window mechanism to prevent congestion.
            * *Use Cases:* Web (HTTP/HTTPS), File Transfer (FTP), Email (SMTP).
            """)
        else:
            st.markdown("""
            * **Connectionless:** No handshake required; sends packets immediately.
            * **Best-Effort Delivery:** No delivery guarantees, acknowledgments, or ordering.
            * **Low Overhead:** Minimal header size (8 bytes vs TCP's 20+ bytes).
            * **Speed:** Faster transmission, ideal for real-time streams.
            * *Use Cases:* Live Video Streaming, VoIP, Online Gaming, DNS lookups.
            """)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_arp:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("🧩 Address Resolution Protocol (ARP) Simulation")
        st.markdown("Resolves logical Layer 3 IP addresses to physical Layer 2 MAC addresses.")
        
        target_ip = st.text_input("Target IP Address to Query", "192.168.1.40")
        if st.button("🔍 Send ARP Request"):
            st.markdown(f"""
            <div class='terminal'>
            [PC-1] Broadcast ARP Request: "Who has {target_ip}?"<br>
            [Network] Frame sent to FF:FF:FF:FF:FF:FF (Broadcast)<br>
            [{target_ip}] Unicast ARP Reply: "{target_ip} is at MAC AA:BB:CC:00:00:04"<br>
            [PC-1] ARP Cache Updated successfully!
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='terminal'>
            ARP Cache Table:<br>
            ----------------------------------------<br>
            IP Address      MAC Address       Interface<br>
            192.168.1.1     CC:DD:EE:00:01:01 eth0<br>
            192.168.1.40    AA:BB:CC:00:00:04 eth0
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
# TAB 6: EVENT LOG & HISTORY
# ==========================================
with tab6:
    st.subheader("📋 Simulation Event Log & History Terminal")
    st.markdown("Real-time chronological log of network events, packet transmissions, failures, and recovery steps.")
    
    log_text = "\n".join(st.session_state['logs']) if st.session_state['logs'] else "[00:00:00] CyberNet Simulation Laboratory Initialized."
    st.markdown(f"""
    <div class='terminal' style='height: 350px;'>
    {log_text}
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑️ Clear Event Logs"):
        st.session_state['logs'] = []
        st.rerun()
