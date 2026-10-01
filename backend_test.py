#!/usr/bin/env python3
"""
Backend Data Persistence Test - Verify NO data wipe across TWO backend restarts
Tests that the Kukdi backend preserves 4 stories and 14 companies across restarts.
"""

import requests
import subprocess
import time
import sys
from typing import Dict, List, Any

# Backend URL from frontend/.env
BASE_URL = "https://github-alive.preview.emergentagent.com/api"

def log(message: str, level: str = "INFO"):
    """Print formatted log message"""
    print(f"[{level}] {message}")

def get_stories() -> Dict[str, Any]:
    """Get all stories and return count + titles"""
    try:
        response = requests.get(f"{BASE_URL}/stories", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Handle both {"stories": [...]} and [...] formats
        if isinstance(data, dict) and "stories" in data:
            stories = data["stories"]
        else:
            stories = data
        
        # Verify no _id leaks
        for story in stories:
            if "_id" in story:
                log(f"❌ CRITICAL: _id leak detected in story: {story.get('title', 'unknown')}", "ERROR")
                return {"error": "_id leak detected"}
        
        titles = [s.get("title", "") for s in stories]
        return {
            "count": len(stories),
            "titles": sorted(titles),  # Sort for consistent comparison
            "raw": stories
        }
    except Exception as e:
        log(f"❌ Failed to get stories: {e}", "ERROR")
        return {"error": str(e)}

def get_companies_count() -> Dict[str, Any]:
    """Get company count from dream overview"""
    try:
        response = requests.get(f"{BASE_URL}/dream/overview", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Verify no _id leaks in companies
        companies = data.get("companies", [])
        for company in companies:
            if "_id" in company:
                log(f"❌ CRITICAL: _id leak detected in company: {company.get('name', 'unknown')}", "ERROR")
                return {"error": "_id leak detected"}
        
        return {
            "count": len(companies),
            "companies": companies
        }
    except Exception as e:
        log(f"❌ Failed to get companies: {e}", "ERROR")
        return {"error": str(e)}

def restart_backend():
    """Restart backend service via supervisorctl"""
    try:
        log("Restarting backend service...", "INFO")
        result = subprocess.run(
            ["sudo", "supervisorctl", "restart", "backend"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            log(f"❌ Backend restart failed: {result.stderr}", "ERROR")
            return False
        log(f"✅ Backend restart command executed: {result.stdout.strip()}", "INFO")
        return True
    except Exception as e:
        log(f"❌ Failed to restart backend: {e}", "ERROR")
        return False

def wait_for_backend(timeout: int = 15):
    """Wait for backend to be ready"""
    log(f"Waiting up to {timeout}s for backend to be ready...", "INFO")
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(f"{BASE_URL}/dream/overview", timeout=5)
            if response.status_code == 200:
                elapsed = time.time() - start
                log(f"✅ Backend ready after {elapsed:.1f}s", "INFO")
                return True
        except:
            pass
        time.sleep(1)
    log(f"❌ Backend not ready after {timeout}s", "ERROR")
    return False

def verify_data_integrity(baseline: Dict, current: Dict, stage: str) -> bool:
    """Verify data matches baseline (no wipes, no duplicates)"""
    log(f"\n{'='*60}", "INFO")
    log(f"VERIFICATION STAGE: {stage}", "INFO")
    log(f"{'='*60}", "INFO")
    
    all_passed = True
    
    # Check stories
    baseline_stories = baseline.get("stories", {})
    current_stories = current.get("stories", {})
    
    if "error" in baseline_stories or "error" in current_stories:
        log(f"❌ Error in stories data", "ERROR")
        all_passed = False
    else:
        baseline_count = baseline_stories.get("count", 0)
        current_count = current_stories.get("count", 0)
        baseline_titles = baseline_stories.get("titles", [])
        current_titles = current_stories.get("titles", [])
        
        log(f"\nSTORIES CHECK:", "INFO")
        log(f"  Baseline count: {baseline_count}", "INFO")
        log(f"  Current count:  {current_count}", "INFO")
        
        if current_count != 4:
            log(f"  ❌ FAIL: Expected EXACTLY 4 stories, got {current_count}", "ERROR")
            all_passed = False
        elif current_count != baseline_count:
            log(f"  ❌ FAIL: Story count changed from {baseline_count} to {current_count}", "ERROR")
            all_passed = False
        else:
            log(f"  ✅ PASS: Story count stable at {current_count}", "INFO")
        
        # Check for duplicates by comparing titles
        if len(current_titles) != len(set(current_titles)):
            log(f"  ❌ FAIL: DUPLICATE stories detected!", "ERROR")
            log(f"  Titles: {current_titles}", "ERROR")
            all_passed = False
        else:
            log(f"  ✅ PASS: No duplicate stories", "INFO")
        
        # Check titles match
        if sorted(baseline_titles) != sorted(current_titles):
            log(f"  ❌ FAIL: Story titles changed!", "ERROR")
            log(f"  Baseline: {baseline_titles}", "ERROR")
            log(f"  Current:  {current_titles}", "ERROR")
            all_passed = False
        else:
            log(f"  ✅ PASS: Story titles unchanged", "INFO")
            log(f"  Titles: {current_titles[:2]}... (showing first 2)", "INFO")
    
    # Check companies
    baseline_companies = baseline.get("companies", {})
    current_companies = current.get("companies", {})
    
    if "error" in baseline_companies or "error" in current_companies:
        log(f"❌ Error in companies data", "ERROR")
        all_passed = False
    else:
        baseline_count = baseline_companies.get("count", 0)
        current_count = current_companies.get("count", 0)
        
        log(f"\nCOMPANIES CHECK:", "INFO")
        log(f"  Baseline count: {baseline_count}", "INFO")
        log(f"  Current count:  {current_count}", "INFO")
        
        if current_count != 14:
            log(f"  ❌ FAIL: Expected EXACTLY 14 companies, got {current_count}", "ERROR")
            all_passed = False
        elif current_count != baseline_count:
            log(f"  ❌ FAIL: Company count changed from {baseline_count} to {current_count}", "ERROR")
            all_passed = False
        else:
            log(f"  ✅ PASS: Company count stable at {current_count}", "INFO")
    
    log(f"\n{'='*60}", "INFO")
    if all_passed:
        log(f"✅ {stage}: ALL CHECKS PASSED", "INFO")
    else:
        log(f"❌ {stage}: FAILURES DETECTED", "ERROR")
    log(f"{'='*60}\n", "INFO")
    
    return all_passed

def main():
    """Main test execution"""
    log("\n" + "="*80, "INFO")
    log("KUKDI BACKEND DATA PERSISTENCE TEST - TWO RESTART VERIFICATION", "INFO")
    log("="*80 + "\n", "INFO")
    
    # STEP 1: Record baseline
    log("STEP 1: Recording baseline data...", "INFO")
    baseline = {
        "stories": get_stories(),
        "companies": get_companies_count()
    }
    
    if "error" in baseline["stories"] or "error" in baseline["companies"]:
        log("❌ CRITICAL: Failed to get baseline data", "ERROR")
        sys.exit(1)
    
    log(f"✅ Baseline recorded: {baseline['stories']['count']} stories, {baseline['companies']['count']} companies", "INFO")
    
    # STEP 2: First restart
    log("\n" + "="*80, "INFO")
    log("STEP 2: FIRST BACKEND RESTART", "INFO")
    log("="*80, "INFO")
    
    if not restart_backend():
        log("❌ CRITICAL: First restart failed", "ERROR")
        sys.exit(1)
    
    time.sleep(8)  # Wait for provisioning
    
    if not wait_for_backend():
        log("❌ CRITICAL: Backend not ready after first restart", "ERROR")
        sys.exit(1)
    
    # Check data after first restart
    after_restart_1 = {
        "stories": get_stories(),
        "companies": get_companies_count()
    }
    
    restart_1_passed = verify_data_integrity(baseline, after_restart_1, "AFTER RESTART #1")
    
    # STEP 3: Second restart
    log("\n" + "="*80, "INFO")
    log("STEP 3: SECOND BACKEND RESTART", "INFO")
    log("="*80, "INFO")
    
    if not restart_backend():
        log("❌ CRITICAL: Second restart failed", "ERROR")
        sys.exit(1)
    
    time.sleep(8)  # Wait for provisioning
    
    if not wait_for_backend():
        log("❌ CRITICAL: Backend not ready after second restart", "ERROR")
        sys.exit(1)
    
    # Check data after second restart
    after_restart_2 = {
        "stories": get_stories(),
        "companies": get_companies_count()
    }
    
    restart_2_passed = verify_data_integrity(baseline, after_restart_2, "AFTER RESTART #2")
    
    # FINAL SUMMARY
    log("\n" + "="*80, "INFO")
    log("FINAL SUMMARY - TWO RESTART VERIFICATION", "INFO")
    log("="*80, "INFO")
    
    log(f"\nBaseline:        {baseline['stories']['count']} stories, {baseline['companies']['count']} companies", "INFO")
    log(f"After Restart 1: {after_restart_1['stories']['count']} stories, {after_restart_1['companies']['count']} companies", "INFO")
    log(f"After Restart 2: {after_restart_2['stories']['count']} stories, {after_restart_2['companies']['count']} companies", "INFO")
    
    if restart_1_passed and restart_2_passed:
        log("\n✅ ✅ ✅ PASS: Data preserved across TWO restarts - nothing wiped, nothing duplicated", "INFO")
        log("✅ Stories: EXACTLY 4 with identical unique titles across all three measurements", "INFO")
        log("✅ Companies: EXACTLY 14 across all three measurements", "INFO")
        log("✅ No _id leaks detected", "INFO")
        log("✅ No duplicates detected", "INFO")
        log("\n🎉 BACKEND DATA PERSISTENCE VERIFIED - PRODUCTION READY", "INFO")
        sys.exit(0)
    else:
        log("\n❌ ❌ ❌ FAIL: Data integrity issues detected across restarts", "ERROR")
        if not restart_1_passed:
            log("❌ First restart verification FAILED", "ERROR")
        if not restart_2_passed:
            log("❌ Second restart verification FAILED", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
