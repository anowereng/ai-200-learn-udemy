# Azure App Service + ACR: Daily Commands

Resource group: `99-b9c51c81-create-and-configure-vnet-peering-in-a`
Web app: `sampan-web`
Registry: `sampan.azurecr.io`
Image: `basic-python`

```powershell
$rg = "99-b9c51c81-create-and-configure-vnet-peering-in-a"
```

## 1. Local environment

Create the virtual environment (only if `.venv` does not exist):

```powershell
python -m venv .venv
```

Start the server (stop it with `Ctrl + C`):

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## 2. Build and push the image to ACR

Run from the folder that contains the `Dockerfile`:

```powershell
az acr build --registry sampan --image basic-python:v1 --file .\Dockerfile .
```

## 3. Auto-build from GitHub (ACR task)

Create a GitHub personal access token with repo access and keep it out of notes and git. Check that it works:

```powershell
$token = "<github-token>"
$headers = @{
    Authorization = "Bearer $token"
    Accept        = "application/vnd.github+json"
}
Invoke-RestMethod -Uri "https://api.github.com/user" -Headers $headers
```

Create the task. Every push to `main` builds an image tagged with the run ID:

```powershell
az acr task create `
  --registry sampan `
  --name ai200-api-build `
  --image "basic-python:{{.Run.ID}}" `
  --context "https://github.com/anowereng/AI200-Learn-Udemy.git#main" `
  --file Dockerfile `
  --git-access-token $token
```

List the tags the task produced:

```powershell
az acr repository show-tags --name sampan --repository basic-python
```

## 4. Point the web app at a new image tag

Registry credentials are already stored in the app settings, so only the image changes:

```powershell
az webapp config container set `
  --name sampan-web `
  --resource-group $rg `
  --container-image-name sampan.azurecr.io/basic-python:cu2
```

## 5. Restart the web app

```powershell
az webapp restart --name sampan-web --resource-group $rg
```

Watch it start:

```powershell
az webapp log tail --name sampan-web --resource-group $rg
```

## 6. Security

- Never save GitHub tokens or the ACR password in notes, chats or repos.
- If a token leaks, delete it in GitHub under Settings, Developer settings, Personal access tokens, then create a new one.
- If the ACR password leaks, run `az acr credential renew --name sampan --password-name password` and update the web app's registry password.

## 7. If the app returns 503

See `acr-image-pull-503-troubleshooting.md`.
