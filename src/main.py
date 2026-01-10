from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello_routes():
    return {"message": f"Hello! This is ARMS service!"}
