from kubernetes import client, config
import datetime
import os

class ActionExecutorAgent:
    def __init__(self, kubeconfig_path=None, simulation_mode=False):
        self.simulation_mode = simulation_mode

        # Load kubeconfig: use provided path, or env, or default
        if kubeconfig_path:
            config.load_kube_config(config_file=kubeconfig_path)
        else:
            try:
                config.load_incluster_config()
            except Exception:
                config.load_kube_config()  
                # Will use $KUBECONFIG or ~/.kube/config

        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()

    def restart_deployment(self, name, namespace="default"):
        if self.simulation_mode:
            return f"[SIMULATE] Would restart deployment '{name}' in namespace '{namespace}'."
        try:
            now = datetime.datetime.utcnow().isoformat()
            patch = {
                "spec": {
                    "template": {
                        "metadata": {
                            "annotations": {
                                "kubectl.kubernetes.io/restartedAt": now
                            }
                        }
                    }
                }
            }
            self.apps_v1.patch_namespaced_deployment(name, namespace, patch)
            return f"Deployment '{name}' restarted at {now}."
        except Exception as e:
            return f"Failed to restart deployment: {e}"

    def restart_pod(self, pod_name, namespace="default"):
        if self.simulation_mode:
            return f"[SIMULATE] Would delete pod '{pod_name}' in namespace '{namespace}'."
        try:
            self.core_v1.delete_namespaced_pod(pod_name, namespace)
            return f"Pod '{pod_name}' deleted in namespace '{namespace}'."
        except Exception as e:
            return f"Failed to delete pod: {e}"

    def execute(self, alert: dict):
        action_type = alert.get("type")
        namespace = alert.get("namespace", "default")
        if action_type == "restart_k8s":
            deployment = alert.get("deployment")
            if not deployment:
                return "Missing deployment name."
            return self.restart_deployment(deployment, namespace)
        elif action_type == "restart_pod":
            pod_name = alert.get("pod_name")
            if not pod_name:
                return "Missing pod name."
            return self.restart_pod(pod_name, namespace)
        else:
            return f"Unknown action type: {action_type}"
