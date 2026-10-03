# Troubleshooting: App Service 503 from ACR Image Pull Failure

2026-10-03

A 503 right after changing the container image means App Service could not pull from the private registry. Give it the registry login and the app port, then start the site.

## Cause

`az webapp config container set` with only `--container-image-name` leaves App Service without registry credentials. The private ACR (`sampan.azurecr.io`) rejects the pull with `ImagePullUnauthorizedFailure`, App Service stops the site, and every request returns 503.

## Fix

Uses the ACR admin user, so no managed identity or role assignment is needed.

```powershell
$rg = "99-b9c51c81-create-and-configure-vnet-peering-in-a"

az acr update --name sampan --admin-enabled true
$u = az acr credential show --name sampan --query username -o tsv
$p = az acr credential show --name sampan --query "passwords[0].value" -o tsv

az webapp config container set `
  --name sampan-web --resource-group $rg `
  --container-image-name sampan.azurecr.io/basic-python:v1 `
  --container-registry-url https://sampan.azurecr.io `
  --container-registry-user $u `
  --container-registry-password $p

az webapp config appsettings set --name sampan-web --resource-group $rg --settings WEBSITES_PORT=8080
az webapp start --name sampan-web --resource-group $rg
```

This writes `DOCKER_REGISTRY_SERVER_URL`, `DOCKER_REGISTRY_SERVER_USERNAME`, `DOCKER_REGISTRY_SERVER_PASSWORD` and `WEBSITES_PORT` into the app's environment variables. `az webapp start` is needed because the failed pull leaves the site stopped.

## Managed identity vs admin credentials

Admin credentials fix it fastest. A managed identity with the `AcrPull` role is the safer setup for anything long-lived.

| | ACR admin user | Managed identity + `AcrPull` |
| --- | --- | --- |
| Secret stored | Yes, password in app settings | None |
| Rotation | Manual; renewing breaks the app until updated | Automatic |
| Access level | Push and pull, shared by everyone using it | Pull only |
| Revoke | Renew the password, which affects every user | Remove the role assignment for that app only |
| Audit | Cannot tell callers apart | Role assignments are traceable in Azure |
| Setup | One command | Identity, role assignment, one setting |
| Needs | ACR contributor access | Permission to create role assignments |
| Best for | Labs and quick tests | Production and shared environments |

Switch later, once you have the permission:

```powershell
$principal = az webapp identity assign --name sampan-web --resource-group $rg --query principalId -o tsv
$acrId = az acr show --name sampan --query id -o tsv
az role assignment create --assignee $principal --role AcrPull --scope $acrId
az webapp config set --name sampan-web --resource-group $rg --generic-configurations "{\"acrUseManagedIdentityCreds\": true}"
az acr update --name sampan --admin-enabled false
```

Role assignments can take a minute or two to apply, so restart the app if the first pull still fails.

## Check

```powershell
az webapp log tail --name sampan-web --resource-group $rg
```

Success looks like `Uvicorn running on http://0.0.0.0:8080`, then `Site startup probe succeeded` and `Site started`. Pull and start errors are in `*_docker.log`.

## If it still fails

| Log text | Fix |
| --- | --- |
| `ImagePullUnauthorizedFailure` | Re-run the Fix; check the user and password are the ACR admin values |
| `manifest unknown` | Wrong tag; list with `az acr repository show-tags --name sampan --repository basic-python` |
| "didn't respond to HTTP pings on port" | Set `WEBSITES_PORT` to the port the app prints at startup (8080 here) |
| Site shows `Stopped` | `az webapp start` |

## Security

The password sits in the app's environment variables in plain text. Never paste it into chats or docs. If it leaks, run `az acr credential renew --name sampan --password-name password`, then re-run the `config container set` step with the new value.
