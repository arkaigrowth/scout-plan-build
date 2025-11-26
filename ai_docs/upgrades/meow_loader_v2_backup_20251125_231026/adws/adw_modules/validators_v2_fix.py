"""Updates for Pydantic V2 string constraints."""

# For Pydantic V2, use Annotated with constr patterns:
from pydantic import constr as constr_v1
from typing_extensions import Annotated
from pydantic import Field

# Branch name pattern
BranchNameStr = Annotated[str, Field(min_length=1, max_length=255, pattern=r'^[a-zA-Z0-9\-_/]+$')]

# Issue number pattern  
IssueNumberStr = Annotated[str, Field(max_length=10, pattern=r'^\d+$')]

# ADW ID pattern
ADWIDStr = Annotated[str, Field(min_length=5, max_length=64, pattern=r'^ADW-[A-Z0-9]+$')]

# Agent name pattern
AgentNameStr = Annotated[str, Field(min_length=1, max_length=64, pattern=r'^[a-z0-9_]+$')]

