import asyncio
import time

import tornado.ioloop
import tornado.web
import tornado.websocket

connections = []
data_sent = 0

total_bytes_sent = 0
total_bytes_sent_global = 0


class EchoWebSocketHandler(tornado.websocket.WebSocketHandler):

    async def send_data_throughput(self):
        global total_bytes_sent_global
        total_bytes_sent = 0
        print("WebSocket connection opened")
        start_time = time.time()
        message = "x" * 1024  # 1 KB of data

        while time.time() - start_time < 5:
            await self.write_message(message)
            total_bytes_sent += len(message)
            # await asyncio.sleep(0)  # yield to allow other tasks to run

        end_time = time.time()

        print(f"Data sent: {total_bytes_sent / 1024} KB")
        print(f"Throughput: {total_bytes_sent / 1024 / (end_time - start_time)} KB/s")
        total_bytes_sent_global += total_bytes_sent

    async def open(self):
        print("WebSocket connection opened")
        connections.append(self)
        await self.send_data_throughput()
        if len(connections) == 1:
            task = asyncio.create_task(throughput_test())

    def on_message(self, message):
        print(f"Received message: {message}")
        self.write_message(f"You said: {message}")

    def on_close(self):
        print("WebSocket connection closed")
        print("Data sent total: ", total_bytes_sent_global / 1024, "KB")
        print("Throughput total: ", total_bytes_sent_global / 1024 / 5, "KB/s")
        print(self.close_code, self.close_reason)

    def check_origin(self, origin):
        # Override to allow connections from any origin
        return True


def make_app():
    return tornado.web.Application(
        [
            (r"/", EchoWebSocketHandler),
        ]
    )


async def broadcast(message):
    global data_sent
    for connection in connections:
        connection.write_message(message)
        data_sent += len(message)


async def throughput_test():
    msg = "x" * 1024  # 1 KB of data
    duration = 5.0
    end_time = asyncio.get_event_loop().time() + duration
    while asyncio.get_event_loop().time() < end_time:
        broadcast(msg)

    print(f"Data sent: {data_sent / 1024} KB")
    print(f"Throughput: {data_sent / 1024 / duration} KB/s")


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("WebSocket server is running at ws://localhost:8888/")
    tornado.ioloop.IOLoop.current().start()
