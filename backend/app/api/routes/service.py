from fastapi import APIRouter
from app.core.config import settings
from fastapi import APIRouter
from uuid import uuid4
from pydantic import BaseModel
from app.services import questionary, summarize


class Summarize(BaseModel):
    text: str
    title: str
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
    operation_id=f"questionary-{str(uuid4())}",
)
def text_questionary(data: Questionary):

    text = data.text
    question = data.question

    issuer = data.issuer
    options = data.options

    print(f"Questionary: {question} - {text[:50]}...")

    response = questionary.initiate(question, text)

    print("Questionary done!")

    return response


@router.post(
    "/summarize",
    tags=["service"],
    summary="Summarize",
    operation_id=f"summarize-{str(uuid4())}",
)
def text_summarize(data: Summarize):

    text = data.text
    title = data.title

    issuer = data.issuer
    options = data.options

    print(f"Summarize: {text[:50]}...")

    response = summarize.initiate(text, title)

    print("Summarize done!")

    return response


__all__ = ["router"]
