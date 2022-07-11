"""Gunicorn configuration"""

wsgi_app = "server:create_api()"
workers = 2
bind = "0.0.0.0:18000"
