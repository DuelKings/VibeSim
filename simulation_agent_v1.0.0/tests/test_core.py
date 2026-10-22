import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'utils'))
from core import energy,stats,resources,structure_xyz,validate,orca_input,parse_qe,parse_orca,windows_to_wsl
class TestUtilities(unittest.TestCase):
 def test_energy(self):
  r=energy({'terms':[{'label':'complex','energy':-9,'coefficient':1},{'label':'substrate','energy':-6,'coefficient':-1},{'label':'adsorbate','energy':-2,'coefficient':-1}]}); self.assertAlmostEqual(r['result_ev'],-1)
 def test_stats(self): self.assertEqual(stats({'values':[1,2,3]})['mean'],2)
 def test_resources(self):
  x=resources({'jobs':12,'cores_per_job':2,'estimated_hours_per_job':1,'ram_gb_per_job':3,'available_cores':8,'available_ram_gb':12}); self.assertEqual(x['safe_concurrency'],3)
 def test_xyz(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'h2.xyz'; p.write_text('2\nhydrogen\nH 0 0 0\nH 0 0 0.74\n')
   self.assertTrue(validate(structure_xyz(p))['valid'])
 def test_orca(self):
  s={'atoms':[{'element':'H','xyz_angstrom':[0,0,0]},{'element':'H','xyz_angstrom':[0,0,.74]}],'pbc':False}
  self.assertIn('* xyz 0 1',orca_input({'structure':s,'charge':0,'multiplicity':1,'method':'PBE0','basis':'def2-SVP','tasks':['Opt']}))
 def test_parsers(self):
  self.assertAlmostEqual(parse_qe('! total energy = -1.0000 Ry\nJOB DONE.')['scf_energy_ry'],-1)
  self.assertTrue(parse_orca('FINAL SINGLE POINT ENERGY -2.0\nORCA TERMINATED NORMALLY')['converged'])
 def test_path(self): self.assertEqual(windows_to_wsl(r'C:\Users\abc'),' /mnt/c/Users/abc'.strip())
if __name__=='__main__': unittest.main()
