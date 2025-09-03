#!/usr/bin/env python3
"""
Notebook Smoke Test Runner for QH Project CI.

This script runs all notebooks with papermill to ensure they execute 
without errors using real data dependencies.

Usage:
    python scripts/run_notebooks_smoke.py [--timeout 300]
"""

import argparse
import subprocess
import sys
import pathlib
import time
from typing import List, Dict


def run_notebook_smoke(notebook_path: pathlib.Path, output_path: pathlib.Path, 
                      parameters: Dict[str, str] = None, timeout: int = 300) -> bool:
    """
    Run a single notebook with papermill.
    
    Args:
        notebook_path: Input notebook path
        output_path: Output notebook path  
        parameters: Parameters to inject
        timeout: Max execution time in seconds
        
    Returns:
        True if successful, False if failed
    """
    cmd = [
        sys.executable, "-m", "papermill", 
        str(notebook_path), 
        str(output_path),
        "--request-save-on-cell-execute"
    ]
    
    # Add parameters if provided
    if parameters:
        for key, value in parameters.items():
            cmd.extend(["-p", key, value])
    
    print(f"🧪 Running smoke test: {notebook_path.name}")
    print(f"   Command: {' '.join(cmd[3:])}")  # Hide python path for cleaner output
    
    try:
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"   ✅ PASS ({elapsed:.1f}s)")
            return True
        else:
            print(f"   ❌ FAIL ({elapsed:.1f}s)")
            print(f"   Error: {result.stderr}")
            if result.stdout:
                print(f"   Output: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ⏰ TIMEOUT ({timeout}s)")
        return False
    except Exception as e:
        print(f"   💥 EXCEPTION: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Run notebook smoke tests')
    parser.add_argument("--timeout", type=int, default=300,
                       help="Timeout per notebook in seconds")
    parser.add_argument("--output-dir", default="artifacts/checks/notebooks",
                       help="Output directory for executed notebooks")
    args = parser.parse_args()
    
    # Define notebooks and their parameters
    notebooks_config = [
        {
            "path": "notebooks/mcmc_k_equals_c_beta_over_alpha.ipynb",
            "parameters": {
                "DATA_CSV": "data/midis_f560w_masslim.csv"
            }
        },
        {
            "path": "notebooks/gw_delta_constraint.ipynb", 
            "parameters": {
                "GW_SUMMARY": "data/gw150914_summary.csv"
            }
        },
        {
            "path": "notebooks/eht_delta_constraint.ipynb",
            "parameters": {
                "EHT_PRIORS": "data/eht_priors.json"  
            }
        },
        {
            "path": "notebooks/hierarchical_delta.ipynb",
            "parameters": {}  # Add parameters if needed
        },
        {
            "path": "notebooks/predictions_calculator.ipynb", 
            "parameters": {}  # Add parameters if needed
        }
    ]
    
    # Create output directory
    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check data dependencies first
    required_data_files = [
        "data/midis_f560w_masslim.csv",
        "data/gw150914_summary.csv", 
        "data/eht_priors.json"
    ]
    
    print("🔍 Checking data dependencies...")
    missing_files = []
    for data_file in required_data_files:
        if not pathlib.Path(data_file).exists():
            missing_files.append(data_file)
            print(f"   ❌ Missing: {data_file}")
        else:
            print(f"   ✅ Found: {data_file}")
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} required data files!")
        print("   Run the appropriate extraction scripts first:")
        for f in missing_files:
            if "gw150914" in f:
                print("   python scripts/ligo_gw150914_extract.py --posterior <file> --out data/gw150914_summary.csv")
            elif "eht_priors" in f:
                print("   python scripts/eht_extract.py --out data/eht_priors.json")
        sys.exit(1)
    
    # Run notebook tests
    print(f"\n🧪 Running {len(notebooks_config)} notebook smoke tests...")
    results = []
    
    for config in notebooks_config:
        notebook_path = pathlib.Path(config["path"])
        
        if not notebook_path.exists():
            print(f"⚠️  Skipping missing notebook: {notebook_path}")
            results.append(False)
            continue
            
        output_path = output_dir / f"{notebook_path.stem}_smoke.ipynb"
        
        success = run_notebook_smoke(
            notebook_path, 
            output_path, 
            config.get("parameters"),
            args.timeout
        )
        results.append(success)
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Smoke Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 ALL NOTEBOOKS PASSED - Ready for PR!")
        sys.exit(0)
    else:
        print(f"💥 {total - passed} NOTEBOOKS FAILED - Fix before PR!")
        sys.exit(1)


if __name__ == "__main__":
    main()
