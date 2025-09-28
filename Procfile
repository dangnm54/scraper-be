# Railway needs to know what command to run to start your application. 
# Procfile is a simple text file that provides this instruction
    # 'uvicorn' -> starts FastAPI server
    # '--host 0.0.0.0' -> tells server to listen on all network interfaces
    # '$PORT' -> an environment variable that Railway automatically provides -> to tell the app which port to use



web: uvicorn app:app --host 0.0.0.0 --port $PORT