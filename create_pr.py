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
    main_ref = requests.get(f"{branch_url}/heads/main", headers=headers).json()
    sha = main_ref["object"]["sha"]

    branch_payload = {"ref": f"refs/heads/{BRANCH_NAME}", "sha": sha}
    requests.post(branch_url, headers=headers, json=branch_payload)

    # Commit the changes
    with open(QUOTES_FILE, "r") as file:
        quotes_content = file.read()

    blob_response = requests.post(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/blobs",
        headers=headers,
        json={"content": quotes_content, "encoding": "utf-8"}
    ).json()

    tree_response = requests.post(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/trees",
        headers=headers,
        json={
            "base_tree": sha,
            "tree": [{"path": QUOTES_FILE, "mode": "100644", "type": "blob", "sha": blob_response["sha"]}]
        }
    ).json()

    commit_response = requests.post(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/commits",
        headers=headers,
        json={
            "message": f"Update quotes.json for {start_of_week_day_name} ({start_of_week_str}) to {current_day_name} ({current_day_str})",
            "tree": tree_response["sha"],
            "parents": [sha]
        }
    ).json()

    requests.patch(
        f"{branch_url}/heads/{BRANCH_NAME}",
        headers=headers,
        json={"sha": commit_response["sha"]}
    )

    # Create a pull request with the updated title and message
    pr_response = requests.post(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls",
        headers=headers,
        json={
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
    ).json()

    if "html_url" in pr_response:
        pr_url = pr_response["html_url"]
        print("Pull request created successfully:", pr_url)

        # Output PR URL to GitHub Actions
        print(f"::set-output name=pr_url::{pr_url}")  # This will pass the PR URL as an output in GitHub Actions

        # Assign a reviewer
        pr_number = pr_response["number"]
        review_response = requests.post(
            f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/requested_reviewers",
            headers=headers,
            json={"reviewers": ["ankit-chaubey"]}  # Replace with actual GitHub username
        )

        if review_response.status_code == 201:
            print("Reviewer assigned successfully.")
            # Output reviewer status to GitHub Actions
            print(f"::set-output name=reviewer_status::Reviewer assigned successfully.")
        else:
            print("Failed to assign reviewer:", review_response.json())
            # Output error to GitHub Actions
            print(f"::set-output name=reviewer_status::Failed to assign reviewer.")

        # Assign the "New Content Level" label to the pull request
        label_payload = {"labels": ["new content"]}
        label_response = requests.post(
            f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{pr_number}/labels",
            headers=headers,
            json=label_payload
        )

        if label_response.status_code == 200:
            print('Label "New Content Level" added successfully.')
            # Output label status to GitHub Actions
            print(f"::set-output name=label_status::Label 'New Content Level' added successfully.")
        else:
            print('Failed to add label:', label_response.json())
            # Output error to GitHub Actions
            print(f"::set-output name=label_status::Failed to add label.")
    else:
        print("Failed to create pull request:", pr_response)
        # Output failure to GitHub Actions
        print(f"::set-output name=pr_creation_status::Failed to create pull request.")

# Run the script
if __name__ == "__main__":
    create_pull_request_with_reviewer()
