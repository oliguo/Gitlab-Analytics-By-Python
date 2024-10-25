import requests
import csv
import logging

# Log to file
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Read the personal access token from the file
with open('token.txt', 'r') as file:
    ACCESS_TOKEN = file.read().strip()

GITLAB_URL = 'https://gitlab.com'  # Adjust to your GitLab instance
headers = {
    'PRIVATE-TOKEN': ACCESS_TOKEN
}

def make_request_with_retries(url, retries=5):
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers)
            logging.info(f"URL: {url}")
            response.raise_for_status()
            logging.info(f"Response JSON: {response.json()}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed (attempt {i + 1}/{retries}): {e}")
            if i < retries - 1:
                logging.info("Retrying...")
            else:
                logging.critical("Failed to get a successful response after multiple retries.")
                raise

def get_groups():
    groups = []
    page = 1
    while True:
        url = f"{GITLAB_URL}/api/v4/groups?page={page}&per_page=100"
        page_groups = make_request_with_retries(url)
        if not page_groups:
            break
        groups.extend(page_groups)
        page += 1
    return groups

def get_projects_from_group(group_id):
    projects = []
    page = 1
    while True:
        url = f"{GITLAB_URL}/api/v4/groups/{group_id}/projects?page={page}&per_page=100"
        page_projects = make_request_with_retries(url)
        if not page_projects:
            break
        projects.extend(page_projects)
        page += 1
    return projects

def get_last_activity(project_id):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/events?per_page=1"
    events = make_request_with_retries(url)
    if events:
        return events[0]
    return None

def main():
    groups = get_groups()
    projects = []
    for group in groups:
        group_projects = get_projects_from_group(group['id'])
        projects.extend(group_projects)
    
    with open('last_activity.csv', 'w', newline='') as csvfile:
        fieldnames = ['Project', 'Project Link', 'Member Name', 'Member Username', 'Action', 'Action Message', 'Action Date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for project in projects:
            last_activity = get_last_activity(project['id'])
            if last_activity:
                action_date = last_activity['created_at']
                action_message = last_activity.get('push_data', {}).get('commit_title', last_activity['action_name'])
                member_name = last_activity['author']['name']
                member_username = last_activity['author']['username']
                
                writer.writerow({
                    'Project': project['name'],
                    'Project Link': project['web_url'],
                    'Member Name': member_name,
                    'Member Username': member_username,
                    'Action': last_activity['action_name'],
                    'Action Message': action_message,
                    'Action Date': action_date
                })

if __name__ == "__main__":
    main()
