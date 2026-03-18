#!/usr/bin/env python3
"""
SmartFlow AI Query Tool
Ask questions to your multi-agent financial AI system
"""

import requests
import json
import sys

def ask_ai(question):
    """Send a question to the SmartFlow AI system"""
    try:
        url = 'http://localhost:8000/api/agents/test-query/test-entity'
        data = {'query': question}
        headers = {'Content-Type': 'application/json'}

        print(f'🤖 Asking SmartFlow AI: "{question}"')
        print('=' * 60)

        response = requests.post(url, json=data, headers=headers, timeout=60)

        if response.status_code == 200:
            result = response.json()
            print(f'🎯 Agent Used: {result.get("agent_used")}')
            print(f'📋 Intent: {result.get("intent")}')
            print()
            print('💡 AI Response:')
            print('-' * 40)
            print(result.get('output', 'No response'))
            print('-' * 40)
            print('✅ Query completed successfully!')
        else:
            print(f'❌ Error: {response.status_code}')
            print('Response:', response.text[:300])

    except requests.exceptions.ConnectionError:
        print('❌ Connection Error: Make sure the backend server is running on port 8000')
        print('Start it with: cd backend && $env:PYTHONPATH = "."; python -m uvicorn app.main:app --reload --port 8000')
    except Exception as e:
        print(f'❌ Error: {e}')

def main():
    if len(sys.argv) > 1:
        question = ' '.join(sys.argv[1:])
        ask_ai(question)
    else:
        print("🤖 SmartFlow AI Query Tool")
        print("Usage: python ask_ai.py 'Your question here'")
        print()
        print("Example questions:")
        print("- 'Who should I pay first?'")
        print("- 'How is my business doing?'")
        print("- 'What are my biggest risks?'")
        print("- 'Am I safe to pay all vendors?'")
        print()
        print("Or run: python ask_ai.py 'Who should I pay first?'")

if __name__ == "__main__":
    main()