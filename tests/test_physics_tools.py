"""Independent dimensional and geometry invariants for framework inputs."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tools'))
from calibrate import air,cfd,ttv
from iceglass.inputs import geometry,blocks,describe
from iceglass.builder import build,variant

class PhysicsTools(unittest.TestCase):
    def test_air_preserves_sink_conductance_under_area_normalization(self):
        a=air(.23,1259.28);b=air(.23,2518.56)
        self.assertAlmostEqual(a['G_W_K'],1/.23)
        self.assertAlmostEqual(a['h_native_W_um2K']*1259.28e6,a['G_W_K'])
        self.assertAlmostEqual(b['h_native_W_um2K'],a['h_native_W_um2K']/2)
    def test_projected_cfd_boundary_integrates_patch_heat(self):
        a=cfd(ROOT/'examples/calibration/synthetic-cfd.csv',2e6)
        self.assertAlmostEqual(a['h_native_W_um2K'],3/(2e6*((25+2*15)/3)))
        self.assertAlmostEqual(a['h_native_W_um2K']*a['projected_area_um2']*a['area_weighted_delta_K'],3)
    def test_ttv_fit_recovers_known_linear_resistance(self):
        a=ttv(ROOT/'examples/calibration/synthetic-ttv.csv',100)
        self.assertEqual(a['R_case_sat_K_W'],.5)
        self.assertEqual(a['residual_K'],[0,0])
        self.assertAlmostEqual(a['h_W_m2K'],20000)
    def test_geometry_rejects_overlap_and_out_of_bounds(self):
        a={'name':'A','position_um':[0,0],'size_um':[2,2],'power_W':[1]}
        b={'name':'B','position_um':[1,1],'size_um':[2,2],'power_W':[1]}
        with self.assertRaises(ValueError):geometry([a,b],[10,10])
        with self.assertRaises(ValueError):geometry([a],[1,1])
    def test_seed_variant_preserves_area_and_changes_only_selected_power_boundary(self):
        with tempfile.TemporaryDirectory() as temp:
            target=variant(ROOT/'models/co-planar/water/static-standard.stk',Path(temp)/'variant',plate_factor=.575,reference_K=308,power_scale=.5)
            data=json.loads((target.parent/'model.json').read_text())
            self.assertTrue(all(x['area_preserved'] for x in data['checks']))
            total=sum(x['first_sample_power_W'] for x in data['checks'])
            self.assertAlmostEqual(total,405.27/2)
            text=target.read_text();self.assertIn('2.346e-08',text);self.assertIn('temperature 308',text)
    def test_constant_transient_source_is_available_for_every_native_slot(self):
        config=json.loads((ROOT/'examples/glass-package.json').read_text())
        config['solver']={'step_s':.005,'slot_s':.005}
        die=next(layer for layer in config['layers'] if layer.get('kind')=='die')
        width,height=config['chip_um']
        die['blocks']=[
            {'name':'DYNAMIC','position_um':[0,0],'size_um':[width/2,height],'power_W':[1,2,3]},
            {'name':'CONSTANT','position_um':[width/2,0],'size_um':[width/2,height],'power_W':[.5]}]
        with tempfile.TemporaryDirectory() as temp:
            target=build(config,Path(temp)/'transient')
            emitted=blocks(next(target.parent.glob('*.flp')))
            self.assertEqual(emitted[1]['power_W'],[.5,.5,.5])
            self.assertEqual(describe(target)['power_range_W'],[1.5,3.5])
            self.assertEqual(die['blocks'][1]['power_W'],[.5])

if __name__=='__main__':unittest.main()
