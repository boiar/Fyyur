# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from .models import Shows, Venue, Artist, db
from . import create_app
from .config import Config
import dateutil.parser
import babel
from flask import render_template, request, flash, redirect, url_for
from datetime import datetime
import logging
from logging import Formatter, FileHandler
from .forms import *

app = create_app(Config)
# ----------------------------------------------------------------------------#
# Filters
# ----------------------------------------------------------------------------#

def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters["datetime"] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------

@app.route("/venues")
def venues():
    # DONE: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    try:
        venues = Venue.query.distinct(Venue.city, Venue.state).all()
        if venues:
            for venue in venues:
                upcoming_shows = len(Venue.query.join(Shows).filter(Shows.c.start_time > datetime.utcnow(), Shows.c.venue_id == venue.id).all())
                data.append({
                        "city": venue.city,
                        "state": venue.state,
                        "venues": [{"id": v.id, "name": v.name,
                            "num_upcoming_shows": upcoming_shows }
                                for v in Venue.query.filter_by(city=venue.city,
                                                           state=venue.state).all()]
                        })
    except Exception as e:
        print(e)
        pass
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # TODO: implement search on Venues //artists// with partial string search. Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term", "")
    search_response = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    data = []
    for venue in search_response:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(Venue.query.join(Shows).filter(Shows.c.start_time > datetime.utcnow(), Shows.c.venue_id == venue.id).all())
        })
        print(data)

    response = {
        "count": len(search_response),
        "data":data
    }
    return render_template("pages/search_venues.html", results=response,
                           search_term=request.form.get("search_term", ""))


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.filter_by(id=venue_id).first()

    # shows = db.session.query(Shows).filter(Shows.c.venue_id == venue.id).all()
    upcoming_shows = Artist.query.join(Shows).filter(Shows.c.start_time > datetime.utcnow(), Shows.c.venue_id == venue_id).all()
    past_shows = Artist.query.join(Shows).filter(Shows.c.start_time < datetime.utcnow(), Shows.c.venue_id == venue_id).all()
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "upcoming_shows":[{
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            } for artist in upcoming_shows],
        "upcoming_shows_count": len(upcoming_shows),
        "past_shows": [{
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time":str(show.start_time)} for artist in past_shows],
        "past_shows_count": len(past_shows),

        }
    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    venue_form = VenueForm()
    # venue_form.validate()
    name = venue_form.name.data
    phone = venue_form.phone.data
    address = venue_form.address.data
    city = venue_form.city.data
    image_url = venue_form.image_link.data
    facebook_url = venue_form.facebook_link.data
    state = venue_form.state.data
    genres = venue_form.genres.data
    seeking_talent = venue_form.seeking_talent.data
    seeking_description = venue_form.seeking_description.data
    website = venue_form.website_link.data

    # DONE: insert form data as a new Venue record in the db, instead
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_url,
                            facebook_link=facebook_url, genres=genres,
                    website_link=website,seeking_talent=seeking_talent,
                        seeking_description=seeking_description)
    try:
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash("Venue " + name + " was successfully listed!")
        # Done: modify data to be the data object returned from db insertion
    except Exception as e:
        # Done: on unsuccessful db insert, flash an error instead.
        # e.g., flash("An error occurred. Venue " + data.name + " could not be listed.")
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        db.session.rollback()
        flash("An error occurred. Venue " +
              name + " could not be listed.")
        db.session.flush()
        print(e)
    
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.filter_by(id=venue_id).first()
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for("index"))


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists", methods=['GET'])
def artists():
    # TODO: replace with real data returned from querying the database
    all_artist = []
    try:
        all_artist = Artist.query.all()
    except:
        db.session.rollback()
        db.session.close()
    data = []
    if all_artist:
        for artist in all_artist:
            data.append({"id": artist.id, "name": artist.name})
    return render_template("pages/artists.html", artists=all_artist)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get("search_term", "")
    search_response = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    data = []
    for artist in search_response:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(Artist.query.join(Shows).filter(Shows.c.start_time > datetime.now(), Shows.c.artist_id == artist_id).all())
        })

    response = {
        "count": len(search_response),
        "data":data
    }
    return render_template("pages/search_artists.html", results=response,
                           search_term=request.form.get("search_term", ""))


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real artist data from the artist table, using artist_id
    shows = db.session.query(Shows).filter(Shows.c.artist_id == artist_id).all()
    # upcoming_shows = Artist.query.join(Shows).filter(Shows.c.start_time > datetime.utcnow()).all()
    # past_shows = Artist.query.join(Shows).filter(Shows.c.start_time < datetime.utcnow(), Shows.c.artist_id == artist_id).all()

    upcoming_shows = Venue.query.join(Shows).filter(Shows.c.start_time > datetime.now(), Shows.c.artist_id == artist_id).all()
    past_shows = Venue.query.join(Shows).filter(Shows.c.start_time < datetime.now(), Shows.c.artist_id == artist_id).all()
    artist = Artist.query.filter_by(id=artist_id).first()

    upcoming_data = []
    for show in shows:
        for venue in upcoming_shows:
            upcoming_data.append({
                    "venue_id": venue.id,
                    "venue_name": venue.name,
                    "venue_image_link": venue.image_link,
                    "start_time":str(show.start_time)})
        print(show.start_time)
    print(upcoming_data)
    data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "facebook_link": artist.facebook_link,
            "website": artist.website_link,
            "image_link": artist.image_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "upcoming_shows_count": len(upcoming_shows),
            "upcoming_shows":  upcoming_data,
            "past_shows": [{
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(show.start_time)} for venue in past_shows],
            "past_shows_count": len(past_shows),

        }
    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter(id == artist_id).first()
    artist = {
        "id": artist.id,
        "name": artist.name,
        "genres": ["Rock n Roll"],
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid"
                      "=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80 "
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["PUT"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid"
                      "=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60 "
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    artist_form = ArtistForm()

    name = artist_form.name.data
    phone = artist_form.phone.data
    city = artist_form.city.data
    image_url = artist_form.image_link.data
    facebook_url = artist_form.facebook_link.data
    state = artist_form.state.data
    genres = artist_form.genres.data
    website = artist_form.website_link.data
    seeking_venue = artist_form.seeking_venue.data
    seeking_description = artist_form.seeking_description.data
    artist = Artist(name=name, city=city, state=state, phone=phone,website_link=website, genres=genres, image_link=image_url,
                    facebook_link=facebook_url, seeking_venue=seeking_venue, seeking_description=seeking_description)
    # TODO: modify data to be the data object returned from db insertion(DONE)
    try:
        db.session.add(artist)
        db.session.commit()
        flash("Artist " + artist.name + " was successfully listed!")
    except:
        db.session.rollback()
        db.session.flush()
        flash("An error occurred. Artist " +
              artist.name + " could not be listed.")
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash("An error occurred. Artist " + data.name + " could not be listed.")
    # on successful db insert, flash success

    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------

@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.(DONE)
    all_shows = []
    try:
        venues_all = Venue.query.join(Artist, Venue.state == Artist.state).all()
        data = db.session.query(Shows).all()
        for show in data:
            artist = Artist.query.filter_by(id=show.artist_id).first()
            venue = Venue.query.filter_by(id=show.venue_id).first()
            all_shows.append({
                        "venue_id": show.id,
                        "venue_name": venue.name,
                        "artist_id": artist.id,
                        "artist_name":artist.name,
                        "artist_image_link": artist.image_link,
                        "start_time": show.start_time
                    })
    except Exception as e:
        print(e)
        pass

    return render_template("pages/shows.html", shows=all_shows)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead(DONE)
    show_form = ShowForm()

    artist_id = show_form.artist_id.data
    venue_id = show_form.venue_id.data
    start_time = show_form.start_time.data

    show = Shows.insert().values(artist_id=artist_id,
                                 venue_id=venue_id, start_time=start_time)
    try:
        db.session.execute(show)
        db.session.commit()
          # on successful db insert, flash success
        flash("Show was successfully listed!")
    except Exception as e:
        flash("An error occurred. Show could not be listed.")
        db.session.rollback()
        db.session.flush()
        print(e)

    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#
# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
"""
