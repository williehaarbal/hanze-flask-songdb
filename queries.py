#
User.query.all()

db.session.execute()

db.session.execute(db.select(user)).scalars().all()

db.session.scalars(db.select(Users)).all()


User.query.first(<filter>)


db.session.scalars(db.select(User)).first()

User.query.filter_by(name="pretty printed").first()

db.session.scalars(db.select(users)).filters_by(name='pretty').first()

https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html
https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/queries/
https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html

https://stackoverflow.com/questions/16573095/case-insensitive-flask-sqlalchemy-query
# Lower / upper compare
from sqlalchemy import func
user = models.User.query.filter(func.lower(User.username) == func.lower("GaNyE")).first(


    # 

artist = Artist.query.all()
for a in artist:
    print(a)

artist = Artist.query.paginate()

artist.per_page
artist.page
artist.items


artist.query.paginate(per_page=5, page=2)
