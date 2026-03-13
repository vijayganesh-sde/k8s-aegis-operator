from utils.slack import send_alert
from .base import BaseModule

class ComplianceModule(BaseModule):
    def run_logic(self):
      self.logger.info("Compliance Module is active.")

    def enforce_resource_limits(self, name, spec, patch):
      if name in ["k8s-engine", "local-path-provisioner"]:
        return

      template = spec.get('template', {})
      pod_spec = template.get('spec', {})
      containers = pod_spec.get('containers', [])
      if not containers:
        return

      first_container = containers[0]
      resources = first_container.get('resources', {})
      limits = resources.get('limits', {})

      cpu = limits.get('cpu', '0')
      memory = limits.get('memory', '0')

      # Trigger if limits are missing OR if they exceed business thresholds
      # Note: In production, you'd use a proper parser for 'Mi'/'Gi' and 'm'
      needs_fix = False
      reason = ""

      if not limits:
        needs_fix = True
        reason = "Missing resource limits."
      elif "Gi" in str(memory) or (str(cpu).isdigit() and int(cpu) > 1):
        needs_fix = True
        reason = f"Resource limits too high ({cpu} CPU, {memory} Memory)."

      if needs_fix:
        self.logger.warning(f"⚖️ Compliance Violation on {name}: {reason}")
        
        patch.spec['template'] = {
            'spec': {
                'containers': [{
                    'name': first_container.get('name'),
                    'image': first_container.get('image'), 
                    'resources': {
                        'limits': {
                            'cpu': '500m',
                            'memory': '512Mi'
                        }
                    }
                }]
            }
        }

        msg = f"⚖️ *Compliance Enforcement:* Deployment `{name}` violated policy: {reason}. Reset to safe defaults."
        send_alert(msg, severity="WARN")