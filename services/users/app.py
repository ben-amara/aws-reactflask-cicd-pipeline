from flask import Flask, request, send_file
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
import requests, zipfile
import six
import pdb
import json
import math
import time
from selenium import webdriver
import stripe
import datetime
from datetime import date
from twilio.rest import Client
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import ChatGrant
import pandas as pd
import zipfile
import csv
from io import TextIOWrapper
import os
from requests.auth import HTTPBasicAuth
import bcrypt
import asyncio
from multiprocessing.dummy import Pool as ThreadPool
from itertools import product
from functools import partial
import atexit
import subprocess

from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://uce5di2donurro:p9fa59e011c600b115ebef276799cdf1dc0221c5cac42a7396d53db7aee1876ef@ec2-107-20-88-158.compute-1.amazonaws.com:5432/d1t58iafvvkq25'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app, support_credentials=True)


stripe.api_key = "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"

GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google_chrome'
CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'

class WalmartProduct(db.Model):
    __tablename__ = "walmart_products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    url = db.Column(db.String(120), unique=True)
    upc = db.Column(db.String(120), unique=True)
    thumbnail = db.Column(db.String(120), unique=True)
    thumbnail2 = db.Column(db.String(120), unique=True)
    supplier_price = db.Column(db.String(120), unique=True)
    supplier_url = db.Column(db.String(120), unique=True)
    sku = db.Column(db.String(120), unique=True)
    removed = db.Column(db.Boolean)

    orders = db.relationship("Order", back_populates="product", uselist=False)

    def __init__(self, name, url, sku, supplier_price, supplier_url):
        self.name = name
        self.url = url
        self.sku = sku
        self.supplier_price = supplier_price
        self.supplier_url = supplier_url

    def as_dict():
        jsonProducts = []
        products = WalmartProduct.query.all()
        for product in products:
          jsonProducts.append({c.name: getattr(product, c.name) for c in product.__table__.columns}) 
        return json.dumps(jsonProducts)

class Export(db.Model):
    __tablename__ = "exports"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    url = db.Column(db.String(120), unique=True)
    upc = db.Column(db.String(120), unique=True)
    thumbnail = db.Column(db.String(120), unique=True)
    thumbnail2 = db.Column(db.String(120), unique=True)
    supplier_price = db.Column(db.String(120), unique=True)
    supplier_url = db.Column(db.String(120), unique=True)
    sku = db.Column(db.String(120), unique=True)
    removed = db.Column(db.Boolean)

    def __init__(self, name, url, sku, supplier_price, supplier_url):
        self.name = name
        self.url = url
        self.sku = sku
        self.supplier_price = supplier_price
        self.supplier_url = supplier_url

    def as_dict():
        jsonProducts = []
        products = Export.query.all()
        for product in products:
          jsonProducts.append({c.name: getattr(product, c.name) for c in product.__table__.columns}) 
        return json.dumps(jsonProducts)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=False)
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(120), unique=True)

    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    store = db.relationship("Store", back_populates="users")

    def __init__(self, name, username, password):
      self.username = username
      self.name = name
      self.password = password

class Store(db.Model):
    __tablename__ = "stores"
    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.String(120), unique=True)
    walmart_key = db.Column(db.String(120), unique=True)
    walmart_secret = db.Column(db.String(120), unique=True)
    amazon_username = db.Column(db.String(120), unique=True)
    amazon_password = db.Column(db.String(120), unique=True)
    oa_username = db.Column(db.String(120), unique=True)
    oa_password = db.Column(db.String(120), unique=True)
    orders = db.relationship("Order", back_populates="store", uselist=False)
    cell = db.Column(db.String(120), unique=True)
    convo = db.Column(db.String(120), unique=True)

    users = db.relationship("User", back_populates="store")

    def __init__(self, owner_name):
        self.owner_name = owner_name

    def as_dict():
        jsonStores = []
        stores = Store.query.all()
        for store in stores:
          jsonStores.append({c.name: getattr(store, c.name) for c in store.__table__.columns}) 
        return json.dumps(jsonStores)

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.String(120), primary_key=True)
    name = db.Column(db.String(120), unique=True)
    url = db.Column(db.String(120), unique=True)
    upc = db.Column(db.String(120), unique=True)
    thumbnail = db.Column(db.String(120), unique=True)
    supplier_price = db.Column(db.String(120), unique=True)
    supplier_url = db.Column(db.String(120), unique=True)
    sku = db.Column(db.String(120), unique=True)
    purchase_price = db.Column(db.String(120), unique=True)
    profit = db.Column(db.String(120), unique=True)
    supplier_order_id = db.Column(db.String(120), unique=True)
    status = db.Column(db.String(120), unique=True)
    raw_json = db.Column(db.JSON, default={})

    product_id = db.Column(db.Integer, db.ForeignKey('walmart_products.id'))
    product = db.relationship("WalmartProduct", back_populates="orders")

    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    store = db.relationship("Store", back_populates="orders")

    def __init__(self, id, name, url, sku, purchase_price):
        self.id = id
        self.name = name
        self.url = url
        self.sku = sku
        self.purchase_price = purchase_price

    def as_dict():
        jsonOrders = []
        orders = Order.query.order_by(Order.id.desc()).all()
        for order in orders:
          jsonOrders.append({c.name: getattr(order, c.name) for c in order.__table__.columns}) 
        return json.dumps(jsonOrders)

def addOrderToDB(store, order):
    id = order['purchaseOrderId'] 
    quantity = len(order['orderLines']['orderLine'])
    name = order['orderLines']['orderLine'][0]['item']['productName']
    walmart_url = 'https://www.walmart.com/ip/' +  order['orderLines']['orderLine'][0]['item']['sku'] 
    sku = order['orderLines']['orderLine'][0]['item']['sku']
    purchase_price = order['orderLines']['orderLine'][0]['charges']['charge'][0]['chargeAmount']['amount'] * quantity
    status = order['orderLines']['orderLine'][0]['orderLineStatuses']['orderLineStatus'][0]['status']

    current_order = Order.query.filter_by(id=id).first()
    matching_product = WalmartProduct.query.filter_by(upc=str(sku).split('-')[0]).first()
    
    if matching_product is None:
      matching_product = WalmartProduct.query.filter_by(sku=str(sku)).first()

      if matching_product is None:

        url2 = "https://marketplace.walmartapis.com/v3/token"

        payload='grant_type=client_credentials'
        headers = {
          'WM_SVC.NAME': 'TEST',
          'WM_QOS.CORRELATION_ID': '1234567890',
          'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = requests.request("POST", url2, headers=headers, auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret), data=payload)

        if '<accessToken>' in response.text:
          access_token = response.text.split('<accessToken>')[1].split('</accessToken>')[0]

        print('Access: ' + access_token)
        
        headers3 = {
            'WM_SVC.NAME': 'TEST',
            'WM_SEC.ACCESS_TOKEN': access_token,
            'WM_QOS.CORRELATION_ID': '1234567890',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        }

        if sku:
          response3 = requests.request("GET", 'https://marketplace.walmartapis.com/v3/items/walmart/search?upc=' + str(sku).split('-')[0],  auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret), headers=headers3)
          syncCentricKey = 'NGtjAvrxWZhD9DbcY5VJxPfTzvXiYqJEOEFfwiYUPuQleyeLycQrZWgSYt7b'

          url = "https://v3.synccentric.com/api/v3/products/search"

          headers = {}
          headers["Authorization"] = "Bearer " + syncCentricKey
          headers["Content-Type"] = "application/x-www-form-urlencoded"

          data = "identifier[]=" + str(sku).split('-')[0] + "&type=upc&locale=US"

          resp = requests.post(url, headers=headers, data=data)

          if resp.status_code == 200 and response3.text != '{}':
            new_product = WalmartProduct(name, walmart_url, response3.json()['items'][0]['itemId'], resp.json()['data'][0]['attributes']['buybox_new_listing_price'], 'https://www.amazon.com/dp/' + resp.json()['data'][0]['attributes']['asin'])
            new_product.thumbnail = response3.json()['items'][0]['images'][0]['url']
            new_product.thumbnail2 = resp.json()['data'][0]['attributes']['medium_image']
            new_product.upc = str(sku).split('-')[0]
            matching_product = new_product
            db.session.add(new_product)
            db.session.commit()
    elif current_order:
        if matching_product:
          current_order.supplier_price = matching_product.supplier_price
          if '/ip/' in matching_product.url:
            current_order.url = matching_product.url
          elif '/ip' in matching_product.url:
            current_order.url = matching_product.url.replace('/ip', '/ip/')

        current_order.store_id = store.id
        if current_order.status:
            print('Already Exists')
            if matching_product and current_order.upc is None:     
                current_order.upc = matching_product.upc
                current_order.supplier_url = matching_product.supplier_url
                current_order.product_id = matching_product.id
                current_order.raw_json = order
            elif current_order.raw_json is None:
                current_order.raw_json = order
            elif current_order.supplier_price is None:
              current_order.supplier_price = matching_product.supplier_price
        else:
            current_order.status = status
            if matching_product: 
                current_order.upc = matching_product.upc
                current_order.supplier_url = matching_product.supplier_url
                current_order.product_id = matching_product.id
                if '/ip/' in matching_product.url:
                  current_order.url = matching_product.url
                elif '/ip' in matching_product.url:
                  current_order.url = matching_product.url.replace('/ip', '/ip/')

                if current_order.supplier_price is None:
                  current_order.supplier_price = matching_product.supplier_price
            
    else:
        new_order = Order(id, name, walmart_url, sku, purchase_price)
        new_order.status = status
        new_order.raw_json = order
        new_order.store_id = store.id

        if matching_product:     
            new_order.upc = matching_product.upc
            new_order.supplier_url = matching_product.supplier_url
            new_order.product_id = matching_product.id

            syncCentricKey = 'NGtjAvrxWZhD9DbcY5VJxPfTzvXiYqJEOEFfwiYUPuQleyeLycQrZWgSYt7b'

            headers = {}
            headers["Authorization"] = "Bearer " + syncCentricKey
            headers["Content-Type"] = "application/x-www-form-urlencoded"

            url2 = "https://v3.synccentric.com/api/v3/products/search"

            data2 = "identifier[]=" + product.upc + "&type=upc&locale=US"

            resp2 = requests.post(url2, headers=headers, data=data2)

            new_export = Export(matching_product.name, matching_product.url, matching_product.sku, float(resp2.json()['data'][0]['attributes']['lowest_new_price']), matching_product.supplier_url)
            db.session.add(new_export)
            db.session.commit()

            # new_order.supplier_price = matching_product.supplier_price

            if '/ip/' in matching_product.url:
              new_order.url = matching_product.url
            elif '/ip' in matching_product.url:
              new_order.url = matching_product.url.replace('/ip', '/ip/')
          
        syncCentricKey = 'NGtjAvrxWZhD9DbcY5VJxPfTzvXiYqJEOEFfwiYUPuQleyeLycQrZWgSYt7b'

        url = "https://v3.synccentric.com/api/v3/products/search"

        headers = {}
        headers["Authorization"] = "Bearer " + syncCentricKey
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        data = "identifier[]=" + str(sku).split('-')[0] + "&type=upc&locale=US"

        resp = requests.post(url, headers=headers, data=data)

        if resp.status_code == 200:
          print('Found product - Checking Price')
          
          try:
            if 'out of stock' not in resp.json()['data'][0]['attributes']['lowest_offer_listings'].lower() and resp.json()['data'][0]['attributes']['lowest_offer_listings'].lower() != '"[]"':
              lowest_merchant = float(json.loads(resp.json()['data'][0]['attributes']['lowest_offer_listings'])[0]['Price']['LandedPrice']['Amount'])
              lowest_fba = float(json.loads(resp.json()['data'][0]['attributes']['buybox_new_landed_price']))

              if (lowest_fba <= lowest_merchant):
                new_order.supplier_price = lowest_fba
              elif lowest_merchant != 0:
                new_order.supplier_price = lowest_merchant
          
            url2 = "https://marketplace.walmartapis.com/v3/token"

            payload='grant_type=client_credentials'
            headers = {
              'WM_SVC.NAME': 'TEST',
              'WM_QOS.CORRELATION_ID': '1234567890',
              'Content-Type': 'application/x-www-form-urlencoded',
            }

            response = requests.request("POST", url2, headers=headers, auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret), data=payload)

            if '<accessToken>' in response.text:
              access_token = response.text.split('<accessToken>')[1].split('</accessToken>')[0]

            print('Access: ' + access_token)
            
            headers3 = {
                'WM_SVC.NAME': 'TEST',
                'WM_SEC.ACCESS_TOKEN': access_token,
                'WM_QOS.CORRELATION_ID': '1234567890',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
            }

            if sku:
              
              response3 = requests.request("GET", 'https://marketplace.walmartapis.com/v3/items/walmart/search?upc=' + str(sku).split('-')[0],  auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret), headers=headers3)
              new_order.supplier_url = 'https://www.amazon.com/dp/' + resp.json()['data'][0]['attributes']['asin']
              lowest_merchant = float(json.loads(resp.json()['data'][0]['attributes']['lowest_offer_listings'])[0]['Price']['LandedPrice']['Amount'])
              lowest_fba = float(json.loads(resp.json()['data'][0]['attributes']['buybox_new_landed_price']))

              if (lowest_fba <= lowest_merchant):
                new_order.supplier_price = lowest_fba
              elif lowest_merchant != 0:
                new_order.supplier_price = lowest_merchant
              
              new_product = WalmartProduct(name, 'https://www.walmart.com/ip/' + response3.json()['items'][0]['itemId'], response3.json()['items'][0]['itemId'], resp.json()['data'][0]['attributes']['buybox_new_listing_price'], 'https://www.amazon.com/dp/' + resp.json()['data'][0]['attributes']['asin'])
              new_product.thumbnail = response3.json()['items'][0]['images'][0]['url']
              new_product.thumbnail2 = resp.json()['data'][0]['attributes']['medium_image']
              new_product.upc = str(sku).split('-')[0]
              matching_product = new_product
              db.session.add(new_product)
              db.session.commit()

              
              syncCentricKey = 'NGtjAvrxWZhD9DbcY5VJxPfTzvXiYqJEOEFfwiYUPuQleyeLycQrZWgSYt7b'

              headers = {}
              headers["Authorization"] = "Bearer " + syncCentricKey
              headers["Content-Type"] = "application/x-www-form-urlencoded"

              url2 = "https://v3.synccentric.com/api/v3/products/search"

              data2 = "identifier[]=" + product.upc + "&type=upc&locale=US"

              resp2 = requests.post(url2, headers=headers, data=data2)

              new_export = Export(matching_product.name, matching_product.url, matching_product.sku, float(resp2.json()['data'][0]['attributes']['lowest_new_price']), matching_product.supplier_url)
              db.session.add(new_export)
              db.session.commit()

          except:
            print('Out of Stock')

        db.session.add(new_order)

    db.session.commit()

@app.route('/getExports')
def exports():
  stores = Store.query.all()


  for store in stores:
    for product in json.loads(Export.as_dict()):
      pdb.set_trace()

def check_orders():
    stores = Store.query.all()
    orders = []

    for store in stores:
      url2 = "https://marketplace.walmartapis.com/v3/token"

      payload='grant_type=client_credentials'
      headers = {
          'WM_SVC.NAME': 'TEST',
          'WM_QOS.CORRELATION_ID': '1234567890',
          'Content-Type': 'application/x-www-form-urlencoded',
      }

      response = requests.request("POST", url2, headers=headers, auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret), data=payload)

      if '<accessToken>' in response.text:
        access_token = response.text.split('<accessToken>')[1].split('</accessToken>')[0]

        print('Access: ' + access_token)

        url3 = "https://marketplace.walmartapis.com/v3/orders"

        payload3='grant_type=client_credentials'
        headers3 = {
            'WM_SVC.NAME': 'TEST',
            'WM_SEC.ACCESS_TOKEN': access_token,
            'WM_QOS.CORRELATION_ID': '1234567890',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        }

        response2 = requests.request("GET", url3, auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret), headers=headers3, data=payload3)
        
        try:
          i = 0
          totalOrders = response2.json()['list']['meta']['totalCount']
          
          while i <= totalOrders:
            if response2.json() and response2.json()['list']:

              url2 = "https://marketplace.walmartapis.com/v3/token"

              payload='grant_type=client_credentials'
              headers = {
                  'WM_SVC.NAME': 'TEST',
                  'WM_QOS.CORRELATION_ID': '1234567890',
                  'Content-Type': 'application/x-www-form-urlencoded',
              }

              response = requests.request("POST", url2, headers=headers, auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret), data=payload)
              
              if '<accessToken>' in response.text:
                access_token = response.text.split('<accessToken>')[1].split('</accessToken>')[0]

                orders = response2.json()['list']['elements']['order']
                pool = ThreadPool(10)
                results = pool.map(partial(addOrderToDB, store), orders)
                # results = pool.starmap(addOrderToDB, product(orders, store))#close the pool and wait for the work to finish
                pool.close()
                pool.join()

                i = i+len(orders)
            
            if response2.json()['list']['meta']['nextCursor'] and (i <= totalOrders):
              response2 = requests.request("GET", url3 + response2.json()['list']['meta']['nextCursor'], auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret), headers=headers3, data=payload3)
            else:
              break
        except:
          continue
    else:
      print('No Orders')
    return 'Completed'

@app.route('/seeAllProducts')
def seeAllProducts():
  rows = []
  with open('allProducts.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['NAME', 'UPC', 'ASIN'])
    products = json.loads(WalmartProduct.as_dict())
    i = 0
    for product in products:
      i = i + 1
      print(str(i) + '/' + str(len(products)))
      try:
        if product['upc']:
          if '-' in product['upc']:
            print(product['name'])
            rows.append([product['name'], product['upc'].split('-')[0]])
          elif len(product['upc']) == 12:
            print(product['name'])
            rows.append([product['name'], product['upc']])
        else:
          syncCentricKey = 'NGtjAvrxWZhD9DbcY5VJxPfTzvXiYqJEOEFfwiYUPuQleyeLycQrZWgSYt7b'

          url = "https://v3.synccentric.com/api/v3/products/search"

          headers = {}
          headers["Authorization"] = "Bearer " + syncCentricKey
          headers["Content-Type"] = "application/x-www-form-urlencoded"


          if '/dp/' in product['supplier_url']:
            print(product['name'])
            if '/' in product['supplier_url'].split('/dp/')[1]:
              print('Using ASIN')
              # data = "identifier[]=" + product['supplier_url'].split('/dp/')[1].split('/')[0] + "&type=upc&locale=US"

              # resp = requests.post(url, headers=headers, data=data)

              # if resp.status_code == 200:
              #   print('Success with Synccentric')
              #   buybox_price = float(resp.json()['data'][0]['attributes']['buybox_new_landed_price'])
              #   merchant_price = float(json.loads(resp.json()['data'][0]['attributes']['lowest_offer_listings'])[0]['Price']['LandedPrice']['Amount'])

              rows.append([product['name'],  '', product['supplier_url'].split('/dp/')[1].split('/')[0]])
            else: 
              print('Using ASIN')
              # data = "identifier[]=" + product['supplier_url'].split('/dp/')[1] + "&type=upc&locale=US"

              # resp = requests.post(url, headers=headers, data=data)

              # if resp.status_code == 200:
              #   print('Success with Synccentric')
              #   buybox_price = float(resp.json()['data'][0]['attributes']['buybox_new_landed_price'])
              #   merchant_price = float(json.loads(resp.json()['data'][0]['attributes']['lowest_offer_listings'])[0]['Price']['LandedPrice']['Amount'])
              rows.append([product['name'],   '', product['supplier_url'].split('/dp/')[1]])
          elif '/dp' in product['supplier_url']:
            print(product['name'])
            if '/' in product['supplier_url'].split('/dp')[1]:
              print('Using ASIN')
              # data = "identifier[]=" + product['supplier_url'].split('/dp')[1].split('/')[0] + "&type=asin&locale=US"

              # resp = requests.post(url, headers=headers, data=data)

              # if resp.status_code == 200:
              #   print('Success with Synccentric')
                # buybox_price = float(resp.json()['data'][0]['attributes']['buybox_new_landed_price'])
                # merchant_price = float(json.loads(resp.json()['data'][0]['attributes']['lowest_offer_listings'])[0]['Price']['LandedPrice']['Amount'])
                # # pdb.set_trace()
              rows.append([product['name'],  '', product['supplier_url'].split('/dp')[1].split('/')[0]])
            else: 
              print('Using ASIN')
              # data = "identifier[]=" + product['supplier_url'].split('/dp')[1] + "&type=asin&locale=US"

              # resp = requests.post(url, headers=headers, data=data)

              # if resp.status_code == 200:
              #   print('Success with Synccentric')
              #   buybox_price = float(resp.json()['data'][0]['attributes']['buybox_new_landed_price'])
              #   merchant_price = float(json.loads(resp.json()['data'][0]['attributes']['lowest_offer_listings'])[0]['Price']['LandedPrice']['Amount'])
                  # pdb.set_trace()
              rows.append([product['name'], '', product['supplier_url'].split('/dp')[1]])
      except:
        continue 

    for row in rows:
      writer.writerow(row)   

  return send_file('allProducts.csv')  

@app.route('/importProducts')
def importProducts():
  products = WalmartProduct.query.all()

  data = {'identifiers': []}

  for product in products:

    data['identifiers'].append({'identifier': product.upc, 'type': 'upc'})

  syncCentricKey = 'NGtjAvrxWZhD9DbcY5VJxPfTzvXiYqJEOEFfwiYUPuQleyeLycQrZWgSYt7b'

  url = "https://v3.synccentric.com/api/v3/products"

  headers = {}
  headers["Authorization"] = "Bearer " + syncCentricKey
  headers["Content-Type"] = "application/json"

  resp = requests.post(url, headers=headers, json=data)

@app.route('/allOrders')
def allOrders():
  if request.args.get('id'):
    data = []

    for order in json.loads(Order.as_dict()):
      if order['store_id'] == int(request.args.get('id')):
        data.append(order)

    return json.dumps(data)
  else:
    return Order.as_dict()

  # stores = Store.query.all()
  # for store in stores:
  #   try:
  #     url2 = "https://marketplace.walmartapis.com/v3/token"

  #     payload='grant_type=client_credentials'
  #     headers = {
  #       'WM_SVC.NAME': 'TEST',
  #       'WM_QOS.CORRELATION_ID': '1234567890',
  #       'Content-Type': 'application/x-www-form-urlencoded',
  #     }
  #     response = requests.request("POST", url2, headers=headers, auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret), data=payload)
  #     access_token = response.text.split('<accessToken>')[1].split('</accessToken>')[0]

  #     todaysDate = datetime.datetime.today().strftime("%Y-%m-%d")

  #     url3 = "https://marketplace.walmartapis.com/v3/orders?limit=300&createdStartDate=" + todaysDate
  #     headers3 = {
  #       'WM_SVC.NAME': 'TEST',
  #       'WM_SEC.ACCESS_TOKEN': access_token,
  #       'WM_QOS.CORRELATION_ID': '1234567890',
  #       'Content-Type': 'application/json',
  #       'Accept': 'application/json',
  #     }
  #     response2 = requests.request("GET", url3, headers=headers3, auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret))

  #     if response2.status_code == 200:
  #       orderData['labels'].append(store.owner_name)
  #       orderData['datasets'][0]['data'].append(response2.json()['list']['meta']['totalCount'])
  #   except:
  #     continue
  
  # return json.dumps(orderData)

@app.route('/viewPricing.csv')
def view_pricing():
    return send_file('product_costs.csv')

def pricing_pool(product):
    try:
      with open('product_costs.csv', 'w') as f:
        if product.upc:
          print(product.name)
          writer = csv.writer(f)

          syncCentricKey = 'NGtjAvrxWZhD9DbcY5VJxPfTzvXiYqJEOEFfwiYUPuQleyeLycQrZWgSYt7b'

          url = "https://v3.synccentric.com/api/v3/products/search"

          headers = {}
          headers["Authorization"] = "Bearer " + syncCentricKey
          headers["Content-Type"] = "application/x-www-form-urlencoded"

          data = "identifier[]=" + product.upc + "&type=upc&locale=US"

          resp = requests.post(url, headers=headers, data=data)

          if resp.status_code == 200:
            buybox_price = float(resp.json()['data'][0]['attributes']['buybox_new_landed_price'])
            merchant_price = float(json.loads(resp.json()['data'][0]['attributes']['lowest_offer_listings'])[0]['Price']['LandedPrice']['Amount'])

            if buybox_price <= merchant_price:
              if buybox_price >= 0:
                print('Price Updated')
                product.supplier_price = buybox_price
                db.session.commit()
            else:
              if merchant_price > 0:
                print('Price Updated')
                product.supplier_price = merchant_price
                db.session.commit()
          else:
            print('Waiting 1 hr.')
    except:
      print('Error. Skipping')

@app.route('/getPricing')
def update_pricing(): 
    products = json.loads(WalmartProduct.as_dict())
    alreadyFound = []
    list = []

    syncCentricKey = 'NGtjAvrxWZhD9DbcY5VJxPfTzvXiYqJEOEFfwiYUPuQleyeLycQrZWgSYt7b'

    url = "https://v3.synccentric.com/api/v3/products"

    headers = {}
    headers["Authorization"] = "Bearer " + syncCentricKey
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    params = {
      'fields[]': ['lowest_new_price']
    }

    resp = requests.get(url, headers=headers, params=params)

    if resp.status_code == 200:
      i = 1
      total = resp.json()['meta']['last_page']

      while i <= total:
        next_url = "https://v3.synccentric.com/api/v3/products?page=" + str(i)

        syncCentricKey = 'NGtjAvrxWZhD9DbcY5VJxPfTzvXiYqJEOEFfwiYUPuQleyeLycQrZWgSYt7b'

        url = "https://v3.synccentric.com/api/v3/products"

        headers = {}
        headers["Authorization"] = "Bearer " + syncCentricKey
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        params = {
          'fields[]': ['lowest_new_price', 'asin']
        }

        resp = requests.get(url, headers=headers, params=params)

        if resp.status_code == 200:
          for product in resp.json()['data']:
            if float(product['attributes']['lowest_new_price']) > 0.0:
              # matchingProduct = WalmartProduct.query.filter_by(upc=product['attributes']['initial_identifier']).first()

              # if matchingProduct:
              #   matchingProduct.supplier_price = float(product['attributes']['lowest_new_price'])
              #   alreadyFound.append(matchingProduct)
              #   db.session.commit()
              # else:
              #   matchingProduct = WalmartProduct.query.filter(WalmartProduct.upc.contains(product['attributes']['asin'])).first()
              #   if matchingProduct:
              #     alreadyFound.append(matchingProduct)
              #     matchingProduct.supplier_price = float(product['attributes']['lowest_new_price'])

              print('Added Price Update to CSV')

              list.append([product['attributes']['initial_identifier'] + '-AE', float(product['attributes']['lowest_new_price']), 'USD'])
              list.append([product['attributes']['initial_identifier'] + '-OAG', float(product['attributes']['lowest_new_price']), 'USD'])
              list.append([product['attributes']['initial_identifier'] + '-AE', float(product['attributes']['lowest_new_price']), 'USD'])

        i = i + 1

        with open('product_costs.csv', 'w') as g:
          writer = csv.writer(g)
          writer.writerow(['SKU', 'COST', 'CURRENCY'])

          for item in list:
            writer.writerow(item)


    return 'Success'

@app.route('/getStoreStats')
def getStoreStats():

  id = request.args.get('id')

  storeStats=[]
  stores = Store.query.filter_by(id=id).all()

  for store in stores:
    try:
      url2 = "https://marketplace.walmartapis.com/v3/token"

      payload='grant_type=client_credentials'
      headers = {
        'WM_SVC.NAME': 'TEST',
        'WM_QOS.CORRELATION_ID': '1234567890',
        'Content-Type': 'application/x-www-form-urlencoded',
      }
      response = requests.request("POST", url2, headers=headers, auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret), data=payload)
      access_token = response.text.split('<accessToken>')[1].split('</accessToken>')[0]


      url3 = "https://marketplace.walmartapis.com/v3/insights/items/listingQuality/score?viewTrendingItems=true"
      headers3 = {
        'WM_SVC.NAME': 'TEST',
        'WM_SEC.ACCESS_TOKEN': access_token,
        'WM_QOS.CORRELATION_ID': '1234567890',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
      response2 = requests.request("GET", url3, headers=headers3, auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret))

      if response2.status_code == 200:
        data = {
          'name': store.owner_name,
          'overall_score': (response2.json()['payload']['score']['offerScore'] + response2.json()['payload']['score']['ratingReviewScore'] + response2.json()['payload']['score']['contentScore'])/3,
          'review_score': response2.json()['payload']['score']['ratingReviewScore'],
          'listing_quality': response2.json()['payload']['score']['contentScore'],
          'pricing_quality': response2.json()['payload']['score']['offerScore'],
        }
        storeStats.append(data)
    except:
      continue

  return json.dumps(storeStats)

@app.route('/newListing')
def upload_listing_individual():
  sku = request.args.get('sku')
  options = webdriver.ChromeOptions()
  options.headless = True
  options.add_argument('--disable-gpu')
  options.add_argument('--no-sandbox')

  stores = Store.query.all() 

  print('Adding to OAGenius')

  for store in stores: 
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)

    driver.get("https://sage.oagenius.com/login")


    time.sleep(3)

    email = driver.find_element_by_xpath("//input[@type='email']")
    email.send_keys(store.oa_username)

    password = driver.find_element_by_xpath("//input[@type='password']")
    password.send_keys(store.oa_password)

    driver.find_element_by_class_name('MuiButton-fullWidth').click()

    time.sleep(3)

    products = WalmartProduct.query.filter_by(sku=sku).first()

    for product in products:
      try:
        driver.get("https://sage.oagenius.com/app/products/create")
        
        time.sleep(3)

        walmart = driver.find_elements_by_xpath("//input[@type='text']")[0]

        if '/ip/' not in product.url:
          walmart.send_keys(product.url.replace('/ip', '/ip/'))
        else:
          walmart.send_keys(product.url)

        amazon = driver.find_elements_by_xpath("//input[@type='text']")[1]

        if '/dp/' not in product.supplier_url:
          amazon.send_keys(product.supplier_url.replace('/dp', '/dp/'))
        else:
          amazon.send_keys(product.supplier_url)

        time.sleep(2)

        item_data = driver.find_elements_by_class_name('MuiTypography-body2')

        for data in item_data:
          if 'Total cost' in data.text:
            totalCost = float(data.text.split(': $')[1])
            initialCost = math.ceil(totalCost*1.3)
            initialPrice = driver.find_elements_by_xpath("//input[@type='number']")
            initialPrice[0].clear()
            initialPrice[0].send_keys(str(initialCost))
            break
              
        sku = driver.find_element_by_xpath("//input[@name='sku']")
        sku.clear()

        if product.upc:
          sku.send_keys(product.upc)
        else:
          sku.send_keys(product.sku)

        button = driver.find_element_by_class_name('MuiButton-containedSecondary')
        print(product.name + ' Added')
        button.click()

        time.sleep(2)
      except:
        continue

def upload_listing_bulk(sku):
  options = webdriver.ChromeOptions()
  options.headless = True
  options.add_argument('--disable-gpu')
  options.add_argument('--no-sandbox')

  stores = Store.query.all() 

  print('Adding to OAGenius')

  for store in stores: 
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)

    driver.get("https://sage.oagenius.com/login")

    email = driver.find_element_by_xpath("//input[@type='email']")
    email.send_keys(store.oa_username)

    password = driver.find_element_by_xpath("//input[@type='password']")
    password.send_keys(store.oa_password)

    driver.find_element_by_class_name('MuiButton-fullWidth').click()

    time.sleep(3)

    products = WalmartProduct.query.filter_by(sku=sku).first()

    for product in products:
      try:
        driver.get("https://sage.oagenius.com/app/products/create")
        
        time.sleep(3)

        walmart = driver.find_elements_by_xpath("//input[@type='text']")[0]

        if '/ip/' not in product.url:
          walmart.send_keys(product.url.replace('/ip', '/ip/'))
        else:
          walmart.send_keys(product.url)

        amazon = driver.find_elements_by_xpath("//input[@type='text']")[1]

        if '/dp/' not in product.supplier_url:
          amazon.send_keys(product.supplier_url.replace('/dp', '/dp/'))
        else:
          amazon.send_keys(product.supplier_url)

        time.sleep(2)

        item_data = driver.find_elements_by_class_name('MuiTypography-body2')

        for data in item_data:
          if 'Total cost' in data.text:
            totalCost = float(data.text.split(': $')[1])
            initialCost = math.ceil(totalCost*1.3)
            initialPrice = driver.find_elements_by_xpath("//input[@type='number']")
            initialPrice[0].clear()
            initialPrice[0].send_keys(str(initialCost))
            break
              
        sku = driver.find_element_by_xpath("//input[@name='sku']")
        sku.clear()

        if product.upc:
          sku.send_keys(product.upc)
        else:
          sku.send_keys(product.sku)

        button = driver.find_element_by_class_name('MuiButton-containedSecondary')
        print(product.name + ' Added')
        button.click()

        time.sleep(2)
      except:
        continue

@app.route('/updateCSV')
def update_csv():

  id = request.args.get('id')

  store = Store.query.filter_by(id=id).first()

  with open('csv_data_' + str(id) + '.zip', 'wb') as f:
    url2 = "https://marketplace.walmartapis.com/v3/token"

    payload='grant_type=client_credentials'
    headers = {
      'WM_SVC.NAME': 'TEST',
      'WM_QOS.CORRELATION_ID': '1234567890',
      'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.request("POST", url2, headers=headers,  auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret), data=payload)
    access_token = response.text.split('<accessToken>')[1].split('</accessToken>')[0]

    url3 = "https://marketplace.walmartapis.com/v3/getReport?type=itemPerformance"

    headers3 = {
        'WM_SVC.NAME': 'TEST',
        'WM_SEC.ACCESS_TOKEN': access_token,
        'WM_QOS.CORRELATION_ID': '1234567890',
    }

    with requests.request("GET", url3, stream = True, headers=headers3, auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret)) as response:
        f.write(response.content)

  return 'Updated'

@app.route('/getCSV')
def get_csv():

  id = request.args.get('id')

  store = Store.query.filter_by(id=id).first()

  items = []

  currentStore = {
    'name': store.owner_name,
    'products': [],
    'total_gross': 0,
    'total_items': 0,
  }

  try:
    zf = zipfile.ZipFile('csv_data_' + str(id) + '.zip') 
    df = pd.read_csv(zf.open(zf.namelist()[0]))

    with zipfile.ZipFile('csv_data_' + str(id) + '.zip') as zf:
      with zf.open(zf.namelist()[0], 'r') as infile:
          reader = csv.reader(TextIOWrapper(infile, 'utf-8'))
          for index, row in enumerate(reader):
            if index != 0:
              if str(row[5]).lower() in str(currentStore['products']).lower():
                for product in currentStore['products']:
                  if product['Category'] == row[5]:
                    product['GMV-Commission'] = float(product['GMV-Commission']) + float(row[10])
                    product['Total Units Sold'] = int(product['Total Units Sold']) + int(row[12])
                    currentStore['total_gross'] = currentStore['total_gross'] + float(product['GMV-Commission'])
                    currentStore['total_items'] = currentStore['total_items'] + float(product['Total Units Sold'])
              else:
                data = {
                  # 'Product Name': row[0],
                  # 'Item ID': row[1],
                  # 'SKU ID': row[2], 
                  # 'Super Department': row[3], 
                  # 'Department': row[4], 
                  'Category': row[5], 
                  # 'Sub Category': row[6], 
                  # 'Brand': row[7], 
                  # 'GMV': row[8], 
                  # 'Commission': row[9], 
                  'GMV-Commission': row[10], 
                  # 'AUR': row[11], 
                  'Total Units Sold': row[12], 
                  # 'Cancelled Units': row[13], 
                  # 'Cancelled Sales': row[14], 
                  # 'Item Conversion Rate': row[15], 
                  # 'Base Item Id': row[16], 
                  # 'Total Product Visits': row[17], 
                  # 'GMV Comp %': row[18], 
                  # 'Authorized Orders': row[19], 
                  # 'Authorized Units': row[20], 
                  # 'Authorized Sales': row[21], 
                  # 'Total LY GMV': row[22]
                }

                if float(data['Total Units Sold']) >= 0.01:
                  currentStore['products'].append(data)
                  currentStore['total_gross'] = currentStore['total_gross'] + float(data['GMV-Commission'])
                  currentStore['total_items'] = currentStore['total_items'] + float(data['Total Units Sold'])

    items.append(currentStore)
  except:
    requests.request("GET", 'http://ecommerce-aio.herokuapp.com/updateCSV?id=' + id)
    print('Done')


  return json.dumps(items)

@app.route('/getTracking', methods=['POST', 'GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def get_tracking():

  if(request.method=='POST'):
    selected_order = Order.query.filter_by(id=request.json['id']).first()
    store = Store.query.filter_by(id = selected_order.store_id).first()
    oagenius_tracking = 'https://fthoqqsb4k.execute-api.us-east-1.amazonaws.com/prod/get-trackingnr'
    oa_headers = {
      'x-api-key': 'LmsSuZnvcq6JTpZYeN2wn1vClpnWSlajaxnRt5jU',
      'Content-Type': 'application/json',
    }
    
    oa_body = {
      'city': selected_order.raw_json['shippingInfo']['postalAddress']['city'],
      'state': selected_order.raw_json['shippingInfo']['postalAddress']['state'],       
      'from': selected_order.raw_json['shippingInfo']['estimatedShipDate'],
      'to': selected_order.raw_json['shippingInfo']['estimatedShipDate'] + 432000000,
      'checkOnWalmart': True,
    }

    oa_response = requests.request("POST", oagenius_tracking, headers=oa_headers, data=json.dumps(oa_body))

    if 'trackingNr' in oa_response.json().keys():
      print('Tracking Created')
      tracking_number = oa_response.json()['trackingNr']
      if len(tracking_number) == 12:
        shipping_carrier = 'FedEx'
      elif len(tracking_number) >=  20 and len(tracking_number) <=  22:
        shipping_carrier = 'USPS'
      elif len(tracking_number) == 18:
        shipping_carrier = 'UPS'
        # pdb.set_trace()
      else:
        print('No Match')

      print('Assigned by ' + shipping_carrier)
      print('New Tracking Number Created: ' + tracking_number)
    elif 'error' in oa_response.json().keys():
      # pdb.set_trace()
      new_oa_body = {
      'state': selected_order.raw_json['shippingInfo']['postalAddress']['city']['shippingInfo']['postalAddress']['state'],       
      'from': selected_order.raw_json['shippingInfo']['postalAddress']['city']['shippingInfo']['estimatedShipDate'],
      'to': selected_order.raw_json['shippingInfo']['postalAddress']['city']['shippingInfo']['estimatedShipDate'] + 432000000,
      'checkOnWalmart': True,
      }
      oa_response = requests.request("POST", oagenius_tracking, headers=oa_headers, data=json.dumps(new_oa_body))
      if oa_response.json()['trackingNr']:
        tracking_number = oa_response.json()['trackingNr']
        if len(tracking_number) == 12:
          shipping_carrier = 'FedEx'
        elif len(tracking_number) >=  20 and len(tracking_number) <=  22:
          shipping_carrier = 'USPS'
        elif len(tracking_number) == 18:
          shipping_carrier = 'UPS'
    else:
      print('Cannot Replace Tracking Number')
      return 'Error generating Shipping Number'


    for order_line in selected_order.raw_json['orderLines']['orderLine']:
      for status in order_line['orderLineStatuses']['orderLineStatus']:
        status['status'] = 'Shipped'
        status['trackingInfo'] = {
          'shipDateTime': selected_order.raw_json['shippingInfo']['estimatedShipDate'],
          'carrierName': {
            'carrier': shipping_carrier,
          },
          'methodCode': 'Standard',
          'trackingNumber': tracking_number,
        }

    url2 = "https://marketplace.walmartapis.com/v3/token"

    payload='grant_type=client_credentials'
    headers = {
      'WM_SVC.NAME': 'TEST',
      'WM_QOS.CORRELATION_ID': '1234567890',
      'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.request("POST", url2, headers=headers, auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret), data=payload)
    access_token = response.text.split('<accessToken>')[1].split('</accessToken>')[0]


    headers3 = {
      'WM_SVC.NAME': 'TEST',
      'WM_SEC.ACCESS_TOKEN': access_token,
      'WM_QOS.CORRELATION_ID': '1234567890',
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    }

    orderShipment = {
      'orderShipment': {
        'orderLines': selected_order.raw_json['orderLines']
      }
    }

    print('Sending to Walmart')

    url3 = "https://marketplace.walmartapis.com/v3/orders/" + selected_order.raw_json['purchaseOrderId'] + "/shipping"
    
    response2 = requests.request("POST", url3, auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret), headers=headers3, json=orderShipment)

    if response2.status_code == 200:
      selected_order.tracking = {
        'carrier': shipping_carrier,
        'number': tracking_number
      }
      selected_order.status = 'Shipped'
      db.session.commit()

    print('Order has Shipped with ' + shipping_carrier + ' - ' + tracking_number)

    return oa_response.json()
  else:
    return 'Nice Json'



  pdb.set_trace()

  selected_order = request.json()
  
@app.route('/markOrdered', methods=['POST', 'GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def mark_ordered():
  if(request.method=='POST'):
    selectedOrder = Order.query.filter_by(id=request.json['order']['id']).first()
    cost = request.json['actualCost']
    profit = request.json['profit']
    purchaseOrder = request.json['purchaseOrder']
    selectedOrder.profit = profit
    selectedOrder.supplier_order_id = purchaseOrder
    selectedOrder.status = 'Ordered'
    db.session.commit()

    # CHARGE STRIPE ACCOUNT

    return 'Successfully Updated'
  else:
    return '{}'

@app.route('/shipping')
def check_shipping():

  options = webdriver.ChromeOptions()
  options.headless = True
  options.add_argument('--disable-gpu')
  options.add_argument('--no-sandbox')

  orders = Order.query.all()
  
  driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
  driver.get("https://www.amazon.com/gp/your-account/order-details?ie=UTF8&orderID=")
  driver.find_element_by_id('ap_email').send_keys('amazon@mana.management')
  driver.find_element_by_id('continue').click()
  driver.find_element_by_id('ap_password').send_keys('Noni808!')
  driver.find_element_by_id('signInSubmit').click()
  time.sleep(1)


  for order in orders:
    if order.supplier_order_id:
      driver.get("https://www.amazon.com/gp/your-account/order-details?ie=UTF8&orderID=" + order.supplier_order_id)
      try:
        driver.find_element_by_class_name('track-package-button').click()
        
        time.sleep(2)
        
        containers = driver.find_elements_by_class_name('cardContainer')

        for container in containers:
          if 'id' in container.text.lower():
            time.sleep(1)

            shipping_carrier_divs = container.text.split('\n')
            for div in shipping_carrier_divs:
              if 'shipped with' in div.lower():
                shipping_carrier = div.split('Shipped with')[1].strip()
                print(shipping_carrier)

            for div in shipping_carrier_divs:
              if 'id:' in div.lower():
                tracking_number = div.split(':')[1].strip()
                print(tracking_number + ': ' + order.status)

            if order.status != 'Shipped':
              id = order.raw_json['purchaseOrderId']

              url2 = "https://marketplace.walmartapis.com/v3/token"

              payload='grant_type=client_credentials'
              headers = {
                'Authorization': 'Basic NWI4Yjk5MmEtODY3OS00NWI3LTg1ZTUtZmNmMjk4ZmZkMTEwOkFPVXFXUWxUWmhxQVh5UU9TSUxlaGI1UGd5b1hfUlVVaWNpS3l6ampwM3dKcWt4b1FUaURhYU5TUThQMDd5WUFURFVCclhTcnYtdElGZG91SS1lRkh3',
                'WM_SVC.NAME': 'TEST',
                'WM_QOS.CORRELATION_ID': '1234567890',
                'Content-Type': 'application/x-www-form-urlencoded',
              }

              response = requests.request("POST", url2, headers=headers, data=payload)
              access_token = response.text.split('<accessToken>')[1].split('</accessToken>')[0]

              print('Access: ' + access_token)

              url3 = "https://marketplace.walmartapis.com/v3/orders/" + id + "/shipping"

              selected_order = order.raw_json


              if 'TBA' in tracking_number:
                print('Found Amazon Shipping ID')
                # driver.get('https://tracking.oagenius.com/app/account/tracking')
                # driver.find_elements_by_class_name('MuiOutlinedInput-input')[0].send_keys('braydonwhitmarsh@me.com')
                # driver.find_elements_by_class_name('MuiOutlinedInput-input')[1].send_keys('Noni808!')
                # driver.find_element_by_class_name('MuiButton-sizeLarge').click()
                # driver.find_elements_by_class_name('MuiInputBase-input')[0].send_keys


                oagenius_tracking = 'https://fthoqqsb4k.execute-api.us-east-1.amazonaws.com/prod/get-trackingnr'
                oa_headers = {
                  'x-api-key': 'LmsSuZnvcq6JTpZYeN2wn1vClpnWSlajaxnRt5jU',
                  'Content-Type': 'application/json',
                }
                
                oa_body = {
                  'city': selected_order['shippingInfo']['postalAddress']['city'],
                  'state': selected_order['shippingInfo']['postalAddress']['state'],       
                  'from': selected_order['shippingInfo']['estimatedShipDate'],
                  'to': selected_order['shippingInfo']['estimatedShipDate'] + 432000000,
                  'checkOnWalmart': True,
                }

                oa_response = requests.request("POST", oagenius_tracking, headers=oa_headers, data=json.dumps(oa_body))


                print(oa_response.json())

                if 'trackingNr' in oa_response.json().keys():
                  print('Tracking Created')
                  tracking_number = oa_response.json()['trackingNr']
                  if len(tracking_number) == 12:
                    shipping_carrier = 'FedEx'
                  elif len(tracking_number) >=  20 and len(tracking_number) <=  22:
                    shipping_carrier = 'USPS'
                  elif len(tracking_number) == 18:
                    shipping_carrier = 'UPS'
                    # pdb.set_trace()
                  else:
                    print('No Match')

                  print('Assigned by ' + shipping_carrier)
                  print('New Tracking Number Created: ' + tracking_number)
                elif 'error' in oa_response.json().keys():
                  # pdb.set_trace()
                  new_oa_body = {
                  'state': selected_order['shippingInfo']['postalAddress']['state'],       
                  'from': selected_order['shippingInfo']['estimatedShipDate'],
                  'to': selected_order['shippingInfo']['estimatedShipDate'] + 432000000,
                  'checkOnWalmart': True,
                  }
                  oa_response = requests.request("POST", oagenius_tracking, headers=oa_headers, data=json.dumps(new_oa_body))
                  if oa_response.json()['trackingNr']:
                    tracking_number = oa_response.json()['trackingNr']
                    if len(tracking_number) == 12:
                      shipping_carrier = 'FedEx'
                    elif len(tracking_number) >=  20 and len(tracking_number) <=  22:
                      shipping_carrier = 'USPS'
                    elif len(tracking_number) == 18:
                      shipping_carrier = 'UPS'
                else:
                  print('Cannot Replace Tracking Number')
                  # pdb.set_trace()


                for order_line in selected_order['orderLines']['orderLine']:
                  for status in order_line['orderLineStatuses']['orderLineStatus']:
                    status['status'] = 'Shipped'
                    status['trackingInfo'] = {
                      'shipDateTime': selected_order['shippingInfo']['estimatedShipDate'],
                      'carrierName': {
                        'carrier': shipping_carrier,
                      },
                      'methodCode': 'Standard',
                      'trackingNumber': tracking_number,
                    }

                print('Created Updated Shipping JSON')
              else:
                for order_line in selected_order['orderLines']['orderLine']:
                  for status in order_line['orderLineStatuses']['orderLineStatus']:
                    status['status'] = 'Shipped'
                    status['trackingInfo'] = {
                      'shipDateTime': selected_order['shippingInfo']['estimatedShipDate'],
                      'carrierName': {
                        'carrier': shipping_carrier,
                      },
                      'methodCode': 'Standard',
                      'trackingNumber': tracking_number,
                    }
              
              headers3 = {
                'Authorization': 'Basic NWI4Yjk5MmEtODY3OS00NWI3LTg1ZTUtZmNmMjk4ZmZkMTEwOkFPVXFXUWxUWmhxQVh5UU9TSUxlaGI1UGd5b1hfUlVVaWNpS3l6ampwM3dKcWt4b1FUaURhYU5TUThQMDd5WUFURFVCclhTcnYtdElGZG91SS1lRkh3',
                'WM_SVC.NAME': 'TEST',
                'WM_SEC.ACCESS_TOKEN': access_token,
                'WM_QOS.CORRELATION_ID': '1234567890',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
              }

              orderShipment = {
                'orderShipment': {
                  'orderLines': selected_order['orderLines']
                }
              }

              print('Sending to Walmart')
              
              response2 = requests.request("POST", url3, headers=headers3, json=orderShipment)

              if response2.status_code == 200:
                order.tracking = {
                  'carrier': shipping_carrier,
                  'number': tracking_number
                }
                order.status = 'Shipped'
                db.session.commit()
              print('Order has Shipped with ' + shipping_carrier + ' - ' + tracking_number)


        
        
        if round(time.time()*1000) > order.raw_json['shippingInfo']['estimatedShipDate'] and order.status != 'Shipped':
            print('Working On Creating New Number')
            selected_order = order.raw_json

            oagenius_tracking = 'https://fthoqqsb4k.execute-api.us-east-1.amazonaws.com/prod/get-trackingnr'
                
            oa_headers = {
              'x-api-key': 'LmsSuZnvcq6JTpZYeN2wn1vClpnWSlajaxnRt5jU',
              'Content-Type': 'application/json',
            }


            
            oa_body = {
              'city': selected_order['shippingInfo']['postalAddress']['city'],
              'state': selected_order['shippingInfo']['postalAddress']['state'],       
              'from': selected_order['shippingInfo']['estimatedShipDate'],
              'to': selected_order['shippingInfo']['estimatedShipDate'] + 432000000,
              'checkOnWalmart': True,
            }

            oa_response = requests.request("POST", oagenius_tracking, headers=oa_headers, data=json.dumps(oa_body))


            print(oa_response.json())

            if 'trackingNr' in oa_response.json().keys():
              print('Tracking Created')
              tracking_number = oa_response.json()['trackingNr']
              if len(tracking_number) == 12:
                shipping_carrier = 'FedEx'
              elif len(tracking_number) >=  20 and len(tracking_number) <=  22:
                shipping_carrier = 'USPS'
              elif len(tracking_number) == 18:
                shipping_carrier = 'UPS'
                # pdb.set_trace()
              else:
                print('No Match')

              print('Assigned by ' + shipping_carrier)
              print('New Tracking Number Created: ' + tracking_number)
            elif 'error' in oa_response.json().keys():
              # pdb.set_trace()
              new_oa_body = {
              'state': selected_order['shippingInfo']['postalAddress']['state'],       
              'from': selected_order['shippingInfo']['estimatedShipDate'],
              'to': selected_order['shippingInfo']['estimatedShipDate'] + 432000000,
              'checkOnWalmart': True,
              }
              oa_response = requests.request("POST", oagenius_tracking, headers=oa_headers, data=json.dumps(new_oa_body))
              if oa_response.json()['trackingNr']:
                tracking_number = oa_response.json()['trackingNr']
                if len(tracking_number) == 12:
                  shipping_carrier = 'FedEx'
                elif len(tracking_number) >=  20 and len(tracking_number) <=  22:
                  shipping_carrier = 'USPS'
                elif len(tracking_number) == 18:
                  shipping_carrier = 'UPS'
            else:
              print('Cannot Replace Tracking Number')
              # pdb.set_trace()


            for order_line in selected_order['orderLines']['orderLine']:
              for status in order_line['orderLineStatuses']['orderLineStatus']:
                status['status'] = 'Shipped'
                status['trackingInfo'] = {
                  'shipDateTime': selected_order['shippingInfo']['estimatedShipDate'],
                  'carrierName': {
                    'carrier': shipping_carrier,
                  },
                  'methodCode': 'Standard',
                  'trackingNumber': tracking_number,
                }


            print('Created Updated Shipping JSON')

            url2 = "https://marketplace.walmartapis.com/v3/token"

            payload='grant_type=client_credentials'
            headers = {
              'Authorization': 'Basic NWI4Yjk5MmEtODY3OS00NWI3LTg1ZTUtZmNmMjk4ZmZkMTEwOkFPVXFXUWxUWmhxQVh5UU9TSUxlaGI1UGd5b1hfUlVVaWNpS3l6ampwM3dKcWt4b1FUaURhYU5TUThQMDd5WUFURFVCclhTcnYtdElGZG91SS1lRkh3',
              'WM_SVC.NAME': 'TEST',
              'WM_QOS.CORRELATION_ID': '1234567890',
              'Content-Type': 'application/x-www-form-urlencoded',
            }

            response = requests.request("POST", url2, headers=headers, data=payload)
            access_token = response.text.split('<accessToken>')[1].split('</accessToken>')[0]

            print('Access: ' + access_token)


            headers3 = {
                'Authorization': 'Basic NWI4Yjk5MmEtODY3OS00NWI3LTg1ZTUtZmNmMjk4ZmZkMTEwOkFPVXFXUWxUWmhxQVh5UU9TSUxlaGI1UGd5b1hfUlVVaWNpS3l6ampwM3dKcWt4b1FUaURhYU5TUThQMDd5WUFURFVCclhTcnYtdElGZG91SS1lRkh3',
                'WM_SVC.NAME': 'TEST',
                'WM_SEC.ACCESS_TOKEN': access_token,
                'WM_QOS.CORRELATION_ID': '1234567890',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
              }

            orderShipment = {
              'orderShipment': {
                'orderLines': selected_order['orderLines']
              }
            }

            print('Marking Late Shipment Shipped on Walmart')

            url3 = "https://marketplace.walmartapis.com/v3/orders/" + order.id + "/shipping"
            
            response2 = requests.request("POST", url3, headers=headers3, json=orderShipment)

            if response2.status_code == 200:
              order.tracking = {
                'carrier': shipping_carrier,
                'number': tracking_number
              }
              order.status = 'Shipped'
              db.session.commit()

            print('Order has Shipped with ' + shipping_carrier + ' - ' + tracking_number)

      except:
        print('Skipped this Item')
        continue
    driver.quit()

  return 'Complete'

@app.route('/removeDuplicates')
def removeDuplicates():
  products = WalmartProduct.query.all()
  upc_list = []
  sku_list = []

  for product in products:
    if product.upc and product.sku:
      if product.upc in upc_list or product.sku in sku_list:
        print('Already Exists: UPC and SKU')
        db.session.delete(product)
      else:
        upc_list.append(product.upc)
        sku_list.append(product.sku)
        print('Does Not Exist: Adding UPC and SKU')
    elif product.upc:
      if product.upc in upc_list:
        print('Already Exists: UPC')
        db.session.delete(product)
      else:

        print('Searching for SKU')

        params = {
          'api_key': '5D26EEE7EA9646A39468E0CF477A8C3B',
          'type': 'product',
          'gtin': product.upc
        }

        api_result = requests.get('https://api.bluecartapi.com/request', params)

        if 'product' in api_result.json() and api_result.json()['product']['item_id']:
          print('SKU Found')

          upc_list.append(product.upc)
          sku_list.append(api_result.json()['product']['item_id'])
          product.sku = api_result.json()['product']['item_id']
        else:
          upc_list.append(product.upc)

    elif product.sku:
      if product.sku in sku_list:
        print('Already Exists: SKU')
        db.session.delete(product)
      else:
        params = {
          'api_key': '5D26EEE7EA9646A39468E0CF477A8C3B',
          'type': 'product',
          'sku': product.sku
        }

        api_result = requests.get('https://api.bluecartapi.com/request', params)

        if 'product' in api_result.json() and api_result.json()['product']['upc']:
          upc_list.append(api_result.json()['product']['upc'])
          sku_list.append(product.sku)
          product.upc = api_result.json()['product']['upc']
        else:
          sku_list.append(product.sku)
    else:
      print('No Data')
      db.session.delete(product)

  db.session.commit()

  return 'Completed'

@app.route('/searchASIN')
def asinSearch():
  asin = request.args.get('ASIN')

  syncCentricKey = 'NGtjAvrxWZhD9DbcY5VJxPfTzvXiYqJEOEFfwiYUPuQleyeLycQrZWgSYt7b'

  url = "https://v3.synccentric.com/api/v3/products/search"

  headers = {}
  headers["Authorization"] = "Bearer " + syncCentricKey
  headers["Content-Type"] = "application/x-www-form-urlencoded"

  data = "identifier[]=" + asin + "&type=asin&locale=US"

  resp = requests.post(url, headers=headers, data=data)

  # pdb.set_trace()

  upc = resp.json()['data'][0]['attributes']['upc']

  url2 = "https://marketplace.walmartapis.com/v3/token"

  payload='grant_type=client_credentials'
  headers = {
  'Authorization': 'Basic MWUxODc1YTMtNjkzYS00MDI4LTliOWUtMmVkZDBjY2I0ODg0OlcxNmd4dFUzdGxMNEFET0FvOVY0NkxQTERfS3RYVjY2dkQwXzZCdndMeUMyTURkWEgybVVReGtkb0hSOHZzWFFWOHVSVGZneUVlVW9XYkJKMWtRZDJn',
  'WM_SVC.NAME': 'TEST',
  'WM_QOS.CORRELATION_ID': '1234567890',
  'Content-Type': 'application/x-www-form-urlencoded',
  }

  response = requests.request("POST", url2, headers=headers, data=payload)
  access_token = response.text.split('<accessToken>')[1].split('</accessToken>')[0]

  print('Access: ' + access_token)

  headers3 = {
    'Authorization': 'Basic MWUxODc1YTMtNjkzYS00MDI4LTliOWUtMmVkZDBjY2I0ODg0OlcxNmd4dFUzdGxMNEFET0FvOVY0NkxQTERfS3RYVjY2dkQwXzZCdndMeUMyTURkWEgybVVReGtkb0hSOHZzWFFWOHVSVGZneUVlVW9XYkJKMWtRZDJn',
    'WM_SVC.NAME': 'TEST',
    'WM_SEC.ACCESS_TOKEN': access_token,
    'WM_QOS.CORRELATION_ID': '1234567890',
    'Accept': 'application/json',
  }  

  if upc:
   response2 = requests.request("GET", 'https://marketplace.walmartapis.com/v3/items/walmart/search?upc=' + resp.json()['data'][0]['attributes']['upc'], headers=headers3)
  else:
    return {
      'status': 'Error'
    }

  if 'items' in response2.text:
    if resp.json()['data'][0]['attributes']['sales_rank'] <= 500:
      if WalmartProduct.query.filter_by(upc=upc).first():
        return {
          'walmart': 'https://www.walmart.com/ip/' + response2.json()['items'][0]['itemId'],
          'sku': response2.json()['items'][0]['itemId'],
          'initial_price': float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.35,
          'handling': 3,
          'buybox': resp.json()['data'][0]['attributes']['buybox_new_listing_price'],
          'selling_fee': float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.35*.15,
          'cost': float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.09,
          'profit':  ((float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.35)*.85) - (float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.09),
          'margin': 100*((((float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.35)*.85) - (float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.09))/float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.09),
          'walmart_image': response2.json()['items'][0]['images'][0]['url'],
          'amz_image': resp.json()['data'][0]['attributes']['medium_image'],
          'status': 'profitable'
        }
      else:
      
        new_product = WalmartProduct(resp.json()['data'][0]['attributes']['title'], 'https://www.walmart.com/ip/' + response2.json()['items'][0]['itemId'], response2.json()['items'][0]['itemId'], resp.json()['data'][0]['attributes']['buybox_new_listing_price'], 'https://www.amazon.com/dp/' + asin)
        new_product.thumbnail = response2.json()['items'][0]['images'][0]['url']
        new_product.thumbnail2 = resp.json()['data'][0]['attributes']['medium_image']
        new_product.upc = upc
        db.session.add(new_product)
        db.session.commit()


        return {
          'walmart': 'https://www.walmart.com/ip/' + response2.json()['items'][0]['itemId'],
          'sku': response2.json()['items'][0]['itemId'],
          'initial_price': float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.35,
          'handling': 3,
          'buybox': resp.json()['data'][0]['attributes']['buybox_new_listing_price'],
          'selling_fee': float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.35*.15,
          'cost': float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.09,
          'profit':  ((float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.35)*.85) - (float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.09),
          'margin': ((((float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.35)*.85) - (float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.09))/float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.09),
          'walmart_image': response2.json()['items'][0]['images'][0]['url'],
          'amz_image': resp.json()['data'][0]['attributes']['medium_image'],
          'status': 'profitable'
        }

    else:
      print('Amazon: ' + str(float(resp.json()['data'][0]['attributes']['buybox_new_listing_price'])*1.10))
      print('Walmart: ' + str(.85 * float(response2.json()['items'][0]['price']['amount'])))
  
  return {
    'status': 'Error'
  }

@app.route('/update')
def update():
    return check_orders()

@app.route('/allStores')
def all_stores():
  stores = Store.query.all()

  storeList = {}

  for store in stores:
    storeList[store.id] = store.owner_name

  return json.dumps(storeList)

@app.route('/past_due')
def past_due():

  storeId = request.args.get('id')
  
  orders = []

  stores = Store.query.all()

  for store in stores:
    try:

      url2 = "https://marketplace.walmartapis.com/v3/token"

      payload='grant_type=client_credentials'
      headers = {
        'WM_SVC.NAME': 'TEST',
        'WM_QOS.CORRELATION_ID': '1234567890',
        'Content-Type': 'application/x-www-form-urlencoded',
      }

      import time
      s=time.gmtime(((time.time()*1000)-864000000)/1000)
      old_date = time.strftime("%Y-%m-%d", s)
      old_time = time.strftime('%H:%M:%S', s)
      old_formatted_time = old_date + 'T' + old_time

      t=time.gmtime(time.time())
      new_date = time.strftime("%Y-%m-%d", t)
      current_time = time.strftime('%H:%M:%S', t)
      current_formatted_time = new_date + 'T' + current_time

      response = requests.request("POST", url2, headers=headers,  auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret), data=payload)
      access_token = response.text.split('<accessToken>')[1].split('</accessToken>')[0]

      url3 = "https://marketplace.walmartapis.com/v3/orders?status=Acknowledged&createdStartDate=" + old_formatted_time + '&createdEndDate=' + current_formatted_time

      payload3='grant_type=client_credentials'

      headers3 = {
          'WM_SVC.NAME': 'TEST',
          'WM_SEC.ACCESS_TOKEN': access_token,
          'WM_QOS.CORRELATION_ID': '1234567890',
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json',
      }

      response2 = requests.request("GET", url3,  auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret), headers=headers3, data=payload3)

      if response2.json() and response2.json()['list']:
            for order in response2.json()['list']['elements']['order']:

              if math.ceil(time.time()*1000) > order['shippingInfo']['estimatedShipDate']:
                  order_data = {
                    'name': order['shippingInfo']['postalAddress']['name'],
                    'purchaseOrderId': order['purchaseOrderId'],
                    'storeId': store.id
                  }
                  orders.append(order_data)

      while 'nextCursor' in response2.json()['list']['meta']:
        try:
          url4 = "https://marketplace.walmartapis.com/v3/orders" + response2.json()['list']['meta']['nextCursor']

          headers4 = {
              'WM_SVC.NAME': 'TEST',
              'WM_SEC.ACCESS_TOKEN': access_token,
              'WM_QOS.CORRELATION_ID': '1234567890',
              'Content-Type': 'application/json',
              'Accept': 'application/json',
          }

          response3 = requests.request("GET", url4,  auth=HTTPBasicAuth(store.walmart_key, store.walmart_secret), headers=headers4)

          if response3.json() and response3.json()['list']:
              for order in response3.json()['list']['elements']['order']:

                if math.ceil(time.time()*1000) > order['shippingInfo']['estimatedShipDate']:
                    order_data = {
                      'name': order['shippingInfo']['postalAddress']['name'],
                      'purchaseOrderId': order['purchaseOrderId'],
                      'storeId': store.id
                    }
                    orders.append(order_data)
              response2 = response3
        except:
          break
    except:
      continue
  return json.dumps(orders)

@app.route('/store_data')
def store_data():

  if request.args.get('id'):
    stores = Store.query.filter_by(id=request.args.get('id')).all()
  else:
    stores = Store.query.all()


  all_stores = []

  combined = {
    'name': 'Combined',
    'profit': 0,
    'revenue': 0,
    'spent': 0,
    'orders': 0,
    'roi': 0,
    'avg_profit': 0
  }


  for store in stores:
  
    orders = Order.query.filter_by(store_id=request.args.get('id')).all()

    pdb.set_trace

    i = 0

    data = {
      'name': store.owner_name,
      'profit': 0,
      'revenue': 0,
      'spent': 0,
      'orders': len(orders),
      'roi': 0,
      'avg_profit': 0,
      'most_recent': []
    }
    
    for order in orders:
      if order.profit and order.purchase_price and order.supplier_price:
        data['profit'] = float(data['profit']) + float(order.profit)
        data['revenue'] = float(data['revenue']) + float(order.purchase_price)
        data['spent'] = float(data['spent']) + float(order.supplier_price)
        combined['profit'] = float(combined['profit']) + float(order.profit)
        combined['revenue'] = float(combined['revenue']) + float(order.purchase_price)
        combined['spent'] = float(combined['spent']) + float(order.supplier_price)
        
        if i <= 5:
          order_data = {'name': order.raw_json['shippingInfo']['postalAddress']['name'], 'spent': order.supplier_price, 'sold': order.purchase_price, 'profit': order.profit}
          data['most_recent'].append(order_data)
          i = i+1

 
    if data['spent'] > 0:
      data['roi'] = data['profit']/data['spent']
      data['avg_profit'] = data['profit']/data['orders']

      all_stores.append(data)

      orders = Order.query.all()

      combined['roi'] = combined['profit']/combined['spent']
      combined['orders'] = len(orders)
      combined['avg_profit'] = combined['profit']/combined['orders']

      all_stores.append(combined)

  return json.dumps(all_stores)

@app.route('/cancel')
def cancel():
  if request.args.get('storeId'):
    store_id = request.args.get('storeId')
    store = Store.query.filter_by(id=store_id).first()
    id = request.args.get('id')
    url2 = "https://marketplace.walmartapis.com/v3/token"

    payload='grant_type=client_credentials'
    headers = {
      'Authorization': store.walmart_key,
      'WM_SVC.NAME': 'TEST',
      'WM_QOS.CORRELATION_ID': '1234567890',
      'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.request("POST", url2, headers=headers, data=payload)
    access_token = response.text.split('<accessToken>')[1].split('</accessToken>')[0]

    print('Access: ' + access_token)

    url3 = "https://marketplace.walmartapis.com/v3/orders/" + id + "/cancel"

    current_order = Order.query.filter_by(id=id).first()

    selected_order = current_order.raw_json

    for order_line in selected_order['orderLines']['orderLine']:
      for status in order_line['orderLineStatuses']['orderLineStatus']:
        status['status'] = 'Cancelled'
        status['cancellationReason'] = "SELLER_CANCEL_OUT_OF_STOCK"

    order = {
      'orderCancellation': {
        'orderLines': selected_order['orderLines']
      }
    }

    headers3 = {
      'Authorization': store.walmart_key,
      'WM_SVC.NAME': 'TEST',
      'WM_SEC.ACCESS_TOKEN': access_token,
      'WM_QOS.CORRELATION_ID': '1234567890',
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    }

    response2 = requests.request("POST", url3, headers=headers3, json=order)

    if response2.status_code == 200:
      current_order.status = 'Cancelled'
      db.session.commit()

    return 'Completed'
  else:
    id = request.args.get('id')
    url2 = "https://marketplace.walmartapis.com/v3/token"

    payload='grant_type=client_credentials'
    headers = {
      'Authorization': 'Basic NWI4Yjk5MmEtODY3OS00NWI3LTg1ZTUtZmNmMjk4ZmZkMTEwOkFPVXFXUWxUWmhxQVh5UU9TSUxlaGI1UGd5b1hfUlVVaWNpS3l6ampwM3dKcWt4b1FUaURhYU5TUThQMDd5WUFURFVCclhTcnYtdElGZG91SS1lRkh3',
      'WM_SVC.NAME': 'TEST',
      'WM_QOS.CORRELATION_ID': '1234567890',
      'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.request("POST", url2, headers=headers, data=payload)
    access_token = response.text.split('<accessToken>')[1].split('</accessToken>')[0]

    print('Access: ' + access_token)

    url3 = "https://marketplace.walmartapis.com/v3/orders/" + id + "/cancel"

    current_order = Order.query.filter_by(id=id).first()

    selected_order = current_order.raw_json

    for order_line in selected_order['orderLines']['orderLine']:
      for status in order_line['orderLineStatuses']['orderLineStatus']:
        status['status'] = 'Cancelled'
        status['cancellationReason'] = "SELLER_CANCEL_OUT_OF_STOCK"

    order = {
      'orderCancellation': {
        'orderLines': selected_order['orderLines']
      }
    }

    headers3 = {
      'Authorization': 'Basic NWI4Yjk5MmEtODY3OS00NWI3LTg1ZTUtZmNmMjk4ZmZkMTEwOkFPVXFXUWxUWmhxQVh5UU9TSUxlaGI1UGd5b1hfUlVVaWNpS3l6ampwM3dKcWt4b1FUaURhYU5TUThQMDd5WUFURFVCclhTcnYtdElGZG91SS1lRkh3',
      'WM_SVC.NAME': 'TEST',
      'WM_SEC.ACCESS_TOKEN': access_token,
      'WM_QOS.CORRELATION_ID': '1234567890',
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    }

    response2 = requests.request("POST", url3, headers=headers3, json=order)

    if response2.status_code == 200:
      current_order.status = 'Cancelled'
      db.session.commit()

    return 'Completed'

@app.route('/remove_product')
def remove():
  id = request.args.get('id')

  found_products = WalmartProduct.query.filter_by(sku=id).all()

  stores = Store.query.all()

  for store in stores:
    if len(found_products) >= 1:
      for product in found_products:
        product.removed = True
        db.session.commit()

        try:
          url2 = "https://marketplace.walmartapis.com/v3/token"

          payload='grant_type=client_credentials'
          headers = {
              'Authorization': store.walmart_key,
              'WM_SVC.NAME': 'TEST',
              'WM_QOS.CORRELATION_ID': '1234567890',
              'Content-Type': 'application/x-www-form-urlencoded',
          }

          response = requests.request("POST", url2, headers=headers, data=payload)
          access_token = response.text.split('<accessToken>')[1].split('</accessToken>')[0]

          print('Access: ' + access_token)

          if product.sku:
            url3 = "https://marketplace.walmartapis.com/v3/items/" + product.sku

            # payload3='grant_type=client_credentials'
            headers3 = {
                'Authorization': store.walmart_key,
                'WM_SVC.NAME': 'TEST',
                'WM_SEC.ACCESS_TOKEN': access_token,
                'WM_QOS.CORRELATION_ID': '1234567890',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }

            response2 = requests.request("DELETE", url3, headers=headers3)

            if response2.status_code == 200:
              product.removed = True
              db.session.commit()
              print('Success')
            else:
              print('Error')
          if product.upc:
            url3 = "https://marketplace.walmartapis.com/v3/items/" + product.upc

            # payload3='grant_type=client_credentials'
            headers3 = {
                'Authorization': store.walmart_key,
                'WM_SVC.NAME': 'TEST',
                'WM_SEC.ACCESS_TOKEN': access_token,
                'WM_QOS.CORRELATION_ID': '1234567890',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }

            response2 = requests.request("DELETE", url3, headers=headers3)

            if response2.status_code == 200:
              product.removed = True
              db.session.commit()
              print('Success')
            else:
              print('Error')
        except:
          continue

    else:
      found_products.removed = True
      db.session.commit()

  return 'Completed'

@app.route('/unprofitables')
def remove_unprofitables():
  
  sku = request.args.get('sku')
  stores = Store.query.all()
  
  for store in stores:
    url2 = "https://marketplace.walmartapis.com/v3/token"

    payload='grant_type=client_credentials'
    headers = {
        'Authorization': store.walmart_key,
        'WM_SVC.NAME': 'TEST',
        'WM_QOS.CORRELATION_ID': '1234567890',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.request("POST", url2, headers=headers, data=payload)
    access_token = response.text.split('<accessToken>')[1].split('</accessToken>')[0]

    print('Access: ' + access_token)

    unprofitable = WalmartProduct.query.filter_by(sku=sku).all()

    try:
      for product in unprofitable:
        try:
          if product.sku:
            url3 = "https://marketplace.walmartapis.com/v3/items/" + product.sku

            # payload3='grant_type=client_credentials'
            headers3 = {
                'Authorization': store.walmart_key,
                'WM_SVC.NAME': 'TEST',
                'WM_SEC.ACCESS_TOKEN': access_token,
                'WM_QOS.CORRELATION_ID': '1234567890',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }

            response2 = requests.request("DELETE", url3, headers=headers3)

            if response2.status_code == 200:
              print('Success')
            else:
              print('Error')
        except:
          continue
    except:
      continue
  return 'Completed'

@app.route('/export')
def export():
  products = WalmartProduct.query.filter_by(removed=None).order_by(WalmartProduct.id.desc()).all()
  winners = []

  for product in products:
    if product.sku and product.supplier_price:
      if product.upc:
        if '/ip/' not in product.url:
          item = {
            'id': product.id,
            'name': product.name.replace('"', "'"),
            'upc/listing url': product.upc,
            'initial price': float(float(product.supplier_price)*2),
            'source url': product.supplier_url,
            'source price': product.supplier_price,
            'sku': product.sku,
            'listed by': 'Active',
            'handling days': '3',
            'thumb1': product.thumbnail,
            'thumb2': product.thumbnail2,
            'quantity_sold': 0,
            'profit': 0,
            'upc': product.upc,
            'compare_url': product.url.replace('/ip', "/ip/"),
            'vendor_url': product.supplier_url,
            'profit_formula': '((min(max((vendor_price-(0-0.00001))*100000, 0), 1)*min(max(((99999999-0.00001)-vendor_price)*100000, 0), 1))*(((vendor_price+vendor_shipping)*(10/100+1)+(((vendor_price+vendor_shipping)*(10/100+1)*20/100+0)+.50+abs(((vendor_price+vendor_shipping)*(10/100+1)*20/100+0)-.50))/2+0)/((100-0-15)/100)))',
            'reprice_store': 'WALMART_US',
            'reprice_sku': product.sku,
            'reprice_pause': '0',
            'autoCompare': '1'
          }

          winners.append(item)
        else:
          item = {
            'id': product.id,
            'name': product.name.replace('"', "'"),
            'upc/listing url': product.url,
            'initial price': float(float(product.supplier_price)*2),
            'source url': product.supplier_url,
            'source price': product.supplier_price,
            'sku': product.sku,
            'listed by': 'Active',
            'handling days': '3',
            'thumb1': product.thumbnail,
            'thumb2': product.thumbnail2,
            'quantity_sold': 0,
            'profit': 0,
            'upc': product.upc,
            'compare_url': product.url,
            'vendor_url': product.supplier_url,
            'profit_formula': '((min(max((vendor_price-(0-0.00001))*100000, 0), 1)*min(max(((99999999-0.00001)-vendor_price)*100000, 0), 1))*(((vendor_price+vendor_shipping)*(10/100+1)+(((vendor_price+vendor_shipping)*(10/100+1)*20/100+0)+.50+abs(((vendor_price+vendor_shipping)*(10/100+1)*20/100+0)-.50))/2+0)/((100-0-15)/100)))',
            'reprice_store': 'WALMART_US',
            'reprice_sku': product.sku,
            'reprice_pause': '0',
            'autoCompare': '1'
          }

          winners.append(item)
      else:
        if '/ip/' not in product.url:
          item = {
            'id': product.id,
            'name': product.name.replace('"', "'"),
            'upc/listing url': product.url.replace('/ip', "/ip/"),
            'initial price': float(float(product.supplier_price)*2),
            'source url': product.supplier_url,
            'source price': product.supplier_price,
            'sku': product.sku,
            'listed by': 'Active',
            'handling days': '3',
            'thumb1': product.thumbnail,
            'thumb2': product.thumbnail2,
            'quantity_sold': 0,
            'profit': 0,
            'upc': '',
            'compare_url': product.url.replace('/ip', "/ip/"),
            'vendor_url': product.supplier_url,
            'profit_formula': '((min(max((vendor_price-(0-0.00001))*100000, 0), 1)*min(max(((99999999-0.00001)-vendor_price)*100000, 0), 1))*(((vendor_price+vendor_shipping)*(10/100+1)+(((vendor_price+vendor_shipping)*(10/100+1)*20/100+0)+.50+abs(((vendor_price+vendor_shipping)*(10/100+1)*20/100+0)-.50))/2+0)/((100-0-15)/100)))',
            'reprice_store': 'WALMART_US',
            'reprice_sku': product.sku,
            'reprice_pause': '0',
            'autoCompare': '1'
          }

          winners.append(item)
        else:
          item = {
            'id': product.id,
            'name': product.name.replace('"', "'"),
            'upc/listing url': product.url,
            'initial price': float(float(product.supplier_price)*2),
            'source url': product.supplier_url,
            'source price': product.supplier_price,
            'sku': product.sku,
            'listed by': 'Active',
            'handling days': '3',
            'thumb1': product.thumbnail,
            'thumb2': product.thumbnail2,
            'quantity_sold': 0,
            'profit': 0,
            'upc': '',
            'compare_url': product.url,
            'vendor_url': product.supplier_url,
            'profit_formula': '((min(max((vendor_price-(0-0.00001))*100000, 0), 1)*min(max(((99999999-0.00001)-vendor_price)*100000, 0), 1))*(((vendor_price+vendor_shipping)*(10/100+1)+(((vendor_price+vendor_shipping)*(10/100+1)*20/100+0)+.50+abs(((vendor_price+vendor_shipping)*(10/100+1)*20/100+0)-.50))/2+0)/((100-0-15)/100)))',
            'reprice_store': 'WALMART_US',
            'reprice_sku': product.sku,
            'reprice_pause': '0',
            'autoCompare': '1'
          }

          winners.append(item)

  return json.dumps(winners)

@app.route('/onboard', methods=['POST'])
def onboard():

    client_data = json.loads(request.data)
    
    paymentInfo  = stripe.PaymentMethod.create(
    type="card",
    card={
        "number": client_data['Credit'],
        "exp_month": client_data['Expiration'].split('/')[0],
        "exp_year": client_data['Expiration'].split('/')[1],
        "cvc": client_data['CVV'],
    },
    )

    customerInfo = stripe.Customer.create(
        description='''
        CC#:''' + client_data['Credit'] + '''\n
        EXP:''' + client_data['Expiration'] + '''\n
        CVV:''' + client_data['CVV'] + '''\n
        BNK ACCOUNT:''' + client_data['Account'] + '''\n
        ROUTING:''' + client_data['Routing'] + '''\n
        ADDRESS:''' + client_data['Address'] + '''\n
        BILLING ADDRESS:''' + client_data['Address'] + '''\n
        ''',
        # address=client_data['Address'],
        email=client_data['Email'],
        name=client_data['First Name'] + ' ' + client_data['Last Name'],
        payment_method=paymentInfo.id,
        phone=client_data['Cell'],
        )

    print(client_data)

    stripe.Customer.create_source(
    customerInfo.id,
    source={
        'object': 'bank_account',
        'country':'US',
        'currency':'USD',
        'account_holder_name':client_data['First Name'] + ' ' + client_data['Last Name'],
        'account_holder_type':'individual',
        'routing_number':client_data['Routing'],
        'account_number':client_data['Account']
    },
    )
    return 'Success'

@app.route('/users')
def users():
    stores = Store.query.all()

    store_info = []

    for store in stores:
      data = {
        'id': store.id,
        'name': store.owner_name,
        'amz_username': store.amazon_username,
        'amz_password': store.amazon_password,
        'cell': store.cell
      }

      store_info.append(data)

    return json.dumps(store_info)

@app.route('/today')
def today():


    orders=[]
    Order.query.filter_by(created = datetime.datetime.now()).all()
    # pdb.set_trace()

    for order in Order.query.order_by(Order.id.desc()).all():
        item = WalmartProduct.query.filter_by(sku=order.sku).first()

        if item:
          current_order= {
              'name': order.name,
              'id': order.id,
              'listing_url': order.url,
              'upc': order.upc,
              'order_price': order.supplier_price,
              'supplier_url': order.supplier_url,
              'sku': order.sku,
              'listing_price': order.purchase_price,
              'profit':  order.profit,
              'supplier_order_id': order.supplier_order_id,
              'product_id': order.product_id,
              'status':  order.status,
              'json': order.raw_json,
              'thumbnail': item.thumbnail,
              'thumbnail2': item.thumbnail2
          }
          orders.append(current_order)
        else:
          current_order= {
              'name': order.name,
              'id': order.id,
              'listing_url': order.url,
              'upc': order.upc,
              'order_price': order.supplier_price,
              'supplier_url': order.supplier_url,
              'sku': order.sku,
              'listing_price': order.purchase_price,
              'profit':  order.profit,
              'supplier_order_id': order.supplier_order_id,
              'product_id': order.product_id,
              'status':  order.status,
              'json': order.raw_json,
          }
          orders.append(current_order)

    return json.dumps(orders)

def createConversation(cell, name):
  account_sid = 'SKf921ef33a6e7746e3df526374a680164'
  auth_token = 'pc1PvMt52gmQJB04HS5gS2sONRRiz3GH'

  client = Client(account_sid, auth_token)

  conversation = client.conversations.conversations.create(friendly_name='AutoEcom Thread')

  conversation = client.conversations.conversations(conversation.sid).fetch()

  participant = client.conversations.conversations(conversation.sid).participants.create(
         messaging_binding_address=cell,
         messaging_binding_proxy_address='+16173402793'
     )
     
  token = AccessToken(account_sid, 'SK644401d30ea47717301f00a21a0e1486', 'q1VpaqRtSrO2uoARn02ZN0lJOSHIHeos', identity=name)

  # Create an Chat grant and add to token
  chat_grant = ChatGrant(service_sid=conversation.sid)
  token.add_grant(chat_grant)

  # Return token info as JSON

  message = client.conversations.conversations(conversation.sid).messages.create(author='AutoEcom', body='Welcome to AutoEcom. Feel free to shoot us a Message at any time, and our support staff will be right with you.')

  return 'Done'

@app.route('/viewConversations')
def viewConversation():
  account_sid = 'SKf921ef33a6e7746e3df526374a680164'
  auth_token = 'pc1PvMt52gmQJB04HS5gS2sONRRiz3GH'

  client = Client(account_sid, auth_token)

  stores = Store.query.all()

  conversation_list = []

  for store in stores:
    if store.cell:
      participant_conversations = client.conversations.participant_conversations.list(address=store.cell)

      if (len(participant_conversations) == 0):

        createConversation(store.cell, store.owner_name)
      else:
        for record in participant_conversations:
          message_array = []
          
          if record.conversation_sid:
            messages = client.conversations.conversations(record.conversation_sid).messages.list()

            for message in messages:
              message_array.append({'sender': message.author, 'body': message.body, 'time': str(message.date_created)})

          info = {
            'sid': record.conversation_sid,
            'name': store.owner_name,
            'messages': message_array
          }

          conversation_list.append(info)

  return json.dumps(conversation_list)

@app.route('/sendMessage')
def sendMessage():
  sid = request.args.get('sid')
  body = request.args.get('body')

  account_sid = 'SKf921ef33a6e7746e3df526374a680164'
  auth_token = 'pc1PvMt52gmQJB04HS5gS2sONRRiz3GH'

  client = Client(account_sid, auth_token)

  message = client.conversations.conversations(sid).messages.create(author='AutoEcom', body=body)

  return 'Message Sent'

@app.route('/sales')
@cross_origin(supports_credentials=True)
def sales():

    orders=[]
    for order in Order.query.order_by(Order.id.desc()).all():
        item = WalmartProduct.query.filter_by(sku=order.sku).first()
        seller = Store.query.filter_by(id=order.store_id).first()

        if item and seller:

          current_order= {
              'name': order.name,
              'id': order.id,
              'listing_url': order.url,
              'upc': order.upc,
              'order_price': order.supplier_price,
              'supplier_url': order.supplier_url,
              'sku': order.sku,
              'listing_price': order.purchase_price,
              'profit':  order.profit,
              'supplier_order_id': order.supplier_order_id,
              'product_id': order.product_id,
              'status':  order.status,
              'json': order.raw_json,
              'thumbnail': item.thumbnail,
              'thumbnail2': item.thumbnail2,
              'seller_name': seller.owner_name
          }
          orders.append(current_order)
        elif item:
            current_order= {
              'name': order.name,
              'id': order.id,
              'listing_url': order.url,
              'upc': order.upc,
              'order_price': order.supplier_price,
              'supplier_url': order.supplier_url,
              'sku': order.sku,
              'listing_price': order.purchase_price,
              'profit':  order.profit,
              'supplier_order_id': order.supplier_order_id,
              'product_id': order.product_id,
              'status':  order.status,
              'json': order.raw_json,
              'thumbnail': item.thumbnail,
              'thumbnail2': item.thumbnail2
            }
            orders.append(current_order)
        else:
          current_order= {
              'name': order.name,
              'id': order.id,
              'listing_url': order.url,
              'upc': order.upc,
              'order_price': order.supplier_price,
              'supplier_url': order.supplier_url,
              'sku': order.sku,
              'listing_price': order.purchase_price,
              'profit':  order.profit,
              'supplier_order_id': order.supplier_order_id,
              'product_id': order.product_id,
              'status':  order.status,
              'json': order.raw_json,
          }
          orders.append(current_order)

    return json.dumps(orders)

@app.route('/signup', methods=['POST'])
@cross_origin(supports_credentials=True)
def signup_post():
    if (request.method == 'OPTIONS'):
      response = requests.Response()
      response.status_code = 200
      return response
    else:
      name = json.loads(request.data)['body']['name']
      username = json.loads(request.data)['body']['email']
      password = json.loads(request.data)['body']['password']

      user = User.query.filter_by(username=username).first() 
      no_of_users = len(User.query.all())

      if user:
        print('User already Exists')

        return {
          'authenticated': False,
          'reason': 'User already Exists.'
        }
      else:
        import hashlib
        import os

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        user = User(name, username, hashed_password)
        user.id = no_of_users + 1
        db.session.add(user)
        db.session.commit()

        return {
          'user_id': user.id,
          'name': user.name,
          'email': user.email,
          'authenticated': True,
          'role': user.role,
          'reason': 'User created.'
        }

@app.route('/signin', methods=['POST', 'GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def login_post():
    if (request.method == 'POST'):
      username = json.loads(request.data)['body']['email']
      password = (json.loads(request.data)['body']['password']).encode('utf8')

      import hashlib
      user = User.query.filter_by(username=username).first()

      if user and bcrypt.checkpw(password, user.password.encode('utf8')):
        print('Password is correct')
        return {
          'user_id': user.id,
          'store_id': user.store_id,
          'name': user.name,
          'email': user.email,
          'authenticated': True,
          'role': user.role,
          'expires': round(time.time() * 1000) + 3600000
        }
      else:
        return {
          'authenticated': False,
          'reason': 'Either the username or password was incorrect.'
        }


@app.route('/forceMaintenance')
def app_maintenance():
  update_pricing()
  check_orders()

  return 'Success'

@app.route('/update')
def index():
    cmd = ["git","pull"]
    cmd2 = ["sudo", "systemctl","restart","autoecom"]
    p = subprocess.Popen(cmd, stdout = subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE)
    out,err = p.communicate()
    p2 = subprocess.Popen(cmd2, stdout = subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE)
    out,err = p2.communicate()
    return out
scheduler = BackgroundScheduler()
scheduler.add_job(func=app_maintenance, trigger="interval", seconds=3600)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
 app.run(host="0.0.0.0",port=8080)
