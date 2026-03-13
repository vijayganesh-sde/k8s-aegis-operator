import base64
from datetime import datetime
from utils.slack import send_alert
from .base import BaseModule

class SecurityModule(BaseModule):
  def run_logic(self):
    self.logger.info("Security Module is active and auditing secret lifetimes.")

  def check_secret_expiry(self, name, namespace, body):
    if namespace in ["kube-system", "kube-public"] or name == "slack-secrets":
      return

    labels = body.get('metadata', {}).get('labels', {})
    if labels.get('business/managed') != 'true':
      return

    self.logger.info(f"🛡️ Auditing Secret: {namespace}/{name}")

    secret_data = body.get('data', {})
    if not secret_data:
      return

    expiry_raw_b64 = secret_data.get('expiry-date')
    if not expiry_raw_b64:
      return

    try:
      expiry_str = base64.b64decode(expiry_raw_b64).decode('utf-8')
      expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
      today = datetime.now()

      if expiry_date < today:
        self.logger.error(f"🚨 Secret {name} HAS EXPIRED!")
        msg = f"🚨 *Security Outage Risk:* Secret `{name}` expired on `{expiry_str}`! Rotate credentials immediately."
        send_alert(msg, severity="CRITICAL")
      
      elif (expiry_date - today).days < 7:
        self.logger.warning(f"🔐 Secret {name} expiring soon.")
        msg = f"🔐 *Security Warning:* Secret `{name}` will expire in `{(expiry_date - today).days}` days."
        send_alert(msg, severity="SECURITY")

    except Exception as e:
      self.logger.error(f"Failed to parse expiry date for {name}: {e}")