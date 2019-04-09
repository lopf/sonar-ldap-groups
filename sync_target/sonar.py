import requests
import sys
import json
import logging

class SonarGroups(object):
    
    def __init__(self, cfg):
        self.groups_search_path = "api/user_groups/search"
        self.group_create_path = "api/user_groups/create"
        self.group_delete_path = "api/user_groups/delete"
        self.url = cfg['sonar']['url']
        self.token = cfg['sonar']['token']
        self.keep_local_groups = cfg['sonar']['keep_local_groups']
        self.logger = logging.getLogger(__name__)

        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

    def delete_groups(self, groups):
        """ delete groups based on a list """
        
        for group in groups:
            if group not in self.keep_local_groups:
                self.logger.debug("delete Sonar group {}".format(group))
                self.__delete_group(group)
            else:
                self.logger.info("keeping local group {}".format(group))

    def __delete_group(self, name):
        """ create a group """
        full_url = self.url + "/" + self.group_delete_path
        sonar_group = 'name=' + name

        try:
            r = requests.post(full_url, headers=self.headers, params=sonar_group, auth=(self.token, ''))
        except requests.exceptions.RequestException as e:
            logger.error(e)
            sys.exit(1)
        if r.status_code == 204:
            self.logger.info("Sonar group {} deleted".format(name))
            pass
        elif r.status_code == 404:
            # what else to do if it doesn't exist
            self.logger.debug("Sonar group {} not found".format(name))
            pass
        else:
            raise Exception("tried to delete group '{}' " + 
                            "received status {} " +
                            "with error {}".format(name, r.status_code, r.text))

    def create_groups(self, groups):
        """ create groups based on a list """
        for group in groups:
            self.logger.debug("create Sonar group {}".format(group))
            self.__create_group(group)
    
    def __create_group(self, name):
        """ create a group """
        full_url = self.url + "/" + self.group_create_path
        sonar_group = 'name=' + name
        try:
            r = requests.post(full_url, headers=self.headers, params=sonar_group, auth=(self.token, ''))
        except requests.exceptions.RequestException as e:
            logger.error(e)
            sys.exit(1)
        
        if r.status_code == 200:
            self.logger.info("Sonar group {} created".format(name))
            pass
        elif r.status_code == 400 and 'already exists' in r.text:
            self.logger.debug("Sonar group {} already exists".format(name))
            # what else to do if it exists
            pass
        else:
            raise Exception("tried to create group '{}' " + 
                            "received status {} " +
                            "with error {}".format(name, r.status_code, r.text))
    
    def get_groups(self):
        """ get the full list of current sonar groups based on search """

        sonar_groups = []
        page_size = 50
        page = 1
        full_url = self.url + "/" + self.groups_search_path
        
            # because of paging, we might have to send multiple requests
        while True:
            query = 'q=&ps={}&p={}'.format(page_size, page)
            try:
                r = requests.get(full_url, headers=self.headers, params=query, auth=(self.token, ''))
            except requests.exceptions.RequestException as e:
                logger.error(e)
                sys.exit(1)
            r_json = r.json()
            for group in r_json['groups']:
                group_name = group['name']
                self.logger.debug("found Sonar group {}".format(group_name))
                sonar_groups.append(group_name)
            result_size = len(r_json['groups'])
            if result_size < page_size:
                break
            # we blättere the page
            page = page + 1

        self.logger.info("found a total of {} Sonar groups".format(len(sonar_groups)))
        return sonar_groups
