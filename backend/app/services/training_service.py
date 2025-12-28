# 训练服务：训练任务处理
import subprocess
import os
import platform
from app.models.training_task import TrainingTask


class TrainingService:
    """训练服务类，处理训练脚本执行和成本计算"""
    
    @staticmethod
    def run_training_script(script_path, training_id, socketio):
        """在后台线程中执行训练脚本并实时发送输出"""
        try:
            socketio.emit('training_log', {'message': f'开始执行脚本: {os.path.basename(script_path)}'})
            socketio.emit('training_log', {'message': f'训练ID: {training_id}'})

            # 根据操作系统选择执行方式
            if platform.system() == 'Windows':
                # Windows系统执行bat，传递 training_id 参数
                process = subprocess.Popen(
                    ["cmd.exe", "/c", script_path, str(training_id)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    cwd=os.path.dirname(script_path),
                    bufsize=1,
                    universal_newlines=False
                )
            else:
                # Linux/Unix系统执行sh，传递 training_id 参数
                process = subprocess.Popen(
                    ["bash", script_path, str(training_id)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    cwd=os.path.dirname(script_path),
                    bufsize=1,
                    universal_newlines=False
                )

            # 实时读取输出，尝试多种编码
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                    
                try:
                    # 尝试UTF-8解码
                    decoded_line = line.decode('utf-8').strip()
                except UnicodeDecodeError:
                    try:
                        # 如果UTF-8失败，尝试GBK
                        decoded_line = line.decode('gbk').strip()
                    except UnicodeDecodeError:
                        # 如果都失败，忽略错误
                        decoded_line = line.decode('utf-8', errors='ignore').strip()

                if decoded_line:
                    socketio.emit('training_log', {'message': decoded_line})

            # 等待进程结束
            returncode = process.wait()

            socketio.emit('training_log', {'message': f'脚本执行完毕，返回码: {returncode}'})

            if returncode == 0:
                # 训练成功，计算并更新成本
                TrainingService.calculate_and_update_cost(training_id, socketio)
                socketio.emit('training_complete', {'status': 'success', 'message': '训练完成', 'training_id': training_id})
            else:
                socketio.emit('training_complete', {'status': 'error', 'message': f'训练失败 (返回码: {returncode})', 'training_id': training_id})

        except Exception as e:
            socketio.emit('training_log', {'message': f'执行脚本时发生异常: {str(e)}'})
            socketio.emit('training_complete', {'status': 'error', 'message': str(e), 'training_id': training_id})
    
    @staticmethod
    def calculate_and_update_cost(training_id, socketio):
        """计算并更新训练成本"""
        try:
            # 获取项目根目录（backend/app/services -> backend/app -> backend -> 项目根）
            current_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            csv_path = os.path.join(project_root, 'cache', 'train', f'train{training_id}', 'resource_usage.csv')
            
            socketio.emit('training_log', {'message': f'查找CSV文件: {csv_path}'})
            
            if os.path.exists(csv_path):
                cost = TrainingTask.update_cost_from_csv(training_id, csv_path)
                socketio.emit('training_log', {'message': f'训练成本已计算: {cost} 元'})
            else:
                socketio.emit('training_log', {'message': f'警告: 未找到资源使用数据文件 {csv_path}'})
        except Exception as e:
            socketio.emit('training_log', {'message': f'计算成本时出错: {str(e)}'})
    
    @staticmethod
    def get_script_path():
        """获取训练脚本路径"""
        command_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'command')
        
        # 根据操作系统选择脚本文件
        if platform.system() == 'Windows':
            script_path = os.path.join(command_dir, 'run_autodl.bat')
        else:
            script_path = os.path.join(command_dir, 'run_autodl.sh')
        
        return script_path
