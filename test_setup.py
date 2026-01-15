"""
Test script to verify system setup
Run this to check if everything is configured correctly
"""

import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("Testing Python package imports...")

    packages = [
        ("langchain", "LangChain"),
        ("langgraph", "LangGraph"),
        ("langchain_google_genai", "LangChain Google Gen AI"),
        ("sqlalchemy", "SQLAlchemy"),
        ("chromadb", "ChromaDB"),
        ("dotenv", "Python-dotenv")
    ]

    failed = []
    for package, name in packages:
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - NOT INSTALLED")
            failed.append(package)

    if failed:
        print(f"\n⚠️  Missing packages: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("\n✓ All packages installed correctly!\n")
    return True

def test_env():
    """Test if .env file is configured"""
    print("Testing environment configuration...")

    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("  ✗ GOOGLE_API_KEY not found in .env file")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Add your Gemini API key")
        print("3. Get key from: https://makersuite.google.com/app/apikey")
        return False

    if api_key == "your_gemini_api_key_here":
        print("  ✗ GOOGLE_API_KEY still has placeholder value")
        print("\nPlease edit .env and add your real API key")
        return False

    print(f"  ✓ GOOGLE_API_KEY found (length: {len(api_key)})")
    print("\n✓ Environment configured correctly!\n")
    return True

def test_gemini_api():
    """Test if Gemini API is accessible"""
    print("Testing Gemini API connection...")

    try:
        from config.settings import get_llm

        llm = get_llm()
        response = llm.invoke("Say 'Hello' in one word")

        print(f"  ✓ API Response: {response.content[:50]}")
        print("\n✓ Gemini API working!\n")
        return True

    except Exception as e:
        print(f"  ✗ API Error: {e}")
        print("\nPossible issues:")
        print("- Invalid API key")
        print("- Network/firewall blocking access")
        print("- API quota exceeded")
        return False

def test_database():
    """Test database initialization"""
    print("Testing database setup...")

    try:
        from database.db_connection import db

        # Try to create tables
        db.init_database()

        # Try a simple query
        result = db.fetch_one("SELECT COUNT(*) as count FROM salary_bands")
        count = result[0] if result else 0

        print(f"  ✓ Database initialized ({count} salary bands)")
        print("\n✓ Database working!\n")
        return True

    except Exception as e:
        print(f"  ✗ Database Error: {e}")
        return False

def test_rag():
    """Test RAG system"""
    print("Testing RAG system...")

    try:
        from rag.policy_vectorstore import policy_rag

        print("  ✓ Policy vectorstore initialized")
        print("\n✓ RAG system working!\n")
        return True

    except Exception as e:
        print(f"  ✗ RAG Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("RECRUITMENT AGENT SYSTEM - SETUP VERIFICATION")
    print("="*60 + "\n")

    tests = [
        ("Package Imports", test_imports),
        ("Environment Variables", test_env),
        ("Gemini API", test_gemini_api),
        ("Database", test_database),
        ("RAG System", test_rag)
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ {name} test failed with exception: {e}\n")
            failed += 1

    print("="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60 + "\n")

    if failed == 0:
        print("🎉 All tests passed! Your system is ready to use.")
        print("\nTry running:")
        print("  python main.py example")
        print("  python main.py interactive")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
