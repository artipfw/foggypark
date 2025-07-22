#!/usr/bin/env python3
"""
Test script to verify Streamlit markdown link rendering
"""

import streamlit as st
from parking_knowledge import ParkingKnowledgeBase

st.set_page_config(page_title="Test Google Maps Links", page_icon="🗺️")

st.title("🗺️ Testing Google Maps Links in Streamlit")

st.markdown("### Direct Markdown Link Test")
st.markdown("Here's a direct link: [Google Maps](https://maps.google.com/maps?q=Union+Square%2C+San+Francisco%2C+CA)")

st.markdown("### Parking Knowledge Base Test")

if st.button("Test Affordable Parking Links"):
    kb = ParkingKnowledgeBase()
    response = kb.get_affordable_parking()
    
    st.markdown("**Response with Google Maps Links:**")
    st.markdown(response)

if st.button("Test Union Square Parking Links"):
    kb = ParkingKnowledgeBase()
    response = kb.get_area_parking(['union', 'square'])
    
    st.markdown("**Response with Google Maps Links:**")
    st.markdown(response)

st.markdown("### Manual Link Test")
test_address = "123 Market Street San Francisco, CA 94105"
kb = ParkingKnowledgeBase()
formatted_link = kb._format_address_with_link(test_address)

st.markdown("**Formatted Address Link:**")
st.markdown(formatted_link)

st.markdown("### Raw Link Test")
import urllib.parse
encoded_address = urllib.parse.quote_plus(f"{test_address}, San Francisco, CA")
raw_link = f"https://maps.google.com/maps?q={encoded_address}"

st.markdown(f"**Raw Link:** {raw_link}")
st.markdown(f"**Markdown Link:** [{test_address}]({raw_link})")
