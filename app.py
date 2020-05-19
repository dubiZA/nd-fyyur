#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
venue_genres = db.Table(
  'venue_genres',
  db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True),
  db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

artist_genres = db.Table(
  'artist_genres',
  db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
  db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(500), nullable=True)

    # Relationships
    shows = db.relationship('Show', backref='venue', lazy=True)
    genres = db.relationship('Genre', secondary=venue_genres,
                              backref=db.backref('venues', lazy=True))


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(500), nullable=True)

    # Relationships
    shows = db.relationship('Show', backref='artist', lazy=True)
    genres = db.relationship('Genre', secondary=artist_genres,
                              backref=db.backref('artists', lazy=True))


class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)

  # Foreign Keys
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)

  def __repr__(self):
        return f'<Show: {self.id} {self.start_time} {self.venue_id} {self.artist_id}>'


class Genre(db.Model):
  __tablename__ = 'genre'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)

  def __repr__(self):
        return f'<Genre: {self.id} {self.name}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # Initialize collection data types and current time
  data = []
  cities_states = []
  current_date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  # Retrieve unique city/state combos from venue table
  unique_cities = db.session.query(Venue.city, Venue.state).distinct()

  # Add the city/state combps to a list for use next
  for city, state in unique_cities:
    cities = {}
    cities['city'] = city
    cities['state'] = state
    cities_states.append(cities)

  # Start building out the data structure expected by the view starting
  # with venue location information. Append this and the next for loops
  # results in to the "data" list
  for location in cities_states:
    venues_list = []
    venues_cities = Venue.query.filter_by(city=location['city']).all()

    # Build out the next part of the expected data structure with
    # getting venue details
    for venue_detail in venues_cities:
      venue = {}
      venue['id'] = venue_detail.id
      venue['name'] = venue_detail.name
      venue['num_upcoming_shows'] = db.session.query(Show).filter(
                                    Show.venue_id==venue['id'],
                                    Show.start_time>=current_date_time
                                    ).count()
      venues_list.append(venue)
      location['venues'] = venues_list
    
    data.append(location)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Get search term and use filter with ilike for case insensitive searching
  # Also get current time and number of query objects from search
  search_term = request.form.get('search_term')
  search_results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  current_date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  count_of_results = len(search_results)
  
  # Initialize the data list and step through each result to retrieve needed data
  data = []
  for venue in search_results:
    venue_id = venue.id
    venue_name = venue.name
    upcoming_show_count = db.session.query(Show).filter(
                            Show.venue_id==venue_id,
                            Show.start_time>=current_date_time
                            ).count()
    venue_details = {
      'id': venue_id,
      'name': venue_name,
      'num_upcoming_shows': upcoming_show_count
    }
    data.append(venue_details)
  
  # Build the response dictionary the view is expecting
  response = {
    'count': count_of_results,
    'data': data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # Query db for venue and shows at that venue. Also get current time
  venue_details = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venue_id).order_by('start_time').all()
  current_date_time = datetime.datetime.now()
  
  # If the venue provided to the endpoint does not exist, return to venue list
  if not venue_details:
    return redirect(url_for('venues'))

  # Construct past/future shows details
  past_shows = []
  upcoming_shows = []
  for show in shows:
    show_details = {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': format_datetime(str(show.start_time))
      }
    if show.start_time < current_date_time:
      past_shows.append(show_details)
    elif show.start_time > current_date_time:
      upcoming_shows.append(show_details)

  # Get genre list for venue
  genre_list = []
  for genre in venue_details.genres:
    genre_list.append(genre.name)

  # Construct data dictionary expected by view
  data = {
    'id': venue_details.id,
    'name': venue_details.name,
    'genres': genre_list,
    'address': venue_details.address,
    'city': venue_details.city,
    'state': venue_details.state,
    'phone': venue_details.phone,
    'website': venue_details.website,
    'facebook_link': venue_details.facebook_link,
    'seeking_talent': venue_details.seeking_talent,
    'seeking_description': venue_details.seeking_description,
    'image_link': venue_details.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')
    image_link = request.form.get('image_link')
    website = request.form.get('website')
    facebook_link = request.form.get('facebook_link')
    
    if seeking_talent == 'y':
      seeking_talent = True
    elif seeking_talent == 'n':
      seeking_talent = False

    new_venue = Venue(
      name=name,
      city=city,
      state=state,
      address=address,
      phone=phone,
      seeking_talent=seeking_talent,
      seeking_description=seeking_description,
      image_link=image_link,
      website=website,
      facebook_link=facebook_link
    )

    genres = request.form.getlist('genres')
    for genre in genres:
      genre_record = Genre.query.filter_by(name=genre).first()
      new_venue.genres.append(genre_record)
    
    db.session.add(new_venue)
    db.session.commit()
    flash(f'Venue {name} was successfully listed!')
  except:
    db.session.rollback()
    flash(f'Venue {name} could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # Get all the artist records from the database
  all_artists = Artist.query.all()

  # Initialize the data list for artist details dictionary
  data = []
  # Loop through each artist, get details and append to data list
  for artist in all_artists:
    artist_details = {
      'id': artist.id,
      'name': artist.name
    }
    data.append(artist_details)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # Get search term and use filter with ilike for case insensitive searching
  # Also get current time and number of query objects from search
  search_term = request.form.get('search_term')
  search_results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  current_date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  count_of_results = len(search_results)
  
  # Initialize the data list and step through each result to retrieve needed data
  data = []
  for artist in search_results:
    artist_id = artist.id
    artist_name = artist.name
    upcoming_show_count = db.session.query(Show).filter(
                                    Show.artist_id==artist_id,
                                    Show.start_time>=current_date_time
                                    ).count()
    artist_details = {
      'id': artist_id,
      'name': artist_name,
      'num_upcoming_shows': upcoming_show_count
    }
    data.append(artist_details)
  
  # Build the response dictionary the view is expecting
  response = {
    'count': count_of_results,
    'data': data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # Query db for artist and shows for the artist. Also get current time
  artist_details = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id=artist_id).order_by('start_time').all()
  current_date_time = datetime.datetime.now() #.strftime('%Y-%m-%d %H:%M:%S')
  
  # If the artist provided to the endpoint does not exist, return to artist list
  if not artist_details:
    return redirect(url_for('artists'))

  # Construct past/future shows details
  past_shows = []
  upcoming_shows = []
  for show in shows:
    show_details = {
        'venue_id': show.venue_id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': format_datetime(str(show.start_time))
      }
    if show.start_time < current_date_time:
      past_shows.append(show_details)
    elif show.start_time > current_date_time:
      upcoming_shows.append(show_details)

  # Get genre list for artist
  genre_list = []
  for genre in artist_details.genres:
    genre_list.append(genre.name)

  # Construct data dictionary expected by view
  data = {
    'id': artist_details.id,
    'name': artist_details.name,
    'genres': genre_list,
    'city': artist_details.city,
    'state': artist_details.state,
    'phone': artist_details.phone,
    'website': artist_details.website,
    'facebook_link': artist_details.facebook_link,
    'seeking_talent': artist_details.seeking_venue,
    'seeking_description': artist_details.seeking_description,
    'image_link': artist_details.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
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
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    seeking_venue = request.form.get('seeking_venue')
    seeking_description = request.form.get('seeking_description')
    image_link = request.form.get('image_link')
    website = request.form.get('website')
    facebook_link = request.form.get('facebook_link')
    
    if seeking_venue == 'y':
      seeking_venue = True
    elif seeking_venue == 'n':
      seeking_venue = False

    new_artist = Artist(
      name=name,
      city=city,
      state=state,
      phone=phone,
      seeking_venue=seeking_venue,
      seeking_description=seeking_description,
      image_link=image_link,
      website=website,
      facebook_link=facebook_link
    )

    genres = request.form.getlist('genres')
    for genre in genres:
      genre_record = Genre.query.filter_by(name=genre).first()
      new_artist.genres.append(genre_record)
    
    db.session.add(new_artist)
    db.session.commit()
    flash(f'Artist {name} was successfully listed!')
  except:
    db.session.rollback()
    flash(f'Artist {name} could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # Get all shows from db
  all_shows = Show.query.all()

  # Initialize empty data list then populate with show details and add to data list
  data = []
  for show in all_shows:
    show_details = {
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': format_datetime(str(show.start_time))
    }

    data.append(show_details)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')

    new_show = Show(
      artist_id=artist_id,
      venue_id=venue_id,
      start_time=start_time
    )
    
    db.session.add(new_show)
    db.session.commit()

    show_id = new_show.id
    flash(f'Show {new_show.id} was successfully listed!')
  except:
    db.session.rollback()
    flash(f'Show could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
    
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
