from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///itemcatalog.db')
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



#Menu for UrbanBurger
category1 = Category(name = "Soccer")
category2 = Category(name = "Basketball")
category3 = Category(name = "Baseball")
category4 = Category(name = "Frisbee")
category5 = Category(name = "Snowboarding")
category6 = Category(name = "Rock Climbing")
category7 = Category(name = "Foosball")
category8 = Category(name = "Skating")
category9 = Category(name = "Hockey")

session.add(category1)
session.add(category2)
session.add(category3)
session.add(category4)
session.add(category5)
session.add(category6)
session.add(category7)
session.add(category8)
session.add(category9)

session.commit()

item1 = Item(name = "Ball", description = "Classic Soccer Ball", category = category1)
session.add(item1)

item2 = Item(name = "Shin Guard", description = "Plastic", category = category1)
session.add(item2)

item3 = Item(name = "Jersey", description = "No.1 Maker of Jersies", category = category1)
session.add(item3)

item4 = Item(name = "Ball", description = "Spaulding", category = category2)
session.add(item4)

item5 = Item(name = "Wrist Sweat Band", description = "Left and Right", category = category2)
session.add(item5)

item6 = Item(name = "Head Sweat Band", description = "Straight from the 70's", category = category2)
session.add(item6)

item7 = Item(name = "Ball", description = "Official MLB equipment", category = category3)
session.add(item7)

item7 = Item(name = "Carbon Fiber Bat", description = "Carbon Fiber", category = category3)
session.add(item7)

session.commit()


print "end of populate"