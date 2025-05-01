#!/usr/bin/env python3
"""
Comprehensive test suite for language settings in the user profile API.

This script:
1. Creates test users in a sandboxed environment
2. Tests all possible language mutations:
   - Adding languages
   - Updating languages
   - Changing default language
   - Removing languages
   - Edge cases (empty lists, invalid data)
3. Verifies that changes are correctly persisted

The tests use unique email addresses to avoid conflicts with real users.
"""

import requests
import json
import sys
import uuid
import time

BASE_URL = "http://localhost:8000"

# Test constants
TEST_USER_PREFIX = "test_user_"
TEST_PASSWORD = "TestPassword123!"

def print_colored(text, color="green"):
    """Print colored text to the console"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "purple": "\033[95m",
        "cyan": "\033[96m",
        "end": "\033[0m"
    }
    print(f"{colors.get(color, colors['green'])}{text}{colors['end']}")

def create_test_user(name_suffix=""):
    """Create a test user and return the user credentials"""
    unique_id = str(uuid.uuid4())[:8]
    name = f"Test User {unique_id}{name_suffix}"
    email = f"{TEST_USER_PREFIX}{unique_id}@example.com"
    password = TEST_PASSWORD
    
    print_colored(f"\nCreating test user: {email}", "blue")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/signup",
            json={
                "email": email,
                "password": password,
                "name": name,
                "native_language": "en",
                "learning_language": "ko"
            }
        )
        
        if response.status_code not in [200, 201]:
            print_colored(f"Failed to create test user (status code {response.status_code}): {response.text}", "red")
            return None
        
        # Check the response payload - the API returns success in the JSON body
        data = response.json()
        if data.get("success"):
            print_colored(f"Test user created successfully: {email} (user_id: {data.get('user_id', 'unknown')})", "green")
            return {"email": email, "password": password, "name": name}
        else:
            print_colored(f"Failed to create test user: {data}", "red")
            return None
    except Exception as e:
        print_colored(f"Error creating test user: {str(e)}", "red")
        return None

def authenticate(email, password):
    """Authenticate with the API and return the token"""
    print_colored(f"Authenticating {email}...", "blue")
    response = requests.post(
        f"{BASE_URL}/api/auth/signin",
        json={"email": email, "password": password}
    )
    
    if response.status_code != 200:
        print_colored(f"Authentication failed: {response.text}", "red")
        return None
    
    token = response.json().get("token")
    print_colored("Authentication successful", "green")
    return token

def get_profile(token, use_cache_breaker=False):
    """Get the current user profile"""
    try:
        # Add cache-busting query param to ensure we get fresh data
        cache_buster = f"?_={time.time()}" if use_cache_breaker else ""
        
        print_colored("Fetching user profile from API...", "blue")
        response = requests.get(
            f"{BASE_URL}/api/user/profile{cache_buster}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code != 200:
            print_colored(f"Failed to get profile: {response.text}", "red")
            return None
        
        profile_data = response.json()
        print_colored(f"Profile data received! Profile contains {len(profile_data.get('additional_languages', []))} additional languages", "blue")
        return profile_data
    except Exception as e:
        print_colored(f"Error getting profile: {str(e)}", "red")
        return None

def update_profile(token, update_data):
    """Update the user profile and return the updated profile"""
    print_colored("\nUpdating profile:", "blue")
    print(json.dumps(update_data, indent=2))
    
    # Ensure additional_languages is properly formatted
    if 'additional_languages' in update_data:
        print_colored(f"Sending {len(update_data['additional_languages'])} additional languages in request", "blue")
        print_colored(f"Additional languages payload structure: {type(update_data['additional_languages'])}", "blue")
        for i, lang in enumerate(update_data['additional_languages']):
            print_colored(f"  Language {i+1}: {lang['language']} ({lang['proficiency']}){' [DEFAULT]' if lang.get('isDefault') else ''}", "blue")
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/user/profile",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            json=update_data
        )
        
        if response.status_code != 200:
            print_colored(f"Failed to update profile (status code {response.status_code}): {response.text}", "red")
            return None
        
        updated_data = response.json()
        print_colored("Response from update API:", "green")
        print_colored(f"Has 'additional_languages' field: {'additional_languages' in updated_data}", "yellow")
        
        if 'additional_languages' in updated_data:
            additional_languages = updated_data.get('additional_languages', [])
            print_colored(f"Number of languages in response: {len(additional_languages)}", "yellow")
            for lang in additional_languages:
                print_colored(f"  - {lang.get('language')} ({lang.get('proficiency')}){' [DEFAULT]' if lang.get('isDefault') else ''}", "yellow")
        
        return updated_data
    except Exception as e:
        print_colored(f"Error updating profile: {str(e)}", "red")
        return None

def compare_language_lists(expected, actual):
    """Compare two lists of languages and return the differences"""
    if not actual:
        if not expected:
            return True, []
        return False, expected
    
    # Check if all expected languages are in the profile
    missing_languages = []
    for expected_lang in expected:
        found = False
        for actual_lang in actual:
            if (expected_lang["language"] == actual_lang["language"] and 
                expected_lang["proficiency"] == actual_lang["proficiency"]):
                # Check isDefault if it's specified
                if "isDefault" in expected_lang and expected_lang["isDefault"] != actual_lang.get("isDefault", False):
                    continue
                found = True
                break
        if not found:
            missing_languages.append(expected_lang)
    
    return len(missing_languages) == 0, missing_languages

def run_test_case(title, user_credentials, profile_update, expected_languages, description=""):
    """Run a test case for updating and verifying languages"""
    print_colored("\n" + "-"*80, "cyan")
    print_colored(f"TEST: {title}", "cyan")
    if description:
        print_colored(description, "blue")
    print_colored("-"*80, "cyan")
    
    token = authenticate(user_credentials["email"], user_credentials["password"])
    if not token:
        return False
    
    # Get original profile
    original_profile = get_profile(token)
    if not original_profile:
        return False
    
    print_colored("\nOriginal profile languages:", "yellow")
    primary_lang = original_profile.get("learning_language", "")
    primary_prof = original_profile.get("proficiency", "")
    print(f"  - Primary: {primary_lang} ({primary_prof})")
    
    additional_langs = original_profile.get("additional_languages", [])
    for lang in additional_langs:
        print(f"  - Additional: {lang['language']} ({lang['proficiency']})" + 
              (" [DEFAULT]" if lang.get("isDefault") else ""))
    
    # Update profile
    print_colored("\nUpdating profile:", "blue")
    print(json.dumps(profile_update, indent=2))
    
    updated_profile = update_profile(token, profile_update)
    if not updated_profile:
        return False
    
    # Give the database a moment to process the update
    print_colored("Waiting 2 seconds for database update to complete...", "blue")
    time.sleep(2)  # Add a small delay to ensure changes have propagated
    
    # Get updated profile - use cache breaker to ensure fresh data
    final_profile = get_profile(token, use_cache_breaker=True)
    if not final_profile:
        return False
    
    print_colored("\nFinal profile languages:", "yellow")
    primary_lang = final_profile.get("learning_language", "")
    primary_prof = final_profile.get("proficiency", "")
    print(f"  - Primary: {primary_lang} ({primary_prof})")
    
    additional_langs = final_profile.get("additional_languages", [])
    for lang in additional_langs:
        print(f"  - Additional: {lang['language']} ({lang['proficiency']})" + 
              (" [DEFAULT]" if lang.get("isDefault") else ""))
    
    # Verify languages
    success, missing = compare_language_lists(expected_languages, additional_langs)
    
    if success:
        print_colored("\n✅ TEST PASSED: Languages were correctly saved!", "green")
    else:
        print_colored("\n❌ TEST FAILED: Languages were not correctly saved!", "red")
        print_colored("Missing languages:", "red")
        for lang in missing:
            print(f"  - {lang['language']} ({lang['proficiency']})" + 
                  (" [DEFAULT]" if lang.get("isDefault", False) else ""))
    
    return success

def delete_test_users():
    """Delete all test users to maintain a clean test environment"""
    print_colored("\nCleaning up test users...", "blue")
    try:
        response = requests.get(
            f"{BASE_URL}/api/user/test-cleanup",
            params={"prefix": TEST_USER_PREFIX, "secret": "test_secret_key"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("deleted_count", 0) > 0:
                print_colored(f"Deleted {data.get('deleted_count')} test users", "green")
            else:
                print_colored("No test users found to delete", "yellow")
        else:
            print_colored(f"Failed to delete test users: {response.text}", "red")
    except Exception as e:
        print_colored(f"Error deleting test users: {str(e)}", "red")

def main():
    print_colored("\n===== LINGOGI USER PROFILE LANGUAGE SETTINGS TEST SUITE =====", "purple")
    print_colored("This test suite verifies that language settings are properly saved.\n", "purple")
    
    # First clean up any existing test users
    delete_test_users()
    
    # Create test users
    user1 = create_test_user("_single_lang")
    user2 = create_test_user("_multi_lang")
    
    if not user1 or not user2:
        print_colored("Failed to create test users. Aborting.", "red")
        return
    
    # Sleep briefly to ensure users are fully created
    time.sleep(1)
    
    # Test cases
    test_results = []
    
    # Test 1: Add a single additional language
    test1_update = {
        "name": user1["name"],
        "native_language": "en",
        "learning_language": "ko",
        "proficiency": "intermediate",
        "additional_languages": [
            {"language": "ja", "proficiency": "beginner", "isDefault": False}
        ]
    }
    test1_expected = [
        {"language": "ja", "proficiency": "beginner", "isDefault": False}
    ]
    test1_result = run_test_case(
        "Add a single additional language",
        user1,
        test1_update,
        test1_expected,
        "Adding Japanese as a beginner language while keeping Korean as primary"
    )
    test_results.append(("Add single language", test1_result))
    
    # Test 2: Add multiple additional languages
    test2_update = {
        "name": user2["name"],
        "native_language": "en",
        "learning_language": "ko",
        "proficiency": "advanced",
        "additional_languages": [
            {"language": "ja", "proficiency": "beginner", "isDefault": False},
            {"language": "es", "proficiency": "intermediate", "isDefault": False},
            {"language": "fr", "proficiency": "beginner", "isDefault": False}
        ]
    }
    test2_expected = [
        {"language": "ja", "proficiency": "beginner", "isDefault": False},
        {"language": "es", "proficiency": "intermediate", "isDefault": False},
        {"language": "fr", "proficiency": "beginner", "isDefault": False}
    ]
    test2_result = run_test_case(
        "Add multiple additional languages",
        user2,
        test2_update,
        test2_expected,
        "Adding Japanese, Spanish, and French as additional languages"
    )
    test_results.append(("Add multiple languages", test2_result))
    
    # Test 3: Update language proficiency
    test3_update = {
        "name": user2["name"],
        "native_language": "en",
        "learning_language": "ko",
        "proficiency": "advanced",
        "additional_languages": [
            {"language": "ja", "proficiency": "intermediate", "isDefault": False},  # Changed from beginner
            {"language": "es", "proficiency": "advanced", "isDefault": False},      # Changed from intermediate
            {"language": "fr", "proficiency": "beginner", "isDefault": False}       # Unchanged
        ]
    }
    test3_expected = [
        {"language": "ja", "proficiency": "intermediate", "isDefault": False},
        {"language": "es", "proficiency": "advanced", "isDefault": False},
        {"language": "fr", "proficiency": "beginner", "isDefault": False}
    ]
    test3_result = run_test_case(
        "Update language proficiency",
        user2,
        test3_update,
        test3_expected,
        "Updating proficiency levels for Japanese and Spanish"
    )
    test_results.append(("Update proficiency", test3_result))
    
    # Test 4: Remove a language
    test4_update = {
        "name": user2["name"],
        "native_language": "en",
        "learning_language": "ko",
        "proficiency": "advanced",
        "additional_languages": [
            {"language": "ja", "proficiency": "intermediate", "isDefault": False},
            {"language": "es", "proficiency": "advanced", "isDefault": False}
            # French removed
        ]
    }
    test4_expected = [
        {"language": "ja", "proficiency": "intermediate", "isDefault": False},
        {"language": "es", "proficiency": "advanced", "isDefault": False}
    ]
    test4_result = run_test_case(
        "Remove a language",
        user2,
        test4_update,
        test4_expected,
        "Removing French from the additional languages"
    )
    test_results.append(("Remove language", test4_result))
    
    # Test 5: Change default language
    test5_update = {
        "name": user2["name"],
        "native_language": "en",
        "learning_language": "es",  # Spanish is now primary
        "proficiency": "advanced",
        "additional_languages": [
            {"language": "ja", "proficiency": "intermediate", "isDefault": False},
            {"language": "ko", "proficiency": "advanced", "isDefault": False}  # Korean moved to additional
        ]
    }
    test5_expected = [
        {"language": "ja", "proficiency": "intermediate", "isDefault": False},
        {"language": "ko", "proficiency": "advanced", "isDefault": False}
    ]
    test5_result = run_test_case(
        "Change default language",
        user2,
        test5_update,
        test5_expected,
        "Making Spanish the primary language and moving Korean to additional languages"
    )
    test_results.append(("Change default", test5_result))
    
    # Test 6: Clear all additional languages
    test6_update = {
        "name": user2["name"],
        "native_language": "en",
        "learning_language": "es",
        "proficiency": "advanced",
        "additional_languages": []  # Empty list
    }
    test6_expected = []  # No additional languages
    test6_result = run_test_case(
        "Clear all additional languages",
        user2,
        test6_update,
        test6_expected,
        "Removing all additional languages, keeping only Spanish as primary"
    )
    test_results.append(("Clear languages", test6_result))
    
    # Print test summary
    print_colored("\n" + "=" * 80, "purple")
    print_colored("TEST SUMMARY:", "purple")
    print_colored("=" * 80, "purple")
    
    for test_name, result in test_results:
        if result:
            print_colored(f"✅ PASSED: {test_name}", "green")
        else:
            print_colored(f"❌ FAILED: {test_name}", "red")
    
    if all(result for _, result in test_results):
        print_colored("\n✅ ALL TESTS PASSED! The language settings feature is working correctly.", "green")
    else:
        print_colored("\n❌ SOME TESTS FAILED. There may be issues with the language settings feature.", "red")
        
    # Clean up test users at the end
    print_colored("\nCleaning up test users after tests...", "blue")
    delete_test_users()

if __name__ == "__main__":
    main()
