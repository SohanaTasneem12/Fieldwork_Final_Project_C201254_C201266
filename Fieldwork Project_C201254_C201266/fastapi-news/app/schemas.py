from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional   


class CategoryBase(BaseModel):
    name: str
    description: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True

class ReporterBase(BaseModel):
    name: str
    email: str

class ReporterCreate(ReporterBase):
    pass

class Reporter(ReporterBase):
    id: int

    class Config:
        from_attributes = True

class PublisherBase(BaseModel):
    name: str
    email: str
    website: Optional[str] = None

class PublisherCreate(PublisherBase):
    pass

class Publisher(PublisherBase):
    id: int

    class Config:
        from_attributes = True

class ImageBase(BaseModel):
    news_id: int
    image_url: str

class ImageCreate(ImageBase):
    pass

class Image(ImageBase):
    id: int

    class Config:
        from_attributes = True


class NewsBase(BaseModel):
    # publisher_website: str
    title: str
    body: str
    link: str
    datetime: datetime

    category: Optional[Category] = None
    reporter: Optional[Reporter] = None
    publisher: Optional[Publisher] = None


class NewsCreate(NewsBase):
    news_publisher: str
    news_reporter: str
    news_category: str
    publisher_website: str
    images: List[str] = []


class News(NewsBase):
    id: int

    class Config:
        from_attributes = True



class SummaryFast(BaseModel):
    news_id: int

class SummaryBase(BaseModel):
    summary_text: str
    news_id: int


class SummaryCreate(SummaryBase):
    pass
    # news_body: str 

class Summary(SummaryBase):
    id: int

    class Config:
        from_attributes = True

