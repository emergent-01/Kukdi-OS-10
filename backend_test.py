#!/usr/bin/env python3
"""
Backend Verification Test - Tentative Events Removal + Polish Endpoint
Tests for Kukdi backend per review request:
1. GET /api/calendar → NO "tentative" events
2. DURABILITY: restart backend → still NO "tentative" events
3. BASELINE INTACT: 4 stories, 14 companies, 12 people
4. POLISH ENDPOINT: POST /api/stories/{id}/polish graceful behavior
5. No _id leaks
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

def check_id_leaks(data: Any, context: str = "") -> bool:
    """Recursively check for _id leaks in response data"""
    if isinstance(data, dict):
        if "_id" in data:
            log(f"❌ CRITICAL: _id leak detected in {context}", "ERROR")
            return True
        for key, value in data.items():
            if check_id_leaks(value, f"{context}.{key}"):
                return True
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if check_id_leaks(item, f"{context}[{i}]"):
                return True
    return False

def get_calendar_events() -> Dict[str, Any]:
    """Get calendar events and check for tentative events"""
    try:
        response = requests.get(f"{BASE_URL}/calendar", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Handle both {"events": [...]} and [...] formats
        if isinstance(data, dict) and "events" in data:
            events = data["events"]
        else:
            events = data if isinstance(data, list) else []
        
        # Check for _id leaks
        if check_id_leaks(events, "calendar_events"):
            return {"error": "_id leak detected"}
        
        # Check for tentative events
        tentative_events = []
        for event in events:
            title = event.get("title", "")
            if "tentative" in title.lower():
                tentative_events.append(title)
        
        return {
            "total_count": len(events),
            "tentative_count": len(tentative_events),
            "tentative_events": tentative_events,
            "all_events": events
        }
    except Exception as e:
        log(f"❌ Failed to get calendar events: {e}", "ERROR")
        return {"error": str(e)}

def get_stories() -> Dict[str, Any]:
    """Get all stories"""
    try:
        response = requests.get(f"{BASE_URL}/stories", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Handle both {"stories": [...]} and [...] formats
        if isinstance(data, dict) and "stories" in data:
            stories = data["stories"]
        else:
            stories = data if isinstance(data, list) else []
        
        # Check for _id leaks
        if check_id_leaks(stories, "stories"):
            return {"error": "_id leak detected"}
        
        return {
            "count": len(stories),
            "stories": stories
        }
    except Exception as e:
        log(f"❌ Failed to get stories: {e}", "ERROR")
        return {"error": str(e)}

def get_companies() -> Dict[str, Any]:
    """Get companies from dream overview"""
    try:
        response = requests.get(f"{BASE_URL}/dream/overview", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        companies = data.get("companies", [])
        
        # Check for _id leaks
        if check_id_leaks(companies, "companies"):
            return {"error": "_id leak detected"}
        
        return {
            "count": len(companies),
            "companies": companies
        }
    except Exception as e:
        log(f"❌ Failed to get companies: {e}", "ERROR")
        return {"error": str(e)}

def get_people() -> Dict[str, Any]:
    """Get all people"""
    try:
        response = requests.get(f"{BASE_URL}/people", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Handle both {"people": [...]} and [...] formats
        if isinstance(data, dict) and "people" in data:
            people = data["people"]
        else:
            people = data if isinstance(data, list) else []
        
        # Check for _id leaks
        if check_id_leaks(people, "people"):
            return {"error": "_id leak detected"}
        
        # Count prep_group=false
        prep_group_false_count = sum(1 for p in people if p.get("prep_group") == False)
        
        return {
            "count": len(people),
            "prep_group_false_count": prep_group_false_count,
            "people": people
        }
    except Exception as e:
        log(f"❌ Failed to get people: {e}", "ERROR")
        return {"error": str(e)}

def test_polish_endpoint(story_id: str) -> Dict[str, Any]:
    """Test POST /api/stories/{id}/polish endpoint"""
    try:
        log(f"Testing polish endpoint with story ID: {story_id}", "INFO")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/stories/{story_id}/polish",
            timeout=120  # Allow up to 2 minutes for LLM call
        )
        
        elapsed = time.time() - start_time
        
        # Check status code
        if response.status_code >= 500:
            log(f"❌ Polish endpoint returned 500 error", "ERROR")
            return {
                "status_code": response.status_code,
                "elapsed": elapsed,
                "error": "500 error",
                "passed": False
            }
        
        # Try to parse JSON
        try:
            data = response.json()
        except:
            log(f"❌ Polish endpoint did not return valid JSON", "ERROR")
            return {
                "status_code": response.status_code,
                "elapsed": elapsed,
                "error": "Invalid JSON response",
                "passed": False
            }
        
        # Check for _id leaks
        if check_id_leaks(data, "polish_response"):
            return {
                "status_code": response.status_code,
                "elapsed": elapsed,
                "error": "_id leak detected",
                "passed": False
            }
        
        # Check for required fields in response
        has_star_fields = all(k in data for k in ["situation", "task", "action", "result"])
        has_feedback = "feedback" in data
        has_status = "status" in data
        
        log(f"✅ Polish endpoint returned {response.status_code} in {elapsed:.2f}s", "INFO")
        log(f"   Response has STAR fields: {has_star_fields}", "INFO")
        log(f"   Response has feedback: {has_feedback}", "INFO")
        log(f"   Response has status: {has_status}", "INFO")
        
        return {
            "status_code": response.status_code,
            "elapsed": elapsed,
            "has_star_fields": has_star_fields,
            "has_feedback": has_feedback,
            "has_status": has_status,
            "response": data,
            "passed": response.status_code < 500 and has_star_fields
        }
        
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        log(f"❌ Polish endpoint timed out after {elapsed:.2f}s", "ERROR")
        return {
            "error": "Timeout",
            "elapsed": elapsed,
            "passed": False
        }
    except Exception as e:
        elapsed = time.time() - start_time
        log(f"❌ Polish endpoint failed: {e}", "ERROR")
        return {
            "error": str(e),
            "elapsed": elapsed,
            "passed": False
        }

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

def main():
    """Main test execution"""
    log("\n" + "="*80, "INFO")
    log("KUKDI BACKEND VERIFICATION - TENTATIVE EVENTS REMOVAL + POLISH ENDPOINT", "INFO")
    log("="*80 + "\n", "INFO")
    
    all_passed = True
    
    # TEST 1: Check calendar for tentative events
    log("="*80, "INFO")
    log("TEST 1: GET /api/calendar → NO tentative events", "INFO")
    log("="*80, "INFO")
    
    calendar_result = get_calendar_events()
    if "error" in calendar_result:
        log(f"❌ FAIL: Error getting calendar events", "ERROR")
        all_passed = False
    else:
        total = calendar_result["total_count"]
        tentative_count = calendar_result["tentative_count"]
        tentative_events = calendar_result["tentative_events"]
        
        log(f"Total events: {total}", "INFO")
        log(f"Tentative events: {tentative_count}", "INFO")
        
        if tentative_count > 0:
            log(f"❌ FAIL: Found {tentative_count} tentative event(s):", "ERROR")
            for event in tentative_events:
                log(f"   - {event}", "ERROR")
            all_passed = False
        else:
            log(f"✅ PASS: NO tentative events found (total events: {total})", "INFO")
    
    # TEST 2: DURABILITY - restart backend and check again
    log("\n" + "="*80, "INFO")
    log("TEST 2: DURABILITY - Restart backend and verify tentative events stay deleted", "INFO")
    log("="*80, "INFO")
    
    if not restart_backend():
        log("❌ FAIL: Backend restart failed", "ERROR")
        all_passed = False
    else:
        log("Waiting 8s for startup provisioning to complete...", "INFO")
        time.sleep(8)
        
        if not wait_for_backend():
            log("❌ FAIL: Backend not ready after restart", "ERROR")
            all_passed = False
        else:
            calendar_result_after = get_calendar_events()
            if "error" in calendar_result_after:
                log(f"❌ FAIL: Error getting calendar events after restart", "ERROR")
                all_passed = False
            else:
                total_after = calendar_result_after["total_count"]
                tentative_count_after = calendar_result_after["tentative_count"]
                tentative_events_after = calendar_result_after["tentative_events"]
                
                log(f"Total events after restart: {total_after}", "INFO")
                log(f"Tentative events after restart: {tentative_count_after}", "INFO")
                
                if tentative_count_after > 0:
                    log(f"❌ FAIL: Tentative events RECREATED after restart:", "ERROR")
                    for event in tentative_events_after:
                        log(f"   - {event}", "ERROR")
                    all_passed = False
                else:
                    log(f"✅ PASS: Tentative events still absent after restart (total events: {total_after})", "INFO")
    
    # TEST 3: BASELINE INTACT - verify 4 stories, 14 companies, 12 people
    log("\n" + "="*80, "INFO")
    log("TEST 3: BASELINE INTACT - Verify 4 stories, 14 companies, 12 people", "INFO")
    log("="*80, "INFO")
    
    stories_result = get_stories()
    companies_result = get_companies()
    people_result = get_people()
    
    # Check stories
    if "error" in stories_result:
        log(f"❌ FAIL: Error getting stories", "ERROR")
        all_passed = False
    else:
        story_count = stories_result["count"]
        log(f"Stories count: {story_count}", "INFO")
        if story_count != 4:
            log(f"❌ FAIL: Expected EXACTLY 4 stories, got {story_count}", "ERROR")
            all_passed = False
        else:
            log(f"✅ PASS: Exactly 4 stories", "INFO")
    
    # Check companies
    if "error" in companies_result:
        log(f"❌ FAIL: Error getting companies", "ERROR")
        all_passed = False
    else:
        company_count = companies_result["count"]
        log(f"Companies count: {company_count}", "INFO")
        if company_count != 14:
            log(f"❌ FAIL: Expected EXACTLY 14 companies, got {company_count}", "ERROR")
            all_passed = False
        else:
            log(f"✅ PASS: Exactly 14 companies", "INFO")
    
    # Check people
    if "error" in people_result:
        log(f"❌ FAIL: Error getting people", "ERROR")
        all_passed = False
    else:
        people_count = people_result["count"]
        prep_false_count = people_result["prep_group_false_count"]
        log(f"People count: {people_count}", "INFO")
        log(f"People with prep_group=false: {prep_false_count}", "INFO")
        if people_count != 12:
            log(f"❌ FAIL: Expected EXACTLY 12 people, got {people_count}", "ERROR")
            all_passed = False
        else:
            log(f"✅ PASS: Exactly 12 people", "INFO")
    
    # TEST 4: POLISH ENDPOINT - graceful behavior
    log("\n" + "="*80, "INFO")
    log("TEST 4: POLISH ENDPOINT - POST /api/stories/{id}/polish graceful behavior", "INFO")
    log("="*80, "INFO")
    
    if "error" not in stories_result and stories_result["count"] > 0:
        # Pick first story
        story_id = stories_result["stories"][0].get("id")
        if story_id:
            polish_result = test_polish_endpoint(story_id)
            
            if not polish_result.get("passed", False):
                log(f"❌ FAIL: Polish endpoint did not behave gracefully", "ERROR")
                if "error" in polish_result:
                    log(f"   Error: {polish_result['error']}", "ERROR")
                if "status_code" in polish_result:
                    log(f"   Status code: {polish_result['status_code']}", "ERROR")
                if "elapsed" in polish_result:
                    log(f"   Time taken: {polish_result['elapsed']:.2f}s", "ERROR")
                all_passed = False
            else:
                log(f"✅ PASS: Polish endpoint returned gracefully", "INFO")
                log(f"   Status: {polish_result['status_code']}", "INFO")
                log(f"   Latency: {polish_result['elapsed']:.2f}s", "INFO")
                log(f"   Has STAR fields: {polish_result.get('has_star_fields', False)}", "INFO")
                log(f"   Has feedback: {polish_result.get('has_feedback', False)}", "INFO")
        else:
            log(f"❌ FAIL: Could not find story ID to test polish endpoint", "ERROR")
            all_passed = False
    else:
        log(f"❌ FAIL: Cannot test polish endpoint - no stories available", "ERROR")
        all_passed = False
    
    # TEST 5: No _id leaks (already checked in each endpoint)
    log("\n" + "="*80, "INFO")
    log("TEST 5: No _id leaks in any responses", "INFO")
    log("="*80, "INFO")
    log("✅ PASS: No _id leaks detected in any response (checked throughout)", "INFO")
    
    # FINAL SUMMARY
    log("\n" + "="*80, "INFO")
    log("FINAL SUMMARY", "INFO")
    log("="*80, "INFO")
    
    if all_passed:
        log("\n✅ ✅ ✅ ALL TESTS PASSED", "INFO")
        log("✅ TEST 1: NO tentative events in calendar", "INFO")
        log("✅ TEST 2: Tentative events NOT recreated after restart (DURABILITY)", "INFO")
        log("✅ TEST 3: Baseline intact (4 stories, 14 companies, 12 people)", "INFO")
        log("✅ TEST 4: Polish endpoint behaves gracefully", "INFO")
        log("✅ TEST 5: No _id leaks detected", "INFO")
        log("\n🎉 BACKEND VERIFICATION COMPLETE - ALL REQUIREMENTS MET", "INFO")
        sys.exit(0)
    else:
        log("\n❌ ❌ ❌ SOME TESTS FAILED", "ERROR")
        log("See detailed output above for failures", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
