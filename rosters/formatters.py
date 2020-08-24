import re
import crypt 

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def gen_maillist(section_map):
	with open(f"{section_map['prefix']}email-list.txt", 'w') as f:
		for q in section_map['roster']:
			f.write('"' + q['fullname'] + '" <' + q['email'] + ">\n")


def gen_netlab(section_map):
	with open(f"{section_map['prefix']}netlab.csv", 'w') as f:
		f.write('User ID, Given/First Name, Family/Last Name, Display Name, Email\n')
		for student in section_map['roster']:
			login = gen_login(section_map, section_map['number'], student)
			f.write(student['email'] + ',' + login['given'] + ',' + login['family'] + ',' + student['fullname'] + ',' + student['email'] + '\n')


def gen_sql(section_map):
	with open(f"{section_map['prefix']}db.sql", 'w') as f:
		f.write('FLUSH PRIVILEGES;\n'); 
		for student in section_map['roster']:
			login = gen_login(section_map, section_map['number'], student)
			f.write('DROP USER IF EXISTS \'' + login['login'] + '\';\n');
			f.write('CREATE USER \'' + login['login'] + '\'@\'%\' IDENTIFIED BY \'' + login['password'] + '\';\n'); 
			f.write('GRANT ALL ON `' + login['login'] + '\\_%`.* to \'' + login['login'] + '\'@\'%\' WITH GRANT OPTION;\n'); 
			f.write('GRANT SELECT ON `public\\_%`.* to \'' + login['login'] + '\'@\'%\';\n'); 
			f.write('GRANT SELECT ON `mysql`.`user` to \'' + login['login'] + '\'@\'%\';\n'); 
			f.write('#GRANT FILE ON *.* to \'' + login['login'] + '\'@\'%\';\n'); 
			# Fixes a bug in some MySQL versions...
			f.write('FLUSH PRIVILEGES;\n'); 


def gen_playbook(section_map):
	config = {
		'users': [],
	}
	for student in section_map['roster']:
		login = gen_login(section_map, section_map['number'], student)
		config['users'].append({
			'name': login['login'],
			'comment': login['safename'],
			'password': crypt.crypt(login['password'], crypt.mksalt()),
			'groups': ['users', login['unixgroup']], 
			'home': f"/home/{login['unixgroup']}/{login['login']}",
		})
	with open(f"{section_map['prefix']}users.yaml", 'w') as f:
		f.write(dump(config, Dumper=Dumper))
