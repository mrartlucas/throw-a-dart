import unittest
from throw_a_dart.semantic_darts import DartSample, SemanticDartTracker
from throw_a_dart.target_engine import TargetField, TargetBehavior
from throw_a_dart.game_state import ACT_NAMES, CircusGameState, Phase

class CoreTests(unittest.TestCase):
    def test_stationary_hit(self):
        field=TargetField(1)
        field.start_act(0)
        result=field.hit_test(64,72)
        self.assertTrue(result.hit)
        self.assertEqual(result.points,50)

    def test_popup_hides(self):
        field=TargetField(1)
        field.start_act(2)
        popup=next(t for t in field.targets if t.behavior is TargetBehavior.POPUP)
        for _ in range(70):
            popup.update()
        self.assertFalse(popup.visible)

    def test_retained_dart_not_repeated(self):
        tracker=SemanticDartTracker()
        tracker.baseline(())
        dart=(DartSample(0,40,40),)
        self.assertEqual(tracker.observe(dart,dart),dart)
        self.assertEqual(tracker.observe((),dart),())

    def test_changed_coordinate_is_new_throw(self):
        tracker=SemanticDartTracker()
        tracker.baseline((DartSample(0,40,40),))
        moved=(DartSample(0,60,60),)
        self.assertEqual(tracker.observe((),moved),moved)

    def test_act_selection_wraps(self):
        game=CircusGameState()
        game.cycle_act(-1)
        self.assertEqual(game.selected_act,len(ACT_NAMES)-1)
        game.cycle_act(1)
        self.assertEqual(game.selected_act,0)

    def test_begin_uses_selected_act(self):
        game=CircusGameState(selected_act=2)
        game.begin()
        self.assertEqual(game.act_index,2)
        self.assertEqual(game.phase,Phase.ACT_INTRO)

    def test_multiplayer_rotates_without_removal_gate(self):
        game=CircusGameState(player_count=2,throws_per_act=2)
        game.begin()
        game.begin_play()
        _,transition=game.record_throw(25)
        self.assertEqual(transition,"continue")
        self.assertEqual(game.current_player,1)
        self.assertEqual(game.phase,Phase.PLAYING)
        game.record_throw(25)
        self.assertEqual(game.current_player,0)

    def test_selected_act_ends_after_all_players_finish(self):
        game=CircusGameState(player_count=2,throws_per_act=1,selected_act=3)
        game.begin()
        game.begin_play()
        game.record_throw(25)
        _,transition=game.record_throw(25)
        self.assertEqual(transition,"game_over")
        self.assertEqual(game.phase,Phase.GAME_RESULT)
        self.assertEqual(game.act_index,3)

    def test_combo_caps_at_three_x(self):
        game=CircusGameState(throws_per_act=10)
        game.begin()
        game.begin_play()
        self.assertEqual(game.record_throw(25)[0],25)
        self.assertEqual(game.record_throw(25)[0],50)
        self.assertEqual(game.record_throw(25)[0],75)
        self.assertEqual(game.record_throw(25)[0],75)

if __name__=='__main__':
    unittest.main()
