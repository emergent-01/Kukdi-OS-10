#!/usr/bin/env python3
"""
Backend API tests for Kukdi starter content seed verification.
Tests ONLY the seeded data: stories, calendar events, dream nudges, and data integrity.
"""
import requests
import sys
import json
from typing import Dict, List, Any

# Base URL from frontend/.env
BASE_URL = "https://github-alive.preview.emergentagent.com/api"

# Expected story titles
EXPECTED_STORY_TITLES = [
    "Doubling the Toastmasters budget",
    "Winning HACKOWASP with a contactless-shopping prototype",
    "Handling conflict in the OWASP chapter",
    "Teaching on mobile-only during COVID"
]

# Expected event titles
EXPECTED_EVENT_TITLES = [
    "Company registrations — expected mid-September (tentative)",
    "Interviews — expected around November (tentative)"
]

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "_id_leaks": []
}


def check_no_id_leak(data: Any, path: str = "root") -> List[str]:
    """Recursively check for _id fields in response data."""
    leaks = []
    if isinstance(data, dict):
        if "_id" in data:
            leaks.append(f"{path} contains _id: {data['_id']}")
        for key, value in data.items():
            leaks.extend(check_no_id_leak(value, f"{path}.{key}"))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            leaks.extend(check_no_id_leak(item, f"{path}[{i}]"))
    return leaks


def test_result(name: str, passed: bool, details: str = ""):
    """Record test result."""
    if passed:
        test_results["passed"].append(f"✅ {name}")
        print(f"✅ PASS: {name}")
        if details:
            print(f"   {details}")
    else:
        test_results["failed"].append(f"❌ {name}: {details}")
        print(f"❌ FAIL: {name}")
        print(f"   {details}")


def check_id_leaks(response_data: Any, test_name: str):
    """Check for _id leaks and record them."""
    leaks = check_no_id_leak(response_data)
    if leaks:
        for leak in leaks:
            test_results["_id_leaks"].append(f"{test_name}: {leak}")
            test_result(f"{test_name} - No _id leak", False, leak)
    else:
        test_result(f"{test_name} - No _id leak", True)


# ============================================================================
# TEST 1: GET /api/stories - 4 STAR story drafts
# ============================================================================

def test_stories():
    """Test GET /api/stories returns exactly 4 story drafts with correct data."""
    print("\n" + "="*70)
    print("TEST 1: GET /api/stories - 4 STAR story drafts")
    print("="*70)
    
    try:
        resp = requests.get(f"{BASE_URL}/stories", timeout=10)
        
        if resp.status_code != 200:
            test_result("GET /api/stories", False, f"Status {resp.status_code}: {resp.text}")
            return
        
        data = resp.json()
        check_id_leaks(data, "GET /api/stories")
        
        stories = data.get("stories", [])
        
        # Test 1a: Exactly 4 stories
        if len(stories) == 4:
            test_result("GET /api/stories returns exactly 4 stories", True, f"Found {len(stories)} stories")
        else:
            test_result("GET /api/stories returns exactly 4 stories", False, 
                       f"Expected 4 stories, found {len(stories)}")
        
        # Test 1b: Check each expected title exists
        found_titles = [s.get("title", "") for s in stories]
        print(f"\n   Found story titles:")
        for title in found_titles:
            print(f"      - {title}")
        
        for expected_title in EXPECTED_STORY_TITLES:
            if expected_title in found_titles:
                test_result(f"Story '{expected_title}' exists", True)
            else:
                test_result(f"Story '{expected_title}' exists", False,
                           f"Title not found in stories")
        
        # Test 1c: Check each story has required fields and no brackets in action
        for i, story in enumerate(stories):
            title = story.get("title", f"Story {i+1}")
            
            # Check status = draft
            if story.get("status") == "draft":
                test_result(f"Story '{title}' status=draft", True)
            else:
                test_result(f"Story '{title}' status=draft", False,
                           f"Status is '{story.get('status')}'")
            
            # Check STAR fields are non-empty
            situation = story.get("situation", "")
            task = story.get("task", "")
            action = story.get("action", "")
            result = story.get("result", "")
            
            if situation and task and action and result:
                test_result(f"Story '{title}' has non-empty STAR fields", True)
            else:
                empty_fields = []
                if not situation: empty_fields.append("situation")
                if not task: empty_fields.append("task")
                if not action: empty_fields.append("action")
                if not result: empty_fields.append("result")
                test_result(f"Story '{title}' has non-empty STAR fields", False,
                           f"Empty fields: {', '.join(empty_fields)}")
            
            # CRITICAL: Check action text does NOT contain square brackets
            if '[' in action or ']' in action:
                test_result(f"Story '{title}' action has NO square brackets", False,
                           f"Action contains brackets: {action[:100]}...")
            else:
                test_result(f"Story '{title}' action has NO square brackets", True)
            
            # Check themes and tags are populated
            themes = story.get("themes", [])
            tags = story.get("tags", [])
            
            if themes:
                test_result(f"Story '{title}' has themes", True, f"{len(themes)} theme(s)")
            else:
                test_result(f"Story '{title}' has themes", False, "themes is empty")
            
            if tags:
                test_result(f"Story '{title}' has tags", True, f"{len(tags)} tag(s)")
            else:
                test_result(f"Story '{title}' has tags", False, "tags is empty")
    
    except Exception as e:
        test_result("GET /api/stories", False, str(e))


# ============================================================================
# TEST 2: GET /api/calendar/events - 2 tentative events
# ============================================================================

def test_calendar_events():
    """Test GET /api/calendar returns 2 tentative events."""
    print("\n" + "="*70)
    print("TEST 2: GET /api/calendar - 2 tentative events")
    print("="*70)
    
    try:
        resp = requests.get(f"{BASE_URL}/calendar", timeout=10)
        
        if resp.status_code != 200:
            test_result("GET /api/calendar", False, f"Status {resp.status_code}: {resp.text}")
            return
        
        data = resp.json()
        check_id_leaks(data, "GET /api/calendar")
        
        events = data.get("events", [])
        
        print(f"\n   Found {len(events)} total events")
        
        # Find the tentative events
        tentative_events = []
        for event in events:
            title = event.get("title", "")
            if "(tentative)" in title.lower():
                tentative_events.append(event)
        
        print(f"   Found {len(tentative_events)} tentative events:")
        for event in tentative_events:
            print(f"      - {event.get('title', 'Untitled')}")
        
        # Test 2a: At least 2 tentative events exist
        if len(tentative_events) >= 2:
            test_result("GET /api/calendar has 2 tentative events", True,
                       f"Found {len(tentative_events)} tentative events")
        else:
            test_result("GET /api/calendar has 2 tentative events", False,
                       f"Expected at least 2, found {len(tentative_events)}")
        
        # Test 2b: Check for specific expected events
        found_titles = [e.get("title", "") for e in tentative_events]
        
        for expected_title in EXPECTED_EVENT_TITLES:
            if expected_title in found_titles:
                test_result(f"Event '{expected_title}' exists", True)
                
                # Find the event and check its properties
                event = next((e for e in tentative_events if e.get("title") == expected_title), None)
                if event:
                    # Check done=false
                    if event.get("done") == False:
                        test_result(f"Event '{expected_title}' done=false", True)
                    else:
                        test_result(f"Event '{expected_title}' done=false", False,
                                   f"done is {event.get('done')}")
                    
                    # Check type
                    event_type = event.get("type", "")
                    if "Company registrations" in expected_title:
                        if event_type == "deadline":
                            test_result(f"Event '{expected_title}' type=deadline", True)
                        else:
                            test_result(f"Event '{expected_title}' type=deadline", False,
                                       f"type is '{event_type}'")
                    elif "Interviews" in expected_title:
                        if event_type == "placement":
                            test_result(f"Event '{expected_title}' type=placement", True)
                        else:
                            test_result(f"Event '{expected_title}' type=placement", False,
                                       f"type is '{event_type}'")
            else:
                test_result(f"Event '{expected_title}' exists", False,
                           f"Title not found in tentative events")
    
    except Exception as e:
        test_result("GET /api/calendar", False, str(e))


# ============================================================================
# TEST 3: GET /api/dream/nudges - structure check
# ============================================================================

def test_dream_nudges():
    """Test GET /api/dream/nudges returns 200 with {nudge, more} structure."""
    print("\n" + "="*70)
    print("TEST 3: GET /api/dream/nudges - structure check")
    print("="*70)
    
    print("\n   (This endpoint may call an LLM and take up to 30s)")
    
    try:
        resp = requests.get(f"{BASE_URL}/dream/nudges", timeout=30)
        
        # Test 3a: Returns 200
        if resp.status_code == 200:
            test_result("GET /api/dream/nudges returns 200", True)
        else:
            test_result("GET /api/dream/nudges returns 200", False,
                       f"Status {resp.status_code}: {resp.text}")
            return
        
        data = resp.json()
        check_id_leaks(data, "GET /api/dream/nudges")
        
        # Test 3b: Has 'nudge' and 'more' keys
        if "nudge" in data and "more" in data:
            test_result("GET /api/dream/nudges has {nudge, more} structure", True)
        else:
            test_result("GET /api/dream/nudges has {nudge, more} structure", False,
                       f"Missing keys. Found: {list(data.keys())}")
            return
        
        nudge = data.get("nudge")
        more = data.get("more")
        
        # Test 3c: 'nudge' may be null (valid when nothing to surface)
        if nudge is None:
            test_result("GET /api/dream/nudges nudge is null (valid)", True,
                       "nudge is null - expected when nothing to surface")
        else:
            test_result("GET /api/dream/nudges nudge is non-null", True,
                       f"nudge type: {type(nudge).__name__}")
        
        # Test 3d: 'more' must be a list
        if isinstance(more, list):
            test_result("GET /api/dream/nudges 'more' is a list", True,
                       f"more has {len(more)} item(s)")
        else:
            test_result("GET /api/dream/nudges 'more' is a list", False,
                       f"more is {type(more).__name__}, expected list")
    
    except requests.exceptions.Timeout:
        test_result("GET /api/dream/nudges", False, "Request timed out after 30s")
    except Exception as e:
        test_result("GET /api/dream/nudges", False, str(e))


# ============================================================================
# TEST 4: Data integrity - companies and people counts
# ============================================================================

def test_data_integrity():
    """Test that existing data is intact: 14 companies, 12 people."""
    print("\n" + "="*70)
    print("TEST 4: Data integrity - companies and people counts")
    print("="*70)
    
    # Test 4a: Companies count = 14
    print("\n--- Test 4a: GET /api/dream/overview companies count ---")
    try:
        resp = requests.get(f"{BASE_URL}/dream/overview", timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            check_id_leaks(data, "GET /api/dream/overview")
            
            companies = data.get("companies", [])
            count = len(companies)
            
            if count == 14:
                test_result("GET /api/dream/overview companies count = 14", True,
                           f"Found {count} companies")
            else:
                test_result("GET /api/dream/overview companies count = 14", False,
                           f"Expected 14, found {count}")
        else:
            test_result("GET /api/dream/overview", False,
                       f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        test_result("GET /api/dream/overview", False, str(e))
    
    # Test 4b: People count = 12
    print("\n--- Test 4b: GET /api/people count ---")
    try:
        resp = requests.get(f"{BASE_URL}/people", timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            check_id_leaks(data, "GET /api/people")
            
            people = data.get("people", [])
            count = len(people)
            
            if count == 12:
                test_result("GET /api/people count = 12", True,
                           f"Found {count} people")
            else:
                test_result("GET /api/people count = 12", False,
                           f"Expected 12, found {count}")
        else:
            test_result("GET /api/people", False,
                       f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        test_result("GET /api/people", False, str(e))


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    print("\n" + "="*70)
    print("KUKDI STARTER CONTENT SEED VERIFICATION")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print("Testing seeded data: stories, events, nudges, data integrity")
    print("="*70)
    
    # Run tests in sequence
    test_stories()
    test_calendar_events()
    test_dream_nudges()
    test_data_integrity()
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    print(f"\n✅ PASSED: {len(test_results['passed'])}")
    for result in test_results['passed']:
        print(f"   {result}")
    
    print(f"\n❌ FAILED: {len(test_results['failed'])}")
    for result in test_results['failed']:
        print(f"   {result}")
    
    if test_results['_id_leaks']:
        print(f"\n🚨 _ID LEAKS DETECTED: {len(test_results['_id_leaks'])}")
        for leak in test_results['_id_leaks']:
            print(f"   {leak}")
    else:
        print("\n✅ NO _ID LEAKS DETECTED")
    
    print("\n" + "="*70)
    
    # Exit with appropriate code
    if test_results['failed'] or test_results['_id_leaks']:
        print("❌ TESTS FAILED")
        sys.exit(1)
    else:
        print("✅ ALL TESTS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
