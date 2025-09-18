#!/usr/bin/env python3
"""
Test script per verificare il sistema di tracking potenziato
"""

import requests
import json
import time
from datetime import datetime

def test_client_info():
    """Test endpoint client-info"""
    print("🧪 Testing /api/client-info endpoint...")
    
    try:
        response = requests.get('http://localhost:5000/api/client-info')
        if response.status_code == 200:
            data = response.json()
            print("✅ Client info endpoint working!")
            print(f"   IP: {data['client_info'].get('ip')}")
            print(f"   User-Agent: {data['client_info'].get('user_agent')}")
            print(f"   Device: {data['client_info'].get('device')}")
            return True
        else:
            print(f"❌ Client info endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing client info: {e}")
        return False

def test_tracking():
    """Test tracking endpoint with mock data"""
    print("\n🧪 Testing /api/track endpoint with mock data...")
    
    mock_data = {
        "sessionId": f"test_session_{int(time.time())}",
        "eventType": "location_captured",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "accuracy": 10,
            "screen": {
                "width": 1920,
                "height": 1080
            }
        }
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/track',
            json=mock_data,
            headers={'User-Agent': 'TestScript/1.0 (Windows NT 10.0; Win64; x64)'}
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ Tracking endpoint working!")
            print(f"   Status: {result.get('status')}")
            return True
        else:
            print(f"❌ Tracking endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing tracking: {e}")
        return False

def check_files():
    """Check if tracking files are being created"""
    print("\n🗂️ Checking tracking files...")
    
    from pathlib import Path
    
    files_to_check = [
        "data/tracking/client_info.jsonl",
        "tracking_backup.txt"
    ]
    
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {file_path} exists ({size} bytes)")
            
            # Show last few lines
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"   Last entry: {lines[-1].strip()[:100]}...")
            except Exception as e:
                print(f"   Error reading file: {e}")
        else:
            print(f"❌ {file_path} not found")

def main():
    print("🚀 TESTING ENHANCED GPS TRACKER")
    print("=" * 40)
    
    # Test client info endpoint
    client_ok = test_client_info()
    
    # Test tracking endpoint
    track_ok = test_tracking()
    
    # Check if files are created
    check_files()
    
    print("\n📊 TEST SUMMARY:")
    print(f"Client Info API: {'✅' if client_ok else '❌'}")
    print(f"Tracking API: {'✅' if track_ok else '❌'}")
    
    if client_ok and track_ok:
        print("\n🎉 All tests passed! Enhanced tracking is working.")
        print("\n💡 Next steps:")
        print("• Visit http://localhost:5000/maps to generate real tracking data")
        print("• Check the files in data/tracking/ folder")
        print("• Monitor tracking_backup.txt for IP and UA data")
    else:
        print("\n⚠️ Some tests failed. Make sure the web server is running:")
        print("python web_server.py")

if __name__ == "__main__":
    main()