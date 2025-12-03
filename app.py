import os
import asyncio
from flask import Flask, request, Response
from botbuilder.core import BotFrameworkAdapterSettings, BotFrameworkAdapter, TurnContext
from botbuilder.schema import Activity
from botframework.connector.auth import MicrosoftAppCredentials

# Get credentials from environment
APP_ID = os.environ.get("MicrosoftAppId")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword")
TENANT_ID = os.environ.get("MicrosoftAppTenantId")

# Trust Teams service URLs to prevent authentication issues
MicrosoftAppCredentials.trust_service_url("https://smba.trafficmanager.net/")
MicrosoftAppCredentials.trust_service_url(
    "https://smba.trafficmanager.net/teams/")

# Configure adapter with auth_tenant_id for single-tenant authentication
settings = BotFrameworkAdapterSettings(
    app_id=APP_ID,
    app_password=APP_PASSWORD
)
# Set auth_tenant_id as an attribute (not a constructor parameter)
settings.auth_tenant_id = TENANT_ID
adapter = BotFrameworkAdapter(settings)

# Create Flask app
app = Flask(__name__)


async def on_turn(turn_context: TurnContext):
    """Handle incoming activities"""
    if turn_context.activity.type == "message":
        await turn_context.send_activity(f"You said: {turn_context.activity.text}")
    elif turn_context.activity.type == "conversationUpdate":
        await turn_context.send_activity("👋 Bot connected successfully!")


@app.route("/api/messages", methods=["POST"])
def messages():
    """Handle messages endpoint"""
    if "application/json" not in request.headers.get("Content-Type", ""):
        return Response("Unsupported Media Type", status=415)

    activity = Activity().deserialize(request.json)
    auth_header = request.headers.get("Authorization", "")

    async def process():
        await adapter.process_activity(activity, auth_header, on_turn)

    # Run async function in event loop
    asyncio.run(process())
    return Response(status=200)


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return "Bot is running. with gunicorn"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3978))
    app.run(host="0.0.0.0", port=port)
