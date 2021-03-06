from django.db import models

from cms.models import CMSPlugin

class MailchimpPlugin(CMSPlugin):
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name
