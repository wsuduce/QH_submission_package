#!/bin/bash
# Master rebuild script for all submission packages
# Run this after ANY change to figures or manuscript

set -e  # Exit on error

echo "=========================================="
echo "    FULL SUBMISSION REBUILD PIPELINE     "
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base directory
BASE_DIR="/mnt/c/Business - Orginizations/QH/SubmissionPackage Scale Constant/QH_submission_package"
cd "$BASE_DIR"

echo -e "${YELLOW}Step 1: Checking for updates...${NC}"
echo "----------------------------------------"

# Check if figures have been modified
FIGURES_MODIFIED=false
for fig in artifacts/figures/*.pdf; do
    if [ "$fig" -nt "submissions/BUILD_MANIFEST.json" ]; then
        echo -e "${YELLOW}⚠ Figure modified: $(basename $fig)${NC}"
        FIGURES_MODIFIED=true
    fi
done

# Check if manuscript has been modified  
if [ "manuscript/QH_Paper_V2_REVIEWER_READY.md" -nt "submissions/BUILD_MANIFEST.json" ]; then
    echo -e "${YELLOW}⚠ Manuscript has been modified${NC}"
fi

echo ""
echo -e "${YELLOW}Step 2: Regenerating figures if needed...${NC}"
echo "----------------------------------------"

if [ "$FIGURES_MODIFIED" = true ]; then
    echo "Figures have been modified - using updated versions"
    # Skip Python figure generation due to numpy compatibility issues
    # Figures should be generated separately using gnuplot script
fi

echo ""
echo -e "${YELLOW}Step 3: Building submission packages...${NC}"
echo "----------------------------------------"

# Run the main builder
python3 submissions/build_submissions.py

echo ""
echo -e "${YELLOW}Step 4: Compiling test PDFs...${NC}"
echo "----------------------------------------"

# Test compile each package
for package in PRD_submission JCAP_submission arXiv_package; do
    echo -e "Testing $package..."
    cd "submissions/$package"
    
    if timeout 30 pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $package compiles successfully${NC}"
    else
        echo -e "${RED}❌ $package compilation failed${NC}"
    fi
    
    cd "$BASE_DIR"
done

echo ""
echo -e "${YELLOW}Step 5: Validation checklist...${NC}"
echo "----------------------------------------"

# Check critical files exist
MISSING_FILES=()

for file in "submissions/PRD_submission/main.tex" \
           "submissions/JCAP_submission/main.tex" \
           "submissions/arXiv_package/main.tex" \
           "submissions/arXiv_package/main.bbl"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All critical files present${NC}"
else
    echo -e "${RED}❌ Missing files:${NC}"
    for file in "${MISSING_FILES[@]}"; do
        echo "   - $file"
    done
fi

echo ""
echo "=========================================="
echo -e "${GREEN}    BUILD COMPLETE!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review the generated PDFs in each submission folder"
echo "2. Check figure quality (especially Figure 2 with log-y)"
echo "3. Verify captions match the figures"
echo "4. Run 'git diff' to see all changes"
echo "5. When satisfied, proceed with submission"
echo ""
echo "Submission folders ready at:"
echo "  📁 submissions/PRD_submission/"
echo "  📁 submissions/JCAP_submission/"
echo "  📁 submissions/arXiv_package/"
echo ""
echo "To rebuild after any change, just run:"
echo "  ./REBUILD_ALL.sh"
echo ""