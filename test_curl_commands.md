# Hardware Service API - Curl Test Commands

## Base URL
```bash
BASE_URL="http://localhost:5002"
```

## 1. Root Endpoint
```bash
curl -X GET "${BASE_URL}/" \
  -H "Content-Type: application/json"
```

## 2. Get Hardware Info
```bash
curl -X GET "${BASE_URL}/get_hw_info?hwSetName=HWSet1" \
  -H "Content-Type: application/json"
```

## 3. Create Hardware Set
```bash
curl -X POST "${BASE_URL}/create_hardware_set" \
  -H "Content-Type: application/json" \
  -d '{
    "hwSetName": "HWSet1",
    "capacity": 100
  }'
```

## 4. Get All Hardware Names
```bash
curl -X GET "${BASE_URL}/get_all_hw_names" \
  -H "Content-Type: application/json"
```

## 5. Check Out Hardware
```bash
curl -X POST "${BASE_URL}/check_out" \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "project123",
    "hwSetName": "HWSet1",
    "qty": 10,
    "userId": "user123"
  }'
```

## 6. Check In Hardware
```bash
curl -X POST "${BASE_URL}/check_in" \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "project123",
    "hwSetName": "HWSet1",
    "qty": 5,
    "userId": "user123"
  }'
```

## Test Scenarios

### Complete Flow Example
```bash
# 1. Create a hardware set
curl -X POST "http://localhost:5002/create_hardware_set" \
  -H "Content-Type: application/json" \
  -d '{"hwSetName": "HWSet1", "capacity": 100}'

# 2. Check hardware info
curl -X GET "http://localhost:5002/get_hw_info?hwSetName=HWSet1" \
  -H "Content-Type: application/json"

# 3. Check out 20 units
curl -X POST "http://localhost:5002/check_out" \
  -H "Content-Type: application/json" \
  -d '{"projectId": "project123", "hwSetName": "HWSet1", "qty": 20, "userId": "user123"}'

# 4. Check hardware info again (should show 80 available)
curl -X GET "http://localhost:5002/get_hw_info?hwSetName=HWSet1" \
  -H "Content-Type: application/json"

# 5. Check in 10 units
curl -X POST "http://localhost:5002/check_in" \
  -H "Content-Type: application/json" \
  -d '{"projectId": "project123", "hwSetName": "HWSet1", "qty": 10, "userId": "user123"}'

# 6. Final check (should show 90 available)
curl -X GET "http://localhost:5002/get_hw_info?hwSetName=HWSet1" \
  -H "Content-Type: application/json"
```

### Error Cases

#### Hardware Not Found
```bash
curl -X GET "http://localhost:5002/get_hw_info?hwSetName=NonExistentHW" \
  -H "Content-Type: application/json"
```

#### Checkout More Than Available
```bash
curl -X POST "http://localhost:5002/check_out" \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "project123",
    "hwSetName": "HWSet1",
    "qty": 1000,
    "userId": "user123"
  }'
```

#### Check In More Than Checked Out
```bash
curl -X POST "http://localhost:5002/check_in" \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "project123",
    "hwSetName": "HWSet1",
    "qty": 1000,
    "userId": "user123"
  }'
```

#### Create Duplicate Hardware Set
```bash
curl -X POST "http://localhost:5002/create_hardware_set" \
  -H "Content-Type: application/json" \
  -d '{
    "hwSetName": "HWSet1",
    "capacity": 100
  }'
```

## Pretty Print JSON Responses

For better readability, pipe through `jq` if available:
```bash
curl -X GET "http://localhost:5002/get_hw_info?hwSetName=HWSet1" \
  -H "Content-Type: application/json" | jq
```

Or use Python for pretty printing:
```bash
curl -X GET "http://localhost:5002/get_hw_info?hwSetName=HWSet1" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

## Running All Tests

Make the test script executable and run:
```bash
chmod +x test_curl.sh
./test_curl.sh
```

