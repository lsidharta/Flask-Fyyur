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
  error = False
  # TODO: replace with real venues data.
  current_time = datetime.now()
  # Get the disctinct cities and states
  data = []
  try:
    distinct_city_state = db.session.query(Venue).\
      distinct(Venue.city, Venue.state).\
      order_by(Venue.city.asc(), Venue.state.asc()).all()
    venues = db.session.query(Venue).all()
    for cs in distinct_city_state:
      data.append({
        'city': cs.city,
        'state': cs.state,
        'venues': [({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len([show for show in venue.shows \
                if show.start_time >= current_time]),
            'num_past_shows': len([show for show in venue.shows \
                if show.start_time < current_time])
          }) for venue in venues \
            if venue.city == cs.city and venue.state == cs.state]
      }) 
  except Exception as e:
    error = True
    print(e)
  finally:
    db.session.close()
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Get the search term from the form
  venues = []
  data = []
  current_time = datetime.now()
  search = request.form.get('search_term', '')
  try:
    venues = Venue.query.filter(Venue.name.ilike("%" + search + "%")).all()
    for venue in venues:
      data.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len([show for show in venue.shows \
                  if show.start_time >= current_time]),
        'num_past_shows': len([show for show in venue.shows \
                  if show.start_time < current_time])                
      })
  except Exception as e:
    error = True
    print(e)
  finally:
    response = {
      'count': len(venues),
      'data': data
    }
  return render_template('pages/search_venues.html', 
    results=response, 
    search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # Find the unique venue with id = venue_id
  # If there is any shows in the venue, compose the shows information
  # For each show, create a dictionary  
  error = False
  current_time = datetime.now()
  data = {}
  q = None
  try:
    q = db.session.query(Venue).filter(Venue.id == venue_id).one_or_404()
    data = {
      'id' : q.id,
      'name' : q.name,
      'genres' : q.genres,
      'address' : q.address,
      'city' : q.city,
      'state' : q.state,
      'phone' : q.phone,
      'website_link' : q.website_link,
      'facebook_link' : q.facebook_link,
      'image_link' : q.image_link,
      'seeking_talent' : q.seeking_talent,
      'seeking_description' : q.seeking_description,
      'upcoming_shows': [],
      'past_shows' : [],
      'upcoming_shows_count': 0,
      'past_shows_count': 0,
      'shows': q.shows
      }

    for show in q.shows:
      artist_dict = {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time
      }
      [data['past_shows'].append(artist_dict) if show.start_time < current_time \
        else data['upcoming_shows'].append(artist_dict) ]
    data['upcoming_shows_count'] = len(data['upcoming_shows'])
    data['past_shows_count'] = len(data['past_shows'])
    
  except Exception as e:
    error = True
    print (e)
  finally:
    db.session.close()
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
      venue.create()
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
    venue.delete()
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
  current_time = datetime.now()
  data = []  
  try:
    artists = Artist.query.order_by(Artist.id.desc()).limit(10)
    [data.append({
        'id': artist.id,
        'name': artist.name,
        'num_upcoming_shows': len([show for show in artist.shows \
          if show.start_time >= current_time]),
        'num_past_shows': len([show for show in artist.shows \
          if show.start_time < current_time])
      }) for artist in artists[::-1]]
  except Exception as e:
    error = True
    print(e)
  finally:
    db.session.close()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = []
  artists = []
  current_time = datetime.now()
  search = request.form.get('search_term', '')
  try:
    artists = Artist.query.filter(Artist.name.ilike("%" + search + "%")).all()
    for artist in artists:
      data.append({
        'id': artist.id,
        'name': artist.name,
        'num_upcoming_shows': len([show for show in artist.shows \
                  if show.start_time >= current_time]),
        'num_past_shows': len([show for show in artist.shows \
                  if show.start_time < current_time])
      })
  except Exception as e:
    error = True
    print(e)
  finally:
    response = {
      'count': len(artists),
      'data': data
    }
  return render_template('pages/search_artists.html', results=response, \
    search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  error = False
  current_time = datetime.now()
  data = {}
  try:
    q = db.session.query(Artist).filter(Artist.id == artist_id).one_or_404()
    data = {
      'id' : q.id,
      'name' : q.name,
      'genres' : q.genres,
      'address' : q.address,
      'city' : q.city,
      'state' : q.state,
      'phone' : q.phone,
      'website_link' : q.website_link,
      'facebook_link' : q.facebook_link,
      'image_link' : q.image_link,
      'seeking_venue' : q.seeking_venue,
      'seeking_description' : q.seeking_description,
      'upcoming_shows': [],
      'past_shows' : [],
      'upcoming_shows_count': 0,
      'past_shows_count': 0
      }
    
    for show in q.shows:
      venue_dict = {
        'venue_id': show.venue_id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.start_time
      }
      [data['past_shows'].append(venue_dict) if show.start_time < current_time \
        else data['upcoming_shows'].append(venue_dict) ]
    data['upcoming_shows_count'] = len(data['upcoming_shows'])
    data['past_shows_count'] = len(data['past_shows'])
  except Exception as e:
    error = True
    print(e)
  finally:
    db.session.close()
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
  form = ArtistForm(request.form, meta={'csrf': False})
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
  form = VenueForm(request.form, meta={'csrf': False})
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
      artist.create()
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
  [data.append({
      'venue_id': sh.venue.id,
      'venue_name': sh.venue.name,
      'start_time': sh.start_time,
      'artist_id': sh.artist.id,
      'artist_name': sh.artist.name,
      'artist_image_link': sh.artist.image_link
    }) for sh in shows]
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
  form = ShowForm(request.form, meta={'csrf': False})
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
        show.create()
        flash('Show was successfully listed!')
    else:
      show.create()
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

