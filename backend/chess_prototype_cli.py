import requests
import chess

API_BASE_URL = "http://localhost:5000/api"


def request_move(fen, engine="minimax", depth=3):
    payload = {"fen": fen, "engine": engine, "depth": depth}
    response = requests.post(f"{API_BASE_URL}/move", json=payload)
    if response.ok:
        return response.json().get("move")
    else:
        print(f"API error {response.status_code}: {response.text}")
        return None


def print_board(board):
    print(board)
    print()


def engine_vs_engine(depth=2):
    print("Engine vs Engine mode")
    board = chess.Board()
    turn = 0
    while not board.is_game_over():
        engine = "alphabeta" if turn % 2 == 0 else "minimax"
        move = request_move(board.fen(), engine, depth)
        if move:
            board.push_uci(move)
            print(f"{engine} plays: {move}")
            print_board(board)
        else:
            print("No move returned by engine.")
            break
        turn += 1
    print("Game over:", board.result())


def human_vs_engine(depth=3):
    print("Choose your Engine: (alphabeta, minimax)")
    engine = input()
    print("You vs Engine mode")
    board = chess.Board()
    print_board(board)
    while not board.is_game_over():
        if board.turn == chess.WHITE:
            move = input("Your move (in UCI, e.g. e2e4): ")
            try:
                chess_move = chess.Move.from_uci(move)
                if chess_move in board.legal_moves:
                    board.push(chess_move)
                else:
                    print("Illegal move. Try again.")
                    continue
            except:
                print("Invalid move format. Try again.")
                continue
        else:
            move = request_move(board.fen(), engine, depth)
            if move:
                board.push_uci(move)
                print(f"Engine plays: {move}")
            else:
                print("Engine failed to return move.")
                break
        print_board(board)
    print("Game over:", board.result())


def human_vs_human():
    print("Human vs Human mode")
    board = chess.Board()
    print_board(board)
    while not board.is_game_over():
        move = input(f"{'White' if board.turn == chess.WHITE else 'Black'} to move (UCI): ")
        try:
            chess_move = chess.Move.from_uci(move)
            if chess_move in board.legal_moves:
                board.push(chess_move)
            else:
                print("Illegal move. Try again.")
                continue
        except:
            print("Invalid move format. Try again.")
            continue
        print_board(board)
    print("Game over:", board.result())


def main():
    print("Select mode:")
    print("1. Engine vs Engine")
    print("2. Human vs Engine")
    print("3. Human vs Human")
    choice = input("Enter 1, 2, or 3: ")
    if choice == "1":
        engine_vs_engine()
    elif choice == "2":
        human_vs_engine()
    elif choice == "3":
        human_vs_human()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
