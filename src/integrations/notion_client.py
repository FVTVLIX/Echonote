# src/integrations/notion_client.py
import requests
from src.config.settings import settings

def create_task(title: str, due_date: str = None, assignee: str = None):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {settings.notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    data = {
        "parent": {"database_id": settings.notion_database_id},
        "properties": {
            "Name": {
                "title": [{"text": {"content": title}}]
            },
            "Assignee": {
                "rich_text": [{"text": {"content": assignee if assignee else "Unassigned"}}]
            }
        }
    }
    
    if due_date:
        data["properties"]["Due Date"] = {
            "date": {"start": due_date}
        }
        
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"Error creating Notion task: {response.text}")
    return response.json()
