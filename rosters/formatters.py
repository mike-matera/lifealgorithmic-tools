import re
import crypt 

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def extract_name(student):
	rval = dict()
	parts = student['fullname'].split()
	rval['family'] = parts[-1]
	rval['given'] = ' '.join(parts[0:-1])
	return rval


def gen_login(section_map, class_number, student):
	m = re.match(r'(\w+)(\d+).*', class_number)
	if m is None: 
		raise ValueError(f"Misunderstood class_number: {class_number}")
	class_number = m.group(1) + m.group(2)
	rval = extract_name(student)
	firstname = rval['given'].replace(' ', '')
	lastname = rval['family'].replace(' ', '')
	lastname = lastname.replace('.', '')
	lastname = lastname.replace('-', '')
	first_bound = min(3, len(firstname))
	last_bound = min(3, len(lastname))
	rval['login'] = lastname[0:first_bound].lower() + firstname[0:last_bound].lower() + class_number
	rval['password'] = firstname[0:2] + lastname[0:2] + student['id'][-4:]
	rval['safename'] = firstname[0] + '. ' + lastname
	rval['unixgroup'] = section_map['department'] + class_number
	return rval


def gen_unix(section_map):
	with open(f"{section_map['prefix']}unix.sh", 'w') as f:
		for student in section_map['roster']:
			login = gen_login(section_map, section_map['number'], student)
			f.write('useradd -g users -G users,' + login['unixgroup'] +\
					' -d /home/' + login['unixgroup'] + '/' + login['login'] +\
					' -m -p \'' + crypt.crypt(login['password'], '$6$af9$') + '\'' +\
					' -c "' + login['given'] + ' ' + login['family'] + '" ' +\
					login['login'] + '\n')


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


def gen_vlab(section_map):
	with open(f"{section_map['prefix']}vlab.bat", 'w') as f:
		for student in section_map['roster']:
			login = gen_login(section_map, section_map['number'], student)
			unixclass = login['unixgroup']
			ou = unixclass.upper()
			f.write('dsadd user "CN='+login['given']+' '+login['family']+',OU='+ou+',DC=cislab,DC=net"'+\
					' -samid ' + login['login'] +\
					' -upn ' + login['login'] + '@cislab.net' +\
					' -fn "' + login['given'] + '"' +\
					' -ln "' + login['family'] + '"' +\
					' -pwd ' + login['password'] +\
					' -desc "' + unixclass + ' student"' +\
					' -memberof "CN='+unixclass+',CN=users,DC=cislab,DC=net"' +\
					' "CN=students,CN=users,DC=cislab,DC=net"' +\
					' -canchpwd yes -pwdneverexpires yes -acctexpires never -disabled no\n')


def gen_sql(section_map):
	with open(f"{section_map['prefix']}db.sql", 'w') as f:
		f.write('FLUSH PRIVILEGES;\n'); 
		for student in section_map['roster']:
			login = gen_login(section_map, section_map['number'], student)
			f.write('DROP USER IF EXISTS \'' + login['login'] + '\';\n');
			f.write('CREATE USER \'' + login['login'] + '\'@\'%.cis.cabrillo.edu\' IDENTIFIED BY \'' + login['password'] + '\';\n'); 
			f.write('GRANT ALL ON `' + login['login'] + '\\_%`.* to \'' + login['login'] + '\'@\'%.cis.cabrillo.edu\' WITH GRANT OPTION;\n'); 
			f.write('GRANT SELECT ON `public\\_%`.* to \'' + login['login'] + '\'@\'%.cis.cabrillo.edu\';\n'); 
			f.write('GRANT SELECT ON `mysql`.`user` to \'' + login['login'] + '\'@\'%.cis.cabrillo.edu\';\n'); 
			f.write('GRANT FILE ON *.* to \'' + login['login'] + '\'@\'%.cis.cabrillo.edu\';\n'); 
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
