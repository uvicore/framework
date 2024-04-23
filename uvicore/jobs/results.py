from pydantic import BaseModel
from prettyprinter import pretty_call, register_pretty


class JobResults(BaseModel):
    # There are no default properties here
    # So why a JobResults at all?  Basically to
    # wrap pydantic BaseModel and provide better pretty priting
    pass


@register_pretty(JobResults)
def pretty_entity(value, ctx):
    """Custom pretty printer for JobResults"""
    return pretty_call(ctx, value.__class__, **value.__dict__)
