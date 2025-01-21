import tkinter as tk    # Import the tkinter module
from tkinter import messagebox, scrolledtext, simpledialog
import socket
import ssl
import threading

class ChatClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chat Client")

        # Request the user to enter a nickname
        self.nickname = simpledialog.askstring("Nickname", "Enter your nickname:")
        if not self.nickname:
            print("Nickname is required.")
            messagebox.showerror("Error", "Nickname is required.")
            exit(1)

        # Create a scrolled text widget to display messages
        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Create an entry widget to type messages
        self.msg_input = tk.Entry(self.root)
        self.msg_input.bind("<Return>", self.send_message)
        self.msg_input.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Create a socket
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.load_verify_locations("/insert/location/server.crt")
            self.ssl_sock = context.wrap_socket(self.sock, server_hostname="localhost")
            self.ssl_sock.connect(('localhost', 12345))
            self.ssl_sock.send(self.nickname.encode())
        except ConnectionRefusedError as e:
            print(f"Could not connect at this time. Please try again later: {e}")
            messagebox.showerror("Error", "Could not connect at this time. Please try again later")
            exit(1)
        except Exception as e:
            print(f"SSL error during connection: {e}")
            messagebox.showerror("Error", "SSL error during connection")
            exit(1)

        # Start a thread to receive messages
        threading.Thread(target=self.receive_messages).start()

    def send_message(self, event=None):
        msg = self.msg_input.get()
        if msg:
            try:
                self.ssl_sock.send(msg.encode())
                self.chat_display.insert(tk.END, f"You: {msg}\n")
                self.msg_input.delete(0, tk.END)
            except Exception as e:
                print(f"Error sending message: {e}")
                messagebox.showerror("Error", "Could not send message")

    def receive_messages(self):
        while True:
            try:
                data = self.ssl_sock.recv(1024).decode()
                if not data:
                    raise ConnectionResetError("Server disconnected")
                self.chat_display.insert(tk.END, f"{data}\n")
            except Exception as e:
                print(f"Error receiving message: {e}")
                messagebox.showerror("Error", "Could not receive message")
                break

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    client = ChatClient()
    client.run()
