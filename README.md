# Circadian Rhythm Tracker

A Streamlit web application for tracking and visualizing circadian rhythm patterns through health metrics including heart rate, blood pressure, and energy levels.

## Features

- **Data Entry**: Record daily health metrics with validation
- **Visualization**: Interactive charts showing circadian patterns over time
- **Data Management**: View, filter, edit, and export your data
- **CSV Storage**: Simple file-based storage system
- **Multi-user Support**: Track data for multiple people

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Local Setup

1. **Download the project files**
   - Download all files from this project to your local machine
   - Maintain the same folder structure:
   ```
   circadian-rhythm-tracker/
   ├── .streamlit/
   │   └── config.toml
   ├── pages/
   │   ├── 1_Data_Entry.py
   │   ├── 2_Visualization.py
   │   └── 3_Data_Management.py
   ├── utils/
   │   ├── data_handler.py
   │   └── validators.py
   ├── app.py
   ├── requirements.txt
   └── README.md
   ```

2. **Install dependencies**
   ```bash
   cd circadian-rhythm-tracker
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the application**
   - Open your web browser
   - Navigate to `http://localhost:8501`
   - The application will automatically open in your default browser

## Usage

### Data Entry
1. Navigate to the "Data Entry" page
2. Fill in your Person ID (use a consistent identifier)
3. Enter the date and time of measurement
4. Record your health metrics:
   - Heart Rate (30-200 BPM)
   - Blood Pressure (Systolic/Diastolic in mmHg)
   - Energy Level (1-10 scale)
5. Add optional notes
6. Click "Save Entry"

### Visualization
- View time series charts of your health metrics
- Analyze circadian patterns by hour of day
- See correlation analysis between different metrics
- Export filtered data as CSV

### Data Management
- View all recorded data in a table
- Filter by person, date range, and metric values
- Search through your data
- Export data to CSV
- Import data from CSV files
- Delete specific person data or clear all data

## Data Schema

The application stores data in CSV format with the following columns:
- `person_id`: Unique identifier for the person
- `timestamp`: Date and time of measurement (YYYY-MM-DD HH:MM:SS)
- `heart_rate`: Heart rate in beats per minute
- `systolic_bp`: Systolic blood pressure in mmHg
- `diastolic_bp`: Diastolic blood pressure in mmHg
- `energy_level`: Energy level on a scale of 1-10
- `notes`: Optional text notes

## Tips for Accurate Tracking

- Take measurements at consistent times each day
- Record data in similar conditions (e.g., before coffee, after waking)
- Include contextual notes that might affect your metrics
- Track regularly to identify patterns in your circadian rhythm

## Data Storage

- Data is stored locally in `circadian_data.csv`
- Backup your data file regularly
- The application creates the CSV file automatically on first use

## Troubleshooting

### Common Issues

1. **Port already in use**: If port 8501 is busy, Streamlit will automatically use the next available port
2. **Permission errors**: Ensure you have write permissions in the application directory
3. **Module not found**: Make sure all dependencies are installed with `pip install -r requirements.txt`

### Data Issues

1. **Invalid entries**: The application validates all input data and will show error messages for invalid entries
2. **Duplicate entries**: The system prevents duplicate entries for the same person at the same timestamp
3. **CSV corruption**: If the CSV file becomes corrupted, delete it and the application will create a new one

## Support

For issues or questions:
1. Check the validation messages in the application
2. Ensure your data follows the required format
3. Verify all dependencies are properly installed

## License

This project is open source and available for personal use.
