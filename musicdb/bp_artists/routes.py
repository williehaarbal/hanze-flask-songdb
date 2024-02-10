from typing import TypedDict
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy import func
from musicdb import db
from musicdb.models import Artist
from .forms import CreateArtist

bp_artists = Blueprint('artists', __name__)


@bp_artists.route("/artists")
def artist():
    artist = db.session.scalars(db.select(Artist)).all()

    for i in artist:
        print(i)

    return render_template('artists.html')


def create_artist(name: str) -> int:
    pass





@bp_artists.route("/artists/add", methods=['GET', 'POST'])
def artist_add():

    if not current_user.is_authenticated:
        flash("You shouldn't be here.")
        redirect(url_for('main.home'))

    errors = None
    title = "MusicDB :: new artist"

    form = CreateArtist()

    if form.validate_on_submit():
        try:
            create_artist(form.name.data, band_cover=form.picture.data, description=form.description.data, country=form.country_flag.data)
            flash('New artist created!')
        except Exception as e:
            flash(f'Error creating new artist. ERROR: {e}')

    return render_template('create_artist.html', form=form, title=title)



def create_artist(name:str, **kwargs) -> int:

    description = None
    country = None
    band_cover = None

    for arg in kwargs:
        if str(arg) == 'description':
            description = kwargs[arg]
        if str(arg) == 'country':
            country = kwargs[arg]
        if str(arg) == 'band_cover':
            band_cover = kwargs[arg]
        
    from musicdb.models import Artist
    from musicdb import db, app

    # Required when using outide Flask runtime
    # app.app_context().push()

    # Check if band already exists

    excist = db.session.query(Artist.id).filter_by(name = name).first() is not None

    if excist:
        return None
    else:
        new_artist = Artist(name=name, country=country, band_cover=None, description=description)
        db.session.add(new_artist)
        db.session.commit()
        return new_artist.id
