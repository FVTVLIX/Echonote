# src/integrations/trello_client.py
import requests
from src.config.settings import settings

def create_card(name: str, desc: str = "", list_id: str = None):
    url = "https://api.trello.com/1/cards"
    
    # If list_id is not provided, we should probably have a default or fetch one
    # For now, we assume settings might have a default list ID or we use a placeholder
    final_list_id = list_id if list_id != "to-do" else settings.trello_board_id # This usage is a bit loose
    
    query = {
        'idList': final_list_id,
        'key': settings.trello_api_key,
        'token': settings.trello_token,
        'name': name,
        'desc': desc
    }

    response = requests.post(url, params=query)
    if response.status_code != 200:
        print(f"Error creating Trello card: {response.text}")
    return response.json()
