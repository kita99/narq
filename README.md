<p align="center">
    <a href="https://narq.readthedocs.io/"><img src="https://github.com/kita99/narq/blob/master/images/logo.png?raw=true" width="600px" alt="narq" /></a>
</p>

[![image](https://img.shields.io/pypi/v/narq.svg?style=flat)](https://pypi.python.org/pypi/narq)
[![image](https://img.shields.io/github/license/kita99/narq)](https://github.com/kita99/narq)
[![image](https://github.com/kita99/narq/workflows/pypi/badge.svg)](https://github.com/kita99/narq/actions?query=workflow:pypi)
[![image](https://github.com/kita99/narq/workflows/ci/badge.svg)](https://github.com/kita99/narq/actions?query=workflow:ci)

## Introduction

narq is a distributed task queue with asyncio and redis, which is built upon
[ReArq](https://github.com/samuelcolvin/arq) (itself a rewrite of [arq](https://github.com/samuelcolvin/arq))


## Motivations

This project is an independent fork of ReArq because it is fundamentally different in its goals. Narq is intended as a
simple to reason about production-grade task queue.

## Features

- AsyncIO support, easy integration with [FastAPI](https://github.com/tiangolo/fastapi).
- Delayed tasks, cron tasks and async task support.
- Full-featured built-in web interface.
- Built-in distributed task lock to ensure a given task is ran one at a time.
- Other powerful features to be discovered.

## Web Interface

![dashboard](./images/dashboard.png)

## Requirements

- Redis >= 5.0


## Quick Start

### Task Definition

```python
# main.py
from narq import Narq

narq = Narq(db_url='mysql://root:123456@127.0.0.1:3306/narq')


@narq.on_shutdown
async def on_shutdown():
    # you can do some clean up work here like close db and so on...
    print("shutdown")


@narq.on_startup
async def on_startup():
    # you can do some initialization work here
    print("startup")


@narq.task(queue="q1")
async def add(self, a, b):
    return a + b


@narq.task(cron="*/5 * * * * * *")  # run task per 5 seconds
async def timer(self):
    return "timer"
```

### Run narq worker

```shell
> narq main:narq worker -q q1 -q q2 # consume tasks from q1 and q2 as the same time
```

```log
2021-03-29 09:54:50.464 | INFO     | narq.worker:_main:95 - Started worker successfully on queue: narq:queue:default
2021-03-29 09:54:50.465 | INFO     | narq.worker:_main:96 - Registered tasks: add, sleep, timer_add
2021-03-29 09:54:50.465 | INFO     | narq.worker:log_redis_info:86 - redis_version=6.2.1 mem_usage=1.43M clients_connected=5 db_keys=6
```

### Run narq timer

If you have timing task or delay task, you should run another command also:

```shell
> narq main:narq timer
```

```log
2021-03-29 09:54:43.878 | INFO     | narq.worker:_main:275 - Start timer successfully
2021-03-29 09:54:43.887 | INFO     | narq.worker:_main:277 - Registered timer tasks: timer_add
2021-03-29 09:54:43.894 | INFO     | narq.worker:log_redis_info:86 - redis_version=6.2.1 mem_usage=1.25M clients_connected=2 db_keys=6
```

Also, you can run timer with worker together by `narq main:narq worker -t`.

### Integration with FastAPI

```python
from fastapi import FastAPI

app = FastAPI()


@app.on_event("shutdown")
async def shutdown() -> None:
    await narq.close()


# then run task in view
@app.get("/test")
async def test():
    job = await add.delay(args=(1, 2))
    # or
    job = await add.delay(kwargs={"a": 1, "b": 2})
    # or
    job = await add.delay(1, 2)
    # or
    job = await add.delay(a=1, b=2)
    result = await job.result(timeout=5)  # wait result for 5 seconds
    print(result.result)
    return result
```


## Start web interface

```shell
> narq main:narq server
Usage: narq server [OPTIONS]

  Start rest api server.

Options:
  --host TEXT         Listen host.  [default: 0.0.0.0]
  -p, --port INTEGER  Listen port.  [default: 8000]
  -h, --help          Show this message and exit..
```

After starting the server, check [https://127.0.0.1:8000/docs](https://127.0.0.1:8000/docs) to see all endpoints and
[https://127.0.0.1:8000](https://127.0.0.1:8000) to use the web interface.

Other options will be passed into `uvicorn` directly, such as `--root-path` etc.

```shell
narq main:narq server --host 0.0.0.0 --root-path /narq
```

### Mount as FastAPI sub app

If you have an existing FastAPI service, to simplify your deployment you might want to mount the narq server as a FastAPI sub app.

```python

from fastapi import FastAPI

from examples.tasks import narq
from narq.server.app import app as narq

app = FastAPI()

app.mount("/narq", narq_app)
narq_app.set_narq(narq)
```

### Start worker inside app

You can also start worker inside your app.

```python
@app.on_event("startup")
async def startup():
    await narq.init()
    await narq.start_worker(with_timer=True, block=False)
```

## ThanksTo

- [arq](https://github.com/samuelcolvin/arq), Fast job queuing and RPC in python with asyncio and redis.
- [ReArq](https://github.com/samuelcolvin/arq), Improved arq rewrite with an API + web interface


## License

This project is licensed under the [Apache-2.0](./LICENSE) License.
