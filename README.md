# FinancialAdviser
Capstone project financial adviser<br/>

## Steps to Run application with Docker:
(1) Build build backend & frontend images. Start containers: <br/>
   docker-compose up --build <br/>
(2) Once container are up under PORTS tab change port visibility to Public<br/>
(3) Open the frontend using the link provided under PORTS tab and Submit the request.<br/>
    Results will be displayed on frontend UI<br/>
(4) To stop the containers<br/>
   docker-compose down<br/>

## Steps to Run application without docker: (TODO - Not complete )
cd finadviser
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

#Run FastAPI Server
#From the finadviser/app/ directory:
uvicorn backend_main:app --host 127.0.0.1 --port 8000

#For multiple workers
#gunicorn backend_main:app -k uvicorn.workers.UvicornWorker --workers 4 --bind 127.0.0.1:8000


#This will launch the API server. You can test it at:
http://127.0.0.1:8000/recommend

#Run Streamlit App (UI)
#In a separate terminal (with the same virtualenv activated):
streamlit run app/frontend_ui.py

#This launches the frontend at:
http://localhost:8501

## Running application by pulling images from dockerHub:  (TODO - Not complete)
#Pull the images from dockerHub and start application

docker pull yourusername/finadviser-backend
docker pull yourusername/finadviser-frontend
docker-compose up

## Push the image to dockerHub:  (TODO - Not complete)
docker push yourusername/finadviser-backend:latest
docker push yourusername/finadviser-frontend:latest

# Docker Commands Cheat Sheet for FinancialAdviser Project
## Container Lifecycle
#List running containers
docker ps

#List all containers (including stopped)
docker ps -a

#Start a container
docker start <container>

#Stop a running container
docker stop <container>

#Restart a container
docker restart <container>

#Remove a stopped container
docker rm <container>

#Force remove a running container
docker rm -f <container>

## Image Management

#List local images
docker images

#Remove an image
docker rmi <image>

#Build an image from Dockerfile (in current directory)
docker build -t <image-name> .

#Pull image from Docker Hub
docker pull <image>

#Push image to Docker Hub
docker push <image>

## Docker Compose
#Start all services
docker-compose up

#Build and start all services
docker-compose up --build

#Start all services in background
docker-compose up -d

#Stop and remove all containers, networks, volumes
docker-compose down

#Build only the backend service
docker-compose build backend

#Rebuild and restart backend
docker-compose up --build backend

#Restart a specific service
docker-compose restart backend

#Tail logs of a service
docker-compose logs -f backend

## Logs & Debugging

#View logs of a container
docker logs finadviser_backend

#Follow logs in real time
docker logs -f finadviser_backend

#Open interactive shell inside a container
docker exec -it finadviser_backend bash

#Inspect detailed container info
docker inspect finadviser_backend


## Cleanup & Pruning
#Remove all stopped containers
docker container prune

#Remove all unused images
docker image prune

#Remove all unused data (containers, networks, images, volumes)
docker system prune

## Example Workflows
#Start backend only
docker-compose up backend

#Rebuild and run frontend only
docker-compose up --build frontend

#Open a shell in the backend container
docker exec -it finadviser_backend bash

#Tail backend logs
docker logs -f finadviser_backend

## Step-by-Step: Push Images to Docker Hub
# Tag your images correctly. Retag each local image with your Docker Hub username as the prefix:
#nrslearning/ is my Docker Hub namespace.

docker tag yourusername/finadviser-backend nrslearning/finadviser-backend:latest<br/>
docker tag yourusername/finadviser-frontend nrslearning/finadviser-frontend:latest<br/>

# log in to docker hub
docker login
docker logout -> to logout

# Push the images 
docker push nrslearning/finadviser-backend:latest
docker push nrslearning/finadviser-frontend:latest

