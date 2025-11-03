# Import necessary libraries and modules
from pymongo import MongoClient
from config import config

'''
Structure of Hardware Set entry:
HardwareSet = {
    'hwSetName': hwSetName,
    'capacity': int,
    'availability': int
}

Structure of Project Checkout entry:
ProjectCheckout = {
    'projectId': str,
    'hwSetName': str,
    'quantity': int
}
'''

# Function to create a new hardware set
def createHardwareSet(client, hwSetName, initCapacity):
    """
    Create a new hardware set in the database.
    Args:
        client: A MongoClient instance
        hwSetName(str): The unique hardware set name
        initCapacity(int): The initial capacity of the hardware set
    
    Returns:
        tuple:
            - bool: Indicates success
            - str: Success or error message
    """
    db = client[config.mongo_database]
    hw_col = db[config.mongo_collection_hardware]

    existing = hw_col.find_one({"hwSetName": hwSetName})
    if existing:
        return False, f"{hwSetName} set already exists"

    hw_set = {
        'hwSetName': hwSetName,
        'capacity': initCapacity,
        'availability': initCapacity
    }

    hw_col.insert_one(hw_set)
    return True, "Hardware set created successfully!"

# Function to query a hardware set by its name
def queryHardwareSet(client, hwSetName):
    """
    Return a hardware data set, including hwSetName.
    Args:
        client: A MongoClient instance
        hwSetName(str): The Unique hardware name
    
    Returns:
        tuple:
            - bool: Indicate whether the hardware exists
            - dict or str: A hardware data set
    """
    db = client[config.mongo_database]
    hw_col = db[config.mongo_collection_hardware]

    hw_set = hw_col.find_one({"hwSetName": hwSetName})
    if not hw_set:
        return False, "Hardware set does not exist"

    return True, hw_set

# Function to update the availability of a hardware set
def updateAvailability(client, hwSetName, delta):
    """
    Update the availability of an existing hardware set.
    Args:
        client: A MongoClient instance
        hwSetName(str): The hardware set name
        delta(int): The change in availability (positive for check-in, negative for check-out)
    
    Returns:
        bool: True if successful, False otherwise
    """
    db = client[config.mongo_database]
    hw_col = db[config.mongo_collection_hardware]

    hw_set = hw_col.find_one({"hwSetName": hwSetName})
    if not hw_set:
        return False
    
    currAvailability = hw_set.get('availability')
    currCapacity = hw_set.get("capacity")
    newAvailability = currAvailability + delta

    # Check if the new availability is valid (not negative, not exceeding capacity)
    if newAvailability < 0 or newAvailability > currCapacity:
        return False

    hw_col.update_one(
        {'hwSetName': hwSetName}, 
        {'$set': {'availability': newAvailability}}
    )
    return True

# Function to request space from a hardware set
def requestSpace(client, hwSetName, amount):
    """
    Request a certain amount of hardware and update availability.
    Args:
        client: A MongoClient instance
        hwSetName(str): The hardware set name
        amount(int): The amount to request
    
    Returns:
        bool: True if successful, False otherwise
    """
    db = client[config.mongo_database]
    hw_col = db[config.mongo_collection_hardware]

    hw_set = hw_col.find_one({"hwSetName": hwSetName})
    if not hw_set:
        return False

    currAvailability = hw_set.get('availability')

    if currAvailability >= amount:
        hw_col.update_one(
            {'hwSetName': hwSetName}, 
            {'$set': {'availability': currAvailability - amount}}
        )
        return True
    else:
        return False

# Function to get all hardware set names
def getAllHwSetNames(client):
    """
    Get and return a list of all hardware set names.
    Args:
        client: A MongoClient instance
    
    Returns:
        list: List of hardware set names
    """
    db = client[config.mongo_database]
    hw_col = db[config.mongo_collection_hardware]
    
    hardware_sets = hw_col.find({}, {"hwSetName": 1})
    return [hw['hwSetName'] for hw in hardware_sets]

# Function to get project's checkout quantity for a specific hardware set
def getProjectCheckout(client, projectId, hwSetName):
    """
    Get the quantity of hardware checked out by a project.
    Args:
        client: A MongoClient instance
        projectId(str): The project ID
        hwSetName(str): The hardware set name
    
    Returns:
        int: The quantity checked out (0 if not found)
    """
    db = client[config.mongo_database]
    checkout_col = db[config.mongo_collection_checkouts]
    
    checkout_record = checkout_col.find_one({
        "projectId": projectId,
        "hwSetName": hwSetName
    })
    
    if checkout_record:
        return checkout_record.get('quantity', 0)
    return 0

# Function to update project's checkout record
def updateProjectCheckout(client, projectId, hwSetName, qty):
    """
    Update or create a project's checkout record.
    Args:
        client: A MongoClient instance
        projectId(str): The project ID
        hwSetName(str): The hardware set name
        qty(int): The quantity to add (can be negative for check-in)
    
    Returns:
        bool: True if successful, False otherwise
    """
    db = client[config.mongo_database]
    checkout_col = db[config.mongo_collection_checkouts]
    
    # Try to find existing record
    existing = checkout_col.find_one({
        "projectId": projectId,
        "hwSetName": hwSetName
    })
    
    if existing:
        # Update existing record
        new_qty = existing.get('quantity', 0) + qty
        if new_qty < 0:
            return False  # Cannot have negative checkout
        if new_qty == 0:
            # Remove record if quantity becomes zero
            checkout_col.delete_one({
                "projectId": projectId,
                "hwSetName": hwSetName
            })
        else:
            checkout_col.update_one(
                {"projectId": projectId, "hwSetName": hwSetName},
                {"$set": {"quantity": new_qty}}
            )
    else:
        # Create new record if qty > 0
        if qty > 0:
            checkout_col.insert_one({
                "projectId": projectId,
                "hwSetName": hwSetName,
                "quantity": qty
            })
        else:
            return False  # Cannot check in more than checked out
    
    return True

