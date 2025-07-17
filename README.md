# FinancialAdviser
Capstone project financial adviser

################################################### 
Steps to Run application without docker 
###################################################
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


################################################### 
Steps to Run application with Docker 
###################################################
#Build and Run with Docker Compose
#From the finadviser/ directory, run:
docker-compose up --build

This will:
Build the backend image using Dockerfile.backend
Build the frontend image using Dockerfile.frontend
Start both containers and link them
FastAPI	http://localhost:8000/docs
Streamlit	http://localhost:8501

#stop the app
docker-compose down

###################################################
Running application by pulling images from dockerHub
###################################################

#Pull the images from dockerHub and start application

docker pull yourusername/finadviser-backend
docker pull yourusername/finadviser-frontend
docker-compose up


###################################################
Push the image to dockerHub
###################################################
docker push yourusername/finadviser-backend:latest
docker push yourusername/finadviser-frontend:latest

