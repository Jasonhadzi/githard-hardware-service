from pydantic import BaseModel, Field

# Request Models
class CheckoutRequest(BaseModel):
    projectId: str = Field(..., description="The project ID")
    hwSetName: str = Field(..., description="The hardware set name")
    qty: int = Field(..., gt=0, description="The quantity to check out (must be positive)")
    userId: str = Field(..., description="The user ID (accepted but not validated - API Gateway handles validation)")

class CheckinRequest(BaseModel):
    projectId: str = Field(..., description="The project ID")
    hwSetName: str = Field(..., description="The hardware set name")
    qty: int = Field(..., gt=0, description="The quantity to check in (must be positive)")
    userId: str = Field(..., description="The user ID (accepted but not validated - API Gateway handles validation)")

class CreateHardwareRequest(BaseModel):
    hwSetName: str = Field(..., description="The hardware set name")
    capacity: int = Field(..., gt=0, description="The initial capacity (must be positive)")

# Response Models
class MessageResponse(BaseModel):
    message: str

