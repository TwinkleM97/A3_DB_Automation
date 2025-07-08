#!/usr/bin/env python3
"""
Selenium Test Script for PROG8850 Assignment 3
Tests user registration, login, and database validation
"""

import os
import random
import time
import tempfile
from dotenv import load_dotenv
import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Load environment variables
load_dotenv()

class SeleniumTester:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.test_username = f"selenium_user_{random.randint(1000, 9999)}"
        self.test_password = "test123"
        self.base_url = "http://localhost:5000"
        
    def setup_driver(self):
        """Setup Chrome driver with headless options"""
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        print(f"Chrome driver initialized successfully")
        
    def test_registration(self):
        """Test user registration functionality"""
        print(f"Testing registration for user: {self.test_username}")
        
        try:
            # Navigate to registration page
            self.driver.get(f"{self.base_url}/register")
            
            # Fill registration form
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys(self.test_username)
            
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.send_keys(self.test_password)
            
            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Wait for redirect to login page
            self.wait.until(EC.url_contains("/login"))
            
            # Check for success message
            success_message = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
            )
            
            print(f"3.Registration successful: {success_message.text}")
            return True
            
        except TimeoutException:
            print("Registration failed: Timeout waiting for elements")
            return False
        except Exception as e:
            print(f"Registration failed: {str(e)}")
            return False
    
    def test_login(self):
        """Test user login functionality"""
        print(f"Testing login for user: {self.test_username}")
        
        try:
            # Navigate to login page
            self.driver.get(f"{self.base_url}/login")
            
            # Fill login form
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys(self.test_username)
            
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.send_keys(self.test_password)
            
            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Wait for redirect to welcome page
            self.wait.until(EC.url_contains("/welcome"))
            
            # Check for welcome message
            welcome_heading = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            
            if self.test_username in self.driver.page_source:
                print(f"Login successful: Welcome page displayed")
                return True
            else:
                print("Login failed: Username not found on welcome page")
                return False
                
        except TimeoutException:
            print("Login failed: Timeout waiting for elements")
            return False
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
    
    def test_database_validation(self):
        """Validate that user data was correctly inserted into database"""
        print(f"Testing database validation for user: {self.test_username}")
        
        try:
            # Connect to database
            conn = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", 3306)),
                user=os.getenv("DB_USER", "student"),
                password=os.getenv("DB_PASS", "studentpass"),
                database=os.getenv("DB_NAME", "prog8850_db")
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s", (self.test_username,))
            result = cursor.fetchone()
            
            if result:
                print(f" Database validation successful: User found in database")
                print(f"   - User ID: {result[0]}")
                print(f"   - Username: {result[1]}")
                print(f"   - Password stored: {'Yes' if result[2] else 'No'}")
                return True
            else:
                print(" Database validation failed: User not found in database")
                return False
                
        except mysql.connector.Error as err:
            print(f" Database validation failed: {err}")
            return False
        except Exception as e:
            print(f" Database validation failed: {str(e)}")
            return False
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()
    
    def test_logout(self):
        """Test logout functionality"""
        print(f"Testing logout functionality")
        
        try:
            # Click logout button
            logout_link = self.driver.find_element(By.LINK_TEXT, "Logout")
            logout_link.click()
            
            # Wait for redirect to login page
            self.wait.until(EC.url_contains("/login"))
            
            # Check for logout message
            logout_message = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "alert-info"))
            )
            
            print(f"Logout successful: {logout_message.text}")
            return True
            
        except TimeoutException:
            print("Logout failed: Timeout waiting for elements")
            return False
        except Exception as e:
            print(f"Logout failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("Starting Selenium Tests for PROG8850 Assignment 3")
        print("=" * 60)
        
        test_results = []
        
        try:
            self.setup_driver()
            
            # Test 1: Registration
            test_results.append(self.test_registration())
            
            # Test 2: Login
            test_results.append(self.test_login())
            
            # Test 3: Database validation
            test_results.append(self.test_database_validation())
            
            # Test 4: Logout
            test_results.append(self.test_logout())
            
        except Exception as e:
            print(f"Test suite failed: {str(e)}")
            test_results.append(False)
        
        finally:
            if self.driver:
                self.driver.quit()
                print("Chrome driver closed")
        
        # Print test results
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        
        test_names = ["Registration", "Login", "Database Validation", "Logout"]
        passed = sum(test_results)
        total = len(test_results)
        
        for i, (test_name, result) in enumerate(zip(test_names, test_results)):
            status = "PASSED" if result else "❌ FAILED"
            print(f"{i+1}. {test_name}: {status}")
        
        print(f"\n Overall Result: {passed}/{total} tests passed")
        
        if passed == total:
            print(" ALL TESTS PASSED! Your application is working correctly.")
            return True
        else:
            print(" Some tests failed. Please check the output above.")
            return False

def main():
    """Main function to run the tests"""
    tester = SeleniumTester()
    success = tester.run_all_tests()
    
    if success:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()