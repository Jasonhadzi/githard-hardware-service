from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pymongo import MongoClient
import hardware_database as hardwareDB
from config import config
from models import (
    CheckoutRequest,
    CheckinRequest,
    CreateHardwareRequest,
    MessageResponse
)

# Initialize FastAPI application
app = FastAPI(
    title="Hardware Service API",
    description="Microservice for managing hardware sets, inventory, and checkout/check-in operations",
    version="1.0.0"
)

def get_mongodb_client():
    """Get MongoDB client using secure connection string from environment variables"""
    try:
        if not config.validate_config():
            raise ValueError("Invalid MongoDB configuration")
        
        connection_string = config.get_mongodb_connection_string()
        # Only use tlsAllowInvalidCertificates for Atlas connections
        use_tls = 'mongodb+srv' in connection_string
        client = MongoClient(
            connection_string, 
            tlsAllowInvalidCertificates=use_tls
        )
        
        # Test the connection
        client.admin.command('ping')
        return client
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Test MongoDB connection on startup"""
    try:
        # Don't use dependency injection here, create client directly
        if not config.validate_config():
            print("⚠ Invalid MongoDB configuration")
            return
        
        connection_string = config.get_mongodb_connection_string()
        use_tls = 'mongodb+srv' in connection_string
        test_client = MongoClient(
            connection_string,
            tlsAllowInvalidCertificates=use_tls
        )
        test_client.admin.command('ping')
        test_client.close()
        print("✓ MongoDB connection successful")
    except Exception as e:
        print(f"⚠ Failed to connect to MongoDB: {e}")
        print("App will start but database features may not work")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hardware Service API", "version": "1.0.0"}

@app.get("/get_hw_info")
async def get_hw_info(
    hwSetName: str,
    client: MongoClient = Depends(get_mongodb_client)
):
    """
    Get hardware set information by name.
    Matches Flask app endpoint format.
    
    Args:
        hwSetName: The name of the hardware set to query
    
    Returns:
        JSON response with hardwareName, capacity, and availability
    """
    if not hwSetName:
        return JSONResponse(content={"error": "Missing 'hwSetName' in request"}, status_code=400)
    
    success, result = hardwareDB.queryHardwareSet(client, hwSetName)
    
    if not success:
        return JSONResponse(content={"message": result}, status_code=404)
    
    return {
        "hardwareName": result.get("hwSetName"),
        "capacity": result.get("capacity"),
        "availability": result.get("availability")
    }

@app.post("/check_out")
async def check_out(
    request: CheckoutRequest,
    client: MongoClient = Depends(get_mongodb_client)
):
    """
    Check out hardware for a project.
    Matches Flask app endpoint format.
    
    Args:
        request: CheckoutRequest containing projectId, hwSetName, qty, and userId
    
    Returns:
        JSON response with message or error
    """
    # Validate required fields (matching Flask app validation)
    if not all([request.projectId, request.hwSetName, request.qty, request.userId]):
        return JSONResponse(content={"error": "Missing required fields"}, status_code=400)
    
    # Check if hardware exists
    hw_exists, hw_data = hardwareDB.queryHardwareSet(client, request.hwSetName)
    if not hw_exists:
        return JSONResponse(content={"error": "Hardware does not exist"}, status_code=404)
    
    # Check availability
    available = hw_data.get("availability", 0)
    if available < request.qty:
        return JSONResponse(content={"error": "Not enough units available to check out"}, status_code=400)
    
    # Request space (updates availability)
    if not hardwareDB.requestSpace(client, request.hwSetName, request.qty):
        return JSONResponse(content={"error": "Failed to check out hardware"}, status_code=400)
    
    # Update project checkout record
    if not hardwareDB.updateProjectCheckout(client, request.projectId, request.hwSetName, request.qty):
        # Rollback availability if checkout record update fails
        hardwareDB.updateAvailability(client, request.hwSetName, request.qty)
        return JSONResponse(content={"error": "Failed to update project checkout record"}, status_code=500)
    
    return {"message": "Checked out successfully"}

@app.post("/check_in")
async def check_in(
    request: CheckinRequest,
    client: MongoClient = Depends(get_mongodb_client)
):
    """
    Check in hardware for a project.
    Matches Flask app endpoint format.
    
    Args:
        request: CheckinRequest containing projectId, hwSetName, qty, and userId
    
    Returns:
        JSON response with message or error
    """
    # Validate required fields (matching Flask app validation)
    if not all([request.projectId, request.hwSetName, request.qty, request.userId]):
        return JSONResponse(content={"error": "Missing required fields"}, status_code=400)
    
    # Check if hardware exists
    hw_exists, hw_data = hardwareDB.queryHardwareSet(client, request.hwSetName)
    if not hw_exists:
        return JSONResponse(content={"error": "Hardware does not exist"}, status_code=404)
    
    # Check project's current checkout
    current_checkout = hardwareDB.getProjectCheckout(client, request.projectId, request.hwSetName)
    if current_checkout < request.qty:
        return JSONResponse(content={"error": "Cannot check in more than currently checked out"}, status_code=400)
    
    # Check capacity constraints
    currAvailability = hw_data.get("availability")
    currCapacity = hw_data.get("capacity")
    newAvailability = currAvailability + request.qty
    
    if newAvailability > currCapacity:
        return JSONResponse(content={"error": "Too big to check in"}, status_code=400)
    
    # Update availability (check-in increases availability)
    if not hardwareDB.updateAvailability(client, request.hwSetName, request.qty):
        return JSONResponse(content={"error": "Failed to check in hardware"}, status_code=400)
    
    # Update project checkout record (negative qty for check-in)
    if not hardwareDB.updateProjectCheckout(client, request.projectId, request.hwSetName, -request.qty):
        # Rollback availability if checkout record update fails
        hardwareDB.updateAvailability(client, request.hwSetName, -request.qty)
        return JSONResponse(content={"error": "Failed to update project checkout record"}, status_code=500)
    
    return {"message": "Checked in successfully"}

@app.post("/create_hardware_set", response_model=MessageResponse)
async def create_hardware_set(
    request: CreateHardwareRequest,
    client: MongoClient = Depends(get_mongodb_client)
):
    """
    Create a new hardware set.
    
    Args:
        request: CreateHardwareRequest containing hwSetName and capacity
    
    Returns:
        MessageResponse: Success message
    """
    success, message = hardwareDB.createHardwareSet(
        client, 
        request.hwSetName, 
        request.capacity
    )
    
    if not success:
        raise HTTPException(status_code=409, detail=message)
    
    return MessageResponse(message=message)

@app.get("/get_all_hw_names")
async def get_all_hw_names(client: MongoClient = Depends(get_mongodb_client)):
    """
    Get all hardware set names.
    Matches Flask app endpoint format (returns empty dict for now, can be extended).
    
    Returns:
        JSON response (empty dict to match Flask app, or list of names)
    """
    hardware_names = hardwareDB.getAllHwSetNames(client)
    # Return empty dict to match Flask app behavior, or return names if needed
    # return {}  # Matches Flask app exactly
    return {"hardwareNames": hardware_names}  # More useful format

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.service_port)

