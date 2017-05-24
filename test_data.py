"""
Nathan D. Hernandez
Udacity FullStack NanoDegree

Test data population script

    - ver: 0.1  05/2017
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User, LoginType, Role

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create a login type
logintype = LoginType(source="google")
session.add(logintype)
session.commit()

# Create a ROLE with 'admin' permission
admin_role = Role(permission="admin")
session.add(admin_role)
session.commit()
# Regular Normal 'contributor' permission
contrib_role = Role(permission="contrib")
session.add(contrib_role)
session.commit()


# Create a sample user / assume they logged in via Google Auth
user1_roles = [admin_role, contrib_role]
user1 = User(logintype_id=logintype.id, roles=user1_roles,
            email="nathandhernandez@gmail.com")
session.add(user1)
session.commit()
# User 2
user2_roles = [contrib_role]
user2 = User(logintype_id=logintype.id, roles=user2_roles,
            email="ndh2@njit.edu")
session.add(user2)
session.commit()

# Create some test Category objects
cat1 = Category(name="Soccer", description="""A globally popular ball game in 
                                              which feet dominate play and 
                                              scoring""",
                                              created_by=user1.email,
                                              last_update_by=user1.email)
session.add(cat1)
session.commit()

cat2 = Category(name="Basketball", description="""A hoop/ball game with major 
                                                  popularity in the United 
                                                  States""",
                                                  created_by=user1.email,
                                                  last_update_by=user1.email)
session.add(cat2)
session.commit()

# Add some items to Categories
item1 = Item(name="Hoop & Net", description="""Brand new hoop with net. Made
                                               in USA.""",
                                               created_by=user1.email,
                                               last_update_by=user1.email,
                                               category_id=cat2.id)
session.add(item1)
session.commit()

item2 = Item(name="Shinguards", description="""To protect your shins during
                                               play""",
                                               created_by=user1.email,
                                               last_update_by=user1.email,
                                               category_id=cat1.id)
session.add(item2)
session.commit()


print "Populated TEST catalog/item/user data!"
