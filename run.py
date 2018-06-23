import urllib.request, tldextract, os

# Ensures we are using the correct code page in windows console!
os.system("chcp 65001")

__HOSTS_HEADER = '# grufwubs combined hosts\n127.0.0.1 localhost\n::1 localhost\n\n# Start of entries generated by download_stripped_hosts.py\n'
__BACKUP_DIR = 'backups/'
__BACKUP_EXT = '.txt'

class HostList:
	def __init__(self, url = str()):
		self.__NAME = self.create_name(url)
		self.__HOSTS = dict()
		self.__NEW_DATA = False # Change name of this flag and connected functions. Gives the wrong idea of what it's actually doing
	
	def create_name(self, url = str()):
		result = ''
		ext = tldextract.extract(url)
		result += ext.domain

		split_url = url.split('/')
		result += '_' + split_url[3]
		result += '_' + split_url[len(split_url) - 1].split('.')[0]

		return result

	def get_name(self):
		return self.__NAME

	def set_hosts(self, hosts = dict()):
		self.__HOSTS = hosts
	
	def get_hosts(self):
		return self.__HOSTS

	def set_new_data_flag(self):
		self.__NEW_DATA = True

	def has_new_data(self):
		return self.__NEW_DATA

def download_process_hosts(url_str):
	# Downloads hosts and passes them to the method addToDict() which returns a sorted, stripped dict of hosts
	print('Downloading hosts from %s' % url_str)
	hostlist = HostList(url_str)

	try:
		raw_text = download(url_str)
		hostlist.set_new_data_flag()
	except Exception:
		print('Unable to download hosts from %s. Retrieving saved backup...' % url_str)
		raw_text = retrieve_hosts_backup(url_str)

	processed_hosts = process_hosts(raw_text)
	hostlist.set_hosts(processed_hosts)
	return hostlist

def download(url_str):
	response = urllib.request.urlopen(url_str)
	data = response.read()
	text = data.decode('utf-8')
	return text

def retrieve_hosts_backup(url_str):
	file_str = __BACKUP_DIR + url_str + __BACKUP_EXT
	if not os.path.exists(file_str):
		print('[!] Hosts backup for %s not found!' % url_str)
		return
	
	file = open(file_str, 'r')
	raw_text = str()
	for line in file.read():
		text += line + '\n'
	return raw_text

def process_hosts(data):
	print('Stripping to raw hosts')
	hosts = dict()
	for line in data.split('\n'):
		lineStr = ""
		lineStr += line
		# Skip unusable lines
		if not lineStr:
			continue

		# Strips any whitespace
		lineStr = lineStr.strip()
        # Strips initial pipe symbols
		lineStr = lineStr.replace('|', '')
        # Strips use of 'www.'
		lineStr = lineStr.replace('www.', '')
        # Strips initial '0.0.0.0 ' / '127.0.0.1 ' from host files
		lineStr = lineStr.replace('0.0.0.0 ', '')
		lineStr = lineStr.replace('127.0.0.1 ', '')

		if '#' in lineStr:
			# Skips comment lines and lines blocking specific CSS items
			if lineStr.startswith('#') or '##' in lineStr:
				continue
			else:
				lineStr = lineStr.split('#')[0] # Removes excess comment strings located after host

		if '^' in lineStr:
			if lineStr.endswith('^third-party'):
				lineStr = lineStr.replace('^third-party', '')

			elif lineStr.endswith('^$important'):
				lineStr = lineStr.replace('^$important', '')

			else:
				if lineStr.endswith('^'):
					lineStr = lineStr.replace('^', '')

				else:
					continue

		if '$' in lineStr:
			continue
		if '!' in lineStr:
			continue
		if ':' in lineStr:
			continue
		if '@' in lineStr:
			continue
		if '*' in lineStr:
			continue
		if '?' in lineStr:
			continue
		if '=' in lineStr:
			continue
		if '[' in lineStr:
			continue
		if ']' in lineStr:
			continue
		if ',' in lineStr:
			continue
		if '/' in lineStr:
			continue
		if '(' in lineStr:
			continue
		if ')' in lineStr:
			continue
		if ';' in lineStr:
			continue
		if '%' in lineStr:
			continue
		if '{' in lineStr:
			continue
		if '{' in lineStr:
			continue

        # Skips final unusables
		if lineStr.startswith('.') or lineStr.endswith('.'):
			continue

		# Adds the host to a dictionary which serves as the value to a parent dictionary (passed in the method argument), with the registered domain as the key
		ext = tldextract.extract(lineStr)
		base_domain = ext.registered_domain
		if base_domain == '' or base_domain == '\n' or base_domain == ' ':
			continue

		# Write line to dictionary
		td = hosts.get(base_domain, dict())
		td[lineStr] = td.get(lineStr, 0) + 1
		hosts[base_domain] = td

	return hosts

def processWhitelist(data):
	whitelist = dict()
	for line in data.split('\n'):
		lineStr = ""
		lineStr += line
		# Skip unusable lines
		if not lineStr:
			continue
		if '#' in lineStr:
			if lineStr.startswith('#') or '##' in lineStr:
				continue
			else:
				lineStr = lineStr.split('#')[0]
		if '$' in lineStr:
			continue
		if '!' in lineStr:
			continue
		if ':' in lineStr:
			continue
		if '@' in lineStr:
			continue
		if '*' in lineStr:
			continue
		if '?' in lineStr:
			continue
		if '=' in lineStr:
			continue
		if '[' in lineStr:
			continue
		if ']' in lineStr:
			continue
		if ',' in lineStr:
			continue
		if '/' in lineStr:
			continue
		if '(' in lineStr:
			continue
		if ')' in lineStr:
			continue
		if ';' in lineStr:
			continue
		if '%' in lineStr:
			continue
		if '{' in lineStr:
			continue
		if '{' in lineStr:
			continue
        # Strips any whitespace
		lineStr = lineStr.strip()
        # Strips initial pipe symbols
		lineStr = lineStr.replace('|', '')
        # Strips use of 'www.'
		lineStr = lineStr.replace('www.', '')
        # Skips final unusables
		if lineStr.startswith('.') or lineStr.endswith('.'):
			continue
		# Adds the host to a dictionary which serves as the value to a parent dictionary (passed in the method argument), with the registered domain as the key
		ext = tldextract.extract(lineStr)
		base_domain = ext.registered_domain
		if base_domain == '' or base_domain == '\n' or base_domain == ' ':
			continue
		# Write to whitelist
		td = whitelist.get(base_domain, dict())
		td[lineStr] = td.get(lineStr, 0) + 1
		whitelist[base_domain] = td
	return whitelist

def backupToFile(data, file_name):
	print('Backing up host list %s...' % file_name)
	if len(data.keys()) == 0:
		print('Dict empty. Not backing up.')
		print(data)
		return

	f = open(file_name, 'w', encoding='utf-8')
	for d in data.keys():
		hosts_dict = data[d]
		for key in hosts_dict:
			f.write(key + '\n')
	f.close()

def compileAndCheck(blocklists, whitelists):
	blocklist = list()
	whitelist = list()

	for w_list in whitelists:
		w_list_dict = w_list.get_hosts()
		for key in w_list_dict.keys():
			for host in w_list_dict[key]:
				whitelist.append(host)
	whitelist = list(dict.fromkeys(whitelist))

	for b_list in blocklists:
		b_list_dict = b_list.get_hosts()
		for key in b_list_dict.keys():
			for host in b_list_dict[key]:
				if not host in whitelist:
					blocklist.append(host)
	blocklist = list(dict.fromkeys(blocklist))

	return blocklist

# def getOrderedKeyList(d):
# 	l = list()
# 	for i in range(0, 10):
# 		if d.get(i):
# 			l.append(i)
# 	return l

# def getHostLengthDictionary(d):
# 	return_dict = dict()
# 	for key in d.keys():
# 		s = key.split('.')
# 		i = len(s)
# 		return_dict.setdefault(i, list()).append(key)
# 	return return_dict

# def getUniqueHosts(d):
# 	# Returns a list of unique hosts for each registered domain, that don't overlap subdomains (e.g. stats.facebook.com and s.stats.facebook.com), keeping only the shortest.
# 	# For each registered domain, goes through the listed hosts and creates a dictionary with {"Number of domain levels" : List[domain, domain, domain]}
# 	length_dict = getHostLengthDictionary(d)
# 	return_list = list()
# 	# Creates an ordered list of keys (which are the domain level ints).
# 	key_list = getOrderedKeyList(length_dict)
# 	# BUG: another hacky fix right here to account for key_list sometimes being empty
# 	if len(key_list) == 0:
# 		return [""]
# 	min_length = min(key_list)
# 	min_length_host = length_dict[min_length][0]
# 	ext = tldextract.extract(min_length_host)
# 	# If dictionary contains the registered domain (so all traffic should be blocked), returns only this.
# 	if min_length_host == ext.registered_domain:
# 		return_list.append(min_length_host)
# 	else:
# 		# Else goes through the dictionary and finds unique non-overlapping domains
# 		previous = list()
# 		# BUG: this for loop seems to create duplicates in some instances
# 		for length in key_list:
# 			current = length_dict[length]
# 			if length == min_length:
# 				previous = current
# 				return_list.extend(current)
# 			else:
# 				add_to_return_list = list()
# 				for host in return_list:
# 					for entry in current:
# 						if host not in entry and len(entry) > len(host):
# 							add_to_return_list.append(entry)
# 				return_list.extend(add_to_return_list)
# 	return return_list

def main():
	print('Downloading blocklists...')
	blocklists = list()
	# blocklists.append( download_process_hosts('https://filters.adtidy.org/extension/chromium/filters/15.txt') )
	blocklists.append( download_process_hosts('https://raw.githubusercontent.com/piperun/iploggerfilter/master/filterlist') )
	blocklists.append( download_process_hosts('https://raw.githubusercontent.com/quidsup/notrack/master/trackers.txt') )
	blocklists.append( download_process_hosts('https://raw.githubusercontent.com/grufwub/DNS-Blocklist-Compiler/master/blacklist.txt') )
	# blocklists.append( download_process_hosts('https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts') )
	blocklists.append( download_process_hosts('https://filters.adtidy.org/extension/chromium/filters/11.txt') )
	blocklists.append( download_process_hosts('https://raw.githubusercontent.com/anarki999/Adblock-List-Archive/master/Better.fyiTrackersBlocklist.txt'))
	blocklists.append( download_process_hosts('https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.2o7Net/hosts'))
	blocklists.append( download_process_hosts('https://raw.githubusercontent.com/AdAway/adaway.github.io/master/hosts.txt'))
	blocklists.append( download_process_hosts('http://someonewhocares.org/hosts/zero/hosts'))
	blocklists.append( download_process_hosts('http://winhelp2002.mvps.org/hosts.txt'))
	blocklists.append( download_process_hosts('https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&mimetype=plaintext&useip=0.0.0.0'))
	blocklists.append( download_process_hosts('https://raw.githubusercontent.com/lightswitch05/hosts/master/ads-and-tracking-extended.txt'))
	blocklists.append( download_process_hosts('https://raw.githubusercontent.com/StevenBlack/hosts/master/data/StevenBlack/hosts'))
	blocklists.append( download_process_hosts('http://www.malwaredomainlist.com/hostslist/hosts.txt'))
	blocklists.append( download_process_hosts('https://zerodot1.gitlab.io/CoinBlockerLists/hosts_browser'))
	blocklists.append( download_process_hosts('https://raw.githubusercontent.com/mitchellkrogza/Badd-Boyz-Hosts/master/hosts'))
	# blocklists.append( download_process_hosts('https://raw.githubusercontent.com/cbuijs/airelle/master/ads.hosts.list'))
	# blocklists.append( download_process_hosts('https://raw.githubusercontent.com/cbuijs/airelle/master/trackers.hosts.list'))
	# blocklists.append( download_process_hosts('https://raw.githubusercontent.com/cbuijs/airelle/master/malware.hosts.list'))
	# blocklists.append( download_process_hosts('https://raw.githubusercontent.com/Yhonay/antipopads/master/hosts') )
	# blocklists.append( download_process_hosts('https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt') )
	# blocklists.append( download_process_hosts('https://raw.githubusercontent.com/anudeepND/blacklist/master/CoinMiner.txt') )
	print('-------------------------\n')

	print('Downloading whitelists...')
	whitelists = list()
	whitelists.append( download_process_hosts('https://raw.githubusercontent.com/grufwub/DNS-Blocklist-Compiler/master/whitelist.txt') )
	whitelists.append( download_process_hosts('https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt') )
	print('--------------------------\n')

	print('Backing up host lists...')
	if not os.path.exists(__BACKUP_DIR):
		print('Host backups directory not found (is this first run?). Creating...')
		os.makedirs(__BACKUP_DIR)

	for blocklist in blocklists:
		if not blocklist.has_new_data(): # skips backing up blocklist if no data downloaded
			continue

		file_name = __BACKUP_DIR + blocklist.get_name() + __BACKUP_EXT
		backupToFile(blocklist.get_hosts(), file_name)

	for whitelist in whitelists:
		if not whitelist.has_new_data(): # skips backing up whitelist if no data downloaded
			continue

		file_name = __BACKUP_DIR + whitelist.get_name() + __BACKUP_EXT
		backupToFile(whitelist.get_hosts(), file_name)
	print('--------------------------\n')

	print('Compiling hosts...')
	compiled_hosts = compileAndCheck(blocklists, whitelists)

	print('Writing hosts to file...')
	count = 1
	f = open('hosts', 'w', encoding='utf-8')
	f.write(__HOSTS_HEADER)
	for host in compiled_hosts:
		# Final dead host remnoval
		if host == '' or host == '\n':
			continue
		host = '127.0.0.1 ' + host.strip()
		f.write(host + '\n')
		# print(count)
		# print(host)
		# print('------------------------------------')
		count += 1
	f.close()
	print('--------------------------\n')
	print('Done! Counted %d entries. (:' % count)

if __name__ == '__main__':
	main()
