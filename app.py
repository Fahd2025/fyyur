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
    shows = db.relationship('Show',backref='venue',lazy=True, cascade="delete")    

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
    shows = db.relationship('Show',backref='artist',lazy=True, cascade="delete")

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

  if Venue.query.count() == 0:
    seed_venue_data()
    seed_artist_data()
    seed_show_data()

  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  data = []
  areas = db.session.query(Venue.city,Venue.state).group_by(Venue.city,Venue.state).all()
  for area in areas:   
    venues_by_area = db.session.query(Venue.id,Venue.name).filter(Venue.city==area.city,Venue.state==area.state).all()
    area_venues = []
    for venue in venues_by_area: 
      num_upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()
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
    
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee" 
  data = []
  search_term=request.form.get('search_term', '')
  print('search_term = ', search_term)
  search_venues = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()  
  print('search_venues = ', search_venues)
  for venue in search_venues:   
    num_upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()
    data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows":num_upcoming_shows
      })

  response={
    "count": len(search_venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue_row = Venue.query.get(venue_id)
  if venue_row is None:
    abort(404, description="Venue data not found")
    
  venue_shows = db.session.query(Show).filter(Show.venue_id == venue_id).all() 

  past_shows= []
  for show in list(filter(lambda s: s.start_time < datetime.now(), venue_shows)):
     past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
      })

  upcoming_shows= []
  for show in list(filter(lambda s: s.start_time > datetime.now(), venue_shows)):
     upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
      }) 

  data = {
    "id": venue_row.id,
    "name": venue_row.name,
    "genres":venue_row.genres,
    "address": venue_row.address,
    "city": venue_row.city,
    "state": venue_row.state,
    "phone": venue_row.phone,
    "website": venue_row.website,
    "facebook_link":venue_row.facebook_link,
    "seeking_talent": venue_row.seeking_talent,
    "image_link": venue_row.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
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
    db.session.commit()   
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
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = []
  search_term=request.form.get('search_term', '')
  print('search_term = ', search_term)
  search_artists = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()  
  print('search_artists = ', search_artists)
  for artist in search_artists:   
    num_upcoming_shows = db.session.query(Show).filter(Show.artist_id == artist.id, Show.start_time > datetime.now()).count()
    data.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows":num_upcoming_shows
      })

  response={
    "count": len(search_artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artists table, using artist_id 

  artist_row = Artist.query.get(artist_id)
  if artist_row is None:
    abort(404, description="Artist data not found")
    
  artist_shows = db.session.query(Show).filter(Show.artist_id == artist_id).all() 

  past_shows= []
  for show in list(filter(lambda s: s.start_time < datetime.now(), artist_shows)):
     past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
      })

  upcoming_shows= []
  for show in list(filter(lambda s: s.start_time > datetime.now(), artist_shows)):
     upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
      }) 

  data = {
    "id": artist_row.id,
    "name": artist_row.name,
    "genres":artist_row.genres,
    "city": artist_row.city,
    "state": artist_row.state,
    "phone": artist_row.phone,
    "website": artist_row.website,
    "facebook_link":artist_row.facebook_link,
    "seeking_venue": artist_row.seeking_venue,
    "image_link": artist_row.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

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

  data = []

  upcoming_shows = db.session.query(Show).filter(Show.start_time > datetime.now()).all()  
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

  venue_id = request.form.get('venue_id')
  venue_row = Venue.query.get(venue_id)
  venue_name = venue_row.name

  artist_id = request.form.get('artist_id')
  artist_row = Artist.query.get(artist_id)
  artist_name = artist_row.name

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
      flash('An error occurred. Show ' + artist_name + ' playing at ' + venue_name + ' at ' + request.form.get('start_time') +  ' could not be listed.')  
    else:
      # on successful db insert, flash success
      flash('Show ' + artist_name + ' playing at ' + venue_name + ' at ' + request.form.get('start_time') +  ' was successfully listed!')  

  else:
    flash('Venue id or Artist id not found ')  
    
  return render_template('pages/home.html')

#  Seed inital data 
#  ----------------------------------------------------------------

def seed_venue_data():
  venue1= Venue(
    #id= 1,
    name= "The Musical Hop",
    genres= ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    address= "1015 Folsom Street",
    city= "San Francisco",
    state= "CA",
    phone= "123-123-1234",
    website= "https://www.themusicalhop.com",
    facebook_link= "https://www.facebook.com/TheMusicalHop",
    seeking_talent= True,
    seeking_description= "We are on the lookout for a local artist to play every two weeks. Please call us.",
    image_link= "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"   
  )
  venue2= Venue(
    #id= 2,
    name= "The Dueling Pianos Bar",
    genres= ["Classical", "R&B", "Hip-Hop"],
    address= "335 Delancey Street",
    city= "New York",
    state= "NY",
    phone= "914-003-1132",
    website= "https://www.theduelingpianos.com",
    facebook_link= "https://www.facebook.com/theduelingpianos",
    seeking_talent= False,
    image_link= "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80"  
  )
  venue3= Venue(
    #id= 3,
    name= "Park Square Live Music & Coffee",
    genres= ["Rock n Roll", "Jazz", "Classical", "Folk"],
    address= "34 Whiskey Moore Ave",
    city= "San Francisco",
    state= "CA",
    phone= "415-000-1234",
    website= "https://www.parksquarelivemusicandcoffee.com",
    facebook_link= "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    seeking_talent= False,
    image_link= "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80"   
  )

  try:   
    db.session.add(venue1)
    db.session.add(venue2)
    db.session.add(venue3)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())   
  finally:
    db.session.close()

def seed_artist_data():
  artist1= Artist(
    #id= 1,
    name= "Guns N Petals",
    genres= ["Rock n Roll"],
    city= "San Francisco",
    state= "CA",
    phone= "326-123-5000",
    website= "https://www.gunsnpetalsband.com",
    facebook_link= "https://www.facebook.com/GunsNPetals",
    seeking_venue= True,
    seeking_description= "Looking for shows to perform at in the San Francisco Bay Area!",
    image_link= "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"   
  )
  artist2= Artist(
    #id= 2,
    name= "Matt Quevedo",
    genres= ["Jazz"],
    city= "New York",
    state= "NY",
    phone= "300-400-5000",
    facebook_link= "https://www.facebook.com/mattquevedo923251523",
    seeking_venue= False,
    image_link= "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80"    
  )
  artist3= Artist(
    #id= 3,
    name= "The Wild Sax Band",
    genres= ["Jazz", "Classical"],
    city= "San Francisco",
    state= "CA",
    phone= "432-325-5432",
    seeking_venue= False,
    image_link= "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"
  )

  try:   
    db.session.add(artist1)
    db.session.add(artist2)
    db.session.add(artist3)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())   
  finally:
    db.session.close()

def seed_show_data():
  show1= Show(
    venue_id= 1,
    artist_id= 1,
    start_time= datetime(2019, 5, 21, 21, 30) 
  )
  show2= Show(
    venue_id= 3,
    artist_id= 2,
    start_time= datetime(2019, 6, 15, 23, 0) 
  )
  show3= Show(
    venue_id= 3,
    artist_id= 3,
    start_time= datetime(2035, 4, 1, 20, 0) 
  )
  show4= Show(
    venue_id= 3,
    artist_id= 3,
    start_time= datetime(2035, 4, 15, 20, 0) 
  )

  try:   
    db.session.add(show1)
    db.session.add(show2)
    db.session.add(show3)
    db.session.add(show4)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())   
  finally:
    db.session.close() 


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
