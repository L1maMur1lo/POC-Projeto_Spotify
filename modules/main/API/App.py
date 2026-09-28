from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.main.API.routers import Artists

origins = [
    'http://127.0.0.1:5500'  # Endereço do servidor local do projeto web
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Allows cookies, authorization headers, etc.
    allow_methods=['*'],  # Allows all standard methods (GET, POST, PUT...)
    allow_headers=['*'],  # Allows all headers
)


@app.get('/')
def api_status():

    return {'API Status': 'ON'}


app.include_router(Artists.router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=8080)
