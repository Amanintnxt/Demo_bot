import os
import asyncio
from flask import Flask, request, Response
from botbuilder.core import BotFrameworkAdapterSettings, BotFrameworkAdapter, TurnContext
from botbuilder.schema import Activity


APP_ID = os.getenv("MicrosoftAppId")
APP_PASSWORD = os.getenv("MicrosoftAppPassword")
TENANT_ID = os.getenv("MicrosoftAppTenantId")  # Single-tenant directory ID


settings = BotFrameworkAdapterSettings(
    app_id=APP_ID,
    app_password=APP_PASSWORD,
    channel_auth_tenant=TENANT_ID
)

adapter = BotFrameworkAdapter(settings)


app = Flask(__name__)


async def on_turn(turn_context: TurnContext):
    if turn_context.activity.type == "message":
        await turn_context.send_activity(f"You said: {turn_context.activity.text}")
    elif turn_context.activity.type == "conversationUpdate":
        await turn_context.send_activity("👋 Bot connected successfully!")

# -----------------------------
# 📩 MESSAGES ENDPOINT
# -----------------------------


@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" not in request.headers.get("Content-Type", ""):
        return Response("Unsupported Media Type", status=415)

    body = request.json
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    async def process():
        await adapter.process_activity(activity, auth_header, on_turn)

    asyncio.run(process())
    return Response(status=200)

# -----------------------------
# ❤️ HEALTH CHECK
# -----------------------------


@app.route("/", methods=["GET"])
def health_check():
    return "Bot is running."


# -----------------------------
# 🚀 ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3978))
    app.run(host="0.0.0.0", port=port)
