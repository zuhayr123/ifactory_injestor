import os
import sys

def create_mosquitto_config(clientID, port):
    config_content = f"""
pid_file /var/run/mosquitto/mosquitto.{clientID}.pid
listener {port}
allow_anonymous true
"""

    with open(f"/etc/mosquitto/conf.d/{clientID}.conf", "w") as f:
        f.write(config_content)

def create_supervisor_config(clientID, port):
    config_content = f"""
[program:mosquitto_{clientID}]
command=mosquitto -c /etc/mosquitto/conf.d/{clientID}.conf
stdout_logfile=/var/log/supervisor/mosquitto_{clientID}.out.log
stderr_logfile=/var/log/supervisor/mosquitto_{clientID}.err.log
autostart=true
autorestart=true
redirect_stderr=true
"""

    with open(f"/etc/supervisor/conf.d/mosquitto_{clientID}.conf", "w") as f:
        f.write(config_content)

def create_pid_directory():
    if not os.path.exists("/var/run/mosquitto"):
        os.system("sudo mkdir /var/run/mosquitto/")
        os.system("sudo chown mosquitto: /var/run/mosquitto/")

def start_broker(clientID):
    os.system(f"sudo supervisorctl reread")
    os.system(f"sudo supervisorctl add mosquitto_{clientID}")
    os.system(f"sudo supervisorctl start mosquitto_{clientID}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: create_broker.py <clientID> <port>")
        sys.exit(1)

    clientID = sys.argv[1]
    port = sys.argv[2]

    create_pid_directory()  # Ensure the PID directory is created and has correct permissions.
    create_mosquitto_config(clientID, port)
    create_supervisor_config(clientID, port)
    start_broker(clientID)
    
    print(f"Broker for {clientID} started on port {port}")

