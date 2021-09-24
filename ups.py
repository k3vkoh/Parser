# ups

import pandas as pd
import re
import pathlib
import os
import shutil
import datetime


def compile(data_d):
	# this function will extract all the important information

	# this is the schema for the header table
	d = {
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

	# this is the schema for the details table
	c = {
		'invoice number':[],
		'tracking number': [],
		'line item': [],
		'charge code': [],
		'charge description': [],
		'charge amount': []
	}

	data = data_d

	vendor_name = 'UPSN'

	data_separator = "*"
	segment_terminator = data[105]

	lines = data.split(segment_terminator)

	invoice_number = None
	invoice_date = None
	account_number = None
	bill2address = None

	line_item = None
	tracking_number = None

	tracking_bool = False
	tracking_count = 0

	index = None

	error = False

	# this will extract all the info
	i = 0
	while i < len(lines):

		if re.match('ST\\*', lines[i]):
			try:
				tracking_bool = False
				invoice_number = None
				invoice_date = None
				account_number = None
				bill2address = None
			except Exception as e:
				error = True

		if re.match('LX\\*', lines[i]):
			try:
				fillempty(d)
				line_item = None
				tracking_number = None
				tracking_count += 1
				index = tracking_count - 1
				tracking_bool = True
				elements = lines[i].split(data_separator)
				d['invoice number'][index] = invoice_number
				d['invoice date'][index] = invoice_date
				d['account number'][index] = account_number
				d['bill to address'][index] = bill2address
				d['vendor'][index] = vendor_name
				line_item = elements[1]
				d['line item'][index] = line_item
			except Exception as e:
				error = True

		# this information is the same for each delivery number
		if not tracking_bool:
			
			if re.match('B3\\*', lines[i]):
				# extracts invoice info
				try:
					elements = lines[i].split(data_separator)
					invoice_number = elements[2]
					invoice_date = elements[6]
				except Exception as e:
					error = True
			
			elif re.match('N9\\*\\d\\d', lines[i]):
				# extracts account number
				try:
					elements = lines[i].split(data_separator)
					account_number = elements[2]
				except Exception as e:
					error = True
			
			elif re.match('N1\\*BT\\*', lines[i]):
				# extracts bill2address
				try:
					address = ''
					address_search = True
					keywords = ['N1', 'N2', 'N3', 'N4', 'BT']
					while address_search:

						elements = lines[i].split(data_separator)
						for x in elements:
							if x not in keywords:
								address = address + ' ' + x

						if (re.match('N4\\*', lines[i])):
							address_search = False
							continue

						try:
							elements = lines[i+1].split(data_separator)
							if elements[0] not in keywords:
								address_search = False
								continue
						except:
							print('Error with address finding')

						i += 1

					bill2address = address
				except Exception as e:
					# f.write('bill2address ' + str(e) + '\n')
					error = True

		# this information is specific for each delivery number
		else:

			if re.match('N9\\*CN', lines[i]):
			# extracts tracking number
				try:
					elements = lines[i].split(data_separator)
					tracking_number = elements[2]
					d['tracking number'][index] = tracking_number
				except Exception as e:
					# f.write('N9-CN ' + str(e) + '\n')
					error = True
			
			elif re.match('N9\\*CR', lines[i]) and d['reference number'][index] == None:
			# extracts reference num
				try:
					elements = lines[i].split(data_separator)
					d['reference number'][index] = elements[2]
				except Exception as e:
					# f.write('N9-CR ' + str(e) + '\n')
					error = True
			
			elif re.match('L0\\*', lines[i]):
				# extracts weight info
				try:
					elements = lines[i].split(data_separator)
					if (elements[5] == 'N'):
						d['gross weight'][index] = elements[4]
					elif (elements[5] == 'B'):
						d['actual weight'][index] = elements[4]
				except Exception as e:
					# f.write('L0 ' + str(e) + '\n')
					error = True

			elif re.match('L1\\*', lines[i]):
			# extracts charge info
				try:
					elements = lines[i].split(data_separator)
					code8 = elements[8]
					value = int(elements[4])
					value = value/100.0
					c['invoice number'].append(invoice_number)
					c['tracking number'].append(tracking_number)
					c['line item'].append(line_item)
					c['charge amount'].append(value)

					if code8 == '':
						c['charge code'].append(None)
					else:
						c['charge code'].append(code8)

					if len(elements) >= 13:
						code12 = elements[12]
						if code12 == '':
							c['charge description'].append(None)
						else:
							c['charge description'].append(code12)
					else:
						c['charge description'].append(None)
				
				except Exception as e:
					# f.write('charge ' + str(e) + '\n')
					error = True


			elif re.match('N1\\*SH\\*', lines[i]):
			# extracts sender address
				try:
					address = ''
					address_search = True
					keywords = ['N1', 'N2', 'N3', 'N4', 'SH']
					while address_search:
						elements = lines[i].split(data_separator)
						for x in elements:
							if x not in keywords:
								address = address + ' ' + x

						if (re.match('N4\\*', lines[i])):
							address_search = False
							continue

						try:
							elements = lines[i+1].split(data_separator)
							if elements[0] not in keywords:
								address_search = False
								continue
						except:
							print('Error with address finding')

						i += 1

					d['sender address'][index] = address
				except Exception as e:
					# f.write('sender address ' + str(e) + '\n')
					error = True

			elif re.match('N1\\*ST\\*', lines[i]):
			# extracts receiver address
				try:
					address = ''
					address_search = True
					keywords = ['N1', 'N2', 'N3', 'N4', 'ST']
					while address_search:
						elements = lines[i].split(data_separator)
						for x in elements:
							if x not in keywords:
								address = address + ' ' + x
						if (re.match('N4\\*', lines[i])):
							address_search = False
							continue

						try:
							elements = lines[i+1].split(data_separator)
							if elements[0] not in keywords:
								address_search = False
								continue
						except:
							print('Error with address finding')

						i += 1

					d['receiver address'][index] = address
				except Exception as e:
					# f.write('receiver address ' + str(e) + '\n')
					error = True

		i += 1

	# f.close()
	return {'d': d, 'c': c, 'error':error}

def fillempty(d):
	data = d
	for key in data:
		data[key].append(None)

	return data
