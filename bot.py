import os
import asyncio
from flask import Flask, request, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity

app = Flask(__name__)

# Load SINGLE-TENANT Bot ID & SECRET
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

# Adapter setup
adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

# Health check


@app.route("/", methods=["GET"])
def home():
    return "⚡ Bot is running!", 200

# Bot logic


async def on_turn(turn_context: TurnContext):
    if turn_context.activity.type == "message":
        await turn_context.send_activity(f"You said: {turn_context.activity.text}")
    else:
        await turn_context.send_activity("👋 Hello from Render bot!")

# Messaging endpoint


@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" not in request.headers.get("Content-Type", ""):
        return Response(status=415)

    body = request.json
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    try:
        # Run async adapter inside Flask sync endpoint
        asyncio.run(adapter.process_activity(activity, auth_header, on_turn))
        return Response(status=202)
    except Exception as e:
        print("ERROR:", e)
        return Response(status=500)


# Start server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3978))
    app.run(host="0.0.0.0", port=port)
