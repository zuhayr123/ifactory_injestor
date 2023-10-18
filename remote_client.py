import socketio

# Constants
SOCKETIO_URL = "http://192.168.1.5:3000"

sio = socketio.Client()

def send_new_client(clientID):
    sio.emit('create_broker', {'client_id': clientID})

def send_delete_broker(clientID):
    sio.emit('delete_broker', {'client_id': clientID})

def main():
    sio.connect(SOCKETIO_URL)

    while True:
        print("1: Create Broker")
        print("2: Delete Broker")
        print("3: Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            clientID = input("Enter clientID to create a broker: ")
            send_new_client(clientID)
        elif choice == "2":
            clientID = input("Enter clientID to delete a broker: ")
            send_delete_broker(clientID)
        elif choice == "3":
            sio.disconnect()
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
