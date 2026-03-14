from .base import BaseModule
from utils.slack import send_alert
import time

class ResilienceModule(BaseModule):
  def __init__(self):
    super().__init__()
    self.last_alert_time = {}  # To track last alert times for rate limiting
  def run_logic(self):
    self.logger.info("🛡️ Resilience Module is active.")

  def handle_oom(self, name, namespace, status):
    container_statuses = status.get('containerStatuses', [])
    for cs in container_statuses:
      state = cs.get('state', {}).get('terminated', {})
      last_state = cs.get('lastState', {}).get('terminated', {})
      
        # THE CATCH: Signal 9 or 'OOMKilled' reason
      if state.get('reason') == 'OOMKilled' or last_state.get('reason') == 'OOMKilled':
          
        current_time = time.time()
        if name in self.last_alert_time and (current_time - self.last_alert_time[name]) < 300:
          return

        self.logger.error(f"🚨 Resilience Alert: Pod {name} killed by OOM.")

        self.last_alert_time[name] = current_time
        
        msg = (f"🚨 *Out of Memory (OOM):* Pod `{name}` in `{namespace}` was terminated.\n"
                f"📦 *Container:* `{cs.get('name')}`\n"
                f"🔄 *Restart Count:* `{cs.get('restartCount')}`\n"
                f"💡 *Tip:* Increase memory limits in the deployment spec.")
        send_alert(msg, severity="CRITICAL")