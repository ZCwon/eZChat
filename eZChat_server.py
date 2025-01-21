import tkinter as tk
from tkinter import messagebox
import socket
import ssl
import threading


# Here is a list to keep track of all the connected clients
clients = []
nicknames = {}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Functions for handling client connections
def handle_client(conn, addr):
    print(f"Connected by {addr}")
    try:
        # Request and store the nickname of the client
        conn.send("Welcome to the chat! Please enter your nickname:".encode())
        nickname = conn.recv(1024).decode().strip()
        nicknames[conn] = nickname
        clients.append(conn)
        broadcast(f"{nickname} joined the chat!".encode(), conn)

        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    raise ConnectionResetError("Client disconnected")
                # Broadcast the received messages to all clients
                broadcast(f"{nickname}: {data.decode()}".encode(), conn)
            except Exception as e:
                print(f"Error receiving data from {addr}: {e}")
                break
    finally:
        conn.close()
        del nicknames[conn]
        clients.remove(conn)
        print(f"Connection closed by {addr}")
        broadcast(f"{nickname} has left the chat.\n".encode(), None)

# Function to broadcast messages to all clients
def broadcast(msg, sender_conn):
    for client in clients:
        if client != sender_conn:
            try:
                client.send(msg)
            except Exception as e:
                print(f"Error broadcasting message: {e}")
                client.close()
                del nicknames[client]
                clients.remove(client)

# Start setting up the chat server
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
try:
    context.load_cert_chain(certfile="/insert/location/server.crt", keyfile="/insert/location/server.key")
except FileNotFoundError as e:
    print(f"Certificate or key file not found: {e}")
    messagebox.showerror("Error", "Certificate or key file not found")
    exit(1)
except ssl.SSLError as e:
    print(f"SSL error loading certificate or key: {e}")
    messagebox.showerror("Error", "SSL error loading certificate or key")
    exit(1)

try:
    server_socket.bind(('0.0.0.0', 12345))
except OSError as e:
    print(f"Error binding address: {e}")
    messagebox.showerror("Error", "Error binding address")
    exit(1)

server_socket.listen()
print("Server has started...")

try:
    while True:
        try:
            conn, addr = server_socket.accept()
            ssl_conn = context.wrap_socket(conn, server_side=True)
            threading.Thread(target=handle_client, args=(ssl_conn, addr)).start()
        except Exception as e:
            print(f"Error accepting connection: {e}")
except KeyboardInterrupt:
    print("Server shutting down...")
finally:
    for client in clients:
        client.close()
    server_socket.close()
