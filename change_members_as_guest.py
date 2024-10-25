import requests
import logging
import csv

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

usernames_to_change = [
    "xxx"
]  # Replace with the usernames you want to change to guest

def make_request_with_retries(url, retries=5):
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers)
            logging.info(f"URL: {url}")
            response.raise_for_status()
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

def get_members_of_project(project_id):
    members = []
    page = 1
    while True:
        url = f"{GITLAB_URL}/api/v4/projects/{project_id}/members?page={page}&per_page=100"
        page_members = make_request_with_retries(url)
        if not page_members:
            break
        members.extend(page_members)
        page += 1
    return members

def change_member_role_to_guest(project_id, user_id, member_name, username, group_name, group_link, project_name, project_link, failed_members):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/members/{user_id}"
    data = {
        'access_level': 10  # 10 is the access level for Guest
    }
    response = requests.put(url, headers=headers, json=data)
    logging.info(f"URL: {url}")
    logging.info(f"Payload: {data}")
    logging.info(f"Response Status Code: {response.status_code}")
    logging.info(f"Response Text: {response.text}")
    if response.status_code != 200:
        failed_members.append({
            'Member Name': member_name,
            'Username': username,
            'Group Name': group_name,
            'Group Link': group_link,
            'Project Name': project_name,
            'Project Link': project_link
        })
    else:
        logging.info(f"Changed role to Guest for user ID {user_id} in project ID {project_id}")

def main():
    groups = get_groups()
    failed_members = []
    for group in groups:
        group_projects = get_projects_from_group(group['id'])
        for project in group_projects:
            project_members = get_members_of_project(project['id'])
            for member in project_members:
                if 'access_level' in member and member['access_level'] == 10:  # Checking access_level for Guest
                    continue
                if member['username'] in usernames_to_change:
                    change_member_role_to_guest(
                        project['id'], member['id'], member['name'], member['username'],
                        group['name'], group['web_url'], project['name'], project['web_url'], failed_members
                    )

    with open('failed_guest.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Member Name', 'Username', 'Group Name', 'Group Link', 'Project Name', 'Project Link'])
        writer.writeheader()
        writer.writerows(failed_members)

if __name__ == "__main__":
    main()
