from utils import LogHelper, LinkedinHelper, NetworkHelper

class ProfilesFinder(object):


	SITE_URL = 'https://www.linkedin.com'
	PROFILE_URL = 'https://www.linkedin.com/profile/view?id='
	SEARCH_URL = 'https://www.linkedin.com/search'
	SEARCH_URL_NORMAL = 'https://www.linkedin.com/search/results/people/?keywords='
	SEARCH_URL_PAGE_NUMBER_NORMAL = '&page_num='
	SEARCH_PEOPLE_URL_NORMAL = '/keywords_users?ref=top_filter'
	SEARCH_WORK_STRING_NORMAL = 'People who work at '
	USER_CONTAINER_PATH_NORMAL = '#results'
	USER_LIST_CONTAINER_PATH_NORMAL = '#results li.result'
	USER_NAME_PATH_NORMAL = 'div > h3 > a'
	USER_POSITION_PATH_NORMAL = 'div > dl.snippet > dd > p'
	USER_LOCATION_PATH_NORMAL = 'div > dl.demographic'
	USER_COMMON_PATH_NORMAL = 'div > div.related-wrapper.collapsed > ul > li.shared-conn > a'
	USER_CONTACT_LEVEL = '.degree-icon'
	USER_DESCRIPTION_PATH_NORMAL = 'div > div.description'
	USER_IMAGE_PATH_NORMAL = 'a img'
	USER_URL_PATH_NORMAL = 'a'
	USER_FRIENDLY_URL_PATH_NORMAL = '.view-public-profile'

	sel = None

	def __init__(self, params=None):
		self.sel = LinkedinHelper.get_logged_in_driver(params)

	def run(self, params, callback=None, batch=False):
		params['from_page'] = int(params['from_page']) if 'from_page' in params else 1
		params['to_page'] = int(params['to_page']) if 'to_page' in params else 1
		params['url'] = self.get_url(params)
		params['to_page'] += 1
		profiles = []
		for numPage in range(params['from_page'], params['to_page']):
			params['num_page'] = numPage
			results = self.extract_page(params, callback)
			if results:
				profiles.append(results)
			else:
				break
		return profiles

	def extract_page(self, params, callback=None):
		exit = False
		url = params['url']
		# curUrl = url + '&page_num=' + str(params['num_page'])
		curUrl = url
		self.sel.loadPage(curUrl)
		container = self.sel.waitShowElement(self.USER_CONTAINER_PATH_NORMAL)
		containers = self.sel.getElements(self.USER_LIST_CONTAINER_PATH_NORMAL)
		profiles = []
		for element in containers:
			userData = {
				'userdata': '',
				'userId': '',
				'extractedLogged': False,
				'extractedPublic': False,
				'firstMessageSent': False,
				'channel': '',
				'conversationId': ''
			}
			username = self.sel.getElementFromValue(element, self.USER_NAME_PATH_NORMAL)
			if username and username != 'LinkedIn Member':
				exit = True
				userData['name'] = username
				userData['position'] = self.sel.getElementFromValue(element, self.USER_POSITION_PATH_NORMAL)
				userData['description'] = self.sel.getElementFromValue(element, self.USER_DESCRIPTION_PATH_NORMAL)
				userData['image'] = self.sel.getElementFromAttribute(element, self.USER_IMAGE_PATH_NORMAL, 'src')
				userData['location'] = self.sel.getElementFromValue(element, self.USER_LOCATION_PATH_NORMAL)
				userData['common'] = self.sel.getElementFromValue(element, self.USER_COMMON_PATH_NORMAL)
				userData['level'] = self.sel.getElementFromValue(element, self.USER_CONTACT_LEVEL)
				userData['friend'] = True if userData['level'] == '1st' else False
				userData['status'] = 'FRIEND' if userData['friend'] else 'FOUND'
				tmpUrl = self.sel.getElementFromAttribute(element, self.USER_URL_PATH_NORMAL, 'href')
				arrUrl = tmpUrl.split('&')
				varUrl = arrUrl[0]
				userData['url'] = varUrl
				arrId = varUrl.split('id=')
				varId = arrId[1]
				userData['id'] = varId
				userData['keywords'] = params['expertise']
				userData['where'] = params['location']
				userData['email'] = params['email']
				userData['status'] = 'FOUND'
				profiles.append(userData)
				if callback:
					callback(userData)
		self.sel.close()
		return profiles

	def get_url(self, params):
		expertise = params['expertise'].split(',')[0]
		location = params['location'].split(',')[0]
		args = {
			'keywords': expertise
		}
		extra = '&' + NetworkHelper.dict_to_querystring(args)
		url = self.SEARCH_URL
		return url

	def batch(self):
		pass