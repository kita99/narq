import asyncio
import importlib
import sys
from functools import wraps
from typing import List

import click
import uvicorn
from click import BadArgumentUsage, Context

from narq.server.app import app
from narq.version import VERSION
from narq.worker import TimerWorker, Worker


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        except asyncio.CancelledError:
            pass

    return wrapper


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(VERSION, "-v", "--version")
@click.option("--verbose", default=False, is_flag=True, help="Enable verbose output.")
@click.argument("narq", required=True)
@click.pass_context
@coro
async def cli(ctx: Context, narq: str, verbose: bool):
    splits = narq.split(":")
    narq_path = splits[0]
    narq = splits[1]
    app.debug = verbose
    try:
        module = importlib.import_module(narq_path)
        r = getattr(module, narq, None)  # type:Narq
        await r.startup()
        ctx.ensure_object(dict)
        ctx.obj["narq"] = r
        ctx.obj["verbose"] = verbose

    except (ModuleNotFoundError, AttributeError) as e:
        raise BadArgumentUsage(ctx=ctx, message=f"Init narq error, {e}.")


@cli.command(help="Start a worker.")
@click.option("-q", "--queue", required=False, multiple=True, help="Queue to consume.")
@click.option(
    "--group-name",
    required=False,
    help="Group name.",
)
@click.option("--consumer-name", required=False, help="Consumer name.")
@click.option("-t", "--with-timer", required=False, is_flag=True, help="Start with timer.")
@click.pass_context
@coro
async def worker(
    ctx: Context, queue: List[str], group_name: str, consumer_name: str, with_timer: bool
):
    narq = ctx.obj["narq"]
    w = Worker(narq, queues=queue, group_name=group_name, consumer_name=consumer_name)
    if with_timer:
        t = TimerWorker(narq)
        await asyncio.gather(w.run(), t.run())
    else:
        await w.run()


@cli.command(help="Start a timer.")
@click.pass_context
@coro
async def timer(ctx: Context):
    narq = ctx.obj["narq"]
    w = TimerWorker(narq)
    await w.run()


@cli.command(
    help="Start rest api server.",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
@click.pass_context
def server(ctx: Context):
    narq = ctx.obj["narq"]
    app.set_narq(narq)

    @app.on_event("shutdown")
    async def shutdown():
        await narq.close()

    kwargs = {
        ctx.args[i][2:].replace("-", "_"): ctx.args[i + 1] for i in range(0, len(ctx.args), 2)
    }
    if "port" in kwargs:
        kwargs["port"] = int(kwargs["port"])
    uvicorn.run("narq.server.app:app", **kwargs)


def main():
    sys.path.insert(0, ".")
    cli()


if __name__ == "__main__":
    main()
