"""
Backend-only verification for provisioning root-cause fix.
Tests the additive/idempotent provisioning of stories, companies, people, and events.
"""
import requests
import json
from typing import Dict, List, Any

# Backend URL from frontend/.env
BASE_URL = "https://github-alive.preview.emergentagent.com/api"

# Expected exact story titles
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

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name: str, passed: bool, details: str = ""):
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"{status} - {name}")
    if details:
        print(f"    {details}")

def check_no_id_leak(data: Any, path: str = "root") -> List[str]:
    """Recursively check for _id field leaks in response data."""
    leaks = []
    if isinstance(data, dict):
        if "_id" in data:
            leaks.append(f"_id found at {path}")
        for key, value in data.items():
            leaks.extend(check_no_id_leak(value, f"{path}.{key}"))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            leaks.extend(check_no_id_leak(item, f"{path}[{i}]"))
    return leaks

def test_stories():
    """Test 1: GET /api/stories - verify exactly 4 story drafts with correct structure."""
    print(f"\n{Colors.BLUE}TEST 1: GET /api/stories{Colors.END}")
    
    try:
        response = requests.get(f"{BASE_URL}/stories", timeout=10)
        print_test("Stories endpoint returns 200", response.status_code == 200, 
                   f"Status: {response.status_code}")
        
        if response.status_code != 200:
            return False
        
        data = response.json()
        stories = data.get("stories", [])
        
        # Check count
        count_pass = len(stories) == 4
        print_test("Exactly 4 stories returned", count_pass, 
                   f"Count: {len(stories)}")
        
        # Check titles
        actual_titles = [s.get("title") for s in stories]
        titles_match = set(actual_titles) == set(EXPECTED_STORY_TITLES)
        print_test("Story titles match expected", titles_match,
                   f"Titles: {actual_titles}")
        
        # Check each story structure
        all_valid = True
        for story in stories:
            title = story.get("title", "Unknown")
            
            # Check status
            if story.get("status") != "draft":
                print_test(f"Story '{title}' status is 'draft'", False,
                           f"Status: {story.get('status')}")
                all_valid = False
            
            # Check STAR fields are non-empty
            for field in ["situation", "task", "action", "result"]:
                value = story.get(field, "")
                if not value or not isinstance(value, str) or len(value.strip()) == 0:
                    print_test(f"Story '{title}' has non-empty {field}", False,
                               f"{field}: '{value}'")
                    all_valid = False
            
            # Check themes and tags are non-empty lists
            themes = story.get("themes", [])
            tags = story.get("tags", [])
            if not isinstance(themes, list) or len(themes) == 0:
                print_test(f"Story '{title}' has non-empty themes list", False,
                           f"themes: {themes}")
                all_valid = False
            if not isinstance(tags, list) or len(tags) == 0:
                print_test(f"Story '{title}' has non-empty tags list", False,
                           f"tags: {tags}")
                all_valid = False
            
            # CRITICAL: Check action text contains NO square brackets
            action = story.get("action", "")
            has_brackets = "[" in action or "]" in action
            if has_brackets:
                print_test(f"Story '{title}' action has NO square brackets", False,
                           f"Action contains brackets: {action[:100]}...")
                all_valid = False
        
        if all_valid:
            print_test("All stories have valid structure", True)
        
        # Check for _id leaks
        leaks = check_no_id_leak(stories, "stories")
        print_test("No _id leaks in stories response", len(leaks) == 0,
                   f"Leaks: {leaks}" if leaks else "")
        
        return count_pass and titles_match and all_valid and len(leaks) == 0
        
    except Exception as e:
        print_test("Stories test execution", False, f"Error: {str(e)}")
        return False

def test_companies():
    """Test 2: GET /api/dream/overview - verify exactly 14 companies."""
    print(f"\n{Colors.BLUE}TEST 2: GET /api/dream/overview{Colors.END}")
    
    try:
        response = requests.get(f"{BASE_URL}/dream/overview", timeout=10)
        print_test("Dream overview endpoint returns 200", response.status_code == 200,
                   f"Status: {response.status_code}")
        
        if response.status_code != 200:
            return False
        
        data = response.json()
        companies = data.get("companies", [])
        
        count_pass = len(companies) == 14
        print_test("Exactly 14 companies returned", count_pass,
                   f"Count: {len(companies)}")
        
        # Check for _id leaks
        leaks = check_no_id_leak(data, "dream/overview")
        print_test("No _id leaks in companies response", len(leaks) == 0,
                   f"Leaks: {leaks}" if leaks else "")
        
        return count_pass and len(leaks) == 0
        
    except Exception as e:
        print_test("Companies test execution", False, f"Error: {str(e)}")
        return False

def test_people():
    """Test 3: GET /api/people - verify exactly 12 people, all unconfirmed prep candidates."""
    print(f"\n{Colors.BLUE}TEST 3: GET /api/people{Colors.END}")
    
    try:
        response = requests.get(f"{BASE_URL}/people", timeout=10)
        print_test("People endpoint returns 200", response.status_code == 200,
                   f"Status: {response.status_code}")
        
        if response.status_code != 200:
            return False
        
        data = response.json()
        people = data.get("people", [])
        
        count_pass = len(people) == 12
        print_test("Exactly 12 people returned", count_pass,
                   f"Count: {len(people)}")
        
        # Check all are unconfirmed prep candidates
        all_valid = True
        for person in people:
            name = person.get("name", "Unknown")
            prep_group = person.get("prep_group")
            prep_candidate = person.get("prep_candidate")
            strengths = person.get("strengths", [])
            
            if prep_group != False:
                print_test(f"Person '{name}' has prep_group=false", False,
                           f"prep_group: {prep_group}")
                all_valid = False
            
            if prep_candidate != True:
                print_test(f"Person '{name}' has prep_candidate=true", False,
                           f"prep_candidate: {prep_candidate}")
                all_valid = False
            
            if not isinstance(strengths, list) or len(strengths) != 0:
                print_test(f"Person '{name}' has empty strengths list", False,
                           f"strengths: {strengths}")
                all_valid = False
        
        if all_valid:
            print_test("All people are unconfirmed prep candidates", True)
        
        # Check for _id leaks
        leaks = check_no_id_leak(people, "people")
        print_test("No _id leaks in people response", len(leaks) == 0,
                   f"Leaks: {leaks}" if leaks else "")
        
        return count_pass and all_valid and len(leaks) == 0
        
    except Exception as e:
        print_test("People test execution", False, f"Error: {str(e)}")
        return False

def test_calendar():
    """Test 4: GET /api/calendar - verify 2 tentative events."""
    print(f"\n{Colors.BLUE}TEST 4: GET /api/calendar{Colors.END}")
    
    try:
        response = requests.get(f"{BASE_URL}/calendar", timeout=10)
        print_test("Calendar endpoint returns 200", response.status_code == 200,
                   f"Status: {response.status_code}")
        
        if response.status_code != 200:
            return False
        
        data = response.json()
        events = data.get("events", [])
        
        # Find the tentative events
        tentative_events = [e for e in events if e.get("title") in EXPECTED_EVENT_TITLES]
        
        count_pass = len(tentative_events) == 2
        print_test("Exactly 2 tentative events found", count_pass,
                   f"Count: {len(tentative_events)}")
        
        # Check event details
        all_valid = True
        for event in tentative_events:
            title = event.get("title", "Unknown")
            event_type = event.get("type")
            done = event.get("done")
            
            # Check type
            if title == EXPECTED_EVENT_TITLES[0]:  # Company registrations
                if event_type != "deadline":
                    print_test(f"Event '{title}' has type='deadline'", False,
                               f"type: {event_type}")
                    all_valid = False
            elif title == EXPECTED_EVENT_TITLES[1]:  # Interviews
                if event_type != "placement":
                    print_test(f"Event '{title}' has type='placement'", False,
                               f"type: {event_type}")
                    all_valid = False
            
            # Check done=false
            if done != False:
                print_test(f"Event '{title}' has done=false", False,
                           f"done: {done}")
                all_valid = False
        
        if all_valid:
            print_test("All tentative events have correct structure", True)
        
        # Check for _id leaks
        leaks = check_no_id_leak(events, "calendar")
        print_test("No _id leaks in calendar response", len(leaks) == 0,
                   f"Leaks: {leaks}" if leaks else "")
        
        return count_pass and all_valid and len(leaks) == 0
        
    except Exception as e:
        print_test("Calendar test execution", False, f"Error: {str(e)}")
        return False

def capture_baseline_counts():
    """Capture current counts for idempotency check."""
    print(f"\n{Colors.BLUE}CAPTURING BASELINE COUNTS{Colors.END}")
    
    counts = {}
    
    try:
        # Stories
        response = requests.get(f"{BASE_URL}/stories", timeout=10)
        if response.status_code == 200:
            data = response.json()
            stories = data.get("stories", [])
            counts["stories"] = len(stories)
            counts["story_titles"] = sorted([s.get("title") for s in stories])
        
        # Companies
        response = requests.get(f"{BASE_URL}/dream/overview", timeout=10)
        if response.status_code == 200:
            data = response.json()
            counts["companies"] = len(data.get("companies", []))
        
        # People
        response = requests.get(f"{BASE_URL}/people", timeout=10)
        if response.status_code == 200:
            data = response.json()
            people = data.get("people", [])
            counts["people"] = len(people)
        
        # Events
        response = requests.get(f"{BASE_URL}/calendar", timeout=10)
        if response.status_code == 200:
            data = response.json()
            events = data.get("events", [])
            counts["events"] = len(events)
        
        print(f"Baseline counts: stories={counts.get('stories')}, companies={counts.get('companies')}, "
              f"people={counts.get('people')}, events={counts.get('events')}")
        
        return counts
        
    except Exception as e:
        print(f"Error capturing baseline: {str(e)}")
        return None

def verify_idempotency(baseline_counts):
    """Verify counts remain stable after restart (no duplicates, no data loss)."""
    print(f"\n{Colors.BLUE}TEST 5: IDEMPOTENCY / NO-WIPE CHECK{Colors.END}")
    
    if not baseline_counts:
        print_test("Idempotency check", False, "No baseline counts available")
        return False
    
    try:
        # Stories
        response = requests.get(f"{BASE_URL}/stories", timeout=10)
        if response.status_code == 200:
            data = response.json()
            stories = data.get("stories", [])
            current_count = len(stories)
            current_titles = sorted([s.get("title") for s in stories])
            
            count_stable = current_count == baseline_counts.get("stories")
            print_test("Stories count stable", count_stable,
                       f"Before: {baseline_counts.get('stories')}, After: {current_count}")
            
            # Check for duplicate titles
            unique_titles = len(set(current_titles))
            no_duplicates = unique_titles == current_count
            print_test("No duplicate story titles", no_duplicates,
                       f"Total: {current_count}, Unique: {unique_titles}")
            
            if not count_stable or not no_duplicates:
                return False
        
        # Companies
        response = requests.get(f"{BASE_URL}/dream/overview", timeout=10)
        if response.status_code == 200:
            data = response.json()
            current_count = len(data.get("companies", []))
            count_stable = current_count == baseline_counts.get("companies")
            print_test("Companies count stable", count_stable,
                       f"Before: {baseline_counts.get('companies')}, After: {current_count}")
            if not count_stable:
                return False
        
        # People
        response = requests.get(f"{BASE_URL}/people", timeout=10)
        if response.status_code == 200:
            data = response.json()
            people = data.get("people", [])
            current_count = len(people)
            count_stable = current_count == baseline_counts.get("people")
            print_test("People count stable", count_stable,
                       f"Before: {baseline_counts.get('people')}, After: {current_count}")
            if not count_stable:
                return False
        
        # Events
        response = requests.get(f"{BASE_URL}/calendar", timeout=10)
        if response.status_code == 200:
            data = response.json()
            events = data.get("events", [])
            current_count = len(events)
            count_stable = current_count == baseline_counts.get("events")
            print_test("Events count stable", count_stable,
                       f"Before: {baseline_counts.get('events')}, After: {current_count}")
            if not count_stable:
                return False
        
        print_test("IDEMPOTENCY VERIFIED - No duplicates, no data loss", True)
        return True
        
    except Exception as e:
        print_test("Idempotency check execution", False, f"Error: {str(e)}")
        return False

def main():
    print(f"\n{Colors.YELLOW}{'='*80}{Colors.END}")
    print(f"{Colors.YELLOW}BACKEND VERIFICATION - PROVISIONING ROOT-CAUSE FIX{Colors.END}")
    print(f"{Colors.YELLOW}{'='*80}{Colors.END}")
    
    results = {}
    
    # Run all tests
    results["stories"] = test_stories()
    results["companies"] = test_companies()
    results["people"] = test_people()
    results["calendar"] = test_calendar()
    
    # Capture baseline for idempotency check
    baseline_counts = capture_baseline_counts()
    
    # Summary
    print(f"\n{Colors.YELLOW}{'='*80}{Colors.END}")
    print(f"{Colors.YELLOW}TEST SUMMARY{Colors.END}")
    print(f"{Colors.YELLOW}{'='*80}{Colors.END}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{test_name.upper()}: {status}")
    
    print(f"\n{Colors.BLUE}Total: {passed}/{total} tests passed{Colors.END}")
    
    if baseline_counts:
        print(f"\n{Colors.BLUE}Baseline counts captured for idempotency verification:{Colors.END}")
        print(f"  Stories: {baseline_counts.get('stories')}")
        print(f"  Companies: {baseline_counts.get('companies')}")
        print(f"  People: {baseline_counts.get('people')}")
        print(f"  Events: {baseline_counts.get('events')}")
        print(f"\n{Colors.YELLOW}To verify idempotency: restart backend and re-run this test{Colors.END}")
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
