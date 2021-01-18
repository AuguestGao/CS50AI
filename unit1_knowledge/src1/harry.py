from logic import *

rain = Symbol("rain") # It is raining.
hagrid = Symbol("hagrid") # Harry visited Hagrid.
dumbledore = Symbol("dumbledore") # Harry visited Dumbledore.

knowledge = And( # KB
    Implication(Not(rain), hagrid), # If it's not raining, harry visited Hagrid.
    Or(hagrid, dumbledore), # Harry visited Hargid or Dumbledore
    Not(And(hagrid, dumbledore)), # Harrry did NOT visit both Hagrid and Dunbledore.
    dumbledore
)

print(model_check(knowledge, rain))
