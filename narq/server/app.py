import asyncio
import os

from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from narq import Narq, constants
from narq.server.routes import router
from narq.worker import TimerWorker, Worker


class App(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.narq = None

    def set_narq(self, narq: Narq):
        self.narq = narq

    async def start_worker(self, with_timer=False, block=False):
        w = Worker(narq=self.narq)
        self.narq.on_shutdown(w.terminate)
        if with_timer:
            t = TimerWorker(narq=self.narq)
            self.narq.on_shutdown(t.terminate)
            runner = asyncio.gather(w.run(), t.run())
        else:
            runner = w.run()
        if block:
            await runner
        else:
            asyncio.ensure_future(runner)


app = App(title="API docs of Narq")
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(constants.STATIC_DIR, "narq", "server", "static")),
    name="static",
)
app.include_router(router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"msg": exc.detail},
    )
