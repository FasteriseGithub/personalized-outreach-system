import requests
from langchain_community.utilities import GoogleSerperAPIWrapper
from typing import Any, Dict, List, Optional

def scrape_linkedin_profile(linkedin_profile_url):
    relevance_api_key = 'your_relevance_api_key'
    relevance_auth_token = 'your_relevance_auth_token'
    relevance_project_id = 'your_relevance_project_id'
    relevance_region = 'your_relevance_region'

    linkedin_scraper_api_endpoint = f'https://api-{relevance_region}.stack.tryrelevance.com/latest/studios/your_studio_id/trigger_limited'

    payload = {
        "params": {
            "url": linkedin_profile_url
        },
        "project": relevance_project_id
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {relevance_auth_token}'
    }

    try:
        response = requests.post(linkedin_scraper_api_endpoint, json=payload, headers=headers)
        response.raise_for_status()
        linkedin_data = response.json()
        return linkedin_data
    except requests.exceptions.RequestException as e:
        print(f"Error scraping LinkedIn profile: {e}")
        return None
    


class CustomGoogleSerperAPIWrapper(GoogleSerperAPIWrapper):
    def __init__(self):
        super().__init__(k=3)

    # getting metadata from my search results in google
    def _parse_snippets(self, results: dict) -> List[str]:
        pprint(results)
        snippets = []

         # extract value from the google search metadata
        for result in results[self.result_key_for_type[self.type]][:self.k]:
            if "snippet" in result:
                snippets.append(result["snippet"])
            for attribute, value in results.get("attributes", {}).items():
                snippets.append(f"{attribute}: {value}.")
            if "link" in result and "title" in result:
                snippets.append(f"""{result["title"]}: {result["link"]}.""")

        if len(snippets) == 0:
            return ["No good Google Search Result was found"]
        return snippets
