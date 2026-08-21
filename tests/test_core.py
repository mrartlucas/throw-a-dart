import unittest
from throw_a_dart.semantic_darts import DartSample, SemanticDartTracker
from throw_a_dart.target_engine import TargetField, TargetBehavior
from throw_a_dart.game_state import SHOWS, TEST_MODE, CircusGameState, Phase

class CoreTests(unittest.TestCase):
    def test_stationary_hit(self):
        field=TargetField(1)
        field.start_act(0)
        result=field.hit_test(64,72)
        self.assertTrue(result.hit)
        self.assertEqual(result.points,50)

    def test_stationary_target_replenishes_after_hit(self):
        field=TargetField(1)
        field.start_act(0)
        ids={target.target_id for target in field.targets}
        field.hit_test(64,72)
        field.update()
        self.assertEqual(len(field.targets),3)
        self.assertTrue(any(target.target_id not in ids for target in field.targets))

    def test_hit_and_miss_leave_short_impact_feedback(self):
        field=TargetField(1)
        field.start_act(0)
        field.hit_test(64,72)
        field.hit_test(2,120)
        self.assertEqual(len(field.impacts),2)
        self.assertTrue(field.impacts[0].hit)
        self.assertFalse(field.impacts[1].hit)
        for _ in range(12):
            field.update()
        self.assertEqual(field.impacts,[])

    def test_popup_hides(self):
        field=TargetField(1)
        field.start_act(2)
        popup=next(t for t in field.targets if t.behavior is TargetBehavior.POPUP)
        for _ in range(70):
            popup.update()
        self.assertFalse(popup.visible)

    def test_hit_popup_is_replaced(self):
        field=TargetField(1)
        field.start_act(2)
        popup=next(t for t in field.targets if t.behavior is TargetBehavior.POPUP)
        popup.visible=True
        result=field.hit_test(int(popup.x),int(popup.y))
        self.assertTrue(result.hit)
        old=popup.target_id
        field.update()
        replacement=next(t for t in field.targets if t.behavior is TargetBehavior.POPUP)
        self.assertNotEqual(replacement.target_id,old)

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

    def test_setup_starts_at_shows(self):
        game=CircusGameState()
        self.assertEqual(game.phase,Phase.SHOW_SELECT)

    def test_three_shows_three_acts_each(self):
        self.assertEqual(len(SHOWS),3)
        self.assertTrue(all(len(show.acts)==3 for show in SHOWS))

    def test_show_selection_wraps(self):
        game=CircusGameState()
        game.cycle_show(-1)
        self.assertEqual(game.selected_show,len(SHOWS)-1)
        game.cycle_show(1)
        self.assertEqual(game.selected_show,0)

    def test_act_selection_wraps_inside_show(self):
        game=CircusGameState()
        game.cycle_act(-1)
        self.assertEqual(game.selected_act,2)
        game.cycle_act(1)
        self.assertEqual(game.selected_act,0)

    def test_test_mode_unlocks_everything(self):
        self.assertTrue(TEST_MODE)
        game=CircusGameState()
        for show_index in range(3):
            self.assertTrue(game.is_show_unlocked(show_index))
            for act_index in range(3):
                self.assertTrue(game.is_act_unlocked(show_index,act_index))

    def test_begin_uses_selected_show_and_act(self):
        game=CircusGameState(selected_show=2,selected_act=1)
        game.begin()
        self.assertEqual(game.show_index,2)
        self.assertEqual(game.act_index,1)
        self.assertEqual(game.phase,Phase.ACT_INTRO)

    def test_difficulty_increases_across_show_act_order(self):
        game=CircusGameState(selected_show=0,selected_act=0)
        game.begin()
        self.assertEqual(game.difficulty_rank,0)
        game.selected_show=2
        game.selected_act=2
        game.begin()
        self.assertEqual(game.difficulty_rank,8)

    def test_later_difficulty_reduces_forgiveness_and_increases_speed(self):
        easy=TargetField(1)
        hard=TargetField(1)
        easy.start_act(1,difficulty=0)
        hard.start_act(1,difficulty=8)
        self.assertLess(hard.forgiveness,easy.forgiveness)
        self.assertGreater(hard.speed_scale,easy.speed_scale)

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
        game=CircusGameState(player_count=2,throws_per_act=1,selected_show=2,selected_act=2)
        game.begin()
        game.begin_play()
        game.record_throw(25)
        _,transition=game.record_throw(25)
        self.assertEqual(transition,"game_over")
        self.assertEqual(game.phase,Phase.GAME_RESULT)
        self.assertEqual(game.show_index,2)
        self.assertEqual(game.act_index,2)

    def test_combo_caps_at_three_x(self):
        game=CircusGameState(throws_per_act=10)
        game.begin()
        game.begin_play()
        self.assertEqual(game.record_throw(25)[0],25)
        self.assertEqual(game.record_throw(25)[0],50)
        self.assertEqual(game.record_throw(25)[0],75)
        self.assertEqual(game.record_throw(25)[0],75)

    def test_star_thresholds_return_zero_to_three(self):
        thresholds=(100,250,450)
        self.assertEqual(CircusGameState.stars_for_score(99,thresholds),0)
        self.assertEqual(CircusGameState.stars_for_score(100,thresholds),1)
        self.assertEqual(CircusGameState.stars_for_score(300,thresholds),2)
        self.assertEqual(CircusGameState.stars_for_score(500,thresholds),3)

if __name__=='__main__':
    unittest.main()
