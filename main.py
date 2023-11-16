import uvicorn

if __name__=="__main__":
    uvicorn.run("src.endpoints:app",host="127.0.0.1",port=9009,reload=True)