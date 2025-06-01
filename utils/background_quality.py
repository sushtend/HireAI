import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

def score_github_background(github_url: str) -> int:
    """
    Score a candidate's GitHub background quality using public profile scraping.
    Args:
        github_url (str): The candidate's GitHub profile URL
    Returns:
        int: Score between 0 and 100
    """
    if not github_url or 'github.com' not in github_url:
        return 0

    try:
        response = requests.get(github_url)
        if response.status_code != 200:
            return 0

        soup = BeautifulSoup(response.text, 'html.parser')

        # Number of public repositories
        repo_count = 0
        repo_tag = soup.find('span', {'class': 'Counter'})
        if repo_tag:
            try:
                repo_count = int(repo_tag.text.strip().replace(',', ''))
            except Exception:
                repo_count = 0

        # Number of followers
        followers = 0
        followers_tag = soup.find('a', href=lambda x: x and x.endswith('?tab=followers'))
        if followers_tag:
            try:
                followers = int(followers_tag.find('span', class_='text-bold').text.strip())
            except Exception:
                followers = 0

        # Arctic Code Vault Contributor badge
        arctic_vault = 'Arctic Code Vault Contributor' in response.text

        # Profile picture
        avatar = soup.find('img', {'alt': 'Avatar'})
        has_avatar = bool(avatar and avatar.get('src'))

        # Scoring logic (tweak as needed)
        score = 0
        score += min(repo_count, 20) * 2      # up to 40 points for repos
        score += min(followers, 20) * 2       # up to 40 points for followers
        if arctic_vault:
            score += 10
        if has_avatar:
            score += 10

        return min(score, 100)

    except Exception as e:
        print(f"Error scoring GitHub profile: {e}")
        return 0


def score_linkedin_background(linkedin_url: str) -> int:
    """
    Score a candidate's LinkedIn background quality.
    Args:
        linkedin_url (str): The candidate's LinkedIn profile URL
    Returns:
        int: Score between 0 and 100
    """
    # TODO: Plug in LinkedIn API or LLM for real scoring, or use data from resume/form
    if not linkedin_url or 'linkedin.com' not in linkedin_url:
        return 0
    # Mock logic: higher score if URL is present
    return 80  # Placeholder score


def score_public_presence(name: str, github_url: str = None, linkedin_url: str = None) -> int:
    """
    Score a candidate's public presence (e.g., mentions, talks, publications).
    Args:
        name (str): Candidate's full name
        github_url (str, optional): GitHub profile URL
        linkedin_url (str, optional): LinkedIn profile URL
    Returns:
        int: Score between 0 and 100
    """
    # TODO: Plug in web search, LLM, or external APIs for real scoring
    if not name:
        return 0
    # Mock logic: higher score if both URLs are present
    score = 50
    if github_url:
        score += 15
    if linkedin_url:
        score += 15
    return min(score, 100)


def score_github_background_api(github_url: str, github_token: str = None) -> int:
    """
    Score a candidate's GitHub background quality using the GitHub API.
    Args:
        github_url (str): The candidate's GitHub profile URL
        github_token (str, optional): GitHub personal access token for higher rate limits
    Returns:
        int: Score between 0 and 100
    """
    if not github_url or 'github.com' not in github_url:
        return 0

    # Extract username from URL
    try:
        username = github_url.rstrip('/').split('/')[-1]
    except Exception:
        return 0

    api_url = f"https://api.github.com/users/{username}"
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'

    try:
        resp = requests.get(api_url, headers=headers)
        if resp.status_code != 200:
            print(f"GitHub API error: {resp.status_code} {resp.text}")
            return 0
        data = resp.json()

        # Scoring logic
        score = 0
        score += min(data.get('public_repos', 0), 20) * 2      # up to 40 points for repos
        score += min(data.get('followers', 0), 20) * 2         # up to 40 points for followers
        if data.get('avatar_url'):
            score += 10
        # Arctic Code Vault badge is not available via API, so skip

        return min(score, 100)
    except Exception as e:
        print(f"Error scoring GitHub profile via API: {e}")
        return 0

if __name__ == "__main__":
    # Test GitHub scoring (scraping)
    github_url_sushtend = "https://github.com/sushtend/"
    score_gh_scrape_sushtend = score_github_background(github_url_sushtend)
    print(f"GitHub score (scrape) for {github_url_sushtend}: {score_gh_scrape_sushtend}")
    
    # Test GitHub scoring (API)
    # Replace with a real GitHub username and your token if testing with API
    github_url_api_test = "https://github.com/octocat"
    github_token = os.getenv("GITHUB_TOKEN")
    score_gh_api_test = score_github_background_api(github_url_api_test, github_token=github_token)
    print(f"GitHub score (API) for {github_url_api_test}: {score_gh_api_test}")

    # Test LinkedIn scoring (placeholder)
    linkedin_url_sushtend = "http://linkedin.com/in/sushtend/"
    linkedin_url_none = ""
    score_li_sushtend = score_linkedin_background(linkedin_url_sushtend)
    score_li_none = score_linkedin_background(linkedin_url_none)
    print(f"LinkedIn score for {linkedin_url_sushtend}: {score_li_sushtend}")
    print(f"LinkedIn score for {linkedin_url_none}: {score_li_none}")

    # Test Public Presence scoring
    name_sushtend = "Sushrut Tendulkar"
    github_url_sushtend_public = "https://github.com/sushtend/"
    linkedin_url_sushtend_public = "http://linkedin.com/in/sushtend/"
    
    score_public_full = score_public_presence(name_sushtend, github_url_sushtend_public, linkedin_url_sushtend_public)
    score_public_no_github = score_public_presence(name_sushtend, linkedin_url=linkedin_url_sushtend_public)
    score_public_no_linkedin = score_public_presence(name_sushtend, github_url=github_url_sushtend_public)
    score_public_name_only = score_public_presence(name_sushtend)
    score_public_none = score_public_presence("")
    
    print(f"Public Presence (Name + GH + LI) for {name_sushtend}: {score_public_full}")
    print(f"Public Presence (Name + LI) for {name_sushtend}: {score_public_no_github}")
    print(f"Public Presence (Name + GH) for {name_sushtend}: {score_public_no_linkedin}")
    print(f"Public Presence (Name Only) for {name_sushtend}: {score_public_name_only}")
    print(f"Public Presence (None): {score_public_none}") 