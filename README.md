**Simple Web application that accepts messages from users and stores them in JSON file**

**How to run this application?**

**You can run this application directly by running main.py with python**

- Clone this repository into a folder of choice on your local machine using the following command:

        ```
        git clone https://github.com/rafalradx/web-app-with-form
        ```

- Navigate into the repo folder and create storage direcotry:

        ```
        cd web-aap-with-form
        mkdir storage
        ```

- Run main.py with python:

        ```
        python main.py
        ```

    or

        ```
        python3 main.py
        ```

- In your favourite brownser enter:

        ```localhost:3000```

**Preferably run this app in docker container**

**To run this application in docker**


    ```
    -  Navigate into repo directory and build a docker image:
    ```
    docker build . -t simple-web-app
    ```
    - Run docker container with port forwarding and bound volume for permanent storage:
    ```
    docker run -it -v $(pwd)/storage:/app/storage -p 3000:3000 -d simple-web-app
    ```
    This will assign your local port 3000 to container 3000 port, 
    and mount your local 'storage' folder into /app/storage folder in container
    The messages send by usera are stored in storage/data.json file