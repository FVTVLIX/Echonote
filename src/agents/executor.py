# src/agents/executor.py
from src.integrations.gmail_client import send_email
from src.integrations.notion_client import create_task as notion_create
from src.integrations.trello_client import create_card as trello_create
import logging

logger = logging.getLogger("executor")

class ExecutorAgent:
    def __init__(self, tool: str = "gmail"):
        self.tool = tool  # "gmail", "notion", "trello"

    def execute_action_items(self, items: list, meeting_summary: str):
        if not isinstance(items, list):
            logger.error(f"Executor received {type(items).__name__} instead of list.")
            return

        for item in items:
            if not isinstance(item, dict):
                logger.warning(f"Skipping non-dictionary item: {item}")
                continue

            # Safe access with defaults
            task = item.get('task', 'Unknown Task')
            owner = item.get('owner', 'Unknown Speaker')
            due = item.get('due', 'ASAP')
            priority = item.get('priority', 'medium')

            if self.tool == "gmail":
                body = f"""
                Hi {owner},

                Following up on our meeting:
                Task: {task}
                Due: {due}
                Priority: {priority}

                Summary: {meeting_summary}

                Please confirm when complete.
                """
                recipient = f"{owner.lower().replace(' ', '.')}@company.com"
                subject = "Action Item: " + task[:50]
                try:
                    send_email(recipient, subject, body)
                except Exception as e:
                    logger.error(f"Failed to send email to {recipient}: {e}")

            elif self.tool == "notion":
                try:
                    notion_create(task, due_date=due, assignee=owner)
                except Exception as e:
                    logger.error(f"Failed to create Notion task: {e}")

            elif self.tool == "trello":
                try:
                    trello_create(task, desc=f"Owner: {owner}\nPriority: {priority}\nSummary: {meeting_summary}", list_id="to-do")
                except Exception as e:
                    logger.error(f"Failed to create Trello card: {e}")