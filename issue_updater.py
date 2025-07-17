import requests
import os
from dotenv import load_dotenv
import argparse


def update_githubitem(workitem_id, org, repo, classification):
    """
    Update a GitHub work item with its classification.

    Args:
        workitem (dict): The work item to update.
        classification (str): The classification result (e.g., 'Bug' or 'Not a Bug').

    Returns:
        dict: The response from the GitHub API.
    """
        # Load the token from the .env file
    load_dotenv()
    GITHUB_TOKEN = os.getenv("HVE_Token")

    # Extract necessary details from the work item
    if not workitem_id or not repo:
        raise ValueError("Invalid work item data. Missing issue number or repository URL.")

    # Construct the API URL
    url = f"https://api.github.com/repos/{org}/{repo}/issues/{workitem_id}"

    # Prepare the payload
    payload = {
        "labels": [classification.upper()] if classification.lower() in ["bug", "story", "feature"] else [],
    }

    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # Check if the label 'BUG' is already set
    get_response = requests.get(url, headers=headers)
    if get_response.status_code == 200:
        print("Existing issue found:", get_response.json())
        existing_labels = [label['name'] for label in get_response.json().get('labels', [])]
        if "BUG" in existing_labels:
            print("Label 'BUG' is already set. No update needed.")
            return get_response.json()

    # Make the PATCH request to update the issue if 'BUG' label is not set
    response = requests.patch(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


# Uncomment this if you want to run the script directly for testing
# This is useful for debugging or local testing without the full application context.
# if __name__ == "__main__":
#     workitem_id = 11
#     org = "sweanan"
#     repo = "ai-workflow"

#     update_response = update_githubitem(workitem_id, org, repo, "Feature")
#     print("Update Response:", update_response)

def parse_args() -> argparse.Namespace:
    """Parse arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser("issue_content_classifier")

    parser.add_argument(
        "--issue_number",
        type=str,
        help="Number of the issue",
    )
    parser.add_argument(
        "--repo",
        type=str,
        help="Repository name",
    )

    parser.add_argument(
        "--org",
        help="Organization name",
        type=str,
    )

    parser.add_argument(
        "--classification",
        help="Classification of the issue (e.g., Bug, Story, Feature)",
        type=str,
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    update_response = update_githubitem(args.issue_number, args.org, args.repo, args.classification)

    print("Update Response:", update_response)