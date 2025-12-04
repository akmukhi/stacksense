from .base_integration import BaseIntegration
from .google_workspace import GoogleWorkspaceIntegration
from .microsoft_365 import Microsoft365Integration
from .slack import SlackIntegration
from .github import GitHubIntegration
from .jira import JiraIntegration
from .notion import NotionIntegration

__all__ = [
    "BaseIntegration",
    "GoogleWorkspaceIntegration",
    "Microsoft365Integration",
    "SlackIntegration",
    "GitHubIntegration",
    "JiraIntegration",
    "NotionIntegration",
]

