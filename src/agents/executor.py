# src/agents/executor.py
from src.integrations.gmail_client import send_email
from src.integrations.notion_client import create_task as notion_create
from src.integrations.trello_client import create_card as trello_create

class ExecutorAgent:
    def __init__(self, tool: str = "gmail"):
        self.tool = tool  # "gmail", "notion", "trello"

    def execute_action_items(self, items: list, meeting_summary: str):
        for item in items:
            if self.tool == "gmail":
                body = f"""
                Hi {item['owner']},

                Following up on our meeting:
                Task: {item['task']}
                Due: {item.get('due', 'ASAP')}
                Priority: {item['priority']}

                Summary: {meeting_summary}

                Please confirm when complete.
                """
                send_email(f"{item['owner'].lower().replace(' ', '.')}@company.com", 
                          "Action Item: " + item['task'][:50], body)

            elif self.tool == "notion":
                notion_create(item['task'], due_date=item.get('due'), assignee=item['owner'])

            elif self.tool == "trello":
                trello_create(item['task'], desc=str(item), list_id="to-do")