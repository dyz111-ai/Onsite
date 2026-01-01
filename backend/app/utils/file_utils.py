# 文件操作工具函数

@staticmethod
def save_file(file, file_type, competition_id, task_type):
    """Save uploaded file to appropriate directory"""
    from flask import current_app
    import os
    import uuid

    if task_type not in ['competition', 'render']:
        raise ValueError("Invalid task type. Must be 'competition' or 'render'.")
    
    # Create directory if it doesn't exist
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], "frontend","cache", task_type, file_type)
    os.makedirs(upload_dir, exist_ok=True)

    extension = file.filename.rsplit('.', 1)[1].lower()
    
    # Generate unique filename
    filename = f"{competition_id}.{extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    file.save(file_path)
    return file_path