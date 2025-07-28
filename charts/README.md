# Helm Chart

This directory contains Helm charts used to deploy SRE-agent's Action-Executor components into a Kubernetes cluster.

## Add the Helm Repository

First, add the `devops-nirvana` Helm repository:

```bash
helm repo add devops-nirvana https://devops-nirvana.s3.amazonaws.com/helm-charts/
```
Install or Upgrade the Release
Use the following command to install or upgrade the action-executor release:

```bash
helm upgrade --install \
  action-executor \
  devops-nirvana/deployment \
  -n agent \
  --create-namespace \
  -f ./values.yaml \
  --wait --timeout 10m --atomic
```

## Explanation of Flags
`--install` — Installs the release if it doesn't already exist.

`-n agent` — Installs into the agent namespace.

`--create-namespace` — Creates the namespace if it doesn't exist.

`-f ./values.yaml` — Specifies custom values for the deployment.

`--wait` — Waits until all resources are ready before marking the release as successful.

`--timeout` 10m — Sets a 10-minute timeout for the operation.

`--atomic` — Rolls back changes if the installation or upgrade fails.

## Prerequisites
Make sure you have Helm version 3.x or higher installed.