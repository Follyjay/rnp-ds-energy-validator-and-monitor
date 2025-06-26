import xml.etree.ElementTree as ET
import pandas as pd
import os

# XML namespace used for parsing DS (Day Schedule) XML files
NAMESPACE = {'ns': 'urn:iec62325.351:tc57wg16:451-2:scheduledocument:5:1'}

# Defined and ensured the existence of the directory where DS-XML files are stored
WATCH_DIR = os.path.abspath("ds_files")
os.makedirs(WATCH_DIR, exist_ok=True)
seen_files = set()

def ds_file_monitor():
    """
    Monitors the DS directory for newly added XML files.
    Prints the name of any new XML file detected.
    Note: Currently checks only once and maintains state within function scope.
    """
    global seen_files
    current_files = set(f for f in os.listdir(WATCH_DIR) if f .endswith('.xml'))

    new_files = current_files - seen_files
    if new_files:
        #for file in sorted(new_files):
            #print(f"New DS files detected: {', '.join(new_files)}")
        seen_files.update(new_files)
        result = list(new_files)
    else:
        #print("No new DS files detected.")
        result = []
        
    seen_files.update(current_files)
    return result  # Return the list of new files detected

    # Update seen files to include current state
    #seen_files.update(current_files)  
    #return list(seen_files)

def get_latest_file(directory):
    """
    Returns the full path to the most recently modified file in a given directory.
    Parameters:
        directory (str): Path to the directory to search.
    Returns:
        str or None: Full path to the latest file or None if directory is empty.
    """
    files = [f for f in os.listdir(directory)]
    if not files:
        return None
    
    # Sort files by modification time in descending order
    files.sort(key=lambda f: os.path.getmtime(os.path.join(directory, f)), reverse=True)
    return os.path.join(directory, files[0])

def get_csv_quantity_for_hour(hour_index, csv_file):
    """
    Extracts a numeric value for a specific hour from a CSV file.
    Parameters:
        hour_index (int): Index representing the hour (e.g., 0 for 00:00–01:00).
        csv_file (str): Path to the CSV file.
    Returns:
        int: Quantity value from the 4th column of the specified hour row.
    """
    df = pd.read_csv(csv_file)
    
    # Extract and clean the value from the specified cell
    raw_value = df.iloc[hour_index, 3]  # Assumes quantity is in 4th column (index 3)
    return int(float(str(raw_value).replace(',', '')))  # Convert to integer

def get_csv_direction_flow_for_hour(hour_index, csv_file):
    """
    Extracts the direct flow value for a specific hour from a CSV file.
    Parameters:
        hour_index (int): Index representing the hour (e.g., 0 for 00:00–01:00).
        csv_file (str): Path to the CSV file.
    Returns:
        string: Direction flow from the 5th column of the specified hour row.
    """
    df = pd.read_csv(csv_file)
    
    # Extract and clean the value from the specified cell
    raw_direction_flow = df.iloc[hour_index, 4]  # Assumes value is in 5th column (index 4)
    return str(raw_direction_flow)

def get_xml_quantity_for_hour(hour_index, direction_of_flow, xml_file):
    """
    Finds the correct quantity in the DS XML file for the given hour and direction.
    Looks up the value active at the start of that hour.

    Parameters:
        hour_index (int): Hour in the day (0–23).
        direction_of_flow (str): 'FRGB' or 'GBFR'.
        xml_file (str): Path to the DS XML file.

    Returns:
        int: Quantity applicable for the hour.
    """

    tree = ET.parse(xml_file)
    root = tree.getroot()
    time_series = root.findall('ns:TimeSeries', NAMESPACE)

    if direction_of_flow == "FRGB":
        series = time_series[0]  # Import from FR to GB
    elif direction_of_flow == "GBFR":
        series = time_series[1]  # Export from GB to FR
    else:
        raise ValueError("Invalid direction specified")

    period = series.find('ns:Period', NAMESPACE)
    points = period.findall('ns:Point', NAMESPACE)

    # Convert hour to seconds from midnight (00:00)
    target_seconds = (hour_index + 1) * 3600

    # Find the last known quantity before or at the target time
    quantity_value_holder = None # Holds the value of the matching quantity 
    for point in points:
        position = int(point.find('ns:position', NAMESPACE).text)
        quantity = int(point.find('ns:quantity', NAMESPACE).text)

        if position <= target_seconds:
            quantity_value_holder = quantity
        else:
            break  # Once we pass the target time, stop

    if quantity_value_holder is None:
        raise ValueError(f"No valid quantity found for hour {hour_index} at {target_seconds}s")

    return quantity_value_holder
