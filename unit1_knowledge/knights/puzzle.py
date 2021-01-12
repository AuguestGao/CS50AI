from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # Base game rule, knight XOR knave
    And(Or(AKnight, AKnave), Not(And(AKnight, AKnave))),
    
    # A tells a truth -> AKnight, AKnave
    Implication(And(AKnight, AKnave), AKnight), 
    # A tells a lie -> AKnave
    Implication(Not(And(AKnight, AKnave)), AKnave)

)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(

    And(Or(AKnight, AKnave), Not(And(AKnight, AKnave))),
    And(Or(BKnight, BKnave), Not(And(BKnight, BKnave))),

    # A tells a truth -> AKnight + both Knaves -> AKnave, BKnave
    Implication(And(AKnave, BKnave), And(AKnight, AKnave, BKnave)),
    # A tells a lie -> AKnave + not both Knaves -> BKnight
    Implication(Not(And(AKnave, BKnave)), And(AKnave, BKnight))
    
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."

knowledge2 = And(

    And(Or(AKnight, AKnave), Not(And(AKnight, AKnave))),
    And(Or(BKnight, BKnave), Not(And(BKnight, BKnave))),
    
    Biconditional(AKnight, BKnave),
    Biconditional(AKnave, BKnight),


    # Self-conflict conditions
    # A tells a truth -> AKnight + same kind -> BKnight + BKnave (B tells a lie)
    # B Tells a lie -> BKnave + same kind -> AKnave + AKnight (A tells a truth)

    # A tells a lie -> AKnave + diff kind -> BKnight (B tells a truth)
    Implication(Not(Or(And(AKnight, BKnight), And(AKnave, BKnave))), And(AKnave, BKnight)),
    # B tells a truth -> BKnight + diff kind -> AKnave 
    Implication(And(Or(AKnave, BKnave), And(AKnight, BKnight)), And(AKnave, BKnight)),
)


# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    And(Or(AKnight, AKnave), Not(And(AKnight, AKnave))),
    And(Or(BKnight, BKnave), Not(And(BKnight, BKnave))),
    And(Or(CKnight, CKnave), Not(And(CKnight, CKnave))),

    Implication(CKnight, AKnight),
    Implication(CKnave, AKnave),
    Implication(And(AKnight, AKnave, CKnave), BKnight),
    Implication(Not(And(AKnight, AKnave, CKnave)), BKnave),
    Implication(BKnight, CKnave),
    Implication(BKnave, CKnight)
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
