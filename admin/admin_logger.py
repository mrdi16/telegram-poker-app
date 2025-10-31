import logging
from datetime import datetime
from typing import Dict, List

class AdminLogger:
    def __init__(self):
        self.action_log = []
    
    def log_admin_action(self, admin_id: int, action_type: str, target: str = "", details: str = ""):
        """Логирование действий администратора"""
        log_entry = {
            'timestamp': datetime.now(),
            'admin_id': admin_id,
            'action_type': action_type,
            'target': target,
            'details': details
        }
        
        self.action_log.append(log_entry)
        
        # Также пишем в консоль
        logging.info(f"ADMIN_ACTION: {action_type} | Admin: {admin_id} | Target: {target} | Details: {details}")
    
    def get_admin_actions(self, admin_id: int = None, action_type: str = None, limit: int = 100) -> List[Dict]:
        """Получить логи действий администраторов"""
        filtered_log = self.action_log
        
        if admin_id:
            filtered_log = [entry for entry in filtered_log if entry['admin_id'] == admin_id]
        if action_type:
            filtered_log = [entry for entry in filtered_log if entry['action_type'] == action_type]
        
        return filtered_log[-limit:]
    
    def get_recent_actions(self, hours: int = 24) -> List[Dict]:
        """Получить действия за последние N часов"""
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        
        recent_actions = [
            entry for entry in self.action_log 
            if entry['timestamp'].timestamp() > cutoff_time
        ]
        
        return recent_actions