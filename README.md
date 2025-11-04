# Hardware Microservice

A standalone FastAPI microservice for managing hardware sets, inventory, and checkout/check-in operations. This service is part of the githard microservices architecture.

## Features

- Hardware set management (create, query, list)
- Inventory tracking (capacity and availability)
- Checkout/check-in operations for projects
- Project-level checkout record tracking
- Automatic API documentation (Swagger UI and ReDoc)
- Docker containerization with Docker Compose

## Architecture

- **Framework**: FastAPI
- **Database**: MongoDB (separate `HardwareService` database)
- **Port**: 5002
- **Documentation**: Auto-generated OpenAPI docs at `/docs` and `/redoc`

## Prerequisites

- Python 3.12+
- Docker and Docker Compose (for containerized deployment)
- MongoDB (or use MongoDB container from docker-compose)

## Setup

### Local Development

1. Clone the repository:
```bash
cd githard-hardware-service
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from `env.template`:
```bash
cp env.template .env
```

5. Update `.env` with your MongoDB connection string (replace `<db_password>` with your actual password):
```env
MONGO_HOST=mongodb+srv://jason_db_user:<db_password>@apad2.y5injgl.mongodb.net/?appName=apad2
MONGO_DATABASE=HardwareService
SERVICE_PORT=5002
ENVIRONMENT=development
```

6. Run the service:
```bash
python app.py
# Or with uvicorn directly:
uvicorn app:app --host 0.0.0.0 --port 5002 --reload
```

### Docker Deployment

1. Create `.env` file from `env.template`:
```bash
cp env.template .env
```

2. Update `.env` with your MongoDB credentials

3. **Configure ngrok (optional but recommended)**:
   - Sign up for a free ngrok account at https://dashboard.ngrok.com/signup
   - Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
   - Add it to your `.env` file:
     ```bash
     NGROK_AUTHTOKEN=your_ngrok_authtoken_here
     ```
   - The `ngrok.yml` file will be automatically generated from this environment variable

4. Build and run with Docker Compose:
```bash
docker-compose up --build
```

The service will be available at:
- **Local**: `http://localhost:5002`
- **Public (via ngrok)**: Check the ngrok web interface at `http://localhost:4040` or container logs:
  ```bash
  docker logs hardware-service-ngrok
  ```
  Look for a line like: `Forwarding https://abc123.ngrok-free.app -> http://hardware-service:5002`

**Access your public URL**:
- Visit `http://localhost:4040` for the ngrok web interface (shows requests, public URL, etc.)
- Or check container logs: `docker logs hardware-service-ngrok | grep "Forwarding"`

## API Endpoints

### GET `/`
Root endpoint providing service information.

**Response:**
```json
{
  "message": "Hardware Service API",
  "version": "1.0.0"
}
```

### GET `/get_hw_info`
Get hardware set information by name.

**Query Parameters:**
- `hwSetName` (string, required): The name of the hardware set

**Response:**
```json
{
  "hardwareName": "HWSet1",
  "capacity": 100,
  "availability": 75
}
```

**Error Responses:**
- `404`: Hardware set does not exist

### POST `/check_out`
Check out hardware for a project.

**Request Body:**
```json
{
  "projectId": "project123",
  "hwSetName": "HWSet1",
  "qty": 10
}
```

**Response:**
```json
{
  "message": "Checked out successfully"
}
```

**Error Responses:**
- `404`: Hardware does not exist
- `400`: Not enough units available to check out

### POST `/check_in`
Check in hardware for a project.

**Request Body:**
```json
{
  "projectId": "project123",
  "hwSetName": "HWSet1",
  "qty": 5
}
```

**Response:**
```json
{
  "message": "Checked in successfully"
}
```

**Error Responses:**
- `404`: Hardware does not exist
- `400`: Cannot check in more than currently checked out
- `400`: Too big to check in (would exceed capacity)

### POST `/create_hardware_set`
Create a new hardware set.

**Request Body:**
```json
{
  "hwSetName": "HWSet1",
  "capacity": 100
}
```

**Response:**
```json
{
  "message": "Hardware set created successfully!"
}
```

**Error Responses:**
- `409`: Hardware set already exists

### GET `/get_all_hw_names`
Get all hardware set names.

**Response:**
```json
{
  "hardwareNames": ["HWSet1", "HWSet2", "HWSet3"]
}
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:5002/docs`
- **ReDoc**: `http://localhost:5002/redoc`

## Database Schema

### Hardware Collection (`hardware`)
```json
{
  "hwSetName": "HWSet1",
  "capacity": 100,
  "availability": 75
}
```

### Project Checkout Collection (`project_checkouts`)
```json
{
  "projectId": "project123",
  "hwSetName": "HWSet1",
  "quantity": 25
}
```

## Testing

Example test files are provided in the `tests/` directory. Run tests with:

```bash
pytest tests/
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_HOST` | Full MongoDB connection string (mongodb:// or mongodb+srv://) | Required |
| `MONGO_DATABASE` | MongoDB database name | `HardwareService` |
| `SERVICE_PORT` | Service port | `5002` |
| `ENVIRONMENT` | Environment (development/production) | `production` |

**Note:** When using a full connection string in `MONGO_HOST`, the database name will be automatically appended. Example:
```
MONGO_HOST=mongodb+srv://user:password@host.net/?appName=apad2
MONGO_DATABASE=HardwareService
```
This will connect to: `mongodb+srv://user:password@host.net/HardwareService?appName=apad2`

## Architecture Notes

- This service assumes the API Gateway handles user/project validation
- Project checkout records are maintained in this service's database
- Each service has its own MongoDB database for isolation
- The service can be scaled independently


