import streamlit as st
from agent import build_agent

st.set_page_config(page_title="Foggy Parking Spot Agent", layout="wide")

st.title("Foggy Parking Spot")
st.markdown("""Ask questions related to parking spot and get answers powered by AI.""")

if 'agent' not in st.session_state:
    st.session_state.agent = build_agent()

query = st.text_input("Your question:", placeholder="Ask about parking...")

if query:
    with st.spinner("Thinking..."):
        response = st.session_state.agent.run(query)
        st.markdown("### Response:")
        st.markdown(response['result'])