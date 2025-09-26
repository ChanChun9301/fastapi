from pydantic import BaseModel,Field
from typing import List, Optional
from datetime import date

class VideoCreate(BaseModel):
    title: str
    file: str
    duration: Optional[int] = None
    language: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    course_id: int


class Video(BaseModel):
    id: int
    title: str
    file: str
    duration: int
    language: Optional[str]
    author: Optional[str]
    description: Optional[str]
    created: date
    course_id: int

    class Config:
        orm_mode = True


class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    image: Optional[str] = None


class Course(BaseModel):
    id: int
    title: str
    description: Optional[str]
    image: Optional[str]
    created: date
    videos: List[Video] = []

    class Config:
        orm_mode = True


