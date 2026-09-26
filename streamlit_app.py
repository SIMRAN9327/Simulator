import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import random
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CyberNet // Interactive Network Routing & Failure Simulator",
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
        padding: 24px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .success-box, .error-box {
        background-color: #1e293b;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 15px;
        font-family: monospace;
    }
    .success-box { border-left: 4px solid #10b981; }
    .error-box { border-left: 4px solid #f43f5e; }
    .concept-box {
        background-color: #0f172a;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 8px;
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True
    st.session_state['stats'] = {'sent': 0, 'delivered': 0, 'dropped': 0, 'latency_sum': 0}
    st.session_state['last_failure_comparison'] = None
    
    # Core Dual-Path Topology: PC1 -- R1 -- R2 -- PC2 (and R1 -- R3 -- PC2)
    G = nx.Graph()
    nodes_data = {
        "PC-1": {"type": "PC", "ip": "192.168.1.10"},
        "PC-2": {"type": "PC", "ip": "192.168.1.20"},
        "R1": {"type": "Router", "ip": "192.168.1.1"},
        "R2": {"type": "Router", "ip": "192.168.2.1"},
        "R3": {"type": "Router", "ip": "192.168.3.1"}
    }
    for node, attrs in nodes_data.items(): 
        G.add_node(node, **attrs)
    
    edges_data = [
        ("PC-1", "R1", 5, "Active"),
        ("R1", "R2", 10, "Active"),
        ("R2", "PC-2", 15, "Active"),
        ("R1", "R3", 15, "Active"),
        ("R3", "PC-2", 20, "Active")
    ]
    for u, v, lat, status in edges_data:
        G.add_edge(u, v, latency=lat, status=status)
    st.session_state['G'] = G

def get_link_cost(u, v, data):
    if data.get('status') == 'Failed':
        return float('inf')
    return data.get('latency', 10)

# --- HEADER & METRICS ---
st.title("🌐 CyberNet: Interactive Network Routing & Failure Simulator")
st.markdown("*B.Tech Computer Networks Project // Dijkstra Shortest-Path & Dynamic Rerouting Engine*")

G = st.session_state['G']
total_nodes = G.number_of_nodes()
active_links = sum(1 for u, v, d in G.edges(data=True) if d.get('status') == 'Active')
total_links = G.number_of_edges()
sent = st.session_state['stats']['sent']
delivered = st.session_state['stats']['delivered']
avg_lat = int(st.session_state['stats']['latency_sum'] / delivered) if delivered > 0 else 0

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Network Nodes", total_nodes)
m2.metric("Active Links", f"{active_links}/{total_links}")
m3.metric("Packets Sent", sent)
m4.metric("Delivered", delivered)
m5.metric("Avg Latency", f"{avg_lat} ms")

st.markdown("<br>", unsafe_allow_html=True)

# --- 3 MAIN STREAMLINED TABS ---
tab1, tab2, tab3 = st.tabs([
    "🗺️ Network Topology",
    "📦 Packet Simulator",
    "💥 Failure Lab"
])

# ==========================================
# TAB 1: NETWORK TOPOLOGY
# ==========================================
with tab1:
    col_info, col_viz = st.columns([1, 1], gap="large")
    
    with col_info:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("🗺️ Network Architecture")
        st.markdown("""
        This simulator features a robust **Dual-Path Enterprise Topology**:
        * **Source & Destination:** `PC-1` and `PC-2`
        * **Primary Path:** `PC-1 ── R1 ── R2 ── PC-2` (Lower Latency: **30 ms**)
        * **Backup Path:** `PC-1 ── R1 ── R3 ── PC-2` (Higher Latency: **35 ms**)
        
        Use the tabs above to transmit packets or simulate link outages in real-time.
        """)
        
        st.markdown("### Active Link States")
        link_status_data = []
        for u, v, d in G.edges(data=True):
            link_status_data.append({"Link": f"{u} ↔ {v}", "Latency": f"{d['latency']} ms", "Status": d['status']})
        st.table(link_status_data)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_viz:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("Live Topology Graph")
        
        pos = nx.spring_layout(G, seed=42)
        
        edge_x, edge_y, edge_colors = [], [], []
        for u, v, d in G.edges(data=True):
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_colors.append('#f43f5e' if d.get('status') == 'Failed' else '#38bdf8')

        node_x, node_y, node_text, node_colors = [], [], [], []
        for node in G.nodes():
            node_x.append(pos[node][0])
            node_y.append(pos[node][1])
            node_text.append(node)
            node_colors.append('#38bdf8' if 'PC' in node else '#8b5cf6')

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=edge_x, y=edge_y, line=dict(width=3, color='#38bdf8'), mode='lines', hoverinfo='none'))
        fig.add_trace(go.Scatter(x=node_x, y=node_y, mode='text+markers',
            marker=dict(size=30, color=node_colors, line=dict(width=2, color='#ffffff')),
            text=node_text, textposition="top center", hoverinfo='text'))
        
        fig.update_layout(showlegend=False, xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                          yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                          template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=420)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 2: PACKET SIMULATOR
# ==========================================
with tab2:
    col_sim_ctrl, col_sim_res = st.columns([1, 1], gap="large")
    
    with col_sim_ctrl:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("📦 Transmit Packet")
        
        nodes_list = list(G.nodes())
        source_node = st.selectbox("Source Device", nodes_list, index=0)
        dest_node = st.selectbox("Destination Device", nodes_list, index=1)
        
        if st.button("▶ SEND PACKET", type="primary"):
            if source_node == dest_node:
                st.warning("Source and destination cannot be identical!")
            else:
                try:
                    path = nx.shortest_path(G, source=source_node, target=dest_node, weight=lambda u, v, d: get_link_cost(u, v, d))
                    total_lat = sum(G[path[i]][path[i+1]]['latency'] for i in range(len(path)-1))
                    hops = len(path) - 1
                    
                    st.session_state['stats']['sent'] += 1
                    st.session_state['stats']['delivered'] += 1
                    st.session_state['stats']['latency_sum'] += total_lat
                    
                    st.session_state['last_packet'] = {
                        'path': path, 'latency': total_lat, 'hops': hops, 'status': 'DELIVERED SUCCESSFULLY'
                    }
                except nx.NetworkXNoPath:
                    st.error("Route Unavailable! Check for failed links in the Failure Lab.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_sim_res:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("📊 Routing Metrics & Inspection")
        
        if 'last_packet' in st.session_state:
            pkt = st.session_state['last_packet']
            st.markdown(f"""
            <div class='success-box'>
            <b>Status:</b> ✓ {pkt['status']}<br>
            <b>Computed Route:</b> `{' ── '.join(pkt['path'])}`
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            c1.metric("Hop Count", pkt['hops'])
            c2.metric("Total Latency", f"{pkt['latency']} ms")
        else:
            st.info("Select source and destination, then click **'▶ SEND PACKET'**.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 3: FAILURE LAB
# ==========================================
with tab3:
    col_fail_ctrl, col_fail_res = st.columns([1, 1], gap="large")
    
    with col_fail_ctrl:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("💥 Link Failure & Rerouting Lab")
        st.markdown("Simulate a network outage by failing a link along the primary path:")
        
        edges_list = [f"{u} ↔ {v}" for u, v, d in G.edges(data=True)]
        target_edge = st.selectbox("Select Link to Break", edges_list, index=1)
        
        col_b1, col_b2 = st.columns(2)
        if col_b1.button("💥 Fail Link"):
            u, v = target_edge.split(" ↔ ")
            orig_path = ["PC-1", "R1", "R2", "PC-2"]
            orig_lat = 30
            
            # Break link
            G[u][v]['status'] = 'Failed'
            
            # Compute new path
            try:
                new_path = nx.shortest_path(G, source="PC-1", target="PC-2", weight=lambda u, v, d: get_link_cost(u, v, d))
                new_lat = sum(G[new_path[i]][new_path[i+1]]['latency'] for i in range(len(new_path)-1))
                
                st.session_state['last_failure_comparison'] = {
                    'failed_link': f"{u} ↔ {v}",
                    'orig_path': orig_path, 'orig_lat': orig_lat,
                    'new_path': new_path, 'new_lat': new_lat
                }
            except nx.NetworkXNoPath:
                st.error("Total Network Partition!")
                
        if col_b2.button("🔄 Restore All Links"):
            for u, v, d in G.edges(data=True):
                d['status'] = 'Active'
            st.session_state['last_failure_comparison'] = None
            st.success("All links restored!")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_fail_res:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("📊 Dynamic Rerouting Comparison")
        
        # Safe lookup using .get() to prevent any KeyError
        if st.session_state.get('last_failure_comparison'):
            fc = st.session_state['last_failure_comparison']
            st.markdown(f"""
            <div class='error-box'>
            <b>Alert: Link {fc['failed_link']} Failed!</b><br>
            Dijkstra's algorithm detected the outage and instantly recalculated the shortest path.
            </div>
            
            <div class='success-box'>
            <b>Original Route:</b> `{' ── '.join(fc['orig_path'])}` ({fc['orig_lat']} ms)<br>
            <b>New Rerouted Path:</b> `{' ── '.join(fc['new_path'])}` ({fc['new_lat']} ms)
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Select a link and click **'💥 Fail Link'** to observe dynamic rerouting in action.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# CONCEPTS SECTION (FOR VIVA PREP)
# ==========================================
st.markdown("""
<div class='concept-box'>
<h3>📚 Core Networking & Algorithm Concepts (Viva Reference)</h3>
<ul>
    <li><b>Dijkstra's Shortest-Path Algorithm:</b> Used by routing protocols (like OSPF) to compute the optimal path with the minimum cumulative cost (latency) from source to destination.</li>
    <li><b>Dynamic Rerouting:</b> When a link fails, its weight is set to infinity. The graph algorithm automatically updates routing tables and diverts traffic through alternative backup links.</li>
    <li><b>Packets & Hops:</b> Data is broken into packets. Each intermediate router represents a "hop" where the packet is inspected and forwarded toward its destination.</li>
</ul>
</div>
""", unsafe_allow_html=True)
