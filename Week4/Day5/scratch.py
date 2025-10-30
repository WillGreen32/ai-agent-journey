from src.client.github import GitHubClient

# Put your PAT here (PATs use "token <PAT>" under the hood in the client)
TOKEN = "YOUR_GITHUB_PAT"

client = GitHubClient(auth_token=TOKEN)

# 1) Repos
first_repo = next(client.list_repos("octocat"))
print("Repo:", first_repo["name"])

# 2) Single repo (ETag cache)
repo = client.get_repo("octocat", "Hello-World")
print("Full name:", repo["full_name"])

# 3) Commits (paginated)
first_commit = next(client.list_commits("octocat", "Hello-World"))
print("Commit SHA:", first_commit["sha"])
    