import re

def extract_json_from_response(reply):
    # Match first code block with json, fallback to raw content
    match = re.search(r"```json\s*(\{.*?\})\s*```", reply, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return reply.strip()