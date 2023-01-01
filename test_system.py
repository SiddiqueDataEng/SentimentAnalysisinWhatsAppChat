#!/usr/bin/env python3
"""
System Test Script for WhatsApp Sentiment Analysis
Tests the core functionality without requiring full deployment
"""

import sys
import os
import requests
import time
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_backend_health():
    """Test if backend is responding"""
    try:
        response = requests.get('http://localhost:8000/health/', timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_frontend():
    """Test if frontend is responding"""
    try:
        response = requests.get('http://localhost:3000/', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

def test_ml_models():
    """Test ML models loading"""
    try:
        # Import Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        import django
        django.setup()
        
        from apps.sentiment.analyzers import MultiModelSentimentAnalyzer
        
        print("🧠 Testing ML models...")
        analyzer = MultiModelSentimentAnalyzer(use_transformers=False)
        analyzer.load_models()
        
        # Test analysis
        test_text = "I love this chat! It's so positive and happy."
        result = analyzer.analyze_text(test_text)
        
        if result and 'ensemble_sentiment' in result:
            sentiment = result['ensemble_sentiment']
            print(f"✅ ML analysis working: '{test_text}' -> {sentiment['label']} ({sentiment['score']:.2f})")
            return True
        else:
            print("❌ ML analysis failed")
            return False
            
    except Exception as e:
        print(f"❌ ML models test failed: {e}")
        return False

def test_preprocessing():
    """Test WhatsApp chat preprocessing"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        import django
        django.setup()
        
        from apps.chat_analysis.preprocessing import WhatsAppChatPreprocessor
        
        print("📝 Testing chat preprocessing...")
        preprocessor = WhatsAppChatPreprocessor()
        
        # Sample WhatsApp chat data
        sample_chat = """12/25/2023, 10:30 - John: Hello everyone! How are you doing?
12/25/2023, 10:31 - Jane: Hi John! I'm doing great, thanks for asking 😊
12/25/2023, 10:32 - Bob: Hey guys! This is awesome!
12/25/2023, 10:33 - John: I'm so happy to see everyone here
12/25/2023, 10:34 - Jane: This chat makes me feel so positive!"""
        
        result = preprocessor.preprocess(sample_chat, anonymize=True)
        
        if result['success'] and result['dataframe'] is not None:
            df = result['dataframe']
            summary = result['summary']
            print(f"✅ Preprocessing working: {summary['total_messages']} messages, {summary['total_participants']} participants")
            return True
        else:
            print(f"❌ Preprocessing failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Preprocessing test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running WhatsApp Sentiment Analysis System Tests")
    print("=" * 60)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Frontend Access", test_frontend),
        ("ML Models", test_ml_models),
        ("Chat Preprocessing", test_preprocessing),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Tests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 All tests passed! System is ready to use.")
        print("\n📊 Access the application:")
        print("   Frontend: http://localhost:3000")
        print("   Backend API: http://localhost:8000/api/")
        print("   Admin Panel: http://localhost:8000/admin/")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        print("💡 Make sure Docker services are running: docker-compose up -d")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)