import requests
from datetime import datetime
from Jira_utils import get_jira_issue_in_progress_time
import re
from math import ceil



GITLAB_URL = "https://gitlab.com"   
PROJECT_ID = "73314485"             
TOKEN = "ur git lab token"  
JIRA_REGEX = r"[A-Z]+-\d+"        

HEADERS = {"PRIVATE-TOKEN": TOKEN}


# def get_deployments():
#     """Fetch deployments for the project."""
#     url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/deployments"
#     res = requests.get(url, headers=HEADERS)
#     res.raise_for_status()
#     return res.json()
def get_deployments(environment="production"):
    """Fetch deployments for the project, filtered by environment."""
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/deployments"
    params = {"environment": environment}  
    res = requests.get(url, headers=HEADERS, params=params)
    res.raise_for_status()
    return res.json()

def get_deployment_details(dep_id):
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/deployments/{dep_id}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json()
    return None

def get_pipeline(pipeline_id):
    """Fetch pipeline details."""
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/pipelines/{pipeline_id}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json()
    return None

def get_pipeline_mrs(pipeline_id):
    """Fetch merge requests related to a pipeline."""
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/pipelines/{pipeline_id}/merge_requests"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json()
    return []

def get_commits(mr_iid):
    """Fetch commits for a merge request."""
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/merge_requests/{mr_iid}/commits"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json()
    return []

# Main

def main():
    deployments = get_deployments("production")
    print(deployments)
    
    for dep in deployments:
        env = dep["environment"]["name"]
        dep_id = dep["id"]
        pipeline_id = dep.get("deployable", {}).get("pipeline", {}).get("id")
        
        print(f"\n Deployment ID: {dep_id} (Environment: {env})")
        
        if not pipeline_id:
            print("   No pipeline found for this deployment")
            continue
        
        print(f"   Pipeline ID: {pipeline_id}")
        
        # 1️⃣ Try API to get merge requests
        mrs = get_pipeline_mrs(pipeline_id)
        
        # 2️⃣ Fallback: derive MR IID from pipeline ref
        if not mrs:
            pipeline = get_pipeline(pipeline_id)
            if pipeline and pipeline.get("ref", "").startswith("refs/merge-requests/"):
                mr_iid = pipeline["ref"].split("/")[2]   # string, not list
                mrs = [{"iid": mr_iid}]
        
        if not mrs:
            print("   No related Merge Request found.")
            continue
        
        for mr in mrs:
            mr_iid = mr["iid"]
            print(f"   Merge Request IID: {mr_iid}")
            
            commits = get_commits(mr_iid)
            if not commits:
                print("     No commits found for this MR")
                continue
            
            # print(f"     Commits in MR ({len(commits)}):")
            commit_dates = []
            for c in commits:
                commit_msg = c.get("title", "")
                # print(f"       - {c['short_id']} {c['title']} ({c['created_at']})")
                commit_dates.append(datetime.strptime(c["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z"))
                jira_ids = re.findall(JIRA_REGEX, commit_msg)
                if jira_ids:
                    print(f"          Jira Issues: {', '.join(jira_ids)}")
                    for jira_id in jira_ids:
                        in_progress_time_info = get_jira_issue_in_progress_time(jira_id)
                        # print(in_progress_time)
                        if in_progress_time_info:
                            in_progress_time = datetime.strptime(in_progress_time_info, "%Y-%m-%dT%H:%M:%S.%f%z")

                            # ✅ Correct usage
                            deployment_details = get_deployment_details(dep_id)
                            if deployment_details:
                                deployment_completed_str = deployment_details.get("deployable", {}).get("finished_at")
                            else:
                                deployment_completed_str = None

                            if deployment_completed_str:
                                deployment_completed = datetime.strptime(deployment_completed_str, "%Y-%m-%dT%H:%M:%S.%f%z")
                                # calculating lead time
                                delta_time = deployment_completed - in_progress_time
                                fractional_days = delta_time.total_seconds() / (24 * 3600)
                                lead_time_days = max(1, ceil(fractional_days))
                                print(f"     Lead Time (days): {lead_time_days}")
                        
                else:
                    print(" There is no jira issue found or jira issue not in progress")


if __name__ == "__main__":
    main()