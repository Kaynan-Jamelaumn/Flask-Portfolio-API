from flask import Blueprint, render_template, url_for, request, flash, redirect, jsonify
from flask_login import login_required, current_user
from .models import Project, User
import json
from website import db
views = Blueprint('views', __name__)
