import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_handler import DataHandler

st.set_page_config(page_title="Data Management", page_icon="💾", layout="wide")

# Initialize data handler
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = DataHandler()

st.title("💾 Data Management")
st.markdown("View, filter, edit, and manage your circadian rhythm data")

# Load data
data = st.session_state.data_handler.load_data()

if data.empty:
    st.warning("📝 No data available. Please add some entries first using the Data Entry page.")
    st.stop()

# Convert timestamp to datetime for better handling
data['timestamp'] = pd.to_datetime(data['timestamp'])

# Sidebar filters
st.sidebar.header("🔍 Data Filters")

# Person filter
available_people = ['All'] + sorted(data['person_id'].unique().tolist())
selected_person = st.sidebar.selectbox("Filter by Person", available_people)

# Date range filter
min_date = data['timestamp'].dt.date.min()
max_date = data['timestamp'].dt.date.max()

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

# Metric filters
st.sidebar.markdown("**Filter by Health Metrics:**")
heart_rate_range = st.sidebar.slider(
    "Heart Rate (BPM)",
    min_value=int(data['heart_rate'].min()),
    max_value=int(data['heart_rate'].max()),
    value=(int(data['heart_rate'].min()), int(data['heart_rate'].max()))
)

energy_level_range = st.sidebar.slider(
    "Energy Level",
    min_value=int(data['energy_level'].min()),
    max_value=int(data['energy_level'].max()),
    value=(int(data['energy_level'].min()), int(data['energy_level'].max()))
)

# Apply filters
filtered_data = data.copy()

if selected_person != 'All':
    filtered_data = filtered_data[filtered_data['person_id'] == selected_person]

filtered_data = filtered_data[
    (filtered_data['timestamp'].dt.date >= start_date) &
    (filtered_data['timestamp'].dt.date <= end_date) &
    (filtered_data['heart_rate'] >= heart_rate_range[0]) &
    (filtered_data['heart_rate'] <= heart_rate_range[1]) &
    (filtered_data['energy_level'] >= energy_level_range[0]) &
    (filtered_data['energy_level'] <= energy_level_range[1])
]

# Display summary statistics
st.subheader("📊 Data Summary")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Records", len(filtered_data))

with col2:
    unique_people = filtered_data['person_id'].nunique()
    st.metric("People Tracked", unique_people)

with col3:
    if not filtered_data.empty:
        date_range_days = (filtered_data['timestamp'].max() - filtered_data['timestamp'].min()).days + 1
        st.metric("Date Range (Days)", date_range_days)

with col4:
    if not filtered_data.empty:
        avg_entries_per_day = len(filtered_data) / max(1, date_range_days)
        st.metric("Avg Entries/Day", f"{avg_entries_per_day:.1f}")

with col5:
    if not filtered_data.empty:
        latest_entry = filtered_data['timestamp'].max().strftime('%Y-%m-%d')
        st.metric("Latest Entry", latest_entry)

# Data table with editing capabilities
st.markdown("---")
st.subheader("📋 Data Table")

if not filtered_data.empty:
    # Sort by timestamp (most recent first)
    display_data = filtered_data.sort_values('timestamp', ascending=False).copy()
    
    # Format timestamp for display
    display_data['timestamp_display'] = display_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    
    # Reorder columns for better display
    column_order = ['person_id', 'timestamp_display', 'heart_rate', 'systolic_bp', 'diastolic_bp', 'energy_level', 'notes']
    display_columns = [col for col in column_order if col in display_data.columns]
    
    # Display editable dataframe
    st.markdown(f"**Showing {len(display_data)} records**")
    
    # Add search functionality
    search_term = st.text_input("🔍 Search in data (person ID, notes):", placeholder="Enter search term...")
    
    if search_term:
        search_mask = (
            display_data['person_id'].str.contains(search_term, case=False, na=False) |
            display_data['notes'].str.contains(search_term, case=False, na=False)
        )
        display_data = display_data[search_mask]
        st.markdown(f"**Search results: {len(display_data)} records found**")
    
    # Pagination
    page_size = st.selectbox("Records per page", [10, 25, 50, 100], index=1)
    total_pages = max(1, (len(display_data) - 1) // page_size + 1)
    
    if total_pages > 1:
        page_number = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
        start_idx = (page_number - 1) * page_size
        end_idx = start_idx + page_size
        paginated_data = display_data.iloc[start_idx:end_idx]
        st.markdown(f"**Page {page_number} of {total_pages}**")
    else:
        paginated_data = display_data
    
    # Display the data table
    st.dataframe(
        paginated_data[display_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "timestamp_display": "Date & Time",
            "person_id": "Person ID",
            "heart_rate": "Heart Rate (BPM)",
            "systolic_bp": "Systolic BP",
            "diastolic_bp": "Diastolic BP",
            "energy_level": "Energy Level",
            "notes": "Notes"
        }
    )
    
else:
    st.info("No records match the current filters.")

# Data export section
st.markdown("---")
st.subheader("📥 Data Export")

col1, col2, col3 = st.columns(3)

with col1:
    if not filtered_data.empty:
        # Export filtered data
        csv_data = filtered_data.copy()
        csv_data['timestamp'] = csv_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        csv = csv_data.to_csv(index=False)
        
        filename = f"circadian_data_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        st.download_button(
            label="📊 Export Filtered Data",
            data=csv,
            file_name=filename,
            mime="text/csv",
            help="Download the currently filtered data as CSV"
        )

with col2:
    if not data.empty:
        # Export all data
        all_csv_data = data.copy()
        all_csv_data['timestamp'] = all_csv_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        all_csv = all_csv_data.to_csv(index=False)
        
        all_filename = f"circadian_data_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        st.download_button(
            label="📋 Export All Data",
            data=all_csv,
            file_name=all_filename,
            mime="text/csv",
            help="Download all data as CSV"
        )

with col3:
    # Data import section
    st.markdown("**📤 Import Data**")
    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=['csv'],
        help="Upload a CSV file with columns: person_id, timestamp, heart_rate, systolic_bp, diastolic_bp, energy_level, notes"
    )
    
    if uploaded_file is not None:
        try:
            import_data = pd.read_csv(uploaded_file)
            
            # Validate required columns
            required_columns = ['person_id', 'timestamp', 'heart_rate', 'systolic_bp', 'diastolic_bp', 'energy_level']
            missing_columns = [col for col in required_columns if col not in import_data.columns]
            
            if missing_columns:
                st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
            else:
                # Validate data types and format
                try:
                    import_data['timestamp'] = pd.to_datetime(import_data['timestamp'])
                    import_data['heart_rate'] = pd.to_numeric(import_data['heart_rate'])
                    import_data['systolic_bp'] = pd.to_numeric(import_data['systolic_bp'])
                    import_data['diastolic_bp'] = pd.to_numeric(import_data['diastolic_bp'])
                    import_data['energy_level'] = pd.to_numeric(import_data['energy_level'])
                    
                    # Add notes column if missing
                    if 'notes' not in import_data.columns:
                        import_data['notes'] = ''
                    
                    st.success(f"✅ File validated successfully! Found {len(import_data)} records.")
                    
                    # Preview data
                    st.markdown("**Preview of imported data:**")
                    st.dataframe(import_data.head(), use_container_width=True)
                    
                    if st.button("💾 Import Data", type="primary"):
                        # Import the data
                        success_count = 0
                        for _, row in import_data.iterrows():
                            entry_data = {
                                'person_id': str(row['person_id']),
                                'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                                'heart_rate': int(row['heart_rate']),
                                'systolic_bp': int(row['systolic_bp']),
                                'diastolic_bp': int(row['diastolic_bp']),
                                'energy_level': int(row['energy_level']),
                                'notes': str(row.get('notes', ''))
                            }
                            
                            if st.session_state.data_handler.add_entry(entry_data):
                                success_count += 1
                        
                        if success_count == len(import_data):
                            st.success(f"🎉 Successfully imported {success_count} records!")
                            st.rerun()
                        else:
                            st.warning(f"⚠️ Imported {success_count} out of {len(import_data)} records. Some records may have been duplicates or invalid.")
                
                except Exception as e:
                    st.error(f"❌ Data validation error: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")

# Data deletion section
st.markdown("---")
st.subheader("🗑️ Data Management Actions")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**⚠️ Danger Zone**")
    
    if st.button("🗑️ Clear All Data", type="secondary"):
        st.warning("This will permanently delete all data. This action cannot be undone!")
        
        confirm_delete = st.text_input("Type 'DELETE ALL' to confirm:", key="delete_confirm")
        
        if confirm_delete == "DELETE ALL":
            if st.button("✅ Confirm Deletion", type="primary", key="confirm_delete"):
                if st.session_state.data_handler.clear_all_data():
                    st.success("✅ All data has been deleted successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to delete data.")

with col2:
    if selected_person != 'All':
        st.markdown(f"**Delete data for {selected_person}**")
        
        person_data_count = len(data[data['person_id'] == selected_person])
        st.write(f"This will delete {person_data_count} records for {selected_person}")
        
        if st.button(f"🗑️ Delete {selected_person}'s Data", type="secondary"):
            confirm_person_delete = st.text_input(f"Type '{selected_person}' to confirm:", key="person_delete_confirm")
            
            if confirm_person_delete == selected_person:
                if st.button("✅ Confirm Person Deletion", type="primary", key="confirm_person_delete"):
                    if st.session_state.data_handler.delete_person_data(selected_person):
                        st.success(f"✅ All data for {selected_person} has been deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete person data.")

# Data insights
if not filtered_data.empty:
    st.markdown("---")
    st.subheader("📈 Quick Data Insights")
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.markdown("**Most Active Users:**")
        user_counts = filtered_data['person_id'].value_counts().head(5)
        for person, count in user_counts.items():
            st.write(f"• {person}: {count} entries")
    
    with insights_col2:
        st.markdown("**Data Quality:**")
        total_entries = len(filtered_data)
        entries_with_notes = len(filtered_data[filtered_data['notes'].str.strip() != ''])
        notes_percentage = (entries_with_notes / total_entries * 100) if total_entries > 0 else 0
        
        st.write(f"• Entries with notes: {entries_with_notes}/{total_entries} ({notes_percentage:.1f}%)")
        
        # Check for data completeness
        missing_data = filtered_data.isnull().sum()
        if missing_data.sum() > 0:
            st.write("• Missing data found:")
            for col, count in missing_data.items():
                if count > 0:
                    st.write(f"  - {col}: {count} missing values")
        else:
            st.write("• ✅ No missing data detected")
