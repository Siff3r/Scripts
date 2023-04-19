import re
import csv
import argparse
import os

def parse_cdp_neighbors(data):
    neighbors = []

    device_id_pattern = re.compile(r'Device ID:(.+)')
    ip_address_pattern = re.compile(r'IPv4 Address: (.+)|IP address: (.+)')
    platform_pattern = re.compile(r'Platform: (.+),\s*Capabilities: (.+)')
    interface_pattern = re.compile(r'Interface: (.+),\s*Port ID \(outgoing port\): (.+)|Interface: (.+),\s*Port ID \(outgoing port\): (.+)')
    
    lines = data.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1

        if device_id_pattern.match(line):
            neighbor = {}
            neighbor['device_id'] = device_id_pattern.match(line).group(1).strip()

            while i < len(lines):
                line = lines[i].strip()
                i += 1

                if ip_address_pattern.match(line):
                    match = ip_address_pattern.match(line)
                    neighbor['ip_address'] = match.group(1).strip() if match.group(1) else match.group(2).strip()
                elif platform_pattern.match(line):
                    neighbor['platform'], neighbor['capabilities'] = platform_pattern.match(line).group(1, 2)
                elif interface_pattern.match(line):
                    match = interface_pattern.match(line)
                    neighbor['interface'] = match.group(1).strip() if match.group(1) else match.group(3).strip()
                    neighbor['port_id'] = match.group(2).strip() if match.group(2) else match.group(4).strip()
                elif '---' in line:
                    neighbors.append(neighbor)
                    break

    return neighbors

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Parse CDP neighbor information from a text file and write to a CSV file.')
parser.add_argument('-i', '--input', help='Input text file containing CDP neighbor information', required=True)
#parser.add_argument('-o', '--output', help='Output CSV file to store parsed CDP neighbor information', required=True)
args = parser.parse_args()

# Read CDP neighbor information from the specified input file
with open(args.input, 'r') as file:
    cdp_neighbor_data = file.read()

parsed_neighbors = parse_cdp_neighbors(cdp_neighbor_data)

csv_output = os.path.splitext(args.input)[0] + '.csv'

# Write the parsed information to the specified output CSV file
with open(csv_output, 'w', newline='') as csvfile:
    fieldnames = ['device_id', 'ip_address', 'platform', 'capabilities', 'interface', 'port_id']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for neighbor in parsed_neighbors:
        writer.writerow(neighbor)

