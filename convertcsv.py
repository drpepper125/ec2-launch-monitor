import csv
import json
import logging
from typing import Dict, List, Any


def load_json_file(file_path: str) -> List[Dict[str, Any]]:
    """Load JSON data from a file and extract instance data."""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Extract instance data from the nested structure
        if 'tagged_instances' in data:
            # Convert the tagged_instances dict to a list of instance records
            instances_list = []
            for instance_id, instance_details in data['tagged_instances'].items():
                # Flatten security_groups and tags for CSV
                instance_record = instance_details.copy()
                instance_record['security_groups'] = ', '.join(instance_details.get('security_groups', []))
                
                # Flatten tags into separate columns
                tags = instance_details.get('tags', {})
                for tag_key, tag_value in tags.items():
                    instance_record[f'tag_{tag_key}'] = tag_value
                
                # Remove the original nested tags dict
                instance_record.pop('tags', None)
                
                instances_list.append(instance_record)
            
            return instances_list
        else:
            logging.warning("No 'tagged_instances' found in JSON data")
            return []
            
    except Exception as e:
        logging.error(f"Error loading JSON file {file_path}: {e}")
        return []

def convert_json_to_csv(json_data: List[Dict[str, Any]], csv_file_path: str) -> None:
    """Convert JSON data to CSV format and save to a file."""
    if not json_data:
        logging.warning("No data to convert to CSV.")
        return
    
    try:
        # Collect all possible fieldnames from all records
        all_fieldnames = set()
        for row in json_data:
            all_fieldnames.update(row.keys())
        
        fieldnames = sorted(list(all_fieldnames))  # Sort for consistent column order
        
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in json_data:
                writer.writerow(row)
        logging.info(f"Successfully converted JSON to CSV: {csv_file_path}")
    except Exception as e:
        logging.error(f"Error converting JSON to CSV: {e}") 

def main():
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    json_file_path = 'multiple_instances_response.json'
    csv_file_path = 'instances.csv'
    
    json_data = load_json_file(json_file_path)
    convert_json_to_csv(json_data, csv_file_path)

if __name__ == "__main__":
    main()
# This code provides a simple utility to convert JSON data to CSV format.
# It includes functions to load JSON data from a file and convert it to CSV,
# handling errors and logging appropriately.