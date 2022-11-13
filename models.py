from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Venue(db.Model):
  __tablename__ = 'venues'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=True)
  genres = db.Column(db.ARRAY(db.String), nullable=False)
  image_link = db.Column(db.String(500), nullable=True)
  facebook_link = db.Column(db.String(120), nullable=True) 
  # TODO: implement any missing fields, as a database migration using Flask-Migrate
  website_link = db.Column(db.String(100), nullable=True) 
  seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String(500), nullable=True)
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
  genres = db.Column(db.ARRAY(db.String), nullable=False)
  image_link = db.Column(db.String(500), nullable=True)
  # TODO: implement any missing fields, as a database migration using Flask-Migrate
  facebook_link = db.Column(db.String(120), nullable=True)
  website_link = db.Column(db.String(100), nullable=True)
  seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String(500), nullable=True)
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
