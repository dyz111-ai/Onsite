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
            # 创建实时日志文件路径
            current_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            realtime_log_dir = os.path.join(project_root, 'cache', 'train', f'train{training_id}')
            os.makedirs(realtime_log_dir, exist_ok=True)
            realtime_log_path = os.path.join(realtime_log_dir, 'realtime.log')
            
            # 根据操作系统选择执行方式
            if platform.system() == 'Windows':
                process = subprocess.Popen(
                    ["cmd.exe", "/c", script_path, str(training_id)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                    cwd=os.path.dirname(script_path),
                    bufsize=0,
                    universal_newlines=False,
                    close_fds=False
                )
            else:
                process = subprocess.Popen(
                    ["bash", script_path, str(training_id)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                    cwd=os.path.dirname(script_path),
                    bufsize=0,
                    universal_newlines=False,
                    close_fds=True
                )

            # 关闭stdin，避免子进程等待输入
            if process.stdin:
                process.stdin.close()

            # 实时读取输出并保存到文件
            selected_port = None
            with open(realtime_log_path, 'a', encoding='utf-8') as log_file:
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                        
                    try:
                        decoded_line = line.decode('utf-8').strip()
                    except UnicodeDecodeError:
                        try:
                            decoded_line = line.decode('gbk').strip()
                        except UnicodeDecodeError:
                            decoded_line = line.decode('utf-8', errors='ignore').strip()

                    if decoded_line:
                        # 保存到文件
                        log_file.write(decoded_line + '\n')
                        log_file.flush()
                        
                        # 检测服务器端口信息
                        if 'Using server port:' in decoded_line:
                            try:
                                selected_port = int(decoded_line.split(':')[-1].strip())
                                # 保存服务器端口到数据库
                                TrainingService.update_server_port(training_id, selected_port)
                            except:
                                pass
                        
                        socketio.emit('training_log', {'message': decoded_line, 'training_id': training_id})

            # 等待进程结束
            returncode = process.wait()
            
            # 确保关闭所有流
            if process.stdout:
                process.stdout.close()

            if returncode == 0:
                # 训练成功，计算并更新成本
                TrainingService.calculate_and_update_cost(training_id, socketio)
                
                # 更新状态为 Trained 并设置结束时间
                TrainingService.update_training_status(training_id, 'Trained', set_end_time=True)
                
                socketio.emit('training_complete', {'status': 'success', 'message': '训练完成', 'training_id': training_id})
            else:
                # 训练失败也设置结束时间
                TrainingService.update_training_status(training_id, 'Training', set_end_time=True)
                socketio.emit('training_complete', {'status': 'error', 'message': f'训练失败 (返回码: {returncode})', 'training_id': training_id})

        except Exception as e:
            socketio.emit('training_complete', {'status': 'error', 'message': str(e), 'training_id': training_id})
    
    @staticmethod
    def calculate_and_update_cost(training_id, socketio):
        """计算并更新训练成本"""
        try:
            current_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            csv_path = os.path.join(project_root, 'cache', 'train', f'train{training_id}', 'resource_usage.csv')
            
            if os.path.exists(csv_path):
                TrainingTask.update_cost_from_csv(training_id, csv_path)
        except Exception as e:
            pass
    
    @staticmethod
    def update_training_status(training_id, status, set_end_time=False):
        """更新训练状态"""
        try:
            from datetime import datetime
            record = TrainingTask.get_by_id(training_id)
            if record:
                record.status = status
                if set_end_time:
                    record.end_time = datetime.now()
                record.update()
        except Exception as e:
            print(f'更新训练状态失败: {e}')
    
    @staticmethod
    def update_server_port(training_id, server_port):
        """更新训练使用的服务器端口"""
        try:
            record = TrainingTask.get_by_id(training_id)
            if record:
                record.server_port = server_port
                record.update()
        except Exception as e:
            pass
    
    @staticmethod
    def get_script_path():
        """获取训练脚本路径"""
        command_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'command')
        
        if platform.system() == 'Windows':
            script_path = os.path.join(command_dir, 'run_autodl.bat')
        else:
            script_path = os.path.join(command_dir, 'run_autodl.sh')
        
        return script_path
    
    @staticmethod
    def kill_training_processes(training_id):
        """终止指定训练ID的训练进程（仅在对应服务器上）"""
        try:
            # 获取训练记录，查看使用的服务器端口
            record = TrainingTask.get_by_id(training_id)
            if not record or not record.server_port:
                return
            
            # 只在对应的服务器上终止进程
            try:
                # 终止所有 train.py 和 torch.distributed.launch 相关进程
                kill_cmd = "pkill -9 -f 'train.py' && pkill -9 -f 'torch.distributed.launch'"
                
                ssh_cmd = [
                    'ssh',
                    '-p', str(record.server_port),
                    f"root@connect.cqa1.seetacloud.com",
                    kill_cmd
                ]
                
                subprocess.run(ssh_cmd, capture_output=True, timeout=10)
            except Exception:
                pass
        except Exception:
            pass
