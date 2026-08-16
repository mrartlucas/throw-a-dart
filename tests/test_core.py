import unittest
from throw_a_dart.semantic_darts import DartSample, SemanticDartTracker
from throw_a_dart.target_engine import TargetField, TargetBehavior
from throw_a_dart.game_state import CircusGameState, Phase

class CoreTests(unittest.TestCase):
    def test_stationary_hit(self):
        f=TargetField(1); f.start_act(0); r=f.hit_test(64,72); self.assertTrue(r.hit); self.assertEqual(r.points,50)
    def test_popup_hides(self):
        f=TargetField(1); f.start_act(2); p=next(t for t in f.targets if t.behavior is TargetBehavior.POPUP)
        for _ in range(70): p.update()
        self.assertFalse(p.visible)
    def test_retained_dart_not_repeated(self):
        t=SemanticDartTracker(); t.baseline(()); d=(DartSample(0,40,40),)
        self.assertEqual(t.observe(d,d),d); self.assertEqual(t.observe((),d),())
    def test_changed_coordinate_is_new_throw(self):
        t=SemanticDartTracker(); t.baseline((DartSample(0,40,40),)); d=(DartSample(0,60,60),)
        self.assertEqual(t.observe((),d),d)
    def test_multiplayer_act_rotation(self):
        g=CircusGameState(player_count=2,throws_per_act=2); g.begin(); g.begin_play()
        g.record_throw(25); g.after_removal(); self.assertEqual(g.current_player,1)
        g.record_throw(25); g.after_removal(); self.assertEqual(g.current_player,0)
        g.record_throw(25); g.after_removal(); self.assertEqual(g.current_player,1)
        g.record_throw(25); self.assertEqual(g.after_removal(),"next_act"); self.assertEqual(g.act_index,1)
    def test_combo_caps_at_three_x(self):
        g=CircusGameState(); g.phase=Phase.PLAYING
        self.assertEqual(g.record_throw(25),25); g.phase=Phase.PLAYING
        self.assertEqual(g.record_throw(25),50); g.phase=Phase.PLAYING
        self.assertEqual(g.record_throw(25),75); g.phase=Phase.PLAYING
        self.assertEqual(g.record_throw(25),75)

if __name__=='__main__': unittest.main()
