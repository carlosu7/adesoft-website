import webapp2
import calendar
import time
import datetime
import mexTime

datetime.timedelta(hours=-5)

def lessFiveHours(ano, mes, dia, hora, minuto):
	date = ano + "-" + mes + "-" + dia + " " + hora +":" + minuto
	return str(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M") + datetime.timedelta(hours=5))

def youtubeTimeFormat(date):
	cadena = ""
	for i in range(0, len(date)):	
		if i == 10:
			cadena = cadena + "T"	
		else:
			cadena = cadena + date[i]
	return cadena
	

class MainPage(webapp2.RequestHandler):
	def get(self):
		today = str(datetime.datetime.now() + datetime.timedelta(hours=-5))
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write("UTC Time :"+str(datetime.datetime.now())+'\n')
		self.response.out.write("Mexico Time: " +str(today) +'\n' )

		time = mexTime.mexTime()

		self.response.out.write(time.getAno()+'\n')
		self.response.out.write(time.getMes()+'\n')
		self.response.out.write(time.getDia()+'\n')
		self.response.out.write(time.getHora()+'\n')
		self.response.out.write(time.getMinuto()+'\n')

		date = youtubeTimeFormat( lessFiveHours(time.getAno(), time.getMes(), time.getDia(), time.getHora(), time.getMinuto()) ) + '.000Z'

		self.response.out.write(youtubeTimeFormat(date)+'\n')
		self.response.out.write('2014-01-31T00:00:00.000Z'+'\n')

app = webapp2.WSGIApplication([('/', MainPage)], debug = True)
