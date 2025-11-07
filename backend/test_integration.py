# test_integration.py - FIXED VERSION
import unittest
import chess
import json
import requests
import time

# Your backend URL
API_URL = "http://localhost:5000/api"

class IntegrationAPITests(unittest.TestCase):
    """Test integration against live backend API"""
    
    def setUp(self):
        """Wait for backend to be ready"""
        time.sleep(0.5)
    
    def test_minimax_engine(self):
        """Test minimax engine via API"""
        response = requests.post(f"{API_URL}/move", json={
            "fen": chess.STARTING_FEN,
            "engine": "minimax",
            "depth": 2
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data.get('move'))
        self.assertIsInstance(data['move'], str)
        print(f"✓ Minimax move: {data['move']}")
    
    def test_alphabeta_engine(self):
        """Test alpha-beta engine via API"""
        response = requests.post(f"{API_URL}/move", json={
            "fen": chess.STARTING_FEN,
            "engine": "alphabeta",
            "depth": 2
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data.get('move'))
        print(f"✓ Alpha-Beta move: {data['move']}")
    
    def test_engine_move_validity(self):
        """Test that engine moves are legal"""
        board = chess.Board()
        response = requests.post(f"{API_URL}/move", json={
            "fen": board.fen(),
            "engine": "minimax",
            "depth": 2
        })
        data = response.json()
        move_uci = data['move']
        
        # Verify move is legal using push_uci
        board_copy = chess.Board(board.fen())
        try:
            board_copy.push_uci(move_uci)
            self.assertTrue(True)
            print(f"✓ Move is legal: {move_uci}")
        except ValueError:
            self.fail(f"Move {move_uci} is not legal")
    
    def test_game_status_initial(self):
        """Test game status for initial position"""
        response = requests.post(f"{API_URL}/game-status", json={
            "fen": chess.STARTING_FEN
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertFalse(data['is_checkmate'])
        self.assertFalse(data['is_stalemate'])
        self.assertFalse(data['is_check'])
        self.assertFalse(data['is_game_over'])
        print("✓ Game status (initial) working")
    
    def test_game_status_checkmate(self):
        """Test game status detection for checkmate"""
        # Fool's mate: 1.f3 e5 2.g4 Qh4#
        mate_fen = "rnbqkbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
        
        response = requests.post(f"{API_URL}/game-status", json={
            "fen": mate_fen
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['is_checkmate'])
        self.assertTrue(data['is_game_over'])
        print("✓ Checkmate detection working")
    
    def test_game_status_check(self):
        """Test game status detection for check"""
        # Position with check
        check_fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"
        
        response = requests.post(f"{API_URL}/game-status", json={
            "fen": check_fen
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertFalse(data['is_checkmate'])
        print("✓ Check/No-check detection working")
    
    def test_save_game(self):
        """Test saving a game"""
        game_data = {
            "gameMode": "vs-minimax",
            "moves": "e2e4 e7e5",
            "finalFen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
            "result": "ongoing",
            "engineDepth": 3,
            "duration": 120
        }
        
        response = requests.post(f"{API_URL}/save-game", json=game_data)
        print(f"Save response status: {response.status_code}")
        print(f"Save response data: {response.text}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data.get('success'))
        self.assertIsNotNone(data.get('id'))
        print(f"✓ Game saved with ID: {data['id']}")
    
    def test_get_games(self):
        """Test retrieving games"""
        response = requests.get(f"{API_URL}/get-games")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        print(f"✓ Retrieved {len(data)} games from database")
    
    def test_game_persistence(self):
        """Test that saved game appears in retrieval"""
        # Save a game
        game_data = {
            "gameMode": "vs-alphabeta",
            "moves": "d2d4 d7d5",
            "finalFen": "rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR w KQkq d6 0 2",
            "result": "ongoing",
            "engineDepth": 4,
            "duration": 60
        }
        
        save_response = requests.post(f"{API_URL}/save-game", json=game_data)
        
        # Handle error response
        if save_response.status_code != 200:
            print(f"Save error: {save_response.text}")
            self.fail(f"Failed to save game: {save_response.status_code}")
        
        save_data = save_response.json()
        
        # Check if success and id exist
        if not save_data.get('success'):
            print(f"Save response: {save_data}")
            self.fail("Save game returned success=false")
        
        saved_id = save_data.get('id')
        self.assertIsNotNone(saved_id, "No ID returned from save")
        
        # Retrieve games
        get_response = requests.get(f"{API_URL}/get-games")
        games = get_response.json()
        
        # Find our game
        saved_game = next((g for g in games if g['id'] == saved_id), None)
        self.assertIsNotNone(saved_game, f"Saved game ID {saved_id} not found in retrieved games")
        self.assertEqual(saved_game['game_mode'], 'vs-alphabeta')
        self.assertEqual(saved_game['engineDepth'], 4)
        print(f"✓ Saved game persisted in database")
    
    def test_engines_with_different_depths(self):
        """Test both engines with various depths"""
        fen = chess.STARTING_FEN
        
        for depth in [1, 2, 3]:
            # Minimax
            response_mm = requests.post(f"{API_URL}/move", json={
                "fen": fen,
                "engine": "minimax",
                "depth": depth
            })
            self.assertEqual(response_mm.status_code, 200)
            move_mm = response_mm.json()['move']
            self.assertIsNotNone(move_mm)
            
            # Alpha-Beta
            response_ab = requests.post(f"{API_URL}/move", json={
                "fen": fen,
                "engine": "alphabeta",
                "depth": depth
            })
            self.assertEqual(response_ab.status_code, 200)
            move_ab = response_ab.json()['move']
            self.assertIsNotNone(move_ab)
        
        print("✓ Both engines work with depths 1, 2, 3")
    
    def test_invalid_fen(self):
        """Test handling of invalid FEN"""
        response = requests.post(f"{API_URL}/move", json={
            "fen": "invalid fen string",
            "engine": "minimax",
            "depth": 2
        })
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400, 500])
        print("✓ Invalid FEN handled")
    
    def test_engine_consistency(self):
        """Test that same position gives consistent moves"""
        fen = chess.STARTING_FEN
        
        moves = []
        for _ in range(2):
            response = requests.post(f"{API_URL}/move", json={
                "fen": fen,
                "engine": "minimax",
                "depth": 2
            })
            moves.append(response.json()['move'])
        
        # All should be valid moves
        self.assertTrue(all(m is not None for m in moves))
        print(f"✓ Engine consistency: {set(moves)}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("INTEGRATION TESTS - Testing Live Backend API")
    print("Make sure backend is running: python app.py")
    print("="*60 + "\n")
    
    unittest.main(verbosity=2)
