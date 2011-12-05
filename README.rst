=============
python-smsapi
=============

Python client library for SMSAPI.pl.

Currently allows:

* Address Book manipulation - adding, listing and deleting numbers and groups
* SMS sending

Author
------

* Grzegorz Biały (https://github.com/grzegorzbialy/)
* ELCODO (http://elcodo.pl)

Install
-------
You can do one of the following:

* python setup.py install
* copy sms to anywhere to your PYTHONPATH (e.g. your project directory)

Requirements
------------

* Python 2.5+
* suds SOAP client library (https://fedorahosted.org/suds/)

Usage
-----

*Init and get points (credits) quantity*::

    from smsapi import SmsApi, SmsApiAddressBook
    import logging

    logging.basicConfig(level=logging.INFO)
    logging.getLogger('suds.client').setLevel(logging.DEBUG)

    username = "<USERNAME>"
    password = "<PASSWORD>"

    sms = SmsApi(username, password)
    ab = SmsApiAddressBook(username, password)

    print "You have %s points left" % sms.get_points()

*Address Book*::

    # add group called "Test Group"
    group_id = ab.add_group(u"Test Group")

    # add test number
    number = ab.add_number(u"48123456789", u"Test Number", group_id)

    # get all groups and assign numbers to it
    groups_and_numbers = {}
    groups = ab.get_groups()
    for g in groups:
        groups_and_numbers[g['name']] = ab.get_numbers(g['id'])

    # print groups_and_numbers
    # expected result:
    # {u'Test Group': [{'group_id': <X>, 'name': Test Number, 'number': 48123456789}]}

*SMS sending*::

    # Send SMS message to +48123456789 - fill sender field "SENDER" and message with "MESSAGE"
    sms = sms.send_sms("48123456789", "SENDER", "MESSAGE", eco=False)

    # print sms
    # expected result:
    # {'cost': '0.1650', 'sms_id': <X>}

License
-------
OSI - The BSD License (http://www.opensource.org/licenses/bsd-license.php)


Copyright (c) 2010, Grzegorz Bialy, ELCODO.pl
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
* Neither the name of the author nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS "AS IS" AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.