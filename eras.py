# Era name -> eraID, taken from the current game export (order is fixed by the game)
ERAS = ["Iron Age","Early Middle Age","High Middle Age","Late Middle Age","Colonial Age",
"Industrial Age","Progressive Era","Modern Era","Postmodern Era","Contemporary Era","Tomorrow Era",
"Future Era","Arctic Future","Oceanic Future","Virtual Future","Space Age Mars",
"Space Age Asteroid Belt","Space Age Venus","Space Age Jupiter Moon","Space Age Titan",
"Space Age Space Hub","Stellar Age: Discovery"]
ERA_ID = {name: i + 3 for i, name in enumerate(ERAS)}   # Iron Age = 3 ... Stellar Age = 24
