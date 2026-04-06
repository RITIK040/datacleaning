# Cleanup Git Script
# This will remove the .git directory and common git metadata files.

$gitFiles = @(".git", ".gitignore", ".gitattributes", ".gitmodules", ".github")

foreach ($file in $gitFiles) {
    if (Test-Path $file) {
        Write-Host "Removing $file..." -ForegroundColor Yellow
        Remove-Item -Path $file -Recurse -Force
        Write-Host "Successfully removed $file." -ForegroundColor Green
    } else {
        Write-Host "$file not found, skipping." -ForegroundColor Gray
    }
}

Write-Host "Git cleanup complete. The project is now 'un-git'-ed." -ForegroundColor Cyan
