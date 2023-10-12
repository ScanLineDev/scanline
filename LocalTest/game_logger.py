import logging
import os
from dataclasses import dataclass
from typing import List, Any

import attrs
import requests

real_path = os.path.realpath(__file__)
dir_path = os.path.dirname(real_path)
FILENAME = f"{dir_path}/logs/game_logs.log"
FILENAME2 = f"{dir_path}/logs/board.log"


@dataclass
class BoardOutput:
    monsters: List[str]
    spells: List[str]
    lifepoints: int
    cards: int
    total_energy: int
    num_untapped_energy: int


@dataclass
class HandOutput:
    hand: List[str]


@dataclass
class PromptOutput:
    prompt: str
    options: List[Any]


@dataclass
class GameBoard:
    player1Board: BoardOutput
    player2Board: BoardOutput


def setup_logger(logger_name: str, log_file: str, mode: str, level: int = logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter("%(message)s")
    fileHandler = logging.FileHandler(log_file, mode=mode)
    fileHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)


setup_logger("game_logs", FILENAME, mode="a")
setup_logger("board_view", FILENAME2, mode="w")

game_logs = logging.getLogger("game_logs")
board_view = logging.getLogger("board_view")


@attrs.define
class GameLogger:
    _game_logs: logging.Logger = attrs.field(init=False, default=game_logs)
    _board_view: logging.Logger = attrs.field(init=False, default=board_view)

    def log(self, msg: Any, source: str = "game_logs") -> None:
        if source == "game_logs":
            self._game_logs.info(f"{msg}")
        else:
            self._board_view.info(f"{msg}")

    @staticmethod
    def make_player_board_output(player) -> BoardOutput:
        spells = player.make_spell_output()
        monsters = player.make_monster_output()
        monster_types = ["--"] * 4
        for idx, mon in enumerate(player.monsters):
            monster_types[idx] = mon.type.name
        lifepoints = player.life_points
        cards = len(player.hand)
        total_energy = player.total_energy
        num_untapped_energy = player.num_energy_untapped()
        return BoardOutput(
            monsters=monsters,
            spells=spells,
            lifepoints=lifepoints,
            cards=cards,
            total_energy=total_energy,
            num_untapped_energy=num_untapped_energy,
        )

    def emit_board(self, player1, player2) -> None:
        print("starting")
        player1board = self.make_player_board_output(player1)
        player2board = self.make_player_board_output(player2)
        board = GameBoard(player1Board=player1board, player2Board=player2board)
        print("Prep done")
        requests.post("http://127.0.0.1:8000/emit/board", json=board.dict())
        print("Done")

    @staticmethod
    def emit_hand(active_player) -> None:
        hand = HandOutput(hand=active_player.display_hand())
        requests.post("http://127.0.0.1:8000/emit/hand", json=hand.dict())

    @staticmethod
    def emit_prompt(msg, options) -> None:
        prompt = PromptOutput(prompt=msg, options=options)
        requests.post("http://127.0.0.1:8000/emit/prompt", json=prompt.dict())


game_logger = GameLogger()
