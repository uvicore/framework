from pydantic import BaseModel
from prettyprinter import pretty_call, register_pretty


class JobResults(BaseModel):
    job_name: str
    job_description: str


@register_pretty(JobResults)
def pretty_entity(value, ctx):
    """Custom pretty printer for JobResults"""
    return pretty_call(ctx, value.__class__, **value.__dict__)
