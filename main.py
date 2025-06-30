from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# ____________ Create "FastAPI application" instance -> manages all web routes and functions
app = FastAPI()


# ____________ Configure CORS
# list specific origins (FE) that allowed to talk to BE
origins = [
    "http://localhost:5173",  
    # eg: http://127.0.0.1:5173",      
    # eg: "http://your-deployed-frontend.com"
]


# Add CORS middleware to FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,        # Allow requests from these specific origins
    allow_credentials = True,       # Allow cookies to be sent (useful for authentication later)
    allow_methods = ["*"],          # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers = ["*"]           # Allow all headers in the request
)





# ____________ Define "API Endpoint" (specific URL server will respond to)

# @app.get("/") means: "When someone sends a GET request to the '/' (root) address,
    # '@' -> decorator | means 'when ever someone visit' 
    # '/' -> root address
    # will run function right below the line
@app.get("/")
def read_root():
    return {"message": "Hello from your Python Backend! hahaha"}

# Let's add another simple endpoint for testing
@app.get("/hello")
def say_hello():
    return {"greeting": "Greetings, user!"}
