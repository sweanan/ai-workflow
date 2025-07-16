from unittest import result
# import yaml
import openai
from dotenv import load_dotenv
import os
import utils
import json
import argparse

# def load_config(config_path):
#     """
#     Load configuration variables from a YAML file.

#     Args:
#         config_path (str): Path to the YAML configuration file.

#     Returns:
#         dict: Configuration variables.
#     """
#     with open(config_path, 'r') as file:
#         return yaml.safe_load(file)

def classify_workitem(work_item):
    """
    Classify a work item as a bug or not using OpenAI's Chat Completion API.

    Args:
        work_item (dict): The work item to classify.

    Returns:
        str: Classification result (e.g., 'Bug' or 'Not a Bug').
    """
    # Load configuration
    #config = load_config("model_config.yaml")
    # openai.api_key = config["openai_api_key"]
    load_dotenv()
    
    # openai.api_type = "azure"
    # openai.api_key = os.environ["AZURE_OPENAI_KEY"]
    # openai.api_base = os.environ["AZURE_OPENAI_ENDPOINT"]
    # openai.api_version = os.environ["AZURE_OPENAI_API_VERSION"]
    # deployment_name = os.environ["AZURE_OPENAI_DEPLOYMENT"]
    openai.api_type = os.getenv("AZURE_OPENAI_API_TYPE", "azure")
    openai.api_key = os.getenv("AZURE_OPENAI_KEY")
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    # Define system and user prompts
    #system_prompt = "You are a helpful software engineer assistant that classifies work items as bugs or not."
    system_prompt = """
        You are a helpful software engineer assistant that classifies work items as bugs or not.
        
        You will be provided with a work item number and description, and your task is to determine if it is a bug or story or feature by analyzing the content of the work item.
        If it is a bug, respond with "Bug". 
            If the work item is a bug, it should describe an issue or defect in the code that needs to be fixed.
            If the work item is a bug, it should include specific details about the problem, such as error messages, unexpected behavior, or steps to reproduce the issue.
        If it is story, respond with "Story".
        If it is a feature, respond with "Feature".
        If you are unsure, respond with "Uncertain" and provide a brief explanation.
        If the work item is a bug, review the work item description and related code to identify the root cause, include any potential resolution steps or suggestions for fixing the issue.
        If the work item is a bug, review the work item description and related code, and pose questions if unable to provide resolution steps.
        Provide your classification in the following format:
        ```json
        {
            "classification": "Bug"  # or "Story", "Feature", "Uncertain"
            "explanation": "Brief explanation of your classification decision."
            "resolution": "Optional resolution steps or suggestions if applicable. For example, 'Investigate the issue in the login module and fix the null pointer exception.'"
            "questions": "Optional questions for clarification if unable to provide resolution steps. For example, 'Could you provide more details about the error message encountered?'"
        }
        ```

        """
    
    
    user_prompt = f"Classify the following work item:\n{work_item}"

    # Call OpenAI's Chat Completion API
    response = openai.ChatCompletion.create(
        # model=config["model"],
        engine=deployment_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    # Extract and return the classification result
    print(response["choices"][0]["message"]["content"].strip())
    reply = response["choices"][0]["message"]["content"].strip()

    result = utils.extract_json_from_response(response["choices"][0]["message"]["content"].strip())

    try:
        parsed_result = json.loads(result)
    except json.JSONDecodeError:
        raise ValueError(f"❌ Model returned non-JSON: {result}")

    return parsed_result, reply


# Uncomment this if you want to run the script directly for testing
# This is useful for debugging or local testing without the full application context.
# if __name__ == "__main__":
#     workitem_id = 13
#     org = "sweanan"
#     repo = "ai-workflow"
#     from load_github import load_github_workitem
#     workitem = load_github_workitem(workitem_id, org, repo)

#     parsed_result, reply  = classify_workitem(workitem)

#     print("Classification:", parsed_result.get("classification", "Unknown"))
#     print("Reply:", reply)


def parse_args() -> argparse.Namespace:
    """Parse arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser("issue_content_classifier")

    parser.add_argument(
        "--issue_content",
        type=str,
        help="Content of the issue",
    )

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

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    parsed_result, reply  = classify_workitem(args.issue_content)

    print("Classification:", parsed_result.get("classification", "Unknown"))
    print("Reply:", reply)