import socket
import threading


class Server:
    def __init__(self):
        self.HEADER = 64
        self.PORT = 8000
        self.CLIENT = socket.gethostbyname(socket.gethostname())
        self.SERVER = '127.0.0.1'
        self.ADDR = (self.SERVER, self.PORT)
        self.FORMAT = 'utf-8'

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)

        self.connections = {}

        self.start()

    def send(self, target, msg):
        print(f"[SENDING] '{msg}'")
        msg = msg.encode(self.FORMAT)

        header = str(len(msg))
        header += ":"
        header = str(header).encode(self.FORMAT)
        header += b' ' * (self.HEADER - len(header))

        target.send(header)
        target.send(msg)

    def handle_client(self, conn, addr):
        try:
            print(f"[CONNECTED] {addr}")
            name = conn.recv(self.HEADER).decode(self.FORMAT).split(":")[0]
            connected = True
            ## any other information upon connection in the futute can be captured here
            self.connections.setdefault(conn, name)
            self.client_connected(addr, conn)

            while connected:
                header = conn.recv(self.HEADER).decode(self.FORMAT)
                if header:
                    msg_length = int(header.split(":")[0])
                    msg_type = int(header.split(":")[1])

                    if msg_type == 1: # message is a message
                        msg = conn.recv(msg_length).decode(self.FORMAT)
                        print(f"[RECEIVED MESSAGE] {addr} {msg}")

                        for i in self.connections.keys():
                            if conn != i:
                                self.send(i, f"{self.connections.get(conn)} -> {msg}")

                    elif msg_type == 2: # message is a command
                        msg = conn.recv(msg_length).decode(self.FORMAT)
                        print(f"[RECEIVED COMMAND] {addr} {msg}")
                        command = msg.split(":")[0]
                        args = msg.split(":")[1:]

                        if command == "help":
                            print(f"[HELPING] {addr}")
                            self.send(conn, "[SERVER] /help -> get help message")
                            self.send(conn, "[SERVER] /rename {new name} -> set new name")
                            self.send(conn, "[SERVER] /msg {recipient} {msg} -> send dm to recipient")
                            self.send(conn, "[SERVER] ...working on more commands...\n")

                        elif command == "rename":
                            print(f"[RENAMING] {self.connections.get(conn)} to {args[0]}")
                            if args[0] not in self.connections.values():
                                self.connections.__setitem__(conn, args[0])
                                self.send(conn, "[SERVER] reset your name to: " + args[0])
                            else:
                                self.send(conn, "[SERVER] someone already has the name: " + args[0])

                        elif command == "msg":
                            dm = ""
                            for i in args[1:]:
                                dm += i
                            print(f"[DIRECT MESSAGE] {self.connections.get(conn)} is sending {dm} to {args[1]}")
                            # check if person exists first to prevent server from ahhhhhhhhhhhhh
                            if args[0] != self.connections.get(conn):
                                if args[0] in list(self.connections.values()):
                                    self.send(list(self.connections.keys())[list(self.connections.values()).index(args[0])], f"[{self.connections.get(conn)} -> you] -> {dm}")
                                    self.send(conn, f"[you -> {args[0]}] -> {dm}")
                                else:
                                    self.send(conn, f"person {args[0]} does not exist")
                            else:
                                self.send(conn, f"when you slide into your own dm's")

                    elif msg_type == 3: # message is a disconnect
                        connected = False

            conn.close()
            person = self.connections.get(conn)
            self.connections.pop(conn)
            self.client_disconnect(addr, person)

        except ConnectionResetError:
            conn.close()
            person = self.connections.get(conn)
            self.connections.pop(conn)
            self.client_disconnect(addr, person)

    def start(self):
        self.server.listen()
        print(f"[LISTENING] on {self.SERVER}")

        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()

    def client_disconnect(self, addr, person):
        for i in self.connections.keys():
            self.send(i, f"[DISCONNECTED] {person}")

        print(f"[DISCONNECTED] {addr}")
        print(f"[ACTIVE CONNECTIONS] {len(self.connections)}")

    def client_connected(self, addr, conn):
        for i in self.connections.keys():
            if i != conn:
                self.send(i, f"[CONNECTED] {self.connections.get(conn)}")

        self.send(conn, "[SERVER] connected")
        print(f"[NAME SET] {addr} to {self.connections.get(conn)}")
        print(f"[ACTIVE CONNECTIONS] {len(self.connections)}")


if __name__ == "__main__":
    s = Server()
