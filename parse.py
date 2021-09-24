#parser main

import pandas as pd
import re
import pathlib
import os
import shutil
import datetime
import numpy as np

import fedex
import ups

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]
my_date = datetime.datetime.now().strftime('%Y-%m-%d')[:11]
my_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

header = {
	'vendor':[],
	'invoice number': [],
	'invoice date': [],
	'account number': [],
	'bill to address': [],
	'line item':[],
	'tracking number': [],
	'reference number': [],
	'gross weight': [],
	'actual weight': [],
	'# of packages': [],
	'sender address': [],
	'receiver address':[]
}

charge = {
	'invoice number':[],
	'tracking number': [],
	'line item': [],
	'charge code': [],
	'charge description': [],
	'charge amount': []
}

df_header = pd.DataFrame(data = header)
df_charge = pd.DataFrame(data = charge)


def convert(data, vendor):

	global df_header, df_charge

	r = None

	try:
		# will compile depending if vendor is fedex or ups
		if vendor == 'UPSN':
			r = ups.compile(data)
		elif vendor == 'FEDEX':
			r = fedex.compile(data)
		else:
			raise ValueError('ERROR 00: INVALID VENDOR')

		d = r['d']
		c = r['c']

		if not r['error']:
			df = pd.DataFrame(data = d)
			df2 = pd.DataFrame(data = c)
			df['JobDate'] = timestamp
			df2['JobDate'] = timestamp

			df_header = pd.concat([df_header, df])
			df_charge = pd.concat([df_charge, df2])

	except:
		pass

def get_data():
	# puts the data into an excel file

	path = my_date + "-charge.xlsx"
	path2 = my_date + "-header.xlsx"
	df_header.index = np.arange(1, len(df_header)+1)
	df_charge.index = np.arange(1, len(df_charge)+1)
	writer = pd.ExcelWriter(path, engine='xlsxwriter')
	df_charge.to_excel(writer, sheet_name='charges')
	writer2 = pd.ExcelWriter(path2, engine='xlsxwriter')
	df_header.to_excel(writer2, sheet_name='header')
	wb = writer.book
	wb2 = writer2.book
	ws = writer.sheets['charges']
	ws2 = writer2.sheets['header']
	ws.set_column('B:B', 16)  
	ws.set_column('C:C', 19)
	ws.set_column('D:D', 8)
	ws.set_column('E:E', 11)  
	ws.set_column('F:F', 16)
	ws.set_column('G:G', 14)
	ws.set_column('H:H', 18)
	writer.save()
	writer2.save()


 

def parse_main():
	for path in pathlib.Path('./data').iterdir():
		if path.is_file():
			f = open(path, "r")
			data = f.read()
			f.close()

			vendor_name = None

			if 'FEDEX' in data:
				vendor_name = 'FEDEX'
			elif 'UPS' in data:
				vendor_name = 'UPSN'

			convert(data, vendor_name)

	get_data()


if __name__ == '__main__' :
	parse_main()
