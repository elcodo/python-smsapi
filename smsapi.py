#! /usr/bin/env python
#
# python-smsapi - Python bindings for the smsapi.pl HTTPS API
#
# Copyright (c) 2012, Grzegorz Bialy, ELCODO.pl
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the author nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import hashlib
import httplib
import json
import urllib
import time

try:
    from suds import WebFault
    from suds.client import Client
except:
    pass


__all__ = ['SmsApi']

VERSION = '0.2'

API_URL = "ssl.smsapi.pl"
WSDL_URL = "https://ssl.smsapi.pl/api/soap/v2/webservices?WSDL"


class SmsApiException(Exception):

    def __init__(self, message, args=[]):
        Exception.__init__(self, message)
        self.args = args

    def __unicode__(self):
        return u"%s" % self.message


class SmsApiBaseObject(object):

    def __init__(self, username, password):
        """Set username and password"""
        self.username = username
        self.password = hashlib.md5(password).hexdigest()

        try:
            self.soap_client = Client(WSDL_URL)
            self.soap_user = self._prepare_soap_user()
        except NameError:
            self.soap_client = None
            self.soap_user = None

    def _prepare_soap_user(self):
        """Prepare User object for SOAP authentication"""
        user = self.soap_client.factory.create('Client')
        user.username = self.username
        user.password = self.password
        return user

    def send_command(self, namespace, params={}):
        params['username'] = self.username
        params['password'] = self.password

        headers = {
            'User-Agent': 'python-smsapi v%s' % VERSION,
            'Accept': 'text/plain',
            'Content-type': 'application/x-www-form-urlencoded',
        }

        h = httplib.HTTPSConnection(API_URL)
        h.request(
            "POST",
            u"/%s.do" % namespace,
            urllib.urlencode(params),
            headers=headers,
        )
        response = h.getresponse()
        return response.read()

    def send_soap_command(self, command, args=[]):
        func = getattr(self.soap_client.service, command)

        try:
            response = func(*args)
        except WebFault, e:
            raise SmsApiException(e)

        if u"result" in response and response[u"result"] != 0:
            raise SmsApiException(response[u"description"])

        return response


class SmsApi(SmsApiBaseObject):

    def get_user(self, username):
        """Get account subuser details"""
        response = self.send_command(namespace="user", params={
            'get_user': username,
            'format': 'json',
        })
        try:
            data = json.loads(response)
            return {
                'username': data['username'],
                'limit': data['limit'],
                'month_limit': data['month_limit'],
                'allow_senders': True if data['senders'] == 1 else False,
                'allow_phonebook': True if data['phonebook'] == 1 else False,
                'is_active': True if data['active'] == 1 else False,
                'info': data['info'],
            }
        except ValueError:
            raise SmsApiException(response)

    def add_user(self, username, password, password_api=None, limit=None,
            month_limit=None, allow_senders=False, allow_phonebook=False,
            is_active=False, info=None):
        """Add account subuser"""
        params = {
            'add_user': username,
            'pass': hashlib.md5(password).hexdigest(),
        }
        if password_api:
            params['pass_api'] = hashlib.md5(password_api).md5()
        if limit:
            params['limit'] = limit
        if month_limit:
            params['month_limit']
        if allow_senders:
            params['senders'] = 1
        if allow_phonebook:
            params['phonebook'] = 1
        if is_active:
            params['active'] = 1
        if info:
            params['info'] = info

        response = self.send_command(namespace="user", params=params)
        if not response.startswith(u"OK"):
            raise SmsApiException(response)
        return True

    def edit_user(self, username, password=None, password_api=None, limit=None,
            month_limit=None, allow_senders=False, allow_phonebook=False,
            is_active=False, info=None):
        """Edit account subuser"""
        params = {
            'set_user': username,
        }
        if password:
            params['pass'] = hashlib.md5(password).hexdigest()
        if password_api:
            params['pass_api'] = hashlib.md5(password_api).md5()
        if limit:
            params['limit'] = limit
        if month_limit:
            params['month_limit']
        if allow_senders:
            params['senders'] = 1
        if allow_phonebook:
            params['phonebook'] = 1
        if is_active:
            params['active'] = 1
        if info:
            params['info'] = info

        response = self.send_command(namespace="user", params=params)
        if not response.startswith(u"OK"):
            raise SmsApiException(response)
        return True

    def get_points(self):
        """Get user points"""
        response = self.send_command(namespace="user", params={
            'credits': 1,
            'details': 1,
        })
        response = response.replace(u"Points: ", u"").split(u";")
        return {
            'points': float(response[0]),
            'pro': float(response[1]),
            'eco': float(response[2]),
            'mms': float(response[3]),
            'vms_gsm': float(response[4]),
            'vms_land': float(response[5]),
        }

    def get_senders(self):
        """Get sender (caller ID) list"""
        response = self.send_command(namespace="sender", params={
            'list': 1,
            'format': 'json',
        })
        try:
            return json.loads(response)
        except ValueError:
            raise SmsApiException(response)

    def get_sender_status(self, name):
        response = self.send_command(namespace="sender", params={
            'status': name,
            'format': 'json',
        })
        try:
            return json.loads(response)
        except ValueError:
            raise SmsApiException(response)

    def add_sender(self, name):
        response = self.send_command(namespace="sender", params={
            'add': name,
        })
        if response != u"OK":
            raise SmsApiException(response)
        return True

    def delete_sender(self, name):
        """Delete sender"""
        response = self.send_command(namespace="sender", params={
            'delete': name,
        })
        if not response.startswith(u"OK"):
            raise SmsApiException(response)
        return True

    def set_default_sender(self, name):
        """Set default sender to name"""
        response = self.send_command(namespace="sender", params={
            'default': name,
        })
        if response != "OK":
            raise SmsApiException(response)
        return True

    def send_sms(self, message, sender_name=None, recipient=None, group=None,
            flash=False, test=False, get_details=False, date=None,
            data_coding=False, idx=None, check_idx=False, eco=False,
            nounicode=False, normalize=False, fast=False, partner_id=None,
            max_parts=None, expiration_date=None):
        params = {
            'message': message.encode('utf-8'),
            'encoding': 'utf-8',
        }
        if sender_name:
            params['from'] = sender_name
        if recipient:
            params['to'] = recipient
        if group:
            params['group'] = group
        if flash:
            params['flash'] = 1
        if test:
            params['test'] = 1
        if get_details:
            params['details'] = 1
        if date:
            params['date_validate'] = 1  # Always perform date check
            params['date'] = time.mktime(date)
        if data_coding:
            params['datacoding'] = u"bin"
        if idx:
            params['idx'] = idx
        if check_idx:
            params['check_idx'] = 1
        if eco:
            params['eco'] = 1
        if nounicode:
            params['nounicode'] = 1
        if normalize:
            params['normalize'] = 1
        if fast:
            params['fast'] = 1
        if partner_id:
            params['partner_id'] = partner_id
        if max_parts and int(max_parts) <= 6:
            params['max_parts'] = max_parts
        if expiration_date:
            params['expiration_date'] = time.mktime(expiration_date)
        response = self.send_command(namespace="sms", params=params)
        if not response.startswith(u"OK"):
            raise SmsApiException(response)

        # Check if message was sent to multiple recipients and return list
        if u"," in recipient:
            data_list = response.split(u";")
            data = []
            for message in data_list:
                message = message.split(u":")
                data.append({
                    'id': message[1],
                    'cost': message[2],
                    'status': message[0],
                })
            return data

        data = response.split(u":")
        return [{
            'id': data[1],
            'cost': data[2],
            'status': data[0],
        }]

    def delete_scheduled_sms(self, id):
        """
        Delete scheduled SMS message.

        Returns True if message was deleted and False when ID doesn't exists.
        """
        response = self.send_command(namespace="sms", params={
            'sch_del': id,
        })
        if response != "OK":
            return False
        return True


class SmsApiAddressBook(SmsApiBaseObject):
    """Address Book contains numbers and groups of numbers"""

    def __init__(self, *args, **kwargs):
        super(SmsApiAddressBook, self).__init__(*args, **kwargs)

        if not self.soap_client:
            raise SmsApiException(u"Suds not installed. Cannot use SmsApiAddressBook.")

    def get_groups(self):
        """Return list of groups"""
        response = self.send_soap_command("get_groups", [
            self.username,
            self.password,
        ])
        if not "groups" in response:
            return None
        retlist = []
        for g in response['groups']:
            retlist.append({
                'id': int(g['id']),
                'name': unicode(g['name']),
                'description': unicode(g['info']),
                'number_count': int(g['num_count']),
            })
        return retlist

    def add_group(self, name, description=u""):
        """Add group. Return ID (int) if added, Exception otherwise"""
        response = self.send_soap_command("add_group", [self.soap_user, name, description])
        try:
            return response['group_id']
        except KeyError:
            pass
        raise SmsApiException("Couldn't add group")

    def delete_group(self, id):
        """Delete group by given id. Returns True if deleted or error dict"""
        response = self.send_soap_command("delete_group", [self.soap_user, int(id)])
        return {
            'code': response['result'],
            'description': response['description'],
        }

    def get_numbers(self, group_id=-1):
        """Return list of numbers"""
        response = self.send_soap_command("get_numbers", [self.soap_user, group_id])
        if "numbers" not in response:
            return []
        retlist = []
        for n in response["numbers"]:
            retlist.append({
                'name': n["name"],
                'number': n["number"],
                'group_id': n["group_id"],
            })
        return retlist

    def add_number(self, number, name, group_id=-1):
        """Add number"""
        num = self.soap_client.factory.create('Number')
        num.number = str(number)
        num.name = name
        num.group_id = group_id

        self.send_soap_command("add_number", [self.soap_user, num])
        return True

    def delete_number(self, number, group_id=-1):
        """Delete number"""
        self.send_soap_command("delete_number", [self.soap_user, number, group_id])
        return True
