# Azure Deployment Script for AI Study Helper
# This script deploys the application to Azure App Service

param(
    [string]$ResourceGroupName = "ai-study-helper-rg",
    [string]$AppServiceName = "ai-study-helper-app",
    [string]$Location = "East US",
    [string]$SubscriptionId = ""
)

Write-Host "🚀 Starting Azure deployment for AI Study Helper..." -ForegroundColor Green

# Check if Azure CLI is installed
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Host "✅ Azure CLI version: $($azVersion.'azure-cli')" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI not found. Please install Azure CLI first." -ForegroundColor Red
    Write-Host "Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Login to Azure
Write-Host "🔐 Logging into Azure..." -ForegroundColor Yellow
az login

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to login to Azure" -ForegroundColor Red
    exit 1
}

# Set subscription if provided
if ($SubscriptionId) {
    Write-Host "📋 Setting subscription to: $SubscriptionId" -ForegroundColor Yellow
    az account set --subscription $SubscriptionId
}

# Get current subscription
$currentSub = az account show --query "name" --output tsv
Write-Host "📋 Current subscription: $currentSub" -ForegroundColor Green

# Create resource group
Write-Host "🏗️ Creating resource group: $ResourceGroupName" -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location

# Create App Service plan
Write-Host "📋 Creating App Service plan..." -ForegroundColor Yellow
az appservice plan create --name "$AppServiceName-plan" --resource-group $ResourceGroupName --sku B1 --is-linux

# Create web app
Write-Host "🌐 Creating web app: $AppServiceName" -ForegroundColor Yellow
az webapp create --resource-group $ResourceGroupName --plan "$AppServiceName-plan" --name $AppServiceName --runtime "PYTHON:3.12"

# Configure the web app
Write-Host "⚙️ Configuring web app..." -ForegroundColor Yellow
az webapp config set --resource-group $ResourceGroupName --name $AppServiceName --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app:app"

# Set environment variables
Write-Host "🔧 Setting environment variables..." -ForegroundColor Yellow
az webapp config appsettings set --resource-group $ResourceGroupName --name $AppServiceName --settings WEBSITES_ENABLE_APP_SERVICE_STORAGE=true

# Deploy the application
Write-Host "📦 Deploying application..." -ForegroundColor Yellow
az webapp deployment source config-local-git --resource-group $ResourceGroupName --name $AppServiceName

# Get the deployment URL
$deploymentUrl = az webapp deployment list-publishing-credentials --resource-group $ResourceGroupName --name $AppServiceName --query "scmUri" --output tsv
Write-Host "🔗 Deployment URL: $deploymentUrl" -ForegroundColor Green

# Get the web app URL
$webAppUrl = az webapp show --resource-group $ResourceGroupName --name $AppServiceName --query "defaultHostName" --output tsv
Write-Host "🌐 Web App URL: https://$webAppUrl" -ForegroundColor Green

Write-Host "✅ Azure deployment completed successfully!" -ForegroundColor Green
Write-Host "📱 Your AI Study Helper is now available at: https://$webAppUrl" -ForegroundColor Cyan
Write-Host "🔧 To manage your app, visit: https://portal.azure.com" -ForegroundColor Cyan
