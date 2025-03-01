#!/usr/bin/env python3
"""
Simple script to test the Trinity Journaling API endpoints.
Run this after starting the server with python run.py

Usage with Anaconda:
    1. Make sure your conda environment is activated: conda activate trinity
    2. Run the test script: python test_api.py
"""

import httpx
import asyncio
import json
from typing import Dict, Any
from app.utils.notion import notion_client
from app.core.config import settings


async def test_health_endpoint(base_url: str) -> None:
    """Test the health check endpoint."""
    print("\n📋 Testing health check endpoint...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/api/v1/health")
            response.raise_for_status()
            
            print(f"✅ Health check successful! Response: {response.json()}")
        except Exception as e:
            print(f"❌ Health check failed: {str(e)}")


async def test_journal_process(base_url: str) -> None:
    """Test the journal processing endpoint with different inputs."""
    
    test_cases = [
        {
            "name": "Gratitude example",
            "payload": {
                "transcription": "I'm grateful for my family and friends who support me.",
                "current_prompt": "gratitude",
                "completed_prompts": []
            }
        },
        {
            "name": "Desire example",
            "payload": {
                "transcription": "I want to travel to Japan next year.",
                "current_prompt": "desire",
                "completed_prompts": ["gratitude"]
            }
        },
        {
            "name": "Brag example",
            "payload": {
                "transcription": "I'm proud of finishing that difficult project at work.",
                "current_prompt": "brag",
                "completed_prompts": ["gratitude", "desire"]
            }
        },
        {
            "name": "Mixed prompt example",
            "payload": {
                "transcription": "I want to get better at playing guitar, but I'm grateful for the progress I've made so far.",
                "current_prompt": "desire",
                "completed_prompts": []
            }
        },
        {
            "name": "User stuck example",
            "payload": {
                "transcription": "Hmm, I don't really know what to say about gratitude today.",
                "current_prompt": "gratitude",
                "completed_prompts": []
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Testing journal processing with: {test_case['name']}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{base_url}/api/v1/journal/process",
                    json=test_case["payload"],
                    timeout=60.0  # Longer timeout for LLM processing
                )
                response.raise_for_status()
                
                result = response.json()
                print(f"✅ Test successful!")
                print(f"📊 Detected prompt: {result['detected_prompt']}")
                print(f"🔄 Prompt changed: {result['prompt_changed']}")
                print(f"📝 Formatted response: {result['formatted_response']}")
                print(f"💾 Saved to Notion: {result['saved_to_notion']}")
            
            except Exception as e:
                print(f"❌ Test failed: {str(e)}")


async def test_completed_prompts(base_url: str) -> None:
    """Test the completed prompts endpoint."""
    print("\n📋 Testing completed prompts endpoint...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/api/v1/journal/completed-prompts")
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Successfully retrieved completed prompts!")
            print(f"📊 Completed prompts: {result}")
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")


async def test_notion_integration() -> None:
    """Test the Notion integration directly."""
    print("\n📋 Testing Notion integration...")
    
    print(f"\n📊 Notion Configuration:")
    print(f"API Key: {'Set' if settings.NOTION_API_KEY else 'Not set'}")
    print(f"Database ID: {settings.NOTION_DATABASE_ID}")
    print(f"Database ID (without hyphens): {settings.NOTION_DATABASE_ID.replace('-', '') if settings.NOTION_DATABASE_ID else 'None'}")
    
    print("\n📊 Testing database access...")
    db_access = await notion_client.check_database_access()
    if db_access:
        print("✅ Successfully accessed the database!")
    else:
        print("❌ Failed to access the database.")
    
    print("\n📊 Testing page retrieval...")
    page_id = await notion_client.get_daily_page()
    if page_id:
        print(f"✅ Successfully found a page with ID: {page_id}")
    else:
        print("❌ Failed to find a suitable page.")
    
    print("\n📊 Testing completed prompts retrieval...")
    completed_prompts = await notion_client.get_completed_prompts()
    print(f"📊 Completed prompts: {completed_prompts}")


async def main():
    base_url = "http://localhost:8000"
    
    print("=" * 40)
    print("🧪 TRINITY JOURNALING API TEST SCRIPT")
    print("=" * 40)
    
    await test_health_endpoint(base_url)
    await test_completed_prompts(base_url)
    await test_notion_integration()
    await test_journal_process(base_url)
    
    print("\n" + "=" * 40)
    print("🏁 Testing complete!")
    print("=" * 40)


if __name__ == "__main__":
    asyncio.run(main())