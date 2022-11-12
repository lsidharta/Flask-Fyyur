#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import os
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import aliased
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form, FlaskForm
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://lieke:Glen2865@localhost:5432/todoapp'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://lieke:Glen2865@localhost:5432/fyyurapp'
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'venues'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=True)
  genres = db.Column(db.ARRAY(db.String), nullable=False)#db.Column(db.String(120), nullable=False)    
  image_link = db.Column(db.String(500), nullable=True)
  facebook_link = db.Column(db.String(120), nullable=True) 
  # TODO: implement any missing fields, as a database migration using Flask-Migrate
  website_link = db.Column(db.String(100), nullable=True) 
  seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String(500), nullable=True) # default="Not currently seeking talent"  
  shows_venue = db.relationship('Show', back_populates='venue', lazy=True)
  
  def __repr__(self):
    return f'id: {self.id}, name:{self.name}, city:{self.city}, state:{self.state}, address:{self.address}, \
    phone:{self.phone}, genres: {self.genres}, image link: {self.image_link}, FB link: {self.facebook_link}, Website link:{self.website_link}, \
    is seeking talents: {self.seeking_talent}, seeking desc: {self.seeking_description} '


class Artist(db.Model):
  __tablename__ = 'artists'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=True)
  genres = db.Column(db.ARRAY(db.String), nullable=False)#db.Column(db.String(120), nullable=False)
  image_link = db.Column(db.String(500), nullable=True)
  # TODO: implement any missing fields, as a database migration using Flask-Migrate
  facebook_link = db.Column(db.String(120), nullable=True) # default="No Facebook Link"
  website_link = db.Column(db.String(100), nullable=True) # default="No Website"
  seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String(500), nullable=True) # default="Not currently seeking performance venues"  
  shows_artist = db.relationship('Show', back_populates='artist', lazy=True)
  
  def __repr__(self):
    return f'<Artist id: {self.id}, name:{self.name}, city:{self.city}, state:{self.state}, address:{self.address}, \
    phone:{self.phone}, genres: {self.genres}, image link: {self.image_link}, FB link: {self.facebook_link}, Website link:{self.website_link}, \
    is seeking talents: {self.seeking_venue}, seeking desc: {self.seeking_description} >'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)
  artist = db.relationship('Artist', back_populates='shows_artist')
  venue = db.relationship('Venue', back_populates='shows_venue')

  def __repr__(self):
    return f'<Show id: {self.id}, start_time: {self.start_time}>'

with app.app_context():
    app.debug = True
    db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  #date = dateutil.parser.parse(value)
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # TODO: replace with real venues data.
  current_time = datetime.now()
  distinct_city_state = db.session.query(Venue.id, Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()
  venues_shows = db.session.query(Venue, Show).join(Venue.shows_venue, isouter=True).all()
  db.session.close()
  data = []
  
  for cs in distinct_city_state:
    city_dict = {}
    city_dict['city'] = cs.city
    city_dict['state'] = cs.state
    city_dict['venues'] = []
    
    venues_dict = {}
    for vs in venues_shows:
      print (vs)
      print ("vs.Venue.id: " + str(vs.Venue.id) + " --- vs.Venue.city: " + vs.Venue.city)
      if vs.Venue.city == cs.city:
        if vs.Venue.id in venues_dict.keys():
          if vs.Show.start_time > current_time:
            venues_dict[vs.Venue.id]['num_upcoming_shows'] += 1
        else:
          venue_dict = {}
          venue_dict['id'] = vs.Venue.id
          venue_dict['name'] = vs.Venue.name
          if vs.Show and vs.Show.start_time > current_time:
            venue_dict['num_upcoming_shows'] = 1
          else:
            venue_dict['num_upcoming_shows'] = 0
          venues_dict[vs.Venue.id] = venue_dict
      city_dict['venues'] = list(venues_dict.values())
    data.append(city_dict)
  """
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  """
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike("%" + search + "%")).all()
  data = []
  for venue in venues:
    data.append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': 0
    })
  response = {
    'count': len(venues),
    'data': data
  }
  response_old={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  error = False
  current_time = datetime.now()
  data = {}
  vs_dict = {}
  vs_dict['past_shows'] = []
  vs_dict['upcoming_shows'] = []
  vs_dict['upcoming_shows_count'] = 0
  vs_dict['past_shows_count'] = 0    
  try:
    shows = db.session.query(Show).filter_by(venue_id=venue_id)
    if shows.count() == 0:
      vs = db.session.query(Venue).filter_by(id=venue_id).one()
    else:
      vs = db.session.query(Venue).filter_by(id=venue_id).join(Venue.shows_venue, isouter=False).one()  
      for sv in vs.shows_venue:
        show = {}
        show['artist_id'] = sv.artist_id
        artist = db.session.query(Artist).filter_by(id = sv.artist_id).one()
        show['artist_name'] = artist.name
        show['artist_image_link'] = artist.image_link
        show['start_time'] = sv.start_time
        if sv.start_time < current_time:
          vs_dict['past_shows'].append(show)
          vs_dict['past_shows_count'] += 1
        else:
          vs_dict['upcoming_shows'].append(show)
          vs_dict['upcoming_shows_count'] += 1
    vs_dict['id'] = vs.id
    vs_dict['name'] = vs.name
    v_genres = vs.genres
    vs_dict['genres'] = vs.genres
    vs_dict['address'] = vs.address
    vs_dict['city'] = vs.city
    vs_dict['state'] = vs.state
    vs_dict['phone'] = vs.phone
    vs_dict['website_link'] = vs.website_link
    vs_dict['facebook_link'] = vs.facebook_link
    vs_dict['image_link'] = vs.image_link
    vs_dict['seeking_talent'] = vs.seeking_talent
    vs_dict['seeking_description'] = vs.seeking_description
  except Exception as e:
    error = True
    print (e)
    db.session.rollback()
  finally:
    db.session.close()
  data = vs_dict
  
  """
  data1={
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
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 3,
  }
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  """
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm() #VenueTestForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form) 
  error = False
  v_name = ""
  v_name = form.name.data
  try:
    venue = Venue(
      name = v_name,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      genres = list(form.genres.data),
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      website_link = form.website_link.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + v_name + ' was successfully listed!')
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
    flash('Venue ' + v_name + ' cannot be listed!')
  finally:
    db.session.close()
  # on successful db insert, flash success
  #if error:
  #  flash('Venue ' + v_name + ' cannot be listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #else:
  #  flash('Venue ' + v_name + ' was successfully listed!')
  return render_template('pages/home.html')

#@app.route('/venues/<venue_id>', methods=['DELETE'])
@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.get_or_404(venue_id)
  venue_name = venue.name
  try:
    db.session.delete(venue)
    db.session.commit()
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
    flash('Venue ' + venue_name + ' cannot be deleted!')
  finally:
    db.session.close()
    flash('Venue ' + venue_name + ' deleted!')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('venues'))#None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = db.session.query(Artist).all()
  db.session.close()
  data = []
  for artist in artists:
    artist_dict = {}
    artist_dict['id'] = artist.id
    artist_dict['name'] = artist.name
    data.append(artist_dict)
  
  data_old=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike("%" + search + "%")).all()
  data = []
  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': 0
    })
  response = {
    'count': len(artists),
    'data': data
  }
  response_old={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = {}
  vs_dict = {}
  current_time = datetime.now()
  vs_dict['past_shows'] = []
  vs_dict['upcoming_shows'] = []
  vs_dict['upcoming_shows_count'] = 0
  vs_dict['past_shows_count'] = 0
  #shows = db.session.query(Show).filter_by(artist_id=artist_id)
  try:
    shows = db.session.query(Show).filter_by(artist_id=artist_id)
    if shows.count() == 0:
      vs = db.session.query(Artist).filter_by(id=artist_id).one()
    else:
      vs = db.session.query(Artist).filter_by(id=artist_id).join(Artist.shows_artist, isouter=False).one()
      for sv in vs.shows_artist:
        show = {}
        show['venue_id'] = sv.venue_id
        venue = db.session.query(Venue).filter_by(id = sv.venue_id).one()
        show['venue_name'] = venue.name
        show['venue_image_link'] = venue.image_link
        show['start_time'] = sv.start_time
        if sv.start_time < current_time:
          vs_dict['past_shows'].append(show)
          vs_dict['past_shows_count'] += 1
        else:
          vs_dict['upcoming_shows'].append(show)
          vs_dict['upcoming_shows_count'] += 1
    vs_dict['id'] = vs.id
    vs_dict['name'] = vs.name
    vs_dict['genres'] = vs.genres
    vs_dict['address'] = vs.address
    vs_dict['city'] = vs.city
    vs_dict['state'] = vs.state
    vs_dict['phone'] = vs.phone
    vs_dict['website_link'] = vs.website_link
    vs_dict['facebook_link'] = vs.facebook_link
    vs_dict['image_link'] = vs.image_link
    vs_dict['seeking_venue'] = vs.seeking_venue
    vs_dict['seeking_description'] = vs.seeking_description
  except Exception as e:
    error = True
    print(e)
    db.session.rollback()
  finally:
    db.session.close()
  data = vs_dict

  data1={
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
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist_old={
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
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  try:
    artist = Artist.query.get_or_404(artist_id)
    form.populate_obj(artist)
    db.session.commit()
    flash(f'Artist {form.name.data} was successfully updated!')
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
    flash(f'Artist {form.name.data} cannot be updated!')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  venue_old={
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
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  try:
    venue = Venue.query.get(venue_id)
    form.populate_obj(venue)
    db.session.commit()
    flash(f'Venue {form.name.data} was successfully updated!')
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  # called upon submitting the new artist listing form
  form = ArtistForm(request.form)
  # Get the data from the new_artist form
  a_name = ""
  a_name = form.name.data
  a_genres = list(form.genres.data)
  try:
    artist = Artist(
      name = a_name,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      genres = a_genres,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      website_link = form.website_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(artist)
    db.session.commit()
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  if not error:
    flash('Artist ' + a_name + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  else:
    flash('Artist ' + a_name + ' cannot be listed!')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = db.session.query(Show,Venue,Artist).all()
  for sh in shows:
    sh_dict = {}
    sh_dict['venue_id'] = sh.Venue.id
    sh_dict['start_time'] = sh.Show.start_time
    sh_dict['artist_id'] = sh.Artist.id
    sh_dict['artist_name'] = sh.Artist.name
    sh_dict['artist_image_link'] = sh.Artist.image_link
    sh_dict['venue_name'] = sh.Venue.name
    data.append(sh_dict)
  data_old=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  form = ShowForm()
  error = False
  artistId = request.form.get('artist_id')
  venueId = request.form.get('venue_id')
  startTime = request.form.get('start_time')
  # TODO: insert form data as a new Show record in the db, instead
  try:
    show = Show(
      venue_id = venueId,
      artist_id = artistId,
      start_time = startTime
    )
    db.session.add(show)
    db.session.commit()
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  # on successful db insert, flash success
  if not error:
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
    flash('Show cannot be listed!')
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
'''
if __name__ == '__main__':
    app.run()
'''
# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

