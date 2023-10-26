import asyncio
import sys


async def stdout_pipe(client):
    events = client.events(decode=True)
    while True:
        for event in events:
            sys.stdout.write(event)
        sys.stdout.flush()
        await asyncio.sleep(0.1)