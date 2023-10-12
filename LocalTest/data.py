from __future__ import annotations

import itertools
import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any, Callable, Optional, Union

import attrs

from game_logger import GameLogger, game_logger

DEFAULT_LIFE_POINTS = 10
DEFAULT_AFFINITY_VALUE = 0.1

logger: GameLogger = game_logger


class Grade(int, Enum):
    E = 0
    D = 1
    C = 2
    B = 3
    A = 4
    S = 5


class MonsterType(str, Enum):
    Fire = "Fire"
    Water = "Water"
    Electric = "Electric"
    Grass = "Grass"
    Ground = "Ground"
    Normal = "Normal"
    Flying = "Flying"
    Dark = "Dark"
    Light = "Light"


type_affinity: Dict[MonsterType, Dict[str, List[MonsterType]]] = {
    MonsterType.Fire: {"plus": [MonsterType.Grass], "neg": [MonsterType.Water]},
    MonsterType.Water: {"plus": [MonsterType.Fire], "neg": [MonsterType.Grass]},
    MonsterType.Electric: {
        "plus": [MonsterType.Water],
        "neg": [MonsterType.Ground, MonsterType.Grass],
    },
    MonsterType.Grass: {"plus": [MonsterType.Water], "neg": [MonsterType.Fire]},
    MonsterType.Ground: {
        "plus": [MonsterType.Electric],
        "neg": [MonsterType.Water, MonsterType.Grass],
    },
    MonsterType.Normal: {"plus": [], "neg": [MonsterType.Dark, MonsterType.Light]},
    MonsterType.Flying: {
        "plus": [MonsterType.Ground],
        "neg": [MonsterType.Water, MonsterType.Electric],
    },
    MonsterType.Dark: {"plus": [MonsterType.Normal], "neg": [MonsterType.Light]},
    MonsterType.Light: {"plus": [MonsterType.Normal], "neg": [MonsterType.Dark]},
}


class SpellType(str, Enum):
    Magic = "magic"
    Trap = "trap"
    Counter = "counter"


class EffectType(str, Enum):
    MONSTER_TAP_STATE = "monster_tap"
    ENERGY = "energy"
    STATUS = "status"
    NEGATE = "negate"
    LIFEPOINTS = "life points"


class BattleState(str, Enum):
    ATTACKING = "attack"
    DEFENDING = "defense"
    IDLE = "idle"


class Actor(str, Enum):
    PLAYER = "player"
    OPPONENT = "opponent"


MONSTER_IMPACTS = [EffectType.MONSTER_TAP_STATE, EffectType.STATUS]


@attrs.define
class Card(ABC):
    name: str
    tapped: bool = attrs.field(init=False, default=False)

    def tap(self):
        self.tapped = True

    def untap(self):
        self.tapped = False

    @property
    def is_untapped(self) -> bool:
        return not self.tapped

    @property
    def state(self) -> str:
        return "untapped" if self.is_untapped else "tapped"

    @abstractmethod
    def view(self) -> str:
        """The way the card should be shown to the user on the board"""
        raise NotImplementedError


@attrs.define
class Energy(Card):
    value: int = attrs.field(init=False, default=1)

    def view(self) -> str:
        return f"Energy 1 {self.state}"


@attrs.define
class AttackCard(Card):
    text: str
    power: int
    energy_required: int

    def view(self) -> str:
        return f"{self.name}: str:{self.power} cost:{self.energy_required}"


@attrs.define
class StatusAlignment(Card):
    effect: float
    turn_limit: Optional[int] = None
    battle_state: Optional[BattleState] = None

    def view(self) -> str:
        view = f"{self.name}: effect:{self.effect:.0%}"
        if self.turn_limit:
            view += f", turns: {self.turn_limit}"
        if self.battle_state:
            view += f", position: {self.battle_state}"
        return view


@attrs.define
class Turn:
    name: str
    count: int
    turn_limit: int

    @staticmethod
    def impact(status: StatusAlignment) -> float:
        return status.effect


@attrs.define
class Monster(Card):
    type: MonsterType
    grade: Grade
    buffs: List[StatusAlignment] = attrs.field(init=False, factory=list)
    equipped: List[AttackCard] = attrs.field(init=False, factory=list)
    battle_state: BattleState = attrs.field(init=False, default=BattleState.IDLE)

    def make_opponent(self, attack: Optional[AttackCard], board: Board) -> Opponent:
        return Opponent(monster=self, attack=attack, board=board)

    def to_attack_state(self):
        self.battle_state = BattleState.ATTACKING

    def to_defense_state(self):
        self.battle_state = BattleState.DEFENDING

    def to_idle_state(self):
        self.battle_state = BattleState.IDLE

    @property
    def get_buff_names(self) -> Optional[str]:
        out = []
        for i in self.buffs:
            out.append(i.view())
        return " ,".join(out) if out else None

    @property
    def get_attacks(self) -> Optional[str]:
        out = []
        for idx, i in enumerate(self.equipped):
            out.append(i.view())
        return " ,".join(out) if out else None

    def view(self) -> str:
        buffs = self.get_buff_names
        attks = self.get_attacks
        view = f"{self.name} ({self.type} / {self.grade.name}), {self.state}"
        if attks:
            view += f", attks:{attks}"
        if buffs:
            view += f", buffs:{buffs}"
        return view


class NegateEffect:
    @staticmethod
    def activate(action: str, spell: Spell, player: Board) -> Board:
        spell.negated = True
        if action == "destroy":
            player.spells.remove(spell)
        return player


@attrs.define
class MonsterTapEffect:
    @staticmethod
    def activate(action: str, monster: Monster) -> None:
        if action == "tap":
            monster.tap()
        else:
            monster.untap()


@attrs.define
class StatusEffect:
    @staticmethod
    def activate(action: str, monster: Monster, buffs: List[StatusAlignment]) -> None:
        if action == "add":
            monster.buffs.extend(buffs)
        else:
            monster.buffs.pop()


@attrs.define
class EnergyEffect:
    @staticmethod
    def activate(action: str, player: Board) -> Board:
        if action == "add":
            print("Here is your hand: \n")
            logger.log("Here is your hand: \n")
            for idx, card in enumerate(player.hand):
                line = f"{idx}__{card} \n"
                print(line)
                logger.log(line)

            idx = input("Choose the index of the card in your hand to set")
            energy = player.hand.pop(int(idx))
            player.set_energy(energy)
        else:
            player.energy.pop()
            player.total_energy -= 1
        return player


@attrs.define
class LifePointsEffect:
    @staticmethod
    def activate(action: str, player: Board, impact: int = 0) -> Board:
        if action == "add":
            player.life_points += impact
        else:
            player.life_points -= impact
        return player


EFFECT_TYPE_TO_FUNC: Dict[EffectType, Callable] = {
    EffectType.MONSTER_TAP_STATE: MonsterTapEffect.activate,
    EffectType.ENERGY: EnergyEffect.activate,
    EffectType.STATUS: StatusEffect.activate,
    EffectType.NEGATE: NegateEffect.activate,
    EffectType.LIFEPOINTS: LifePointsEffect.activate,
}


@attrs.define
class Effect:
    type: EffectType
    action: str
    actor: Actor
    type_to_func: Dict[EffectType, Callable] = attrs.field(
        init=False, default=EFFECT_TYPE_TO_FUNC
    )

    def activate(self, *args, **kwargs) -> Any:
        return self.type_to_func[self.type](action=self.action, *args, **kwargs)


@attrs.define
class Spell(Card):
    text: str
    type: SpellType
    effect: Effect
    impact: float = attrs.field(default=0)
    energy_required: int = attrs.field(default=0)
    status_alignment: List[StatusAlignment] = attrs.field(factory=list)
    negated: bool = attrs.field(init=False, default=False)

    def activate(self, player: Board, other_player: Board):
        if self.negated:
            print("Effect negated")
            logger.log("Effect negated")
            return player, other_player

        actor = player if self.effect.actor == Actor.PLAYER else other_player
        other = other_player if self.effect.actor == Actor.PLAYER else player
        if player.pay_energy(self.energy_required):
            if self.effect.type in MONSTER_IMPACTS:
                print("Current monsters on the field: \n")
                logger.log("Current monsters on the field: \n")
                for idx, card in enumerate(actor.monsters):
                    line = f"{idx}__{card} \n"
                    print(line)
                    logger.log(line)

                mon_idx = input("Choose the index of monster card on the field")
                selected_monster = actor.monsters[int(mon_idx)]
                if self.effect.type == EffectType.MONSTER_TAP_STATE:
                    self.effect.activate(monster=selected_monster)
                elif self.effect.type == EffectType.STATUS:
                    self.effect.activate(
                        monster=selected_monster, buffs=self.status_alignment
                    )
                else:
                    print("Nothing happened")
                    logger.log("Nothing happened")
            elif self.effect.type == EffectType.ENERGY:
                actor = self.effect.activate(player=actor)
            elif self.effect.type == EffectType.NEGATE:
                print("Current spells on the field: \n")
                logger.log("Current spells on the field: \n")
                for idx, card in enumerate(actor.spells):
                    line = f"{idx}__{card} \n"
                    print(line)
                    logger.log(line)

                spell_idx = input(
                    "Choose the corresponding index for the spell you want to negate?"
                )
                selected_spell = actor.spells[int(spell_idx)]
                actor = self.effect.activate(spell=selected_spell, player=actor)
            elif self.effect.type == EffectType.LIFEPOINTS:
                actor = self.effect.activate(player=actor, impact=int(self.impact))
            else:
                print("Nothing happened")
                logger.log("Nothing happened")
        else:
            print("Not enough energy to play this card")
            logger.log("Not enough energy to play this card")
        return actor, other

    @property
    def get_alignment_names(self) -> Optional[str]:
        out = []
        for i in self.status_alignment:
            out.append(i.view())
        return ", ".join(out) if out else None

    def view(self) -> str:
        impact = self.impact if self.impact > 0 else None
        energy_required = self.energy_required if self.energy_required > 0 else None
        alignments = self.get_alignment_names
        view = "NEGATED " if self.negated else ""
        view += f"{self.name} ({self.type.name} / {self.effect.type.name}) {self.state}"
        if energy_required:
            view += f", cost: {energy_required}"
        if impact:
            if impact > 1:
                view += f", impact: {impact}"
            else:
                view += f", impact: {impact:.0%}"
        if alignments:
            view += f", alignments: {alignments}"
        return view


@attrs.define
class Opponent:
    monster: Monster
    attack: Optional[AttackCard]
    board: Board

    def _base_power(self) -> int:
        grade_val = self.monster.grade
        attack_from_equip = self.attack.power if self.attack else 0
        return attack_from_equip + int(grade_val)

    def _buff_debuff_impact(self, base_power: int) -> float:
        buff_debuff: float = 0
        for bd in self.monster.buffs:
            if bd.battle_state and self.monster.battle_state != bd.battle_state:
                print(f"Buff not applied {bd.name}, pet not in correct state")
                logger.log(f"Buff not applied {bd.name}, pet not in correct state")
            else:
                print("Buff impact of {:.1%}".format(bd.effect))
                logger.log("Buff impact of {:.1%}".format(bd.effect))
                buff_debuff += bd.effect
        return base_power * buff_debuff

    def attack_power(self, opponent_type: Optional[MonsterType] = None) -> int:
        affinity_impact = 0
        base_power = self._base_power()
        buff_debuff_impact = self._buff_debuff_impact(base_power)
        if opponent_type:
            affinity: float = (
                DEFAULT_AFFINITY_VALUE
                if opponent_type in type_affinity[self.monster.type]["plus"]
                else 0
            )
            if affinity > 0:
                print("affinity impact of {:.1%}".format(affinity))
                logger.log("affinity impact of {:.1%}".format(affinity))
            affinity_impact = base_power * affinity
        return round(base_power + affinity_impact + buff_debuff_impact)

    def def_power(self, opponent_type: MonsterType):
        base_power = self._base_power()
        buff_debuff_impact = self._buff_debuff_impact(base_power)
        affinity: float = (
            -DEFAULT_AFFINITY_VALUE
            if opponent_type in type_affinity[self.monster.type]["neg"]
            else 0
        )
        affinity_impact = base_power * affinity
        return round(base_power + affinity_impact + buff_debuff_impact)


@attrs.define
class Deck:
    attack_cards: List[AttackCard]
    spell_cards: List[Spell]
    monster_cards: List[Monster]
    energy_cards: List[Energy] = attrs.field(
        init=False, default=[Energy(name="Energy")] * 15
    )
    all_cards: List[Union[AttackCard, Spell, Monster, Energy]] = attrs.field(
        init=False, factory=list
    )

    def __attrs_post_init__(self):
        all_cards = list(
            itertools.chain(
                self.attack_cards,
                self.spell_cards,
                self.energy_cards,
                self.monster_cards,
            )
        )
        random.shuffle(all_cards)
        self.all_cards = all_cards

    def starting_hand(self) -> List[Union[AttackCard, Spell, Monster, Energy]]:
        hand = []
        while len(hand) < 6:
            if len(hand) == 5 and not self.monster_in_hand(hand):
                for idx, i in enumerate(self.all_cards):
                    if isinstance(i, Monster):
                        hand.append(self.all_cards.pop(idx))
                        break
            else:
                hand.append(self.all_cards.pop())
        return hand

    @staticmethod
    def monster_in_hand(cards: List[Any]) -> bool:
        for i in cards:
            if isinstance(i, Monster):
                return True
        return False

    def draw(self) -> Any:
        try:
            return self.all_cards.pop()
        except IndexError:
            print("No more cards")
            logger.log("No more cards")
            return None


@attrs.define
class Board:
    deck: Deck
    hand: List[Union[AttackCard, Spell, Monster, Energy]]
    total_energy: int = attrs.field(init=False, default=0)
    energy: List[Energy] = attrs.field(init=False, factory=list)
    monsters: List[Monster] = attrs.field(init=False, factory=list)
    spells: List[Spell] = attrs.field(init=False, factory=list)
    life_points: int = attrs.field(init=False, default=DEFAULT_LIFE_POINTS)
    turn: int = attrs.field(init=False, default=0)

    def reset_energies(self) -> None:
        if self.energy:
            print("resetting energy")
            logger.log("No more cards")
            for e in self.energy:
                e.untap()
            self.total_energy = len(self.energy)

    def reset_monsters_to_idle(self) -> None:
        for monster in self.monsters:
            monster.to_idle_state()

    def pay_energy(self, cost: int) -> bool:
        tapped = []
        print(
            f"total_energy={self.total_energy}, energies={len(self.energy)}, cost={cost}"
        )
        logger.log(
            f"total_energy={self.total_energy}, energies={len(self.energy)}, cost={cost}"
        )
        if self.total_energy < cost or len(self.energy) < cost:
            print("You do not have enough energy to play this card")
            logger.log("You do not have enough energy to play this card")
            return False

        print(self.energy)
        logger.log(self.energy)
        for e in self.energy:
            if not e.tapped:
                tapped.append(e)
                if len(tapped) == cost:
                    self.total_energy -= cost
                    for en in tapped:
                        en.tap()
                    print(f"total_energy={self.total_energy}")
                    logger.log(f"total_energy={self.total_energy}")
                    return True

        print("You do not have enough energy to play this card")
        logger.log("You do not have enough energy to play this card")
        return False

    def set_energy(self, energy: Energy) -> None:
        self.energy.append(energy)
        self.total_energy += energy.value

    def attack_ready(self) -> int:
        count = 0
        for m in self.monsters:
            if m.is_untapped and m.equipped:
                count += 1
        return count

    @property
    def can_defend(self) -> bool:
        return bool(len(self.monsters) > 0 and self.attack_ready() > 0)

    def untap_monsters(self) -> None:
        for m in self.monsters:
            m.untap()

    def can_counter_from(self) -> List[str]:
        counter_from = []
        for spell in self.spells:
            if spell.type == SpellType.Counter:
                counter_from.append("field")
                break
        for card in self.hand:
            if isinstance(card, Spell) and card.type == SpellType.Counter:
                counter_from.append("hand")
                break
        return counter_from

    def make_spell_output(self) -> List[str]:
        out = [""] * 4
        for idx, i in enumerate(self.spells):
            out[idx] = i.view()
        return out

    def make_monster_output(self) -> List[str]:
        out = [""] * 4
        for idx, i in enumerate(self.monsters):
            out[idx] = i.view()
        return out

    def num_energy_untapped(self):
        count = 0
        for e in self.energy:
            if not e.tapped:
                count += 1
        return count

    def display_hand(self) -> List[str]:
        out = []
        for i in self.hand:
            out.append(i.view())
        return out
