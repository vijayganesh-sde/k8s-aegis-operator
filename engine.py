import kopf
import logging
from modules.efficiency import EfficiencyModule
from modules.security import SecurityModule
from modules.compliance import ComplianceModule

# Initialize Modules
efficiency = EfficiencyModule()
security = SecurityModule()
compliance = ComplianceModule()

@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
  settings.scanning.cluster_wide = True
  logging.info("🚀 k8s-engine: Business Reliability Platform Started")

# --- Efficiency Handlers ---
@kopf.on.create('persistentvolumeclaims')
@kopf.on.update('persistentvolumeclaims')
def handle_pvc_events(name, namespace, status, **kwargs):
  efficiency.scan_for_zombies(name, namespace, status)

@kopf.timer('deployments', interval=3600, labels={'business/auto-sleep': 'true'})
def handle_sleep_cycle(name, spec, patch, **_):
  efficiency.manage_sleep_schedule(name, spec, patch)

# --- Security & Compliance Handlers ---
@kopf.timer('secrets', interval=86400) # Check once a day
def monitor_secrets(name, namespace, body, **_):
  security.check_secret_expiry(name, namespace, body)

@kopf.on.create('deployments')
@kopf.on.update('deployments')
def enforce_compliance(name, namespace, spec, patch, **_):
  if namespace in ["kube-system", "kube-public", "kube-node-lease"]:
    return
  compliance.enforce_resource_limits(name, spec, patch)