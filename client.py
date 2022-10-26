import threading
import Tkinter as tk
import tk
#import winsound
import socket
import time

class Client:
    def __init__(self, name):
        self.HEADER = 64
        self.PORT = 8000
        self.SERVER = '127.0.0.1'
        self.ADDR = (self.SERVER, self.PORT)
        self.FORMAT = 'utf-8'

        self.connected = False
        self.running = True
        self.connecting = False

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.name = name
        self.data = []

        self.connect()

    def connect(self):
        while not self.connected and self.running:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                print("trying to connect")

                self.client.connect(self.ADDR)
                self.connected = True

            except ConnectionRefusedError:
                print("could not connect")

        if self.connected and self.running:
            self.send_name()
            thread2 = threading.Thread(target=self.receive)
            thread2.start()

    def send(self, msg, msg_type):
        msg = msg.encode(self.FORMAT)
        header = str(len(msg))
        header += ":"
        header += str(msg_type)
        header += ":"
        header = str(header).encode(self.FORMAT)
        header += b' ' * (self.HEADER - len(header))

        self.client.send(header)
        self.client.send(msg)

    def receive(self):
        while self.running:
            try:
                msg_header = self.client.recv(self.HEADER).decode(self.FORMAT)
                if msg_header:
                    msg_length = int(msg_header.split(":")[0])
                    msg = self.client.recv(msg_length).decode(self.FORMAT)

                    print(f"{msg}")
                    self.data.append(f"{msg}")

                    thread3 = threading.Thread(target=self.beep())
                    thread3.start()

            except Exception:
                if self.connected:
                    self.connected = False

    def send_name(self):
        header = self.name
        header += ":"
        # add any more data about the client here upon joining
        header = header.encode(self.FORMAT)
        header += b' ' * (self.HEADER - len(header))

        self.client.send(header)

    def disconnect(self):
        if self.connected:
            self.send("", 3)
            self.client.detach()
        self.connected = False

    def check_change(self):
        if self.data:
            return True
        else:
            return False

    def get_data(self):
        data = self.data[0]
        self.data = self.data[1:]

        return data

    def beep(self):
        #winsound.Beep(1000, 100)
        pass

class ScrollFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.canvas = tk.Canvas(self, borderwidth=0, width=450, height=550)
        self.frame = tk.Frame(self.canvas)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.counter = 0

    def add(self, data):
        label = tk.Label(self.frame, text=data, width=len(data), anchor='w')
        label.grid(row=self.counter, column=0, sticky="ew")
        self.counter += 1

    def onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.update_scrollbar()

    def update_scrollbar(self):
        self.canvas.yview_moveto(1)


class App(tk.Tk, Client):
    def __init__(self):
        super().__init__()

        self.title('chatting v1.0')
        self.geometry('400x600')

        self.msg_frame = ScrollFrame(self)
        self.msg_frame.pack(anchor='nw')

        self.btm_frame = tk.Frame()
        self.btm_frame.pack(anchor='s')

        self.snd_frame = tk.Frame(self.btm_frame, height=50, width=450)
        self.snd_frame.pack(side='left')

        self.con_frame = tk.Frame(self.btm_frame, height=50, width=50)
        self.con_frame.pack(side='right')

        self.label = tk.Label(self.snd_frame, width=40, justify='center', text="enter your name")
        self.label.grid(sticky='nw')

        self.entry = tk.Entry(self.snd_frame, width=40, justify='left')
        self.entry.bind("<Key>", self.handle_entry)
        self.entry.grid(sticky='sw')

        self.con = tk.Label(self.con_frame, width=15, height=3, justify='center', bg='red', text="not connected")
        self.con.grid(sticky='ne')

        self.open = True
        self.first = True
        self.closing = False

    def handle_entry(self, key):
        if key.char == "\r":
            content = self.entry.get()
            self.entry.delete(0, 'end')
            self.entry.update()
            # check commands and whatnot
            if len(content) > 0:
                if not self.first:
                    if list(content)[0] != "/":
                        self.client.send(content, 1)
                        self.msg_frame.add("you -> " + content)
                    else:
                        msg = content[1:].split(" ")
                        valid = True

                        if msg[0] == "rename":
                            if len(msg) != 2:
                                valid = False
                            else:
                                self.client.name = msg[1]

                        elif msg[0] == "msg":
                            if len(msg) != 3:
                                valid = False

                        elif msg[0] == "help":
                            if len(msg) != 1:
                                valid = False

                        if valid:
                            self.client.send(content[1:].replace(" ", ":"), 2)
                        else:
                            self.msg_frame.add("SERVER -> invalid usage, use /help")
                else:
                    self.first = False

                    self.label.config(text="", bg="#F0F0F0")
                    self.client = Client(content)
                    # begin to connect

                    self.connecting_animation()

    def announce(self, msg, duration, background='#F0F0F0'):
        self.label.config(text=msg, bg=background)
        self.label.update()
        time.sleep(duration)
        self.label.config(text="", bg="#F0F0F0")
        self.label.update()

    def connecting_animation(self):
        counter = 0

        thread1 = threading.Thread(target=self.client.connect)
        thread1.start()

        while not self.client.connected and not self.closing:
            self.label.config(text="connecting " + "." * counter)
            self.label.update()
            time.sleep(0.2)
            counter += 1
            if counter > 10:
                counter = 0

        if not self.closing:
            if self.client.connected:
                self.con.config(bg='green', text="connected")
                self.announce(msg="connected", duration=2, background='green')

    def update_socket(self):
        if not self.first:
            if self.client.check_change():
                self.msg_frame.add(self.client.get_data())

            if self.client.connected:
                self.con.config(bg='green', text="connected")
            else:
                self.con.config(bg='red', text="not connected")
                if self.client.running:
                    self.announce(msg="SERVER CLOSED", background='red', duration=2)
                self.on_close()

    def on_close(self):
        print("closing")
        self.closing = True

        if not self.first:
            self.client.disconnect()
            self.client.running = False

        self.open = False


if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close)

    while app.open:
        app.update()
        app.update_idletasks()
        if not app.first:
            app.update_socket()

    app.destroy()
