import pandas as pd

class DataItem(object):
	def __init__(self, data = None, dtype = None):
		object.__init__(self)
		self.data  = None
		self.dtyle = None
		try:
		int(data)
		float(data)	
		
		

	def to_int(self):
		try:
			int_data  = int(self.data)
			self.data = int_data
			return self.data
		except ValueError:
			return None
		
		

	def data_type(self):
		return type(self.data)




m = DataItem("12eas")

print (m.to_int())
print (m.data)