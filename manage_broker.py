import sys
import subprocess
import os

# Constants for paths
CONFIG_DIR = "/etc/mosquitto/conf.d"
SUPERVISOR_CONFIG_DIR = "/etc/supervisor/conf.d"
BASE_PORT = 1883  # Starting port for brokers

def generate_mosquitto_config(client_id):
    port = BASE_PORT + int(client_id[-1])  # Assuming the clientID ends with a number
    config_content = f"""
    pid_file /var/run/mosquitto{client_id}.pid
    listener {port}
    log_dest file /var/log/mosquitto{client_id}.log
    """
    
    with open(f"{CONFIG_DIR}/mosquitto{client_id}.conf", "w") as config_file:
        config_file.write(config_content)

def generate_supervisor_config(client_id):
    supervisor_config_content = f"""
[program:mosquitto{client_id}]
command=mosquitto -c {CONFIG_DIR}/mosquitto{client_id}.conf
autostart=true
autorestart=true
redirect_stderr=true
"""
    with open(f"{SUPERVISOR_CONFIG_DIR}/mosquitto{client_id}.conf", "w") as config_file:
        config_file.write(supervisor_config_content)

def start_broker(client_id):
    generate_mosquitto_config(client_id)
    generate_supervisor_config(client_id)
    subprocess.run(["sudo", "supervisorctl", "reread"])
    subprocess.run(["sudo", "supervisorctl", "update"])
    subprocess.run(["sudo", "supervisorctl", "start", f"mosquitto{client_id}"])

def stop_broker(client_id):
    # Stopping the broker through Supervisor
    subprocess.run(["sudo", "supervisorctl", "stop", f"mosquitto{client_id}"])
    
    # Removing the configuration files
    os.remove(f"{CONFIG_DIR}/mosquitto{client_id}.conf")
    os.remove(f"{SUPERVISOR_CONFIG_DIR}/mosquitto{client_id}.conf")

    # Reread and update Supervisor to reflect removed configuration
    subprocess.run(["sudo", "supervisorctl", "reread"])
    subprocess.run(["sudo", "supervisorctl", "update"])

if __name__ == "__main__":
    action = sys.argv[1]
    client_id = sys.argv[2]

    if action == "start":
        start_broker(client_id)
    elif action == "stop":
        stop_broker(client_id)
