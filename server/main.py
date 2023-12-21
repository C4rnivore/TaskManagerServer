import json
from fastapi import Depends, FastAPI, Response, Request, WebSocketDisconnect, status, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import event
import uvicorn
import database 
import crud, models, schemas

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# python -m uvicorn main:app --reload  

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# Tasks endpoints
@app.get("/tasks/fetch/all")
def read_tasks(request:Request, db: Session = Depends(get_db)):
    return db.query(models.Task).all()

@app.post("/tasks/add/{user_id}")
async def create_task(user_id:str, task: schemas.TaskCreate, response:Response, db: Session = Depends(get_db)):
    response = Response()
    response.headers.append('Access-Control-Allow-Origin', '*')
    response.headers.append('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
    response.headers.append('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
    
    try:
        crud.create_user_task(db=db, task=task, user_id=user_id)
        response.status_code=status.HTTP_200_OK
        await send_notification(f'Created new task: {task.title}')
    except:
        response.status_code=status.HTTP_404_NOT_FOUND
    return response

@app.delete("/tasks/delete/{task_id}")
async def delete_task(task_id:str, response:Response, db: Session = Depends(get_db)):
    response = Response()
    response.headers.append('Access-Control-Allow-Origin', '*')
    response.headers.append('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
    response.headers.append('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')

    try:
        crud.delete_task_by_id(db=db, task_id=task_id)
        response.status_code = status.HTTP_200_OK
        await send_notification(f'Task deleted')
    except:
         response.status_code = status.HTTP_404_NOT_FOUND
    return response

@app.put("/tasks/update/{task_id}")
async def update_task(task_id:str, task: schemas.TaskCreate, response:Response, db:Session = Depends(get_db)):
    response = Response()
    response.headers.append('Access-Control-Allow-Origin', '*')
    response.headers.append('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
    response.headers.append('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
    try:
        crud.update_task_by_id(db, task_id, task)
        response.status_code = status.HTTP_200_OK
        await send_notification(f'Task updated')
    except:
        response.status_code = status.HTTP_404_NOT_FOUND

    return response


# User endpoints
@app.post('/users/create')
async def create_user(user: schemas.UserCreate, response:Response, db:Session=Depends(get_db)):
    response = Response()
    response.headers.append('Access-Control-Allow-Origin', '*')
    response.headers.append('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
    response.headers.append('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
    try:
        user = crud.create_user(db=db, user=user)
        response.status_code = status.HTTP_200_OK
        await send_notification(f'User created')
    except:
        response.status_code = status.HTTP_404_NOT_FOUND
    return response


connected_clients = []

async def send_notification(message):
    for client in connected_clients:
        await client.send_text(message)

# Websockets
@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    while True:
        try:
            data = await websocket.receive_text()
            await send_notification(data)
        except WebSocketDisconnect:
            connected_clients.remove(websocket)
        except:
            pass
            break

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)