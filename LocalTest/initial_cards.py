import random
from typing import List

from numpy.random import default_rng

from data import (
    Monster,
    MonsterType,
    Grade,
    Spell,
    SpellType,
    AttackCard,
    Deck,
    Effect,
    Actor,
    EffectType,
    StatusAlignment,
    BattleState,
)


# Monsters
def rand_monster_type() -> MonsterType:
    mon_types = list(MonsterType)
    normal_heavy = mon_types + [MonsterType.Normal] * len(mon_types) * 4
    return random.choice(normal_heavy)


def rand_grade() -> Grade:
    rand = default_rng().normal(0, 0.1)
    if rand <= -0.3:
        return Grade.E
    elif rand <= -0.1:
        return Grade.D
    elif rand <= 0.1:
        return Grade.C
    elif rand <= 0.2:
        return Grade.B
    elif rand <= 0.3:
        return Grade.A
    elif rand > 0.3:
        return Grade.S
    else:
        return random.choice(list(Grade))


all_pets = [
    Monster(name=f"Mon {i}", type=rand_monster_type(), grade=rand_grade())
    for i in range(50)
]

# spells

DoubleAttack = Spell(
    name="Double Attack",
    text="You can attack once more, if you have the needed energy",
    type=SpellType.Magic,
    energy_required=1,
    effect=Effect(
        type=EffectType.MONSTER_TAP_STATE,
        action="untap",
        actor=Actor.PLAYER,
    ),
)
EnergyBoost = Spell(
    name="Energy Boost",
    text="You can set an extra energy",
    type=SpellType.Magic,
    effect=Effect(
        type=EffectType.ENERGY,
        action="add",
        actor=Actor.PLAYER,
    ),
)
Poisoner = Spell(
    name="Poisoner",
    text="Inflict poison on one pet",
    type=SpellType.Trap,
    status_alignment=[StatusAlignment(name="Poison", effect=-0.03)],
    effect=Effect(
        type=EffectType.STATUS,
        action="add",
        actor=Actor.OPPONENT,
    ),
)
ExtraGuard = Spell(
    name="Extra Guard",
    text="plus 10 percent defense boost when blocking",
    type=SpellType.Counter,
    status_alignment=[
        StatusAlignment(
            name="Extra Guard", effect=0.1, battle_state=BattleState.DEFENDING
        )
    ],
    effect=Effect(
        type=EffectType.STATUS,
        action="add",
        actor=Actor.PLAYER,
    ),
)
Boost = Spell(
    name="Boost",
    text="pay 1 energy to increase life points by 3",
    type=SpellType.Magic,
    energy_required=1,
    impact=3,
    effect=Effect(
        type=EffectType.LIFEPOINTS,
        action="add",
        actor=Actor.PLAYER,
    ),
)
Negate = Spell(
    name="Negate",
    text="Negate a played or set card's effects and destroy it",
    type=SpellType.Counter,
    energy_required=1,
    effect=Effect(
        type=EffectType.NEGATE,
        action="destroy",
        actor=Actor.OPPONENT,
    ),
)

all_spells = [DoubleAttack, EnergyBoost, Poisoner, ExtraGuard, Negate, Boost]


def get_spell_cards_for_deck() -> List[Spell]:
    return random.choices(all_spells, k=4)


def get_monster_cards_for_deck() -> List[Monster]:
    return random.choices(all_pets, k=5)


# Attacks


def rand_weak() -> AttackCard:
    return AttackCard(
        name="weak attack",
        text="This is a weak attack",
        power=random.choice([1, 2, 3]),
        energy_required=random.choice([1, 2]),
    )


def rand_mid() -> AttackCard:
    return AttackCard(
        name="mid attack",
        text="This is a mid attack",
        power=random.choice([4, 5]),
        energy_required=random.choice([3, 4]),
    )


def rand_strong() -> AttackCard:
    return AttackCard(
        name="strong attack",
        text="This is a strong attack",
        power=random.choice([6, 7, 7, 9, 10]),
        energy_required=random.choice([6, 7, 10]),
    )


extra_strong = AttackCard(
    name="extra strong attack",
    text="This is an extra strong attack",
    power=10,
    energy_required=10,
)

all_attack_cards = (
    [rand_weak()] * 6 + [rand_mid()] * 3 + [rand_strong()] + [extra_strong]
)


def get_attack_cards_for_deck() -> List[AttackCard]:
    cards: List[AttackCard] = []
    while len(cards) < 6:
        attack_card: AttackCard = random.choice(all_attack_cards)
        if attack_card == extra_strong and extra_strong in cards:
            pass
        else:
            cards.append(attack_card)
    return cards


def get_deck() -> Deck:
    attack_cards = get_attack_cards_for_deck()
    spell_cards = get_spell_cards_for_deck()
    monster_cards = get_monster_cards_for_deck()
    return Deck(
        attack_cards=attack_cards, spell_cards=spell_cards, monster_cards=monster_cards
    )
