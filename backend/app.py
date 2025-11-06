# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
import math
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://myuser:mypassword@localhost/chess_games')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Database Model
class GameRecord(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    date_played = Column(DateTime, default=datetime.utcnow)
    game_mode = Column(String(50), nullable=False)
    moves = Column(Text, nullable=False)
    final_fen = Column(Text, nullable=False)
    result = Column(String(50))
    engine_depth = Column(Integer)
    duration_seconds = Column(Integer)

Base.metadata.create_all(engine)

# Piece values for evaluation
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}

def evaluate_board(board):
    """Evaluate board position - positive favors white, negative favors black"""
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value
    
    white_moves = len(list(board.legal_moves))
    board.turn = chess.BLACK
    black_moves = len(list(board.legal_moves))
    board.turn = chess.WHITE
    return score + (white_moves - black_moves) * 0.1

def minimax(board, depth, maximizing_player, engine_color=chess.WHITE):
    """Minimax algorithm"""
    if depth == 0 or board.is_game_over():
        return None, evaluate_board(board)
    
    legal_moves = list(board.legal_moves)
    
    if maximizing_player:
        max_eval = -math.inf
        best_move = legal_moves[0]
        for move in legal_moves:
            board.push(move)
            _, eval_score = minimax(board, depth - 1, False, engine_color)
            board.pop()
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
        return best_move, max_eval
    else:
        min_eval = math.inf
        best_move = legal_moves[0]
        for move in legal_moves:
            board.push(move)
            _, eval_score = minimax(board, depth - 1, True, engine_color)
            board.pop()
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
        return best_move, min_eval

def alpha_beta(board, depth, alpha, beta, maximizing_player, engine_color=chess.WHITE):
    """Alpha-Beta Pruning algorithm"""
    if depth == 0 or board.is_game_over():
        return None, evaluate_board(board)
    
    legal_moves = list(board.legal_moves)
    
    if maximizing_player:
        max_eval = -math.inf
        best_move = legal_moves[0]
        for move in legal_moves:
            board.push(move)
            _, eval_score = alpha_beta(board, depth - 1, alpha, beta, False, engine_color)
            board.pop()
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return best_move, max_eval
    else:
        min_eval = math.inf
        best_move = legal_moves[0]
        for move in legal_moves:
            board.push(move)
            _, eval_score = alpha_beta(board, depth - 1, alpha, beta, True, engine_color)
            board.pop()
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return best_move, min_eval

@app.route('/api/move', methods=['POST'])
def get_move():
    """Get engine move"""
    data = request.json
    fen = data.get('fen')
    engine = data.get('engine')
    depth = data.get('depth', 4)
    
    board = chess.Board(fen)
    
    if engine == 'minimax':
        move, _ = minimax(board, depth, board.turn == chess.WHITE)
    else:
        move, _ = alpha_beta(board, depth, -math.inf, math.inf, board.turn == chess.WHITE)
    
    return jsonify({'move': move.uci() if move else None})

@app.route('/api/game-status', methods=['POST'])
def game_status():
    """Check game status"""
    data = request.json
    fen = data.get('fen')
    board = chess.Board(fen)
    
    return jsonify({
        'is_checkmate': board.is_checkmate(),
        'is_stalemate': board.is_stalemate(),
        'is_check': board.is_check(),
        'is_game_over': board.is_game_over(),
    })

@app.route('/api/save-game', methods=['POST'])
def save_game():
    """Save completed game to database"""
    try:
        data = request.json
        session = Session()
        
        game_record = GameRecord(
            game_mode=data.get('gameMode'),
            moves=data.get('moves'),
            final_fen=data.get('finalFen'),
            result=data.get('result'),
            engine_depth=data.get('engineDepth'),
            duration_seconds=data.get('duration')
        )
        
        session.add(game_record)
        session.commit()
        session.close()
        
        return jsonify({'success': True, 'id': game_record.id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get-games', methods=['GET'])
def get_games():
    """Retrieve all games from database"""
    try:
        session = Session()
        games = session.query(GameRecord).all()
        
        games_data = [{
            'id': game.id,
            'date_played': game.date_played.isoformat(),
            'game_mode': game.game_mode,
            'moves': game.moves,
            'final_fen': game.final_fen,
            'result': game.result,
            'engine_depth': game.engine_depth,
            'duration_seconds': game.duration_seconds
        } for game in games]
        
        session.close()
        return jsonify(games_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
