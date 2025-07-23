# FinancialAdviser
Capstone project financial adviser <br/>

## Steps to Run application with Docker:
(1) Build build backend & frontend images. Start containers: <br/>
   docker-compose up --build <br/>
(2) Once container are up under PORTS tab change port visibility to Public <br/>
(3) Open the frontend using the link provided under PORTS tab and Submit the request. <br/>
    Results will be displayed on frontend UI <br/>
(4) To stop the containers <br/>
   docker-compose down <br/>

## Steps to Run application without docker: (TODO - Not complete )
cd finadviser <br/>
python -m venv venv <br/>
source venv/bin/activate  # On Windows: venv\Scripts\activate <br/>

pip install --upgrade pip <br/>
pip install -r requirements.txt <br/>

#Run FastAPI Server
#From the finadviser/app/ directory: <br/>
uvicorn backend_main:app --host 127.0.0.1 --port 8000 <br/>

#For multiple workers <br/>
#gunicorn backend_main:app -k uvicorn.workers.UvicornWorker --workers 4 --bind 127.0.0.1:8000 <br/>


#This will launch the API server. You can test it at: <br/>
http://127.0.0.1:8000/recommend <br/>

#Run Streamlit App (UI) <br/>
#In a separate terminal (with the same virtualenv activated): <br/>
streamlit run app/frontend_ui.py <br/>

#This launches the frontend at: <br/>
http://localhost:8501 <br/>

## Running application by pulling images from dockerHub:  (TODO - Not complete)
#Pull the images from dockerHub and start application <br/>

docker pull yourusername/finadviser-backend <br/>
docker pull yourusername/finadviser-frontend <br/>
docker-compose up <br/>

## Push the image to dockerHub:  (TODO - Not complete)
docker push yourusername/finadviser-backend:latest <br/>
docker push yourusername/finadviser-frontend:latest <br/>

# Docker Commands Cheat Sheet for FinancialAdviser Project
## Container Lifecycle
#List running containers <br/>
docker ps <br/>

#List all containers (including stopped) <br/>
docker ps -a <br/>

#Start a container <br/>
docker start <container> <br/>

#Stop a running container <br/>
docker stop <container> <br/>

#Restart a container <br/>
docker restart <container> <br/>

#Remove a stopped container <br/>
docker rm <container> <br/>

#Force remove a running container <br/>
docker rm -f <container> <br/>

## Image Management

#List local images <br/>
docker images <br/>

#Remove an image <br/>
docker rmi <image> <br/>

#Build an image from Dockerfile (in current directory) <br/>
docker build -t <image-name> . <br/>

#Pull image from Docker Hub <br/>
docker pull <image> <br/>

#Push image to Docker Hub <br/>
docker push <image> <br/>

## Docker Compose
#Start all services <br/>
docker-compose up <br/>

#Build and start all services <br/>
docker-compose up --build <br/>

#Start all services in background <br/>
docker-compose up -d <br/>

#Stop and remove all containers, networks, volumes <br/>
docker-compose down <br/>

#Build only the backend service <br/>
docker-compose build backend <br/>

#Rebuild and restart backend <br/>
docker-compose up --build backend <br/>

#Restart a specific service <br/>
docker-compose restart backend <br/>

#Tail logs of a service <br/>
docker-compose logs -f backend <br/>

## Logs & Debugging <br/>

#View logs of a container <br/>
docker logs finadviser_backend <br/>

#Follow logs in real time <br/>
docker logs -f finadviser_backend <br/>

#Open interactive shell inside a container   <br/>
docker exec -it finadviser_backend bash   <br/>

#Inspect detailed container info   <br/>
docker inspect finadviser_backend   <br/>


## Cleanup & Pruning <br/>
#Remove all stopped containers   <br/>
docker container prune   <br/>

#Remove all unused images   <br/>
docker image prune   <br/>

#Remove all unused data (containers, networks, images, volumes)  <br/>
docker system prune  

## Example Workflows <br/>
#Start backend only   <br/>
docker-compose up backend   <br/>

#Rebuild and run frontend only   <br/>
docker-compose up --build frontend   <br/>

#Open a shell in the backend container   <br/>
docker exec -it finadviser_backend bash   <br/>

#Tail backend logs   <br/>
docker logs -f finadviser_backend   <br/>

## Step-by-Step: Push Images to Docker Hub
# Tag your images correctly. Retag each local image with your Docker Hub username as the prefix:
#nrslearning/ is my Docker Hub namespace. <br/>

docker tag yourusername/finadviser-backend nrslearning/finadviser-backend:latest  <br/>
docker tag yourusername/finadviser-frontend nrslearning/finadviser-frontend:latest  <br/>

# log in to docker hub <br/>
docker login  <br/>
docker logout -> to logout  <br/>

# Push the images  <br/>
docker push nrslearning/finadviser-backend:latest  <br/>
docker push nrslearning/finadviser-frontend:latest  <br/>

