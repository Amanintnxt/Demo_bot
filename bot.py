import os
from aiohttp import web
from botbuilder.core import BotFrameworkAdapterSettings, BotFrameworkAdapter, TurnContext
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity

APP_ID = os.environ.get("MicrosoftAppId")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword")

adapter = BotFrameworkAdapter(
    BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD))


async def on_turn(turn_context: TurnContext):
    if turn_context.activity.type == "message":
        await turn_context.send_activity(f"You said: {turn_context.activity.text}")
    else:
        await turn_context.send_activity("👋 Running aiohttp bot on Render!")


async def messages(req: web.Request):
    if "application/json" not in req.headers.get("Content-Type", ""):
        return web.Response(status=415)

    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    await adapter.process_activity(activity, auth_header, on_turn)
    return web.Response(status=202)


app = web.Application(middlewares=[aiohttp_error_middleware])
app.router.add_post("/api/messages", messages)
app.router.add_get("/", lambda req: web.Response(text="Bot is running."))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3978))
    web.run_app(app, host="0.0.0.0", port=port)
