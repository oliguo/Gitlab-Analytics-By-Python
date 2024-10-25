import requests
import csv
import time

# Read the personal access token from the file
with open('token.txt', 'r') as file:
    ACCESS_TOKEN = file.read().strip()

GITLAB_URL = 'https://gitlab.com'  # Adjust to your GitLab instance
headers = {
    'PRIVATE-TOKEN': ACCESS_TOKEN
}

def get_groups():
    groups = []
    page = 1
    while True:
        url = f"{GITLAB_URL}/api/v4/groups?page={page}&per_page=100"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        page_groups = response.json()
        if not page_groups:
            break
        groups.extend(page_groups)
        page += 1
    return groups

def get_projects(group_id):
    projects = []
    page = 1
    while True:
        url = f"{GITLAB_URL}/api/v4/groups/{group_id}/projects?page={page}&per_page=100"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        page_projects = response.json()
        if not page_projects:
            break
        projects.extend(page_projects)
        page += 1
    return projects

def get_project_members(project_id):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/members"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_user_email(user_id):
    retries = 3
    while retries > 0:
        try:
            url = f"{GITLAB_URL}/api/v4/users/{user_id}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            time.sleep(1.5)  # Delay to avoid hitting rate limit
            return response.json().get('email', 'N/A')
        except requests.exceptions.HTTPError as err:
            if response.status_code == 429:  # Rate limit error
                time.sleep(10)  # Wait before retrying
                retries -= 1
            else:
                raise err
    return 'N/A'  # If retries are exhausted

def main():
    groups = get_groups()
    unique_groups = set()
    unique_projects = set()
    unique_members = set()

    # Open all CSV files
    with open('gitlab_data.csv', 'w', newline='') as csvfile, \
         open('gitlab_groups.csv', 'w', newline='') as groups_csv, \
         open('gitlab_projects.csv', 'w', newline='') as projects_csv, \
         open('gitlab_members.csv', 'w', newline='') as members_csv:

        # Set up CSV writers
        fieldnames = ['Group', 'Group Link', 'Project', 'Project Link', 'Member Name', 'Member Username', 'Member Email', 'Member Link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        groups_writer = csv.DictWriter(groups_csv, fieldnames=['Group ID', 'Group Name', 'Group Link'])
        groups_writer.writeheader()

        projects_writer = csv.DictWriter(projects_csv, fieldnames=['Project ID', 'Project Name', 'Project Link'])
        projects_writer.writeheader()

        members_writer = csv.DictWriter(members_csv, fieldnames=['Member ID', 'Member Name', 'Member Username', 'Member Email', 'Member Link'])
        members_writer.writeheader()

        for group in groups:
            group_id = group['id']
            if group_id not in unique_groups:
                unique_groups.add(group_id)
                groups_writer.writerow({
                    'Group ID': group_id,
                    'Group Name': group['name'],
                    'Group Link': f"{GITLAB_URL}/groups/{group_id}"
                })

            projects = get_projects(group_id)
            for project in projects:
                project_id = project['id']
                if project_id not in unique_projects:
                    unique_projects.add(project_id)
                    projects_writer.writerow({
                        'Project ID': project_id,
                        'Project Name': project['name'],
                        'Project Link': f"{GITLAB_URL}/{project['path_with_namespace']}"
                    })

                members = get_project_members(project_id)
                for member in members:
                    member_id = member['id']
                    email = get_user_email(member_id)
                    
                    writer.writerow({
                        'Group': group['name'],
                        'Group Link': f"{GITLAB_URL}/groups/{group_id}",
                        'Project': project['name'],
                        'Project Link': f"{GITLAB_URL}/{project['path_with_namespace']}",
                        'Member Name': member['name'],
                        'Member Username': member['username'],
                        'Member Email': email,
                        'Member Link': f"{GITLAB_URL}/{member['username']}"
                    })

                    if member_id not in unique_members:
                        unique_members.add(member_id)
                        members_writer.writerow({
                            'Member ID': member_id,
                            'Member Name': member['name'],
                            'Member Username': member['username'],
                            'Member Email': email,
                            'Member Link': f"{GITLAB_URL}/{member['username']}"
                        })

    total_groups = len(unique_groups)
    total_projects = len(unique_projects)
    total_members = len(unique_members)

    with open('summary.txt', 'w') as summary_file:
        summary_file.write(f"Total Unique Groups: {total_groups}\n")
        summary_file.write(f"Total Unique Projects: {total_projects}\n")
        summary_file.write(f"Total Unique Members: {total_members}\n")

if __name__ == "__main__":
    main()