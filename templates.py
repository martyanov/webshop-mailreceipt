# -*- coding: utf-8 -*
#
# ePoint WebShop
# Copyright (C) 2011 - 2012 ePoint Systems Ltd
# Author: Andrey Martyanov
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

from flaskext.babel import gettext as _

__all__ = ['render_header', 'render_footer', 'render_message', 'render_subject']

def render_header():
    return """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
    <html>

    <head>
      <title>%(title)s</title>
      <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
      <link rel="stylesheet" type="text/css" href="static/style.css">
      <link rel="icon" type="image/x-icon" href="static/epoint.ico">
    </head>

    <body>

      <div id="header">
      </div>
    """ % {'title': _('WebShop Mailreceipt')}


def render_footer():
    return """
      <div id="footer">
        <p>ePoint Systems Ltd.</p>
      </div>

    </body>

    </html>
    """

def render_message(title, details):
    return """
      <div class="content">
        <h1>%(title)s</h1>
        <p>%(details)s</p>
      </div>
    """ % {
        'title': title,
        'details': details
    }


def render_subject(cert_id):
    return "%(subject)s %(id)s" % {'subject': _('Payment receipt, reference:'),
                                   'id': cert_id}
