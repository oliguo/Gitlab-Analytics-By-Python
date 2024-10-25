# Gitlab-Analytics-By-Python
  With AI help to generate the requirement to analytics activities, projects, groups and member.

# Init the enviroment
```
python3 -m venv myenv
source myenv/bin/activate
```

# Update token in token.txt
Ensure that you have the owner or maintainer permissions of your groups and projects.

token.txt
```
xxxxxxx
```

# CSVs
Note: Member Email maybe not able to fetch if member doesn't public it.

gitlab_data.csv 
```
Group,Group Link,Project,Project Link,Member Name,Member Username,Member Email,Member Link
```
gitlab_groups.csv
```
Group ID,Group Name,Group Link
```
gitlab_projects.csv
```
Project ID,Project Name,Project Link
```
gitlab_members.csv
```
Member ID,Member Name,Member Username,Member Email,Member Link
```
last_activity.csv
```
Project,Project Link,Member Name,Member Username,Action,Action Message,Action Date
```
unique_last_activity.csv(read from last_activity.csv)
```
Member Name,Last Action Date,Project,Member Username
```
