from fastapi import FastAPI
import uvicorn

from app.router import news, summary

# app = FastAPI()

app = FastAPI(
    title="FastAPI News Summary",
    version="0.2",
    #description="This is the API documentation for News Summary generating by AI.",
    # terms_of_service="http://example.com/terms/",
    contact={
        "name": "Sohana Tasneem", 
        "email": "sohanatasneem12@gmail.com",
    },
    # license_info = {
    #     "name": "MIT License",
    #     "url": "https://opensource.org/licenses/MIT",
    # },
    redoc_url="/documentation",
    docs_url="/try-out",
)

app.include_router(news.router)
app.include_router(summary.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the News Summary API"}

if __name__ == "__main__":
    # uvicorn.run("main:app", host="localhost", port=8001, reload=True)
    uvicorn.run("main:app", host="localhost", port=8011, reload=True)