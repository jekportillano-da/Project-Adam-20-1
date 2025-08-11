#!/usr/bin/env python3
"""Quick test to verify servers are responsive"""
import requests
import sys

def test_url(url, name):
    try:
        response = requests.get(url, timeout=5)
        print(f"✓ {name}: {response.status_code}")
        return True
    except Exception as e:
        print(f"✗ {name}: {e}")
        return False

print("Testing servers...")
test_url("http://localhost:8080/login", "Prod Login")
test_url("http://localhost:8080/docs", "Prod Docs")
test_url("http://localhost:8000/demo", "Demo Home")
test_url("http://localhost:8000/demo/bills", "Demo Bills")
