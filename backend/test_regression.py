# test_regression.py
import unittest
import chess
import json
import os
from app import app, evaluate_board, minimax, alpha_beta, GameRecord, Session, engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile

class RegressionTests(unittest.TestCase):
    """Test that old functionality still works after new features added"""
    
    def setUp(self):
        self.initial_fen = chess.STARTING_FEN
        self.board = chess.Board(self.initial_fen)
        app.config["TESTING"] = True
        self.client = app.test_client()
    
    # Original engine tests (from test_app.py)
    def test_evaluate_board_initial(self):
        """Initial board should be balanced"""
        score = evaluate_board(self.board)
        self.assertTrue(abs(score) < 0.5)
    
    def test_minimax_move_generation(self):
        """Minimax should generate valid moves"""
        move, score = minimax(self.board, depth=2, maximizing_player=True)
        self.assertIsInstance(move, chess.Move)
        self.assertIsInstance(score, (int, float))
    
    def test_alpha_beta_move_generation(self):
        """Alpha-beta should generate valid moves"""
        move, score = alpha_beta(self.board, depth=2, alpha=-float('inf'), 
                                 beta=float('inf'), maximizing_player=True)
        self.assertIsInstance(move, chess.Move)
        self.assertIsInstance(score, (int, float))
    
    def test_api_move_minimax(self):
        """API should return valid moves for minimax"""
        response = self.client.post('/api/move', json={
            "fen": self.initial_fen,
            "engine": "minimax",
            "depth": 2
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("move", data)
        self.assertIsNotNone(data['move'])
    
    def test_api_move_alphabeta(self):
        """API should return valid moves for alpha-beta"""
        response = self.client.post('/api/move', json={
            "fen": self.initial_fen,
            "engine": "alphabeta",
            "depth": 2
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("move", data)
        self.assertIsNotNone(data['move'])
    
    def test_api_game_status_initial(self):
        """Game status should work for initial position"""
        response = self.client.post('/api/game-status', json={
            "fen": self.initial_fen
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data["is_checkmate"])
        self.assertFalse(data["is_stalemate"])
        self.assertFalse(data["is_check"])
        self.assertFalse(data["is_game_over"])

if __name__ == "__main__":
    unittest.main()
