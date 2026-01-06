import subprocess
import threading
import os
import platform
from app.models.competition import Competition
from app.utils.file_utils import save_file
from flask import current_app

class CompetitionService:
    """竞赛服务类，处理竞赛相关操作"""
    
    @staticmethod
    # In app/services/competition.py
    def create_competition(created_time, end_time, status, type, number, open_scenario_file, target_points_file):
        """Create a new competition with file uploads"""
        try:
            # Create competition record with file paths
            competition_id = Competition.insert(
                created_time=created_time,
                end_time=end_time,
                status=status,
                type=type,
                number=number
            )

            # Save files to appropriate directories
            save_file(open_scenario_file, 'OpenSCENARIO', competition_id, "competition")
            save_file(target_points_file, 'destination', competition_id, "competition")
            
            # FIX: Use proper path resolution based on current file location
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            script_path = os.path.join(base_dir, "command", "render_datasets.sh")
            app = current_app._get_current_object()
            
            # Execute render_dataset.sh script in a new thread without waiting
            def run_render_script():
                with app.app_context():
                    try:
                        # Run the script and capture results
                        result = subprocess.run(
                            [script_path, "competition", str(competition_id)],
                            capture_output=True,
                            text=True
                        )
                        
                        # Only set published if script completed successfully (exit code 0)
                        if result.returncode == 0:
                            Competition.set_published(competition_id)
                            app.logger.info(f"Competition {competition_id} published successfully")
                        else:
                            Competition.set_failed(competition_id)
                            app.logger.error(
                                f"Render script failed with exit code {result.returncode}\n"
                                f"Stdout: {result.stdout}\n"
                                f"Stderr: {result.stderr}"
                            )
                    except subprocess.TimeoutExpired:
                        app.logger.error(f"Render script timed out for competition {competition_id}")
                    except Exception as e:
                        app.logger.error(f"Error executing render script: {str(e)}")
                        
            # Start the thread
            render_thread = threading.Thread(target=run_render_script)
            render_thread.start()
            
            return competition_id
        except Exception as e:
            raise Exception(f"Failed to create competition: {str(e)}")


    @staticmethod
    def get_min_number_by_type(competition_type: str) -> int:
        """获取指定类型竞赛的最小题号"""
        min = Competition.get_min_number_by_type(competition_type)
        if min:
            return min
        else:
            return 0
        
    @staticmethod
    def get_competitions_by_type(competition_type: str):
        """获取指定类型竞赛"""
        competitions = Competition.get_competitions_by_type(competition_type)
        return competitions