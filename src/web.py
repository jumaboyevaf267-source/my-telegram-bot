from aiohttp import web


async def health(request):
    return web.Response(text="Bot is running!")


async def start_web(port: int):

    app = web.Application()

    app.router.add_get("/", health)

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()
