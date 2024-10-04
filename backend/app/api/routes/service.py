from fastapi import APIRouter
from app.core.config import settings
from fastapi import APIRouter
from uuid import uuid4
from pydantic import BaseModel
from app.services import questionary


class Summarize(BaseModel):
    text: str
    issuer: str | None = None
    options: dict | None = None


class Questionary(BaseModel):
    text: str
    question: str
    issuer: str | None = None
    options: dict | None = None


router = APIRouter()


@router.post(
    "/questionary",
    tags=["service"],
    summary="Questionary",
    operation_id=f"qa-{str(uuid4())}",
)
def text_questionary(data: Questionary):

    text = data.text
    question = data.question

    issuer = data.issuer
    options = data.options

    print(f"Questionary: {question} - {text[:50]}")

    response = questionary.initiate(question, text)

    print("Questionary done!")

    return response


__all__ = ["router"]
