import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import asyncio

from notion_client import Client, AsyncClient
from notion_client.errors import APIResponseError
from app.core.config import settings
from app.models.schemas import NotionEntry

# Set up logging
logger = logging.getLogger(__name__)

class NotionClient:
    """Client for interacting with the Notion API using the official SDK."""
    
    def __init__(self):
        self.api_key = settings.NOTION_API_KEY
        
        # Get database ID and ensure it has no hyphens
        raw_db_id = settings.NOTION_DATABASE_ID
        self.database_id = raw_db_id.replace("-", "") if raw_db_id else ""
        
        # Print the database ID for debugging
        print(f"Notion database ID (raw): {raw_db_id}")
        print(f"Notion database ID (processed): {self.database_id}")
            
        self.is_configured = bool(self.api_key and self.database_id)
        
        if self.is_configured:
            # Use the synchronous client for now
            self.client = Client(auth=self.api_key)
            logger.info(f"Notion integration initialized with database ID: {self.database_id}")
        else:
            self.client = None
            logger.warning("Notion integration is not fully configured. Some features will be disabled.")
    
    async def check_database_access(self) -> bool:
        """Check if the database exists and is accessible."""
        if not self.is_configured:
            logger.info("Notion integration not configured, skipping database access check")
            return False
            
        try:
            # Try to retrieve the database
            logger.info(f"Checking access to database with ID: {self.database_id}")
            print(f"Attempting to access Notion database with ID: {self.database_id}")
            
            # Ensure we're using the non-hyphenated version
            db_id = self.database_id.replace("-", "")
            self.client.databases.retrieve(database_id=db_id)
            
            logger.info("Successfully accessed the database")
            return True
        except APIResponseError as e:
            logger.error(f"Error accessing database: {str(e)}")
            print(f"Error accessing database: {str(e)}")
            if "404" in str(e):
                logger.error("Database not found. Please check the database ID.")
                print(f"Database ID used: {db_id}")
                print("Database not found. Please check the database ID.")
            elif "403" in str(e):
                logger.error("Permission denied. Please check that the integration has been shared with the database.")
                print("Permission denied. Please check that the integration has been shared with the database.")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking database access: {str(e)}")
            return False
    
    async def get_daily_page(self) -> Optional[str]:
        """Find the Notion page ID for the 'Daily: @Today' page."""
        if not self.is_configured:
            logger.info("Notion integration not configured, skipping get_daily_page")
            return None
            
        # First check if we can access the database
        if not await self.check_database_access():
            logger.error("Cannot access the database, skipping get_daily_page")
            return None
            
        try:
            # Query the database for the Daily page
            logger.info(f"Querying Notion database with ID: {self.database_id}")
            logger.info(f"API Key is {'set' if self.api_key else 'not set'}")
            
            # Ensure we're using the non-hyphenated version
            db_id = self.database_id.replace("-", "")
            
            # First try to find a page with "Daily: @Today" in the title
            try:
                logger.info("Attempting to find 'Daily: @Today' page")
                response = self.client.databases.query(
                    database_id=db_id,
                    filter={
                        "property": "title",
                        "title": {
                            "contains": "Daily: @Today"
                        }
                    }
                )
                
                results = response.get("results", [])
                if results:
                    page_id = results[0]["id"]
                    logger.info(f"Found 'Daily: @Today' page with ID: {page_id}")
                    return page_id
                else:
                    logger.info("No 'Daily: @Today' page found in results")
            except APIResponseError as e:
                logger.error(f"Error querying Notion for 'Daily: @Today': {str(e)}")
            
            # If no results, try a broader search for any "Daily" page
            try:
                logger.info("No page with 'Daily: @Today' found, trying broader search")
                response = self.client.databases.query(
                    database_id=db_id,
                    filter={
                        "property": "title",
                        "title": {
                            "contains": "Daily"
                        }
                    }
                )
                
                results = response.get("results", [])
                if results:
                    page_id = results[0]["id"]
                    logger.info(f"Found 'Daily' page with ID: {page_id}")
                    return page_id
                else:
                    logger.info("No 'Daily' pages found in results")
            except APIResponseError as e:
                logger.error(f"Error querying Notion for 'Daily': {str(e)}")
            
            # If still no results, get the most recent page
            try:
                logger.info("No 'Daily' pages found, getting most recent page")
                response = self.client.databases.query(
                    database_id=db_id,
                    sorts=[
                        {
                            "timestamp": "created_time",
                            "direction": "descending"
                        }
                    ],
                    page_size=1
                )
                
                results = response.get("results", [])
                if results:
                    page_id = results[0]["id"]
                    logger.info(f"Found most recent page with ID: {page_id}")
                    return page_id
                else:
                    logger.info("No pages found in database query results")
            except APIResponseError as e:
                logger.error(f"Error querying Notion for most recent page: {str(e)}")
            
            logger.error("No pages found in the database")
            return None
        except Exception as e:
            logger.error(f"Exception in get_daily_page: {str(e)}")
            logger.error("Please check that:")
            logger.error("1. The database ID is correct")
            logger.error("2. The integration has been shared with the database")
            logger.error("3. The database contains pages")
            return None
    
    async def update_page_content(self, page_id: str, entry: NotionEntry) -> bool:
        """Update a Notion page with journal content."""
        if not self.is_configured:
            logger.info("Notion integration not configured, skipping update_page_content")
            return False
            
        try:
            print(f"Attempting to update page content for page ID: {page_id}")
            
            # Instead of appending blocks, we'll update the page properties
            # This uses the "update" permission instead of "insert" permission
            
            # Create properties to update based on the entry
            properties = {}
            
            # Add journal entries as properties
            if entry.gratitude:
                properties["gratitudes"] = {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "\n".join(entry.gratitude)}
                        }
                    ]
                }
                
            if entry.desire:
                properties["desires"] = {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "\n".join(entry.desire)}
                        }
                    ]
                }
                
            if entry.brag:
                properties["brags"] = {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "\n".join(entry.brag)}
                        }
                    ]
                }
            
            # Update the page properties
            try:
                print(f"Updating page properties for page ID: {page_id}")
                self.client.pages.update(
                    page_id=page_id,
                    properties=properties
                )
                
                logger.info(f"Successfully updated page properties for page ID: {page_id}")
                return True
            except APIResponseError as e:
                error_message = str(e)
                logger.error(f"API error updating Notion page: {error_message}")
                print(f"API error updating Notion page: {error_message}")
                
                if "Insufficient permissions" in error_message:
                    logger.error("The integration doesn't have permission to update this page.")
                    print("The integration doesn't have permission to update this page.")
                    print("Please make sure you've shared the page with the integration and given it appropriate access.")
                    print("Current permissions: Can read content, Can update content, Cannot insert content")
                
                # Log the content we were trying to add for debugging
                logger.debug(f"Failed to update properties: {properties}")
                return False
        except Exception as e:
            logger.error(f"Error updating Notion page: {str(e)}")
            print(f"Error updating Notion page: {str(e)}")
            return False
    
    async def get_completed_prompts(self) -> List[str]:
        """Get a list of completed prompts for the current day."""
        if not self.is_configured:
            logger.info("Notion integration not configured, returning empty completed prompts list")
            return []
            
        try:
            page_id = await self.get_daily_page()
            if not page_id:
                return []
                
            # Get the blocks for the page
            try:
                response = self.client.blocks.children.list(block_id=page_id)
                
                blocks = response.get("results", [])
                completed_prompts = []
                
                for block in blocks:
                    if block.get("type") == "heading_2":
                        rich_text = block.get("heading_2", {}).get("rich_text", [])
                        if rich_text:
                            heading_text = rich_text[0].get("text", {}).get("content", "").lower()
                            if heading_text in ["gratitude", "desire", "brag"]:
                                completed_prompts.append(heading_text)
                
                return completed_prompts
            except APIResponseError as e:
                logger.error(f"API error getting completed prompts: {str(e)}")
                return []
        except Exception as e:
            logger.error(f"Exception in get_completed_prompts: {str(e)}")
            return []
    
    async def save_journal_entry(self, prompt_type: str, content: str) -> bool:
        """Save a journal entry to Notion."""
        if not self.is_configured:
            logger.info(f"Notion integration not configured, skipping save for prompt: {prompt_type}")
            return False
            
        try:
            # Get the Daily page
            print(f"Looking for Daily page to save {prompt_type} entry")
            page_id = await self.get_daily_page()
            if not page_id:
                logger.error("Could not find a suitable page in Notion")
                print("Could not find a suitable page in Notion to save the entry")
                return False
            
            print(f"Found page with ID: {page_id}")
            
            # Get existing entries
            completed_prompts = await self.get_completed_prompts()
            print(f"Current completed prompts: {completed_prompts}")
            
            # Prepare the journal entry
            entry = NotionEntry(
                date=datetime.now().strftime("%Y-%m-%d"),
                gratitude=[content] if prompt_type == "gratitude" else [],
                desire=[content] if prompt_type == "desire" else [],
                brag=[content] if prompt_type == "brag" else []
            )
            
            print(f"Attempting to save {prompt_type} entry: {content}")
            
            # Update the page
            success = await self.update_page_content(page_id, entry)
            if success:
                logger.info(f"Successfully saved {prompt_type} entry to Notion")
                print(f"Successfully saved {prompt_type} entry to Notion")
            else:
                logger.error(f"Failed to save {prompt_type} entry to Notion")
                print(f"Failed to save {prompt_type} entry to Notion")
            return success
        except Exception as e:
            logger.error(f"Exception in save_journal_entry: {str(e)}")
            print(f"Error saving journal entry: {str(e)}")
            return False

# Instantiate the Notion client
notion_client = NotionClient() 