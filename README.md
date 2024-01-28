# Simple Web application that accepst messages from users and stores them in JSON file"

**You can run this application by running directly main.py with python**


**To run this application you need docker**

**How to run this application**
   - Clone this repository into a folder of choice on your local machine using the following command:
     ```
     git clone https://github.com/rafalradx/web-app-with-form
     ```
   -  Navigate into repo directory and build a docker image:
   ```
   docker build . -t simple-web-app
   ```
   - Run docker container with port forwarding and bound volumes:
   ```
   docker run -it -v $(pwd)/storage:/app/storage -p 3000:3000 -d simple-web-app
   ```
   This will assign your local port 3000 to container 3000 port, 
   and mount your local 'storage' folder into /app/storage folder in container