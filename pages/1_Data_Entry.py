import streamlit as st
import pandas as pd
from datetime import datetime, time
from utils.data_handler import DataHandler
from utils.validators import validate_health_metrics

st.set_page_config(page_title="Data Entry", page_icon="📝")

# Initialize data handler
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = DataHandler()

st.title("📝 Data Entry")
st.markdown("Record your daily circadian rhythm health metrics")

# Create form for data entry
with st.form("health_metrics_form"):
    st.subheader("Health Metrics Entry")
    
    col1, col2 = st.columns(2)
    
    with col1:
        person_id = st.text_input(
            "Person ID *",
            help="Unique identifier for tracking (e.g., your name or ID)",
            placeholder="e.g., john_doe"
        )
        
        # Date and time inputs
        entry_date = st.date_input(
            "Date *",
            value=datetime.now().date(),
            help="Date of measurement"
        )
        
        entry_time = st.time_input(
            "Time *",
            value=datetime.now().time(),
            help="Time of measurement"
        )
        
        heart_rate = st.number_input(
            "Heart Rate (BPM) *",
            min_value=30,
            max_value=200,
            value=70,
            help="Resting heart rate in beats per minute"
        )
    
    with col2:
        # Blood pressure inputs
        st.markdown("**Blood Pressure (mmHg) ***")
        systolic_bp = st.number_input(
            "Systolic",
            min_value=70,
            max_value=250,
            value=120,
            help="Upper blood pressure reading"
        )
        
        diastolic_bp = st.number_input(
            "Diastolic",
            min_value=40,
            max_value=150,
            value=80,
            help="Lower blood pressure reading"
        )
        
        energy_level = st.slider(
            "Energy Level *",
            min_value=1,
            max_value=10,
            value=5,
            help="Rate your current energy level (1=Very Low, 10=Very High)"
        )
        
        # Optional notes
        notes = st.text_area(
            "Notes (Optional)",
            placeholder="Any additional observations or context...",
            help="Optional notes about your current state or activities"
        )
    
    # Form submission
    submitted = st.form_submit_button("💾 Save Entry", type="primary")
    
    if submitted:
        # Validate inputs
        if not person_id.strip():
            st.error("❌ Person ID is required")
        else:
            # Combine date and time
            timestamp = datetime.combine(entry_date, entry_time)
            
            # Validate health metrics
            validation_result = validate_health_metrics(
                heart_rate, systolic_bp, diastolic_bp, energy_level
            )
            
            if validation_result['valid']:
                # Create data entry
                entry_data = {
                    'person_id': person_id.strip(),
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'heart_rate': heart_rate,
                    'systolic_bp': systolic_bp,
                    'diastolic_bp': diastolic_bp,
                    'energy_level': energy_level,
                    'notes': notes.strip() if notes else ''
                }
                
                # Save data
                success = st.session_state.data_handler.add_entry(entry_data)
                
                if success:
                    st.success("✅ Health metrics saved successfully!")
                    st.balloons()
                    
                    # Display saved entry
                    st.markdown("**Saved Entry:**")
                    display_data = {
                        'Person ID': entry_data['person_id'],
                        'Timestamp': entry_data['timestamp'],
                        'Heart Rate': f"{entry_data['heart_rate']} BPM",
                        'Blood Pressure': f"{entry_data['systolic_bp']}/{entry_data['diastolic_bp']} mmHg",
                        'Energy Level': f"{entry_data['energy_level']}/10"
                    }
                    
                    if entry_data['notes']:
                        display_data['Notes'] = entry_data['notes']
                    
                    for key, value in display_data.items():
                        st.write(f"**{key}:** {value}")
                else:
                    st.error("❌ Failed to save entry. Please try again.")
            else:
                st.error(f"❌ Validation Error: {validation_result['message']}")

# Display recent entries for this person
if person_id and person_id.strip():
    st.markdown("---")
    st.subheader(f"📊 Recent Entries for {person_id}")
    
    data = st.session_state.data_handler.load_data()
    if not data.empty:
        person_data = data[data['person_id'] == person_id.strip()].tail(10)
        if not person_data.empty:
            person_data_sorted = person_data.sort_values('timestamp', ascending=False)
            st.dataframe(
                person_data_sorted[['timestamp', 'heart_rate', 'systolic_bp', 'diastolic_bp', 'energy_level', 'notes']],
                use_container_width=True
            )
        else:
            st.info(f"No entries found for {person_id}")
    else:
        st.info("No data available yet")

# Instructions
st.markdown("---")
st.markdown("""
### 📋 Instructions:
- **Person ID**: Use a consistent identifier to track your data over time
- **Timestamp**: Record the exact date and time of your measurement
- **Heart Rate**: Measure your resting heart rate (preferably upon waking)
- **Blood Pressure**: Take readings in a relaxed state
- **Energy Level**: Rate how energetic you feel on a scale of 1-10
- **Notes**: Add context like sleep quality, caffeine intake, exercise, etc.

### 💡 Tips for Accurate Tracking:
- Take measurements at consistent times each day
- Record data in similar conditions (e.g., before coffee, after waking)
- Include contextual notes that might affect your metrics
- Track regularly to identify patterns in your circadian rhythm
""")
