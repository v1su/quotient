import os
import requests
from datetime import datetime, timedelta

# Get the environment variables
GH_TOKEN = os.getenv("GH_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")
QUOTES_FILE = "quotes.json"
BRANCH_NAME = "update-quotes"

# Function to get the name of the day for a given date
def get_day_name(date):
    return date.strftime("%A")

# Function to calculate the start of the current week (Sunday) and the current day
def get_week_dates():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday() + 1)  # Sunday of the current week
    end_of_week = start_of_week + timedelta(days=6)  # Saturday of the current week

    return start_of_week, today

# Function to make a safe API request
def make_request(url, method="GET", headers=None, data=None):
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        
        # Check if the response was successful
        response.raise_for_status()
        
        # Attempt to parse the response as JSON
        try:
            return response.json()
        except ValueError:
            print(f"Error: Invalid JSON response from {url}")
            return None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return None

# Function to create a pull request and assign a reviewer
def create_pull_request_with_reviewer():
    headers = {
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get the start and current day of the week
    start_of_week, current_day = get_week_dates()

    # Format the dates as strings
    start_of_week_str = start_of_week.strftime("%Y-%m-%d")
    current_day_str = current_day.strftime("%Y-%m-%d")

    # Get the day names
    start_of_week_day_name = get_day_name(start_of_week)
    current_day_name = get_day_name(current_day)

    # Create a new branch
    branch_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/refs"
    main_ref = make_request(f"{branch_url}/heads/main", headers=headers)

    if not main_ref or "object" not in main_ref:
        print("Error: Failed to get SHA of the main branch.")
        return

    sha = main_ref["object"]["sha"]

    branch_payload = {"ref": f"refs/heads/{BRANCH_NAME}", "sha": sha}
    branch_response = make_request(branch_url, method="POST", headers=headers, data=branch_payload)
    if not branch_response:
        print("Error: Failed to create the new branch.")
        return

    # Commit the changes
    with open(QUOTES_FILE, "r") as file:
        quotes_content = file.read()

    blob_response = make_request(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/blobs",
        method="POST",
        headers=headers,
        data={"content": quotes_content, "encoding": "utf-8"}
    )
    
    if not blob_response:
        print("Error: Failed to create a new blob.")
        return

    tree_response = make_request(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/trees",
        method="POST",
        headers=headers,
        data={
            "base_tree": sha,
            "tree": [{"path": QUOTES_FILE, "mode": "100644", "type": "blob", "sha": blob_response["sha"]}]
        }
    )

    if not tree_response:
        print("Error: Failed to create tree.")
        return

    commit_response = make_request(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/commits",
        method="POST",
        headers=headers,
        data={
            "message": f"Update quotes.json for {start_of_week_day_name} ({start_of_week_str}) to {current_day_name} ({current_day_str})",
            "tree": tree_response["sha"],
            "parents": [sha]
        }
    )

    if not commit_response:
        print("Error: Failed to create commit.")
        return

    commit_sha = commit_response["sha"]
    patch_response = make_request(
        f"{branch_url}/heads/{BRANCH_NAME}",
        method="PATCH",
        headers=headers,
        data={"sha": commit_sha}
    )

    if not patch_response:
        print("Error: Failed to update the branch with the commit.")
        return

    # Create a pull request with the updated title and message
    pr_response = make_request(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls",
        method="POST",
        headers=headers,
        data={
            "title": f"Update quotes.json for {start_of_week_day_name} ({start_of_week_str}) to {current_day_name} ({current_day_str})",
            "head": BRANCH_NAME,
            "base": "main",
            "body": (
                f"Hello, I found some of your new thoughts in your diary. "
                f"Would you like to update it with the schedule from {start_of_week_day_name} ({start_of_week_str}) "
                f"to {current_day_name} ({current_day_str}) to be sent to your channel? "
                f"Please review and update it."
            )
        }
    )

    if pr_response and "html_url" in pr_response:
        print("Pull request created successfully:", pr_response["html_url"])

        # Assign a reviewer
        pr_number = pr_response["number"]
        review_response = make_request(
            f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/requested_reviewers",
            method="POST",
            headers=headers,
            data={"reviewers": ["ankit-chaubey"]}  # Replace with actual GitHub username
        )

        if review_response and review_response.get("status_code") == 201:
            print("Reviewer assigned successfully.")
        else:
            print("Failed to assign reviewer:", review_response)

        # Assign the "New Content Level" label to the pull request
        label_payload = {"labels": ["new content"]}
        label_response = make_request(
            f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{pr_number}/labels",
            method="POST",
            headers=headers,
            data=label_payload
        )

        if label_response and label_response.get("status_code") == 200:
            print('Label "New Content Level" added successfully.')
        else:
            print('Failed to add label:', label_response)
    else:
        print("Failed to create pull request:", pr_response)

# Run the script
if __name__ == "__main__":
    create_pull_request_with_reviewer()
