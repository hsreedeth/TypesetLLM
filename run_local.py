#!/usr/bin/env python

from __future__ import annotations

import asyncio
import os

from uvicorn.config import Config
from uvicorn.server import Server

from src.api import app


async def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    config = Config(app=app, host=host, port=port, log_level="info")
    server = Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
