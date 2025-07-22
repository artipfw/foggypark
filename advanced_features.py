import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from datetime import datetime, timedelta
import random

def load_parking_data():
    """Load and process parking data for visualizations"""
    try:
        with open("sample/datav3.json", "r") as f:
            data = json.load(f)
        
        garages = []
        for garage in data.get("garages", []):
            if garage.get("name"):
                garages.append({
                    'name': garage.get('name', ''),
                    'address': garage.get('address', ''),
                    'hourly_rate': garage.get('hourlyRate', 0),
                    'features': len(garage.get('features', [])),
                    'phone': garage.get('phone', ''),
                    'website': garage.get('website', ''),
                    'hours': garage.get('hours', 'Unknown')
                })
        
        return pd.DataFrame(garages)
    except Exception as e:
        st.error(f"Error loading parking data: {e}")
        return pd.DataFrame()

def show_analytics_dashboard():
    """Display analytics dashboard"""
    st.header("📊 Parking Analytics Dashboard")
    
    df = load_parking_data()
    if df.empty:
        st.warning("No parking data available for analytics.")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Garages", len(df))
    
    with col2:
        avg_rate = df['hourly_rate'].mean()
        st.metric("Avg Hourly Rate", f"${avg_rate:.2f}")
    
    with col3:
        max_rate = df['hourly_rate'].max()
        st.metric("Highest Rate", f"${max_rate:.2f}")
    
    with col4:
        min_rate = df['hourly_rate'].min()
        st.metric("Lowest Rate", f"${min_rate:.2f}")
    
    # Price distribution chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Price Distribution")
        fig_hist = px.histogram(
            df, 
            x='hourly_rate', 
            nbins=10,
            title="Distribution of Hourly Rates",
            labels={'hourly_rate': 'Hourly Rate ($)', 'count': 'Number of Garages'}
        )
        fig_hist.update_layout(showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Features vs Price")
        fig_scatter = px.scatter(
            df, 
            x='features', 
            y='hourly_rate',
            title="Features vs Hourly Rate",
            labels={'features': 'Number of Features', 'hourly_rate': 'Hourly Rate ($)'},
            hover_data=['name']
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Top/Bottom garages
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💸 Most Expensive")
        top_expensive = df.nlargest(5, 'hourly_rate')[['name', 'hourly_rate', 'address']]
        for _, garage in top_expensive.iterrows():
            st.write(f"**{garage['name']}** - ${garage['hourly_rate']:.2f}/hr")
            st.caption(garage['address'])
    
    with col2:
        st.subheader("💰 Most Affordable")
        top_affordable = df.nsmallest(5, 'hourly_rate')[['name', 'hourly_rate', 'address']]
        for _, garage in top_affordable.iterrows():
            st.write(f"**{garage['name']}** - ${garage['hourly_rate']:.2f}/hr")
            st.caption(garage['address'])

def show_parking_map():
    """Display parking locations on a map"""
    st.header("🗺️ Parking Locations Map")
    
    # Sample coordinates for San Francisco garages (in a real app, you'd geocode the addresses)
    sample_locations = [
        {"name": "Downtown Garage", "lat": 37.7749, "lon": -122.4194, "rate": 8.0},
        {"name": "Union Square Parking", "lat": 37.7880, "lon": -122.4074, "rate": 12.0},
        {"name": "Financial District Lot", "lat": 37.7946, "lon": -122.3999, "rate": 15.0},
        {"name": "SOMA Parking", "lat": 37.7749, "lon": -122.4194, "rate": 6.0},
        {"name": "Mission Bay Garage", "lat": 37.7706, "lon": -122.3892, "rate": 4.0},
    ]
    
    df_map = pd.DataFrame(sample_locations)
    
    st.map(df_map[['lat', 'lon']], zoom=12)
    
    # Show details
    st.subheader("📍 Location Details")
    for location in sample_locations:
        with st.expander(f"{location['name']} - ${location['rate']}/hr"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Rate:** ${location['rate']}/hr")
                st.write(f"**Coordinates:** {location['lat']}, {location['lon']}")
            with col2:
                if st.button(f"Get Directions", key=f"directions_{location['name']}"):
                    st.info(f"Opening directions to {location['name']}...")

def show_usage_statistics():
    """Display usage statistics and trends"""
    st.header("📈 Usage Statistics")
    
    # Generate sample usage data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    usage_data = {
        'date': dates,
        'queries': [random.randint(10, 100) for _ in range(len(dates))],
        'unique_users': [random.randint(5, 50) for _ in range(len(dates))],
        'avg_response_time': [random.uniform(0.5, 3.0) for _ in range(len(dates))]
    }
    
    df_usage = pd.DataFrame(usage_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Daily Queries")
        fig_queries = px.line(
            df_usage, 
            x='date', 
            y='queries',
            title="Daily Query Volume"
        )
        st.plotly_chart(fig_queries, use_container_width=True)
    
    with col2:
        st.subheader("⚡ Response Time")
        fig_response = px.line(
            df_usage, 
            x='date', 
            y='avg_response_time',
            title="Average Response Time (seconds)"
        )
        st.plotly_chart(fig_response, use_container_width=True)
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_queries = df_usage['queries'].sum()
        st.metric("Total Queries (30d)", total_queries)
    
    with col2:
        avg_daily_users = df_usage['unique_users'].mean()
        st.metric("Avg Daily Users", f"{avg_daily_users:.0f}")
    
    with col3:
        avg_response = df_usage['avg_response_time'].mean()
        st.metric("Avg Response Time", f"{avg_response:.2f}s")

def show_feedback_system():
    """Display feedback collection system"""
    st.header("💬 Feedback & Suggestions")
    
    with st.form("feedback_form"):
        st.subheader("Help us improve Foggy Park!")
        
        rating = st.select_slider(
            "How would you rate your experience?",
            options=[1, 2, 3, 4, 5],
            value=5,
            format_func=lambda x: "⭐" * x
        )
        
        feedback_type = st.selectbox(
            "What type of feedback is this?",
            ["General Feedback", "Bug Report", "Feature Request", "Data Issue"]
        )
        
        feedback_text = st.text_area(
            "Your feedback:",
            placeholder="Tell us what you think or what we can improve..."
        )
        
        contact_email = st.text_input(
            "Email (optional):",
            placeholder="your.email@example.com"
        )
        
        submitted = st.form_submit_button("Submit Feedback")
        
        if submitted:
            if feedback_text.strip():
                # In a real app, you'd save this to a database
                st.success("Thank you for your feedback! We appreciate your input.")
                st.balloons()
            else:
                st.error("Please provide some feedback before submitting.")
    
    # Show recent feedback (mock data)
    st.subheader("📝 Recent Community Feedback")
    sample_feedback = [
        {"rating": 5, "text": "Great app! Found parking quickly.", "type": "General Feedback"},
        {"rating": 4, "text": "Would love to see real-time availability.", "type": "Feature Request"},
        {"rating": 5, "text": "Very helpful for finding cheap parking.", "type": "General Feedback"},
    ]
    
    for feedback in sample_feedback:
        with st.expander(f"{'⭐' * feedback['rating']} - {feedback['type']}"):
            st.write(feedback['text'])

def export_chat_history():
    """Export chat history functionality"""
    if 'chat_history' in st.session_state and st.session_state.chat_history:
        chat_data = []
        for chat in st.session_state.chat_history:
            chat_data.append({
                'Timestamp': chat['timestamp'],
                'Question': chat['question'],
                'Answer': chat['answer'],
                'Response Time (s)': chat['response_time']
            })
        
        df_export = pd.DataFrame(chat_data)
        csv = df_export.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Chat History",
            data=csv,
            file_name=f"foggy_park_chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No chat history to export yet. Start asking questions!")
