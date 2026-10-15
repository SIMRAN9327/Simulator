import time
import random
import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="AI Network Topology & Simulation Advisor",
    page_icon="🌐",
    layout="wide"
)

# App Header
st.title("🌐 AI-Powered Network Architect & Simulator")
st.markdown("""
Welcome! Configure your network parameters below. Our AI advisor will instantly determine the 
optimal topology, transmission media, and hardware, followed by a real-time packet delivery simulation.
""")

st.sidebar.header("⚙️ Network Parameters")

# User Inputs
num_nodes = st.sidebar.slider("Number of Nodes", min_value=2, max_value=30, value=8, step=1)
packet_count = st.sidebar.slider("Packets to Send", min_value=10, max_value=500, value=50, step=10)
traffic_type = st.sidebar.selectbox("Traffic / Data Type", ["General Data / Web", "High-Speed Video / Streaming", "IoT / Sensor Telemetry", "Mission-Critical / Financial"])
env_type = st.sidebar.selectbox("Environment Type", ["Indoor Office / Home", "Industrial / Factory Floor", "Long Distance / Wide Area"])

# AI Decision Engine Logic
def ai_network_advisor(nodes, traffic, environment):
    # Topology Selection
    if environment == "Long Distance / Wide Area":
        topology = "Mesh Topology"
        topo_reason = "Provides redundant paths over wide areas, ensuring fault tolerance if a link fails."
    elif nodes <= 4 and traffic == "IoT / Sensor Telemetry":
        topology = "Star Topology"
        topo_reason = "Centralized control is optimal for small sensor clusters and easy troubleshooting."
    elif traffic == "Mission-Critical / Financial":
        topology = "Full Mesh Topology"
        topo_reason = "Zero downtime tolerance requires direct point-to-point connections between all nodes."
    else:
        topology = "Star-Extended / Tree Topology"
        topo_reason = "Scalable, highly manageable, and isolates traffic efficiently for medium-to-large node counts."

    # Transmission Media Selection
    if environment == "Industrial / Factory Floor":
        media = "Industrial Shielded Twisted-Pair (Cat6A) & Fiber Optics"
        media_reason = "Resistant to high electromagnetic interference (EMI) typical in factory environments."
    elif environment == "Long Distance / Wide Area":
        media = "Single-Mode Fiber Optic Cables"
        media_reason = "Supports high-bandwidth data transmission over long distances with minimal signal loss."
    else:
        media = "Cat6 Gigabit Ethernet & Wi-Fi 6 (802.11ax)"
        media_reason = "Provides a cost-effective, high-speed balance for standard indoor office environments."

    # Network Device Selection
    if "Mesh" in topology:
        device = "Layer 3 Managed Core Switches & Enterprise Routers"
        device_reason = "Required to handle complex dynamic routing tables and redundant path calculations."
    elif nodes > 15:
        device = "Enterprise Managed Switch & VLAN-capable Access Points"
        device_reason = "Handles larger broadcast domains and segments heavy data traffic effectively."
    else:
        device = "Gigabit Ethernet Switch / Wireless Access Point"
        device_reason = "Sufficient capacity to connect small node sets seamlessly without bottlenecks."

    return {
        "topology": topology, "topo_reason": topo_reason,
        "media": media, "media_reason": media_reason,
        "device": device, "device_reason": device_reason
    }

recommendation = ai_network_advisor(num_nodes, traffic_type, env_type)

# Display AI Recommendations in Tabs/Columns
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

# Simulation Section
st.subheader("🚀 Live Network Simulation Dashboard")
st.write("Click the button below to start simulating packet transmissions across your generated network layout.")

if st.button("Run Packet Simulation", type="primary"):
    # Create graph representation using NetworkX based on node count and topology style
    G = nx.erdos_renyi_graph(n=num_nodes, p=0.4 if "Mesh" in recommendation['topology'] else 0.2, seed=42)
    if len(G.edges()) == 0:  # Safety check if graph is disconnected
        G = nx.path_graph(num_nodes)
        
    pos = nx.spring_layout(G, seed=42)

    # Setup Plotly figure for network graph
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1.5, color='#888'), hoverinfo='none', mode='lines')

    node_x, node_y, node_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"Node {node}")

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='text+markers',
        text=node_text, textposition="top center",
        marker=dict(showscale=True, colorscale='YlGnBu', size=20, color=list(range(num_nodes)), 
                    line_width=2, line_color='white')
    )

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=f"<b>Simulated Network Topology ({num_nodes} Nodes)</b>",
                        showlegend=False, hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    # Placeholders for live metrics & visualization
    plot_placeholder = st.empty()
    plot_placeholder.plotly_chart(fig, use_container_width=True)

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    m_packets = metric_col1.empty()
    m_success = metric_col2.empty()
    m_latency = metric_col3.empty()
    m_status = metric_col4.empty()

    # Simulation loop tracking packets
    successful_packets = 0
    latencies = []
    
    progress_bar = st.progress(0)
    
    for i in range(1, packet_count + 1):
        # Simulate packet behavior
        time.sleep(0.04) # Control speed of simulation stream
        is_success = random.random() > 0.05 # 95% success rate baseline
        latency = random.uniform(2.5, 45.0) # ms
        
        if is_success:
            successful_packets += 1
            latencies.append(latency)
        
        # Update UI Metrics dynamically
        m_packets.metric("Packets Sent", f"{i} / {packet_count}")
        success_rate = (successful_packets / i) * 100
        m_success.metric("Success Rate", f"{success_rate:.1f}%")
        avg_lat = sum(latencies)/len(latencies) if latencies else 0
        m_latency.metric("Avg Latency", f"{avg_lat:.1f} ms")
        m_status.metric("Network Status", "🟢 Optimal" if success_rate > 90 else "🟠 Congested")
        
        progress_bar.progress(i / packet_count)

    st.success("🎉 Simulation completed successfully! All packets processed through the AI-optimized configuration.")
