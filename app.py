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
from models import db, Venue, Artist, Show
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

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
  # Get the disctinct cities and states
  distinct_city_state = db.session.query(Venue.id, Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()
  # Get the 10 latest venues
  venues_shows = db.session.query(Venue, Show).join(Venue.shows_venue, isouter=True).order_by(Venue.id.desc()).limit(10)
  venues_shows = venues_shows[::-1] # Reverse the order
  db.session.close()
  data = []
  
  for cs in distinct_city_state:
    city_dict = {}
    city_dict['city'] = cs.city
    city_dict['state'] = cs.state
    city_dict['venues'] = []
    
    venues_dict = {}
    for vs in venues_shows:
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
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # Get the search term from the form
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
    # Find the unique venue with id = venue_id
    vs = Venue.query.filter_by(id=venue_id).one()
    # If there is any shows in the venue, compose the shows information
    if len(vs.shows_venue) > 0:
      # For each show, create a dictionary
      for show in vs.shows_venue:
        show_dict = {}
        show_dict['artist_id'] = show.artist.id
        show_dict['artist_name'] = show.artist.name
        show_dict['artist_image_link'] = show.artist.image_link
        show_dict['start_time'] = show.start_time
        # For the past shows
        if show.start_time < current_time:
          vs_dict['past_shows'].append(show_dict)
          vs_dict['past_shows_count'] += 1
        # For the upcoming shows
        else:
          vs_dict['upcoming_shows'].append(show_dict)
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
    vs_dict['seeking_talent'] = vs.seeking_talent
    vs_dict['seeking_description'] = vs.seeking_description
  except Exception as e:
    error = True
    print (e)
    db.session.rollback()
  finally:
    db.session.close()
  data = vs_dict
  
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
  error = False
  # Set the Flask form
  form = VenueForm(request.form, meta={'csrf': False}) 

  # Validate all fields
  if form.validate():
    # Get the venue name
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
  # If there is any invalid field
  else:
    # Contruct the error message
    message = []
    for field, err in form.errors.items():
      message.append(field + ' ' + ('|'.join(err)))
    flash('Errors: ' + str(message))
    # Refresh the form
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

  # on successful db insert, flash success
   # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
  # Query the last 10 artist in the ascending order
  artists = Artist.query.order_by(Artist.id.desc()).limit(10)
  artists = artists[::-1]
  db.session.close()
  data = []
  for artist in artists:
    artist_dict = {}
    artist_dict['id'] = artist.id
    artist_dict['name'] = artist.name
    data.append(artist_dict)
  
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
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  error = False
  current_time = datetime.now()
  data = {}
  vs_dict = {}
  vs_dict['past_shows'] = []
  vs_dict['upcoming_shows'] = []
  vs_dict['upcoming_shows_count'] = 0
  vs_dict['past_shows_count'] = 0
  #shows = db.session.query(Show).filter_by(artist_id=artist_id)
  try:
    #shows = db.session.query(Show).filter_by(artist_id=artist_id)
    vs = Artist.query.filter_by(id=artist_id).one()
    #if shows.count() == 0:
    #  vs = db.session.query(Artist).filter_by(id=artist_id).one()
    if len(vs.shows_artist) > 0:
      #vs = db.session.query(Artist).filter_by(id=artist_id).join(Artist.shows_artist, isouter=False).one()
      for show in vs.shows_artist:
        show_dict = {}
        show_dict['venue_id'] = show.venue.id #venue_id
        #venue = db.session.query(Venue).filter_by(id = sv.venue_id).one()
        show_dict['venue_name'] = show.venue.name
        show_dict['venue_image_link'] = show.venue.image_link
        show_dict['start_time'] = show.start_time
        if show.start_time < current_time:
          vs_dict['past_shows'].append(show_dict)
          vs_dict['past_shows_count'] += 1
        else:
          vs_dict['upcoming_shows'].append(show_dict)
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

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  if form.validate():
    try:
      artist = Artist.query.get(artist_id)
      form.populate_obj(artist)
      # Update the database
      db.session.commit()
      flash(f'Artist {form.name.data} was successfully updated!')
    except Exception as e:
      print(e)
      error = True
      db.session.rollback()
      flash('Error is occured. Artist cannot be updated.' )
    finally:
      db.session.close()
  # If there is any invalid field
  else:
    # Contruct the error message
    message = []
    for field, err in form.errors.items():
      message.append(field + ' ' + ('|'.join(err)))
    flash('Errors: ' + str(message))
    artist_data = Artist.query.get(artist_id)
    form.populate_obj(artist_data)
    return render_template('forms/edit_artist.html', form=form, artist=artist_data)
    
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  # Get the venue information from database
  venue = Venue.query.get(venue_id)
  # Populate the VenueForm with the venue information
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  if form.validate():
    try:
      venue = Venue.query.get(venue_id)
      form.populate_obj(venue)
      # Update the database
      db.session.commit()
      flash(f'Venue {form.name.data} was successfully updated!')
    except Exception as e:
      print(e)
      error = True
      db.session.rollback()
      flash(f'Error is occured. Venue cannot be updated.')
    finally:
      db.session.close()
  # If there is any invalid field
  else:
    # Contruct the error message
    message = []
    for field, err in form.errors.items():
      message.append(field + ' ' + ('|'.join(err)))
    flash('Errors: ' + str(message))
    venue_data = Venue.query.get(venue_id)
    form.populate_obj(venue_data)
    return render_template('forms/edit_venue.html', form=form, venue=venue_data)

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
  form = ArtistForm(request.form, meta={'csrf': False})

  # Validate all fields
  if form.validate():
    # Get the data from the new_artist form
    a_name = ""
    a_name = form.name.data
    try:
      # Create an Artist object
      artist = Artist(
        name = a_name,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        genres = list(form.genres.data),
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        website_link = form.website_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data
      )
      # Insert the new artist to the database
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + a_name + ' was successfully listed!')
    except Exception as e:
      print(e)
      error = True
      db.session.rollback()
      flash('Artist ' + a_name + ' cannot be listed!')
    finally:
      db.session.close()
  # If there is any invalid field
  else:
    # Contruct the error message
    message = []
    for field, err in form.errors.items():
      message.append(field + ' ' + ('|'.join(err)))
    flash('Errors: ' + str(message))
    # Refresh the form
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)
    
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.order_by(Show.start_time).all()
  for sh in shows:
    sh_dict = {}
    sh_dict['venue_id'] = sh.venue.id
    sh_dict['venue_name'] = sh.venue.name
    sh_dict['start_time'] = sh.start_time
    sh_dict['artist_id'] = sh.artist.id
    sh_dict['artist_name'] = sh.artist.name
    sh_dict['artist_image_link'] = sh.artist.image_link
    data.append(sh_dict)

  return render_template('pages/shows.html', shows=data)

#  Create Show
#  ----------------------------------------------------------------

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  form = ShowForm(request.form)
  error = False
  # Gather show information from the form
  artistId = form.artist_id.data
  venueId = form.venue_id.data
  startTime = form.start_time.data
  # TODO: insert form data as a new Show record in the db, instead
  try:
    # Create Show object
    show = Show(
      venue_id = venueId,
      artist_id = artistId,
      start_time = startTime
    )
    # Find if the artist has shows arranged
    # If there are arranged shows, check whether the artist is available on that day
    show_times = db.session.query(Show.start_time).filter(Show.artist_id == artistId).all()
    if len(show_times) > 0:
      show_times_dict = {}
      for st in show_times:
        date = st[0].date()
        show_times_dict[date] = date
      if startTime.date() in show_times_dict.keys():
        flash('The artist is busy on that day! Please find different date.')
      else:
        # If the artist is available, insert the show in the database
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    else:
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
    flash('An error has occured. Show cannot be listed!')
  finally:
    db.session.close()
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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

