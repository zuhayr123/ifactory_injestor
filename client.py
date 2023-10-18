import socketio

# Define the Socket.io client
sio = socketio.Client()

# Event handler for the 'status' event from the server
@sio.on('status')
def on_status(data):
    print(data)

# Connect to the Socket.io server
def connect_to_server():
    sio.connect('http://localhost:3000')
    print('Connected to Server!')

    try:
        while True:
            client_id = input('Enter clientID to create a new broker (or "exit" to quit): ')
            if client_id.lower() == 'exit':
                break

            sio.emit('create_broker', client_id)
    except KeyboardInterrupt:
        pass
    finally:
        print("\nDisconnecting from Server...")
        sio.disconnect()

if __name__ == "__main__":
    connect_to_server()
