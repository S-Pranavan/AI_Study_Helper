# Azure Deployment Guide for AI Study Helper

This guide will help you deploy the AI Study Helper application to Azure App Service.

## Prerequisites

1. **Azure Account**: You need an Azure account with an active subscription
2. **Azure CLI**: Install Azure CLI from [Microsoft's official site](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
3. **Git**: Ensure Git is installed and configured
4. **Python 3.12**: The application requires Python 3.12

## Quick Deployment (Automated)

### Option 1: GitHub Actions (Recommended)

1. **Fork/Clone the Repository**
   ```bash
   git clone https://github.com/S-Pranavan/AI_Study_Helper.git
   cd AI_Study_Helper
   ```

2. **Set up GitHub Secrets**
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Add a new secret: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - Get the publish profile from Azure Portal → Your App Service → Get publish profile

3. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Azure deployment configuration"
   git push origin main
   ```

4. **Monitor Deployment**
   - Go to Actions tab in your GitHub repository
   - The deployment will start automatically

### Option 2: Manual Azure CLI Deployment

1. **Login to Azure**
   ```bash
   az login
   ```

2. **Run the Deployment Script**
   ```bash
   # For Windows PowerShell
   .\deploy-to-azure.ps1
   
   # For Linux/Mac
   bash deploy-to-azure.sh
   ```

## Manual Deployment Steps

### 1. Create Azure Resources

```bash
# Set your variables
RESOURCE_GROUP="ai-study-helper-rg"
APP_SERVICE_NAME="ai-study-helper-app"
LOCATION="East US"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create App Service plan
az appservice plan create --name "$APP_SERVICE_NAME-plan" --resource-group $RESOURCE_GROUP --sku B1 --is-linux

# Create web app
az webapp create --resource-group $RESOURCE_GROUP --plan "$APP_SERVICE_NAME-plan" --name $APP_SERVICE_NAME --runtime "PYTHON:3.12"
```

### 2. Configure the Web App

```bash
# Set startup command
az webapp config set --resource-group $RESOURCE_GROUP --name $APP_SERVICE_NAME --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 startup:app"

# Set environment variables
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_SERVICE_NAME --settings WEBSITES_ENABLE_APP_SERVICE_STORAGE=true

# Enable local Git deployment
az webapp deployment source config-local-git --resource-group $RESOURCE_GROUP --name $APP_SERVICE_NAME
```

### 3. Deploy the Application

```bash
# Get deployment URL
DEPLOYMENT_URL=$(az webapp deployment list-publishing-credentials --resource-group $RESOURCE_GROUP --name $APP_SERVICE_NAME --query "scmUri" --output tsv)

# Add Azure remote
git remote add azure $DEPLOYMENT_URL

# Deploy
git push azure main
```

## Testing the Deployment

### 1. Test with Playwright

```bash
# Install Playwright
pip install playwright
playwright install

# Run Azure deployment test
python test_azure_deployment.py
```

### 2. Manual Testing

1. Open your Azure web app URL
2. Test the "Start OCR" button
3. Verify OCR functionality works
4. Test navigation between pages

## Configuration Files

- `azure-deploy.yml` - GitHub Actions workflow
- `deploy-to-azure.ps1` - PowerShell deployment script
- `requirements-azure.txt` - Production dependencies
- `startup.py` - Azure startup script
- `test_azure_deployment.py` - Playwright test for Azure

## Troubleshooting

### Common Issues

1. **Port Configuration**: Ensure the app listens on `0.0.0.0` and uses `PORT` environment variable
2. **Dependencies**: Check that all requirements are in `requirements-azure.txt`
3. **Startup Command**: Verify the startup command in Azure App Service configuration
4. **Python Version**: Ensure Azure App Service is configured for Python 3.12

### Logs

```bash
# View application logs
az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_SERVICE_NAME

# Download logs
az webapp log download --resource-group $RESOURCE_GROUP --name $APP_SERVICE_NAME
```

## Cost Optimization

- Use **B1** App Service Plan for development/testing
- Consider **F1** (Free) for initial testing
- Scale up to **P1V2** or **P2V2** for production

## Security Considerations

1. **Environment Variables**: Store sensitive data in Azure App Service Configuration
2. **HTTPS**: Azure provides free SSL certificates
3. **Authentication**: Consider adding Azure AD authentication
4. **Network Security**: Use Azure Front Door for additional security layers

## Support

For issues with:
- **Azure**: Check Azure documentation and support
- **Application**: Check the application logs and GitHub issues
- **Deployment**: Verify all prerequisites and configuration steps

## Next Steps

After successful deployment:
1. Set up custom domain (optional)
2. Configure monitoring and alerts
3. Set up CI/CD pipeline
4. Implement backup strategies
5. Add performance monitoring
