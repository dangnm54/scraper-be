# 1. Import FastAPI class
from fastapi import FastAPI

# 2. Create a "FastAPI application" instance -> manages all web routes and functions
app = FastAPI()

# 3. Define your first "API Endpoint" (a specific URL your server will respond to)

# @app.get("/") means: "When someone sends a GET request to the '/' (root) address,
# '@' -> decorator | means 'when ever someone visit' 
# '/' -> root address
# will run function right below the line
@app.get("/")
def read_root():
    # This function will be called.
    # It returns a Python dictionary, which FastAPI automatically turns into JSON.
    return {"message": "Hello from your Python Backend! hahaha"}

# Let's add another simple endpoint for testing
@app.get("/hello")
def say_hello():
    return {"greeting": "Greetings, user!"}

# How to run this:
# 1. Save this file as 'main.py' in your 'backend' folder.
# 2. Open your terminal/command prompt in the 'backend' folder.
# 3. Type: uvicorn main:app --reload
# 4. Visit http://127.0.0.1:8000/ or http://127.0.0.1:8000/hello in your web browser.