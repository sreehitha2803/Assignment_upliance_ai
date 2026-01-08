import random
from dataclasses import dataclass
from typing import Dict, Literal, Callable

Move = Literal["rock", "paper", "scissors", "bomb", "invalid"]


def tool(func: Callable) -> Callable:
    """Decorator to mark a function as a tool."""
    func.is_tool = True
    return func


class BaseAgent:
    def __init__(self, name: str):
        self.name = name


@dataclass
class GameState:
    round_number: int = 1
    user_score: int = 0
    bot_score: int = 0
    user_bomb_used: bool = False
    bot_bomb_used: bool = False
    game_over: bool = False


@tool
def validate_move(move: str, bomb_used: bool) -> Move:
    move = move.lower().strip()

    if move not in {"rock", "paper", "scissors", "bomb"}:
        return "invalid"

    if move == "bomb" and bomb_used:
        return "invalid"

    return move


@tool
def resolve_round(user_move: Move, bot_move: Move) -> str:
    if user_move == "invalid":
        return "bot"

    if user_move == bot_move:
        return "draw"

    if user_move == "bomb" and bot_move != "bomb":
        return "user"

    if bot_move == "bomb" and user_move != "bomb":
        return "bot"

    wins_against = {
        "rock": "scissors",
        "paper": "rock",
        "scissors": "paper",
    }

    return "user" if wins_against.get(user_move) == bot_move else "bot"


@tool
def update_game_state(
    state: Dict,
    winner: str,
    user_move: Move,
    bot_move: Move,
) -> Dict:
    state["round_number"] += 1

    if winner == "user":
        state["user_score"] += 1
    elif winner == "bot":
        state["bot_score"] += 1

    if user_move == "bomb":
        state["user_bomb_used"] = True

    if bot_move == "bomb":
        state["bot_bomb_used"] = True

    if state["round_number"] > 3:
        state["game_over"] = True

    return state


class GameRefereeAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="game_referee")
        self.state = GameState().__dict__

    def explain_rules(self) -> str:
        return (
            " Rock–Paper–Scissors–Plus\n"
            "• Best of 3 rounds\n"
            "• Moves: rock, paper, scissors, bomb\n"
            "• Bomb beats all (one-time use)\n"
            "• Invalid input wastes the round"
        )

    def choose_bot_move(self) -> Move:
        moves = ["rock", "paper", "scissors"]
        if not self.state["bot_bomb_used"]:
            moves.append("bomb")
        return random.choice(moves)

    def handle_turn(self, user_input: str) -> str:
        if self.state["game_over"]:
            return "The game is already over."

        user_move = validate_move(user_input, self.state["user_bomb_used"])
        bot_move = self.choose_bot_move()

        winner = resolve_round(user_move, bot_move)

        self.state = update_game_state(
            self.state, winner, user_move, bot_move
        )

        response = [
            f" Round {self.state['round_number'] - 1}",
            f" You played: {user_move}",
            f" Bot played: {bot_move}",
        ]

        if user_move == "invalid":
            response.append(" Invalid move — round wasted.")
        elif winner == "draw":
            response.append(" Draw this round.")
        elif winner == "user":
            response.append(" You win the round!")
        else:
            response.append(" Bot wins the round.")

        response.append(
            f" Score — You: {self.state['user_score']} | Bot: {self.state['bot_score']}"
        )

        if self.state["game_over"]:
            response.append(self.final_result())
        else:
            response.append("➡️ Your next move?")

        return "\n".join(response)

    def final_result(self) -> str:
        if self.state["user_score"] > self.state["bot_score"]:
            return " Final Result: You win the game!"
        elif self.state["bot_score"] > self.state["user_score"]:
            return " Final Result: Bot wins the game!"
        return " Final Result: It's a draw!"



if __name__ == "__main__":
    agent = GameRefereeAgent()
    print(agent.explain_rules())

    while not agent.state["game_over"]:
        user_input = input("\nYour move: ")
        print(agent.handle_turn(user_input))
