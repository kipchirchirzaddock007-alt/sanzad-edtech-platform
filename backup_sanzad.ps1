# backup_sanzad.ps1
# Automatic backup script for SANZAD project

# 1. SOURCE: your main SANZAD project folder
$src = "C:\Users\ADMIN\OneDrive\Desktop\sanzad_global_dashboard"

# 2. DESTINATION: where backups (zip files) will be stored
$destDir = "C:\Users\ADMIN\Documents\SANZAD_backups"

# 3. Create a timestamp like 20251218_150900
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# 4. Build the backup zip path, e.g. C:\Users\ADMIN\Documents\SANZAD_backups\sanzad_backup_20251218_150900.zip
$zipPath = Join-Path $destDir "sanzad_backup_$timestamp.zip"

# 5. Ensure destination directory exists
if (!(Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir | Out-Null
}

# 6. Create the zip of the entire project folder
Write-Host "Creating backup from $src to $zipPath ..."
Compress-Archive -Path "$src\*" -DestinationPath $zipPath -Force

Write-Host "Backup created successfully at:"
Write-Host $zipPath
