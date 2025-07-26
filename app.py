import streamlit as st
import pandas as pd
import os
from utils.data_handler import DataHandler

# Configure page
st.set_page_config(
    page_title="Circadian Rhythm Tracker",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data handler
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = DataHandler()

# Main page content
st.title("🌙 Circadian Rhythm Tracker")
st.markdown("---")

st.markdown("""
## Welcome to your Circadian Rhythm Tracking Dashboard

This application helps you track and visualize your circadian rhythm patterns through various health metrics:

### Features:
- **📝 Data Entry**: Record your daily health metrics including heart rate, blood pressure, and energy levels
- **📊 Visualization**: Interactive charts showing your circadian patterns over time
- **💾 Data Management**: View, filter, and export your recorded data

### Getting Started:
1. Navigate to the **Data Entry** page to start recording your daily metrics
2. Use the **Visualization** page to analyze your circadian patterns
3. Manage your data through the **Data Management** page

### Health Metrics Tracked:
- **Heart Rate** (BPM): Resting heart rate measurements
- **Blood Pressure** (mmHg): Systolic and diastolic readings
- **Energy Level** (1-10): Subjective energy assessment scale
"""
)

# Display recent data summary if available
data = st.session_state.data_handler.load_data()
if not data.empty:
    st.markdown("---")
    st.subheader("📈 Quick Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_records = len(data)
        st.metric("Total Records", total_records)
    
    with col2:
        unique_people = data['person_id'].nunique()
        st.metric("People Tracked", unique_people)
    
    with col3:
        if not data.empty:
            latest_date = pd.to_datetime(data['timestamp']).max().strftime('%Y-%m-%d')
            st.metric("Latest Entry", latest_date)
    
    with col4:
        avg_energy = data['energy_level'].mean()
        st.metric("Avg Energy Level", f"{avg_energy:.1f}/10")
    
    # Recent entries
    st.markdown("---")
    st.subheader("🕐 Recent Entries")
    recent_data = data.tail(5).sort_values('timestamp', ascending=False)
    st.dataframe(
        recent_data[['person_id', 'timestamp', 'heart_rate', 'systolic_bp', 'diastolic_bp', 'energy_level']],
        use_container_width=True
    )
else:
    st.info("👆 Start by adding your first entry using the Data Entry page in the sidebar!")
