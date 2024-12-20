import os
import requests

# Get the environment variables
GH_TOKEN = os.getenv("GH_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")
QUOTES_FILE = "quotes.json"
BRANCH_NAME = "update-quotes"

# Function to create a pull request and assign a reviewer
def create_pull_request_with_reviewer():
    headers = {
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

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
            "message": "Update quotes.json for next week",
            "tree": tree_response["sha"],
            "parents": [sha]
        }
    ).json()

    requests.patch(
        f"{branch_url}/heads/{BRANCH_NAME}",
        headers=headers,
        json={"sha": commit_response["sha"]}
    )

    # Create a pull request
    pr_response = requests.post(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls",
        headers=headers,
        json={
            "title": "Update quotes.json for next week",
            "head": BRANCH_NAME,
            "base": "main",
            "body": "This pull request updates the quotes.json file with messages scheduled for next week."
        }
    ).json()

    if "html_url" in pr_response:
        print("Pull request created successfully:", pr_response["html_url"])

        # Assign a reviewer
        pr_number = pr_response["number"]
        review_response = requests.post(
            f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/requested_reviewers",
            headers=headers,
            json={"reviewers": ["ankit-chaubey"]}  # Replace with actual GitHub username
        )

        if review_response.status_code == 201:
            print("Reviewer assigned successfully.")
        else:
            print("Failed to assign reviewer:", review_response.json())
    else:
        print("Failed to create pull request:", pr_response)

# Run the script
if __name__ == "__main__":
    create_pull_request_with_reviewer()
