import subprocess
import threading
import os
import platform
from app.models.task_submit import TaskSubmit
from app.utils.file_utils import save_file
from flask import current_app

class TaskSubmitService:
    """竞赛服务类，处理竞赛相关操作"""
    
    @staticmethod
    # In app/services/competition.py
    def submit_task(user_id, created_time, name, open_scenario_file, target_points_file):
        try:
            status = "Rendering"
            render_id = TaskSubmit.submit_task(
                user_id,
                status,
                created_time, 
                name, 
            )

            task_type = "render"
            # Save files to appropriate directories
            save_file(open_scenario_file, 'OpenSCENARIO', render_id, task_type)
            save_file(target_points_file, 'destination', render_id, task_type)
            
            # FIX: Use proper path resolution based on current file location
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            script_path = os.path.join(base_dir, "command", "render_with_monitoring.sh")
            app = current_app._get_current_object()
            
            # Execute render_dataset.sh script in a new thread without waiting
            def run_render_script():
                with app.app_context():
                    try:
                        # Run the script and capture results
                        result = subprocess.run(
                            [script_path, str(render_id)],
                            capture_output=True,
                            text=True
                        )
                        
                        # Only set published if script completed successfully (exit code 0)
                        TaskSubmit.set_completed(render_id)
                        if result.returncode == 0:
                            app.logger.info(f"Render {render_id} published successfully")
                        else:
                            app.logger.error(
                                f"Render script failed with exit code {result.returncode}\n"
                                f"Stdout: {result.stdout}\n"
                                f"Stderr: {result.stderr}"
                            )
                    except subprocess.TimeoutExpired:
                        app.logger.error(f"Render script timed out for competition {render_id}")
                    except Exception as e:
                        app.logger.error(f"Error executing render script: {str(e)}")
                        
            # Start the thread
            render_thread = threading.Thread(target=run_render_script)
            render_thread.start()
            
            return render_id
        except Exception as e:
            raise Exception(f"Failed to create competition: {str(e)}")

