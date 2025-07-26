import re
from datetime import datetime, time
import logging

def validate_person_id(person_id):
    """Validate person ID format and content"""
    if not person_id or not isinstance(person_id, str):
        return {'valid': False, 'message': 'Person ID is required and must be a string'}
    
    person_id = person_id.strip()
    
    if len(person_id) < 2:
        return {'valid': False, 'message': 'Person ID must be at least 2 characters long'}
    
    if len(person_id) > 50:
        return {'valid': False, 'message': 'Person ID must be 50 characters or less'}
    
    # Check for valid characters (letters, numbers, underscore, hyphen)
    if not re.match(r'^[a-zA-Z0-9_-]+$', person_id):
        return {'valid': False, 'message': 'Person ID can only contain letters, numbers, underscores, and hyphens'}
    
    return {'valid': True, 'message': 'Valid person ID'}

def validate_heart_rate(heart_rate):
    """Validate heart rate value"""
    if not isinstance(heart_rate, (int, float)):
        return {'valid': False, 'message': 'Heart rate must be a number'}
    
    if heart_rate < 30:
        return {'valid': False, 'message': 'Heart rate too low (minimum 30 BPM)'}
    
    if heart_rate > 200:
        return {'valid': False, 'message': 'Heart rate too high (maximum 200 BPM)'}
    
    return {'valid': True, 'message': 'Valid heart rate'}

def validate_blood_pressure(systolic, diastolic):
    """Validate blood pressure values"""
    if not isinstance(systolic, (int, float)) or not isinstance(diastolic, (int, float)):
        return {'valid': False, 'message': 'Blood pressure values must be numbers'}
    
    if systolic < 70:
        return {'valid': False, 'message': 'Systolic pressure too low (minimum 70 mmHg)'}
    
    if systolic > 250:
        return {'valid': False, 'message': 'Systolic pressure too high (maximum 250 mmHg)'}
    
    if diastolic < 40:
        return {'valid': False, 'message': 'Diastolic pressure too low (minimum 40 mmHg)'}
    
    if diastolic > 150:
        return {'valid': False, 'message': 'Diastolic pressure too high (maximum 150 mmHg)'}
    
    if diastolic >= systolic:
        return {'valid': False, 'message': 'Diastolic pressure must be lower than systolic pressure'}
    
    # Check for reasonable blood pressure ranges
    if systolic < 90 and diastolic < 60:
        return {'valid': True, 'message': 'Valid blood pressure (low normal)', 'warning': 'Blood pressure is in the low range'}
    
    if systolic >= 140 or diastolic >= 90:
        return {'valid': True, 'message': 'Valid blood pressure (high)', 'warning': 'Blood pressure is in the high range'}
    
    return {'valid': True, 'message': 'Valid blood pressure'}

def validate_energy_level(energy_level):
    """Validate energy level value"""
    if not isinstance(energy_level, (int, float)):
        return {'valid': False, 'message': 'Energy level must be a number'}
    
    if energy_level < 1:
        return {'valid': False, 'message': 'Energy level must be at least 1'}
    
    if energy_level > 10:
        return {'valid': False, 'message': 'Energy level must be at most 10'}
    
    return {'valid': True, 'message': 'Valid energy level'}

def validate_timestamp(timestamp):
    """Validate timestamp format and value"""
    if isinstance(timestamp, str):
        try:
            # Try to parse the timestamp string
            parsed_timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                # Try alternative format
                parsed_timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M')
            except ValueError:
                return {'valid': False, 'message': 'Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS or YYYY-MM-DD HH:MM'}
    elif isinstance(timestamp, datetime):
        parsed_timestamp = timestamp
    else:
        return {'valid': False, 'message': 'Timestamp must be a string or datetime object'}
    
    # Check if timestamp is not in the future
    now = datetime.now()
    if parsed_timestamp > now:
        return {'valid': False, 'message': 'Timestamp cannot be in the future'}
    
    # Check if timestamp is not too old (more than 10 years)
    ten_years_ago = datetime(now.year - 10, now.month, now.day)
    if parsed_timestamp < ten_years_ago:
        return {'valid': False, 'message': 'Timestamp cannot be more than 10 years ago'}
    
    return {'valid': True, 'message': 'Valid timestamp', 'parsed_timestamp': parsed_timestamp}

def validate_notes(notes):
    """Validate notes field"""
    if notes is None:
        return {'valid': True, 'message': 'Valid notes (empty)'}
    
    if not isinstance(notes, str):
        return {'valid': False, 'message': 'Notes must be a string'}
    
    if len(notes) > 500:
        return {'valid': False, 'message': 'Notes must be 500 characters or less'}
    
    return {'valid': True, 'message': 'Valid notes'}

def validate_health_metrics(heart_rate, systolic_bp, diastolic_bp, energy_level):
    """Comprehensive validation of all health metrics"""
    validations = []
    
    # Validate heart rate
    hr_validation = validate_heart_rate(heart_rate)
    if not hr_validation['valid']:
        return hr_validation
    
    # Validate blood pressure
    bp_validation = validate_blood_pressure(systolic_bp, diastolic_bp)
    if not bp_validation['valid']:
        return bp_validation
    
    # Validate energy level
    energy_validation = validate_energy_level(energy_level)
    if not energy_validation['valid']:
        return energy_validation
    
    # Collect warnings
    warnings = []
    if 'warning' in bp_validation:
        warnings.append(bp_validation['warning'])
    
    # Additional cross-validation checks
    # High energy with low heart rate might be unusual
    if energy_level >= 8 and heart_rate < 60:
        warnings.append('High energy level with low heart rate - please verify readings')
    
    # Low energy with high heart rate might indicate stress or illness
    if energy_level <= 3 and heart_rate > 100:
        warnings.append('Low energy with high heart rate - consider medical consultation')
    
    result = {'valid': True, 'message': 'All health metrics are valid'}
    if warnings:
        result['warnings'] = warnings
    
    return result

def validate_entry_data(entry_data):
    """Validate a complete entry data dictionary"""
    required_fields = ['person_id', 'timestamp', 'heart_rate', 'systolic_bp', 'diastolic_bp', 'energy_level']
    
    # Check for required fields
    for field in required_fields:
        if field not in entry_data:
            return {'valid': False, 'message': f'Missing required field: {field}'}
    
    # Validate person ID
    person_validation = validate_person_id(entry_data['person_id'])
    if not person_validation['valid']:
        return person_validation
    
    # Validate timestamp
    timestamp_validation = validate_timestamp(entry_data['timestamp'])
    if not timestamp_validation['valid']:
        return timestamp_validation
    
    # Validate health metrics
    metrics_validation = validate_health_metrics(
        entry_data['heart_rate'],
        entry_data['systolic_bp'],
        entry_data['diastolic_bp'],
        entry_data['energy_level']
    )
    if not metrics_validation['valid']:
        return metrics_validation
    
    # Validate notes if present
    if 'notes' in entry_data:
        notes_validation = validate_notes(entry_data['notes'])
        if not notes_validation['valid']:
            return notes_validation
    
    result = {'valid': True, 'message': 'Entry data is valid'}
    
    # Include any warnings from health metrics validation
    if 'warnings' in metrics_validation:
        result['warnings'] = metrics_validation['warnings']
    
    return result

def sanitize_input(input_string):
    """Sanitize string input to prevent potential issues"""
    if not isinstance(input_string, str):
        return str(input_string)
    
    # Remove leading/trailing whitespace
    sanitized = input_string.strip()
    
    # Remove any null bytes
    sanitized = sanitized.replace('\x00', '')
    
    # Limit length to prevent extremely long inputs
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000]
        logging.warning("Input string truncated due to excessive length")
    
    return sanitized

def validate_csv_data(df):
    """Validate a pandas DataFrame for CSV import"""
    required_columns = ['person_id', 'timestamp', 'heart_rate', 'systolic_bp', 'diastolic_bp', 'energy_level']
    
    # Check for required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return {'valid': False, 'message': f'Missing required columns: {missing_columns}'}
    
    # Check for empty DataFrame
    if df.empty:
        return {'valid': False, 'message': 'No data found in CSV'}
    
    validation_errors = []
    validation_warnings = []
    
    # Validate each row
    for index, row in df.iterrows():
        try:
            # Create entry data for validation
            entry_data = {
                'person_id': row['person_id'],
                'timestamp': row['timestamp'],
                'heart_rate': row['heart_rate'],
                'systolic_bp': row['systolic_bp'],
                'diastolic_bp': row['diastolic_bp'],
                'energy_level': row['energy_level'],
                'notes': row.get('notes', '')
            }
            
            # Validate the entry
            validation_result = validate_entry_data(entry_data)
            
            if not validation_result['valid']:
                validation_errors.append(f"Row {index + 1}: {validation_result['message']}")
            elif 'warnings' in validation_result:
                validation_warnings.extend([f"Row {index + 1}: {warning}" for warning in validation_result['warnings']])
                
        except Exception as e:
            validation_errors.append(f"Row {index + 1}: Error validating data - {str(e)}")
    
    if validation_errors:
        return {
            'valid': False, 
            'message': f'Validation failed with {len(validation_errors)} errors',
            'errors': validation_errors[:10],  # Limit to first 10 errors
            'total_errors': len(validation_errors)
        }
    
    result = {'valid': True, 'message': f'CSV data is valid ({len(df)} rows)'}
    
    if validation_warnings:
        result['warnings'] = validation_warnings[:20]  # Limit to first 20 warnings
        result['total_warnings'] = len(validation_warnings)
    
    return result
