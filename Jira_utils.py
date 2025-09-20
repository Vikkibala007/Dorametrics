import requests

# Jira configuration
JIRA_URL = "https://balamurugan969820.atlassian.net"  # Jira base URL
JIRA_EMAIL = "balamurugan969820@gmail.com"           # Jira email
JIRA_API_TOKEN = "ATATT3xFfGF0YTs8CfU3BxsOK50po4fbpBsLwF2yq9NuFF4CceCaosor2agFbZSUhKmacLA6TzmuoTgOnrqd-LJYxv3JbOPn4RoyDedVFtDvlXfLU_TwQF_0cpXLhs8PX7vz84-8y4KXezfyac6lWPue0_bJGLdEAC38E8TwGQ7gZVp1XVxwogg=7F1ABC98"              # Jira API token

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