import requests
import os

# Settings
owner = "XainLubin"
repo = "CSC365GroupProject"
token = None  # Optional, use None for public repo access
output_file = "all_issues.txt"

# GitHub API endpoint
url = f"https://api.github.com/repos/{owner}/{repo}/issues"
headers = {"Authorization": f"token {token}"} if token else {}

params = {
    "state": "all",  # options: open, closed, all
    "per_page": 100,
    "page": 1
}

with open(output_file, "w", encoding="utf-8") as f:
    issue_count = 0
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        issues = response.json()

        if not issues:
            break

        for issue in issues:
            if "pull_request" in issue:
                continue  # Skip PRs that show up in issues

            issue_count += 1
            f.write(f"Issue #{issue['number']}: {issue['title']}\n")
            f.write(f"State: {issue['state']} | Created: {issue['created_at']} | Author: {issue['user']['login']}\n")
            f.write("-" * 80 + "\n")
            f.write(issue['body'] or "[No description]")  # Handle empty bodies
            f.write("\n" + "=" * 100 + "\n\n")

        params["page"] += 1

print(f"{issue_count} issues written to {output_file}")
