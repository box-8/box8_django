from django.http import HttpRequest
from typing import Any, Dict

class SessionManager:
    @staticmethod
    def init_session(request: HttpRequest, defaults: Dict[str, Any] = None) -> None:
        if defaults is None:
            defaults = {}
        
        default_settings = {
            'selected_llm': 'openai',
            **defaults
        }
        
        for key, value in default_settings.items():
            if key not in request.session:
                request.session[key] = value
    
    @staticmethod
    def get_user_directory(request: HttpRequest, base_path: str) -> str:
        return os.path.join(base_path, str(request.user.id))
    
    @staticmethod
    def set_session_data(request: HttpRequest, key: str, value: Any) -> None:
        request.session[key] = value
    
    @staticmethod
    def get_session_data(request: HttpRequest, key: str, default: Any = None) -> Any:
        return request.session.get(key, default)
