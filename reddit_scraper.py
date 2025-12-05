from typing import List
import os
from utils import *
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
import google.generativeai as genai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from aiolimiter import AsyncLimiter
from datetime import datetime, timedelta

load_dotenv()

two_weeks_ago = datetime.today() - timedelta(days=14)
two_weeks_ago_str = two_weeks_ago.strftime('%Y-%m-%d')

class MCPOverloadedError(Exception):
    pass

mcp_limiter = AsyncLimiter(1, 15)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

server_params = StdioServerParameters(
    command="npx",
    env={
        "API_TOKEN": os.getenv("API_TOKEN"),
        "WEB_UNLOCKER_ZONE": os.getenv("WEB_UNLOCKER_ZONE"),
    },
    args=["@brightdata/mcp"],
)

class GeminiAgent:
    def __init__(self, model, tools):
        self.model = model
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}
    
    async def ainvoke(self, input_data):
        messages = input_data["messages"]
        
        system_message = ""
        user_message = ""
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            elif msg["role"] == "user":
                user_message = msg["content"]
        
        full_prompt = f"{system_message}\n\n{user_message}"
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2000,
                )
            )
            
            topic = user_message.split("'")[1] if "'" in user_message else "the topic"
            print(f"[{datetime.now()}] 🔴 RedditScraper: AI analysis completed for '{topic}'")
            return {"messages": [{"content": response.text}]}
        except Exception as e:
            print(f"[{datetime.now()}] 🔴 RedditScraper: AI analysis failed - {str(e)}")
            topic = user_message.split("'")[1] if "'" in user_message else "the topic"
            return {"messages": [{"content": f"Reddit discussions about {topic} are currently unavailable."}]}

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=15, max=60),
    retry=retry_if_exception_type(MCPOverloadedError),
    reraise=True
)
async def process_topic(agent, topic: str):
    print(f"[{datetime.now()}] 🔴 RedditScraper: Initializing Reddit scraper...")
    print(f"[{datetime.now()}] 🔴 RedditScraper: Two weeks cutoff date: {two_weeks_ago_str}")
    print(f"[{datetime.now()}] 🔴 RedditScraper: Processing topic '{topic}'")
    
    async with mcp_limiter:
        messages = [
            {
                "role": "system",
                "content": f"""You are a Reddit analysis expert. Use available tools to:
                1. Find top 2 posts about the given topic BUT only after {two_weeks_ago_str}, NOTHING before this date strictly!
                2. Analyze their content and sentiment
                3. Create a summary of discussions and overall sentiment"""
            },
            {
                "role": "user",
                "content": f"""Analyze Reddit posts about '{topic}'. 
                Provide a comprehensive summary including:
                - Main discussion points
                - Key opinions expressed
                - Any notable trends or patterns
                - Summarize the overall narrative, discussion points and also quote interesting comments without mentioning names
                - Overall sentiment (positive/neutral/negative)"""
            }
        ]
        
        try:
            response = await agent.ainvoke({"messages": messages})
            return response["messages"][-1]["content"]
        except Exception as e:
            if "Overloaded" in str(e):
                raise MCPOverloadedError("Service overloaded")
            else:
                raise

async def scrape_reddit_topics(topics: List[str]) -> dict[str, dict]:
    print(f"[{datetime.now()}] 🔴 RedditScraper: Starting Reddit scraping for {len(topics)} topics")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print(f"[{datetime.now()}] 🔴 RedditScraper: Initializing MCP session...")
                await session.initialize()
                tools = await load_mcp_tools(session)
                agent = GeminiAgent(model, tools)
                
                reddit_results = {}
                for idx, topic in enumerate(topics, 1):
                    print(f"[{datetime.now()}] 🔴 RedditScraper: Processing topic {idx}/{len(topics)}: '{topic}'")
                    summary = await process_topic(agent, topic)
                    reddit_results[topic] = summary
                    print(f"[{datetime.now()}] 🔴 RedditScraper: Completed '{topic}' - {len(summary)} chars")
                    await asyncio.sleep(5)
                
                print(f"[{datetime.now()}] 🔴 RedditScraper: Completed processing all {len(topics)} topics")
                return {"reddit_analysis": reddit_results}
                
    except Exception as e:
        print(f"[{datetime.now()}] 🔴 RedditScraper: Error in scrape_reddit_topics: {str(e)}")
        reddit_results = {}
        for topic in topics:
            reddit_results[topic] = f"Reddit discussions about {topic} are currently unavailable."
        return {"reddit_analysis": reddit_results}