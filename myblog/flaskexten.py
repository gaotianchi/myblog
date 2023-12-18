"""
Created: 2023-11-20
Author: Gao Tianchi
"""

from flask_cors import CORS
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
mail = Mail()
cors = CORS()
