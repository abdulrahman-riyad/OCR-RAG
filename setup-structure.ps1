# PowerShell script to create project directory structure

Write-Host "Creating OCR-RAG Project Directory Structure..." -ForegroundColor Green

# Create main directories
$directories = @(
    "frontend\app\upload",
    "frontend\app\documents\[id]",
    "frontend\app\search",
    "frontend\components\upload",
    "frontend\components\documents",
    "frontend\components\search",
    "frontend\lib",
    "backend\app\api",
    "backend\app\core",
    "backend\app\services",
    "backend\app\models",
    "backend\app\utils",
    "backend\tests",
    "r2r-config",
    "data\uploads",
    "data\processed",
    "data\cache",
    "scripts",
    "docs"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Write-Host "Created: $dir" -ForegroundColor Yellow
}

# Create .gitkeep files in data directories
$gitkeepDirs = @(
    "data\uploads",
    "data\processed",
    "data\cache"
)

foreach ($dir in $gitkeepDirs) {
    New-Item -ItemType File -Force -Path "$dir\.gitkeep" | Out-Null
}

# Create empty __init__.py files for Python packages
$pythonDirs = @(
    "backend\app",
    "backend\app\api",
    "backend\app\core",
    "backend\app\services",
    "backend\app\models",
    "backend\app\utils",
    "backend\tests"
)

foreach ($dir in $pythonDirs) {
    New-Item -ItemType File -Force -Path "$dir\__init__.py" | Out-Null
}

Write-Host "`nDirectory structure created successfully!" -ForegroundColor Green