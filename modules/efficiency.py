from utils.slack import send_alert
from datetime import datetime
from kubernetes import client, config
from .base import BaseModule

class EfficiencyModule(BaseModule):
  def run_logic(self):
    self.logger.info("Efficiency Module is active and monitoring PVCs/Deployments.")

  def scan_for_zombies(self, name, namespace, status):
    """
    Triggered by engine.py. 
    Checks if a Bound PVC is actually attached to any running Pod.
    """
    phase = status.get('phase')
    self.logger.info(f"🔍 Scanning PVC {name} (Phase: {phase})")

    # The "Outage" scenario
    if phase == 'Pending':
      self.logger.warning(f"⏳ PVC {name} is stuck in Pending. Application may be failing to start.")


    #The "Waste" scenario
    elif phase == 'Bound':
      is_attached = self._is_pvc_used_by_pods(name, namespace)
      if not is_attached:
        self.logger.warning(f"🧟 Zombie Found: {name}")
        msg = f"💰 *Cost Alert:* PVC `{name}` is Bound but NOT in use. Delete it to save costs!"
        send_alert(msg, severity="COST")

  def _is_pvc_used_by_pods(self, pvc_name, namespace):
    """Internal helper to query the K8s API."""
    try:
      v1 = client.CoreV1Api()
      pods = v1.list_namespaced_pod(namespace)
      for pod in pods.items:
        if pod.spec.volumes:
          for vol in pod.spec.volumes:
            if vol.persistent_volume_claim and vol.persistent_volume_claim.claim_name == pvc_name:
              return True
      return False
    except Exception as e:
      self.logger.error(f"Failed to check pod attachments: {e}")
      return True 

  def manage_sleep_schedule(self, name, spec, patch):
    hour = datetime.now().hour
    # Business Logic: Scale to 0 between 8 PM and 8 AM
    if (hour >= 20 or hour < 8) and spec.get('replicas') != 0:
      patch.spec['replicas'] = 0
      send_alert(f"🌙 *Cost Optimization:* Scaled down `{name}` for the night.", severity="COST")