"""External-source amendments retain original science and refuse stale inputs."""
import copy
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import catalogue
import record_external_reports
from export_batch import load, seal, sha, write


def fixture(base):
    root = base / 'repo'; root.mkdir()
    shutil.copytree(ROOT / 'schemas', root / 'schemas')
    folder = root / 'candidates/tic-243500407-s01'
    shutil.copytree(ROOT / 'candidates/tic-243500407-s01', folder)
    original = load(folder / 'candidate.json')
    original['novelty']['status'] = 'no_match_in_checked_sources'
    original['novelty']['evidence'] = [x for x in original['novelty']['evidence']
                                     if x != 'evidence/external-report.json']
    original['evidence'] = [x for x in original['evidence']
                           if not x.startswith('evidence/external-')]
    (folder / 'evidence/external-report.json').unlink(missing_ok=True)
    shutil.rmtree(folder / 'evidence/external-source', ignore_errors=True)
    write(folder / 'candidate.json', original)
    old = load(folder / 'evidence-manifest.json')
    seal(folder, {f['path']:f['source_sha256'] for f in old['files'] if 'source_sha256' in f})
    source = base / 'source'; source.mkdir()
    p = original['signal']['period_d']['value']
    review = {'schema_version':'1.0', 'candidate_id':original['id'], 'tic':original['target']['tic'],
        'source_candidate_sha256':sha(folder / 'candidate.json'),
        'photometry_sha256':sha(folder / 'evidence/photometry.json'),
        'review_outcome':'matching_external_aperture_report', 'nominal_centres_agree':True,
        'event_comparison':{'status':'unresolved','distinct_events':3,
                            'maximum_abs_residual_duration':0.1},
        'source_record':{'tic':original['target']['tic'], 'period_d':p,
                        'source_file':'results_public/candidates_allsky.csv', 'raw_row_number':2,
                        'reported_disposition':{'tier':'likely nearby FP'},'raw':{'NFPP':'0.8'}},
        'source_commit':'a'*40, 'source_url':'https://github.com/eumemic/exoplanets',
        'reviewed_utc':'2026-10-11T12:30:00Z', 'limits':['Host/clock/probability uncalibrated'],
        'supplementary_files':[], 'supplementary_status':'no_per_signal_files_in_snapshot',
        'input_scientific_blocks':{k:copy.deepcopy(original[k]) for k in
            (*record_external_reports.SCIENCE,'publication')}}
    write(source / 'case.json', review)
    path = source / 'review.json'
    write(path, {'source_run':'fixture','cases':[{'candidate_id':original['id'],
                                                'file':'case.json','sha256':sha(source/'case.json')}]})
    write(source / 'manifest.json', {'command':'vet-external-report-review', 'run_id':'fixture',
        'ok':True,'git':{'commit':'b'*40},
        'outputs':{'review.json':sha(path),'case.json':sha(source/'case.json')}})
    return root,folder,path,original


class ExternalReportAmendments(unittest.TestCase):
    def test_source_context_changes_novelty_without_physical_promotion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,folder,path,original=fixture(Path(tmp))
            self.assertEqual(record_external_reports.record_reports(root,'test',path)['updated_records'],1)
            updated=load(folder/'candidate.json')
            self.assertEqual(updated['novelty']['status'],'previously_reported')
            for key in (*record_external_reports.SCIENCE,'publication'):
                self.assertEqual(updated[key],original[key])
            context=load(folder/'evidence/external-report.json')
            self.assertEqual(context['previous_novelty'],original['novelty'])
            self.assertEqual(context['source_record']['raw']['NFPP'],'0.8')
            self.assertEqual(record_external_reports.record_reports(root,'test',path)['updated_records'],0)
            oldroot=catalogue.ROOT
            try:
                catalogue.ROOT=root
                catalogue.validate(updated,folder)
            finally:
                catalogue.ROOT=oldroot

    def test_stale_science_and_corrupt_source_refused_before_any_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,folder,path,original=fixture(Path(tmp))
            candidate=load(folder/'candidate.json');candidate['signal']['depth_ppm']['value']+=1
            write(folder/'candidate.json',candidate)
            old=load(folder/'evidence-manifest.json')
            sources={f['path']:f['source_sha256'] for f in old['files'] if 'source_sha256' in f}
            seal(folder,sources)
            with self.assertRaisesRegex(ValueError,'Scientific dossier'):
                record_external_reports.record_reports(root,'test',path)
            self.assertFalse((folder/'evidence/external-report.json').exists())
            write(folder/'candidate.json',original)
            seal(folder,sources)
            (path.parent/'case.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'bytes changed'):
                record_external_reports.record_reports(root,'test',path)
            self.assertEqual(load(folder/'candidate.json'),original)

    def test_private_path_and_calibrated_claim_refused(self):
        for change in ('private','timing'):
            with tempfile.TemporaryDirectory() as tmp:
                root,folder,path,original=fixture(Path(tmp))
                review=load(path.parent/'case.json')
                if change=='private':review['source_record']['raw']['path']='/Users/person/private'
                else:review['event_comparison']['status']='diagnostic_event_agreement'
                write(path.parent/'case.json',review)
                report=load(path);report['cases'][0]['sha256']=sha(path.parent/'case.json');write(path,report)
                manifest=load(path.parent/'manifest.json')
                manifest['outputs']={n:sha(path.parent/n) for n in manifest['outputs']}
                write(path.parent/'manifest.json',manifest)
                with self.assertRaises(ValueError):
                    record_external_reports.record_reports(root,'test',path)
                self.assertEqual(load(folder/'candidate.json'),original)


if __name__=='__main__':unittest.main()
