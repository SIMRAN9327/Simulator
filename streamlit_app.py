import time
import random
import streamlit as st
import networkx as nx
import plotly.graph_objects as go

# Page Configuration with Dark Theme defaults
st.set_page_config(
    page_title="AI Network Topology & Live Routing Simulator",
    page_icon="🌐",
    layout="wide"
)

# Custom CSS styling for dark enterprise aesthetic
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
st.title("🌐 AI-Powered Enterprise Network Architect & Route Simulator")
st.markdown("""
Configure your enterprise network parameters below. Our AI advisor designs the optimal topology based on 
engineering trade-offs, maps out true shortest-path routing, and runs a **high-performance multi-hop packet simulation**.
""")

st.sidebar.header("⚙️ Enterprise Network Config")

# User Inputs (Up to 1000 nodes supported)
num_nodes = st.sidebar.slider("Number of Nodes", min_value=2, max_value=1000, value=25, step=5)
packet_count = st.sidebar.slider("Packets to Simulate", min_value=10, max_value=200, value=40, step=10)
sim_speed = st.sidebar.select_slider("Simulation Animation Speed", options=["Fast", "Normal", "Slow"], value="Normal")
traffic_type = st.sidebar.selectbox("Traffic / Data Type", ["General Data / Web", "High-Speed Video / Streaming", "IoT / Sensor Telemetry", "Mission-Critical / Financial"])
env_type = st.sidebar.selectbox("Environment Type", ["Indoor Office / Home", "Industrial / Factory Floor", "Long Distance / Wide Area"])

# Delay mapping based on speed setting
speed_delay = {"Fast": 0.005, "Normal": 0.02, "Slow": 0.06}[sim_speed]

# Advanced Engineering AI Decision Engine
def ai_network_advisor(nodes, traffic, environment):
    if environment == "Long Distance / Wide Area":
        if traffic == "Mission-Critical / Financial":
            topology = "Full Mesh Topology"
            topo_reason = "Provides direct multi-path connectivity, minimizing transit hops for low-latency financial feeds over wide areas."
        else:
            topology = "Partial Mesh Topology"
            topo_reason = "Balances long-range routing redundancy with capital expenditure by interconnecting critical distribution sites."
    elif nodes <= 12 and traffic == "IoT / Sensor Telemetry":
        topology = "Star Topology"
        topo_reason = "Centralized collection hub simplifies low-power sensor tracking and minimizes local control overhead."
    elif traffic == "Mission-Critical / Financial" and nodes <= 40:
        topology = "Full Mesh Topology"
        topo_reason = "Provides absolute path redundancy so that any single link severance is bypassed instantaneously."
    elif traffic == "High-Speed Video / Streaming" and nodes <= 35:
        topology = "Ring / Token-Ring Protected Topology"
        topo_reason = "Supports structured sequential stream distribution with built-in dual-counter-rotating ring protection."
    elif nodes > 150:
        topology = "Hierarchical Star-Tree Topology"
        topo_reason = "Organizes massive scale volumes (up to 1,000 nodes) into Core, Distribution, and Access tiers to curb broadcast domains."
    else:
        topology = "Extended Star Topology"
        topo_reason = "Cost-effective modular design isolating local switch traffic while scaling easily across office floors."

    # Transmission Media Logic (Engineering Context)
    if environment == "Industrial / Factory Floor":
        if traffic == "High-Speed Video / Streaming":
            media = "Armored Single-Mode Fiber Optics"
            media_reason = "Required for high-bandwidth video throughput while immune to severe electromagnetic interference (EMI) from heavy machinery."
        else:
            media = "Industrial Shielded Twisted-Pair (Cat6A STP) with Grounding"
            media_reason = "Heavy copper shielding prevents electromagnetic noise degradation typical on factory floors."
    elif environment == "Long Distance / Wide Area":
        media = "Single-Mode Fiber Optic Cables (SMF)"
        media_reason = "Utilizes pure light pulses to span long geographic distances with minimal attenuation or signal loss."
    else: # Indoor Office / Home
        if traffic == "High-Speed Video / Streaming":
            media = "Cat6A Copper Ethernet & Wi-Fi 7 (802.11be) Multi-Gig Backbones"
            media_reason = "Delivers multi-gigabit throughput rates required for heavy low-latency 4K/8K video streams."
        elif traffic == "IoT / Sensor Telemetry":
            media = "Low-Power Wireless (LoRaWAN / Zigbee) & Structured Cat5e"
            media_reason = "LoRaWAN offers long-range low-power sensor packet collection, while Cat5e drops support local wired controller nodes."
        else:
            media = "Cat6 Gigabit Ethernet (GbE) & Wi-Fi 6 (802.11ax)"
            media_reason = "Provides an optimal balance of cost-efficiency and high-speed enterprise throughput for office users."

    # Network Hardware Logic
    if nodes > 200 or "Mesh" in topology:
        device = "Layer 3 Enterprise Core Switches & Modular Routers"
        device_reason = "Engineered to run dynamic routing protocols (OSPF/BGP) and handle heavy multi-path packet switching."
    elif nodes > 50:
        device = "Managed Gigabit Switches with VLAN Segmentation"
        device_reason = "Segments heavy broadcast domains to secure departmental workflows and control traffic priority."
    else:
        device = "Smart Gigabit Switch & High-Density Access Points"
        device_reason = "Sufficient capacity to connect localized node clusters without hardware backplane bottlenecks."

    return {
        "topology": topology, "topo_reason": topo_reason,
        "media": media, "media_reason": media_reason,
        "device": device, "device_reason": device_reason
    }

recommendation = ai_network_advisor(num_nodes, traffic_type, env_type)

# Display AI Recommendations
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

# Alternative Topologies & Trade-off Analysis
st.subheader("⚖️ Engineering Trade-off Analysis (Rejected Alternatives)")
st.write(f"To understand why the AI selected **{recommendation['topology']}**, here is how alternative layouts compare and why they were deprioritized:")

alt_col1, alt_col2 = st.columns(2)

with alt_col1:
    st.markdown("#### ⭕ Ring Topology")
    st.markdown("- **Trade-off:** Data travels sequentially. While dual-ring setups support bypass protection, single rings suffer high latency hops as node counts grow.")
    st.markdown(f"- **Why deprioritized:** {'Selected for structured stream efficiency.' if 'Ring' in recommendation['topology'] else 'Inadequate scalability for dense enterprise workloads.'}")

    st.markdown("#### 🚌 Bus / Linear Topology")
    st.markdown("- **Trade-off:** Relies on a single central shared cable backbone. High traffic triggers widespread packet collisions.")
    st.markdown("- **Why deprioritized:** High vulnerability to single-point physical cuts and severe bandwidth bottlenecks.")

with alt_col2:
    st.markdown("#### ⭐ Standard Star Topology")
    star_reason = "Selected as the core baseline design." if "Star" in recommendation['topology'] else "Central hub dependency introduces a critical single point of failure for large-scale clustered routing."
    st.markdown("- **Disadvantage:** All traffic transits through a central switch or controller.")
    st.markdown(f"- **Why deprioritized:** {star_reason}")

    st.markdown("#### 🕸️ Traditional Full Mesh Topology")
    mesh_reason = "Adopted for mission-critical core resiliency." if "Full Mesh" in recommendation['topology'] else "Exorbitantly high cabling, port, and interface transceiver costs as node density increases."
    st.markdown("- **Disadvantage:** Every node connects to every other node, causing exponential port overhead.")
    st.markdown(f"- **Why deprioritized:** {mesh_reason}")

st.markdown("---")

# Simulation Section with Accurate Topology Generation & Shortest-Path Routing
st.subheader("🚀 Live Multi-Hop Route Simulation Dashboard")
st.write("Watch active data packets route dynamically across calculated multi-hop paths from source to destination.")

if st.button("Start Live Route Simulation", type="primary"):
    # Generate NetworkX graph precisely matching recommended topology
    topo_name = recommendation['topology']
    
    if "Ring" in topo_name:
        G = nx.cycle_graph(num_nodes)
    elif "Full Mesh" in topo_name and num_nodes <= 50:
        G = nx.complete_graph(num_nodes)
    elif "Star" in topo_name:
        G = nx.star_graph(num_nodes - 1) if num_nodes > 1 else nx.path_graph(2)
    elif "Hierarchical" in topo_name:
        # Generate true multi-tier tree graph
        branching = max(2, min(4, int(num_nodes ** 0.35)))
        try:
            G = nx.full_rary_tree(branching, num_nodes)
            # Add cross-links to ensure higher connectivity for mesh-like feel
            if num_nodes > 10:
                G.add_edge(0, min(5, num_nodes-1))
        except Exception:
            G = nx.erdos_renyi_graph(n=num_nodes, p=0.15, seed=42)
    else: # Partial Mesh / Extended Star
        G = nx.watts_strogatz_graph(n=num_nodes, k=min(4, max(2, num_nodes-1)), p=0.3, seed=42)

    # Ensure graph connectivity backup
    if not nx.is_connected(G) and num_nodes <= 200:
        components = list(nx.connected_components(G))
        for i in range(len(components) - 1):
            G.add_edge(list(components[i])[0], list(components[i+1])[0])

    # Compute layout
    sqrt_val = num_nodes ** 0.5
    pos = nx.spring_layout(G, seed=42, k=1.5 / sqrt_val if sqrt_val > 0 else None)

    # Prepare static traces for edges and nodes
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

    node_size = max(4, min(16, 250 // int(num_nodes**0.4)))
    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers',
        hoverinfo='text', text=node_text,
        marker=dict(size=node_size, color='#58a6ff', line=dict(width=1, color='#1f6feb'))
    )

    # Active packet marker trace
    packet_trace = go.Scatter(
        x=[], y=[], mode='markers',
        marker=dict(size=node_size * 1.4, color='#3fb950', symbol='diamond', line=dict(width=1, color='#ffffff')),
        name='Active Packet'
    )

    fig = go.Figure(data=[edge_trace, node_trace, packet_trace],
                    layout=go.Layout(
                        title=f"<b>Simulated Routing Matrix ({recommendation['topology']} | {num_nodes} Nodes)</b>",
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
    
    node_list = list(G.nodes())
    if len(node_list) < 2:
        node_list = [0, 1]

    # Simulate Packet Transmissions via Shortest Paths
    for i in range(1, packet_count + 1):
        # Pick distinct source and destination nodes
        src = random.choice(node_list)
        dst = random.choice(node_list)
        while dst == src and len(node_list) > 1:
            dst = random.choice(node_list)

        try:
            path = nx.shortest_path(G, source=src, target=dst)
        except Exception:
            path = [src, dst] if src != dst else [src]

        # Animate packet moving hop-by-hop along the shortest path
        path_failed = False
        for h in range(len(path) - 1):
            n1, n2 = path[h], path[h+1]
            p1, p2 = pos[n1], pos[n2]

            # Model congestion / link failure probability based on node load
            if random.random() < (0.02 + (num_nodes / 5000.0)):
                path_failed = True
                break

            steps = 3
            for step in range(steps + 1):
                fraction = step / steps
                curr_x = p1[0] + fraction * (p2[0] - p1[0])
                curr_y = p1[1] + fraction * (p2[1] - p1[1])
                
                fig.data[2].x = [curr_x]
                fig.data[2].y = [curr_y]
                plot_placeholder.plotly_chart(fig, use_container_width=True, key=f"sim_plot_{i}_{h}_{step}")
                time.sleep(speed_delay)

        # Calculate metrics based on path length and simulated network load conditions
        hop_count = len(path) - 1
        simulated_latency = max(1.2, hop_count * 4.5 + random.uniform(0.5, 4.0))

        if not path_failed:
            successful_packets += 1
            latencies.append(simulated_latency)

        # Update Telemetry Metrics (clearly labeled as simulated)
        m_packets.metric("Packets Processed", f"{i} / {packet_count}")
        success_rate = (successful_packets / i) * 100
        m_success.metric("Simulated Success Rate", f"{success_rate:.1f}%")
        avg_lat = sum(latencies)/len(latencies) if latencies else 0
        m_latency.metric("Simulated Avg Latency", f"{avg_lat:.2f} ms")
        m_status.metric("Network Load Status", "🟢 Nominal" if success_rate > 92 else "🟠 Congested")
        
        progress_bar.progress(i / packet_count)

    # Clear active packet marker when simulation finishes
    fig.data[2].x = []
    fig.data[2].y = []
    plot_placeholder.plotly_chart(fig, use_container_width=True, key="sim_plot_final")
    st.success("🎉 Simulation run completed successfully across optimized network routing matrices!")
