import pandas as pd
import os
from datetime import datetime
import logging

class DataHandler:
    """Handle CSV data operations for circadian rhythm tracking"""
    
    def __init__(self, csv_file='circadian_data.csv'):
        self.csv_file = csv_file
        self.columns = [
            'person_id', 'timestamp', 'heart_rate', 'systolic_bp', 
            'diastolic_bp', 'energy_level', 'notes'
        ]
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            df = pd.DataFrame(columns=self.columns)
            df.to_csv(self.csv_file, index=False)
            logging.info(f"Created new CSV file: {self.csv_file}")
    
    def load_data(self):
        """Load data from CSV file"""
        try:
            if os.path.exists(self.csv_file) and os.path.getsize(self.csv_file) > 0:
                df = pd.read_csv(self.csv_file)
                # Ensure all required columns exist
                for col in self.columns:
                    if col not in df.columns:
                        df[col] = '' if col == 'notes' else 0
                return df
            else:
                return pd.DataFrame(columns=self.columns)
        except Exception as e:
            logging.error(f"Error loading data: {str(e)}")
            return pd.DataFrame(columns=self.columns)
    
    def add_entry(self, entry_data):
        """Add a new entry to the CSV file"""
        try:
            # Load existing data
            df = self.load_data()
            
            # Create new entry dataframe
            new_entry = pd.DataFrame([entry_data])
            
            # Check for duplicates (same person, timestamp)
            if not df.empty:
                duplicate_mask = (
                    (df['person_id'] == entry_data['person_id']) &
                    (df['timestamp'] == entry_data['timestamp'])
                )
                if duplicate_mask.any():
                    logging.warning(f"Duplicate entry detected for {entry_data['person_id']} at {entry_data['timestamp']}")
                    return False
            
            # Append new entry
            df = pd.concat([df, new_entry], ignore_index=True)
            
            # Save to CSV
            df.to_csv(self.csv_file, index=False)
            logging.info(f"Added new entry for {entry_data['person_id']}")
            return True
            
        except Exception as e:
            logging.error(f"Error adding entry: {str(e)}")
            return False
    
    def update_entry(self, index, updated_data):
        """Update an existing entry by index"""
        try:
            df = self.load_data()
            
            if index < 0 or index >= len(df):
                logging.error(f"Invalid index: {index}")
                return False
            
            # Update the entry
            for key, value in updated_data.items():
                if key in df.columns:
                    df.loc[index, key] = value
            
            # Save to CSV
            df.to_csv(self.csv_file, index=False)
            logging.info(f"Updated entry at index {index}")
            return True
            
        except Exception as e:
            logging.error(f"Error updating entry: {str(e)}")
            return False
    
    def delete_entry(self, index):
        """Delete an entry by index"""
        try:
            df = self.load_data()
            
            if index < 0 or index >= len(df):
                logging.error(f"Invalid index: {index}")
                return False
            
            # Remove the entry
            df = df.drop(index=index).reset_index(drop=True)
            
            # Save to CSV
            df.to_csv(self.csv_file, index=False)
            logging.info(f"Deleted entry at index {index}")
            return True
            
        except Exception as e:
            logging.error(f"Error deleting entry: {str(e)}")
            return False
    
    def delete_person_data(self, person_id):
        """Delete all data for a specific person"""
        try:
            df = self.load_data()
            
            # Filter out the person's data
            df = df[df['person_id'] != person_id]
            
            # Save to CSV
            df.to_csv(self.csv_file, index=False)
            logging.info(f"Deleted all data for person: {person_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error deleting person data: {str(e)}")
            return False
    
    def clear_all_data(self):
        """Clear all data from the CSV file"""
        try:
            df = pd.DataFrame(columns=self.columns)
            df.to_csv(self.csv_file, index=False)
            logging.info("Cleared all data")
            return True
            
        except Exception as e:
            logging.error(f"Error clearing data: {str(e)}")
            return False
    
    def get_person_data(self, person_id, start_date=None, end_date=None):
        """Get data for a specific person with optional date filtering"""
        try:
            df = self.load_data()
            
            if df.empty:
                return pd.DataFrame(columns=self.columns)
            
            # Filter by person
            person_data = df[df['person_id'] == person_id].copy()
            
            if person_data.empty:
                return pd.DataFrame(columns=self.columns)
            
            # Apply date filtering if provided
            if start_date or end_date:
                person_data['timestamp'] = pd.to_datetime(person_data['timestamp'])
                
                if start_date:
                    person_data = person_data[person_data['timestamp'].dt.date >= start_date]
                
                if end_date:
                    person_data = person_data[person_data['timestamp'].dt.date <= end_date]
            
            return person_data.sort_values('timestamp')
            
        except Exception as e:
            logging.error(f"Error getting person data: {str(e)}")
            return pd.DataFrame(columns=self.columns)
    
    def get_summary_stats(self, person_id=None):
        """Get summary statistics for all data or specific person"""
        try:
            df = self.load_data()
            
            if df.empty:
                return {}
            
            if person_id:
                df = df[df['person_id'] == person_id]
                
            if df.empty:
                return {}
            
            stats = {
                'total_entries': len(df),
                'date_range': {
                    'start': pd.to_datetime(df['timestamp']).min(),
                    'end': pd.to_datetime(df['timestamp']).max()
                },
                'heart_rate': {
                    'mean': df['heart_rate'].mean(),
                    'std': df['heart_rate'].std(),
                    'min': df['heart_rate'].min(),
                    'max': df['heart_rate'].max()
                },
                'blood_pressure': {
                    'systolic_mean': df['systolic_bp'].mean(),
                    'diastolic_mean': df['diastolic_bp'].mean(),
                    'systolic_std': df['systolic_bp'].std(),
                    'diastolic_std': df['diastolic_bp'].std()
                },
                'energy_level': {
                    'mean': df['energy_level'].mean(),
                    'std': df['energy_level'].std(),
                    'min': df['energy_level'].min(),
                    'max': df['energy_level'].max()
                },
                'unique_people': df['person_id'].nunique() if not person_id else 1
            }
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting summary stats: {str(e)}")
            return {}
    
    def export_data(self, person_id=None, start_date=None, end_date=None):
        """Export data as CSV string with optional filtering"""
        try:
            if person_id:
                df = self.get_person_data(person_id, start_date, end_date)
            else:
                df = self.load_data()
                
                if start_date or end_date:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    
                    if start_date:
                        df = df[df['timestamp'].dt.date >= start_date]
                    
                    if end_date:
                        df = df[df['timestamp'].dt.date <= end_date]
            
            return df.to_csv(index=False)
            
        except Exception as e:
            logging.error(f"Error exporting data: {str(e)}")
            return ""
    
    def backup_data(self, backup_filename=None):
        """Create a backup of the current data"""
        try:
            if not backup_filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_filename = f"circadian_data_backup_{timestamp}.csv"
            
            df = self.load_data()
            df.to_csv(backup_filename, index=False)
            logging.info(f"Data backed up to: {backup_filename}")
            return backup_filename
            
        except Exception as e:
            logging.error(f"Error backing up data: {str(e)}")
            return None
