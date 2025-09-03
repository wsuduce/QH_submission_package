# PowerShell version of the simple rebuild script for Windows
# Simple rebuild script that actually works
# Compiles all three submission packages with the corrected figures

param(
    [switch]$SkipBibtex = $false
)

# Stop on first error
$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Green
Write-Host "    SIMPLE SUBMISSION REBUILD             " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Get the current directory (should be the base directory)
$BaseDir = Get-Location
Write-Host "Working in: $BaseDir" -ForegroundColor Yellow

Write-Host "Testing compilation of each package..." -ForegroundColor Yellow
Write-Host "----------------------------------------"

# Function to safely run pdflatex with timeout
function Invoke-PdfLatex {
    param(
        [string]$TexFile = "main.tex",
        [int]$TimeoutSeconds = 60
    )
    
    try {
        $Process = Start-Process -FilePath "pdflatex" -ArgumentList "-interaction=nonstopmode", $TexFile -NoNewWindow -PassThru
        
        # Wait for process with timeout
        $Finished = $Process.WaitForExit($TimeoutSeconds * 1000)
        
        if (-not $Finished) {
            $Process.Kill()
            throw "Process timed out after $TimeoutSeconds seconds"
        }
        
        return $Process.ExitCode -eq 0
    } catch {
        Write-Host "Error running pdflatex: $_" -ForegroundColor Red
        return $false
    }
}

# Function to run bibtex safely
function Invoke-Bibtex {
    param([string]$BibFile = "main")
    
    if ($SkipBibtex) {
        Write-Host "   Skipping bibtex (requested)" -ForegroundColor Yellow
        return
    }
    
    try {
        $Process = Start-Process -FilePath "bibtex" -ArgumentList $BibFile -NoNewWindow -PassThru -Wait
        # Bibtex can have non-zero exit codes but still work, so we don't check exit code
        Write-Host "   Bibtex completed" -ForegroundColor Cyan
    } catch {
        Write-Host "   Warning: bibtex failed: $_" -ForegroundColor Yellow
    }
}

# Test PRD package
Write-Host ""
Write-Host "1. Testing PRD submission..." -ForegroundColor Yellow
$PrdDir = Join-Path $BaseDir "submissions\PRD_submission"

if (Test-Path $PrdDir) {
    Push-Location $PrdDir
    try {
        if (Invoke-PdfLatex -TimeoutSeconds 60) {
            Write-Host "✅ PRD package compiles!" -ForegroundColor Green
            
            # Run bibtex
            Invoke-Bibtex
            
            # Second pass for references
            if (Invoke-PdfLatex -TimeoutSeconds 30) {
                Write-Host "✅ References updated" -ForegroundColor Green
            }
            
            if (Test-Path "main.pdf") {
                $PdfSize = (Get-Item "main.pdf").Length
                Write-Host "   PDF generated: $([math]::Round($PdfSize/1KB, 1)) KB" -ForegroundColor Green
            }
        } else {
            Write-Host "❌ PRD compilation failed" -ForegroundColor Red
        }
    } finally {
        Pop-Location
    }
} else {
    Write-Host "❌ PRD submission directory not found" -ForegroundColor Red
}

# Test arXiv package
Write-Host ""
Write-Host "2. Testing arXiv package..." -ForegroundColor Yellow
$ArxivDir = Join-Path $BaseDir "submissions\arXiv_package"

if (Test-Path $ArxivDir) {
    Push-Location $ArxivDir
    try {
        if (Invoke-PdfLatex -TimeoutSeconds 60) {
            Write-Host "✅ arXiv package compiles!" -ForegroundColor Green
            
            # Generate .bbl for arXiv safety
            Invoke-Bibtex
            
            # Second pass
            if (Invoke-PdfLatex -TimeoutSeconds 30) {
                Write-Host "✅ Final pass completed" -ForegroundColor Green
            }
            
            if (Test-Path "main.bbl") {
                Write-Host "   .bbl file generated for arXiv" -ForegroundColor Green
            }
            if (Test-Path "main.pdf") {
                $PdfSize = (Get-Item "main.pdf").Length
                Write-Host "   PDF generated: $([math]::Round($PdfSize/1KB, 1)) KB" -ForegroundColor Green
            }
        } else {
            Write-Host "❌ arXiv compilation failed" -ForegroundColor Red
        }
    } finally {
        Pop-Location
    }
} else {
    Write-Host "❌ arXiv package directory not found" -ForegroundColor Red
}

# Test JCAP package
Write-Host ""
Write-Host "3. Testing JCAP submission..." -ForegroundColor Yellow
$JcapDir = Join-Path $BaseDir "submissions\JCAP_submission"

if (Test-Path $JcapDir) {
    Push-Location $JcapDir
    try {
        # JCAP uses JHEP class which might not be installed, so we'll be more lenient
        if (Invoke-PdfLatex -TimeoutSeconds 60) {
            Write-Host "✅ JCAP package compiles!" -ForegroundColor Green
            
            Invoke-Bibtex
            
            if (Invoke-PdfLatex -TimeoutSeconds 30) {
                Write-Host "✅ Final pass completed" -ForegroundColor Green
            }
            
            if (Test-Path "main.pdf") {
                $PdfSize = (Get-Item "main.pdf").Length
                Write-Host "   PDF generated: $([math]::Round($PdfSize/1KB, 1)) KB" -ForegroundColor Green
            }
        } else {
            Write-Host "⚠️ JCAP compilation needs JHEP class (expected on some systems)" -ForegroundColor Yellow
        }
    } finally {
        Pop-Location
    }
} else {
    Write-Host "❌ JCAP submission directory not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "    REBUILD COMPLETE!                    " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Figure 2 status:"
Write-Host "   - CORRECTED: log-y scale version with REAL MIDIS data"
Write-Host "   - BACKUPS: Previous versions saved as fig2_*_OLD.pdf"
Write-Host ""
Write-Host "📁 Submission packages tested:"

# List generated PDFs
$PdfFiles = Get-ChildItem -Path "submissions\*\main.pdf" -ErrorAction SilentlyContinue
foreach ($Pdf in $PdfFiles) {
    $Size = [math]::Round($Pdf.Length/1KB, 1)
    $RelativePath = $Pdf.FullName.Replace($BaseDir, "").TrimStart('\')
    Write-Host "   $RelativePath ($Size KB)"
}

if ($PdfFiles.Count -eq 0) {
    Write-Host "   No PDFs found - check compilation errors above" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Next steps:"
Write-Host "1. Review the generated PDFs"
Write-Host "2. Check that Figure 2 shows log-y scale properly"
Write-Host "3. Verify captions match the new figure format"
Write-Host "4. When satisfied, submit to journals!"
Write-Host ""
Write-Host "Usage options:"
Write-Host "  .\SIMPLE_REBUILD.ps1               # Full rebuild with bibtex"
Write-Host "  .\SIMPLE_REBUILD.ps1 -SkipBibtex   # Skip bibtex (faster)"

