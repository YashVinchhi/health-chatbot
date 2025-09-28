#!/usr/bin/env python3
"""
Test script to verify RASA integration and multilingual functionality
Run this to test your newly trained model with the GUI
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

# Test messages in different languages
TEST_MESSAGES = [
    # English tests
    {"message": "Hello", "language": "English", "expected_intent": "greet"},
    {"message": "I have fever", "language": "English", "expected_intent": "ask_symptoms"},
    {"message": "Find hospitals near me", "language": "English", "expected_intent": "ask_hospital_info"},
    {"message": "COVID vaccine information", "language": "English", "expected_intent": "ask_vaccination"},
    {"message": "Emergency help needed", "language": "English", "expected_intent": "emergency_help"},

    # Hindi tests
    {"message": "नमस्ते", "language": "Hindi", "expected_intent": "greet"},
    {"message": "मुझे बुखार है", "language": "Hindi", "expected_intent": "ask_symptoms"},
    {"message": "नजदीकी अस्पताल", "language": "Hindi", "expected_intent": "ask_hospital_info"},
    {"message": "कोविड का टीका", "language": "Hindi", "expected_intent": "ask_vaccination"},

    # Telugu tests
    {"message": "వనక్కం", "language": "Telugu", "expected_intent": "greet"},
    {"message": "నాకు జ్వరం వచ్చింది", "language": "Telugu", "expected_intent": "ask_symptoms"},
    {"message": "దగ్గరలో హాస్పిటల్", "language": "Telugu", "expected_intent": "ask_hospital_info"},

    # Tamil tests
    {"message": "வணக்கம்", "language": "Tamil", "expected_intent": "greet"},
    {"message": "எனக்கு காய்ச்சல் வந்துருச்சு", "language": "Tamil", "expected_intent": "ask_symptoms"},

    # Bengali tests
    {"message": "নমস্কার", "language": "Bengali", "expected_intent": "greet"},
    {"message": "আমার জ্বর হয়েছে", "language": "Bengali", "expected_intent": "ask_symptoms"},
]

class RASATestSuite:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.rasa_url = "http://localhost:5005"
        self.session_id = f"test_session_{int(time.time())}"
        self.results = []

    async def test_backend_connection(self):
        """Test if backend is responding"""
        print("🔄 Testing backend connection...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/api/health/rasa/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Backend connected: {data}")
                        return True
                    else:
                        print(f"❌ Backend error: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Backend connection failed: {e}")
            return False

    async def test_rasa_direct(self):
        """Test direct RASA connection"""
        print("🔄 Testing direct RASA connection...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.rasa_url}/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ RASA server online: {data.get('model_file', 'Model loaded')}")
                        return True
                    else:
                        print(f"❌ RASA error: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ RASA connection failed: {e}")
            return False

    async def test_multilingual_messages(self):
        """Test multilingual message processing"""
        print("\n🌍 Testing multilingual message processing...")
        print("=" * 60)

        async with aiohttp.ClientSession() as session:
            for i, test_case in enumerate(TEST_MESSAGES, 1):
                print(f"\n📝 Test {i}/{len(TEST_MESSAGES)} - {test_case['language']}")
                print(f"   Message: '{test_case['message']}'")

                try:
                    # Send to backend chat endpoint
                    payload = {
                        "message": test_case["message"],
                        "session_id": self.session_id
                    }

                    async with session.post(
                        f"{self.backend_url}/api/health/chat",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    ) as response:

                        if response.status == 200:
                            data = await response.json()

                            result = {
                                "test_id": i,
                                "language": test_case["language"],
                                "message": test_case["message"],
                                "expected_intent": test_case["expected_intent"],
                                "actual_intent": data.get("intent", "unknown"),
                                "confidence": data.get("confidence", 0),
                                "response": data.get("response", "")[:100] + "..." if len(data.get("response", "")) > 100 else data.get("response", ""),
                                "source": data.get("source", "unknown"),
                                "success": True
                            }

                            # Check if intent matches
                            intent_match = result["actual_intent"] == result["expected_intent"]
                            confidence_good = result["confidence"] > 0.5 if result["confidence"] else False

                            print(f"   Intent: {result['actual_intent']} {'✅' if intent_match else '❌'}")
                            print(f"   Confidence: {result['confidence']:.2f} {'✅' if confidence_good else '❌'}")
                            print(f"   Source: {result['source']}")
                            print(f"   Response: {result['response']}")

                            self.results.append(result)

                        else:
                            print(f"   ❌ HTTP Error: {response.status}")
                            self.results.append({
                                "test_id": i,
                                "language": test_case["language"],
                                "message": test_case["message"],
                                "error": f"HTTP {response.status}",
                                "success": False
                            })

                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    self.results.append({
                        "test_id": i,
                        "language": test_case["language"],
                        "message": test_case["message"],
                        "error": str(e),
                        "success": False
                    })

                # Small delay between tests
                await asyncio.sleep(0.5)

    def generate_test_report(self):
        """Generate a comprehensive test report"""
        print("\n📊 MULTILINGUAL RASA TEST REPORT")
        print("=" * 60)

        successful_tests = [r for r in self.results if r.get("success", False)]
        failed_tests = [r for r in self.results if not r.get("success", False)]

        print(f"📈 Total Tests: {len(self.results)}")
        print(f"✅ Successful: {len(successful_tests)}")
        print(f"❌ Failed: {len(failed_tests)}")
        print(f"📊 Success Rate: {len(successful_tests)/len(self.results)*100:.1f}%")

        # Language breakdown
        languages = {}
        for result in successful_tests:
            lang = result.get("language", "Unknown")
            if lang not in languages:
                languages[lang] = 0
            languages[lang] += 1

        print(f"\n🌍 Language Support:")
        for lang, count in languages.items():
            print(f"   {lang}: {count} tests passed")

        # Intent accuracy
        if successful_tests:
            intent_matches = sum(1 for r in successful_tests
                               if r.get("actual_intent") == r.get("expected_intent"))
            print(f"\n🎯 Intent Accuracy: {intent_matches}/{len(successful_tests)} ({intent_matches/len(successful_tests)*100:.1f}%)")

        # Confidence scores
        confidence_scores = [r.get("confidence", 0) for r in successful_tests if r.get("confidence")]
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            print(f"🔢 Average Confidence: {avg_confidence:.2f}")

        # Source breakdown
        sources = {}
        for result in successful_tests:
            source = result.get("source", "unknown")
            if source not in sources:
                sources[source] = 0
            sources[source] += 1

        print(f"\n📡 Response Sources:")
        for source, count in sources.items():
            print(f"   {source}: {count} responses")

        # Failed tests details
        if failed_tests:
            print(f"\n❌ Failed Tests Details:")
            for test in failed_tests:
                print(f"   {test['language']}: '{test['message'][:30]}...' - {test.get('error', 'Unknown error')}")

        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.results),
                "successful": len(successful_tests),
                "failed": len(failed_tests),
                "success_rate": len(successful_tests)/len(self.results)*100 if self.results else 0
            },
            "results": self.results
        }

        with open(f"rasa_test_report_{int(time.time())}.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Detailed report saved to: rasa_test_report_{int(time.time())}.json")

async def main():
    """Main test function"""
    print("🚀 RASA Multilingual Health Chatbot Test Suite")
    print("=" * 60)
    print("This script tests your newly trained RASA model integration")
    print("with multilingual support for Hindi, Telugu, Tamil, Bengali, and English")
    print()

    test_suite = RASATestSuite()

    # Test backend connection
    backend_ok = await test_suite.test_backend_connection()

    # Test RASA connection
    rasa_ok = await test_suite.test_rasa_direct()

    if not backend_ok:
        print("\n⚠️  Backend is not responding. Make sure to:")
        print("   1. Run: cd backend && python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload")
        return

    if not rasa_ok:
        print("\n⚠️  RASA server is not responding. Make sure to:")
        print("   1. Run: cd rasa_bot && rasa run --enable-api --cors '*' --port 5005")
        print("   2. Also run: rasa run actions --port 5055 (in another terminal)")
        return

    # Run multilingual tests
    await test_suite.test_multilingual_messages()

    # Generate report
    test_suite.generate_test_report()

    print("\n🎉 Testing completed!")
    print("\nNext steps:")
    print("1. If tests passed, your RASA model is working correctly!")
    print("2. Open http://localhost:3000 to use the GUI")
    print("3. Try the test messages in the web interface")
    print("4. Check the test report JSON file for detailed results")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        print("Please make sure all services are running:")
        print("- Backend API (port 8000)")
        print("- RASA Server (port 5005)")
        print("- RASA Actions (port 5055)")
