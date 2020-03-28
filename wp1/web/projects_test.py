import json

from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase


class ProjectTest(BaseWebTestcase):

  def setUp(self):
    super().setUp()
    projects = []
    for i in range(101):
      projects.append({
          'p_project': b'Project %s' % str(i).encode('utf-8'),
          'p_timestamp': b'20181225'
      })

    ratings = []
    for i in range(25):
      for quality in ('FA-Class', 'A-Class', 'B-Class'):
        for importance in ('High-Class', 'Low-Class'):
          ratings.append({
              'r_project': 'Project 0',
              'r_namespace': 0,
              'r_article': '%s_%s_%s' % (quality, importance, i),
              'r_score': 0,
              'r_quality': quality,
              'r_quality_timestamp': '20191225T00:00:00',
              'r_importance': importance,
              'r_importance_timestamp': '20191226T00:00:00',
          })

    with self.wp10db.cursor() as cursor:
      cursor.executemany(
          'INSERT INTO projects (p_project, p_timestamp) '
          'VALUES (%(p_project)s, %(p_timestamp)s)', projects)
      cursor.executemany(
          'INSERT INTO ratings '
          '(r_project, r_namespace, r_article, r_score, r_quality, '
          ' r_quality_timestamp, r_importance, r_importance_timestamp) '
          'VALUES '
          '(%(r_project)s, %(r_namespace)s, %(r_article)s, %(r_score)s, '
          ' %(r_quality)s, %(r_quality_timestamp)s, %(r_importance)s, '
          ' %(r_importance_timestamp)s)', ratings)
    self.wp10db.commit()

  def test_list(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/')
      data = json.loads(rv.data)
      self.assertEqual(101, len(data))

  def test_count(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/count')
      data = json.loads(rv.data)
      self.assertEqual(101, data['count'])

  def test_table(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 1/table')
      data = json.loads(rv.data)
      self.assertTrue('data' in data['table_data'])

  def test_table_404(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Foo Fake Project/table')
      self.assertEqual('404 NOT FOUND', rv.status)

  def test_articles_ok(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/articles')
      self.assertEqual('200 OK', rv.status)

  def test_articles_returned(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/articles')
      data = json.loads(rv.data)

      # Currently limited to 100 items
      self.assertEqual(100, len(data))

  def test_articles_quality_only(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/articles?quality=FA-Class')
      data = json.loads(rv.data)

      # Currently limited to 100 items
      self.assertEqual(50, len(data))
      for article in data:
        self.assertEqual('FA', article['quality'])

  def test_articles_importance_only(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/articles?importance=High-Class')
      data = json.loads(rv.data)

      self.assertEqual(75, len(data))
      for article in data:
        self.assertEqual('High', article['importance'])

  def test_articles_quality_importance(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get(
          '/v1/projects/Project 0/articles?quality=A-Class&importance=Low-Class'
      )
      data = json.loads(rv.data)

      self.assertEqual(25, len(data))
      for article in data:
        self.assertEqual('Low', article['importance'])
        self.assertEqual('A', article['quality'])

  def test_articles_no_results(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get(
          '/v1/projects/Project 0/articles?quality=Foo-Bar&importance=Low-Class'
      )
      self.assertEqual('200 OK', rv.status)
      data = json.loads(rv.data)
      self.assertEqual(0, len(data))