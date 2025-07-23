# Steps to Run application with Docker:
 (1) Start containers <br/>
 (2) After container are up, under PORTS tab change port visibility to Public <br/>
 (3) Open frontend using the link provided under PORTS tab to lauch the UI <br/>

 ## Steps to Launch application by pulling Docker images from docker hub   
 #Docker images nrslearning/finadviser-backend:latest and nrslearning/finadviser-frontend-streamlit:latest  
  
  ### Start application  
   docker compose up  
 
  ### Stop application  
   docker compose down  
  
 ## Steps to build the Docker images and start application  
  ### Build/Rebuild images and start application  
    docker-compose up --build  
    
  ### Build only backend or only frontend images.  
    docker compose build backend  
    docker compose build frontend_streamlit  
  
  ### Start only one container a time  
    docker compose up -d backend   # in case of detached mode (-d for detached mode)  
               OR  
    docker compose up backend      # in case of Normal mode  
  
    docker compose up -d frontend_streamlit   # in case of detached mode (-d for detached mode)  
               OR  
    docker compose up frontend_streamlit      # in case of Normal mode  

  ### Stop only one container at a time  
    docker compose down backend  
    docker compose down frontend_streamlit          

  ### Command to pull only if image doesn’t exist locally  
    docker compose up --build --pull missing  

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

# Step-by-Step guide to Push Images to Docker Hub
 ## Tag your images correctly. Retag each local image with your Docker Hub username as the prefix:
  #nrslearning/ is my Docker Hub namespace. <br/>
  docker tag yourusername/finadviser-backend  nrslearning/finadviser-backend:latest  <br/>
  docker tag yourusername/finadviser-frontend  nrslearning/finadviser-frontend:latest  <br/>

 ## log in to docker hub <br/>
  docker login  <br/>
  docker logout -> to logout  <br/>

 ## Push the images  <br/>
  docker push nrslearning/finadviser-backend:latest  <br/>
  docker push nrslearning/finadviser-frontend:latest  <br/>

# Command to pull images from dockerHub:
  docker pull nrslearning/finadviser-backend:latest <br/>
  docker pull nrslearning/finadviser-frontend:latest <br/>

# Docker Commands Cheat Sheet for FinancialAdviser Project
  ## Container Lifecycle
    ### List running containers <br/>
      docker ps <br/>

    ### List all containers (including stopped) <br/>
      docker ps -a <br/>

    ### Start a container <br/>
      docker start <container> <br/>

    ### Stop a running container <br/>
      docker stop <container> <br/>

    ### Restart a container <br/>
      docker restart <container> <br/>

    ### Remove a stopped container <br/>
      docker rm <container> <br/>

    ### Force remove a running container <br/>
      docker rm -f <container> <br/>

  ## Image Management
    ### List local images <br/>
      docker images <br/>

    ### Remove an image <br/>
      docker rmi <image> <br/>

    ### Build an image from Dockerfile (in current directory) <br/>
      docker build -t <image-name> . <br/>

    ### Pull image from Docker Hub <br/>
     docker pull <image> <br/>

    ### Push image to Docker Hub <br/>
     docker push <image> <br/>

  ## Docker Compose
    ### Start all services <br/>
     docker-compose up <br/>

    ### Build and start all services <br/>
     docker-compose up --build <br/>

    ### Start all services in background <br/>
     docker-compose up -d <br/>

    ### Stop and remove all containers, networks, volumes <br/>
     docker-compose down <br/>

    ### Build only the backend service <br/>
     docker-compose build backend <br/>

    ### Rebuild and restart backend <br/>
     docker-compose up --build backend <br/>

    ### Restart a specific service <br/>
     docker-compose restart backend <br/>

    ### Tail logs of a service <br/>
     docker-compose logs -f backend <br/>

   ## Logs & Debugging <br/>
    ### View logs of a container <br/>
     docker logs finadviser_backend <br/>

    ### Follow logs in real time <br/>
     docker logs -f finadviser_backend <br/>

    ### Open interactive shell inside a container   <br/>
     docker exec -it finadviser_backend bash   <br/>

    ### Inspect detailed container info   <br/>
     docker inspect finadviser_backend   <br/>

   ## Cleanup & Pruning <br/>
    ### Remove all stopped containers   <br/>
     docker container prune   <br/>

    ### Remove all unused images   <br/>
     docker image prune   <br/>

    ### Remove all unused data (containers, networks, images, volumes)  <br/>
     docker system prune  

   ## Example Workflows <br/>
    ### Start backend only   <br/>
     docker-compose up backend   <br/>

    ### Rebuild and run frontend only   <br/>
     docker-compose up --build frontend   <br/>

## Open a shell in the backend container   <br/>
 docker exec -it finadviser_backend bash   <br/>

## Tail backend logs   <br/>
 docker logs -f finadviser_backend   <br/>

