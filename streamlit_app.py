import time
import random
import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import pandas as pd

# Page Configuration with Dark Theme defaults
st.set_page_config(
    page_title="AI Network Topology & Live Simulation Advisor",
    page_icon="🌐",
    layout="wide"
)

# Custom CSS styling for a cohesive dark aesthetic
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("🌐 AI-Powered Network Architect & Live Packet Simulator")
st.markdown("""
Configure your enterprise network parameters below. Our AI advisor designs the optimal topology, 
transmission media, and hardware, breaks down why other topologies were rejected, and runs a **live animation of packets**.
""")

st.sidebar.header("⚙️ Enterprise Network Config")

# User Inputs (Up to 1000 nodes supported)
num_nodes = st.sidebar.slider("Number of Nodes", min_value=2, max_value=1000, value=25, step=5)
packet_count = st.sidebar.slider("Packets to Send", min_value=10, max_value=200, value=40, step=10)
traffic_type = st.sidebar.selectbox("Traffic / Data Type", ["General Data / Web", "High-Speed Video / Streaming", "IoT / Sensor Telemetry", "Mission-Critical / Financial"])
env_type = st.sidebar.selectbox("Environment Type", ["Indoor Office / Home", "Industrial / Factory Floor", "Long Distance / Wide Area"])

# Advanced AI Decision Engine Logic
def ai_network_advisor(nodes, traffic, environment):
    # --- Topology Logic ---
    if environment == "Long Distance / Wide Area":
        topology = "Mesh Topology"
        topo_reason = "Provides redundant long-range routing paths, guaranteeing multi-point fault tolerance."
    elif nodes <= 12 and traffic == "IoT / Sensor Telemetry":
        topology = "Star Topology"
        topo_reason = "Centralized hub collection point simplifies sensor node tracking and drops overhead."
    elif traffic == "Mission-Critical / Financial":
        topology = "Full Mesh Topology"
        topo_reason = "Zero-failure tolerance necessitates direct, dedicated point-to-point links between all nodes."
    else:
        topology = "Hierarchical Star-Tree Topology"
        topo_reason = "Efficiently clusters massive node volumes (up to 1,000+) while curbing broadcast congestion."

    # --- Transmission Media Logic (Fully Dynamic) ---
    if environment == "Industrial / Factory Floor":
        if traffic == "High-Speed Video / Streaming":
            media = "Armored Single-Mode Fiber Optics"
            media_reason = "Mandatory for high-bandwidth video throughput while completely immune to high industrial EMI."
        else:
            media = "Industrial Shielded Twisted-Pair (Cat6A STP) with Grounding"
            media_reason = "Heavy copper shielding prevents electromagnetic noise degradation from heavy factory machinery."
    elif environment == "Long Distance / Wide Area":
        media = "Single-Mode Fiber Optic Cables (SMF)"
        media_reason = "Utilizes light pulses to span kilometers with virtually zero attenuation or signal loss."
    else: # Indoor Office / Home
        if traffic == "High-Speed Video / Streaming":
            media = "Cat6A Copper Ethernet & Wi-Fi 7 (802.11be) Multi-Gig Backbones"
            media_reason = "Delivers multi-gigabit throughput rates required for heavy 4K/8K video streaming streams."
        elif traffic == "IoT / Sensor Telemetry":
            media = "Low-Power Wireless (LoRaWAN / Zigbee) & Cat5e Drops"
            media_reason = "Optimized for low-bandwidth, high-density sensor packet bursts over wide indoor coverage."
        else:
            media = "Cat6 Gigabit Ethernet (GbE) & Wi-Fi 6 (802.11ax)"
            media_reason = "Provides an optimal balance of cost-effectiveness and high-speed throughput for general office users."

    # --- Network Hardware Logic ---
    if nodes > 200 or "Mesh" in topology:
        device = "Layer 3 Enterprise Core Switches & Modular Routers"
        device_reason = "Engineered to process dynamic routing table algorithms and massive simultaneous routing loops."
    elif nodes > 50:
        device = "Managed Gigabit Switches with VLAN Partitioning"
        device_reason = "Segments heavy broadcast traffic domains to secure workloads and pace data frames."
    else:
        device = "Smart Gigabit Switch & High-Density Access Points"
        device_reason = "Sufficient capacity to connect localized node sets seamlessly without hardware bottlenecks."

    return {
        "topology": topology, "topo_reason": topo_reason,
        "media": media, "media_reason": media_reason,
        "device": device, "device_reason": device_reason
    }

recommendation = ai_network_advisor(num_nodes, traffic_type, env_type)

# Display AI Recommendations in Dark Styled Containers
st.subheader("🤖 AI Recommended Architecture")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🔀 Topology")
    st.info(f"**{recommendation['topology']}**")
    st.write(recommendation['topo_reason'])

with col2:
    st.markdown("### 🔌 Transmission Media")
    st.success(f"**{recommendation['media']}**")
    st.write(recommendation['media_reason'])

with col3:
    st.markdown("### 📦 Network Hardware")
    st.warning(f"**{recommendation['device']}**")
    st.write(recommendation['device_reason'])

st.markdown("---")

# Alternative Topologies & Disadvantages Breakdown
st.subheader("⚖️ Why Other Topologies Were Rejected (Trade-off Analysis)")
st.write("To understand why the AI selected **" + recommendation['topology'] + "**, here is how alternative layouts compare and why they failed your specific requirements:")

# Build an interactive or structured table/card breakdown of unchosen alternatives
alt_col1, alt_col2 = st.columns(2)

with alt_col1:
    st.markdown("#### ⭕ Ring Topology")
    st.markdown("- **Disadvantage:** Data travels sequentially through every node. If a single cable breaks or a node fails, the entire network ring goes down.")
    st.markdown("- **Why rejected:** Poor scalability for high node counts and creates a single point of absolute failure on every segment.")

    st.markdown("#### 🚌 Bus Topology")
    st.markdown("- **Disadvantage:** Relies on a single central cable (the backbone). Heavy traffic triggers severe packet collisions, and cable damage halves the network.")
    st.markdown("- **Why rejected:** Highly unstable for modern heavy packet workloads and completely inadequate for large scale operations.")

with alt_col2:
    st.markdown("#### ⭐ Standard Star Topology")
    st.markdown("- **Disadvantage:** Everything routes directly through a central hub or switch. If the central device fails, all connected peripheral nodes lose network access.")
    st.markdown("- **Why rejected:** " + ("Suitable for small counts, but fails under heavy multi-path long-distance requirements or massive 1,000-node cluster constraints." if num_nodes > 50 else "Not optimal for your chosen environment resilience level.")))

    st.markdown("#### 🕸️ Traditional Mesh Topology")
    st.markdown("- **Disadvantage:** Exorbitantly high cable and port costs; wiring complexity grows exponentially as node density increases.")
    st.markdown("- **Why rejected:** " + ("Used where required, but unnecessary infrastructure overhead for lower-density scenarios." if "Mesh" not in recommendation['topology'] else "Chosen due to critical reliability needs.")))

st.markdown("---")

# Simulation Section
st.subheader("🚀 Live Packet-Flow Simulation Dashboard")
st.write("Watch active data packets hop across connections in real-time.")

if st.button("Start Live Packet Simulation", type="primary"):
    p_val = 0.05 if num_nodes > 100 else (0.3 if "Mesh" in recommendation['topology'] else 0.15)
    G = nx.erdos_renyi_graph(n=num_nodes, p=max(p_val, 2.0/num_nodes), seed=42)
    
    if not nx.is_connected(G) and num_nodes <= 150:
        G = nx.connected_watts_strogatz_graph(n=num_nodes, k=min(4, num_nodes-1), p=0.1, seed=42)
    
    sqrt_val = num_nodes ** 0.5
    pos = nx.spring_layout(G, seed=42, k=1.0 / sqrt_val if sqrt_val > 0 else None)

    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.0 if num_nodes > 200 else 1.5, color='#30363d'),
        hoverinfo='none', mode='lines'
    )

    node_x, node_y, node_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"Node {node}")

    node_size = max(4, min(18, 300 // int(num_nodes**0.5)))
    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers',
        hoverinfo='text', text=node_text,
        marker=dict(size=node_size, color='#58a6ff', line=dict(width=1, color='#1f6feb'))
    )

    packet_trace = go.Scatter(
        x=[], y=[], mode='markers',
        marker=dict(size=node_size * 1.2, color='#3fb950', symbol='diamond', line=dict(width=1, color='#ffffff')),
        name='Active Packets'
    )

    fig = go.Figure(data=[edge_trace, node_trace, packet_trace],
                    layout=go.Layout(
                        title=f"<b>Live Traffic Routing Matrix ({num_nodes} Nodes Active)</b>",
                        showlegend=False, hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=40),
                        paper_bgcolor='#0e1117',
                        plot_bgcolor='#0e1117',
                        font=dict(color='#e0e0e0'),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    plot_placeholder = st.empty()
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    m_packets = metric_col1.empty()
    m_success = metric_col2.empty()
    m_latency = metric_col3.empty()
    m_status = metric_col4.empty()

    successful_packets = 0
    latencies = []
    progress_bar = st.progress(0)
    
    edge_list = list(G.edges())
    if not edge_list:
        edge_list = [(0, 1)]

    for i in range(1, packet_count + 1):
        active_edge = random.choice(edge_list)
        start_pos = pos[active_edge[0]]
        end_pos = pos[active_edge[1]]

        steps = 4
        for step in range(steps + 1):
            fraction = step / steps
            curr_x = start_pos[0] + fraction * (end_pos[0] - start_pos[0])
            curr_y = start_pos[1] + fraction * (end_pos[1] - start_pos[1])
            
            fig.data[2].x = [curr_x]
            fig.data[2].y = [curr_y]
            plot_placeholder.plotly_chart(fig, use_container_width=True)
            time.sleep(0.01)

        is_success = random.random() > 0.04
        latency = random.uniform(1.2, 38.0)
        
        if is_success:
            successful_packets += 1
            latencies.append(latency)
        
        m_packets.metric("Packets Sent", f"{i} / {packet_count}")
        success_rate = (successful_packets / i) * 100
        m_success.metric("Success Rate", f"{success_rate:.1f}%")
        avg_lat = sum(latencies)/len(latencies) if latencies else 0
        m_latency.metric("Avg Latency", f"{avg_lat:.2f} ms")
        m_status.metric("Network Status", "🟢 Optimal" if success_rate > 90 else "🟠 High Load")
        
        progress_bar.progress(i / packet_count)

    fig.data[2].x = []
    fig.data[2].y = []
    plot_placeholder.plotly_chart(fig, use_container_width=True)
    st.success("🎉 Simulation cycle finalized successfully across all network nodes!")
