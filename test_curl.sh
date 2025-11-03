#!/bin/bash

# Hardware Service API - Test Curl Commands
# Service URL (read from environment variable or use default)
BASE_URL="${HARDWARE_SERVICE_URL:-http://localhost:5002}"

echo "=========================================="
echo "Hardware Service API - Test Commands"
echo "=========================================="
echo ""

# 1. Root endpoint
echo "1. Testing root endpoint..."
curl -X GET "${BASE_URL}/" \
  -H "Content-Type: application/json"
echo -e "\n"

# 2. Get hardware info (requires hardware to exist)
echo "2. Testing GET /get_hw_info (replace HWSet1 with existing hardware name)..."
curl -X GET "${BASE_URL}/get_hw_info?hwSetName=HWSet1" \
  -H "Content-Type: application/json"
echo -e "\n"

# 3. Create hardware set
echo "3. Testing POST /create_hardware_set..."
curl -X POST "${BASE_URL}/create_hardware_set" \
  -H "Content-Type: application/json" \
  -d '{
    "hwSetName": "HWSet1",
    "capacity": 100
  }'
echo -e "\n"

# 4. Create another hardware set
echo "4. Creating another hardware set..."
curl -X POST "${BASE_URL}/create_hardware_set" \
  -H "Content-Type: application/json" \
  -d '{
    "hwSetName": "HWSet2",
    "capacity": 50
  }'
echo -e "\n"

# 5. Get all hardware names
echo "5. Testing GET /get_all_hw_names..."
curl -X GET "${BASE_URL}/get_all_hw_names" \
  -H "Content-Type: application/json"
echo -e "\n"

# 6. Get hardware info (after creation)
echo "6. Testing GET /get_hw_info for HWSet1..."
curl -X GET "${BASE_URL}/get_hw_info?hwSetName=HWSet1" \
  -H "Content-Type: application/json"
echo -e "\n"

# 7. Check out hardware
echo "7. Testing POST /check_out..."
curl -X POST "${BASE_URL}/check_out" \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "project123",
    "hwSetName": "HWSet1",
    "qty": 10,
    "userId": "user123"
  }'
echo -e "\n"

# 8. Check hardware info after checkout
echo "8. Checking hardware info after checkout..."
curl -X GET "${BASE_URL}/get_hw_info?hwSetName=HWSet1" \
  -H "Content-Type: application/json"
echo -e "\n"

# 9. Check in hardware
echo "9. Testing POST /check_in..."
curl -X POST "${BASE_URL}/check_in" \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "project123",
    "hwSetName": "HWSet1",
    "qty": 5,
    "userId": "user123"
  }'
echo -e "\n"

# 10. Check hardware info after check-in
echo "10. Checking hardware info after check-in..."
curl -X GET "${BASE_URL}/get_hw_info?hwSetName=HWSet1" \
  -H "Content-Type: application/json"
echo -e "\n"

# 11. Test error case - checkout more than available
echo "11. Testing error case - checkout more than available..."
curl -X POST "${BASE_URL}/check_out" \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "project123",
    "hwSetName": "HWSet1",
    "qty": 1000,
    "userId": "user123"
  }'
echo -e "\n"

# 12. Test error case - hardware not found
echo "12. Testing error case - hardware not found..."
curl -X GET "${BASE_URL}/get_hw_info?hwSetName=NonExistentHW" \
  -H "Content-Type: application/json"
echo -e "\n"

echo "=========================================="
echo "Test sequence completed!"
echo "=========================================="

