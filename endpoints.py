import base64
from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from search import get_results

app = FastAPI(title="Incubig search API",
              description="Semantic search on USPTO patent database",
              version="0.1.0",
              docs_url='/xsearch/docs',
              redoc_url='/xsearch/redoc',
              openapi_url='/xsearch/openapi.json')

origins = ["http://localhost:3000/","https://incubig.live","https://ai.incubig.org","https://dyr.incubig.org","https://nyon.org","https://www.preempt.life"]
api_keys = ["60PKCZgn3smuESHN9e8vbVHxiXVS/8H+vXeFC4ruW1d0YAc1UczQlTQ/C2JlnwlEOKjtnLB0N2I0oheAHJGZeB2bVURMQRC1GvM0k45kyrSmiK98bPPlJPu8q1N/TlK4",
            "i90s+B2JsSzEqDJXkAP/WsZ7yGoSNg0/OZqOy2JY2qBBBAmreZebxp7//S4x/Z828lyvckygAz0Mctd1iP3yYrgja1sA3R3t3hHbuHFCteTfgPnAdbMeoZxcnOKRLOJm"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header in api_keys:
        return api_key_header
    raise HTTPException(
        status_code=401,
        detail="Invalid or missing API Key",
    )

@app.get("/xsearch/search")
def search(query: str="*",filter: str=None,select: str="publication_number,publication_year,application_year,application_date,title,abstract_text,industry,sector,sub_sector,main_cpc,further_cpc,assignee,assignee_country,inventor,kind",search_fields: str="title,abstract_text,description_text,claims_text", top: int=1000, skip: int=0,cut_off: float=0.0, api_key: str = Security(get_api_key)):
    return(get_results(query,filter,select,search_fields,top,skip,cut_off))