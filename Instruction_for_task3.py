Directory Structure

Ensure your project folder is structured like this:

ds-final-project/
├── server/
│   ├── Dockerfile
│   └── server.py
├── balancer/
│   ├── Dockerfile
│   └── balancer.py
│   └── hash_ring.py
|── docker-composer.yml

Setup Instructions
Step 1: Build the Server Image
    
docker build -t simple-server ./server
    
Launch the Load Balancer
Start the system using Docker Compose:
    
docker-compose up --build
    
Interacting with the System
Create Server Replicas
To create server containers dynamically, run:
    
curl -X POST http://localhost:5000/add -H "Content-Type: application/json" -d '{"n": 3}'

Access the Load-Balanced Route
You can send requests to the /home endpoint:

curl "http://localhost:5000/home"
