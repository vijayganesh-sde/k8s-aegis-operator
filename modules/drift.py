import json
from .base import BaseModule
from utils.slack import send_alert

class DriftModule(BaseModule):
  def run_logic(self):
    self.logger.info("🔍 Running Drift Detection Logic...")

  def check_drift(self, name, namespace, body, patch):
    annotations = body.get('metadata', {}).get('annotations', {})
    last_applied_str = annotations.get('kubectl.kubernetes.io/last-applied-configuration')
    
    if not last_applied_str:
      return # Skip if not deployed via 'kubectl apply'

    last_applied_spec = json.loads(last_applied_str).get('spec', {})
    desired_replicas = last_applied_spec.get('replicas')
    
    current_replicas = body.get('spec', {}).get('replicas')
    self.logger.info(f"🧐 Checking Drift for {name}: Desired={desired_replicas}, Current={current_replicas}")
    if desired_replicas is not None and current_replicas != desired_replicas:
      self.logger.warning(f"🔄 Drift! {name} has {current_replicas} replicas, should be {desired_replicas}")
      
      patch.spec['replicas'] = desired_replicas
      send_alert(f"🔄 *Drift Reverted:* Restored `{name}` to {desired_replicas} replicas.", severity="WARN")