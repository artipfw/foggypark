import streamlit as st
from agent import build_agent
import time
from datetime import datetime
from __about__ import __version__
from advanced_features import (
    show_analytics_dashboard,
    show_parking_map,
    show_usage_statistics,
    show_feedback_system,
    export_chat_history
)

# Page configuration
st.set_page_config(
    page_title="🅿️ Foggy Park - Smart Parking Assistant",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        background-color: #f8f9fa;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }

    .assistant-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }

    .stats-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid #e0e0e0;
    }

    .feature-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }

    .feature-card:hover {
        transform: translateY(-5px);
    }

    .nav-button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .nav-button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    with st.spinner("🚀 Initializing Foggy Park Assistant..."):
        try:
            st.session_state.agent = build_agent()
            st.session_state.agent_ready = True
        except Exception as e:
            st.session_state.agent_ready = False
            st.session_state.error_message = str(e)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'query_count' not in st.session_state:
    st.session_state.query_count = 0

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Chat"

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div class="sidebar-section">
        <h2 style="text-align: center; color: #667eea;">🅿️ Foggy Park</h2>
        <p style="text-align: center; color: #666;">Smart Parking Assistant</p>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown("### 🧭 Navigation")
    pages = {
        "💬 Chat": "Chat",
        "📊 Analytics": "Analytics",
        "🗺️ Map": "Map",
        "📈 Statistics": "Statistics",
        "💬 Feedback": "Feedback"
    }

    for page_name, page_key in pages.items():
        if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
            st.session_state.current_page = page_key

    st.markdown("---")

    # Stats Dashboard
    st.markdown("### 📊 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <h4 style="color: #667eea;">{st.session_state.query_count}</h4>
            <p style="margin: 0; font-size: 0.8rem;">Queries</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <h4 style="color: #764ba2;">{len(st.session_state.chat_history)}</h4>
            <p style="margin: 0; font-size: 0.8rem;">Chats</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick Actions
    st.markdown("### 🚀 Quick Actions")
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    if st.button("🔄 Reset Assistant", use_container_width=True):
        if 'agent' in st.session_state:
            del st.session_state.agent
        st.session_state.agent_ready = False
        st.rerun()

    # Export functionality
    if st.session_state.chat_history:
        export_chat_history()

    st.markdown("---")

    # System Status
    st.markdown("### ⚡ System Status")
    if st.session_state.get('agent_ready', False):
        st.success("✅ Assistant Ready")
    else:
        st.error("❌ Assistant Not Ready")
        if 'error_message' in st.session_state:
            st.error(f"Error: {st.session_state.error_message}")

    # Version information
    st.sidebar.info(f"Version: {__version__}")

# Main Content Area
current_page = st.session_state.current_page

if current_page == "Chat":
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🅿️ Foggy Park</h1>
        <h3>Your Smart Parking Assistant for San Francisco</h3>
        <p>Find the perfect parking spot with AI-powered recommendations</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get('agent_ready', False):
        st.error("🚨 Assistant is not ready. Please check the system status in the sidebar.")
        st.stop()

    # Feature highlights
    st.markdown("### ✨ What I Can Help You With")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>💰 Price Comparison</h4>
            <p>Find the most affordable parking options in your area</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>📍 Location Search</h4>
            <p>Discover parking near specific landmarks and addresses</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>⭐ Feature Matching</h4>
            <p>Find parking with specific amenities like EV charging</p>
        </div>
        """, unsafe_allow_html=True)

    # Example questions
    st.markdown("### 💡 Try These Questions")
    example_questions = [
        "What are the cheapest parking options in downtown SF?",
        "Find parking garages near Union Square",
        "Which garages are open 24/7?",
        "Show me parking with EV charging stations",
        "What's the hourly rate for parking in SOMA?",
        "Find covered parking near the Financial District"
    ]

    cols = st.columns(3)
    for i, question in enumerate(example_questions):
        with cols[i % 3]:
            if st.button(question, key=f"example_{i}", use_container_width=True):
                st.session_state.current_query = question

    # Chat interface
    st.markdown("### 💬 Ask About Parking")

    # Initialize clear flag
    if 'clear_input' not in st.session_state:
        st.session_state.clear_input = False

    # Input area
    query = st.text_input(
        "Your question:",
        placeholder="Ask me anything about parking in San Francisco...",
        value=st.session_state.get('current_query', '') if not st.session_state.clear_input else '',
        key="query_input"
    )

    # Clear the current_query after it's been used
    if 'current_query' in st.session_state:
        del st.session_state.current_query

    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🧹 Clear", use_container_width=True)

    if clear_button:
        st.session_state.clear_input = True
        st.rerun()

    # Reset clear flag after rerun
    if st.session_state.clear_input:
        st.session_state.clear_input = False

    # Process query
    if (ask_button or query) and query.strip():
        with st.spinner("🤔 Thinking..."):
            try:
                start_time = time.time()
                response = st.session_state.agent.invoke(query)
                end_time = time.time()

                # Add to chat history
                st.session_state.chat_history.append({
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'question': query,
                    'answer': response['result'],
                    'response_time': round(end_time - start_time, 2)
                })
                st.session_state.query_count += 1

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 📝 Conversation History")

        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"🕐 {chat['timestamp']} - {chat['question'][:50]}...", expanded=(i==0)):
                # User message
                st.markdown("**🙋 You:**")
                st.markdown(chat['question'])

                st.markdown("---")

                # Assistant response with HTML rendering for links
                st.markdown("**🤖 Assistant:**")
                st.markdown(chat['answer'], unsafe_allow_html=True)

                st.caption(f"⏱️ Response time: {chat['response_time']}s")

elif current_page == "Analytics":
    show_analytics_dashboard()

elif current_page == "Map":
    show_parking_map()

elif current_page == "Statistics":
    show_usage_statistics()

elif current_page == "Feedback":
    show_feedback_system()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🅿️ <strong>Foggy Park</strong> - Making parking in San Francisco easier, one query at a time!</p>
    <p><small>Powered by AI • Built with ❤️ for San Francisco • Enhanced Version</small></p>
</div>
""", unsafe_allow_html=True)