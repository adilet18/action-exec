from kubernetes import client, config
import datetime
import subprocess
import shlex
import logging

class ActionExecutorAgent:
    def __init__(self, kubeconfig_path=None, simulation_mode=False):
        self.simulation_mode = simulation_mode

        # Load Kubernetes config
        if kubeconfig_path:
            config.load_kube_config(config_file=kubeconfig_path)
        else:
            try:
                config.load_incluster_config()
            except Exception:
                config.load_kube_config()

        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()

        # Logging
        logging.basicConfig(
            filename="action_executor.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        # Dangerous command patterns (regex)
        self.DANGEROUS_PATTERNS = [
            r"kubectl\s+delete\s+--all\b",
            r"kubectl\s+delete\s+all\b",
            r"kubectl\s+delete\s+.*\s+--all\b",
            r"kubectl\s+delete\s+.*\s+-A\b",  # Delete across all namespaces
            r"helm\s+uninstall\s+--all\b",
            r"helm\s+delete\s+--all\b",
            r"helm\s+.*\s+--purge\b"
        ]

    def is_safe_command(self, full_command: str) -> bool:
        """Check against dangerous patterns"""
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, full_command):
                logging.warning(f"Blocked dangerous command: {full_command}")
                return False
        return True

    def execute_command(self, command: str) -> dict:
        """
        Executes either a kubectl or helm command safely.
        """
        if not command.startswith("kubectl ") and not command.startswith("helm "):
            return {"error": "Only 'kubectl' or 'helm' commands are allowed."}

        if not self._is_safe_command(command):
            return {"error": "Command blocked for safety reasons."}

        try:
            args = shlex.split(command)
        except ValueError as e:
            return {"error": f"Failed to parse command: {str(e)}"}

        if self.simulation_mode:
            return {
                "command": command,
                "stdout": f"[SIMULATION] Would run: {command}",
                "stderr": "",
                "exit_code": 0,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }

        try:
            proc = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60
            )

            result = {
                "command": command,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
                "exit_code": proc.returncode,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }

            logging.info(f"Executed command: {command} | Exit code: {proc.returncode}")
            return result

        except subprocess.TimeoutExpired:
            return {"error": "Command timed out."}
        except Exception as e:
            return {"error": f"Execution failed: {str(e)}"}

    def execute(self, alert: dict):
        # Placeholder for alert-based execution
        action_type = alert.get("action_type")
        # You can expand this as needed
        pass