#!/usr/bin/env python3
"""
Simple test for Google Maps links in Streamlit
"""

import streamlit as st
from parking_knowledge import ParkingKnowledgeBase

st.title("🗺️ Google Maps Links Test")

# Test different link formats
st.markdown("### 1. Direct HTML Link")
html_link = '<a href="https://maps.google.com/maps?q=Union+Square%2C+San+Francisco%2C+CA" target="_blank">Union Square, San Francisco</a>'
st.markdown(f"📍 {html_link}", unsafe_allow_html=True)

st.markdown("### 2. Markdown Link")
markdown_link = "[Union Square, San Francisco](https://maps.google.com/maps?q=Union+Square%2C+San+Francisco%2C+CA)"
st.markdown(f"📍 {markdown_link}")

st.markdown("### 3. Streamlit Link Button")
if st.link_button("🗺️ Open Union Square in Google Maps", "https://maps.google.com/maps?q=Union+Square%2C+San+Francisco%2C+CA"):
    st.success("Link clicked!")

st.markdown("### 4. Test Parking Knowledge Base")
if st.button("Get Affordable Parking with Links"):
    kb = ParkingKnowledgeBase()
    response = kb.get_affordable_parking()
    st.markdown(response, unsafe_allow_html=True)

st.markdown("### 5. Test Individual Address")
kb = ParkingKnowledgeBase()
test_address = "333 Post Street San Francisco, CA 94108"
formatted_address = kb._format_address_with_link(test_address)
st.markdown(f"**Formatted Address:** {formatted_address}", unsafe_allow_html=True)

# Also test markdown version
markdown_address = kb._format_address_with_markdown_link(test_address)
st.markdown(f"**Markdown Version:** {markdown_address}")
