#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
import sys
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# connect to a local postgresql database

migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate  
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))

    seeking_talent = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(500))   
    shows = db.relationship('Show',backref='venue',lazy=True)    

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

     # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))

    seeking_venue = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show',backref='artist',lazy=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)   
    artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
    venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)   
    start_time = db.Column(db.DateTime, nullable=False)

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  current_time = datetime.now()
  areas = db.session.query(Venue.city,Venue.state).group_by(Venue.city,Venue.state).all()
  for area in areas:   
    venues_by_area = db.session.query(Venue.id,Venue.name).filter(Venue.city==area.city,Venue.state==area.state).all()
    area_venues = []
    for venue in venues_by_area: 
      num_upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue.id, Show.start_time > current_time).count()
      area_venues.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows":num_upcoming_shows
      })

    new_area = {
        "city": area.city,
        "state": area.state,
        "venues": area_venues
    }
    data.append(new_area) 

  print(data)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
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
    "upcoming_shows_count": 1,
  }
  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    # create new Venue object with recived values
    new_venue_row = Venue(
        name = request.form.get('name'),
        city = request.form.get('city'),
        state = request.form.get('state'), 
        address = request.form.get('address'), 
        phone = request.form.get('phone'), 
        genres = request.form.getlist('genres'), 
        facebook_link = request.form.get('facebook_link'),
        website  = request.form.get('website'),
        image_link = request.form.get('image_link')
        )    
    db.session.add(new_venue_row)
    
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())   
  finally:
    db.session.close()

  if error:
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')  
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form.get('name') + ' was successfully listed!')
    
  return render_template('pages/home.html')

#  Update Venue
#  ----------------------------------------------------------------  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  edit_venue_row = Venue.query.get(venue_id)
  if edit_venue_row is None:
    abort(404, description="Venue data not found")
  
  # populate form with values from venue with ID <venue_id>
  form = VenueForm()
  form.name.data = edit_venue_row.name
  form.city.data = edit_venue_row.city
  form.state.data = edit_venue_row.state  
  form.address.data = edit_venue_row.address
  form.phone.data = edit_venue_row.phone
  form.genres.data = edit_venue_row.genres 
  form.facebook_link.data = edit_venue_row.facebook_link
  form.website.data = edit_venue_row.website
  form.image_link.data = edit_venue_row.image_link
  
  venue={
    "id": edit_venue_row.id
  }  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    edit_venue_row = Venue.query.get(venue_id)

    # update existing Venue with recived values
    edit_venue_row.name = request.form.get('name')    
    edit_venue_row.city = request.form.get('city')
    edit_venue_row.state = request.form.get('state')
    edit_venue_row.address = request.form.get('address')    
    edit_venue_row.phone = request.form.get('phone')
    edit_venue_row.genres = request.form.getlist('genres')    
    edit_venue_row.facebook_link = request.form.get('facebook_link')
    edit_venue_row.website = request.form.get('website')
    edit_venue_row.image_link = request.form.get('image_link') 

    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())    
  finally:
    db.session.close()

  if error:
    # on unsuccessful db update, flash an error instead.
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be updated.')     
    return redirect(url_for('edit_venue', venue_id=venue_id))
  else:
    # on successful db update, flash success
    flash('Venue ' + request.form.get('name') + ' was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id)) 

#  Delete Venue
#  ----------------------------------------------------------------  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  delete_venue_row = Venue.query.get(venue_id)
  venue_name = delete_venue_row.name
  try:
    db.session.delete(delete_venue_row)
    # db.session.commit()   
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())    
  finally:
    db.session.close()

  if error:
    # on unsuccessful db delete, flash an error instead.
    flash('An error occurred. Venue ' + venue_name + ' could not be deleted.')  
  else:
    # on successful db delete, flash success
    flash('Venue ' + venue_name + ' was successfully deleted!')
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[{
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
  response={
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
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
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
  data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    # create new Artist object with recived values
    new_artist_row = Artist(
        name = request.form.get('name'),
        city = request.form.get('city'),
        state = request.form.get('state'), 
        phone = request.form.get('phone'), 
        genres = request.form.getlist('genres'), 
        facebook_link = request.form.get('facebook_link'),
        website  = request.form.get('website'),
        image_link = request.form.get('image_link')
        )    
    db.session.add(new_artist_row)    
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())   
  finally:
    db.session.close()

  if error:
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')  
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form.get('name') + ' was successfully listed!')
    
  return render_template('pages/home.html')

#  Update Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  edit_artist_row = Artist.query.get(artist_id)
  if edit_artist_row is None:
    abort(404, description="Artist data not found")
  
  # populate form with values from artist with ID <artist_id>
  form = ArtistForm()
  form.name.data = edit_artist_row.name
  form.city.data = edit_artist_row.city
  form.state.data = edit_artist_row.state  
  form.phone.data = edit_artist_row.phone
  form.genres.data = edit_artist_row.genres 
  form.facebook_link.data = edit_artist_row.facebook_link
  form.website.data = edit_artist_row.website
  form.image_link.data = edit_artist_row.image_link
  
  artist={
    "id": edit_artist_row.id
  }  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    edit_artist_row = Artist.query.get(artist_id)

    # update existing Artist with recived values
    edit_artist_row.name = request.form.get('name')    
    edit_artist_row.city = request.form.get('city')
    edit_artist_row.state = request.form.get('state') 
    edit_artist_row.phone = request.form.get('phone')
    edit_artist_row.genres = request.form.getlist('genres')    
    edit_artist_row.facebook_link = request.form.get('facebook_link')
    edit_artist_row.website = request.form.get('website')
    edit_artist_row.image_link = request.form.get('image_link') 

    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())    
  finally:
    db.session.close()

  if error:
    # on unsuccessful db update, flash an error instead.
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be updated.')     
    return redirect(url_for('edit_artist', artist_id=artist_id))
  else:
    # on successful db update, flash success
    flash('Artist ' + request.form.get('name') + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id)) 

#  Delete Artist
#  ----------------------------------------------------------------  

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  error = False
  delete_artist_row = Artist.query.get(artist_id)
  artist_name = delete_artist_row.name
  try:
    db.session.delete(delete_artist_row)
    db.session.commit()   
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())    
  finally:
    db.session.close()

  if error:
    # on unsuccessful db delete, flash an error instead.
    flash('An error occurred. Artist ' + artist_name + ' could not be deleted.')  
  else:
    # on successful db delete, flash success
    flash('Artist ' + artist_name + ' was successfully deleted!')

  return redirect(url_for('artists'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]

  data = []
  current_time = datetime.now()
  upcoming_shows = db.session.query(Show).filter(
      Show.start_time > current_time).all()
  for show in upcoming_shows:
     data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
      })

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
  # TODO: insert form data as a new Show record in the db, instead
  error = False

  venue_id = request.form.get('venue_id'), 
  venue_row = Venue.query.get(venue_id)
  venue_name = venue_row.name

  artist_id = request.form.get('artist_id'),
  artist_row = Artist.query.get(artist_id)

  if not(venue_row is None or artist_row is None):
    try: 
      # create new Show object with recived values
      new_show_row = Show(
          artist_id = artist_id,
          venue_id = venue_id,        
          start_time = request.form.get('start_time')
          )    
      db.session.add(new_show_row)    
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())   
    finally:
      db.session.close()
      
    if error:
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show ' + venue_name + ' at ' + request.form.get('start_time') + ' could not be listed.')  
    else:
      # on successful db insert, flash success
      flash('Show ' + venue_name + ' at ' + request.form.get('start_time') + ' was successfully listed!')  

  else:
    flash('Venue id or Artist id not found ')  
    
  return render_template('pages/home.html')

#  Error Handler
#  ----------------------------------------------------------------

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
