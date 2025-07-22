#!/usr/bin/env python3
"""
Demo script showing Google Maps links functionality
"""

import streamlit as st
from parking_knowledge import ParkingKnowledgeBase
from mcp_location_service import MCPLocationService

st.set_page_config(
    page_title="🗺️ Google Maps Links Demo",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Google Maps Links Demo - Foggy Park")
st.markdown("This demo shows how Google Maps links work in the parking assistant.")

# Sidebar with instructions
with st.sidebar:
    st.markdown("### 📋 Instructions")
    st.markdown("""
    1. Click the buttons below to test different parking queries
    2. Look for 📍 addresses in the responses
    3. Click on any address to open Google Maps
    4. Links open in a new tab/window
    """)
    
    st.markdown("### 🔧 Technical Details")
    st.markdown("""
    - Uses HTML `<a>` tags with `target="_blank"`
    - Proper URL encoding with `urllib.parse.quote_plus()`
    - Automatic San Francisco context addition
    - Works in both knowledge base and MCP service
    """)

# Main content
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💰 Affordable Parking")
    if st.button("🔍 Find Cheapest Parking", key="affordable"):
        with st.spinner("Finding affordable parking..."):
            kb = ParkingKnowledgeBase()
            response = kb.get_affordable_parking()
            st.markdown("**Response with Google Maps Links:**")
            st.markdown(response, unsafe_allow_html=True)

    st.markdown("### 🏢 Area-Specific Parking")
    area = st.selectbox("Choose an area:", ["Union Square", "Financial District", "SOMA", "Mission Bay"])
    if st.button(f"🔍 Find Parking in {area}", key="area"):
        with st.spinner(f"Finding parking in {area}..."):
            kb = ParkingKnowledgeBase()
            area_keywords = area.lower().split()
            response = kb.get_area_parking(area_keywords)
            st.markdown("**Response with Google Maps Links:**")
            st.markdown(response, unsafe_allow_html=True)

with col2:
    st.markdown("### 🕐 24/7 Parking")
    if st.button("🔍 Find 24/7 Parking", key="24_7"):
        with st.spinner("Finding 24/7 parking..."):
            kb = ParkingKnowledgeBase()
            response = kb.get_24_7_parking()
            st.markdown("**Response with Google Maps Links:**")
            st.markdown(response, unsafe_allow_html=True)

    st.markdown("### ⚡ EV Charging Parking")
    if st.button("🔍 Find EV Charging", key="ev"):
        with st.spinner("Finding EV charging parking..."):
            kb = ParkingKnowledgeBase()
            response = kb.get_ev_parking()
            st.markdown("**Response with Google Maps Links:**")
            st.markdown(response, unsafe_allow_html=True)

# Test section
st.markdown("---")
st.markdown("### 🧪 Link Format Testing")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**HTML Link (Current Method)**")
    kb = ParkingKnowledgeBase()
    test_address = "333 Post Street San Francisco, CA 94108"
    html_link = kb._format_address_with_link(test_address)
    st.markdown(html_link, unsafe_allow_html=True)

with col2:
    st.markdown("**Markdown Link (Alternative)**")
    markdown_link = kb._format_address_with_markdown_link(test_address)
    st.markdown(markdown_link)

with col3:
    st.markdown("**Streamlit Link Button**")
    maps_url = kb._create_google_maps_link(test_address)
    st.link_button("🗺️ Open in Maps", maps_url)

# Raw link display
st.markdown("### 🔗 Raw Link Examples")
st.code(f"HTML: {html_link}")
st.code(f"Markdown: {markdown_link}")
st.code(f"Direct URL: {maps_url}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🗺️ <strong>Google Maps Integration</strong> - Making navigation to parking spots effortless!</p>
    <p><small>Click any 📍 address to open Google Maps • Links open in new tab</small></p>
</div>
""", unsafe_allow_html=True)
