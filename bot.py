import os
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

# -----------------------------
# HEALTH CHECK FOR RENDER
# -----------------------------


@app.route("/", methods=["GET"])
def home():
    return "⚡ Python bot is running!", 200

# -----------------------------
# SIMPLE BOT LOGIC
# -----------------------------


async def on_turn(turn_context: TurnContext):
    if turn_context.activity.type == "message":
        await turn_context.send_activity(f"You said: {turn_context.activity.text}")
    else:
        await turn_context.send_activity("👋 Hello! Simple Python Bot is running.")

# -----------------------------
# /api/messages ENDPOINT
# -----------------------------


@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers.get("Content-Type", ""):
        body = request.json
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    try:
        task = adapter.process_activity(activity, auth_header, on_turn)
        return Response(status=202)
    except Exception as e:
        print("Error:", e)
        return Response(status=500)


# -----------------------------
# RUN APP (LOCAL + RENDER)
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3978))
    print(f"Bot running at http://0.0.0.0:{port}/api/messages")
    app.run(host="0.0.0.0", port=port)
