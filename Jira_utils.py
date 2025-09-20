import requests

# Jira configuration
JIRA_URL = ""  # Jira base URL
JIRA_EMAIL = ""           # Jira email
JIRA_API_TOKEN = ""              # Jira API token

JIRA_HEADERS = {
    "Accept": "application/json"
}

def get_jira_issue_in_progress_time(issue_key):
    """
    Fetch the timestamp when a Jira issue moved to 'In Progress'.
    Returns ISO timestamp string or None if not found.
    """
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}?expand=changelog"
    
    res = requests.get(url, headers=JIRA_HEADERS, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
    # print(f"Status code: {res.status_code}")
    
    if res.status_code != 200:
        print(f" Could not fetch Jira issue {issue_key} (status {res.status_code})")
        return None
    
    data = res.json()
    # print(data)
    changelog = data.get("changelog", {}).get("histories", [])
    # print(changelog)
    
    for history in changelog:
        for item in history.get("items", []):
            # print(f" Item :{item}")
            if item.get("field") == "status" and item.get("toString") == "In Progress":
                return history.get("created")  # Timestamp when status changed
    
    return None

# jira_detials = get_jira_issue_in_progress_time()
# print(jira_detials)