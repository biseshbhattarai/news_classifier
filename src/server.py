from flask import Flask 
from flask_mongoengine import MongoEngine 
from flask import jsonify 
from flask import request
from flask_cors import CORS , cross_origin
import requests 
from bs4 import BeautifulSoup 


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MONGODB_SETTINGS'] = { 
	'db': 'scrapnews',
	'host' : 'localhost', 
	'port': 27017

}

logged_in_user = ['dinesh'] #Session 

db = MongoEngine()
db.init_app(app)



class User(db.Document):
	username = db.StringField()
	email = db.StringField()
	password = db.StringField()

class News(db.Document):
	username = db.StringField()
	news_title = db.StringField()
	news_link = db.StringField()
	classified = db.StringField()
	category = db.StringField()



class Scraper : 

	def __init__(self):
		self.urls = ["https://plakhabar.com/2021", "https://onlinekhabar.com"]


	def scrape_pla(self, pages):
		print("s")
		for i in range(2 , pages):
			print("{}/page/{}/".format(self.urls[0] , i))
			page = requests.get("{}/page/{}/".format(self.urls[0] , i))
			print(page.status_code)
			soup = BeautifulSoup(page.text , 'html.parser')
			articles = soup.find_all('article')
			for news in articles : 
				header = news.find('header')
				links = header.find('a')
				
				
				news_link_page = requests.get(links['href'])
				soups = BeautifulSoup(news_link_page.content , 'html.parser')
				title = soups.title.get_text() 
				print(title) 
				News(username=logged_in_user[0], news_title=title , news_link=links['href'], classified="False", category="").save()
				

	def scrape_onlinekhabar(self, pages):
		counter = 0 
		if counter == 0: 
			page = requests.get("{}/content/news".format(self.urls[1]))
			soup = BeautifulSoup(page.text , 'html.parser')
			divs = soup.find_all('div', class_="relative list__post show_grid--view")
			for div in divs : 
				links = div.find('a')
				
				res = requests.get(links['href'])
				soups = BeautifulSoup(res.content, 'html.parser')
				title = soups.title.get_text()
				News(username=logged_in_user[0], news_title=title , news_link=links['href'], classified="False", category="").save()

			counter += 1 
		if counter >= 1 : 
			for i in range(2, pages):
				page = requests.get("{}/content/news".format(self.urls[1]))
				soup = BeautifulSoup(page.text , 'html.parser')
				divs = soup.find_all('div', class_="relative list__post show_grid--view")
				for div in divs : 
					links = div.find('a')
					
					res = requests.get(links['href'])
					soups = BeautifulSoup(res.content, 'html.parser')
					title = soups.title.get_text()
					News(username=logged_in_user[0], news_title=title , news_link=links['href'], classified="False", category="").save()









@app.route('/')
def index():
	return "Hello , world"

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST': 
		req_data = request.get_json()
		if req_data['email'] is not None and req_data['password'] is not None:
			print(req_data['email'], req_data['password'])
			userr = User.objects(email=req_data['email'], password=req_data['password']).first()
			print(userr)
			if userr.password == req_data['password']:
				logged_in_user.append(req_data['email'])
		else:
			return 'Error'
		return 'Success'


@app.route('/register', methods=['GET'])
def register():
	if request.method == 'POST':
		req_data = request.get_json()
		print(req_data)
		User(username=req_data['fullname'], email=req_data['email'], password=req_data['password']).save()
		return "GET"


@app.route('/current_user', methods=['GET', 'POST'])
def current():
	c_u = ""
	if len(logged_in_user) != 0: 
		c_u = logged_in_user[0]
		print(c_u)
	elif len(logged_in_user) == 0 : 
		c_u = "guest"
	return c_u


@app.route('/logout', methods=['GET', 'POST'])
def logout():
	logged_in_user.pop()
	return "True"

s =Scraper()
s.scrape_onlinekhabar(5)
s.scrape_pla(5)

if __name__ == '__main__':
	app.run(debug=True)
	
