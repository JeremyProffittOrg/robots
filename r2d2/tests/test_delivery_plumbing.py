"""Revision-aware delivery plumbing.

Revision C keeps its published paths, URLs and bytes. Revision D gets its own
paths, URLs and labels, and package.py refuses revision D until a passing
revision D verification exists.
"""
import ast
import datetime
import hashlib
import json
import re
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import yaml

R2=Path(__file__).resolve().parents[1]
REPO=R2.parent
sys.path.insert(0,str(R2/'scripts'))
import package  # noqa: E402

CDN='https://d1lftyhk9r30k1.cloudfront.net'
C_PUBLISHED={'motion.mp4':'d1fc448eada115beff02fba91838d8b1a777718063af1071bd711ca7b9563844',
             'design.pdf':'7d0aea209b468f9a6dd2193c18e49f7b062b0f3e240a1ea6fe520940c5247c0f'}
PATH_KEYS=['delivery','pdf','pdf_check','pdf_render','drawings','archive','video_preview']


def sha(data):return hashlib.sha256(data).hexdigest()


class RevisionCUnchanged(unittest.TestCase):
    def test_default_revision_is_c(self):
        self.assertEqual(package.DEFAULT_REVISION,'C')
        self.assertEqual(package.cli_revision([]),'C')
        parser=package.add_revision_argument(__import__('argparse').ArgumentParser())
        self.assertEqual(parser.parse_args([]).revision,'C')

    def test_paths_match_the_original_layout(self):
        self.assertEqual(package.delivery_dir('C'),R2/'output/delivery')
        self.assertEqual(package.path('C','pdf'),R2/'output/pdf/r2d2-design-and-assembly.pdf')
        self.assertEqual(package.path('C','pdf_check'),R2/'docs/pdf-check.json')
        self.assertEqual(package.path('C','pdf_render'),R2/'output/pdf/rendered')
        self.assertEqual(package.path('C','drawings'),R2/'output/drawings')
        self.assertEqual(package.path('C','archive'),R2/'output/r2d2-fabrication.zip')
        self.assertEqual(package.path('C','video_preview'),R2/'tmp/reference/video-preview.png')

    def test_urls_and_labels_match_the_published_revision(self):
        self.assertEqual(package.public_url('C','motion.mp4'),CDN+'/r2d2/revision-c/motion.mp4')
        self.assertEqual(package.public_url('C','design.pdf'),CDN+'/r2d2/revision-c/design.pdf')
        self.assertEqual(package.s3_prefix('C'),'r2d2/revision-c')
        self.assertEqual(package.label('C'),'R2-24 revision C')
        self.assertEqual(package.video_title('C'),'R2-24 | revision C')
        self.assertEqual(package.release_date('C'),'September 12, 2026')

    def test_published_files_keep_their_bytes(self):
        delivery=R2/'output/delivery'
        manifest=json.loads((delivery/'manifest.json').read_text())
        self.assertEqual(manifest['revision'],'C')
        self.assertEqual(manifest['files'],C_PUBLISHED)
        for name,expected in C_PUBLISHED.items():
            with self.subTest(name=name):self.assertEqual(sha((delivery/name).read_bytes()),expected)

    def test_revision_c_manual_wording_is_preserved(self):
        c=package.profile('C')
        self.assertIn('Metal fabrication worksheet',c['manual_required_text'])
        self.assertEqual(c['fabrication_title'],'Metal fabrication worksheet')
        self.assertTrue(c['metal_profiles'] and c['posture_plot'])
        self.assertEqual(c['video_scenes'][3][1].format(designs=10,pieces=14),'10 STL designs / 14 printed pieces. Metal frame stays assembled.')


class RevisionDSeparate(unittest.TestCase):
    def test_paths_are_revision_d(self):
        self.assertEqual(package.delivery_dir('D'),R2/'output/delivery/revision-d')
        self.assertEqual(package.delivery_dir('d'),R2/'output/delivery/revision-d')
        self.assertEqual(package.path('D','pdf'),R2/'output/pdf/revision-d/r2d2-design-and-assembly.pdf')
        self.assertEqual(package.path('D','pdf_check'),R2/'docs/pdf-check-revision-d.json')
        self.assertEqual(package.path('D','drawings'),R2/'output/drawings/revision-d')
        self.assertEqual(package.path('D','archive'),R2/'output/r2d2-fabrication-revision-d.zip')

    def test_urls_and_labels_are_revision_d(self):
        self.assertEqual(package.public_url('D','motion.mp4'),CDN+'/r2d2/revision-d/motion.mp4')
        self.assertEqual(package.public_url('D','design.pdf'),CDN+'/r2d2/revision-d/design.pdf')
        self.assertEqual(package.s3_prefix('D'),'r2d2/revision-d')
        self.assertEqual(package.label('D'),'R2-24 revision D')
        self.assertEqual(package.video_title('D'),'R2-24 | revision D')
        self.assertEqual(package.release_date('D',datetime.date(2026,10,1)),'October 1, 2026')
        self.assertEqual(package.cli_revision(['verify.py','--revision','d']),'D')
        self.assertEqual(package.cli_revision(['verify.py','--revision=D']),'D')

    def test_revision_d_is_a_release_not_development(self):
        d=package.profile('D')
        self.assertNotIn('development',' '.join(str(package.path('D',k)) for k in PATH_KEYS))
        self.assertFalse(d['metal_profiles'])
        self.assertNotIn('Metal',d['subtitle']+d['fabrication_title']+d['mechanism_footer'])
        self.assertNotIn('Metal fabrication worksheet',d['manual_required_text'])

    def test_no_revision_d_path_overwrites_revision_c(self):
        c_paths={package.path('C',k) for k in PATH_KEYS}|{package.delivery_dir('C')/n for n in ['manifest.json','video.json',*package.DELIVERY_FILES]}
        d_paths={package.path('D',k) for k in PATH_KEYS}|{package.delivery_dir('D')/n for n in ['manifest.json','video.json',*package.DELIVERY_FILES]}
        self.assertFalse(c_paths&d_paths)
        self.assertEqual(set(package.REVISIONS['C']),set(package.REVISIONS['D']))

    def test_unknown_revisions_and_files_are_rejected(self):
        for bad in ['B','D-development','',None]:
            with self.subTest(bad=bad),self.assertRaises(ValueError):package.revision_key(bad)
        with self.assertRaises(ValueError):package.public_url('D','manifest.json')
        with self.assertRaises(ValueError):package.cli_revision(['--revision'])


class Fixture:
    """A miniature r2d2 tree with a published revision C and a candidate release."""
    def __init__(self,root,revision,all_pass=True,verified_revision=None,video_revision=None,drawing_revision=None,
                 source_hashes=True,catalog_extra=0):
        self.root=root;key=package.revision_key(revision)
        def write(rel,data):
            f=root/rel;f.parent.mkdir(parents=True,exist_ok=True)
            f.write_bytes(data if isinstance(data,bytes) else data.encode());return f
        write('cad/validation.json',json.dumps({'rows':[{'part':'body','quantity':2},{'part':'leg','quantity':1}]}))
        for name in ['body','leg']:write(f'stl/{name}.stl',b'solid '+name.encode())
        write('stl/development/study.stl',b'solid study')
        mp3s=['audio/a.mp3','audio/b.mp3']
        for m in mp3s:write(m,b'ID3'+m.encode())
        write('audio/catalog.csv','path,sha256\n'+''.join(f'{m},x\n' for m in mp3s+[f'audio/missing{i}.mp3' for i in range(catalog_extra)]))
        for rel in ['bom/b.csv','electronics/w.csv','firmware/src/main.cpp','scripts/s.py','docs/assembly.md','README.md','.gitignore','.gitattributes']:
            write(rel,'fixture '+rel)
        # Published revision C files that must never change.
        self.c_files={}
        for name,data in [('motion.mp4',b'C video'),('design.pdf',b'C pdf'),('video.json',b'{}')]:
            self.c_files[name]=sha(write(f'output/delivery/{name}',data).read_bytes())
        self.c_files['manifest.json']=sha(write('output/delivery/manifest.json',json.dumps({'revision':'C'})).read_bytes())
        p=package.profile(key);delivery=Path(p['delivery'])
        pdf=write(p['pdf'],b'%PDF '+key.encode())
        write(p['pdf_check'],json.dumps({'revision':key,'pages':3,'all_pages_rendered':True,'sha256':sha(pdf.read_bytes())}))
        video=write(delivery/'motion.mp4',b'video '+key.encode()) if key!='C' else root/'output/delivery/motion.mp4'
        report={'sha256':sha(video.read_bytes())}
        if video_revision!='legacy':report['revision']=video_revision or key
        write(delivery/'video.json',json.dumps(report))
        if key=='C':self.c_files['video.json']=sha((root/'output/delivery/video.json').read_bytes())
        drawings=Path(p['drawings'])
        for f in ['01-robot.png','components/01-body.png']:write(drawings/f,b'PNG '+f.encode())
        write(drawings/'index.json',json.dumps({'revision':drawing_revision or key,'pngs':[{'file':'01-robot.png'},{'file':'components/01-body.png'}]}))
        if key=='C':write('output/drawings/revision-d/99-other.png',b'not revision C')
        verification={'revision':verified_revision or key,'physical_validation':False}
        if all_pass is not None:verification['all_pass']=all_pass
        if source_hashes:verification['source_sha256']={'stl/body.stl':sha((root/'stl/body.stl').read_bytes())}
        write('docs/verification.json',json.dumps(verification))

    def c_unchanged(self):
        return all(sha((self.root/'output/delivery'/n).read_bytes())==h for n,h in self.c_files.items())


class PackageGate(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='r2-delivery-');self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()

    def assertNothingReleased(self,fixture,revision='D'):
        self.assertFalse((package.delivery_dir(revision,self.root)/'manifest.json').exists())
        self.assertFalse((package.delivery_dir(revision,self.root)/'design.pdf').exists())
        self.assertFalse(package.path(revision,'archive',self.root).exists())
        self.assertTrue(fixture.c_unchanged())

    def test_refuses_revision_d_without_all_pass_revision_d_verification(self):
        cases={'failed D verification':dict(all_pass=False),
               'missing all_pass':dict(all_pass=None),
               'truthy non-boolean all_pass':dict(all_pass='yes'),
               'passing revision C verification':dict(verified_revision='C'),
               'D development status':dict(verified_revision='D-development'),
               'no source hashes':dict(source_hashes=False)}
        for name,options in cases.items():
            with self.subTest(name),tempfile.TemporaryDirectory(prefix='r2-gate-') as folder:
                self.root=Path(folder);fixture=Fixture(self.root,'D',**options)
                with self.assertRaises(package.ReleaseNotReady):package.package('D',self.root)
                self.assertNothingReleased(fixture)

    def test_refuses_revision_d_built_from_revision_c_artifacts(self):
        for name,options in {'unlabelled video':dict(video_revision='legacy'),'revision C video':dict(video_revision='C'),
                             'revision C drawings':dict(drawing_revision='C')}.items():
            with self.subTest(name),tempfile.TemporaryDirectory(prefix='r2-gate-') as folder:
                self.root=Path(folder);fixture=Fixture(self.root,'D',**options)
                with self.assertRaises(package.ReleaseNotReady):package.package('D',self.root)
                self.assertNothingReleased(fixture)

    def test_counts_come_from_manifests(self):
        fixture=Fixture(self.root,'D',catalog_extra=1)
        with self.assertRaisesRegex(package.ReleaseNotReady,'MP3'):package.package('D',self.root)
        self.assertNothingReleased(fixture)

    def test_passing_revision_d_writes_only_revision_d_paths(self):
        fixture=Fixture(self.root,'D')
        manifest_path=package.package('D',self.root)
        self.assertEqual(manifest_path,self.root/'output/delivery/revision-d/manifest.json')
        manifest=json.loads(manifest_path.read_text())
        self.assertEqual(manifest['revision'],'D')
        self.assertEqual(manifest['files'],{'motion.mp4':sha(b'video D'),'design.pdf':sha(b'%PDF D')})
        self.assertTrue(fixture.c_unchanged())
        self.assertFalse((self.root/'output/r2d2-fabrication.zip').exists())
        with zipfile.ZipFile(self.root/'output/r2d2-fabrication-revision-d.zip') as z:names=set(z.namelist())
        self.assertIn('r2d2/output/delivery/revision-d/motion.mp4',names)
        self.assertIn('r2d2/output/pdf/revision-d/r2d2-design-and-assembly.pdf',names)
        self.assertIn('r2d2/output/drawings/revision-d/components/01-body.png',names)
        self.assertNotIn('r2d2/output/delivery/motion.mp4',names)

    def test_revision_c_packaging_keeps_root_paths(self):
        fixture=Fixture(self.root,'C',video_revision='legacy')
        manifest_path=package.package('C',self.root)
        self.assertEqual(manifest_path,self.root/'output/delivery/manifest.json')
        manifest=json.loads(manifest_path.read_text())
        self.assertEqual(list(manifest),['revision','files','pdf_pages','video_simulation','physical_tested'])
        self.assertEqual(manifest['revision'],'C')
        self.assertEqual(manifest['files']['motion.mp4'],fixture.c_files['motion.mp4'])
        with zipfile.ZipFile(self.root/'output/r2d2-fabrication.zip') as z:names=set(z.namelist())
        self.assertIn('r2d2/output/delivery/motion.mp4',names)
        self.assertIn('r2d2/output/pdf/r2d2-design-and-assembly.pdf',names)
        self.assertIn('r2d2/output/drawings/components/01-body.png',names)
        self.assertFalse(any('revision-d' in n for n in names))
        self.assertFalse((self.root/'output/delivery/revision-d/manifest.json').exists())


class PublicationWorkflowAndInfra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template=(R2/'infra/deliverables.yaml').read_text()
        cls.workflow_text=(REPO/'.github/workflows/publish-r2d2.yml').read_text()
        cls.workflow=yaml.safe_load(cls.workflow_text)

    def test_bucket_policy_allows_exactly_revision_c_and_d_deliverables(self):
        resources=re.findall(r"\$\{Artifacts\.Arn\}/(r2d2/[^']+)'",self.template)
        self.assertEqual(sorted(resources),sorted(f'{package.s3_prefix(r)}/{n}' for r in 'CD' for n in package.DELIVERY_FILES))
        self.assertIn("BaseUrl:\n    Value: !Sub 'https://${Delivery.DomainName}/r2d2/revision-c'",self.template)
        self.assertIn("DeliveryOrigin:\n    Value: !Sub 'https://${Delivery.DomainName}'",self.template)

    def test_no_fixed_cost_monitoring_or_unbounded_logs(self):
        self.assertNotRegex(self.template,r'AWS::CloudWatch::(Alarm|Dashboard)')
        for group in re.findall(r'Type: AWS::Logs::LogGroup(?:\n {6,}.*)*',self.template):
            self.assertIn('RetentionInDays: 7',group)

    def test_workflow_keeps_oidc_permissions_and_concurrency(self):
        self.assertEqual(self.workflow['permissions'],{'contents':'read','id-token':'write'})
        self.assertEqual(self.workflow['concurrency'],{'group':'r2d2-publication','cancel-in-progress':False})
        trigger=self.workflow[True]['push']
        self.assertEqual(trigger['branches'],['main'])
        self.assertIn('r2d2/output/delivery/**',trigger['paths'])
        steps=self.workflow['jobs']['publish']['steps']
        creds=[s for s in steps if str(s.get('uses','')).startswith('aws-actions/configure-aws-credentials')]
        self.assertEqual(creds[0]['with']['role-to-assume'],'${{ vars.AWS_DEPLOY_ROLE_ARN }}')
        self.assertNotRegex(self.workflow_text,r'(?i)aws-access-key-id|aws-secret-access-key|AWS_ACCESS_KEY_ID')

    def test_workflow_publishes_and_verifies_each_revision_directory(self):
        run=next(s['run'] for s in self.workflow['jobs']['publish']['steps'] if s.get('name')=='Upload and verify every packaged revision')
        for required in ['entries=("C r2d2/output/delivery")','for folder in r2d2/output/delivery/revision-*/; do',
                         'if [[ ! -f "$dir/manifest.json" ]]; then','prefix="r2d2/revision-${revision,,}"',
                         "assert manifest['revision']==revision",'"s3://$bucket/$prefix/$name"',
                         '--paths "/$prefix/motion.mp4" "/$prefix/design.pdf"','cmp "$dir/$name" "$download"',
                         '(cd "$dir" && sha256sum "$name") >> "$GITHUB_STEP_SUMMARY"','test "$code" = 206',
                         "grep -qi '^content-type: video/mp4'","grep -qi '^content-type: application/pdf'",
                         '"https://$bucket.s3.us-east-1.amazonaws.com/$prefix/motion.mp4")" = 403',
                         '"https://$bucket.s3.us-east-1.amazonaws.com/$prefix/design.pdf")" = 403',
                         '"https://$bucket.s3.us-east-1.amazonaws.com/?list-type=2")" = 403',
                         'echo "PASS revision $revision:']:
            with self.subTest(required=required):self.assertIn(required,run)
        # Heredoc terminator must sit at column zero after YAML dedent.
        self.assertIn('\nPY\n',run)


class ScriptsUseSharedRevision(unittest.TestCase):
    SCRIPTS=['package.py','build_manual.py','render_video.py','draw_robot.py']

    def test_scripts_parse(self):
        for name in self.SCRIPTS:
            with self.subTest(name=name):ast.parse((R2/'scripts'/name).read_text(encoding='utf-8'))

    def test_release_scripts_take_revision_from_package(self):
        for name in self.SCRIPTS[1:]:
            source=(R2/'scripts'/name).read_text(encoding='utf-8')
            with self.subTest(name=name):
                imports=[n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.ImportFrom) and n.module=='package']
                self.assertTrue(imports)
                self.assertIn('add_revision_argument',source)
                for literal in ['revision-c','R2-24 revision C','R2-24 | revision C',"'REVISION C'","=='C'","'revision':'C'"]:
                    self.assertNotIn(literal,source)


if __name__=='__main__':
    unittest.main()
