"""
Configuration file for application.
"""

import os

from dotenv import load_dotenv

load_dotenv()

DATABASE = {
    'uri': os.getenv('MONGO_COLL_URI', 'mongodb://localhost/local')
}
