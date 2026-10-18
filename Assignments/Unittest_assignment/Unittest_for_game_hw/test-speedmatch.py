
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import pygame

import speedmatch as game


class TestShapesAndCards(unittest.TestCase):
    
    def test_shapes_of_same_type_are_equal(self):
        self.assertEqual(game.Circle(), game.Circle())

    def test_shapes_of_different_types_are_not_equal(self):
        self.assertNotEqual(game.Circle(), game.Square())

    def test_card_matches_when_shape_and_color_match(self):
        first = game.Card(game.Circle(), (255, 0, 0))
        second = game.Card(game.Circle(), (255, 0, 0))
        self.assertTrue(first.matches(second))

    def test_card_does_not_match_when_color_differs(self):
        first = game.Card(game.Circle(), (255, 0, 0))
        second = game.Card(game.Circle(), (0, 0, 255))
        self.assertFalse(first.matches(second))

    def test_card_does_not_match_when_shape_differs(self):
        first = game.Card(game.Circle(), (255, 0, 0))
        second = game.Card(game.Square(), (255, 0, 0))
        self.assertFalse(first.matches(second))


class TestCardFactory(unittest.TestCase):

    def setUp(self):
        self.shapes = [game.Circle(), game.Square(), game.Triangle(), game.Diamond()]
        self.colors = [(1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4)]
        self.factory = game.CardFactory(self.shapes, self.colors)

    def test_create_random_uses_only_items_allowed_by_variety(self):
        with patch("speedmatch.random.choice", side_effect=lambda items: items[-1]):
            card = self.factory.create_random(2)
        self.assertIs(card.shape, self.shapes[1])
        self.assertEqual(card.color, self.colors[1])

    def test_create_next_can_copy_previous_card(self):
        previous = game.Card(game.Triangle(), (10, 20, 30))
        with patch("speedmatch.random.random", return_value=0.1):
            next_card = self.factory.create_next(previous, 2, 0.5)
        self.assertTrue(next_card.matches(previous))
        self.assertIsNot(next_card, previous)

    def test_create_next_generates_random_card_when_match_chance_fails(self):
        previous = game.Card(game.Circle(), self.colors[0])
        with patch("speedmatch.random.random", return_value=0.9), \
             patch("speedmatch.random.choice", side_effect=lambda items: items[1]):
            next_card = self.factory.create_next(previous, 2, 0.5)
        self.assertIs(next_card.shape, self.shapes[1])
        self.assertEqual(next_card.color, self.colors[1])


class TestLevelManager(unittest.TestCase):

    def test_starts_at_level_one_with_variety_two(self):
        levels = game.LevelManager(correct_per_level=5, max_variety=4)
        self.assertEqual(levels.level, 1)
        self.assertEqual(levels.variety, 2)

    def test_level_increases_after_required_correct_answers(self):
        levels = game.LevelManager(correct_per_level=5, max_variety=4)
        for _ in range(5):
            levels.register_correct()
        self.assertEqual(levels.level, 2)
        self.assertEqual(levels.variety, 3)

    def test_variety_never_exceeds_maximum(self):
        levels = game.LevelManager(correct_per_level=1, max_variety=4)
        for _ in range(20):
            levels.register_correct()
        self.assertEqual(levels.variety, 4)


class TestScoreBoard(unittest.TestCase):
    def setUp(self):
        self.board = game.ScoreBoard()

    def test_new_round_starts_with_zero_values(self):
        self.assertEqual(self.board.score, 0)
        self.assertEqual(self.board.correct, 0)
        self.assertEqual(self.board.total, 0)
        self.assertEqual(self.board.accuracy, 0)

    def test_correct_answers_add_base_points_and_streak_bonus(self):
        self.board.register_correct()
        self.assertEqual(self.board.score, 11)
        self.board.register_correct()
        self.assertEqual(self.board.score, 23)
        self.assertEqual(self.board.correct, 2)
        self.assertEqual(self.board.total, 2)

    def test_wrong_answer_resets_streak_and_applies_penalty(self):
        self.board.register_correct()
        self.board.register_correct()
        self.board.register_wrong()
        self.assertEqual(self.board.score, 18)  
        self.assertAlmostEqual(self.board.accuracy, 200 / 3)
        self.board.register_wrong()
        self.assertEqual(self.board.score, 13)

    def test_score_never_drops_below_zero(self):
        self.board.register_wrong()
        self.assertEqual(self.board.score, 0)

    def test_accuracy_counts_correct_answers_over_all_answers(self):
        self.board.register_correct()
        self.board.register_wrong()
        self.board.register_correct()
        self.board.register_wrong()
        self.assertEqual(self.board.accuracy, 50)

    def test_best_score_survives_reset(self):
        self.board.register_correct()
        self.board.finish()
        best = self.board.best
        self.board.reset()
        self.assertEqual(self.board.score, 0)
        self.assertEqual(self.board.best, best)

    def test_finish_does_not_reduce_previous_best(self):
        self.board.register_correct()
        self.board.finish()
        best = self.board.best
        self.board.reset()
        self.board.register_wrong()
        self.board.finish()
        self.assertEqual(self.board.best, best)


class TestTimerAndFeedback(unittest.TestCase):

    def test_timer_counts_down_and_rounds_display_up(self):
        timer = game.Timer(10)
        timer.update(0.8)
        self.assertEqual(timer.display_seconds, 10)
        self.assertFalse(timer.finished)

    def test_timer_stops_at_zero(self):
        timer = game.Timer(3)
        timer.update(10)
        self.assertTrue(timer.finished)
        self.assertEqual(timer.display_seconds, 0)

    def test_timer_reset_restores_full_duration(self):
        timer = game.Timer(3)
        timer.update(1.5)
        timer.reset()
        self.assertEqual(timer.display_seconds, 3)
        self.assertFalse(timer.finished)

    def test_feedback_shows_triggered_color_until_time_expires(self):
        flash = game.FeedbackFlash(0.35)
        flash.trigger(game.Settings.GREEN)
        self.assertEqual(flash.current_color(game.Settings.PANEL), game.Settings.GREEN)
        flash.update(0.2)
        self.assertEqual(flash.current_color(game.Settings.PANEL), game.Settings.GREEN)
        flash.update(0.2)
        self.assertEqual(flash.current_color(game.Settings.PANEL), game.Settings.PANEL)

    def test_feedback_reset_clears_color_immediately(self):
        flash = game.FeedbackFlash(0.35)
        flash.trigger(game.Settings.RED)
        flash.reset()
        self.assertEqual(flash.current_color(game.Settings.PANEL), game.Settings.PANEL)


class TestButton(unittest.TestCase):

    def setUp(self):
        self.button = game.Button((10, 10, 100, 50), "Test", game.Settings.GREEN)

    def test_left_click_inside_button_is_detected(self):
        event = SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=(20, 20))
        self.assertTrue(self.button.is_clicked(event))

    def test_click_outside_button_is_ignored(self):
        event = SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=(200, 200))
        self.assertFalse(self.button.is_clicked(event))

    def test_right_click_is_ignored(self):
        event = SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=3, pos=(20, 20))
        self.assertFalse(self.button.is_clicked(event))

    def test_non_mouse_event_is_ignored(self):
        event = SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_SPACE)
        self.assertFalse(self.button.is_clicked(event))


class TestPlaySceneAnswerLogic(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.game = SimpleNamespace(scoreboard=game.ScoreBoard(), change_scene=lambda name: None)
        self.scene = game.PlayScene(self.game)
        self.scene._previous = game.Card(game.Circle(), (255, 0, 0))
        self.scene._current = game.Card(game.Circle(), (255, 0, 0))
        self.next_card = game.Card(game.Square(), (0, 0, 255))
        self.scene._factory.create_next = lambda *args: self.next_card

    def tearDown(self):
        pygame.quit()

    def test_correct_match_answer_increases_score_and_level_counter(self):
        self.scene._answer(True)
        self.assertEqual(self.game.scoreboard.correct, 1)
        self.assertEqual(self.game.scoreboard.total, 1)
        self.assertEqual(self.scene._levels.level, 1)
        self.assertEqual(self.scene._flash.current_color(game.Settings.PANEL), game.Settings.GREEN)

    def test_wrong_answer_adds_penalty_and_red_feedback(self):
        self.scene._answer(False)
        self.assertEqual(self.game.scoreboard.correct, 0)
        self.assertEqual(self.game.scoreboard.total, 1)
        self.assertEqual(self.game.scoreboard.score, 0)
        self.assertEqual(self.scene._flash.current_color(game.Settings.PANEL), game.Settings.RED)

    def test_first_card_answer_does_not_change_score(self):
        self.scene._previous = None
        self.scene._current = game.Card(game.Circle(), (255, 0, 0))
        self.scene._answer(True)
        self.assertEqual(self.game.scoreboard.total, 0)
        self.assertEqual(self.game.scoreboard.score, 0)

    def test_answer_advances_previous_and_current_cards(self):
        old_current = self.scene._current
        self.scene._answer(True)
        self.assertIs(self.scene._previous, old_current)
        self.assertIs(self.scene._current, self.next_card)


if __name__ == "__main__":
    unittest.main(verbosity=2)
