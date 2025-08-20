import unittest
import tempfile
from pathlib import Path
import json
import importlib.util
import subprocess
from unittest.mock import patch


def load_editor_module():
    base_dir = Path(__file__).resolve().parents[1]
    module_path = base_dir / 'simple-yaml-editor.py'
    spec = importlib.util.spec_from_file_location('simple_yaml_editor_under_test', str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod


class SimpleYamlEditorE2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_editor_module()

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmpdir.name)
        # default YAML file for tests
        self.test_file = self.tmp / 'test.yaml'
        self.test_file.write_text('a: 1\n', encoding='utf-8')
        # configure module globals
        self.mod.current_file = str(self.test_file)
        self.mod.backup_dir = self.tmp / '.blocked'
        self.mod.backup_dir.mkdir(exist_ok=True)
        self.client = self.mod.app.test_client()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_index_loads(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'YAML Editor', resp.data)

    def test_save_updates_file(self):
        payload = {'content': 'foo: 2\n', 'auto_save': False}
        resp = self.client.post('/save', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(self.test_file.read_text(encoding='utf-8'), 'foo: 2\n')

    def test_backups_list_and_restore(self):
        # create a backup of initial content
        self.mod.create_backup(str(self.test_file))
        # modify file
        self.test_file.write_text('b: 3\n', encoding='utf-8')
        # list backups
        resp = self.client.get('/list-backups')
        self.assertEqual(resp.status_code, 200)
        backups = resp.get_json().get('backups', [])
        self.assertGreater(len(backups), 0)
        backup_name = backups[0]
        # restore
        resp = self.client.post('/restore-backup', data=json.dumps({'backup': backup_name}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json()['success'])
        # file content should be restored to original
        self.assertEqual(self.test_file.read_text(encoding='utf-8'), 'a: 1\n')

    def test_test_docker_compose_static_ok(self):
        compose_file = self.tmp / 'docker-compose.test.yaml'
        compose_file.write_text('version: "3.8"\nservices:\n  a:\n    image: busybox\n', encoding='utf-8')
        self.mod.current_file = str(compose_file)

        def fake_run(args, capture_output=True, text=True):
            # Simulate successful `docker compose config` (or docker-compose)
            if (args and args[0] == 'docker' and len(args) > 1 and args[1] == 'compose') or (args and args[0] == 'docker-compose'):
                return subprocess.CompletedProcess(args, 0, stdout='OK', stderr='')
            return subprocess.CompletedProcess(args, 1, stdout='', stderr='unexpected command')

        with patch('subprocess.run', side_effect=fake_run):
            resp = self.client.post('/test-docker', data=json.dumps({'static_only': True}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('OK', data.get('output', ''))

    def test_test_dockerfile_static_only_ok(self):
        dockerfile = self.tmp / 'Dockerfile'
        dockerfile.write_text('FROM alpine:3.18\n', encoding='utf-8')
        self.mod.current_file = str(dockerfile)

        def fake_run(args, capture_output=True, text=True):
            # Simulate successful `docker image inspect alpine:3.18`
            if args[:3] == ['docker', 'image', 'inspect']:
                return subprocess.CompletedProcess(args, 0, stdout='[]', stderr='')
            # Should not reach build because static_only
            return subprocess.CompletedProcess(args, 1, stdout='', stderr='should not build in static mode')

        with patch('subprocess.run', side_effect=fake_run):
            resp = self.client.post('/test-docker', data=json.dumps({'static_only': True}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('Static check OK', data.get('output', ''))
        self.assertIn('No build executed', data.get('output', ''))

    def test_test_dockerfile_static_only_missing_image(self):
        dockerfile = self.tmp / 'Dockerfile'
        dockerfile.write_text('FROM alpine:3.18\n', encoding='utf-8')
        self.mod.current_file = str(dockerfile)

        def fake_run(args, capture_output=True, text=True):
            # Simulate missing image for `docker image inspect`
            if args[:3] == ['docker', 'image', 'inspect']:
                return subprocess.CompletedProcess(args, 1, stdout='', stderr='not found')
            return subprocess.CompletedProcess(args, 1, stdout='', stderr='should not build in static mode')

        with patch('subprocess.run', side_effect=fake_run):
            resp = self.client.post('/test-docker', data=json.dumps({'static_only': True}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertFalse(data['success'])
        self.assertIn('not present locally', data.get('error', ''))


if __name__ == '__main__':
    unittest.main(verbosity=2)
