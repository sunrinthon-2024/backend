from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

app = FastAPI()

API_KEY = "1234567abcdef"

security = HTTPBearer()


async def get_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials == API_KEY:
        return credentials.credentials
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


@app.get("/users/me")
async def read_users_me(api_key: str = Depends(get_api_key)):
    return {"msg": "Hello, authenticated user!"}


# Swagger UI customization
from fastapi.openapi.utils import get_openapi


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API with Bearer Token",
        version="1.0.0",
        description="This is a simple API with Bearer token authentication",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"HTTPBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
