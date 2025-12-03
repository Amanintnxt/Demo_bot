import os
from aiohttp import web
from botbuilder.core import BotFrameworkAdapterSettings, BotFrameworkAdapter, TurnContext
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity

# Get credentials from environment
APP_ID = os.environ.get("MicrosoftAppId")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword")
# Required for single-tenant
TENANT_ID = os.environ.get("MicrosoftAppTenantId")

# Configure adapter with tenant ID for single-tenant authentication
settings = BotFrameworkAdapterSettings(
    app_id=APP_ID,
    app_password=APP_PASSWORD,
    tenant_id=TENANT_ID  # Critical for single-tenant bots
)
adapter = BotFrameworkAdapter(settings)


async def on_turn(turn_context: TurnContext):
    """Handle incoming activities"""
    if turn_context.activity.type == "message":
        await turn_context.send_activity(f"You said: {turn_context.activity.text}")
    elif turn_context.activity.type == "conversationUpdate":
        await turn_context.send_activity("👋 Bot connected successfully!")


async def messages(req: web.Request):
    """Handle messages endpoint"""
    if "application/json" not in req.headers.get("Content-Type", ""):
        return web.Response(status=415)

    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    # Process activity with authentication
    await adapter.process_activity(activity, auth_header, on_turn)
    return web.Response(status=202)


# Create app
app = web.Application(middlewares=[aiohttp_error_middleware])
app.router.add_post("/api/messages", messages)
app.router.add_get("/", lambda req: web.Response(text="Bot is running."))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3978))
    web.run_app(app, host="0.0.0.0", port=port)
