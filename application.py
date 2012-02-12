# -*- coding: utf-8 -*
#
# ePoint WebShop
# Copyright (C) 2010 - 2012 ePoint Systems Ltd
# Author: Andrey Martyanov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

import os.path
import sys

sys.stdout = sys.stderr

import cherrypy

from mailreceipt.templates import *
from mailreceipt import settings
from mailreceipt.i18n import translate as _
from webshop.http import urlfetch
from webshop.document import DocumentSource, Document
from webshop.mail import Mailer, MailerException
from webshop.message import TextMessage, MIMESignedMessage, MIMEEncryptedMessage
from webshop.gpg import GPG
from webshop.pgp import make_document
from webshop import settings as ws_settings


class MailReceiptApp(object):
    def _render_error_page(self, title, details):
        page = [render_header()]
        page.append(render_message(title, details))
        page.append(render_footer())
        return page
    
    @cherrypy.expose
    def index(self, email=None, pgp=None, mime=None, sn=None, **params):
        cherrypy.response.headers['Content-Type'] = "text/html"
        page = [render_header()]
        if cherrypy.request.method == 'POST':
            # TODO: check email for validity
            if email is None or email == '':
                return self._render_error_page(_('Missing parameter'),
                                               _('Email parameter is mandatory.'))
            # TODO: check serial number for validity
            if sn is None or sn == '':
                return self._render_error_page(_('Missing parameter'),
                                               _('Certificate serial number parameter is mandatory.'))
            document_source = DocumentSource(settings.ISSUER, sn=sn)
            document = Document(document_source)
            verified = document.verify()
            # document.verify() returns False if verification failed
            # and None upon another error
            if verified != False:
                _id = document.get_id()
                if mime:
                    signature = document.get_signature()
                    body = document.get_body()
                    message = MIMESignedMessage(settings.SMTP_USERNAME,
                                                email,
                                                render_subject(_id),
                                                body,
                                                signature)
                else:
                    if not pgp:
                        body = document.get_raw_data()
                        message = TextMessage(settings.SMTP_USERNAME,
                                              email,
                                              render_subject(_id),
                                              body)
                if pgp:
                    gnupg = GPG(gnupghome=ws_settings.GNUPG_HOME)
                    received = gnupg.receive_keys(pgp, always_trust=True)
                    if received:
                        if mime:
                            encrypted = gnupg.encrypt(message.as_string(),
                                                      pgp,
                                                      always_trust=True)
                            if encrypted:        
                                message = MIMEEncryptedMessage(settings.SMTP_USERNAME,
                                                               email,
                                                               render_subject(_id),
                                                               str(encrypted))
                            else:
                                return self._render_error_page(
                                    _('Something went wrong'),
                                    _('Encryption problem. Sorry for the inconvenience!'))
                        else:
                            message = make_document(document.get_raw_data())
                            encrypted = gnupg.encrypt(message,
                                                      pgp,
                                                      always_trust=True,
                                                      no_literal=True)
                            if encrypted:
                                message = TextMessage(settings.SMTP_USERNAME,
                                                      email,
                                                      render_subject(_id),
                                                      str(encrypted))
                            else:
                                return self._render_error_page(
                                    _('Something went wrong'),
                                    _('Encryption problem. Sorry for the inconvenience!'))
                    else:
                        return self._render_error_page(
                            _('Something went wrong'),
                            _('Can not receive key. Sorry for the inconvenience!'))
                
                m = Mailer(suppress_exceptions=False)
                try:
                    m.send(message)
                except MailerException:
                    return self._render_error_page(_('Something went wrong'),
                                                   _('Please try again later. Sorry for the inconvenience!'))
                page.append(render_message(_('Request was completed successfully'),
                                           _('Your receipt will be emailed shortly. Thank you for your patience!')))
            else:
                return self._render_error_page(_('Something went wrong'),
                                               _('Please try again later. Sorry for the inconvenience!'))
        else:
            page.append(render_message(_('Malformed request'),
                                       _('You should use POST request with Content-Type: application/x-www-form-urlencoded and appropriate parameters list.')))
        page.append(render_footer())
        return page

def run():
    # Cherrypy configuration settings
    application_conf = {
        'environment': 'embedded',
    }

    debug = True if settings.DEBUG == 'true' else False
    if debug:
        application_conf['request.show_tracebacks'] = True

    # Update CherryPy configuration
    cherrypy.config.update(application_conf)

    # Create an instance of the application
    mail_receipt_app = MailReceiptApp()

    return cherrypy.Application(mail_receipt_app, script_name=None, config=None)
