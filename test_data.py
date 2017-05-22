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

roles = [admin_role, contrib_role]

# Create a sample user / assume they logged in via Google Auth
user = User(logintype_id=logintype.id, roles=roles,
            email="nathandhernandez@gmail.com")
session.add(user)
session.commit()

# Create some test Category objects
cat1 = Category(name="Soccer", description="""A globally popular ball game in 
                                              in which feet dominate play and
                                              scoring""",
                                              created_by=user.email,
                                              last_update_by=user.email)
session.add(cat1)
session.commit()

cat2 = Category(name="Basketball", description="""A hoop/ball game with major 
                                                  popularity in the United 
                                                  States""",
                                                  created_by=user.email,
                                                  last_update_by=user.email)
session.add(cat2)
session.commit()

print "Populated TEST catalog/item/user data!"
