from ninja import Router, Schema, Field
from typing import Optional


class CreateCard(Schema):
    target_url: str = Field(..., min_length=1, required=True)
    category: str = Field(..., min_length=1, required=True)
    shutdown_time: str = Field(..., min_length=1, required=True)

class Error(Schema):
    details: str
