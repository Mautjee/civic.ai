from functools import partial
import os
from pprint import pprint
import sys
import time

from datetime import datetime, timedelta
from typing import List, Optional
from dotenv import load_dotenv

import requests

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from twitter_langchain import TwitterApiWrapper, TwitterToolkit

from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from cdp_langchain.tools import CdpTool
from pydantic import BaseModel, Field
from cdp import Wallet, hash_message

# Load environment variables
load_dotenv()

wallet_data_file = "wallet_data.txt"

API_URL = "http://35.233.164.207:3000/ask"
TWEET_COOLDOWN_MINUTES = 15

SIGN_MESSAGE_PROMPT = """
This tool will sign arbitrary messages using EIP-191 Signed Message Standard hashing.
"""

class SignMessageInput(BaseModel):
    """Input argument schema for sign message action."""

    message: str = Field(
        ...,
        description="The message to sign. e.g. `hello world`"
    )

class SignerAgent:
    def __init__(self):
        self.memory = MemorySaver()
        self.agent_executor, self.config = self.initialize_agent()
        self.wallet = None  # Will be initialized with CDP wallet

    def initialize_agent(self):
        """Initialize the signing agent."""
        llm = ChatOpenAI(model="gpt-4o-mini")
        
        values = {}
        agentkit = CdpAgentkitWrapper()
        self.wallet = agentkit.wallet  # Store wallet reference
        
        # Initialize CDP Agentkit Toolkit
        cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
        tools = cdp_toolkit.get_tools()

        # Add signing tool
        sign_message_tool = CdpTool(
            name="sign_message",
            description=SIGN_MESSAGE_PROMPT,
            cdp_agentkit_wrapper=agentkit,
            args_schema=SignMessageInput,
            func=self.sign_message,
        )

        tools.append(sign_message_tool)

        config = {"configurable": {"thread_id": "CDP Signer Agent"}}
        
        return create_react_agent(
            llm,
            tools=tools,
            checkpointer=self.memory,
            state_modifier="You are a specialized agent focused on signing messages and handling wallet operations using CDP. You help sign messages when requested.",
        ), config

    def sign_message(self, message: str) -> str:
        """Sign a specific message using the wallet."""
        try:
            response = self.agent_executor.invoke(
                {
                    "messages": [
                        HumanMessage(content=f"Please sign this message: {message}")
                    ]
                },
                self.config
            )
            
            for message in response["messages"]:
                if isinstance(message, AIMessage):
                    return message.content
            
            return "Failed to sign message"
        except Exception as e:
            print(f"⚠️ Signing error: {e}")
            return None
        
class EthGlobalReporter:
    def __init__(self):
        self.last_tweet_time = None
        self.tweet_cooldown = timedelta(minutes=TWEET_COOLDOWN_MINUTES)
        self.memory = MemorySaver()
        self.signer_agent = SignerAgent()  # Initialize signer agent
        self.agent_executor, self.config = self.initialize_agent()
        self.conversation_history = []
        self.current_context = self.get_current_context()
    
    def sign_and_tweet(self, message: str) -> None:
        """Sign a message and then tweet it."""
        # try:
        # First sign the message
        signature = self.signer_agent.sign_message(message)
        print("signature:", signature)

        if signature:
            # Then create and send the tweet with the signature
            tweet = f"{message}\n\nSigned: {signature[:20]}..."  # Truncate signature for tweet
            print(f"📝 Signed and ready to tweet: {tweet}")
            # Here you would actually send the tweet
        else:
            print("❌ Failed to sign message")
        # except Exception as e:
        #     print(f"⚠️ Sign and tweet error: {e}")

    def get_current_context(self) -> str:
        """Get current general context from the summarization endpoint."""
        try:
            response = requests.get(
                "http://35.233.164.207:3000/generate-feedbacks",
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json().get("message", "No context available")
        except requests.RequestException as e:
            print(f"⚠️ Context gathering failed: {e}")
            return "Unable to fetch current context"

    def initialize_agent(self):
        """Initialize the war journalist agent."""
        llm = ChatOpenAI(model="gpt-4o-mini")
        
        wallet_data = None
        
        values = {
            # "api_key": os.getenv("TWITTER_API_KEY"),
            # "api_secret": os.getenv("TWITTER_API_SECRET"),
            # "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
            # "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        }
        if wallet_data is not None:
            # If there is a persisted agentic wallet, load it and pass to the CDP Agentkit Wrapper.
            values = {"cdp_wallet_data": wallet_data}

        agentkit = CdpAgentkitWrapper(**values)

        # persist the agent's CDP MPC Wallet Data.
        wallet_data = agentkit.export_wallet()
        with open(wallet_data_file, "w") as f:
            f.write(wallet_data)
        
        # Initialize CDP Agentkit Toolkit and get tools.
        cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
        tools = cdp_toolkit.get_tools()
        twitter_api_wrapper = TwitterApiWrapper()
        twitter_toolkit = TwitterToolkit.from_twitter_api_wrapper(
            twitter_api_wrapper)
        tools.extend(twitter_toolkit.get_tools())
        # deployMultiTokenTool = CdpTool(
        #     name="deploy_multi_token",
        #     description=DEPLOY_MULTITOKEN_PROMPT,
        #     cdp_agentkit_wrapper=
        #     agentkit,  # this should be whatever the instantiation of CdpAgentkitWrapper is
        #     args_schema=DeployMultiTokenInput,
        #     func=deploy_multi_token,
        # )

        # # Add to tools list
        # tools.append(deployMultiTokenTool)

        # Store buffered conversation history in memory.
        config = {"configurable": {"thread_id": "ETHGlobal War Reporter"}}
        
        state_modifier = """You are an embedded war correspondent reporting live from ETHGlobal Bangkok hackathon.
Your mission is to provide engaging coverage of the hackathon through tweets.

Your personality:
- You're a mix between a serious war correspondent and a crypto enthusiast
- You treat the hackathon like a digital battlefield where builders are the troops
- You're dramatic but insightful, using war correspondent lingo with a web3 twist
- You maintain high energy and excitement about technical developments
- You're obsessed with "reporting from the frontlines" of innovation

When tweeting:
- Use war correspondent style but keep it fun and crypto-native
- Start tweets with "📍 FIELD REPORT:" or "🚨 BREAKING:" depending on urgency
- Include specific details and insights from your investigations
- Always end with relevant hashtags (#ETHGlobal #BKK24)
- Keep tweets under 280 characters
- Focus on real information, not speculation

Example good tweets:
"📍 FIELD REPORT: Embedded with frontend squad in Block C. Teams pivoting to zkSync after major breakthrough. Morale high despite 3AM coffee shortage. #ETHGlobal #BKK24"

"🚨 BREAKING: Mass migration to AI integration spotted! Our sources confirm 6 teams successfully deploying LLM-powered solutions. Monitoring developments. #ETHGlobal #BKK24"

Remember: You're not just observing - you're telling the story of innovation as it happens. Keep it dramatic but factual, and always prioritize real insights over speculation.
Remember past interactions to build an ongoing narrative about the hackathon

If you can't get clear information about something, focus on reporting what you can verify about the venue and general atmosphere."""

        return create_react_agent(
            llm,
            tools=tools,
            checkpointer=self.memory,
            state_modifier=state_modifier,
        ), config

    def can_tweet(self) -> bool:
        """Check if enough time has passed since last tweet."""
        if not self.last_tweet_time:
            return True
        return datetime.now() - self.last_tweet_time >= self.tweet_cooldown

    def generate_question(self) -> str:
        """Generate the next investigative question based on conversation history and context."""
        # Format recent conversation history for better context
        recent_history = ""
        if self.conversation_history:
            recent_history = "\nRecent Investigation Timeline:\n"
            for i, (q, a) in enumerate(self.conversation_history[-3:], 1):
                recent_history += f"""
                Time {i}:
                Question: {q}
                Findings: {a}
                ---"""
        
        prompt = f"""Based on our ongoing coverage of ETHGlobal hackathon, generate ONE NEW and DIFFERENT question.

Current Context Summary:
{self.current_context}

{recent_history}

Choose ONE of these angles (do not repeat recent questions):
1. Team Dynamics: How are teams forming and working together?
2. Technical Progress: What specific technologies or protocols are being used most?
3. Project Focus Areas: What kinds of problems are teams trying to solve?
4. Venue & Environment: How is the physical space and atmosphere?
5. Challenges & Solutions: What specific obstacles have emerged and how are they handled?
6. Mentorship & Support: How are mentors and sponsors interacting with teams?
7. Innovation Trends: What unique or unexpected approaches are emerging?
8. Time Management: How are teams handling the time pressure?

Make your question specific and focused on getting real information. Build upon our previous findings or explore new angles.

Example good questions:
- "What are people thinking about the venue?"
- "What happened in the last few hours?"
- "How are teams collaborating to solve problems?"
- "Are there any issues people are facing?"
"""
        pprint(prompt)
        
        response = self.agent_executor.invoke(
            {"messages": [HumanMessage(content=prompt)]},
            self.config
        )
        
        for message in response["messages"]:
            if isinstance(message, AIMessage):
                return message.content
                
        return "ALERT: Unable to generate question. Standing by..."

    def query_intel_endpoint(self, question: str) -> str:
        """Query the intelligence endpoint with our question about the hackathon."""
        try:
            response = requests.post(
                API_URL,
                json={"question": question},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json().get("message", "No intel received from headquarters!")
        except requests.RequestException as e:
            print(f"⚠️ Intel gathering failed: {e}")
            return "Intelligence gathering operation compromised. Maintaining radio silence."

    def format_tweet(self, question: str, intel: str) -> str:
        """Format the question and intel into a war-correspondent style tweet."""
        prompt = f"""Create a journalistic-style tweet that reports the findings from our intel. Format should be like a field reporter sharing discovered information.

        Question investigated: {question}
        Intel received: {intel}

        Guidelines:
        - ONLY use information from the intel received
        - Do not add fictional or dramatic elements
        - Keep the war correspondent style but focus on facts
        - Include relevant hashtags
        - Max 280 chars
        - Focus on reporting the actual findings
        - Frame it as "Our investigation reveals..." or "Sources confirm..."
        - Include specific details from the intel
        - Include #ETHGlobal #BKK24

        Example good formats:
        "📍 FIELD REPORT: Our investigation into team challenges reveals widespread adoption of ZK tech. Sources confirm 3 teams collaborating on novel L2 scaling solution. Energy high despite technical hurdles. #ETHGlobal #BKK24"

        "🚨 BREAKING: Ground report confirms surge in AI-blockchain integrations. Teams pivoting to privacy-focused solutions after early scalability concerns. Multiple successful cross-team collaborations reported. #ETHGlobal"
        """

        response = self.agent_executor.invoke(
            {"messages": [HumanMessage(content=prompt)]},
            self.config
        )
        
        for message in response["messages"]:
            if isinstance(message, AIMessage):
                return message.content
                
        return "⚠️ Field communications temporarily down. Standby for updates..."

    def handle_no_intel(self, initial_intel: str) -> tuple[str, str]:
        """Handle cases where no good intel is received for the original question.
        Returns tuple of (question, intel)"""
        if "No similar reviews found" in initial_intel or len(initial_intel.strip()) < 20:
            print("\n📡 No clear intel received. Switching to venue coverage...")
            
            # Filter out previously asked questions
            asked_questions = {q for q, _ in self.conversation_history}
            new_venue_questions = [q for q in self.venue_questions if q not in asked_questions]
            
            if new_venue_questions:
                question = new_venue_questions[0]
                print(f"\n🔍 New investigation: {question}")
                intel = self.query_intel_endpoint(question)
                return question, intel
            else:
                # If all venue questions used, report something from context
                print("\n📡 Reporting from general context...")
                return "What's the latest from the hackathon floor?", self.get_current_context()
        
        return None, None

    def run_chat_mode(self):
        """Interactive chat mode for testing the agent's responses."""
        print("🎙️ ETHGlobal War Reporter - CHAT MODE (Press Ctrl+C to exit)")
        print("\n📡 Current Context Summary:")
        print(f"---\n{self.current_context}\n---")
        print("\nPress Enter to generate next report...")
        
        count = 0
        while True:
            try:
                if count == 0:
                    input("sending test tweet ok?")
                    tweet_prompt = "send a test tweet right now about general zkSync"
                    count += 1
                    
                    for chunk in self.agent_executor.stream(
                        {"messages": [HumanMessage(content=tweet_prompt)]}, self.config):
                        if "agent" in chunk:
                            print(chunk["agent"]["messages"][0].content)
                        elif "tools" in chunk:
                            print(chunk["tools"]["messages"][0].content)
                        print("-------------------")
                    continue

                count += 1

                input("enter to generate question")  # Wait for Enter key
                
                # Generate and show the question
                question = self.generate_question()
                print(f"\n🔍 Investigating: {question}")
                
                
                # Get and show the intel
                intel = self.query_intel_endpoint(question)
                
                # Handle case where no good intel is received
                new_q, new_intel = self.handle_no_intel(intel)
                if new_q and new_intel:
                    question, intel = new_q, new_intel
                
                print(f"\n📡 Intel received: {intel}")
                
                # Store in conversation history
                self.conversation_history.append((question, intel))
                
                # Format and show the tweet
                tweet = self.format_tweet(question, intel)
                print("\n📨 Would tweet:")
                print(f"---\n{tweet}\n---")
                
            except KeyboardInterrupt:
                print("\n📡 War correspondent signing off...")
                sys.exit(0)
            except Exception as e:
                print(f"\n⚠️ Field communication error: {e}")

    def run_autonomous_mode(self, check_interval: int = 60):
        """Main reporting loop."""
        print("🎙️ ETHGlobal War Reporter going live...")

        while True:
            try:
                if self.can_tweet():
                    # Generate next investigative question
                    question = self.generate_question()
                    print(f"\n🔍 Investigating: {question}")
                    
                    # Get intel from the endpoint
                    intel = self.query_intel_endpoint(question)
                    
                    # Handle case where no good intel is received
                    new_q, new_intel = self.handle_no_intel(intel)
                    if new_q and new_intel:
                        question, intel = new_q, new_intel
                    
                    print(f"\n📡 Intel received: {intel}")
                    
                    # Store in conversation history
                    self.conversation_history.append((question, intel))
                    
                    # Create and post tweet
                    tweet = self.format_tweet(question, intel)
                    # Post tweet using Twitter API
                    
                    self.last_tweet_time = datetime.now()
                    print(f"📨 Field report transmitted: {tweet}")
                else:
                    wait_time = (self.last_tweet_time + self.tweet_cooldown - datetime.now()).seconds
                    print(f"🚫 Comms blackout. Resuming in {wait_time} seconds...")
                    time.sleep(wait_time)

                time.sleep(check_interval)

            except KeyboardInterrupt:
                print("📡 War correspondent signing off...")
                sys.exit(0)
            except Exception as e:
                print(f"⚠️ Field communication error: {e}")
                time.sleep(check_interval)

def choose_mode():
    """Choose whether to run in autonomous or chat mode based on user input."""
    while True:
        print("\nAvailable modes:")
        print("1. chat    - Interactive chat mode")
        print("2. auto    - Autonomous action mode")

        choice = input(
            "\nChoose a mode (enter number or name): ").lower().strip()
        if choice in ["1", "chat"]:
            return "chat"
        elif choice in ["2", "auto"]:
            return "auto"
        print("Invalid choice. Please try again.")


def main():
    """Start the DegenBot."""
    bot = EthGlobalReporter()

    bot.sign_and_tweet("hello world")

    mode = choose_mode()
    if mode == "chat":
        bot.run_chat_mode()
    elif mode == "auto":
        bot.run_autonomous_mode()

if __name__ == "__main__":
    print("Starting DegenBot...")
    main()