import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from utils.data_handler import DataHandler

st.set_page_config(page_title="Visualization", page_icon="📊", layout="wide")

# Initialize data handler
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = DataHandler()

st.title("📊 Circadian Rhythm Visualization")
st.markdown("Analyze your health metrics and circadian patterns over time")

# Load data
data = st.session_state.data_handler.load_data()

if data.empty:
    st.warning("📝 No data available for visualization. Please add some entries first using the Data Entry page.")
    st.stop()

# Convert timestamp to datetime
data['timestamp'] = pd.to_datetime(data['timestamp'])
data['date'] = data['timestamp'].dt.date
data['time'] = data['timestamp'].dt.time
data['hour'] = data['timestamp'].dt.hour
data['day_of_week'] = data['timestamp'].dt.day_name()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Person selection
available_people = sorted(data['person_id'].unique())
selected_person = st.sidebar.selectbox(
    "Select Person",
    options=available_people,
    index=0
)

# Date range selection
min_date = data['date'].min()
max_date = data['date'].max()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Handle single date selection
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

# Filter data
filtered_data = data[
    (data['person_id'] == selected_person) &
    (data['date'] >= start_date) &
    (data['date'] <= end_date)
].copy()

if filtered_data.empty:
    st.warning("No data found for the selected filters. Please adjust your selection.")
    st.stop()

# Display metrics summary
st.subheader(f"📈 Summary for {selected_person}")
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_hr = filtered_data['heart_rate'].mean()
    st.metric("Avg Heart Rate", f"{avg_hr:.1f} BPM")

with col2:
    avg_systolic = filtered_data['systolic_bp'].mean()
    st.metric("Avg Systolic BP", f"{avg_systolic:.1f} mmHg")

with col3:
    avg_diastolic = filtered_data['diastolic_bp'].mean()
    st.metric("Avg Diastolic BP", f"{avg_diastolic:.1f} mmHg")

with col4:
    avg_energy = filtered_data['energy_level'].mean()
    st.metric("Avg Energy Level", f"{avg_energy:.1f}/10")

# Main visualizations
st.markdown("---")

# Time series charts
st.subheader("🕐 Time Series Analysis")

tab1, tab2, tab3, tab4 = st.tabs(["Heart Rate", "Blood Pressure", "Energy Level", "All Metrics"])

with tab1:
    fig_hr = px.line(
        filtered_data,
        x='timestamp',
        y='heart_rate',
        title='Heart Rate Over Time',
        labels={'heart_rate': 'Heart Rate (BPM)', 'timestamp': 'Date & Time'}
    )
    fig_hr.update_traces(line=dict(color='red', width=2))
    st.plotly_chart(fig_hr, use_container_width=True)

with tab2:
    fig_bp = go.Figure()
    fig_bp.add_trace(go.Scatter(
        x=filtered_data['timestamp'],
        y=filtered_data['systolic_bp'],
        mode='lines+markers',
        name='Systolic',
        line=dict(color='blue', width=2)
    ))
    fig_bp.add_trace(go.Scatter(
        x=filtered_data['timestamp'],
        y=filtered_data['diastolic_bp'],
        mode='lines+markers',
        name='Diastolic',
        line=dict(color='orange', width=2)
    ))
    fig_bp.update_layout(
        title='Blood Pressure Over Time',
        xaxis_title='Date & Time',
        yaxis_title='Blood Pressure (mmHg)'
    )
    st.plotly_chart(fig_bp, use_container_width=True)

with tab3:
    fig_energy = px.line(
        filtered_data,
        x='timestamp',
        y='energy_level',
        title='Energy Level Over Time',
        labels={'energy_level': 'Energy Level', 'timestamp': 'Date & Time'}
    )
    fig_energy.update_traces(line=dict(color='green', width=2))
    fig_energy.update_layout(yaxis=dict(range=[1, 10]))
    st.plotly_chart(fig_energy, use_container_width=True)

with tab4:
    # Normalized all metrics chart
    normalized_data = filtered_data.copy()
    
    # Normalize each metric to 0-1 scale for comparison
    for col in ['heart_rate', 'systolic_bp', 'diastolic_bp', 'energy_level']:
        min_val = normalized_data[col].min()
        max_val = normalized_data[col].max()
        if max_val > min_val:
            normalized_data[f'{col}_norm'] = (normalized_data[col] - min_val) / (max_val - min_val)
        else:
            normalized_data[f'{col}_norm'] = 0.5
    
    fig_all = go.Figure()
    fig_all.add_trace(go.Scatter(
        x=normalized_data['timestamp'],
        y=normalized_data['heart_rate_norm'],
        mode='lines',
        name='Heart Rate',
        line=dict(color='red', width=2)
    ))
    fig_all.add_trace(go.Scatter(
        x=normalized_data['timestamp'],
        y=normalized_data['systolic_bp_norm'],
        mode='lines',
        name='Systolic BP',
        line=dict(color='blue', width=2)
    ))
    fig_all.add_trace(go.Scatter(
        x=normalized_data['timestamp'],
        y=normalized_data['diastolic_bp_norm'],
        mode='lines',
        name='Diastolic BP',
        line=dict(color='orange', width=2)
    ))
    fig_all.add_trace(go.Scatter(
        x=normalized_data['timestamp'],
        y=normalized_data['energy_level_norm'],
        mode='lines',
        name='Energy Level',
        line=dict(color='green', width=2)
    ))
    fig_all.update_layout(
        title='All Metrics Normalized (0-1 scale)',
        xaxis_title='Date & Time',
        yaxis_title='Normalized Value'
    )
    st.plotly_chart(fig_all, use_container_width=True)

# Circadian pattern analysis
st.markdown("---")
st.subheader("🌙 Circadian Pattern Analysis")

col1, col2 = st.columns(2)

with col1:
    # Average by hour of day
    hourly_avg = filtered_data.groupby('hour').agg({
        'heart_rate': 'mean',
        'systolic_bp': 'mean',
        'diastolic_bp': 'mean',
        'energy_level': 'mean'
    }).reset_index()
    
    fig_hourly = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Heart Rate by Hour', 'Energy Level by Hour', 'Systolic BP by Hour', 'Diastolic BP by Hour'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig_hourly.add_trace(
        go.Scatter(x=hourly_avg['hour'], y=hourly_avg['heart_rate'], 
                  mode='lines+markers', name='Heart Rate', line=dict(color='red')),
        row=1, col=1
    )
    
    fig_hourly.add_trace(
        go.Scatter(x=hourly_avg['hour'], y=hourly_avg['energy_level'], 
                  mode='lines+markers', name='Energy Level', line=dict(color='green')),
        row=1, col=2
    )
    
    fig_hourly.add_trace(
        go.Scatter(x=hourly_avg['hour'], y=hourly_avg['systolic_bp'], 
                  mode='lines+markers', name='Systolic BP', line=dict(color='blue')),
        row=2, col=1
    )
    
    fig_hourly.add_trace(
        go.Scatter(x=hourly_avg['hour'], y=hourly_avg['diastolic_bp'], 
                  mode='lines+markers', name='Diastolic BP', line=dict(color='orange')),
        row=2, col=2
    )
    
    fig_hourly.update_layout(height=600, title_text="Average Metrics by Hour of Day")
    fig_hourly.update_xaxes(title_text="Hour of Day")
    
    st.plotly_chart(fig_hourly, use_container_width=True)

with col2:
    # Day of week patterns
    dow_avg = filtered_data.groupby('day_of_week').agg({
        'heart_rate': 'mean',
        'systolic_bp': 'mean',
        'diastolic_bp': 'mean',
        'energy_level': 'mean'
    }).reset_index()
    
    # Order days of week
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_avg['day_of_week'] = pd.Categorical(dow_avg['day_of_week'], categories=day_order, ordered=True)
    dow_avg = dow_avg.sort_values('day_of_week')
    
    # Create radar chart for day of week patterns
    fig_radar = go.Figure()
    
    # Normalize values for radar chart
    metrics = ['heart_rate', 'systolic_bp', 'diastolic_bp', 'energy_level']
    for metric in metrics:
        values = dow_avg[metric].tolist()
        values.append(values[0])  # Close the radar chart
        days = dow_avg['day_of_week'].tolist()
        days.append(days[0])
        
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=days,
            fill='toself',
            name=metric.replace('_', ' ').title()
        ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True)
        ),
        showlegend=True,
        title="Weekly Pattern Radar Chart"
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)

# Correlation analysis
st.markdown("---")
st.subheader("🔗 Correlation Analysis")

correlation_data = filtered_data[['heart_rate', 'systolic_bp', 'diastolic_bp', 'energy_level']]
correlation_matrix = correlation_data.corr()

fig_corr = px.imshow(
    correlation_matrix,
    text_auto=True,
    aspect="auto",
    title="Correlation Matrix of Health Metrics",
    color_continuous_scale="RdBu_r"
)

st.plotly_chart(fig_corr, use_container_width=True)

# Statistical insights
st.markdown("---")
st.subheader("📊 Statistical Insights")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Heart Rate Statistics:**")
    hr_stats = filtered_data['heart_rate'].describe()
    st.write(f"• Mean: {hr_stats['mean']:.1f} BPM")
    st.write(f"• Std Dev: {hr_stats['std']:.1f} BPM")
    st.write(f"• Range: {hr_stats['min']:.0f} - {hr_stats['max']:.0f} BPM")
    
    st.markdown("**Energy Level Statistics:**")
    energy_stats = filtered_data['energy_level'].describe()
    st.write(f"• Mean: {energy_stats['mean']:.1f}/10")
    st.write(f"• Std Dev: {energy_stats['std']:.1f}")
    st.write(f"• Range: {energy_stats['min']:.0f} - {energy_stats['max']:.0f}")

with col2:
    st.markdown("**Blood Pressure Statistics:**")
    systolic_stats = filtered_data['systolic_bp'].describe()
    diastolic_stats = filtered_data['diastolic_bp'].describe()
    st.write(f"• Systolic Mean: {systolic_stats['mean']:.1f} mmHg")
    st.write(f"• Diastolic Mean: {diastolic_stats['mean']:.1f} mmHg")
    st.write(f"• BP Range: {systolic_stats['min']:.0f}/{diastolic_stats['min']:.0f} - {systolic_stats['max']:.0f}/{diastolic_stats['max']:.0f}")
    
    # Find peak energy times
    if len(filtered_data) > 0:
        peak_energy_times = filtered_data[filtered_data['energy_level'] == filtered_data['energy_level'].max()]['hour'].unique()
        st.markdown("**Peak Energy Hours:**")
        st.write(f"• {', '.join(map(str, sorted(peak_energy_times)))}:00")

# Export filtered data
st.markdown("---")
if st.button("📥 Export Filtered Data as CSV"):
    csv = filtered_data.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"circadian_data_{selected_person}_{start_date}_{end_date}.csv",
        mime="text/csv"
    )
