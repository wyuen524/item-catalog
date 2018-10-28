from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Weapon, ItemInfo, User

engine = create_engine('sqlite:///fortniteitems.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

user1 = User(email="wyuen524@gmail.com")
session.add(user1)
session.commit()

class1 = Weapon(name="Assault Rifle", user=user1)

session.add(class1)
session.commit()

item1 = ItemInfo(name="M4",
                 description="Small hit box, good for midrange fights",
                 damage="32", dps="181.5", weapon=class1, user=user1)

session.add(item1)
session.commit()

class2 = Weapon(name="Shotgun", user=user1)

session.add(class2)
session.commit()

item2 = ItemInfo(name="Pump",
                 description="Large hit box, good for close range fights",
                 damage="85", dps="59.5", weapon=class2, user=user1)

session.add(item2)
session.commit()

class3 = Weapon(name="Submachine Gun", user=user1)

session.add(class3)
session.commit()

item3 = ItemInfo(name="P90",
                 description="Low single hit damage but fast firing rate",
                 damage="20", dps="200", weapon=class3, user=user1)

session.add(item3)
session.commit()

class4 = Weapon(name="Sniper Rifle", user=user1)

session.add(class4)
session.commit()

item4 = ItemInfo(name="Hunting Rifle",
                 description="High damage on hit but requires good aim",
                 damage="90", dps="225", weapon=class4, user=user1)

session.add(item4)
session.commit()

class5 = Weapon(name="Explosives", user=user1)

session.add(class5)
session.commit()

item5 = ItemInfo(name="Rocket Launcher",
                 description="Great for long range fights and knocking down" +
                 "enemy buildings",
                 damage="110", dps="82.5", weapon=class5, user=user1)

session.add(item5)
session.commit()

print "added items!"
