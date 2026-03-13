import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger("SlackUtil")

SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL") 

client = WebClient(token=SLACK_TOKEN)

def send_alert(message: str, severity: str = "INFO"):
  if not SLACK_TOKEN or not SLACK_CHANNEL:
    logger.error("Slack configuration missing (Token or Channel).")
    return

  if SLACK_CHANNEL.startswith("#"):
    logger.warning(f"Using channel name '{SLACK_CHANNEL}'. If it fails, use the Channel ID instead.")

  icons = {"INFO": "ℹ️", "WARN": "⚠️", "CRITICAL": "🚨", "COST": "💰", "SECURITY": "🔐"}
  icon = icons.get(severity, "🤖")
  formatted_message = f"{icon} *k8s-engine Alert* [{severity}]\n{message}"

  try:
    client.chat_postMessage(channel=SLACK_CHANNEL, text=formatted_message)
    logger.info(f"✅ Successfully sent {severity} alert to Slack.")
  except SlackApiError as e:
    logger.error(f"❌ Slack API Error: {e.response['error']}")