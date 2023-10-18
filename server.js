const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { exec } = require('child_process');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const activeBrokers = new Set();

var BASE_PORT = 1883;

io.on('connection', (socket) => {
    console.log('A user connected');

    socket.on('create_broker', (clientID) => {
        console.log(`Received clientID: ${clientID}`);
        
        if (!activeBrokers.has(clientID)) {
            exec(`python3 manage_broker.py start ${clientID}`, (error, stdout, stderr) => {
                if (error) {
                    console.error(`exec error: ${error}`);
                    socket.emit('status', `Error starting broker for clientID: ${clientID}`);
                    return;
                }
                
                activeBrokers.add(clientID);
                let port = getPortFromClientID(clientID);
                
                // Printing the port number on the command line
                console.log(`Started broker for clientID: ${clientID} on port: ${port}`);
                
                socket.emit('status', { message: `Broker started for clientID: ${clientID}`, port: port });
            });
        } else {
            let port = getPortFromClientID(clientID);
            console.log(`Broker already running for clientID: ${clientID} on port: ${port}`);
            socket.emit('status', { message: `Broker already running for clientID: ${clientID}`, port: port });
        }
    });    
});

function getPortFromClientID(clientID) {
    let lastDigit = parseInt(clientID.slice(-1), 10);
    return isNaN(lastDigit) ? null : BASE_PORT + lastDigit;
}

server.listen(3000, () => {
  console.log('listening on *:3000');
});
