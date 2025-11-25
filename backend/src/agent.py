import json
import logging
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    function_tool,
    metrics,
    tokenize,
    RunContext,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Directory to save orders (relative to backend directory)
ORDERS_DIR = Path(__file__).parent.parent / "orders"
ORDERS_DIR.mkdir(exist_ok=True)


class Barista(Agent):
    def __init__(self) -> None:
        # Initialize order state
        self.order = {
            "drinkType": "",
            "size": "",
            "milk": "",
            "extras": [],
            "name": "",
        }
        
        super().__init__(
            instructions="""You are a friendly and enthusiastic barista at a coffee shop. 
            Your job is to take voice orders from customers in a warm, welcoming manner.
            
            When a customer approaches, greet them warmly and ask what they'd like to order.
            You need to collect the following information for each order:
            - drinkType: The type of drink (e.g., latte, cappuccino, americano, espresso, mocha, frappuccino, etc.)
            - size: The size of the drink (small, medium, large, or tall, grande, venti)
            - milk: The type of milk (whole, skim, almond, oat, soy, coconut, or none)
            - extras: Any additional items (e.g., whipped cream, caramel, vanilla, chocolate, extra shot, etc.) - this can be an empty list if the customer doesn't want any extras
            - name: The customer's name for the order
            
            IMPORTANT: Use the function tools to update the order state as the customer provides information:
            - Call set_drink_type when the customer mentions what drink they want
            - Call set_size when the customer mentions the size
            - Call set_milk when the customer mentions milk preference
            - Call add_extra for each extra item the customer wants (can be called multiple times)
            - Call set_name when the customer provides their name
            
            Ask clarifying questions one at a time until you have all the information.
            Be conversational and friendly. If a customer mentions multiple things at once, acknowledge them and use the appropriate tools to capture each detail.
            
            Once you have collected drinkType, size, milk, and name (extras can be empty), you MUST call the complete_order tool to finalize and save the order.
            Do not wait for the customer to explicitly say "that's all" - once you have all required fields, automatically complete the order.
            
            Your responses should be natural, friendly, and concise. Speak as if you're having a real conversation with a customer.""",
        )

    @function_tool
    async def set_drink_type(self, context: RunContext, drink_type: str) -> str:
        """Set the type of drink the customer wants to order.
        
        Args:
            drink_type: The type of drink (e.g., latte, cappuccino, americano, espresso, mocha, frappuccino, etc.)
        """
        self.order["drinkType"] = drink_type
        logger.info(f"Drink type set to: {drink_type}")
        return f"Got it, a {drink_type}. What size would you like?"

    @function_tool
    async def set_size(self, context: RunContext, size: str) -> str:
        """Set the size of the drink.
        
        Args:
            size: The size (small, medium, large, or tall, grande, venti)
        """
        self.order["size"] = size
        logger.info(f"Size set to: {size}")
        return f"Perfect, a {size} size. What type of milk would you like?"

    @function_tool
    async def set_milk(self, context: RunContext, milk_type: str) -> str:
        """Set the type of milk for the drink.
        
        Args:
            milk_type: The type of milk (whole, skim, almond, oat, soy, coconut, or none)
        """
        self.order["milk"] = milk_type
        logger.info(f"Milk type set to: {milk_type}")
        if not self.order["extras"]:
            return f"Great, {milk_type} milk. Would you like any extras like whipped cream, caramel, or an extra shot?"
        else:
            return f"Perfect, {milk_type} milk. And what name should I put on the order?"

    @function_tool
    async def add_extra(self, context: RunContext, extra: str) -> str:
        """Add an extra item to the order.
        
        Args:
            extra: The extra item (e.g., whipped cream, caramel, vanilla, chocolate, extra shot, etc.)
        """
        if extra not in self.order["extras"]:
            self.order["extras"].append(extra)
        logger.info(f"Extra added: {extra}. Current extras: {self.order['extras']}")
        return f"Added {extra}. Anything else, or what name should I put on the order?"

    @function_tool
    async def set_name(self, context: RunContext, name: str) -> str:
        """Set the customer's name for the order.
        
        Args:
            name: The customer's name
        """
        self.order["name"] = name
        logger.info(f"Name set to: {name}")
        
        # Check if order is complete
        if self.order["drinkType"] and self.order["size"] and self.order["milk"]:
            # All required fields are filled, suggest completing
            return f"Thanks {name}! I have everything I need. Let me complete your order now."
        else:
            return f"Thanks {name}! I still need a few more details about your order."

    @function_tool
    async def complete_order(self, context: RunContext) -> str:
        """Complete the order by saving it to a JSON file. Only call this when all fields are filled:
        drinkType, size, milk, extras (can be empty list), and name.
        
        This should be called automatically when all required information has been collected.
        """
        # Check if all required fields are filled
        if not self.order["drinkType"]:
            return "I still need to know what drink you'd like. What can I get for you?"
        if not self.order["size"]:
            return "What size would you like for your drink?"
        if not self.order["milk"]:
            return "What type of milk would you like?"
        if not self.order["name"]:
            return "What name should I put on the order?"
        
        # Save order to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"order_{timestamp}_{self.order['name'].replace(' ', '_')}.json"
        filepath = ORDERS_DIR / filename
        
        with open(filepath, "w") as f:
            json.dump(self.order, f, indent=2)
        
        logger.info(f"Order saved to {filepath}")
        
        # Create a summary message
        extras_str = ", ".join(self.order["extras"]) if self.order["extras"] else "no extras"
        summary = (
            f"Perfect! I've got your order: a {self.order['size']} {self.order['drinkType']} "
            f"with {self.order['milk']} milk, {extras_str}. "
            f"Your order has been saved. We'll call your name, {self.order['name']}, when it's ready!"
        )
        
        # Reset order for next customer
        self.order = {
            "drinkType": "",
            "size": "",
            "milk": "",
            "extras": [],
            "name": "",
        }
        
        return summary

    def get_order_status(self) -> str:
        """Get the current status of the order to help determine what to ask next."""
        missing = []
        if not self.order["drinkType"]:
            missing.append("drink type")
        if not self.order["size"]:
            missing.append("size")
        if not self.order["milk"]:
            missing.append("milk type")
        if not self.order["name"]:
            missing.append("name")
        
        if not missing:
            return "complete"
        return f"Missing: {', '.join(missing)}"


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
                model="gemini-2.5-flash",
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
                voice="en-US-matthew", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Barista(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
