import attr
import flask

from wp1.web.db import get_db
import wp1.logic.project as logic_project
import wp1.logic.rating as logic_rating
import wp1.tables as tables

projects = flask.Blueprint('projects', __name__)


@projects.route('/')
def list_():
  wp10db = get_db('wp10db')
  projects = logic_project.list_all_projects(wp10db)
  return flask.jsonify(list(project.to_web_dict() for project in projects))


@projects.route('/count')
def count():
  wp10db = get_db('wp10db')
  count = logic_project.count_projects(wp10db)
  return flask.jsonify({'count': count})


@projects.route('/<project_name>/table')
def table(project_name):
  wp10db = get_db('wp10db')
  project_name_bytes = project_name.encode('utf-8')
  project = logic_project.get_project_by_name(wp10db, project_name_bytes)
  if project is None:
    return flask.abort(404)

  data = tables.generate_project_table_data(wp10db, project_name_bytes)
  data = tables.convert_table_data_for_web(data)

  return flask.jsonify({'table_data': data})


@projects.route('/<project_name>/articles')
def articles(project_name):
  wp10db = get_db('wp10db')
  project_name_bytes = project_name.encode('utf-8')
  project = logic_project.get_project_by_name(wp10db, project_name_bytes)
  if project is None:
    return flask.abort(404)

  quality = flask.request.args.get('quality')
  importance = flask.request.args.get('importance')

  if quality:
    quality = quality.encode('utf-8')
  if importance:
    importance = importance.encode('utf-8')

  ratings = logic_rating.get_project_rating_by_type(wp10db,
                                                    project_name_bytes,
                                                    quality=quality,
                                                    importance=importance)

  return flask.jsonify(list(rating.to_web_dict() for rating in ratings))