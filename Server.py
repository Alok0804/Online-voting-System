import socket
import threading
from threading import Thread

# Lock to prevent race conditions when accessing shared resources
lock = threading.Lock()

# Function to handle each client's connection and voting process
def client_thread(connection):
    try:
        # Receive voter details
        data = connection.recv(1024)  # Receiving voter details
        log = data.decode().split(' ')

        try:
            # Convert first part of log (Voter ID) to integer for validation
            log[0] = int(log[0])

            # Verify voter credentials (use your own verification method)
            if verify_voter(log[0], log[1]):  # Authenticate
                # Check if the voter has already cast a vote
                if is_eligible_to_vote(log[0]):
                    print(f'Voter Logged in... ID: {log[0]}')
                    connection.send("Authenticate".encode())
                else:
                    print(f'Vote Already Cast by ID: {log[0]}')
                    connection.send("VoteCasted".encode())
                    return
            else:
                print('Invalid Voter')
                connection.send("InvalidVoter".encode())
                return

        except ValueError:
            # Handle case where Voter ID is not an integer
            print('Invalid Credentials: ID should be an integer')
            connection.send("InvalidVoter".encode())
            return

        # Receive the vote after successful authentication
        data = connection.recv(1024)
        print(f"Vote Received from ID: {log[0]}  Processing...")

        # Acquire lock to ensure that vote updating is thread-safe
        lock.acquire()
        try:
            # Update the database with the vote
            if update_vote(data.decode(), log[0]):
                print(f"Vote Casted Successfully by voter ID = {log[0]}")
                connection.send("Successful".encode())
            else:
                print(f"Vote Update Failed by voter ID = {log[0]}")
                connection.send("VoteUpdateFailed".encode())
        finally:
            lock.release()  # Ensure lock is released after database operation

    except Exception as e:
        print(f"Error handling client: {e}")
        connection.send("ServerError".encode())
    
    finally:
        # Close connection
        connection.close()

# Function to start and manage the voting server
def voting_server():
    # Create and bind server socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'  # Explicitly use localhost
    port = 4001  # Match the port in voter.py

    try:
        serversocket.bind((host, port))
    except socket.error as e:
        print(f"Socket binding error: {e}")
        return

    print(f"Waiting for the connection on {host}:{port}")
    serversocket.listen(10)

    # Accept client connections in a loop
    while True:
        try:
            client, address = serversocket.accept()
            print(f'Connected to : {address}')

            # Notify client that the connection was successful
            client.send("Connection Established".encode())

            # Create a new thread for each client connection
            t = Thread(target=client_thread, args=(client,))
            t.start()

        except Exception as e:
            print(f"Error accepting client connection: {e}")

    serversocket.close()

# Placeholder functions for verification and vote updating (replace with actual implementation)
def verify_voter(voter_id, password):
    return True  # Replace with actual voter verification logic

def is_eligible_to_vote(voter_id):
    return True  # Replace with actual logic to check if voter is eligible

def update_vote(vote_data, voter_id):
    return True  # Replace with actual vote updating logic

if __name__ == '__main__':
    voting_server()
