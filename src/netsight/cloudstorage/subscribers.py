# -- The contents of this file is copyright (c) 2011 Netsight Internet     -- #
# -- Solutions Ltd. All rights reserved. Please see COPYRIGHT.txt and      -- #
# -- LICENCE.txt for further information.                                  -- #
"""
Event handlers
"""
import logging
from plone import api
from zope.component import queryAdapter
from ZPublisher.HTTPRequest import FileUpload

from .interfaces import ICloudStorage

logger = logging.getLogger('netsight.cloudstorage')


def content_saved(object, event):
    """
    When an object is saved check its fields to see if any can be uploaded to
    S3
    """
    adapter = queryAdapter(object, ICloudStorage)
    if adapter is None:
        return

    if not hasattr(object.REQUEST, 'form'):
        return

    # look for file upload items on the request
    for key, value in object.REQUEST.form.items():
        if isinstance(value, FileUpload):
            value.seek(0)
            if len(value.read()):
                logger.info(
                    'Found file fields on %s. Enqueing upload',
                    '/'.join(object.getPhysicalPath())
                )
                adapter.enqueue()
                return


def mark_uploaded(event):
    """
    Event handler for completion of uploads

    :param event: The event object
    :type event: :class:`UploadComplete`
    """
    context = event.context
    fieldname = event.fieldname
    adapter = ICloudStorage(context)
    logger.info('Celery says %s has been uploaded', fieldname)
    adapter.mark_as_cloud_available(fieldname)


def email_creator(event):
    """
    Event handler to email content creator when upload completes

    :param event: The event object
    :type event: :class:`UploadComplete`
    """
    context = event.context
    adapter = ICloudStorage(context)
    # Only send email once all fields have been uploaded
    # TODO: Configurable emails
    if not adapter.has_uploaded_all_fields():
        return

    portal = api.portal.get()
    creator = api.user.get(context.Creator())
    creator_email = creator.getProperty('email')
    subject = u'%s: Files for "%s" have been uploaded' % (
        portal.Title().decode('utf8', 'ignore'),
        context.Title().decode('utf8', 'ignore'),
    )
    body = """This is an automated email.

    File data for the following item has been successfully
    uploaded to secure cloud storage:

    %s (%s)
    %s
    """ % (
        context.Title(),
        context.Type(),
        context.absolute_url()
    )
    api.portal.send_email(
        recipient=creator_email,
        subject=subject,
        body=body,
    )
