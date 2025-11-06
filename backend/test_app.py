import unittest
import chess
import json

from app import app, evaluate_board, minimax, alpha_beta

class ChessEngineTests(unittest.TestCase):

    def setUp(self):
        # Standard initial position FEN
        self.initial_fen = chess.STARTING_FEN
        self.board = chess.Board(self.initial_fen)

    def test_evaluate_board_initial(self):
        # Initial board should be balanced
        score = evaluate_board(self.board)
        self.assertTrue(abs(score) < 0.5)

    def test_minimax_move_generation(self):
        move, score = minimax(self.board, depth=2, maximizing_player=True)
        self.assertIsInstance(move, chess.Move)
        self.assertIsInstance(score, float)

    def test_alpha_beta_move_generation(self):
        move, score = alpha_beta(self.board, depth=2, alpha=-float('inf'), beta=float('inf'), maximizing_player=True)
        self.assertIsInstance(move, chess.Move)
        self.assertIsInstance(score, float)

    def test_minimax_terminal(self):
        # Check minimax on checkmate position
        mate_fen = "7K/5kq1/8/8/8/8/8/8 w - - 0 1" # Black is about to mate
        board = chess.Board(mate_fen)
        move, score = minimax(board, depth=1, maximizing_player=True)
        print(score)
        self.assertTrue(board.is_game_over() or score < 0)

    def test_alpha_beta_terminal(self):
        # Check alpha-beta on stalemate position
        stalemate_fen = "7K/5kq1/8/8/8/8/8/8 w - - 0 1" # White has a mate in one
        board = chess.Board(stalemate_fen)
        move, score = alpha_beta(board, depth=1, alpha=-float('inf'), beta=float('inf'), maximizing_player=True)
        self.assertTrue(board.is_game_over() or score > 0)


class FlaskAPITests(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.fen = chess.STARTING_FEN

    def test_api_move_minimax(self):
        response = self.client.post('/api/move', json={
            "fen": self.fen,
            "engine": "minimax",
            "depth": 2
        })
        data = json.loads(response.data)
        self.assertIn("move", data)
        self.assertIsInstance(data['move'], str)

    def test_api_move_alphabeta(self):
        response = self.client.post('/api/move', json={
            "fen": self.fen,
            "engine": "alphabeta",
            "depth": 2
        })
        data = json.loads(response.data)
        self.assertIn("move", data)
        self.assertIsInstance(data['move'], str)

    def test_api_game_status(self):
        response = self.client.post('/api/game-status', json={
            "fen": self.fen
        })
        data = json.loads(response.data)
        self.assertIn("is_checkmate", data)
        self.assertIn("is_stalemate", data)
        self.assertIn("is_check", data)
        self.assertIn("is_game_over", data)
        self.assertFalse(data["is_checkmate"])
        self.assertFalse(data["is_stalemate"])
        self.assertFalse(data["is_check"])
        self.assertFalse(data["is_game_over"])

    def test_api_game_status_checkmate(self):
        mate_fen = "rnb1kbnr/ppppqppp/8/8/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
        response = self.client.post('/api/game-status', json={
            "fen": mate_fen
        })
        data = json.loads(response.data)
        self.assertTrue(isinstance(data["is_checkmate"], bool))
        self.assertTrue(isinstance(data["is_stalemate"], bool))
        self.assertTrue(isinstance(data["is_check"], bool))
        self.assertTrue(isinstance(data["is_game_over"], bool))

if __name__ == "__main__":
    unittest.main()
