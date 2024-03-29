import threadmedaddy as tmd
import tldextract, os
from urllib.request import urlopen, URLError, HTTPError

# Ensures we are using the correct code page in windows consoles!
if os.name == "nt":
	os.system("chcp 65001")

__HOSTS_HEADER = '# grufwubs combined hosts\n127.0.0.1 localhost\n127.0.0.1 localhost.localdomain\n127.0.0.1 local\n255.255.255.255 broadcasthost\n::1 localhost\n::1 ip6-localhost\n::1 ip6-loopback\nfe80::1%lo0 localhost\nff00::0 ip6-localnet\nff00::0 ip6-mcastprefix\nff02::1 ip6-allnodes\nff02::2 ip6-allrouters\nff02::3 ip6-allhosts\n0.0.0.0 0.0.0.0\n\n# Start of entries generated by download_stripped_hosts.py\n'
__LINE_PREFIX = '0.0.0.0 '
__BACKUP_DIR = 'backups/'
__BACKUP_EXT = '.txt'
__OUTPUT_DIR = 'compiled'
__OUTPUT_FILE = 'hosts'
__GLOBAL_WHITELIST = dict()

# Quick funct to write backup file string and minimize code with reuse
def build_backup_file_str(raw_url):
	file_str = __BACKUP_DIR

	url = "" + raw_url
	if url.startswith("http://"):
		url = url.replace("http://", "")
	if url.startswith("https://"):
		url = url.replace("https://", "")
	url = url.replace("/", "_")
	url = url.replace(".", "")
	file_str += url

	return file_str + __BACKUP_EXT

# Try downloading hosts, or if failed then read from backup
def download_hosts(source_url):
	hl = list()

	try:
		# Try downloading new data
		response = urlopen(source_url)
		raw = response.read()
		text = raw.decode('utf-8')
	except HTTPError | URLError:
		# Downloading new data failed ):
		print('Unable to download hosts from %s. Retrieving saved backup...' % source_url)
		file_str = build_backup_file_str(source_url)

		if not os.path.exists(file_str):
			print('There is no saved backup for %s!' % source_url)
			return

		f = open(file_str, 'r')
		text = f.read()

	for line in text.split('\n'):
		hl.append(line)

	return hl

def backup_to_file(file_str, hosts):
	print("  [backing up %s with %i entries]" % (file_str, len(hosts)))
	f = open(file_str, 'w')
	for host in hosts:
		f.write(host + '\n')
	f.close()

def process_host(host):
	# Skip unusable lines
	if not host:
		return

	# Strips any whitespace
	host = host.strip()
	# Strips initial pipe symbols
	host = host.replace('|', '')
	# Strips initial '0.0.0.0 ' / '127.0.0.1 ' from host files
	host = host.replace('0.0.0.0 ', '')
	host = host.replace('127.0.0.1 ', '')

	if '#' in host:
	# Skips comment lines and lines blocking specific CSS items
		if host.startswith('#') or '##' in host:
			return
		else:
			host = host.split('#')[0] # Removes excess comment strings located after host

	if '^' in host:
		if host.endswith('^third-party'):
			host = host.replace('^third-party', '')
		elif host.endswith('^$important'):
			host = host.replace('^$important', '')
		else:
			if host.endswith('^'):
				host = host.replace('^', '')
			else:
				return

	if '$' in host:
		return
	if '!' in host:
		return
	if ':' in host:
		return
	if '@' in host:
		return
	if '*' in host:
		return
	if '?' in host:
		return
	if '=' in host:
		return
	if '[' in host:
		return
	if ']' in host:
		return
	if ',' in host:
		return
	if '/' in host:
		return
	if '(' in host:
		return
	if ')' in host:
		return
	if ';' in host:
		return
	if '%' in host:
		return
	if '{' in host:
		return
	if '{' in host:
		return

	# Skips final unusables
	if host.startswith('.') or host.endswith('.'):
		return

	# Adds the host to a dictionary which serves as the value to a parent dictionary (passed in the method argument), with the registered domain as the key
	ext = tldextract.extract(host)
	base_domain = ext.registered_domain
	if base_domain == '' or base_domain == '\n' or base_domain == ' ':
		return

	if host in __GLOBAL_WHITELIST:
		return

	return host

def run(bl_list, wl_list):
	# Ensures required directories exist
	if not os.path.isdir(__BACKUP_DIR):
		os.mkdir(__BACKUP_DIR)
	if not os.path.isdir(__OUTPUT_DIR):
		os.mkdir(__OUTPUT_DIR)

	print('Downloading blacklists...')
	blacklist = list()
	for url in bl_list:
		print('--> %s' % url)
		hosts = download_hosts(url)
		blacklist.extend(hosts)
		backup_to_file( build_backup_file_str(url) , hosts)

	print('Downloading whitelists...')
	for url in wl_list:
		print('--> %s' % url)
		hosts = download_hosts(url)
		for host in hosts:
			__GLOBAL_WHITELIST[host] = __GLOBAL_WHITELIST.get(host, 0) + 1
		backup_to_file( build_backup_file_str(url) , hosts)

	# TODO: keep multithreading library updated, and move to using safe dictionary for data storage instead of
	# current safe list
	print('Multithreaded hosts processing...')
	mt = tmd.MultiThreader()
	mt.add_data(blacklist)
	mt.set_function(process_host)
	mt.run()

	print('Sorting processed data...')
	compiled_hosts = dict()
	for host in mt.get_processed_data():
		if host:
			compiled_hosts[host] = compiled_hosts.get(host, 0) + 1
	file_str = __OUTPUT_DIR + '/' + __OUTPUT_FILE

	print('Writing processed data to file...')
	count = 0
	f = open(file_str, 'w')
	f.write(__HOSTS_HEADER)
	for host in compiled_hosts.keys():
		f.write(__LINE_PREFIX + host + '\n')
		count += 1
	f.close()

	print('Compiled %d hosts.' % count)
