# 训练相关的 API 路由
from flask import Blueprint, jsonify, request
import threading
import os
from app.models.competition import Competition
from app.utils.jwt_utils import decode_token
from app.services.competition import CompetitionService
from flask import send_from_directory

competition_bp = Blueprint('competition', __name__, url_prefix='/api/competition')

@competition_bp.route('/add', methods=['POST'])
def add_competition():
    """提交一个赛题"""
    try:
        # For multipart/form-data, use request.form and request.files
        created_time = request.form.get('created_time')
        end_time = request.form.get('end_time')
        status = request.form.get('status')
        type = request.form.get('type')
        number = request.form.get('number')
        open_scenario_file = request.files.get('open_scenario')
        target_points_file = request.files.get('target_points')
        
        # Validate required fields
        if not all([created_time, end_time, status, type, number, open_scenario_file, target_points_file]):
            return jsonify({"error": "Missing required fields"}), 400
            
        # Process the files and create competition
        CompetitionService.create_competition(
            created_time, 
            end_time, 
            status, 
            type, 
            number,
            open_scenario_file,
            target_points_file
        )
        
        return jsonify({"message": "成功提交", "status": "started"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@competition_bp.route('/get-mini-number/<competition_type>', methods=['GET'])
def get_min_number(competition_type):
    """Get the minimum number for a specific competition type (e.g., 'TypeA')"""
    try:
        # Get the minimum number for the given type
        min_number = Competition.get_min_number_by_type(competition_type)
        
        if min_number is not None:
            return jsonify({
                "type": competition_type,
                "min_number": min_number,
                "message": "Success"
            }), 200
        else:
            return jsonify({
                "type": competition_type,
                "message": "No competitions found for this type"
            }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@competition_bp.route('/get-by-type/<competition_type>', methods=['GET'])
def get_competitions_by_type(competition_type):
    """Get competitions by type with all information properly formatted"""
    try:
        competitions = CompetitionService.get_competitions_by_type(competition_type)
        
        # Transform database results into properly formatted response
        formatted_competitions = []
        for comp in competitions:
            formatted_competitions.append({
                "id": comp['competition_id'],
                "created_time": comp['created_time'].isoformat() if comp['created_time'] else None,
                "end_time": comp['end_time'].isoformat() if comp['end_time'] else None,
                "status": comp['status'],
                "type": comp['type'],
                "number": comp['number']
            })
        
        return jsonify({
            "type": competition_type,
            "competitions": formatted_competitions,
            "total": len(formatted_competitions),
            "message": "Success"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
