import csv
from datetime import datetime

def get_latest_actions(csv_file):
    members = {}

    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            username = row['Member Username']
            action_date = datetime.strptime(row['Action Date'], '%Y-%m-%dT%H:%M:%S.%fZ')
            
            if username not in members or action_date > members[username]['Last Action Date']:
                members[username] = {
                    'Name': row['Member Name'],
                    'Last Action Date': action_date,
                    'Project': row['Project'],
                    'Username': username
                }
                
    unique_members = [{'Member Name': info['Name'], 'Last Action Date': info['Last Action Date'].strftime('%Y-%m-%dT%H:%M:%S.%fZ'), 'Project': info['Project'], 'Member Username': info['Username']} for info in members.values()]
    
    with open('unique_last_activity.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Member Name', 'Last Action Date', 'Project', 'Member Username'])
        writer.writeheader()
        writer.writerows(unique_members)

# Usage
csv_file_path = 'last_activity.csv'
get_latest_actions(csv_file_path)
