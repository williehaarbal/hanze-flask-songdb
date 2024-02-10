def create_db():
    from musicdb import db, app
    from musicdb.models import Song, User, Artist, Album, UsersLikesSongs
    app.app_context().push()
    db.create_all()


def make_admin(user: str):
    from musicdb import db, app
    from musicdb.models import Song, User, Artist, Album, UsersLikesSongs
    app.app_context().push()

    try:
        db.session.query(User). \
        filter(User.username == user). \
        update({'admin': True})
        db.session.commit()
        print(f"User '{user}' has been turned into an admin. ")
    except Exception as e:
        print(f"Could not make user {user} admin. ERROR: {e}")