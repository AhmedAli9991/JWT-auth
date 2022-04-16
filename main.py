from fastapi import FastAPI
from Routes import Users
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI( 
    title="JWT",
    contact={
        "name": "Ahmed Ali",
        "email": "ahmedalibalti2000@gmail.com",
    })
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {"message": "Hello World "}
app.include_router(Users.router, prefix="/User",tags=["Users"])
