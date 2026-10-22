"""Non-destructive initialization. Detect host + WSL + pseudo and utility inventory; no simulation jobs."""
import argparse, json, os, platform, shutil, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'utils'))
from core import detect,scan_pp,write_json,windows_to_wsl

def probe_wsl():
    result={'available':False,'distributions':[],'active':False,'linux_probe':None}
    exe=shutil.which('wsl.exe')
    if not exe: return result
    result['available']=True
    try:
        p=subprocess.run([exe,'--list','--quiet'],capture_output=True,timeout=8)
        result['distributions']=[x.strip().replace('\x00','') for x in p.stdout.decode('utf-16-le',errors='ignore').splitlines() if x.strip().replace('\x00','')]
    except Exception as e: result['probe_error']=str(e)
    return result

def main():
    p=argparse.ArgumentParser(description='Initialize simulation agent. Never launches DFT/AIMD.')
    p.add_argument('--pseudo-root',action='append',default=[],help='Actual pseudopotential directory accessible in current execution environment (repeatable)')
    p.add_argument('--workspace',default=None,help='Simulation workspace for prospective jobs; not created by initializer')
    p.add_argument('--no-pp-scan',action='store_true')
    p.add_argument('--output-dir',default=str(ROOT/'config'/'detected'))
    args=p.parse_args(); out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    results=detect(); results['wsl_bridge']=probe_wsl() if os.name=='nt' else {'active':results['host']['is_wsl'],'available':False,'note':'Windows bridge is only probed when launched on Windows'}
    results['workspace']={'candidate':args.workspace,'verified':bool(args.workspace and Path(args.workspace).is_dir())}
    results['utils']={}
    for f in sorted((ROOT/'utils').glob('*.py')):
        if f.name in ('__init__.py','core.py'): continue
        results['utils'][f.stem]={'path':str(f.resolve()),'exists':True,'interface':'--input JSON_PATH --output JSON_PATH --help','status':'implemented' if f.stem in IMPLEMENTED else 'not_implemented'}
    roots=list(args.pseudo_root)
    inventory_hint=os.environ.get('SIM_AGENT_PSEUDO_ROOT','')
    results['pseudopotentials']={'candidate_from_inventory':inventory_hint,'candidate_verified':bool(inventory_hint and Path(inventory_hint).is_dir()),'scans':[]}
    if inventory_hint and Path(inventory_hint).is_dir() and not roots: roots.append(inventory_hint)
    if results['host']['is_wsl']:
        candidate=windows_to_wsl(inventory_hint)
        if candidate and Path(candidate).is_dir() and not roots: roots.append(candidate)
    for root in roots:
        try:
            if args.no_pp_scan: results['pseudopotentials']['scans'].append({'root':root,'exists':Path(root).is_dir(),'scanned':False})
            else:
                catalog=scan_pp(root); catalog_path=out/f'pseudopotentials_{len(results["pseudopotentials"]["scans"])+1}.json'; write_json(catalog_path,catalog)
                results['pseudopotentials']['scans'].append({'root':root,'exists':True,'scanned':True,'count':catalog['count'],'manifest':str(catalog_path)})
        except Exception as e: results['pseudopotentials']['scans'].append({'root':root,'exists':False,'error':str(e)})
    results['limits']={'max_jobs_approved':None,'max_concurrent_jobs_approved':None,'max_corehours_approved':None,'max_walltime_hours_approved':None,'allow_unattended':False,'allow_external_downloads':False}
    results['execution_ready']=False
    results['missing_for_execution']=['User-approved resource limits','Executable verified on selected execution target','Validated calculation-specific inputs and pseudopotentials','Explicit permission to launch jobs']
    results['warning']='Hardware detection is not a performance benchmark; CPU/RAM availability changes. No code was installed and no jobs were run.'
    write_json(out/'detected_environment.json',results)
    print('Initialization completed:',out/'detected_environment.json')
    print('Detected executables:',', '.join(k for k,v in results['executables'].items() if v['verified']) or 'none')
    print('Simulation execution remains DISABLED pending approvals and input checks.')
IMPLEMENTED={'bandgap_analyzer','orbital_analyzer','bond_scan_generator','conformer_ranker','trajectory_analyzer','checkpoint_manager','xtb_crest_runner','conformer_generator','adsorption_builder','surface_builder','reaction_path_builder','structure_parser','structure_validator','pp_catalog_auditor','qe_input_generator','orca_input_generator','qe_output_parser','orca_output_parser','xtb_crest_parser','energy_calculator','statistics_aggregator','resource_estimator','job_executor','convergence_validator','simulation_monitor','simulation_reporter'}
if __name__=='__main__': main()
