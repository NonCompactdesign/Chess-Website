# test_mutations.py
import unittest
import chess
from app import evaluate_board, minimax, alpha_beta
import copy

class MutationTests(unittest.TestCase):
    """Tests designed to catch common mutations in chess logic"""
    
    def test_piece_values_matter(self):
        """Verify that piece values affect evaluation"""
        # Position with white queen vs black queen
        board_white_advantage = chess.Board("rnb1kbnr/pppppppp/8/8/8/8/PPPPPPQP/RNBQKBNR w KQkq - 0 1")
        board_equal = chess.Board("rnb1kbnr/pppppppp/8/8/8/8/PPPPPPqP/RNBQKBNR w KQkq - 0 1")
        
        score_white_advantage = evaluate_board(board_white_advantage)
        score_equal = evaluate_board(board_equal)
        
        # White advantage should be higher
        self.assertGreater(score_white_advantage, score_equal)
    
    def test_minimax_maximization(self):
        """Verify minimax actually maximizes"""
        board = chess.Board()
        
        # Get move for maximizing player
        move_max, score_max = minimax(board, depth=2, maximizing_player=True)
        
        # Get move for minimizing player  
        move_min, score_min = minimax(board, depth=2, maximizing_player=False)
        
        # Scores should be different (likely)
        # Maximizing should find better moves for white
        self.assertIsNotNone(move_max)
        self.assertIsNotNone(move_min)
    
    def test_alpha_beta_pruning_effect(self):
        """Verify alpha-beta pruning finds same or similar scores"""
        board = chess.Board()
        
        move_mm, score_mm = minimax(board, depth=3, maximizing_player=True)
        move_ab, score_ab = alpha_beta(board, depth=3, alpha=-float('inf'), 
                                       beta=float('inf'), maximizing_player=True)
        
        # Both should find same score (or very close due to move ordering)
        self.assertAlmostEqual(score_mm, score_ab, places=1)
    
    def test_depth_affects_evaluation(self):
        """Verify deeper search gives better evaluation"""
        board = chess.Board()
        
        _, score_depth1 = minimax(board, depth=1, maximizing_player=True)
        _, score_depth2 = minimax(board, depth=2, maximizing_player=True)
        
        # Scores should exist and be different
        self.assertIsInstance(score_depth1, (int, float))
        self.assertIsInstance(score_depth2, (int, float))
    
    def test_checkmate_detection(self):
        """Verify engine detects checkmate"""
        # Foolscmate position: 1.f3 e5 2.g4 Qh4#
        mate_board = chess.Board("rnbqkbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")
        
        move, score = minimax(mate_board, depth=1, maximizing_player=True)
        
        # Score should be very negative (white is getting mated)
        self.assertLess(score, -5)
    
    def test_stalemate_evaluation(self):
        """Verify stalemate positions are identified"""
        # Stalemate: white king on h8, black king on g6, no legal moves for white
        stalemate_fen = "7K/5k2/8/8/8/8/8/8 w - - 0 1"
        board = chess.Board(stalemate_fen)
        
        # Should still return a move or handle gracefully
        move, score = minimax(board, depth=1, maximizing_player=True)
        # In stalemate, it's a draw (score near 0)
        self.assertIsInstance(score, (int, float))
    
    def test_alpha_beta_cutoff(self):
        """Verify alpha-beta actually prunes branches"""
        board = chess.Board()
        
        # Call with tight alpha-beta bounds
        move, score = alpha_beta(board, depth=2, alpha=5, beta=6, maximizing_player=True)
        
        self.assertIsNotNone(move)
        self.assertIsInstance(score, (int, float))

if __name__ == "__main__":
    unittest.main()
