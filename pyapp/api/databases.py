from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import UUID, uuid4

from src.data_access.models import UserDatabase, UserDbSchema
from src.data_access.database import get_db
from src.utils.auth import encrypt_value, decrypt_value
from src.utils.jwt_auth import decode_access_token
from src.data_access.schema_extractor import get_schema_json
from src.data_access.vectorestore_manager import create_vectorstore_for_user_db
from src.api.auth import get_current_user


router = APIRouter()


class DatabaseConnectionRequest(BaseModel):
    name: str
    host: str
    port: int
    username: str
    password: str
    database: str
    schema: str


@router.post("/connect_database")
def connect_database(
    data: DatabaseConnectionRequest,
    user_data=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = UUID(user_data.get("sub"))

    # Encrypt sensitive fields
    encrypted_host = encrypt_value(data.host)
    encrypted_username = encrypt_value(data.username)
    encrypted_password = encrypt_value(data.password)
    encrypted_dbname = encrypt_value(data.database)

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

    # Extract schema
    try:
        schema_json = get_schema_json(conn_params={
            "host": data.host,
            "port": data.port,
            "user": data.username,
            "password": data.password,
            "dbname": data.database,
        }, schema_name=data.schema)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema extraction failed: {str(e)}")

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


@router.get("/get_user_databases")
def get_user_databases(
    db: Session = Depends(get_db),
    user_data=Depends(get_current_user)
):
    user_id = user_data.get("sub")
    dbs = db.query(UserDatabase).filter(UserDatabase.user_id == user_id).all()
    return [
        {
            "id": str(db_entry.id),
            "name": db_entry.name,
            "db_type": db_entry.db_type,
            "host": decrypt_value(db_entry.host),
            "port": db_entry.port,
            "db_name": db_entry.db_name,
        }
        for db_entry in dbs
    ]


@router.get("/get_user_database/{db_id}")
def get_user_database(db_id: UUID, db: Session = Depends(get_db), user_data=Depends(get_current_user)):
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
