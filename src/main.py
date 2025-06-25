from src.data_access.vectorestore_manager import create_vectorstore_for_user_db, create_vectorstore_from_schema
from src.data_access.vectorstore_singleton import set_vectorstore
from src.services.handle_query import handle_query
from src.utils.load_api_key import load_api_key
from config.config import SCHEMA_JSON_DIR

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from pydantic import BaseModel

from sqlalchemy.orm import Session
from uuid import uuid4, UUID

from src.data_access.database import get_db
from src.data_access.models import User, UserDatabase, UserDbSchema
from src.utils.auth import hash_password, verify_password
from pydantic import BaseModel, EmailStr

from src.utils.jwt_auth import create_access_token
from fastapi import Security
from fastapi.security import OAuth2PasswordBearer
from src.utils.jwt_auth import decode_access_token
from src.utils.auth import decrypt_value, encrypt_value
from src.data_access.schema_extractor import get_schema_json



@asynccontextmanager
async def lifespan(app: FastAPI):
    load_api_key()
    # schema, schema_text = load_schema()
    # vectorstore = create_vectorstore_from_schema()
    # set_vectorstore(vectorstore)
    pass
    yield

print("Starting app")
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # You can tighten this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_api_key()
class QueryRequest(BaseModel):
    query: str
    history: list[dict] = []
    db_id: UUID
 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.post("/api/query")
async def query_api(request: QueryRequest, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_data = decode_access_token(token)
    user_id = UUID(user_data["sub"])
    return handle_query(request.query, history=request.history, db_id=request.db_id, user_id=user_id, db=db)

# Reuse get_db dependency

class SignupRequest(BaseModel):
    email: EmailStr
    password: str

@app.post("/signup")
def signup(user: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        id=uuid4(),
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user_id": str(new_user.id)}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@app.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(db_user.id)})
    return {"access_token": token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload  # or just payload["sub"]


@app.get("/me")
def get_profile(user=Depends(get_current_user)):
    return {"message": "Welcome!", "user_id": user["sub"]}


class DatabaseConnectionRequest(BaseModel):
    name: str
    host: str
    port: int
    username: str
    password: str
    database: str
    schema: str


@app.post("/connect_database")
def connect_database(
    data: DatabaseConnectionRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Get user from token
    user_data = decode_access_token(token)
    if not user_data or "sub" not in user_data:
        raise HTTPException(status_code=401, detail="Invalid user token")
    
    user_id = UUID(user_data.get("sub"))

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user token")

    # Encrypt sensitive fields
    encrypted_host = encrypt_value(data.host)
    # encrypted_port = str(data.port)# encrypt_value(str(data.port))
    encrypted_username = encrypt_value(data.username)
    encrypted_password = encrypt_value(data.password)
    encrypted_dbname = encrypt_value(data.database)

    # Save to UserDatabase
    user_db = UserDatabase(
        id=uuid4(),
        user_id=user_id,
        name=data.name,
        db_type="PostgreSQL",
        host=encrypted_host,
        port=data.port,
        username=encrypted_username,
        password_encrypted=encrypted_password,
        db_name=encrypted_dbname,
    )
    db.add(user_db)
    db.commit()
    db.refresh(user_db)

    # Attempt to connect and extract schema
    try:
        # Call your existing method (adjust as needed)
        schema_json = get_schema_json(conn_params={
            "host": data.host,
            "port": data.port,
            "user": data.username,
            "password": data.password,
            "dbname": data.database,
        }, schema_name=data.schema)
        print("============\n", schema_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema extraction failed: {str(e)}")

    # Save schema
    user_schema = UserDbSchema(
        id=uuid4(),
        user_database_id=user_db.id,
        schema_name="public" if data.schema == "" else data.schema,
        schema_json_info=schema_json,
    )
    db.add(user_schema)
    db.commit()

    create_vectorstore_for_user_db(user_id=str(user_db.user_id), db_id=str(user_db.id), db=db)

    return {"message": "Database connected and schema extracted successfully"}    


@app.get("/get_user_databases")
def get_user_databases(
    db: Session = Depends(get_db),
    current_user_dict: dict = Depends(get_current_user)
):
    try:
        user_id = current_user_dict.get("sub")
        dbs = db.query(UserDatabase).filter(UserDatabase.user_id == user_id).all()
        return [
            {
                "id": str(db_entry.id),
                "name": db_entry.name,
                "db_type": db_entry.db_type,
                "host": decrypt_value(db_entry.host),
                "port": db_entry.port,
                "db_name": db_entry.db_name,
                # You can add more fields if needed
            }
            for db_entry in dbs
        ]
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching databases: {str(e)}")


@app.get("/get_user_database/{db_id}")
def get_user_database(db_id: UUID, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_data = decode_access_token(token)
    if not user_data or "sub" not in user_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = UUID(user_data["sub"])

    user_db = db.query(UserDatabase).filter_by(id=db_id, user_id=user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Database not found")

    schema_obj = db.query(UserDbSchema).filter_by(user_database_id=db_id).first()
    return {
        "name": user_db.name,
        "db_type": user_db.db_type,
        "host": decrypt_value(user_db.host),
        "port": user_db.port,
        "username": decrypt_value(user_db.username),
        "schema": schema_obj.schema_name if schema_obj else "N/A"
    }
