import os
import time
import requests

# Get the environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")
PR_NUMBER = os.getenv("PR_NUMBER")  # The PR number to check
REVIEWER = "ankit-chaubey"  # The GitHub username of the reviewer to look for

# GitHub API headers
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Function to check if the PR has been approved by the reviewer
def check_review_status(pr_number):
    reviews_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/reviews"
    reviews = requests.get(reviews_url, headers=headers).json()

    for review in reviews:
        if review["user"]["login"] == REVIEWER and review["state"] == "APPROVED":
            return True
    return False

# Function to merge the pull request
def merge_pull_request(pr_number):
    merge_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/merge"
    merge_response = requests.put(merge_url, headers=headers).json()
    
    if merge_response.get("merged", False):
        print(f"Pull request #{pr_number} merged successfully!")
    else:
        print(f"Failed to merge pull request #{pr_number}:", merge_response)

# Main function to wait for review and merge
def wait_for_review_and_merge():
    pr_number = 123  # Replace this with the actual PR number dynamically
    print(f"Checking review status for PR #{pr_number}...")

    # Wait for review and merge
    while True:
        if check_review_status(pr_number):
            merge_pull_request(pr_number)
            break
        else:
            print("Review not approved yet. Waiting...")
            time.sleep(60)  # Check every 60 seconds

# Run the script
if __name__ == "__main__":
    wait_for_review_and_merge()
