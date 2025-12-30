# 训练相关的 API 路由
from flask import Blueprint, jsonify, request
import threading
import os
from app.models.competition import Competition
from app.utils.jwt_utils import decode_token
from app.services.competition import CompetitionService
from flask import send_from_directory

task_submit_bp = Blueprint('task_submit', __name__, url_prefix='/api/task_submit')

@task_submit_bp.route('/add', methods=['POST'])
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

