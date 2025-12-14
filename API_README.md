# Timetable Scheduler REST API

A Flask-based REST API for accessing timetable data including levels, instructors, courses, and schedules.

## Quick Start

### 1. Install Dependencies

```bash
venv/bin/pip install -r requirements_api.txt
```

### 2. Generate Timetable Data

Run the timetable solver to generate the JSON data file:

```bash
venv/bin/python main.py
```

This creates `Data/timetable_data.json` with all timetable information.

### 3. Start the API Server

```bash
venv/bin/python api.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
- `GET /api/health` - Check if API is running

### Levels
- `GET /api/levels` - Get all levels with departments and specializations

### Instructors
- `GET /api/instructors` - Get all instructors with their schedules
- `GET /api/instructors/<instructor_id>` - Get specific instructor details

### Courses
- `GET /api/courses` - Get all courses
- `GET /api/courses/<course_id>/schedule` - Get course schedule with time slots
- `GET /api/courses/<course_id>/details` - Get course details with instructors and students

### Timetable
- `GET /api/timetable` - Get complete timetable
  - Query params: `?day=Monday&level=1&section=CSIT-1-s1`

### Sections & Rooms
- `GET /api/sections` - Get all sections
- `GET /api/rooms` - Get all rooms

### Metadata
- `GET /api/metadata` - Get timetable generation metadata

## Example Usage

```bash
# Health check
curl http://localhost:5000/api/health

# Get all levels
curl http://localhost:5000/api/levels

# Get instructor by ID
curl http://localhost:5000/api/instructors/I001

# Get course details
curl http://localhost:5000/api/courses/CSC111/details

# Get Monday's timetable
curl http://localhost:5000/api/timetable?day=Monday

# Get level 1 timetable
curl http://localhost:5000/api/timetable?level=1
```

## Response Format

All endpoints return JSON:

```json
{
  "success": true,
  "data": { ... },
  "count": 10
}
```

## CORS Support

The API includes CORS support for cross-origin requests, making it easy to integrate with web frontends.

## Files

- `api.py` - Main Flask application
- `api_service.py` - Service layer for data management
- `requirements_api.txt` - API dependencies
- `output/export.py` - Includes JSON export functionality
- `main.py` - Generates timetable data (JSON + CSV)
