# 1.2 Sockets, TCP and UDP: under HTTP
# Example "many_clients" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import asyncio


async def handle(reader, writer):
    name = (await reader.readline()).decode().strip()
    await asyncio.sleep(0.1)                 # slow work, but the other clients still run
    writer.write(f"hello {name}\n".encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def client(port, name):
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    writer.write(f"{name}\n".encode())
    await writer.drain()
    reply = await reader.readline()
    writer.close()
    await writer.wait_closed()
    return reply.decode().strip()


async def main():
    server = await asyncio.start_server(handle, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    loop = asyncio.get_running_loop()
    start = loop.time()
    replies = await asyncio.gather(*(client(port, name) for name in ["ann", "bob", "cy"]))
    print(replies)
    print("3 clients that need 0.1 s each took about", round(loop.time() - start, 1), "s in total")
    server.close()
    await server.wait_closed()


asyncio.run(main())
