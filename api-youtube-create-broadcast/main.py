import webapp2
import pprint
import httplib2
import sys
import os
import json

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.appengine import OAuth2Decorator
from oauth2client.client import flow_from_clientsecrets
from google.appengine.ext import db
from oauth2client.appengine import CredentialsProperty
from google.appengine.api import users
from google.appengine.api import oauth
from oauth2client.appengine import StorageByKeyName


#Clase de tipo datastore para almacenar la informacion de la credencial del usuario
class CredentialsModel(db.Model):
  credentials = CredentialsProperty()

#Creamos un decorator que sirve para manejar Oauth2 (pantalla de consentimiento al usuario para acceder a su informacion)
decorator = OAuth2Decorator(
	client_id='316673399221-ggs3lp34bnjsa2j59cudbit7nokqmrla.apps.googleusercontent.com',
	client_secret='R_FY5r1XWhqKyOK-2rNmGOsl',
	scope='https://www.googleapis.com/auth/youtube')

#Funcion para obtener el servicio de youtube
def getService():
	flow = flow_from_clientsecrets('client_secrets.json',
		                       scope='https://www.googleapis.com/auth/youtube',
		                       redirect_uri='http://localhost:8080/oauth2callback')

	user = users.get_current_user()
	storage = StorageByKeyName(CredentialsModel, user.user_id(), 'credentials')
	credentials = storage.get()

	http = httplib2.Http()
	http = credentials.authorize(http)

	authenticated_service = build('youtube', 'v3', http=http)
	return authenticated_service

# Creacion del broadcast, colocamos el titulo, fecha de inicio y termino, estatus de privacidad
def insert_broadcast(youtube):
  insert_broadcast_response = youtube.liveBroadcasts().insert(
    part="snippet,status",
    body=dict(
      snippet=dict(
        title="Programacion Avanzada con el maestro Hugo Mendez",
        scheduledStartTime='2015-9-10T15:50:00.000Z', #5HORAS DE DIFERENCIA
        scheduledEndTime='2015-9-10T16:50:00.000Z'
      ),
      status=dict(
        privacyStatus="public"
      )
    )
  ).execute()

  snippet = insert_broadcast_response["snippet"]

  print "ID Broadcast : '%s' con titulo '%s' fue publicado el '%s'." % (
    insert_broadcast_response["id"], snippet["title"], snippet["publishedAt"])
  return insert_broadcast_response["id"]

# Creacion del livestream y configuracion del titulo, formato y tipo de ingestion
def insert_stream(youtube):
  insert_stream_response = youtube.liveStreams().insert(
    part="snippet,cdn",
    body=dict(
      kind='youtube#liveStream',
      snippet=dict(
        title="H++"
        ),
      cdn=dict(
       format="360p",
       ingestionType="rtmp"
    ))).execute()
  snippet = insert_stream_response["snippet"]
  cdn = insert_stream_response["cdn"]

  print "ID Stream '%s' con titulo '%s' ha sido insertado" % (insert_stream_response["id"], snippet["title"])
  print "url rtmp: '%s'." % (cdn["ingestionInfo"]["streamName"])
  print "Stream name: '%s'." % (cdn["ingestionInfo"]["ingestionAddress"])
  return insert_stream_response["id"]

#Asociacion del broadcast con el stream
def bind_broadcast(youtube, broadcast_id, stream_id):
  bind_broadcast_response = youtube.liveBroadcasts().bind(
    part="id,contentDetails",
    id=broadcast_id,
    streamId=stream_id).execute()

  print "Broadcast '%s' fue asociado al stream '%s'." % (bind_broadcast_response["id"], bind_broadcast_response["contentDetails"]["boundStreamId"])
  

class MainPage(webapp2.RequestHandler):
	#solicitar que se haya creado un decorator
	@decorator.oauth_required
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		user = users.get_current_user()

		#verificacion si hay un usuario logeado en su cuenta de google
		if user:
			youtube = getService()
			try:
	    			broadcast_id = insert_broadcast(youtube)
				stream_id = insert_stream(youtube)
				bind_broadcast(youtube, broadcast_id, stream_id)

			#excepciones http como 404, 403, 401 y su descricion 
	  		except HttpError, e:
	    			print "Un error HTTP %d occurrio:\n%s" % (e.resp.status, e.content)
		else:
			self.redirect(users.create_login_url())

app = webapp2.WSGIApplication([
	('/', MainPage),
	(decorator.callback_path, decorator.callback_handler())], 
	debug = True)


