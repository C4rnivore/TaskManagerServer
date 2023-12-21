from sqlalchemy.orm import Session
import models, schemas


#Create
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(hashed_password=user.password, username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_task(db: Session, task: schemas.TaskCreate, user_id: int):
    try:
        db_item = models.Task(**task.model_dump(), owner_id=user_id)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except:
        print('Can\'t add task')
        return
    

#Read
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Task).all()

#Update
def update_task_by_id(db: Session, task_id:str, task: schemas.TaskCreate):
    task_current = get_task(db=db, task_id=int(task_id))

    task_current.title = task.title
    task_current.description = task.description
    db.add(task_current)
    db.commit()
    db.refresh(task_current)
    return 

#Delete
def delete_task_by_id(db:Session, task_id:str):
    task = get_task(db=db, task_id=int(task_id))
    db.delete(task)
    db.commit()
    return


