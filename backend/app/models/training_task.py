from app.database import get_db_cursor

class TrainingTask:
    def __init__(self, training_id, user_id, created_time, status, train_cost, test_score, total_score, server_port=None, end_time=None):
        self.training_id = training_id
        self.user_id = user_id
        self.created_time = created_time
        self.status = status
        self.train_cost = train_cost
        self.test_score = test_score
        self.total_score = total_score
        self.server_port = server_port
        self.end_time = end_time
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.training_id,  # 前端使用 id
            'training_id': self.training_id,  # 保留原字段
            'user_id': self.user_id,
            'createdAt': str(self.created_time) if self.created_time else None,  # 前端使用 createdAt
            'created_time': str(self.created_time) if self.created_time else None,  # 保留原字段
            'end_time': str(self.end_time) if self.end_time else None,
            'status': self.status,
            'train_cost': self.train_cost,
            'test_score': self.test_score,
            'total_score': self.total_score,
            'server_port': self.server_port,
            'competition_type': getattr(self, 'competition_type', None),
            'competition_number': getattr(self, 'competition_number', None),
            'render_cost': getattr(self, 'render_cost', 0.0),
            'dataset_count': getattr(self, 'dataset_count', 0)
        }
    
    @staticmethod
    def get_all_by_user(user_id):
        """获取指定用户的所有训练记录（包含测试赛题信息和渲染成本）"""
        try:
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    """
                    SELECT 
                        t.training_id, t.user_id, t.created_time, t.status, 
                        t.train_cost, t.test_score, t.total_score, t.server_port, t.end_time,
                        c.type as competition_type, c.number as competition_number,
                        COALESCE(SUM(r.render_cost), 0) as render_cost,
                        COUNT(trr.render_id) as dataset_count
                    FROM training_task t
                    LEFT JOIN test_task tt ON t.training_id = tt.training_id
                    LEFT JOIN competition c ON tt.competition_id = c.competition_id
                    LEFT JOIN training_render_relation trr ON t.training_id = trr.training_id
                    LEFT JOIN render r ON trr.render_id = r.render_id
                    WHERE t.user_id = %s
                    GROUP BY t.training_id, t.user_id, t.created_time, t.status, 
                             t.train_cost, t.test_score, t.total_score, t.server_port, t.end_time,
                             c.type, c.number
                    ORDER BY t.created_time DESC
                    """,
                    (user_id,)
                )
                results = cursor.fetchall()
                
                records = []
                for row in results:
                    record = TrainingTask(
                        training_id=row['training_id'],
                        user_id=row['user_id'],
                        created_time=row['created_time'],
                        status=row['status'],
                        train_cost=row['train_cost'],
                        test_score=row['test_score'],
                        total_score=row['total_score'],
                        server_port=row.get('server_port'),
                        end_time=row.get('end_time')
                    )
                    # 添加赛题信息
                    record.competition_type = row['competition_type']
                    record.competition_number = row['competition_number']
                    # 添加渲染成本
                    record.render_cost = float(row['render_cost']) if row['render_cost'] else 0.0
                    # 添加数据集数量
                    record.dataset_count = int(row['dataset_count']) if row.get('dataset_count') else 0
                    records.append(record)
                
                return records
        except Exception as e:
            print(f"获取训练记录失败: {e}")
            return []
    
    @staticmethod
    def get_all():
        """获取所有训练记录"""
        try:
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    """
                    SELECT training_id, user_id, created_time, status, 
                           train_cost, test_score, total_score
                    FROM training_task
                    ORDER BY created_time DESC
                    """
                )
                results = cursor.fetchall()
                
                return [TrainingTask(
                    training_id=row['training_id'],
                    user_id=row['user_id'],
                    created_time=row['created_time'],
                    status=row['status'],
                    train_cost=row['train_cost'],
                    test_score=row['test_score'],
                    total_score=row['total_score']
                ) for row in results]
        except Exception as e:
            print(f"获取训练记录失败: {e}")
            return []
    
    @staticmethod
    def get_by_id(training_id):
        """根据ID获取训练记录"""
        try:
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    """
                    SELECT training_id, user_id, created_time, status, 
                           train_cost, test_score, total_score, server_port, end_time
                    FROM training_task
                    WHERE training_id = %s
                    """,
                    (training_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return TrainingTask(
                        training_id=row['training_id'],
                        user_id=row['user_id'],
                        created_time=row['created_time'],
                        status=row['status'],
                        train_cost=row['train_cost'],
                        test_score=row['test_score'],
                        total_score=row['total_score'],
                        server_port=row.get('server_port'),
                        end_time=row.get('end_time')
                    )
                return None
        except Exception as e:
            print(f"获取训练记录失败: {e}")
            return None
    
    @staticmethod
    def create(user_id, status='Training', train_cost=0.0, test_score=0.0, total_score=0.0):
        """创建新的训练记录"""
        try:
            from datetime import datetime
            with get_db_cursor() as cursor:
                # 使用 Python 本地时间
                created_time = datetime.now()
                cursor.execute(
                    """
                    INSERT INTO training_task 
                    (user_id, created_time, status, train_cost, test_score, total_score)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING training_id, user_id, created_time, status, train_cost, test_score, total_score
                    """,
                    (user_id, created_time, status, train_cost, test_score, total_score)
                )
                row = cursor.fetchone()
                
                return TrainingTask(
                    training_id=row['training_id'],
                    user_id=row['user_id'],
                    created_time=row['created_time'],
                    status=row['status'],
                    train_cost=row['train_cost'],
                    test_score=row['test_score'],
                    total_score=row['total_score']
                )
        except Exception as e:
            print(f"创建训练记录失败: {e}")
            raise e
    
    def update(self):
        """更新训练记录"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE training_task
                    SET status = %s, train_cost = %s, test_score = %s, total_score = %s, server_port = %s, end_time = %s
                    WHERE training_id = %s
                    """,
                    (self.status, self.train_cost, self.test_score, self.total_score, self.server_port, self.end_time, self.training_id)
                )
        except Exception as e:
            print(f"更新训练记录失败: {e}")
            raise e
    
    @staticmethod
    def calculate_cost_from_csv(csv_path):
        """从CSV文件计算训练成本"""
        import csv
        
        try:
            total_training_time = 0
            total_cpu_usage = 0
            total_gpu_utilization = 0
            total_memory_usage = 0
            row_count = 0
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_training_time = float(row['training_time_seconds'])
                    total_cpu_usage += float(row['cpu_usage_total_seconds'])
                    total_gpu_utilization += float(row['gpu_utilization_total(%)'])
                    total_memory_usage += float(row['memory_usage_total_mb'])
                    row_count += 1
            
            if row_count == 0:
                return 0.0
            
            # 计算平均值
            avg_cpu = total_cpu_usage / row_count
            avg_gpu = total_gpu_utilization / row_count
            avg_memory = total_memory_usage / row_count
            
            # 成本计算公式（可以根据实际情况调整权重）
            # CPU: 每秒 0.0001 元
            # GPU: 每百分比 0.001 元
            # 内存: 每MB 0.00001 元
            cpu_cost = avg_cpu * 0.0001
            gpu_cost = avg_gpu * 0.001
            memory_cost = avg_memory * 0.00001
            
            total_cost = cpu_cost + gpu_cost + memory_cost
            
            return round(total_cost, 4)
        except Exception as e:
            print(f"计算成本失败: {e}")
            return 0.0
    
    @staticmethod
    def update_cost_from_csv(training_id, csv_path):
        """从CSV文件读取数据并更新训练成本"""
        try:
            cost = TrainingTask.calculate_cost_from_csv(csv_path)
            
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE training_task
                    SET train_cost = %s
                    WHERE training_id = %s
                    """,
                    (cost, training_id)
                )
            
            return cost
        except Exception as e:
            print(f"更新训练成本失败: {e}")
            raise e
    
    @staticmethod
    def delete(training_id):
        """删除训练记录（级联删除关联的 training_render_relation 和 test_task）"""
        try:
            with get_db_cursor() as cursor:
                # 先删除 training_render_relation 中的关联记录
                cursor.execute("DELETE FROM training_render_relation WHERE training_id = %s", (training_id,))
                
                # 删除 test_task 中的关联记录
                cursor.execute("DELETE FROM test_task WHERE training_id = %s", (training_id,))
                
                # 最后删除训练记录本身
                cursor.execute("DELETE FROM training_task WHERE training_id = %s", (training_id,))
        except Exception as e:
            print(f"删除训练记录失败: {e}")
            raise e

    @staticmethod
    def get_leaderboard():
        """
        获取总分排行榜数据
        逻辑：找到每个参赛选手的最高分数记录，按分数排序
        注意：所有参赛选手都要显示，没有训练任务的选手分数记为0，排在最后
        """
        try:
            with get_db_cursor(commit=False) as cursor:
                # 查询每个参赛选手的最高分数记录，包括没有训练任务的选手
                # 使用窗口函数ROW_NUMBER()来获取每个用户的最高分记录
                # 分数相同时按创建时间排序，还相同按user_id排序
                query = """
                WITH all_participants AS (
                    SELECT participant_id as user_id, account FROM participant
                ),
                ranked_tasks AS (
                    SELECT 
                        p.user_id,
                        p.account,
                        t.training_id,
                        t.created_time,
                        t.total_score,
                        ROW_NUMBER() OVER (
                            PARTITION BY p.user_id 
                            ORDER BY 
                                COALESCE(t.total_score, 0) DESC,
                                t.created_time DESC,
                                p.account ASC
                        ) as rank_within_user,
                        CASE WHEN t.training_id IS NOT NULL THEN 1 ELSE 0 END as has_training_data
                    FROM all_participants p
                    LEFT JOIN training_task t ON p.user_id = t.user_id
                )
                SELECT 
                    ROW_NUMBER() OVER (
                        ORDER BY 
                            rt.has_training_data DESC,
                            COALESCE(rt.total_score, 0) DESC,
                            rt.created_time DESC,
                            rt.account ASC
                    ) as global_rank,
                    rt.user_id,
                    rt.account,
                    COALESCE(rt.total_score, 0) as max_score,
                    rt.created_time
                FROM ranked_tasks rt
                WHERE rt.rank_within_user = 1
                ORDER BY 
                    rt.has_training_data DESC,
                    max_score DESC,
                    rt.created_time DESC,
                    rt.account ASC
                """
                
                cursor.execute(query)
                results = cursor.fetchall()
                
                return results
        except Exception as e:
            print(f"获取总分排行榜数据失败: {e}")
            raise e
    
    @staticmethod
    def get_leaderboard_by_cost():
        """
        获取训练成本排行榜数据
        逻辑：找到每个参赛选手的最低成本记录，按成本排序（越低越好）
        注意：所有参赛选手都要显示，0或NULL的成本视为无穷大，排在最后
        """
        try:
            with get_db_cursor(commit=False) as cursor:
                # 查询每个参赛选手的最低成本记录，包括没有训练任务的选手
                # 使用窗口函数ROW_NUMBER()来获取每个用户的最低成本记录
                # 成本相同时按创建时间排序，还相同按user_id排序
                query = """
                WITH all_participants AS (
                    SELECT participant_id as user_id, account FROM participant
                ),
                ranked_tasks AS (
                    SELECT 
                        p.user_id,
                        p.account,
                        t.training_id,
                        t.created_time,
                        t.train_cost,
                        ROW_NUMBER() OVER (
                            PARTITION BY p.user_id 
                            ORDER BY 
                                CASE 
                                    WHEN t.train_cost IS NULL OR t.train_cost = 0 THEN 1 ELSE 0 END ASC,
                                t.train_cost ASC,
                                t.created_time DESC,
                                p.account ASC
                        ) as rank_within_user,
                        CASE WHEN t.training_id IS NOT NULL THEN 1 ELSE 0 END as has_training_data
                    FROM all_participants p
                    LEFT JOIN training_task t ON p.user_id = t.user_id
                )
                SELECT 
                    ROW_NUMBER() OVER (
                        ORDER BY 
                            rt.has_training_data DESC,
                            CASE 
                                WHEN rt.train_cost IS NULL OR rt.train_cost = 0 THEN 1 ELSE 0 END ASC,
                            rt.train_cost ASC,
                            rt.created_time DESC,
                            rt.account ASC
                    ) as global_rank,
                    rt.user_id,
                    rt.account,
                    CASE 
                        WHEN rt.train_cost IS NULL OR rt.train_cost = 0 THEN '无穷大' 
                        ELSE rt.train_cost::TEXT 
                    END as min_cost,
                    rt.created_time
                FROM ranked_tasks rt
                WHERE rt.rank_within_user = 1
                ORDER BY 
                    rt.has_training_data DESC,
                    CASE 
                        WHEN rt.train_cost IS NULL OR rt.train_cost = 0 THEN 1 ELSE 0 END ASC,
                    rt.train_cost ASC,
                    rt.created_time DESC,
                    rt.account ASC
                """
                
                cursor.execute(query)
                results = cursor.fetchall()
                
                return results
        except Exception as e:
            print(f"获取成本排行榜数据失败: {e}")
            raise e
    
    @staticmethod
    def get_leaderboard_by_test_score():
        """
        获取测试分数排行榜数据
        逻辑：找到每个参赛选手的最高测试分数记录，按分数排序（越高越好）
        注意：所有参赛选手都要显示，没有训练任务的选手测试分数记为0，排在最后
        """
        try:
            with get_db_cursor(commit=False) as cursor:
                # 查询每个参赛选手的最高测试分数记录，包括没有训练任务的选手
                # 使用窗口函数ROW_NUMBER()来获取每个用户的最高测试分数记录
                # 分数相同时按创建时间排序，还相同按user_id排序
                query = """
                WITH all_participants AS (
                    SELECT participant_id as user_id, account FROM participant
                ),
                ranked_tasks AS (
                    SELECT 
                        p.user_id,
                        p.account,
                        t.training_id,
                        t.created_time,
                        t.test_score,
                        ROW_NUMBER() OVER (
                            PARTITION BY p.user_id 
                            ORDER BY 
                                COALESCE(t.test_score, 0) DESC,
                                t.created_time DESC,
                                p.account ASC
                        ) as rank_within_user,
                        CASE WHEN t.training_id IS NOT NULL THEN 1 ELSE 0 END as has_training_data
                    FROM all_participants p
                    LEFT JOIN training_task t ON p.user_id = t.user_id
                )
                SELECT 
                    ROW_NUMBER() OVER (
                        ORDER BY 
                            rt.has_training_data DESC,
                            COALESCE(rt.test_score, 0) DESC,
                            rt.created_time DESC,
                            rt.account ASC
                    ) as global_rank,
                    rt.user_id,
                    rt.account,
                    COALESCE(rt.test_score, 0) as max_test_score,
                    rt.created_time
                FROM ranked_tasks rt
                WHERE rt.rank_within_user = 1
                ORDER BY 
                    rt.has_training_data DESC,
                    max_test_score DESC,
                    rt.created_time DESC,
                    rt.account ASC
                """
                
                cursor.execute(query)
                results = cursor.fetchall()
                
                return results
        except Exception as e:
            print(f"获取测试分数排行榜数据失败: {e}")
            raise e
    
    @staticmethod
    def get_user_best_score(user_id):
        """
        获取指定用户的最高分数记录
        """
        try:
            with get_db_cursor(commit=False) as cursor:
                query = """
                SELECT 
                    training_id,
                    user_id,
                    created_time,
                    status,
                    train_cost,
                    test_score,
                    total_score
                FROM training_task
                WHERE user_id = %s
                ORDER BY 
                    COALESCE(total_score, 0) DESC,
                    created_time DESC
                LIMIT 1
                """
                
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                
                if result:
                    return TrainingTask(**result)
                return None
        except Exception as e:
            print(f"获取用户最高分记录失败: {e}")
            raise e
