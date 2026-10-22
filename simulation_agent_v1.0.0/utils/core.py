"""Simulation Agent utilities v1.0.0. Standard-library-first, no automatic heavy jobs."""
from __future__ import annotations
import argparse, json, math, os, re, shutil, subprocess, sys, hashlib, platform, time, statistics
from pathlib import Path
from datetime import datetime, timezone

EV_PER_HARTREE = 27.211386245988
EV_PER_RY = EV_PER_HARTREE / 2

def read_json(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def write_json(p, data):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8'); return str(p)
def utc(): return datetime.now(timezone.utc).isoformat()
def require(d, *keys):
    for k in keys:
        if k not in d: raise ValueError(f'Missing required key: {k}')
def path_info(path):
    if not path: return {'value':None,'verified':False}
    p=Path(path).expanduser()
    return {'value':str(p),'verified':p.exists(),'is_file':p.is_file(),'is_dir':p.is_dir()}
def which(name): return shutil.which(name)
def windows_to_wsl(path, distro=None):
    m=re.match(r'^([A-Za-z]):[\\/](.*)$',path)
    if not m: return None
    return '/mnt/'+m.group(1).lower()+'/'+m.group(2).replace('\\','/')
def memory_gb():
    try:
        import psutil
        vm=psutil.virtual_memory(); return {'total_gb':round(vm.total/2**30,2),'available_gb':round(vm.available/2**30,2),'source':'psutil'}
    except ImportError:
        if sys.platform.startswith('linux'):
            vals={}
            for line in Path('/proc/meminfo').read_text().splitlines():
                x=line.split(':'); vals[x[0]]=int(x[1].strip().split()[0])/2**20
            return {'total_gb':round(vals.get('MemTotal',0),2),'available_gb':round(vals.get('MemAvailable',0),2),'source':'/proc/meminfo'}
    return {'total_gb':None,'available_gb':None,'source':'unavailable'}
def detect():
    disk=shutil.disk_usage(Path.cwd()); is_wsl='microsoft' in platform.release().lower() or bool(os.environ.get('WSL_DISTRO_NAME'))
    r={'schema_version':'1.0.0','captured_utc':utc(),'host':{'os':platform.system(),'release':platform.release(),'architecture':platform.machine(),'hostname':platform.node(),'is_wsl':is_wsl,'wsl_distro':os.environ.get('WSL_DISTRO_NAME'),'cpu_logical':os.cpu_count(),'cpu_physical':None,'memory':memory_gb(),'disk_cwd_free_gb':round(disk.free/2**30,2),'disk_cwd_total_gb':round(disk.total/2**30,2),'gpu':{'status':'unverified','note':'GPU not assumed usable for any simulator'}} ,'executables':{},'python':{'executable':sys.executable,'version':platform.python_version()},'packages':{}}
    try:
        import psutil
        r['host']['cpu_physical']=psutil.cpu_count(logical=False)
    except ImportError: pass
    for name in ['pw.x','ph.x','bands.x','dos.x','projwfc.x','pp.x','orca','xtb','crest','mpirun','mpiexec','srun','wsl.exe','nvidia-smi']:
        loc=which(name); r['executables'][name]={'path':loc,'verified':bool(loc),'version':'not_probed'}
    for pkg in ['numpy','scipy','ase','pymatgen','rdkit','psutil']:
        try:
            from importlib.metadata import version
            r['packages'][pkg]={'available':True,'version':version(pkg)}
        except Exception: r['packages'][pkg]={'available':False,'version':None}
    return r

def scan_pp(root, inventory=None):
    root=Path(root).expanduser(); results=[]
    if not root.is_dir(): raise FileNotFoundError(f'Pseudopotential directory not found: {root}')
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.suffix.lower()!='.upf': continue
        try:
            with p.open('r',encoding='utf-8',errors='replace') as f: sample=f.read(160000)
            upf=re.search(r'<PP_HEADER\b([^>]*)(?:/?>)',sample,re.I|re.S)
            attrs=dict(re.findall(r'([A-Za-z_]+)\s*=\s*["\']([^"\']+)["\']',upf.group(1))) if upf else {}
            if not attrs:
                for key, pattern in [('element',r'Element\s*:\s*([^\s]+)'),('functional',r'Functional\s*:\s*([^\n]+)'),('pseudo_type',r'Pseudopotential type\s*:\s*([^\n]+)'),('z_valence',r'Z valence\s*:\s*([\d.]+)')]:
                    m=re.search(pattern,sample,re.I); attrs[key]=m.group(1).strip() if m else None
            fn=p.name.lower(); folder=str(p.parent).lower(); hints=[]
            if '_risky_removed' in folder: hints.append('QUARANTINED: do not use')
            if 'pbesol' in fn and '/pbe/' in folder.replace('\\','/'): hints.append('FUNCTIONAL_FOLDER_FILENAME_MISMATCH')
            if 'pbe.' in fn and '/lda/' in folder.replace('\\','/'): hints.append('FUNCTIONAL_FOLDER_FILENAME_MISMATCH')
            results.append({'path':str(p.resolve()),'file':p.name,'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'header':attrs,'header_detected':bool(upf or any(v for v in attrs.values())),'warnings':hints,'validated_for_use':False})
        except Exception as e: results.append({'path':str(p),'error':str(e),'validated_for_use':False})
    return {'root':str(root.resolve()),'scanned_utc':utc(),'count':len(results),'files':results,'note':'Catalog only; must verify XC, relativistic type, valence, SSSP cutoffs, convergence before use.'}

def structure_xyz(path):
    txt=Path(path).read_text().splitlines(); n=int(txt[0].strip()); atoms=[]
    if len(txt)<n+2: raise ValueError('Incomplete XYZ')
    for s in txt[2:2+n]:
        a=s.split();
        if len(a)<4: raise ValueError('XYZ atom line malformed')
        atoms.append({'element':a[0],'xyz_angstrom':[float(x) for x in a[1:4]]})
    return {'atoms':atoms,'charge':None,'multiplicity':None,'cell_angstrom':None,'pbc':False,'source':str(path)}
def structure(path):
    p=Path(path)
    if p.suffix.lower()=='.xyz': return structure_xyz(path)
    try:
        from ase.io import read
        a=read(str(p)); return {'atoms':[{'element':el,'xyz_angstrom':[float(v) for v in xyz]} for el,xyz in zip(a.get_chemical_symbols(),a.positions)],'cell_angstrom':[[float(v) for v in row] for row in a.cell],'pbc':bool(any(a.pbc)),'charge':None,'multiplicity':None,'source':str(path)}
    except ImportError: raise RuntimeError('CIF/POSCAR requires ASE: pip install ase')

def validate(s):
    atoms=s.get('atoms',[]); issues=[]
    if not atoms: issues.append('No atoms')
    for i,a in enumerate(atoms):
        if len(a.get('xyz_angstrom',[]))!=3 or not all(math.isfinite(float(x)) for x in a.get('xyz_angstrom',[])): issues.append(f'Invalid coordinates at atom {i}')
    distances=[]
    for i in range(len(atoms)):
        for j in range(i+1,len(atoms)):
            d=math.dist(atoms[i]['xyz_angstrom'],atoms[j]['xyz_angstrom']); distances.append(d)
            if d<0.45: issues.append(f'Atoms {i},{j} unrealistically close ({d:.3f} Å); heuristic only')
    if s.get('pbc') and not s.get('cell_angstrom'): issues.append('Periodic structure lacks cell')
    if s.get('multiplicity') is not None and s['multiplicity']<1: issues.append('Invalid multiplicity')
    return {'valid':not issues,'issues':issues,'atom_count':len(atoms),'min_pair_distance_angstrom':min(distances) if distances else None,'note':'Heuristic geometry check; not a chemical validity certification'}

def qe_input(d):
    require(d,'structure','pseudopotentials','settings'); s=d['structure']; settings=d['settings']; atoms=s['atoms']; pps=d['pseudopotentials']
    if not s.get('pbc'): raise ValueError('QE requires explicit periodic cell; do not fabricate cell for isolated molecules')
    if not s.get('cell_angstrom') or len(s['cell_angstrom'])!=3: raise ValueError('Missing 3x3 cell')
    species=list(dict.fromkeys(a['element'] for a in atoms))
    if any(e not in pps for e in species): raise ValueError('Missing pseudopotential mapping for element')
    for k in ['ecutwfc_ry','ecutrho_ry']:
        if not isinstance(settings.get(k),(float,int)) or settings[k]<=0: raise ValueError(f'{k} must be positive; sourced from PP metadata and tests')
    kpts=settings.get('k_grid')
    if not (isinstance(kpts,list) and len(kpts)==3 and all(isinstance(v,int) and v>0 for v in kpts)): raise ValueError('Provide explicit validated k_grid of three positive integers')
    calc=settings.get('calculation','scf')
    if calc not in ['scf','relax','vc-relax','md','vc-md','nscf','bands']: raise ValueError('Unsupported QE calculation')
    pseudo_dir=d.get('pseudo_dir')
    if not pseudo_dir: raise ValueError('Explicit pseudo_dir required')
    if any('/' in pps[e] or '\\' in pps[e] for e in species): raise ValueError('Use basenames of pseudopotentials in one staged directory; no arbitrary paths')
    for e in species:
        if not (Path(pseudo_dir)/pps[e]).is_file(): raise FileNotFoundError(f'Pseudopotential missing: {pps[e]} in {pseudo_dir}')
    lines=["&CONTROL",f" calculation='{calc}',",f" prefix='{d.get('prefix','sim')}',",f" pseudo_dir='{pseudo_dir}',",f" outdir='{d.get('outdir','./tmp')}',",'/','&SYSTEM',' ibrav=0,',f' nat={len(atoms)},',f' ntyp={len(species)},',f" ecutwfc={settings['ecutwfc_ry']},",f" ecutrho={settings['ecutrho_ry']},"]
    if settings.get('occupations'):
        lines.append(f" occupations='{settings['occupations']}',")
        if settings.get('smearing'): lines.extend([f" smearing='{settings['smearing']}',",f" degauss={settings.get('degauss_ry',0.01)},"])
    if settings.get('nspin')==2: lines.append(' nspin=2,')
    lines.extend(['/','&ELECTRONS',f" conv_thr={settings.get('conv_thr',1e-8)},",f" mixing_beta={settings.get('mixing_beta',0.3)},",'/'])
    if calc in ('relax','vc-relax','md','vc-md'):
        lines.extend(['&IONS',f" ion_dynamics='{settings.get('ion_dynamics','bfgs' if 'relax' in calc else 'verlet')}',",'/'])
    if calc in ('vc-relax','vc-md'): lines.extend(['&CELL'," cell_dynamics='bfgs'," if calc=='vc-relax' else " cell_dynamics='pr',",'/'])
    lines.append('ATOMIC_SPECIES')
    masses=d.get('atomic_masses_amu',{})
    for e in species:
        if e not in masses: raise ValueError('Explicit atomic_masses_amu required for each element; use curated periodic table utility')
        lines.append(f' {e} {masses[e]} {pps[e]}')
    lines.append('ATOMIC_POSITIONS angstrom')
    for a in atoms: lines.append(' '+a['element']+' '+' '.join(f'{x:.10f}' for x in a['xyz_angstrom']))
    lines.append('CELL_PARAMETERS angstrom')
    for v in s['cell_angstrom']: lines.append(' '+' '.join(f'{x:.10f}' for x in v))
    lines.extend(['K_POINTS automatic', ' '+' '.join(map(str,kpts))+' '+' '.join(map(str,settings.get('k_shift',[0,0,0])))])
    return '\n'.join(lines)+'\n'

def orca_input(d):
    require(d,'structure','charge','multiplicity','method','basis'); s=d['structure']
    if d['multiplicity']<1: raise ValueError('Multiplicity >=1 required')
    if s.get('pbc'): raise ValueError('ORCA molecular template does not model periodic boundary conditions')
    tasks=d.get('tasks',['Opt']); allowed={'Opt','Freq','SP','TightSCF','SlowConv','VeryTightSCF','RIJCOSX','D3BJ','D4','DefGrid3','CPCM'}
    if any(t not in allowed for t in tasks): raise ValueError('Unsupported task token; requires review')
    n=d.get('nprocs',1); ram=d.get('maxcore_mb',1000)
    if n<1 or ram<100: raise ValueError('Invalid nprocs or maxcore_mb')
    lines=['! '+ ' '.join([d['method'],d['basis']]+tasks),f'%pal nprocs {n} end',f'%maxcore {ram}','* xyz '+str(d['charge'])+' '+str(d['multiplicity'])]
    for a in s['atoms']: lines.append(' '+a['element']+' '+' '.join(f'{x:.9f}' for x in a['xyz_angstrom']))
    lines.append('*'); return '\n'.join(lines)+'\n'

def parse_qe(content):
    matches=re.findall(r'!\s+total energy\s*=\s*([+-]?[\d.Ee+-]+)\s+Ry',content)
    forces=re.findall(r'Total force\s*=\s*([+-]?[\d.Ee+-]+)',content)
    done='JOB DONE.' in content
    return {'program':'qe','job_done':done,'scf_energy_ry':float(matches[-1]) if matches else None,'scf_energy_ev':float(matches[-1])*EV_PER_RY if matches else None,'total_force_ry_bohr':float(forces[-1]) if forces else None,'scf_cycles_with_energies':len(matches),'converged':done and bool(matches),'warnings':find_errors(content)}
def parse_orca(content):
    matches=re.findall(r'FINAL SINGLE POINT ENERGY\s+([+-]?[\d.Ee+-]+)',content)
    done='ORCA TERMINATED NORMALLY' in content
    opt='THE OPTIMIZATION HAS CONVERGED' in content
    return {'program':'orca','terminated_normally':done,'optimization_converged':opt,'energy_hartree':float(matches[-1]) if matches else None,'energy_ev':float(matches[-1])*EV_PER_HARTREE if matches else None,'converged':done and bool(matches),'warnings':find_errors(content)}
def parse_xtb(content):
    m=re.findall(r'TOTAL ENERGY\s+([+-]?[\d.Ee+-]+)',content)
    return {'program':'xtb','energy_hartree':float(m[-1]) if m else None,'energy_ev':float(m[-1])*EV_PER_HARTREE if m else None,'warnings':find_errors(content),'converged':'normal termination of xtb' in content.lower() and bool(m)}
def find_errors(s):
    msgs=[]
    for pattern in ['convergence NOT achieved','Error in routine','SCF NOT CONVERGED','ERROR TERMINATION','segmentation fault','out of memory','NaN']:
        if re.search(re.escape(pattern),s,re.I): msgs.append(pattern)
    return msgs

def energy(d):
    require(d,'terms'); units=d.get('input_unit','eV'); factors={'eV':1.,'hartree':EV_PER_HARTREE,'Ry':EV_PER_RY,'kJ/mol':1/96.4853321233}
    if units not in factors: raise ValueError('Unsupported unit')
    total=0.; contributions=[]
    for t in d['terms']:
        require(t,'label','energy','coefficient')
        val=float(t['energy'])*float(t['coefficient'])*factors[units]
        if not math.isfinite(val): raise ValueError('Nonfinite energy')
        total+=val; contributions.append({'label':t['label'],'contribution_eV':val})
    return {'result_ev':total,'result_kj_mol':total*96.4853321233,'terms':contributions,'definition':d.get('definition'),'note':'Verify reference stoichiometry, charge, spin, method, cell consistency and corrections outside arithmetic utility.'}
def stats(d):
    xs=[float(x) for x in d['values']]
    if not xs or any(not math.isfinite(x) for x in xs): raise ValueError('Need finite observations')
    n=len(xs); sd=statistics.stdev(xs) if n>1 else None
    return {'n':n,'mean':statistics.mean(xs),'sd_sample':sd,'sem':sd/math.sqrt(n) if sd is not None else None,'ci95_normal_approx': [statistics.mean(xs)-1.96*sd/math.sqrt(n),statistics.mean(xs)+1.96*sd/math.sqrt(n)] if n>1 else None,'warning':'Requires independent samples; normal CI is approximate and not justified for small n/correlated trajectories.'}
def resources(d):
    require(d,'jobs','cores_per_job','estimated_hours_per_job','ram_gb_per_job','available_cores','available_ram_gb')
    if any(d[k]<=0 for k in ['jobs','cores_per_job','estimated_hours_per_job','ram_gb_per_job','available_cores','available_ram_gb']): raise ValueError('Positive values required')
    safe_ram=d['available_ram_gb']*(1-float(d.get('os_ram_reserve_fraction',.25)))
    concurrent=min(int(d['jobs']),int(d['available_cores']//d['cores_per_job']),int(safe_ram//d['ram_gb_per_job']),int(d.get('user_concurrency_cap',999999)))
    return {'safe_concurrency':max(0,concurrent),'estimated_corehours_total':d['jobs']*d['cores_per_job']*d['estimated_hours_per_job'],'estimated_wallhours_if_serial':d['jobs']*d['estimated_hours_per_job'],'estimated_wallhours_if_concurrent': math.ceil(d['jobs']/concurrent)*d['estimated_hours_per_job'] if concurrent else None,'feasible_by_cpu_ram':concurrent>=1,'estimate_not_guarantee':True}
def execute(d):
    require(d,'argv','cwd'); argv=d['argv']; cwd=Path(d['cwd']).resolve()
    if not cwd.is_dir(): raise FileNotFoundError('cwd absent')
    if not isinstance(argv,list) or not argv or not all(isinstance(a,str) for a in argv): raise ValueError('argv must be list of strings')
    allow=d.get('allow_executable_paths',[])
    exe=Path(argv[0]); located=shutil.which(argv[0]) if not exe.is_absolute() else str(exe)
    if not located or not Path(located).is_file(): raise FileNotFoundError('Executable absent')
    if str(Path(located).resolve()) not in [str(Path(x).resolve()) for x in allow]: raise PermissionError('Executable not approved in allow_executable_paths')
    if not d.get('explicit_execution_approval',False): raise PermissionError('Explicit execution approval required')
    timeout=int(d.get('timeout_seconds',600));
    if timeout<1 or timeout>86400: raise ValueError('timeout out of approved range 1..86400')
    stdin=None
    if d.get('stdin_file'):
        stdin=(cwd/d['stdin_file']).resolve()
        if not stdin.is_relative_to(cwd) or not stdin.is_file(): raise ValueError('stdin_file outside working directory or absent')
    with (stdin.open('rb') if stdin else open(os.devnull,'rb')) as source:
        try:
            run=subprocess.run([str(Path(located).resolve())]+argv[1:],cwd=str(cwd),stdin=source,capture_output=True,timeout=timeout,check=False)
            result={'exit_code':run.returncode,'stdout':run.stdout.decode(errors='replace')[-200000:],'stderr':run.stderr.decode(errors='replace')[-200000:],'timed_out':False}
        except subprocess.TimeoutExpired as e: result={'exit_code':None,'stdout':(e.stdout or b'').decode(errors='replace')[-200000:],'stderr':(e.stderr or b'').decode(errors='replace')[-200000:],'timed_out':True}
    result.update({'argv':[str(Path(located).resolve())]+argv[1:],'cwd':str(cwd),'utc':utc()}); return result

def bandgap(d):
    """Discrete eigenvalue/occupation analysis. Not a converged fundamental gap."""
    require(d,'states'); occupied=[]; unoccupied=[]
    for st in d['states']:
        require(st,'energy_ev','occupation'); e=float(st['energy_ev']); occ=float(st['occupation'])
        if not math.isfinite(e): raise ValueError('Nonfinite eigenvalue')
        if occ>float(d.get('occupied_threshold',0.5)): occupied.append(e)
        else: unoccupied.append(e)
    if not occupied or not unoccupied: raise ValueError('Need occupied and unoccupied states, consistent with spin and k sampling')
    v=max(occupied); c=min(unoccupied)
    return {'vbm_ev':v,'cbm_ev':c,'gap_ev':max(0.,c-v),'metallic_or_fractional_occupation_warning':c<v,'classification':'sampled_kohn_sham_eigenvalue_gap_not_quasiparticle_gap','requires_kpoint_and_functional_convergence':True}
def orbital(d):
    require(d,'orbitals'); return bandgap({'states':d['orbitals'],'occupied_threshold':d.get('occupied_threshold',0.5)}) | {'label':'Molecular orbital HOMO-LUMO eigenvalue gap; not optical gap or excitation energy'}
def bond_scan(d):
    require(d,'structure','atom_i','atom_j','distances_angstrom')
    s=d['structure']; i=d['atom_i']; j=d['atom_j']; atoms=s['atoms']
    if i==j or not 0<=i<len(atoms) or not 0<=j<len(atoms): raise ValueError('Invalid atom indices (0-based)')
    ai=atoms[i]['xyz_angstrom']; aj=atoms[j]['xyz_angstrom']; delta=[aj[k]-ai[k] for k in range(3)]; norm=math.sqrt(sum(x*x for x in delta))
    if norm<1e-9: raise ValueError('Coincident atoms')
    grid=d['distances_angstrom'];
    if len(grid)>200 or not grid or any(float(x)<=0 for x in grid): raise ValueError('Invalid distances or too many structures')
    import copy
    out=[]
    for distance in grid:
        b=copy.deepcopy(s); b['atoms'][j]['xyz_angstrom']=[ai[k]+float(distance)*delta[k]/norm for k in range(3)]
        out.append({'distance_angstrom':float(distance),'structure':b})
    return {'structures':out,'interpretation':'Rigid displaced atom only; constrained optimization and electronic-state tracking required for meaningful dissociation curve'}
def conformer_rank(d):
    require(d,'conformers'); conf=d['conformers'];
    if not conf: raise ValueError('No conformers')
    ranked=sorted(conf,key=lambda x:float(x['energy_ev'])); unique=[]
    for c in ranked:
        if any(c.get('fingerprint') and c.get('fingerprint')==u.get('fingerprint') for u in unique): continue
        unique.append(c)
    return {'ranked':unique,'removed_exact_fingerprint_duplicates':len(conf)-len(unique),'note':'Fingerprint deduplication only; geometry RMSD clustering must be added for scientific conformer deduplication'}
def trajectory(d):
    require(d,'frames'); frames=d['frames'];
    if len(frames)<2: raise ValueError('Need >=2 frames')
    temps=[float(f['temperature_k']) for f in frames if f.get('temperature_k') is not None]
    return {'frames':len(frames),'mean_temperature_k':statistics.mean(temps) if temps else None,'sample_temperature_sd_k':statistics.stdev(temps) if len(temps)>1 else None,'diagnostics':'Basic temperature only: diffusion/MSD require unwrapped periodic coordinates, time units and equilibration selection.'}
def checkpoint(d):
    require(d,'working_directory','restart_files'); root=Path(d['working_directory']).resolve(); files=[]
    for name in d['restart_files']:
        p=(root/name).resolve()
        if not p.is_relative_to(root): raise ValueError('Restart path outside working directory')
        files.append({'path':str(p),'exists':p.exists(),'bytes':p.stat().st_size if p.is_file() else None})
    return {'files':files,'restart_possible':all(f['exists'] and f['bytes'] is not None for f in files),'warning':'Presence is not proof of uncorrupted or version-compatible restart data'}
def xtb_crest_config(d):
    require(d,'xyz_file','charge','uhf','method')
    if d['method'] not in ('gfn0','gfn1','gfn2'): raise ValueError('Unknown GFN model')
    xyz=Path(d['xyz_file'])
    if not xyz.is_file(): raise FileNotFoundError(xyz)
    if int(d['uhf'])<0: raise ValueError('uhf must be >=0')
    argv=['xtb',xyz.name,'--'+d['method'],'--chrg',str(int(d['charge'])),'--uhf',str(int(d['uhf'])),'--opt']
    return {'argv':argv,'cwd':str(xyz.parent),'execution_authorized':False,'warning':'Generated command only; job-executor separately requires approval.'}
def conformer_gen(d):
    require(d,'smiles'); smiles=d['smiles']; n=int(d.get('n_conformers',10))
    if not 1<=n<=100: raise ValueError('n_conformers must be 1..100')
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
    except ImportError: raise RuntimeError('Requires RDKit (not installed); do not invent conformers')
    mol=Chem.AddHs(Chem.MolFromSmiles(smiles))
    if mol is None: raise ValueError('Invalid SMILES')
    params=AllChem.ETKDGv3(); params.randomSeed=int(d.get('seed',42)); ids=list(AllChem.EmbedMultipleConfs(mol,numConfs=n,params=params))
    if not ids: raise RuntimeError('RDKit embedding failed')
    return {'smiles':smiles,'conformers':[{'id':idx,'atoms':[{'element':a.GetSymbol(),'xyz_angstrom':[float(v) for v in mol.GetConformer(idx).GetAtomPosition(a.GetIdx())]} for a in mol.GetAtoms()]} for idx in ids],'warning':'Unoptimized conformers; pass to xTB/CREST, preserve stereochemistry and charge.'}
def adsorption_build(d):
    require(d,'slab','adsorbate','translation_angstrom'); import copy
    slab=copy.deepcopy(d['slab']); ads=d['adsorbate']; shift=d['translation_angstrom']
    if len(shift)!=3 or not slab.get('pbc'): raise ValueError('Periodic slab and three-component translation required')
    for a in ads['atoms']:
        b=copy.deepcopy(a); b['xyz_angstrom']=[b['xyz_angstrom'][i]+shift[i] for i in range(3)]; slab['atoms'].append(b)
    result=validate(slab)
    return {'structure':slab,'geometry_check':result,'warning':'Translation only. Adsorption height, collision check, orientations, binding site symmetry and relaxations are not automatic.'}
def surface_build(d):
    require(d,'structure_path','miller','layers','vacuum_angstrom')
    try:
        from ase.io import read
        from ase.build import surface
    except ImportError: raise RuntimeError('Requires ASE')
    if len(d['miller'])!=3: raise ValueError('Three Miller indices required')
    bulk=read(d['structure_path']); slab=surface(bulk,tuple(d['miller']),int(d['layers']),vacuum=float(d['vacuum_angstrom']))
    return {'structure':{'atoms':[{'element':e,'xyz_angstrom':[float(v) for v in xyz]} for e,xyz in zip(slab.get_chemical_symbols(),slab.positions)],'cell_angstrom':slab.cell.array.tolist(),'pbc':True},'warning':'Review slab polarity, termination, symmetry, thickness, coverage and dipole corrections; ASE output is not validated.'}
def reaction_path(d):
    require(d,'reactant','product','images'); a=d['reactant']; b=d['product']; n=int(d['images'])
    if n<2 or n>40: raise ValueError('images must be 2..40')
    if len(a['atoms'])!=len(b['atoms']) or [x['element'] for x in a['atoms']] != [x['element'] for x in b['atoms']]: raise ValueError('Atom ordering/mapping must match')
    import copy
    frames=[]
    for i in range(n):
        t=i/(n-1); f=copy.deepcopy(a)
        for idx,at in enumerate(f['atoms']): at['xyz_angstrom']=[(1-t)*x+t*y for x,y in zip(a['atoms'][idx]['xyz_angstrom'],b['atoms'][idx]['xyz_angstrom'])]
        frames.append(f)
    return {'candidate_linear_interpolation_images':frames,'warning':'NOT a validated minimum-energy path: atom mapping, periodic unwrap, alignment, NEB/TS and endpoint validation required'}

def run_command(name, data):
    extra={'bandgap-analyzer':bandgap,'orbital-analyzer':orbital,'bond-scan-generator':bond_scan,'conformer-ranker':conformer_rank,'trajectory-analyzer':trajectory,'checkpoint-manager':checkpoint,'xtb-crest-runner':xtb_crest_config,'conformer-generator':conformer_gen,'adsorption-builder':adsorption_build,'surface-builder':surface_build,'reaction-path-builder':reaction_path}
    if name in extra: return extra[name](data)
    if name=='detect': return detect()
    if name=='pp-catalog': return scan_pp(data['root'])
    if name=='structure-parser': return structure(data['path'])
    if name=='structure-validator': return validate(data['structure'])
    if name=='qe-input-generator': return {'input_text':qe_input(data)}
    if name=='orca-input-generator': return {'input_text':orca_input(data)}
    if name in ['qe-output-parser','orca-output-parser','xtb-crest-parser']:
        s=Path(data['path']).read_text(errors='replace')
        return {'qe-output-parser':parse_qe,'orca-output-parser':parse_orca,'xtb-crest-parser':parse_xtb}[name](s)
    if name=='energy-calculator': return energy(data)
    if name=='statistics-aggregator': return stats(data)
    if name=='resource-estimator': return resources(data)
    if name=='job-executor': return execute(data)
    if name=='convergence-validator':
        r=data['parsed']; issues=[]
        if not r.get('converged',False): issues.append('Program did not satisfy completion/convergence markers')
        if r.get('warnings'): issues.extend(r['warnings'])
        return {'passed':not issues,'issues':issues,'note':'Completion marker alone is insufficient for property-level scientific convergence.'}
    if name=='simulation-monitor':
        p=Path(data['path']); content=p.read_text(errors='replace')[-50000:]
        return {'exists':p.exists(),'size_bytes':p.stat().st_size,'recent_warnings':find_errors(content),'last_lines':content.splitlines()[-15:],'note':'Snapshot only; no background monitor daemon.'}
    if name=='simulation-reporter':
        require(data,'results','assumptions','software','validation')
        return {'schema_version':'1.0.0','created_utc':utc(),**data}
    raise NotImplementedError(f'{name} is planned but not implemented. Do not call it as executable.')

def main(tool=None):
    p=argparse.ArgumentParser(description='Simulation Agent '+str(tool or '')+' v1.0.0')
    p.add_argument('--input',help='JSON input path; optional for detect')
    p.add_argument('--output',help='JSON result path')
    p.add_argument('--print-example',action='store_true')
    args=p.parse_args()
    if args.print_example:
        print(json.dumps({'tool':tool,'input':'JSON specified in README; verify schema'},indent=2)); return
    try:
        inp=read_json(args.input) if args.input else {}
        result=run_command(tool,inp)
        if args.output: write_json(args.output,result)
        else: print(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    except Exception as e:
        print(json.dumps({'tool':tool,'error_type':type(e).__name__,'error':str(e),'success':False},indent=2),file=sys.stderr)
        raise SystemExit(2)
if __name__=='__main__':
    main(sys.argv[1] if len(sys.argv)>1 else None)
