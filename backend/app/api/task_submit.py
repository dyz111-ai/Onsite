# 训练相关的 API 路由
from flask import Blueprint, jsonify, request
import threading
import os
from app.models.task_submit import TaskSubmit
from app.utils.jwt_utils import decode_token
from app.services.task_submit import TaskSubmitService
from flask import send_from_directory

task_submit_bp = Blueprint('task_submit', __name__, url_prefix='/api/task-submit')

@task_submit_bp.route('/submit', methods=['POST'])
def submit_task():
    """提交一个赛题"""
    try:
        # For multipart/form-data, use request.form and request.files
        user_id = request.form.get('user_id')
        status = request.form.get('status')
        created_time = request.form.get('created_time')
        name = request.form.get('name')

        open_scenario_file = request.files.get('open_scenario')
        target_points_file = request.files.get('target_points')
        
        # Validate required fields
        if not all([user_id, status, created_time, name, open_scenario_file, target_points_file]):
            return jsonify({"error": "Missing required fields"}), 400
            
        # Process the files and create competition
        TaskSubmitService.submit_task(
            user_id, 
            created_time, 
            name, 
            open_scenario_file, 
            target_points_file
        )
        
        return jsonify({"message": "成功提交", "status": "started"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

