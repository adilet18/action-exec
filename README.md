# Action Executor Service

This microservice is responsible for executing actions as part of the SRE agent system. It provides a REST API to trigger Kubernetes operations such as restarting deployments or pods.

---

## Features
- **Restart Kubernetes Deployments** via API
- **Restart Kubernetes Pods** via API
- **Simulation Mode** for safe dry-runs
- **Health Check Endpoint**

---
  
## Requirements
- Python 3.9+
- Access to a Kubernetes cluster (via kubeconfig or in-cluster service account)
- [Poetry](https://python-poetry.org/) for dependency management

---

## Setup

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd action-executor-service
   ```

2. **Install dependencies:**
   ```sh
   poetry install
   ```

3. **Set up Kubernetes credentials:**
   - **Locally:** Ensure your kubeconfig is at `~/.kube/config` or set the `KUBECONFIG` environment variable.
   - **In Kubernetes:** Deploy with a service account that has the necessary RBAC permissions (see below).

4. **Run the service:**
   ```sh
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

---

## Docker

Build and run with Docker:
```sh
# Build the image
docker build -t action-executor-service .

# Run the container (mount kubeconfig if running locally)
docker run -p 8000:8000 -v ~/.kube/config:/home/appuser/.kube/config:ro action-executor-service
```

---

## API Endpoints

### Health Check
- **GET** `/api/v1/healthz`
  - Returns: `{ "status": "ok" }`

### Execute Action
- **POST** `/api/v1/action/execute`
  - **Request Body:**
    ```json
    {
      "type": "restart_k8s", // or "restart_pod"
      "parameters": {
        "deployment": "my-deployment", // for restart_k8s
        "pod_name": "my-pod-123",     // for restart_pod
        "namespace": "default"        // optional, default is "default"
      },
      "simulate": true // optional, default is true
    }
    ```
  - **Response:**
    ```json
    { "result": "Deployment 'my-deployment' restarted at 2024-07-17T12:34:56.789Z." }
    ```

---

## Supported Actions
- `restart_k8s`: Restart a deployment by patching its pod template annotation.
- `restart_pod`: Delete a pod (it will be recreated by its controller).

---

## Security & Permissions
- **Kubernetes Access:** The service uses either a kubeconfig file or in-cluster service account.
- **RBAC:** The service account or user must have permissions to patch deployments and delete pods. Example RBAC:
  ```yaml
  apiVersion: rbac.authorization.k8s.io/v1
  kind: Role
  metadata:
    name: restart-role
    namespace: default
  rules:
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "patch"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "delete"]
  ```
- **API Security:** Protect the API endpoints (e.g., with API keys, authentication middleware) in production.

---

## Development & Testing
- Run tests with:
  ```sh
  poetry run pytest
  ```

---

## Troubleshooting
- **Kubernetes authentication failed:** Ensure kubeconfig or service account is present and valid.
- **RBAC errors:** Check the service account/user has the correct permissions.
- **API errors:** Check logs for stack traces and error messages.

---

## License
MIT 

---

## Kubernetes Deployment

This service is designed to be deployed as a pod in your Kubernetes cluster. Helm charts are provided in the `charts/` directory to simplify deployment.

See [charts/README.md](charts/README.md) for detailed instructions and useful Helm commands to deploy or upgrade the Action Executor Service in your cluster.

--- 

## Swagger UI Usage

This service exposes a Swagger UI for interacting with its API endpoints, including the ability to run arbitrary Kubernetes commands (if enabled and approved).

![Diagram showing API flow](../images/image.png)


## API Endpoints

> GET `/healthz`
> Checks if the service is alive and responsive. Useful for liveness/readiness probes.

> ⚠️ **Use with Caution**  
> POST `/exec` endpoint allows shell command execution and should be tightly controlled  
> (e.g., internal use only, behind authentication/proxy layers).

> GET `/`
> Returns a welcome message (useful for testing connectivity).


---

### Executing a Kubernetes Command

1. Open the Swagger UI in your browser:

> http://localhost:8000/docs

2. Scroll down to:
POST /exec


3. Set the `approve` parameter to `true`.

> ℹ️ **About `approve`:**  
> This flag is required to execute potentially dangerous or state-changing commands (e.g., deleting pods, scaling deployments, modifying resources).  
> If the `approve` parameter is not set to `true`, the request will be blocked to prevent accidental or malicious execution.  
>  
> This serves as a safeguard to avoid unintended disruptions in production environments. Use this with extreme caution and only when you are confident in the command being run.

4. In the **Request Body**, provide a valid Kubernetes command. Example:
```json
{
  "command": "kubectl delete po nginx-ingress-nginx-controller-b95ccb4b5-5g7hp -n nginx-ingress"
}
```

5. Click "Execute".