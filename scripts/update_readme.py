"""
Auto-update the README.md projects section with latest GitHub repos.
Runs via GitHub Actions — fetches public repos, generates markdown cards,
and replaces content between marker comments.
"""

import json
import os
import urllib.request

USERNAME = "krishbaveja07"
README_PATH = "README.md"
EXCLUDE_REPOS = {USERNAME}  # exclude the profile repo itself

# Language → color mapping for badges
LANG_COLORS = {
    "TypeScript": "3178C6",
    "JavaScript": "F7DF1E",
    "Kotlin": "7F52FF",
    "Python": "3776AB",
    "Java": "ED8B00",
    "HTML": "E34F26",
    "CSS": "1572B6",
    "Swift": "F05138",
    "Dart": "0175C2",
    "Go": "00ADD8",
    "Rust": "DEA584",
    "C++": "00599C",
    "C": "A8B9CC",
    "Ruby": "CC342D",
    "PHP": "777BB4",
    "Shell": "89E051",
}


def fetch_repos():
    """Fetch all public repos for the user via GitHub API."""
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated&type=public"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"token {token}")

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def make_lang_badge(language):
    """Create a shields.io badge for a language."""
    if not language:
        return ""
    color = LANG_COLORS.get(language, "8b949e")
    logo_color = "black" if language == "JavaScript" else "white"
    return f"![{language}](https://img.shields.io/badge/{language}-{color}?style=flat-square&logo={language.lower()}&logoColor={logo_color})"


def make_repo_card(repo):
    """Generate a markdown card for a single repo."""
    name = repo["name"]
    desc = repo["description"] or "No description provided"
    lang = repo["language"] or ""
    stars = repo["stargazers_count"]
    forks = repo["forks_count"]
    url = repo["html_url"]

    lang_badge = make_lang_badge(lang)
    stars_badge = f"![Stars](https://img.shields.io/github/stars/{USERNAME}/{name}?style=flat-square&color=58a6ff&label=%E2%AD%90)"
    forks_badge = f"![Forks](https://img.shields.io/github/forks/{USERNAME}/{name}?style=flat-square&color=8b949e&label=%F0%9F%94%80)"

    card = f"""### <a href="{url}">{name}</a>
{lang_badge} {stars_badge} {forks_badge}

> {desc}"""
    return card


def generate_projects_section(repos):
    """Generate the full projects table from a list of repos."""
    if not repos:
        return "_No public repositories yet — stay tuned!_"

    rows = []
    # Process repos in pairs for 2-column layout
    for i in range(0, len(repos), 2):
        left = repos[i]
        right = repos[i + 1] if i + 1 < len(repos) else None

        left_card = make_repo_card(left)
        if right:
            right_card = make_repo_card(right)
            row = f"""<tr>
<td width="50%" valign="top">

{left_card}

</td>
<td width="50%" valign="top">

{right_card}

</td>
</tr>"""
        else:
            row = f"""<tr>
<td width="50%" valign="top">

{left_card}

</td>
<td width="50%"></td>
</tr>"""
        rows.append(row)

    return "<table>\n" + "\n".join(rows) + "\n</table>"


def update_readme(projects_md):
    """Replace content between marker comments in README."""
    with open(README_PATH, "r") as f:
        content = f.read()

    start_marker = "<!-- PROJECTS:START -->"
    end_marker = "<!-- PROJECTS:END -->"

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        print("ERROR: Could not find PROJECTS markers in README.md")
        return False

    new_content = (
        content[: start_idx + len(start_marker)]
        + "\n"
        + projects_md
        + "\n"
        + content[end_idx:]
    )

    with open(README_PATH, "w") as f:
        f.write(new_content)

    print(f"README updated with {projects_md.count('<tr>')} project rows")
    return True


def main():
    repos = fetch_repos()

    # Filter out the profile repo and forks, sort by stars then updated
    repos = [
        r
        for r in repos
        if r["name"] not in EXCLUDE_REPOS and not r["fork"]
    ]
    repos.sort(key=lambda r: (r["stargazers_count"], r["updated_at"]), reverse=True)

    # Cap at 6 repos max for a clean look
    repos = repos[:6]

    projects_md = generate_projects_section(repos)
    update_readme(projects_md)


if __name__ == "__main__":
    main()
