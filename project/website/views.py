from flask import Blueprint, render_template, url_for, request, flash, redirect, jsonify
from flask_login import current_user
from .models import Project
import json
from website import db, images
from flask_uploads import UploadNotAllowed
from datetime import datetime
views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        public_projects = Project.query.filter_by(public=True).all()
        return render_template("index.html", user=current_user, public_projects=public_projects)


@views.route('/project/', methods=['GET'])
def projects():
    if request.method == 'GET':
        if not current_user.is_authenticated:
            flash('You must be logged in', category='error')
            return redirect(url_for('auth.login'))
        projects = Project.query.filter_by(
            user_id=current_user.id).all()
        return render_template('dashboard.html', projects=projects)


@views.route('/project/create', methods=['POST'])
def project_create():
    if not current_user.is_authenticated:
        flash('You must be logged in', category='error')
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('create.html')

    if request.method == 'POST':
        name = request.form.get('name')
        resume = request.form.get('resume')
        text = request.form.get('text')
        source_code = request.form.get('source-code')
        live_code = request.form.get('live-code')
        image = request.files['image']
        public = request.form.get('public')  # on off
        public = True if public == 'on' else False

        errors = []
        if not name:
            flash('name must not be null')
            errors.append(1)

        new_project = Project(name=name, resume=resume, text=text, source_code=source_code, live_code=live_code,
                              user_id=current_user.id, public=public)
        if image:  # Check if an image was uploaded
            try:
                filename = images.save(image)
                new_project.image = filename
            except UploadNotAllowed:
                flash('Upload Method not allowed', category='error')
                errors.append(2)
        if len(errors) == 0:
            db.session.add(new_project)
            db.session.commit()
            flash('Porject created', category='success')

        else:
            data = {"name", "resume", "text", "source_code",
                    "live_code", "image", "public"}
            return render_template('create.html', data=data)
    return redirect(url_for('views.projects'))


@views.route('/project/<int:projectId>', methods=['GET', 'PUT', 'DELETE'])
def project_action(projectId):
    project = Project.query.get(projectId)
    if not project:
        flash('Project not found', category='error')
        return redirect(url_for('views.projects'))

    if not current_user.is_authenticated and request.method != 'GET':
        flash('You must be logged in', category='error')
        return redirect(url_for('auth.login'))

    if project.user_id != current_user.id and request.method != 'GET':
        flash('This project does not belong to you', category='error')

    if request.method == 'GET':
        if project.user_id != current_user.id and project.public == False:
            flash('this project is not accessible to the public', category='error')
            return redirect(url_for('views.dashboard'))
        return render_template('project.html', project=project)

    if request.method == 'PUT':
        name = request.form.get('name')
        resume = request.form.get('resume')
        text = request.form.get('text')
        source_code = request.form.get('source_code')
        live_code = request.form.get('live_source')
        image = request.files['image']
        public = request.form.get('public')  # on off
        public = True if public == 'on' else False
        if not name:
            flash('Name must not be empty', category='error')
            return redirect(url_for('views.project_action', projectId=projectId))
        else:
            project.name, project.resume, project.text, project.source_code, project.live_code, project.public = name, resume, text, source_code, live_code, public
            project.updated_at = datetime.utcnow()
            if image:
                try:
                    filename = images.save(image)
                    project.image = filename
                except UploadNotAllowed:
                    flash('File type is not allowed',
                          category='error')
            db.session.commit()
            flash('Project updated', category='success')

    if request.method == 'DELETE':
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted', category='success')
    return redirect(url_for('views.projects'))


@views.route('/api/index', methods=['GET',])
def api_index():
    if request.method == 'GET':
        public_projects = Project.query.filter_by(public=True).all()
        projects = [{"id": project.id, "name": project.name, "resume": project.resume, "text": project.text,
                     "source_code": project.source_code, "live_code": project.live_code,
                     "image": project.image, "public": project.public} for project in public_projects]
        return jsonify({"projects": projects}), 200
    return jsonify({"message": "Method not allowed"}), 405


@views.route('/api/projects', methods=['GET'])
def api_projects():
    if request.method == 'GET':
        if not current_user.is_authenticated:
            return jsonify({"error": "You must be logged in"}), 400
        projects = Project.query.filter_by(
            user_ide=current_user.id).all()
        projects = [{"id": project.id, "name": project.name, "resume": project.resume, "text": project.text,
                     "source_code": project.source_code, "live_code": project.live_code,
                     "image": project.image, "public": project.public} for project in projects]
        return jsonify({"projects": projects}), 200

    return jsonify({"message": "Method not allowed"}), 405


@views.route('/api/project/', methods=['POST'])
def api_project_create():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return jsonify({"error": "You must be logged in to add a project"}), 400

        data = request.get_json()
        name = data.get('name')
        resume = data.get('resume')
        text = data.get('text')
        source_code = data.get('source_code')
        live_code = data.get('live_code')
        image = data.get('image')
        public = data.get('public')  # on off

        if not name:
            return jsonify({"error": "Name must not be null"}), 400

        new_project = Project(name=name, resume=resume, text=text, source_code=source_code, live_code=live_code,
                              user_id=current_user.id, public=public)
        if image:  # Check if an image was uploaded
            try:
                filename = images.save(image)
                new_project.image = filename
            except UploadNotAllowed:
                return jsonify({"error": "Upload Method not allowed"}), 400
        db.session.add(new_project)
        db.session.commit()
        return jsonify({"message": "Project added successfully", "project": new_project.to_dict()}), 201
    return jsonify({"message": "Method not allowed"}), 405


@views.route('/api/project/<int:projectId', methods=['GET', 'PUT', 'DELETE'])
def api_project_acition(projectId):
    project = Project.query.get(projectId)

    if not project:
        return jsonify({"error": "Project not found"}), 404

    if request.method == 'GET':
        if not current_user.is_authenticated and project.public == False:
            return jsonify({"error": "You must be logged in to get a project"}), 401

        if project.user_id != current_user.id and project.public == False:
            return jsonify({"error": "This project does not belong to you"}), 401
        project = {"id": project.id, "name": project.name, "resume": project.resume,
                   "text": project.text, "source_code": project.source_code, "live_code": project.live_code, "created_at": project.created_at, "updated_at": project.updated_at, "image": project.image}
        return jsonify({"project": project}), 200

    if request.method == 'PUT':
        if not current_user.is_authenticated:
            return jsonify({"error": "You must be logged in to update a project"}), 400

        if project.user_id != current_user.id:
            return jsonify({"This project does not belong to you"}), 400
        data = request.get_json()
        name = data.get('name')
        resume = data.get('resume')
        text = data.get('text')
        source_code = data.get('source_code')
        live_code = data.get('live_code')
        image = data.get('image')
        public = data.get('public')  # on off
        if not name:
            return jsonify({"error": "Name must not be null"}), 400

        project.name, project.resume, project.text, project.source_code, project.live_code, project.public = name, resume, text, source_code, live_code, public
        project.updated_at = datetime.utcnow()

        if image:  # Check if an image was uploaded
            try:
                filename = images.save(image)
                project.image = filename
            except UploadNotAllowed:
                return jsonify({"error": "Upload Method not allowed"}), 400
        db.session.commit()
        project = {"id": project.id, "name": project.name, "resume": project.resume,
                   "text": project.text, "source_code": project.source_code, "live_code": project.live_code, "created_at": project.created_at, "updated_at": project.updated_at, "image": project.image}
        return jsonify({"project": project}), 200
    if request.method == 'DELETE':
        if not current_user.is_authenticated:
            return jsonify({"error": "You must be logged in to delete a project"}), 400
        if project.user_id != current_user.id:
            return jsonify({"This project does not belong to you"}), 400
        db.session.delete(project)
        db.session.commit()
        return jsonify({"message": "Project deleted"}), 200

    return jsonify({"message": "Method not allowed"}), 405
