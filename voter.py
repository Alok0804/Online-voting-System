import tkinter as tk
import socket
from tkinter import *
from VotingPage import votingPg  # Ensure this module exists for the next page
import time  # Added for retry delay

# Establish connection to the server with retries
def establish_connection(retries=5, delay=2):
    host = '127.0.0.1'  # Localhost
    port = 4001  # Match the port in server.py
    
    for attempt in range(retries):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Attempting to connect to server... (Attempt {attempt + 1}/{retries})")
            client_socket.connect((host, port))
            print("Connected to server")

            # Receive connection establishment message
            message = client_socket.recv(1024).decode()
            if message == "Connection Established":
                return client_socket
            else:
                print("Server response did not indicate successful connection.")
                client_socket.close()
                time.sleep(delay)
        except Exception as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    
    print("All connection attempts failed.")
    return None

# Display failure message and reset login page
def failed_return(root, frame1, client_socket, message):
    for widget in frame1.winfo_children():
        widget.destroy()
    message = message + "... \nTry again..."
    Label(frame1, text=message, font=('Helvetica', 12, 'bold')).grid(row=1, column=1)
    try:
        if client_socket:
            client_socket.close()
    except Exception as e:
        print(f"Error while closing socket: {e}")

# Handle login authentication with the server
def log_server(root, frame1, client_socket, voter_ID, password):
    if not (voter_ID and password):
        voter_ID = "0"
        password = "x"

    try:
        # Send credentials to the server
        message = f"{voter_ID} {password}"
        client_socket.send(message.encode())

        # Receive server response
        message = client_socket.recv(1024).decode()

        if message == "Authenticate":
            votingPg(root, frame1, client_socket)
        elif message == "VoteCasted":
            failed_return(root, frame1, client_socket, "Vote has already been cast")
        elif message == "InvalidVoter":
            failed_return(root, frame1, client_socket, "Invalid Voter")
        else:
            failed_return(root, frame1, client_socket, "Server Error")
    except Exception as e:
        print(f"Error during authentication: {e}")
        failed_return(root, frame1, client_socket, "Communication error with the server")

# Build login page GUI
def voterLogin(root, frame1):
    # Attempt to connect to the server
    client_socket = establish_connection()
    if not client_socket:
        failed_return(root, frame1, None, "Unable to connect to server")
        return

    root.title("Voter Login")

    # Clear frame and create login form
    for widget in frame1.winfo_children():
        widget.destroy()
    Label(frame1, text="Voter Login", font=('Helvetica', 18, 'bold')).grid(row=0, column=2, rowspan=1)
    Label(frame1, text="").grid(row=1, column=0)
    Label(frame1, text="Voter ID:", anchor="e", justify=LEFT).grid(row=2, column=0)
    Label(frame1, text="Password:", anchor="e", justify=LEFT).grid(row=3, column=0)

    voter_ID = tk.StringVar()
    password = tk.StringVar()

    e1 = Entry(frame1, textvariable=voter_ID)
    e1.grid(row=2, column=2)
    e3 = Entry(frame1, textvariable=password, show='*')
    e3.grid(row=3, column=2)

    sub = Button(frame1, text="Login", width=10, command=lambda: log_server(root, frame1, client_socket, voter_ID.get(), password.get()))
    Label(frame1, text="").grid(row=4, column=0)
    sub.grid(row=5, column=3, columnspan=2)

    frame1.pack()
    root.mainloop()

# Run the Tkinter application
if __name__ == "__main__":
    root = Tk()
    root.geometry('500x500')
    frame1 = Frame(root)
    voterLogin(root, frame1)
