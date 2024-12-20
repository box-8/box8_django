import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHAREPOINT_DIR = os.path.join(BASE_DIR, 'chatapp', 'sharepoint')
DATASETS_DIR = os.path.join(SHAREPOINT_DIR, 'datasets')

# Session keys
SESSION_SELECTED_LLM = 'selected_llm'
SESSION_CURRENT_ANALYSE = 'current_analyse'
SESSION_CURRENT_FICHES = 'current_fiches'

# File extensions
PDF_EXTENSION = '.pdf'
DOCX_EXTENSION = '.docx'
JSON_EXTENSION = '.json'

# Response messages
MSG_SUCCESS = 'success'
MSG_ERROR = 'error'
MSG_SELECT_FILE = 'Please select a file'
MSG_INVALID_REQUEST = 'Invalid request'
