import json

import requests


class APIOperation:
    def __init__(self, ip, name='Default', port=7443, version='v4_0', user='admin', password='admin!234'):
        self.version = version
        self.name = name
        self.ip_addr = ip
        self.port = port
        self.user = user
        self.password = password
        self.cookies = None
        self.baseurl = 'https://%s:7443/api/public/%s/' % (self.ip_addr, self.version)
        self.json_headers = {'content-type': 'application/json'}
        self.last_request = None
        requests.packages.urllib3.disable_warnings()

    def __make_json_request(self, schema_postfix, request_type, payload=None, is_json=True):
        if request_type == 'post':
            r = requests.post(self.baseurl + schema_postfix, json.dumps(payload),
                              verify=False, headers=self.json_headers, cookies=self.cookies)
        elif request_type == 'get':
            r = requests.get(self.baseurl + schema_postfix, verify=False, cookies=self.cookies)

        elif request_type == 'delete':
            r = requests.delete(self.baseurl + schema_postfix,
                                verify=False, headers=self.json_headers, cookies=self.cookies)
        else:
            raise ValueError('No supported request type : %s' % request_type)

        self.last_request = r
        if request_type != 'delete':
            return r.json() if is_json is True else r

    def do_login(self):
        payload = {'username': self.user, 'password': self.password}
        r = self.__make_json_request('session', 'post', payload)
        self.cookies = self.last_request.cookies
        return r

    def do_create_zone(self, zone_name):
        payload = {'name': zone_name, 'description': 'Default Description',
                   'login' : {'apLoginName': 'admin', 'apLoginPassword': 'admin!234'}}
        r = self.__make_json_request('rkszones', 'post', payload)
        return r

    def do_create_identity_user(self, user_name):
        payload = {'firstName': user_name, 'lastName': user_name, 'isDisabled': 'NO', 'userName': user_name,'password': '!lab4man1','confirmPassword': '!lab4man1',
                   'confirmPassword': '!lab4man1','countryName': 'UNITED STATES','subscriberPackage': {'name' : 'Local User Package'},
                  }
        r = self.__make_json_request('identity/users', 'post', payload)
        return r

    def do_get_zones(self):
        r = self.__make_json_request('rkszones', 'get')
        return r

    def do_get_identity_users(self):
        r = self.__make_json_request('identity/users', 'get')
        print(r)
        return r

    def do_delete_zone(self, zone_id):
        r = self.__make_json_request('rkszones/%s' % zone_id, 'delete')
        # return r.json()

    def do_delete_identity_user(self, user_id):
        r = self.__make_json_request('identity/users/%s' % user_id, 'delete')
        # return r.json()

    def do_delete_all_zones(self):
        while True:
            zonelist = self.do_get_zones()['list']
            if zonelist.__len__() <= 1:
                break

            for zoneinfo in zonelist:
                print('Deleting %s(%s) ' % (zoneinfo['name'], zoneinfo['id']))
                self.do_delete_zone(zoneinfo['id'])

    def do_delete_all_identity_users(self):
        while True:
            userlist = self.do_get_identity_users()['list']
            if userlist.__len__() <= 1:
                break

            for userinfo in userlist:
                print('Deleting %s(%s) ' % (userinfo['userName'], userinfo['id']))
                self.do_delete_identity_user(userinfo['id'])

    def do_get_control_plane_list(self):
        r = self.__make_json_request('applications/controlplane', 'get')
        return r

    def do_get_logs(self, control_plane_id):
        r = self.__make_json_request('applications/download/%s' % control_plane_id, 'get', is_json=False)
        return r

    def do_get_snap_logs(self, control_plane_id):
        r = self.__make_json_request('applications/downloadsnap/%s' % control_plane_id, 'get', is_json=False)
        return r