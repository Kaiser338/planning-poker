# Getting started
## Planning poker

A platform for playing planning poker

## Setup

1. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

2. Activate the virtual environment:

    On Windows:
    ```bash
    .\venv\Scripts\activate
    ```

    On Linux/Mac:
    ```bash
    source venv/bin/activate
    ```

3. Install packages from requirements:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up the environment variable:

    Before running the application, make sure to set the `SECRET_KEY` environment variable with your Django secret key.

    ```bash
    export SECRET_KEY="your_secret_key_here"
    ```

5. Starting the application:

    ```bash
    cd mkppoker
    python manage.py runserver
    ```

Remember to replace `"your_secret_key_here"` with the actual secret key you want to use for your Django application.


### Waiting for the game to start

![alt text](https://i.imgur.com/k7V9ULR.png)

### Game started

![alt text](https://i.imgur.com/Zs8VlzG.png)

### Cards revealed

![alt text](https://i.imgur.com/vfIaoBl.png)
