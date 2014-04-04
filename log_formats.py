import re
from urlparse import urlparse, parse_qs

def _get_url_components(the_url):
	u = urlparse(the_url)
	names = ['scheme', 'netloc', 'path', 'params', 'query', 'fragment']
	return {names[x]:u[x] for x in range(6)}

## weblogic_default

extract_rule = re.compile('(?P<ip>\d+\.\d+\.\d+\.\d+) - (?P<user>[^\s]+) \[(?P<date>[^\]]+)\] "(?P<request>[^"]+)" (?P<status>\d+) (?P<response_size>\d+)')
request_details = re.compile('(?P<req_type>GET|POST) (?P<full_url>[^\s]+) (?P<http_version>.*)')

#kept_tokens['req_params'] = ";".join( sorted( self.parse_qs(o.query).keys() ) )
def weblogic_default( the_line ):
	result = extract_rule.match(the_line).groupdict()
	result.update( request_details.match(result['request']).groupdict() )
	result.update( _get_url_components( result['full_url'] ) )
	return result

### errorlog_apache

extract_rule = re.compile( '\[(?P<date>[^\]]+)\]\s\[(?P<severity>[^\]]+)\](?P<log_message>.*)' )
def errorlog_apache( the_line ):
	return extract_rule.match(the_line).groupdict()

