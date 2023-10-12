from __future__ import annotations

from enum import Enum
from typing import Optional, Tuple, Dict

import attrs
from prettytable import PrettyTable

from data import Board, Opponent, Spell, SpellType, Deck
from game_logger import GameLogger, game_logger
from initial_cards import get_deck

logger: GameLogger = game_logger

YESNO = ["Yes", "No"]
INDEXOP = [0, 1, 2, 3]
HANDINDEX = [0, 1, 2, 3, 4, 5, 6]


class Source(str, Enum):
    Hand = "in hand"
    Monsters = "on monster field"
    Spells = "on spell field"


@attrs.define
class Phases:
    def setup_phases(self, player: Board, other_player: Board) -> Tuple[Board, Board]:
        player.reset_energies()
        player.reset_monsters_to_idle()
        player = self.draw_phase(player)
        logger.emit_hand(player)
        player, other_player = self.counter_phases(player, other_player)
        player = self.set_energy_phase(player)
        logger.emit_hand(player)
        player = self.set_monster_phase(player)
        logger.emit_hand(player)
        player = self.set_spell_phase(player)
        logger.emit_hand(player)
        player = self.equip_attack_card_phase(player)
        logger.emit_hand(player)
        return player, other_player

    def action_phases(self, player: Board, other_player: Board) -> Tuple[Board, Board]:
        in_play = True
        while in_play:
            self.display(Source.Hand, player)
            msg = "Do you want to take an action?: (y/n)"
            logger.emit_prompt(msg=msg, options=YESNO)
            choice = input(msg)
            if choice == "y":
                player, other_player = self.attack_phase(player, other_player)
                player, other_player = self.counter_phases(player, other_player)
                player, other_player = self.activate_spells_phase(player, other_player)
                player, other_player = self.counter_phases(player, other_player)
            else:
                player, other_player = self.counter_phases(player, other_player)
                in_play = False
        return player, other_player

    def counter_phases(self, player: Board, other_player: Board) -> Tuple[Board, Board]:
        # opponent first
        player, other_player = self.counter_phase(
            player, countering=other_player, name="Opponent"
        )
        # player can retaliate
        other_player, player = self.counter_phase(
            other_player, countering=player, name="Player"
        )
        return player, other_player

    def counter_phase(
        self, player: Board, countering: Board, name: str
    ) -> Tuple[Board, Board]:
        in_play = True
        while in_play:
            counter = countering.can_counter_from()
            if not counter:
                return player, countering
            logger.emit_hand(countering)
            print(f"\n {name} can counter from {counter}")
            logger.log(f"{name} can counter from {counter}")
            for p in counter:
                s = Source.Hand if p == "hand" else Source.Spells
                print(f"counter(s) {s}")
                logger.log(f"counter(s) {s}")
                self.display(s, countering, counters=True)
            msg = "Do you want to play a counter? (y/n)"
            logger.emit_prompt(msg=msg, options=YESNO)
            choice = input(msg)
            if choice == "y":
                if "hand" in counter:
                    msg = "Do you want to play a counter from hand? (y/n)"
                    logger.emit_prompt(msg=msg, options=YESNO)
                    choice = input(msg)
                    if choice == "y":
                        self.display(Source.Hand, countering, counters=True)
                        msg = "Choose the corresponding index for the spell you want to use?"
                        logger.emit_prompt(msg=msg, options=HANDINDEX)
                        spell_idx = input(msg)
                        selected_spell = countering.hand[int(spell_idx)]
                        countering, player = selected_spell.activate(countering, player)
                        self.display(Source.Hand, countering, counters=True)
                        try:
                            countering.hand.pop(int(spell_idx))
                        except IndexError:
                            print(f"spell idx = {spell_idx}")
                            logger.log(f"spell idx = {spell_idx}")
                            print(f"len spells = {len(countering.hand)}")
                            logger.log(f"len spells = {len(countering.hand)}")
                if "field" in counter:
                    msg = "Do you want to play a counter from field? (y/n)"
                    logger.emit_prompt(msg=msg, options=YESNO)
                    choice = input(msg)
                    if choice == "y":
                        self.display(Source.Spells, countering, counters=True)
                        msg = "Choose the corresponding index for the spell you want to use?"
                        logger.emit_prompt(msg=msg, options=INDEXOP)
                        spell_idx = input(msg)
                        selected_spell = countering.spells[int(spell_idx)]
                        countering, player = selected_spell.activate(countering, player)
                        self.display(Source.Spells, countering, counters=True)
                        try:
                            countering.spells.pop(int(spell_idx))
                        except IndexError:
                            print(f"spell idx = {spell_idx}")
                            logger.log(f"spell idx = {spell_idx}")
                            print(f"len spells = {len(countering.spells)}")
                            logger.log(f"len spells = {len(countering.spells)}")
            else:
                in_play = False
        print("Counter turn end")
        logger.log("Counter turn end")
        return player, countering

    def draw_phase(self, player: Board) -> Board:
        print("Draw phase")
        logger.log("Draw phase")
        draw = player.deck.draw()
        player.hand.append(draw)
        self.display(Source.Hand, player)
        if len(player.hand) > 7:
            msg = "You have too many cards, choose the idx of a card to discard"
            print(msg)
            logger.log(msg)
            logger.emit_prompt(msg=msg, options=[i for i in range(len(player.hand))])
            idx = input(msg)
            player.hand.pop(int(idx))
            self.display(Source.Hand, player)
        player.untap_monsters()
        return player

    @staticmethod
    def set_energy_phase(player: Board) -> Board:
        msg = "Do you want to set and energy card?: (y/n)"
        logger.emit_prompt(msg=msg, options=YESNO)
        choice = input(msg)
        if choice == "y":
            msg = "Choose the index of the card in your hand to set"
            logger.emit_prompt(msg=msg, options=HANDINDEX)
            idx = input(msg)
            energy = player.hand.pop(int(idx))
            player.set_energy(energy)
        return player

    def set_monster_phase(self, player: Board) -> Board:
        while len(player.monsters) <= 3:
            self.display(Source.Hand, player)
            msg = "Do you want to set a monster card?: (y/n)"
            logger.emit_prompt(msg=msg, options=YESNO)
            choice = input(msg)
            if choice == "y":
                msg = "Choose the index of the card in your hand to set"
                logger.emit_prompt(msg=msg, options=HANDINDEX)
                idx = input(msg)
                monster = player.hand.pop(int(idx))
                player.monsters.append(monster)
            else:
                break
        return player

    def set_spell_phase(self, player: Board) -> Board:
        while len(player.spells) <= 4:
            self.display(Source.Hand, player)
            msg = "Do you want to set any spell card?: (y/n)"
            logger.emit_prompt(msg=msg, options=YESNO)
            choice = input(msg)
            if choice == "y":
                msg = "Choose the index of the card in your hand to set"
                logger.emit_prompt(msg=msg, options=HANDINDEX)
                idx = input(msg)
                spell = player.hand.pop(int(idx))
                spell.tap()
                player.spells.append(spell)
            else:
                break
        return player

    def equip_attack_card_phase(self, player: Board) -> Board:
        while len(player.hand) > 0:
            self.display(Source.Hand, player)
            msg = "Do you want to play any attack cards?: (y/n)"
            logger.emit_prompt(msg=msg, options=YESNO)
            choice = input(msg)
            if choice == "y":
                msg = "Choose the index of the card in your hand to play"
                logger.emit_prompt(msg=msg, options=HANDINDEX)
                attk_idx = input(msg)
                attack = player.hand.pop(int(attk_idx))
                self.display(Source.Monsters, player)

                ready = False
                while not ready:
                    msg = "Choose the index of the monster card on the field to equip"
                    logger.emit_prompt(msg=msg, options=INDEXOP)
                    mon_idx = input(msg)
                    selected_monster = player.monsters[int(mon_idx)]
                    if len(selected_monster.equipped) == 2:
                        print("Can't equip any more attacks to this monster")
                        logger.log("Can't equip any more attacks to this monster")
                        player.hand.append(attack)
                        break
                    else:
                        player.monsters[int(mon_idx)].equipped.append(attack)
                        ready = True
            else:
                break
        return player

    def activate_spells_phase(
        self, player: Board, other_player: Board
    ) -> Tuple[Board, Board]:
        while len(player.spells) > 0:
            msg = "Do you want to activate any spell cards?: (y/n)"
            logger.emit_prompt(msg=msg, options=YESNO)
            choice = input(msg)
            if choice == "y":
                self.display(Source.Spells, player)
                msg = "Choose the corresponding index for the spell you want to use?"
                logger.emit_prompt(msg=msg, options=INDEXOP)
                spell_idx = input(msg)
                selected_spell = player.spells[int(spell_idx)]
                player, other_player = selected_spell.activate(player, other_player)
                self.display(Source.Spells, player)
                try:
                    player.spells.pop(int(spell_idx))
                except IndexError:
                    print(f"spell idx = {spell_idx}")
                    logger.log(f"spell idx = {spell_idx}")
                    print(f"len spells = {len(player.spells)}")
                    logger.log(f"len spells = {len(player.spells)}")
            else:
                break
        return player, other_player

    def attack_phase(self, player: Board, other_player: Board) -> Tuple[Board, Board]:
        max_possible_attacks = player.attack_ready()
        while max_possible_attacks > 0:
            msg = f"You have {max_possible_attacks} attacks available. Do you want to attack with any monsters?: (y/n)"
            logger.emit_prompt(msg=msg, options=YESNO)
            choice = input(msg)
            if choice == "y":
                self.display(Source.Monsters, player, untapped=True)
                msg = "Choose the index of monster card on the field to attack with"
                logger.emit_prompt(msg=msg, options=INDEXOP)
                mon_idx = input(msg)
                selected_monster = player.monsters[int(mon_idx)]
                print("Here are this monsters attacks")
                logger.log("Here are this monsters attacks")
                print(selected_monster.get_attacks)
                msg = "Choose the index for the attack you want to use"
                logger.emit_prompt(msg=msg, options=INDEXOP)
                attk_idx = input(msg)
                attack = selected_monster.equipped[int(attk_idx)]
                if not player.pay_energy(attack.energy_required):
                    print("you do not have enough energy for that attack")
                    logger.log("you do not have enough energy for that attack")
                else:
                    direct = True
                    selected_monster.to_attack_state()
                    opponent_one = selected_monster.make_opponent(attack, player)
                    if other_player.can_defend:
                        self.display(
                            Source.Monsters, player, other_player, untapped=True
                        )
                        msg = (
                            "Player 2, do you want to defend with any monsters?: (y/n)"
                        )
                        logger.emit_prompt(msg=msg, options=YESNO)
                        choice = input(msg)
                        if choice == "y":
                            msg = "Player two choose the index of the monster to defend with"
                            logger.emit_prompt(msg=msg, options=INDEXOP)
                            p2_mon_idx = input(msg)
                            selected_defender = other_player.monsters[int(p2_mon_idx)]
                            defend = None
                            if selected_defender.equipped:
                                print("Here are your monster's attacks")
                                logger.log("Here are your monster's attacks")
                                print(selected_defender.get_attacks)
                                logger.log(selected_defender.get_attacks)
                                use_equip = input(
                                    "Do you want to defend with an attack card? (y/n)"
                                )
                                if use_equip == "y":
                                    msg = "Choose the index for the attack you want to use to defend"
                                    logger.emit_prompt(msg=msg, options=INDEXOP)
                                    def_idx = input(msg)
                                    defend = selected_defender.equipped[int(def_idx)]
                            if not defend or (
                                defend
                                and other_player.pay_energy(defend.energy_required)
                            ):
                                selected_defender.to_defense_state()
                                opponent_two = selected_defender.make_opponent(
                                    defend, other_player
                                )
                                player, other_player = self.battle(
                                    opponent_one, opponent_two
                                )
                                selected_monster.tap()
                                selected_defender.tap()
                                direct = False
                    if direct:
                        attack_power = opponent_one.attack_power()
                        print("Direct attack")
                        logger.log("Direct attack")
                        print(f"Damage inflicted = {attack_power}")
                        logger.log(f"Damage inflicted = {attack_power}")
                        other_player.life_points -= attack_power
                        selected_monster.tap()
                    max_possible_attacks -= 1
            else:
                break
        return player, other_player

    @staticmethod
    def battle(opponent_one: Opponent, opponent_two: Opponent) -> Tuple[Board, Board]:
        attack_power = opponent_one.attack_power(opponent_two.monster.type)
        defense_power = opponent_two.def_power(opponent_one.monster.type)
        delta = abs(attack_power - defense_power)
        if attack_power == defense_power:
            print(f"Attack cancelled out, no damage inflicted")
            logger.log(f"Attack cancelled out, no damage inflicted")
        elif attack_power > defense_power:
            opponent_two.board.life_points -= delta
            print(f"Player 2, damage inflicted = -{delta}")
            logger.log(f"Player 2, damage inflicted = -{delta}")
        else:
            opponent_one.board.life_points -= delta
            print(f"Player 1, damage inflicted = -{delta}")
            logger.log(f"Player 1, damage inflicted = -{delta}")
        return opponent_one.board, opponent_two.board

    def display(
        self,
        source: Source,
        player: Board,
        other_player: Optional[Board] = None,
        untapped: bool = False,
        counters: bool = False,
    ) -> None:
        if source == Source.Hand:
            self.hand(player, counters)
        elif source == Source.Monsters:
            self.monsters_on_field(player, other_player, untapped)
        else:
            self.spells_on_field(player, counters)

    @staticmethod
    def hand(player: Board, counters: bool):
        print("Here is your hand: \n")
        logger.log("Here is your hand: \n")
        if counters:
            for idx, card in enumerate(player.hand):
                line = (
                    f"{idx}__{card.view()} \n"
                    if isinstance(card, Spell) and card.type == SpellType.Counter
                    else None
                )
                if line:
                    print(line)
                    logger.log(line)
        else:
            for idx, card in enumerate(player.display_hand()):
                line = f"{idx}__{card}"
                if line:
                    print(line)
                    logger.log(line)

    @staticmethod
    def monsters_on_field(player: Board, other_player: Optional[Board], untapped: bool):
        msg = (
            "Current monsters on your opponents field: \n"
            if other_player
            else "Current monsters on the field: \n"
        )
        player_mons = other_player.monsters if other_player else player.monsters
        print(msg)
        logger.log(msg)
        for idx, mons in enumerate(player_mons):
            if untapped:
                line = f"{idx}__{mons.view()} \n" if mons.is_untapped else None
            else:
                line = f"{idx}__{mons.view()}"
            if line:
                print(line)
                logger.log(line)

    @staticmethod
    def spells_on_field(player: Board, counters: bool):
        print("Current spells on the field: \n")
        logger.log("Current spells on the field: \n")
        for idx, spell in enumerate(player.spells):
            if counters:
                line = (
                    f"{idx}__{spell.view()} \n"
                    if spell.type == SpellType.Counter
                    else None
                )
            else:
                line = f"{idx}__{spell.view()}"
            if line:
                print(line)
                logger.log(line)


@attrs.define
class Game:
    players: Dict[str, Board]
    phases: Phases = Phases()
    turn: int = attrs.field(init=False, default=0)

    def display_player_boards(self) -> str:
        player1 = self.players["player_1"]
        player2 = self.players["player_2"]
        x = PrettyTable()
        p1_spells_output = player1.make_spell_output()
        p1_monster_output = player1.make_monster_output()
        p2_spells_output = player2.make_spell_output()
        p2_monster_output = player2.make_monster_output()
        x.field_names = ["Name", "index_0", "index_1", "index_2", "index_3"]
        x.add_rows(
            [
                ["Opponent", "", "", "", ""],
                ["Cards in hand", len(player2.hand), "", "", ""],
                ["Life points", player2.life_points, "", "", ""],
                [
                    "Total Energy",
                    player2.total_energy,
                    "",
                    "Num_untapped",
                    player2.num_energy_untapped(),
                ],
                [
                    "Spells",
                    p2_spells_output[0],
                    p2_spells_output[1],
                    p2_spells_output[2],
                    p2_spells_output[3],
                ],
                [
                    "Monsters",
                    p2_monster_output[0],
                    p2_monster_output[1],
                    p2_monster_output[2],
                    p2_monster_output[3],
                ],
                ["", "", "", "", ""],
                ["", "", "", "", ""],
                [
                    "Monsters",
                    p1_monster_output[0],
                    p1_monster_output[1],
                    p1_monster_output[2],
                    p1_monster_output[3],
                ],
                [
                    "Spells",
                    p1_spells_output[0],
                    p1_spells_output[1],
                    p1_spells_output[2],
                    p1_spells_output[3],
                ],
                [
                    "Total Energy",
                    player1.total_energy,
                    "",
                    "Num_untapped",
                    player1.num_energy_untapped(),
                ],
                ["Life points", player1.life_points, "", "", ""],
                ["Cards in hand", len(player1.hand), "", "", ""],
                ["Player", "", "", "", ""],
            ]
        )
        x.align["Name"] = "l"
        return x.get_string()

    def which_player(self, player: Board) -> str:
        key_list = list(self.players.keys())
        val_list = list(self.players.values())
        position = val_list.index(player)
        return key_list[position]

    def other_player(self, player_name: str) -> Board:
        other_player = []
        for name, player in self.players.items():
            if player_name == name:
                continue
            else:
                other_player.append(player)
        return other_player[0]

    @property
    def first_turn(self) -> bool:
        return self.turn == 0

    def next_turn(self) -> None:
        self.turn += 1

    @property
    def both_players_alive(self) -> bool:
        return bool(
            self.players["player_1"].life_points > 0
            and self.players["player_2"].life_points > 0
        )

    def print_winner(self):
        winner = (
            self.players["player_1"]
            if self.players["player_1"].life_points > 0
            else self.players["player_2"]
        )
        print(f"{self.which_player(winner)} wins!")
        logger.log(f"{self.which_player(winner)} wins!")

    def play(self):
        while self.both_players_alive:
            for player_name, active_player in self.players.items():
                msg = f"{player_name} it's your turn!"
                print(msg)
                logger.log(msg)

                opponent = self.other_player(player_name)
                logger.emit_board(active_player, opponent)
                print(self.display_player_boards())

                active_player, opponent = self.phases.setup_phases(
                    active_player, opponent
                )
                print(self.display_player_boards())
                logger.emit_board(active_player, opponent)
                logger.log(self.display_player_boards(), source="board_view")

                # action phase
                if not self.first_turn:
                    print("Action Phase!")
                    logger.log("Action Phase!")
                    active_player, opponent = self.phases.action_phases(
                        active_player, opponent
                    )
                    print(self.which_player(active_player))
                    logger.log(self.which_player(active_player))
                    print("\n")
                    logger.log(self.display_player_boards(), source="board_view")

                if not self.both_players_alive:
                    break

                print("\n")
                print("Turn end")
                logger.log("Turn end")
                self.next_turn()
        self.print_winner()

    def test_play(self):
        for i in range(0, 10):
            active_player = self.players["player_1"]
            opponent = self.players["player_2"]
            print(active_player)
            print(opponent)
            logger.emit_board(active_player, opponent)


def player_swap(player1: Board, player2: Board) -> Tuple[Board, Board]:
    temp = player2
    player2 = player1
    player1 = temp
    return player1, player2


def set_up_players() -> Dict[str, Board]:
    player_one_deck: Deck = get_deck()
    player_two_deck: Deck = get_deck()

    player_one_hand = player_one_deck.starting_hand()
    player_two_hand = player_two_deck.starting_hand()

    player_one_board = Board(deck=player_one_deck, hand=player_one_hand)
    player_two_board = Board(deck=player_two_deck, hand=player_two_hand)

    return {"player_1": player_one_board, "player_2": player_two_board}
