"""
Flask REST API for Timetable Scheduler
Provides endpoints for levels, instructors, courses, and timetable data
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from api_service import TimetableAPIService

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# File paths configuration
FILE_PATHS = {
    "courses": "Data/Courses.csv",
    "rooms": "Data/Rooms.csv",
    "instructors": "Data/Instructors.csv",
    "timeslots": "Data/TimeSlots.csv",
    "sections": "Data/sections_data.xlsx",
    "available_courses": "Data/Avilable_Course.csv"
}

JSON_FILE = "Data/timetable_data.json"

# Initialize service
service = TimetableAPIService(JSON_FILE, FILE_PATHS)


# ============= Health Check =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running"""
    from datetime import datetime
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Timetable API is running"
    })


# ============= Levels Endpoints =============

@app.route('/api/levels', methods=['GET'])
def get_levels():
    """Get all unique levels with their departments and specializations"""
    try:
        levels = service.get_all_levels()
        return jsonify({
            "success": True,
            "data": levels,
            "count": len(levels)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============= Instructors Endpoints =============

@app.route('/api/instructors', methods=['GET'])
def get_instructors():
    """Get all instructors with their details and schedules"""
    try:
        instructors = service.get_all_instructors()
        return jsonify({
            "success": True,
            "data": instructors,
            "count": len(instructors)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/instructors/<instructor_id>', methods=['GET'])
def get_instructor(instructor_id):
    """Get specific instructor details by ID"""
    try:
        instructor = service.get_instructor_by_id(instructor_id)
        if instructor:
            return jsonify({
                "success": True,
                "data": instructor
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Instructor with ID '{instructor_id}' not found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============= Courses Endpoints =============

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses"""
    try:
        courses = service.get_all_courses()
        return jsonify({
            "success": True,
            "data": courses,
            "count": len(courses)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/courses/<course_id>/schedule', methods=['GET'])
def get_course_schedule(course_id):
    """Get course schedule with all time slots"""
    try:
        schedule_data = service.get_course_schedule(course_id)
        if schedule_data["course"]:
            return jsonify({
                "success": True,
                "data": schedule_data
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Course with ID '{course_id}' not found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/courses/<course_id>/details', methods=['GET'])
def get_course_details(course_id):
    """Get comprehensive course information including instructors and students"""
    try:
        details = service.get_course_details(course_id)
        if details:
            return jsonify({
                "success": True,
                "data": details
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Course with ID '{course_id}' not found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============= Timetable Endpoints =============

@app.route('/api/timetable', methods=['GET'])
def get_timetable():
    """Get complete timetable with optional filters (day, level, section)"""
    try:
        day = request.args.get('day')
        level = request.args.get('level')
        section = request.args.get('section')

        timetable = service.get_timetable(day=day, level=level, section=section)
        return jsonify({
            "success": True,
            "data": timetable,
            "filters": {
                "day": day,
                "level": level,
                "section": section
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============= Sections Endpoints =============

@app.route('/api/sections', methods=['GET'])
def get_sections():
    """Get all sections with their details"""
    try:
        sections = service.get_all_sections()
        return jsonify({
            "success": True,
            "data": sections,
            "count": len(sections)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============= Rooms Endpoints =============

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Get all rooms with their details"""
    try:
        rooms = service.get_all_rooms()
        return jsonify({
            "success": True,
            "data": rooms,
            "count": len(rooms)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============= Metadata Endpoint =============

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    """Get timetable generation metadata"""
    try:
        metadata = service.get_metadata()
        return jsonify({
            "success": True,
            "data": metadata
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============= Error Handlers =============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


# ============= Main =============

if __name__ == '__main__':
    print("=" * 60)
    print("Timetable Scheduler REST API")
    print("=" * 60)
    print("\nAvailable Endpoints:")
    print("  - GET  /api/health")
    print("  - GET  /api/levels")
    print("  - GET  /api/instructors")
    print("  - GET  /api/instructors/<instructor_id>")
    print("  - GET  /api/courses")
    print("  - GET  /api/courses/<course_id>/schedule")
    print("  - GET  /api/courses/<course_id>/details")
    print("  - GET  /api/timetable?day=<day>&level=<level>&section=<section>")
    print("  - GET  /api/sections")
    print("  - GET  /api/rooms")
    print("  - GET  /api/metadata")
    print("\n" + "=" * 60)
    print("Starting server on http://localhost:5000")
    print("=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
