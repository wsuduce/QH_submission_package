# PowerShell version of the rebuild script for Windows
# Master rebuild script for all submission packages
# Run this after ANY change to figures or manuscript

param(
    [switch]$Quick = $false
)

# Stop on first error
$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Green
Write-Host "    FULL SUBMISSION REBUILD PIPELINE     " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Get the current directory (should be the base directory)
$BaseDir = Get-Location
Write-Host "Working in: $BaseDir" -ForegroundColor Yellow

Write-Host "Step 1: Checking for updates..." -ForegroundColor Yellow
Write-Host "----------------------------------------"

# Check if figures have been modified
$FiguresModified = $false
$ManifestFile = Join-Path $BaseDir "submissions\BUILD_MANIFEST.json"

if (Test-Path $ManifestFile) {
    $ManifestTime = (Get-Item $ManifestFile).LastWriteTime
    
    # Check figures
    $FigureFiles = Get-ChildItem -Path "artifacts\figures\*.pdf" -ErrorAction SilentlyContinue
    foreach ($Fig in $FigureFiles) {
        if ($Fig.LastWriteTime -gt $ManifestTime) {
            Write-Host "⚠️ Figure modified: $($Fig.Name)" -ForegroundColor Yellow
            $FiguresModified = $true
        }
    }
    
    # Check manuscript
    $ManuscriptFile = "manuscript\QH_Paper_V2_REVIEWER_READY.md"
    if (Test-Path $ManuscriptFile) {
        $ManuscriptTime = (Get-Item $ManuscriptFile).LastWriteTime
        if ($ManuscriptTime -gt $ManifestTime) {
            Write-Host "⚠️ Manuscript has been modified" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "ℹ️ No previous build manifest found" -ForegroundColor Cyan
    $FiguresModified = $true
}

Write-Host ""
Write-Host "Step 2: Using corrected figures..." -ForegroundColor Yellow
Write-Host "----------------------------------------"

# Check if we have the fixed figure
$FixedFigure = "artifacts\figures\fig2_beta_over_alpha_to_k_FIXED.pdf"
$CurrentFigure = "artifacts\figures\fig2_beta_over_alpha_to_k.pdf"

if (Test-Path $FixedFigure) {
    if (-not (Test-Path $CurrentFigure) -or (Get-Item $FixedFigure).LastWriteTime -gt (Get-Item $CurrentFigure).LastWriteTime) {
        Write-Host "📊 Using corrected Figure 2 with log-y scale" -ForegroundColor Green
        # Copy the fixed version to the main version
        Copy-Item $FixedFigure $CurrentFigure -Force
        Write-Host "✅ Updated fig2_beta_over_alpha_to_k.pdf with corrected version"
    }
}

Write-Host ""
Write-Host "Step 3: Building submission packages..." -ForegroundColor Yellow
Write-Host "----------------------------------------"

# Run the main builder
try {
    python submissions\build_submissions.py
    Write-Host "✅ Submission builder completed" -ForegroundColor Green
} catch {
    Write-Host "❌ Submission builder failed: $_" -ForegroundColor Red
    exit 1
}

if (-not $Quick) {
    Write-Host ""
    Write-Host "Step 4: Testing PDF compilation..." -ForegroundColor Yellow
    Write-Host "----------------------------------------"

    # Test compile each package
    $Packages = @("PRD_submission", "JCAP_submission", "arXiv_package")
    
    foreach ($Package in $Packages) {
        $PackageDir = Join-Path "submissions" $Package
        if (Test-Path $PackageDir) {
            Write-Host "Testing $Package..." -ForegroundColor Cyan
            Push-Location $PackageDir
            
            try {
                # Try to compile with pdflatex (with timeout equivalent)
                $Process = Start-Process -FilePath "pdflatex" -ArgumentList "-interaction=nonstopmode", "main.tex" -NoNewWindow -PassThru -Wait
                
                if ($Process.ExitCode -eq 0 -and (Test-Path "main.pdf")) {
                    Write-Host "✅ $Package compiles successfully" -ForegroundColor Green
                    
                    # Get PDF size for verification
                    $PdfSize = (Get-Item "main.pdf").Length
                    Write-Host "   PDF size: $([math]::Round($PdfSize/1KB, 1)) KB"
                } else {
                    Write-Host "❌ $Package compilation failed" -ForegroundColor Red
                }
            } catch {
                Write-Host "⚠️ $Package compilation error: $_" -ForegroundColor Yellow
            } finally {
                Pop-Location
            }
        } else {
            Write-Host "⚠️ $Package directory not found" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "Step 5: Validation checklist..." -ForegroundColor Yellow
Write-Host "----------------------------------------"

# Check critical files exist
$MissingFiles = @()
$CriticalFiles = @(
    "submissions\PRD_submission\main.tex",
    "submissions\JCAP_submission\main.tex", 
    "submissions\arXiv_package\main.tex",
    "submissions\arXiv_package\main.bbl"
)

foreach ($File in $CriticalFiles) {
    if (-not (Test-Path $File)) {
        $MissingFiles += $File
    }
}

if ($MissingFiles.Count -eq 0) {
    Write-Host "✅ All critical files present" -ForegroundColor Green
} else {
    Write-Host "❌ Missing files:" -ForegroundColor Red
    foreach ($File in $MissingFiles) {
        Write-Host "   - $File" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "    BUILD COMPLETE!                      " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Review the generated PDFs in each submission folder"
Write-Host "2. Check figure quality (especially Figure 2 with log-y)"
Write-Host "3. Verify captions match the figures"
Write-Host "4. Run 'git diff' to see all changes"
Write-Host "5. When satisfied, proceed with submission"
Write-Host ""
Write-Host "Submission folders ready at:"
Write-Host "  📁 submissions\PRD_submission\"
Write-Host "  📁 submissions\JCAP_submission\"
Write-Host "  📁 submissions\arXiv_package\"
Write-Host ""
Write-Host "To rebuild after any change, just run:"
Write-Host "  .\REBUILD_ALL.ps1"
Write-Host "  .\REBUILD_ALL.ps1 -Quick  # Skip PDF compilation tests"
Write-Host ""

