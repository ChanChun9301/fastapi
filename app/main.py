import os
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine, Base
from typing import List, Optional
from uuid import uuid4
import os
from fastapi import Query
from .utils import *

# Create all database tables
Base.metadata.create_all(bind=engine)

# === Constants ===
UPLOAD_DIR = "dipclub/media/videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure the directory exists

# === FastAPI App ===
app = FastAPI()

# Serve static media files
app.mount("/media", StaticFiles(directory="dipclub/media"), name="media")

# === DB Dependency ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Routes ===

@app.post("/courses/", response_model=schemas.Course)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    return crud.create_course(db, course)

from fastapi import Query
from typing import Optional

@app.get("/courses/", response_model=list[schemas.Course])
def list_courses(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = Query(None, description="Поиск по названию или описанию"),
    created_from: Optional[str] = Query(None, description="Дата создания от (YYYY-MM-DD)"),
    created_to: Optional[str] = Query(None, description="Дата создания до (YYYY-MM-DD)"),
    sort_by: Optional[str] = Query("created", description="Сортировка по полю"),
    sort_order: Optional[str] = Query("desc", description="Направление сортировки (asc/desc)"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Course)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (models.Course.title.ilike(search_pattern)) |
            (models.Course.description.ilike(search_pattern))
        )
    if created_from:
        query = query.filter(models.Course.created >= created_from)
    if created_to:
        query = query.filter(models.Course.created <= created_to)

    # Сортировка
    sort_column = getattr(models.Course, sort_by, None)
    if sort_column is not None:
        if sort_order.lower() == "desc":
            sort_column = sort_column.desc()
        else:
            sort_column = sort_column.asc()
        query = query.order_by(sort_column)

    courses = query.offset(skip).limit(limit).all()
    return courses

@app.get("/videos/", response_model=list[schemas.Video])
def list_videos(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = Query(None, description="Поиск по названию и описанию"),
    language: Optional[str] = Query(None, description="Фильтр по языку"),
    author: Optional[str] = Query(None, description="Фильтр по автору"),
    created_from: Optional[str] = Query(None),
    created_to: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created"),
    sort_order: Optional[str] = Query("desc"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Video)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (models.Video.title.ilike(search_pattern)) |
            (models.Video.description.ilike(search_pattern))
        )
    if language:
        query = query.filter(models.Video.language == language)
    if author:
        query = query.filter(models.Video.author == author)
    if created_from:
        query = query.filter(models.Video.created >= created_from)
    if created_to:
        query = query.filter(models.Video.created <= created_to)

    sort_column = getattr(models.Video, sort_by, None)
    if sort_column is not None:
        if sort_order.lower() == "desc":
            sort_column = sort_column.desc()
        else:
            sort_column = sort_column.asc()
        query = query.order_by(sort_column)

    videos = query.offset(skip).limit(limit).all()
    return videos

@app.get("/courses/{course_id}", response_model=schemas.Course)
def get_course(course_id: int, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return db_course

@app.post("/courses/{course_id}/videos", response_model=schemas.Video)
def add_video(course_id: int, video: schemas.VideoCreate, db: Session = Depends(get_db)):
    return crud.create_video(db, course_id, video)

@app.get("/media/videos/{filename}")
def get_video(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@app.post("/courses/{course_id}/upload_video/", response_model=schemas.Video)
async def upload_video(
    course_id: int,
    title: str,
    file: UploadFile = File(...),
    language: Optional[str] = None,
    author: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Сохраняем файл на диск
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Проверяем MIME тип
    mime_type = get_mime_type(file_path)
    allowed_types = ["video/mp4", "video/avi", "video/mkv"]
    if mime_type not in allowed_types:
        os.remove(file_path)  # Удаляем файл, если тип не разрешён
        raise HTTPException(status_code=400, detail="Недопустимый тип файла")

    # Получаем длительность видео (через ffprobe)
    duration = get_video_duration(file_path)

    relative_file_path = f"/media/videos/{filename}"

    video_data = schemas.VideoCreate(
        title=title,
        file=relative_file_path,
        duration=duration,
        language=language,
        author=author,
        description=description,
        course_id=course_id
    )
    return crud.create_video(db, course_id, video_data)

@app.delete("/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_video(video_id: int, db: Session = Depends(get_db)):
    video = crud.get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Видео не найдено")

    # Удаляем файл с диска (с учётом что путь вида /media/videos/filename)
    file_path = video.file.lstrip("/")  # убираем ведущий слэш
    if os.path.exists(file_path):
        os.remove(file_path)

    # Удаляем запись из БД
    crud.delete_video(db, video_id)
    return

def delete_course(db: Session, course_id: int):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        return None
    # Удаляем изображение с диска
    if course.image:
        image_path = course.image.lstrip("/")  # убрать ведущий слэш
        if os.path.exists(image_path):
            os.remove(image_path)
    db.delete(course)
    db.commit()
    return course

from fastapi import status

@app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course_endpoint(course_id: int, db: Session = Depends(get_db)):
    course = crud.delete_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return
