#!/usr/bin/env python3
"""
Setup Verification Script for WhatsApp Sentiment Analysis
Verifies the project structure and basic functionality without requiring services
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (missing)")
        return False

def check_directory_structure():
    """Check if all required directories and files exist"""
    print("📁 Checking project structure...")
    
    required_files = [
        # Backend files
        ("backend/manage.py", "Django management script"),
        ("backend/core/settings.py", "Django settings"),
        ("backend/core/urls.py", "Main URL configuration"),
        ("backend/apps/authentication/models.py", "Authentication models"),
        ("backend/apps/chat_analysis/models.py", "Chat analysis models"),
        ("backend/apps/sentiment/analyzers.py", "Sentiment analyzers"),
        ("backend/requirements.txt", "Backend dependencies"),
        ("backend/Dockerfile", "Backend Docker configuration"),
        
        # Frontend files
        ("frontend/package.json", "Frontend dependencies"),
        ("frontend/src/App.js", "Main React component"),
        ("frontend/src/pages/Home.js", "Home page component"),
        ("frontend/src/pages/Upload.js", "Upload page component"),
        ("frontend/Dockerfile", "Frontend Docker configuration"),
        
        # Configuration files
        ("docker-compose.yml", "Docker Compose configuration"),
        (".env.example", "Environment variables template"),
        ("README.md", "Project documentation"),
        ("DEPLOYMENT.md", "Deployment guide"),
        
        # Setup scripts
        ("setup.sh", "Linux/Mac setup script"),
        ("setup.bat", "Windows setup script"),
    ]
    
    passed = 0
    for filepath, description in required_files:
        if check_file_exists(filepath, description):
            passed += 1
    
    print(f"\n📊 Structure check: {passed}/{len(required_files)} files found")
    return passed == len(required_files)

def check_python_syntax():
    """Check Python files for syntax errors"""
    print("\n🐍 Checking Python syntax...")
    
    python_files = [
        "backend/manage.py",
        "backend/core/settings.py",
        "backend/apps/authentication/models.py",
        "backend/apps/chat_analysis/models.py",
        "backend/apps/sentiment/analyzers.py",
        "test_system.py",
    ]
    
    passed = 0
    for filepath in python_files:
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    compile(f.read(), filepath, 'exec')
                print(f"✅ Syntax OK: {filepath}")
                passed += 1
            except SyntaxError as e:
                print(f"❌ Syntax Error in {filepath}: {e}")
            except Exception as e:
                print(f"⚠️  Could not check {filepath}: {e}")
        else:
            print(f"❌ File not found: {filepath}")
    
    print(f"\n📊 Syntax check: {passed}/{len(python_files)} files passed")
    return passed == len(python_files)

def check_docker_files():
    """Check Docker configuration files"""
    print("\n🐳 Checking Docker configuration...")
    
    docker_files = [
        ("docker-compose.yml", "Docker Compose"),
        ("backend/Dockerfile", "Backend Dockerfile"),
        ("frontend/Dockerfile", "Frontend Dockerfile"),
    ]
    
    passed = 0
    for filepath, description in docker_files:
        if check_file_exists(filepath, description):
            # Basic validation - check if file is not empty
            try:
                with open(filepath, 'r') as f:
                    content = f.read().strip()
                    if content:
                        print(f"  ✅ {description} has content")
                        passed += 1
                    else:
                        print(f"  ❌ {description} is empty")
            except Exception as e:
                print(f"  ⚠️  Could not read {description}: {e}")
    
    print(f"\n📊 Docker check: {passed}/{len(docker_files)} files valid")
    return passed == len(docker_files)

def check_frontend_structure():
    """Check frontend structure"""
    print("\n⚛️  Checking React frontend structure...")
    
    frontend_files = [
        "frontend/package.json",
        "frontend/src/App.js",
        "frontend/src/index.js",
        "frontend/src/components/Header.js",
        "frontend/src/pages/Home.js",
        "frontend/src/pages/Upload.js",
        "frontend/src/pages/Analysis.js",
        "frontend/src/pages/Dashboard.js",
    ]
    
    passed = 0
    for filepath in frontend_files:
        if check_file_exists(filepath, f"Frontend file"):
            passed += 1
    
    print(f"\n📊 Frontend check: {passed}/{len(frontend_files)} files found")
    return passed == len(frontend_files)

def main():
    """Run all verification checks"""
    print("🔍 WhatsApp Sentiment Analysis - Setup Verification")
    print("=" * 60)
    
    # Change to project directory if script is run from elsewhere
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    checks = [
        ("Project Structure", check_directory_structure),
        ("Python Syntax", check_python_syntax),
        ("Docker Configuration", check_docker_files),
        ("Frontend Structure", check_frontend_structure),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            results.append((check_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Verification Results:")
    print("=" * 60)
    
    passed = 0
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Checks passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 All verification checks passed!")
        print("\n🚀 Next steps:")
        print("1. Run setup script: ./setup.sh (Linux/Mac) or setup.bat (Windows)")
        print("2. Or manually start with: docker-compose up -d")
        print("3. Test the system: python test_system.py")
        print("\n📖 See DEPLOYMENT.md for detailed instructions")
    else:
        print(f"\n⚠️  {len(results) - passed} checks failed.")
        print("Please check the project structure and fix any missing files.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)