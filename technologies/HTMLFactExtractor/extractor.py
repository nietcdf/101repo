#! /usr/bin/env python
from HTMLParser import HTMLParser
import json
import re
import sys


class FragmentHTMLParser(HTMLParser):
	tree_stack = []
	fragments = {"fragments": []}

	def get_line_number(self):
		return self.getpos()[0]

	def count_fragments(self, new_fragment):
		fragment_count = 0
		for fragment in self.get_current_position()["fragments"]:
			if fragment["name"] == new_fragment["name"] and fragment["classifier"] == new_fragment["classifier"]:
				fragment_count += 1
		return fragment_count

	def get_current_position(self):
		position = self.fragments
		for fragment_id in self.tree_stack:
			position = position["fragments"][fragment_id]
		return position

	def get_fragment_by_name_and_classifier(self, new_fragment):
		fragment_list = self.get_current_position()["fragments"]
		for fragment in fragment_list:
			if fragment["name"] == new_fragment["name"] and fragment["classifier"] == new_fragment["classifier"]:
				return fragment

	def create_index(self, new_fragment):
		old_index = self.count_fragments(new_fragment)
		if old_index == 1:
			self.get_fragment_by_name_and_classifier(new_fragment)["index"] = 1
			new_fragment['index'] = 2
		elif old_index > 1:
			new_fragment['index'] = old_index + 1

	def add_fragment(self, new_fragment, push_tree_stack):
		self.create_index(new_fragment)
		count_of_fragments = len(self.get_current_position()["fragments"])
		self.get_current_position()["fragments"].append(new_fragment)
		if push_tree_stack:
			self.tree_stack.append(count_of_fragments)

	#Begin Override Functions
	def handle_starttag(self, tag, attrs):
		self.add_fragment(
			{"name": str(tag), "startLine": self.get_line_number(), "fragments": [], "classifier": "tag"}, True)
		for attribute in attrs:
			attribute_fragment = {"name": str(attribute[0]), "startLine": self.get_line_number(),
								  "endLine": self.get_line_number(), "fragments": [], "classifier": "attribute",
								  "value": str(attribute[1])}
			self.get_current_position()["fragments"].append(attribute_fragment)
		#debugBegin
		#print("Beg " + str(tag) + str(self.tree_stack))

	def handle_endtag(self, tag):
		self.get_current_position()["endLine"] = self.get_line_number()
		self.tree_stack.pop()

		#debugBegin
		#print("End " + str(tag) + str(self.tree_stack))

	def handle_data(self, data):
		if re.search("\S", data):
			end_line = self.get_line_number() + len(data.splitlines()) - 1
			text_fragment = {"name": "text", "startLine": self.get_line_number(), "endLine": end_line,
							 "fragments": [], "classifier": "text"}
			self.add_fragment(text_fragment, False)

	def get_fragments(self):
		return self.fragments


parser = FragmentHTMLParser()
parser.feed(sys.stdin.read())

#parser.feed('<html>\n'
#			'<head>\n'
#			'<title><h1>Test</h1></title>\n'
#			'<script src="source/sfd/fs.js" lang="JS"></script>'
#			'</head>\n'
#			'<body>\n'
#			'<h1>Parse me!</h1>\n'
#			'<h1>Parse me too!</h1>\n'
#			'<h1>Hey <b>P</b><b>a</b>rse me tooo!</h1>\n'
#			'</body>\n'
#			'</html>\n')
print(json.dumps(parser.get_fragments()))