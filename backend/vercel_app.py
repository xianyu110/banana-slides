"""
Vercel Serverless Function Entry Point
This file adapts the Flask app for Vercel's serverless environment
"""
import os
import sys

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import app

# Vercel requires a variable named 'app' or 'application'
# The Flask app is already created in app.py
# We just need to export it
application = app

# For Vercel serverless functions
def handler(event, context):
    """AWS Lambda-style handler for Vercel"""
    return application(event, context)
