# test cases for HOT Export Tasks
import logging
import json
import uuid
import sys
import cPickle
import traceback
import os
from hot_exports import settings
from django.test import TestCase
from django.contrib.auth.models import User
from mock import Mock, patch, PropertyMock, MagicMock
from unittest import skip
from ..task_runners import ExportTaskRunner
from jobs.models import ExportFormat, Job, Tag
from django.contrib.gis.geos import GEOSGeometry, Polygon
from tasks.export_tasks import (ExportTask, ShpExportTask,
                                ObfExportTask, GarminExportTask,
                                KmlExportTask, OSMConfTask,
                                OverpassQueryTask, OSMToPBFConvertTask,
                                OSMPrepSchemaTask)
from tasks.models import ExportRun, ExportTask, ExportTaskResult
from celery.datastructures import ExceptionInfo

logger = logging.getLogger(__name__)
  
class TestExportTasks(TestCase):
    
    def setUp(self,):
        self.user = User.objects.create(username='demo', email='demo@demo.com', password='demo')
        #bbox = Polygon.from_bbox((-7.96, 22.6, -8.14, 27.12))
        bbox = Polygon.from_bbox((-10.85,6.25,-10.62,6.40))
        the_geom = GEOSGeometry(bbox, srid=4326)
        self.job = Job.objects.create(name='TestJob',
                                 description='Test description', user=self.user,
                                 the_geom=the_geom)
        self.run = ExportRun.objects.create(job=self.job)
    
    @patch('celery.app.task.Task.request')
    @patch('utils.osmconf.OSMConfig')
    def test_run_osmconf_task(self, mock_config, mock_request):
        task = OSMConfTask()
        celery_uid = str(uuid.uuid4())
        type(mock_request).id = PropertyMock(return_value=celery_uid)
        osm_conf = mock_config.return_value
        stage_dir = settings.EXPORT_STAGING_ROOT  + str(self.run.uid)
        expected_output_path = stage_dir + '/' + 'export_config.ini'
        osm_conf.create_osm_conf.return_value = expected_output_path
        saved_export_task = ExportTask.objects.create(run=self.run, status='PENDING', name=task.name)
        result = task.run(run_uid=str(self.run.uid), stage_dir=stage_dir)
        osm_conf.create_osm_conf.assert_called_with(stage_dir=stage_dir)
        self.assertEquals(expected_output_path, result['result'])
        # test tasks update_task_state method
        run_task = ExportTask.objects.get(celery_uid=celery_uid)
        self.assertIsNotNone(run_task)
        self.assertEquals('RUNNING', run_task.status)
        
    @patch('celery.app.task.Task.request')
    @patch('utils.overpass.Overpass')
    def test_run_overpass_task(self, mock_overpass, mock_request):
        task = OverpassQueryTask()
        celery_uid = str(uuid.uuid4())
        type(mock_request).id = PropertyMock(return_value=celery_uid)
        overpass_query = mock_overpass.return_value
        stage_dir = settings.EXPORT_STAGING_ROOT  + str(self.run.uid)
        expected_output_path = stage_dir + '/' + 'query.osm'
        overpass_query.run_query.return_value = expected_output_path
        saved_export_task = ExportTask.objects.create(run=self.run, status='PENDING', name=task.name)
        result = task.run(run_uid=str(self.run.uid), stage_dir=stage_dir)
        overpass_query.run_query.assert_called_once()
        self.assertEquals(expected_output_path, result['result'])
        # test tasks update_task_state method
        run_task = ExportTask.objects.get(celery_uid=celery_uid)
        self.assertIsNotNone(run_task)
        self.assertEquals('RUNNING', run_task.status)
        
    @patch('celery.app.task.Task.request')
    @patch('utils.pbf.OSMToPBF')
    def test_run_osmtopbf_task(self, mock_overpass, mock_request):
        task = OSMToPBFConvertTask()
        celery_uid = str(uuid.uuid4())
        type(mock_request).id = PropertyMock(return_value=celery_uid)
        osmtopbf = mock_overpass.return_value
        stage_dir = settings.EXPORT_STAGING_ROOT  + str(self.run.uid)
        expected_output_path = stage_dir + '/' + 'query.pbf'
        osmtopbf.convert.return_value = expected_output_path
        saved_export_task = ExportTask.objects.create(run=self.run, status='PENDING', name=task.name)
        result = task.run(run_uid=str(self.run.uid), stage_dir=stage_dir)
        osmtopbf.convert.assert_called_once()
        self.assertEquals(expected_output_path, result['result'])
        # test tasks update_task_state method
        run_task = ExportTask.objects.get(celery_uid=celery_uid)
        self.assertIsNotNone(run_task)
        self.assertEquals('RUNNING', run_task.status)
    
    @patch('celery.app.task.Task.request')
    @patch('utils.osmparse.OSMParser')
    def test_run_osmprepschema_task(self, mock_parser, mock_request):
        task = OSMPrepSchemaTask()
        celery_uid = str(uuid.uuid4())
        type(mock_request).id = PropertyMock(return_value=celery_uid)
        prep_schema = mock_parser.return_value
        stage_dir = settings.EXPORT_STAGING_ROOT  + str(self.run.uid) + '/'
        expected_output_path = stage_dir + 'query.sqlite'
        prep_schema.instancemethod.return_value = expected_output_path
        saved_export_task = ExportTask.objects.create(run=self.run, status='PENDING', name=task.name)
        result = task.run(run_uid=str(self.run.uid), stage_dir=stage_dir)
        prep_schema.instancemethod.assert_called_once()
        self.assertEquals(expected_output_path, result['result'])
        # test tasks update_task_state method
        run_task = ExportTask.objects.get(celery_uid=celery_uid)
        self.assertIsNotNone(run_task)
        self.assertEquals('RUNNING', run_task.status)
        
    
    @patch('celery.app.task.Task.request')
    @patch('utils.shp.SQliteToShp')
    def test_run_shp_export_task(self, mock, mock_request):
        task = ShpExportTask()
        celery_uid = str(uuid.uuid4())
        type(mock_request).id = PropertyMock(return_value=celery_uid)
        sqlite_to_shp = mock.return_value
        sqlite_to_shp.convert.return_value = '/path/to/shapefile.shp'
        stage_dir = settings.EXPORT_STAGING_ROOT  + str(self.run.uid)
        saved_export_task = ExportTask.objects.create(run=self.run, status='PENDING', name=task.name)
        result = task.run(run_uid=str(self.run.uid), stage_dir=stage_dir)
        sqlite_to_shp.convert.assert_called_once()
        self.assertEquals('/path/to/shapefile.shp', result['result'])
        # test tasks update_task_state method
        run_task = ExportTask.objects.get(celery_uid=celery_uid)
        self.assertIsNotNone(run_task)
        self.assertEquals('RUNNING', run_task.status)
    
    @patch('shutil.rmtree')
    @patch('shutil.move')
    @patch('celery.app.task.Task.request')
    @patch('utils.osmand.OSMToOBF')
    def test_run_obf_export_task(self, mock_obf, mock_request,
                                 mock_move, mock_rmtree):
        task = ObfExportTask()
        celery_uid = str(uuid.uuid4())
        type(mock_request).id = PropertyMock(return_value=celery_uid)
        osm_to_obf = mock_obf.return_value
        shutil_move = mock_move.return_value
        shutil_rmtree = mock_rmtree.return_value
        expected_output_path = '/home/ubuntu/export_staging/' + str(self.run.uid) + '/query.obf'
        osm_to_obf.convert.return_value = expected_output_path
        stage_dir = settings.EXPORT_STAGING_ROOT  + str(self.run.uid) + '/'
        saved_export_task = ExportTask.objects.create(run=self.run, status='PENDING', name=task.name)
        result = task.run(run_uid=str(self.run.uid), stage_dir=stage_dir)
        osm_to_obf.convert.assert_called_once()
        shutil_move.assert_called_once()
        shutil_rmtree.assert_called_once()
        self.assertEquals(expected_output_path, result['result'])
        # test tasks update_task_state method
        run_task = ExportTask.objects.get(celery_uid=celery_uid)
        self.assertIsNotNone(run_task)
        self.assertEquals('RUNNING', run_task.status)
        
    @patch('shutil.rmtree')
    @patch('shutil.move')
    @patch('celery.app.task.Task.request')
    @patch('utils.garmin.OSMToIMG')
    def test_run_garmin_export_task(self, mock_obf, mock_request,
                                    mock_move, mock_rmtree):
        task = GarminExportTask()
        celery_uid = str(uuid.uuid4())
        type(mock_request).id = PropertyMock(return_value=celery_uid)
        osm_to_img = mock_obf.return_value
        shutil_move = mock_move.return_value
        shutil_rmtree = mock_rmtree.return_value
        expected_output_path = '/home/ubuntu/export_staging/' + str(self.run.uid) + '/garmin.zip'
        osm_to_img.run_mkgmap.return_value = expected_output_path
        stage_dir = settings.EXPORT_STAGING_ROOT  + str(self.run.uid) + '/'
        saved_export_task = ExportTask.objects.create(run=self.run, status='PENDING', name=task.name)
        result = task.run(run_uid=str(self.run.uid), stage_dir=stage_dir)
        osm_to_img.run_mkgmap.assert_called_once()
        shutil_move.assert_called_once()
        shutil_rmtree.assert_called_once()
        self.assertEquals(expected_output_path, result['result'])
        # test tasks update_task_state method
        run_task = ExportTask.objects.get(celery_uid=celery_uid)
        self.assertIsNotNone(run_task)
        self.assertEquals('RUNNING', run_task.status)

    @patch('celery.app.task.Task.request')
    @patch('utils.kml.SQliteToKml')
    def test_run_kml_export_task(self, mock_kml, mock_request):
        task = KmlExportTask()
        celery_uid = str(uuid.uuid4())
        type(mock_request).id = PropertyMock(return_value=celery_uid)
        sqlite_to_kml = mock_kml.return_value
        expected_output_path = '/home/ubuntu/export_staging/' + str(self.run.uid) + '/query.kmz'
        sqlite_to_kml.convert.return_value = expected_output_path
        stage_dir = settings.EXPORT_STAGING_ROOT  + str(self.run.uid) + '/'
        saved_export_task = ExportTask.objects.create(run=self.run, status='PENDING', name=task.name)
        result = task.run(run_uid=str(self.run.uid), stage_dir=stage_dir)
        sqlite_to_kml.convert.assert_called_once()
        self.assertEquals(expected_output_path, result['result'])
        # test the tasks update_task_state method
        run_task = ExportTask.objects.get(celery_uid=celery_uid)
        self.assertIsNotNone(run_task)
        self.assertEquals('RUNNING', run_task.status)

    def test_task_on_success(self,):
        shp_export_task = ShpExportTask()
        celery_uid = str(uuid.uuid4())
        # assume task is running
        running_task = ExportTask.objects.create(
            run=self.run,
            celery_uid=celery_uid,
            status='RUNNING',
            name=shp_export_task.name
        )
        shp_export_task = ShpExportTask()
        output_url = 'http://testserver/some/output/file.shp'
        shp_export_task.on_success(retval={'result': output_url}, task_id=celery_uid,
                                   args={}, kwargs={'run_uid': str(self.run.uid)})
        task = ExportTask.objects.get(celery_uid=celery_uid)
        self.assertIsNotNone(task)
        result = task.result
        self.assertIsNotNone(result)
        self.assertEqual(task, result.task)
        self.assertEquals('SUCCESS', task.status)
        self.assertEquals('Shapefile Export', task.name)
        # pull out the result and test
        result = ExportTaskResult.objects.get(task__celery_uid=celery_uid)
        self.assertIsNotNone(result)
        self.assertEquals(output_url, result.output_url)
    
    def test_task_on_failure(self,):
        shp_export_task = ShpExportTask()
        celery_uid = str(uuid.uuid4())
        # assume task is running
        running_task = ExportTask.objects.create(
            run=self.run,
            celery_uid=celery_uid,
            status='RUNNING',
            name=shp_export_task.name
        )
        exc = None
        exc_info = None
        try:
            raise ValueError('some unexpected error')
        except ValueError as e:
            exc = e
            exc_info = sys.exc_info()
        einfo = ExceptionInfo(exc_info=exc_info)
        shp_export_task.on_failure(exc, task_id=celery_uid, einfo=einfo,
                                   args={}, kwargs={'run_uid': str(self.run.uid)})
        task = ExportTask.objects.get(celery_uid=celery_uid)
        self.assertIsNotNone(task)
        exception = task.exceptions.all()[0]
        exc_info = cPickle.loads(str(exception.exception)).exc_info
        error_type, msg, tb = exc_info[0], exc_info[1], exc_info[2]
        self.assertEquals(error_type, ValueError)
        self.assertEquals('some unexpected error', str(msg))
        #traceback.print_exception(error_type, msg, tb)
        
        
        