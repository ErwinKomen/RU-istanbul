"""Models for the BASIC app.

"""
from django.db import models, transaction
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.db.models.functions import Lower
from django.db.models.query import QuerySet 
from django.urls import reverse
from django.utils import timezone
from django.utils.html import mark_safe
from markdown import markdown

import json
import pytz
import lxml
import lxml.html

# From own stuff
from istanbul.settings import TIME_ZONE
from .utils import ErrHandle

LONG_STRING=255
MAX_TEXT_LEN = 200

# =================== HELPER functions ================================

def get_current_datetime():
    """Get the current time"""
    return timezone.now()

def adapt_markdown(val, lowercase=False):
    """Call markdown, but perform some actions to make it a bit safer"""

    sBack = ""
    oErr = ErrHandle()
    try:
        if val != None:
            val = val.replace("***", "\*\*\*")
            sBack = mark_safe(markdown(val, safe_mode='escape', extensions=['tables']))
            sBack = sBack.replace("<p>", "")
            sBack = sBack.replace("</p>", "")
            if lowercase:
                sBack = sBack.lower()
            #print(sBack)
    except:
        msg = oErr.get_error_message()
        oErr.DoError("adapt_markdown")
    return sBack

def get_crpp_date(dtThis, readable=False):
    """Convert datetime to string"""

    if readable:
        # Convert the computer-stored timezone...
        dtThis = dtThis.astimezone(pytz.timezone(TIME_ZONE))
        # Model: yyyy-MM-dd'T'HH:mm:ss
        sDate = dtThis.strftime("%d/%B/%Y (%H:%M)")
    else:
        # Model: yyyy-MM-dd'T'HH:mm:ss
        sDate = dtThis.strftime("%Y-%m-%dT%H:%M:%S")
    return sDate

def striphtml(data):
    """"""

    sBack = data
    if not data is None and data != "":
        xml = lxml.html.document_fromstring(data)
        if not xml is None:
            sBack = xml.text_content()
    return sBack


# =================== HELPER classes ==================================

class Custom():
    """Just adding some functions"""

    def custom_getkv(self, item, **kwargs):
        """Get key and value from the manuitem entry"""

        oErr = ErrHandle()
        key = ""
        value = ""
        try:
            keyfield = kwargs.get("keyfield", "name")
            if keyfield == "path" and item['type'] == "fk_id":
                key = "{}_id".format(key)
            key = item[keyfield]
            if self != None:
                if item['type'] == 'field':
                    value = getattr(self, item['path'])
                elif item['type'] == "fk":
                    fk_obj = getattr(self, item['path'])
                    if fk_obj != None:
                        value = getattr( fk_obj, item['fkfield'])
                elif item['type'] == "fk_id":
                    # On purpose: do not allow downloading the actual ID of a foreign ky - id's migh change
                    pass
                    #fk_obj = getattr(self, item['path'])
                    #if fk_obj != None:
                    #    value = getattr( fk_obj, "id")
                elif item['type'] == 'func':
                    value = self.custom_get(item['path'], kwargs=kwargs)
                    # return either as string or as object
                    if keyfield == "name":
                        # Adaptation for empty lists
                        if value == "[]": value = ""
                    else:
                        if value == "": 
                            value = None
                        elif value[0] == '[':
                            value = json.loads(value)
        except:
            msg = oErr.get_error_message()
            oErr.DoError("Custom/custom_getkv")
        return key, value


# Create your models here.
class UserSearch(models.Model):
    """User's searches"""
    
    # [1] The listview where this search is being used
    view = models.CharField("Listview", max_length = LONG_STRING)
    # [1] The parameters used for this search
    params = models.TextField("Parameters", default="[]")    
    # [1] The number of times this search has been done
    count = models.IntegerField("Count", default=0)
    # [1] The usage history
    history = models.TextField("History", default="{}")    
    
    class Meta:
        verbose_name = "User search"
        verbose_name_plural = "User searches"

    def add_search(view, param_list, username):
        """Add or adapt search query based on the listview"""

        oErr = ErrHandle()
        obj = None
        try:
            # DOuble check
            if len(param_list) == 0:
                return obj

            params = json.dumps(sorted(param_list))
            if view[-1] == "/":
                view = view[:-1]
            history = {}
            obj = UserSearch.objects.filter(view=view, params=params).first()
            if obj == None:
                history['count'] = 1
                history['users'] = [dict(username=username, count=1)]
                obj = UserSearch.objects.create(view=view, params=params, history=json.dumps(history), count=1)
            else:
                # Get the current count
                count = obj.count
                # Adapt it
                count += 1
                obj.count = count
                # Get and adapt the history
                history = json.loads(obj.history)
                history['count'] = count
                # Make sure there are users
                if not 'users' in history:
                    history['users'] = []
                    oErr.Status("Usersearch/add_search: added 'users' to history: {}".format(json.dumps(history)))
                bFound = False
                for oUser in history['users']:
                    if oUser['username'] == username:
                        # This is the count for a particular user
                        oUser['count'] += 1
                        bFound = True
                        break
                if not bFound:
                    history['users'].append(dict(username=username, count=1))
                obj.history = json.dumps(history)
                obj.save()

        except:
            msg = oErr.get_error_message()
            oErr.DoError("UserSearch/add_search")
        # Return what we found
        return obj

    def load_parameters(search_id, qd):
        """Retrieve the parameters for the search with the indicated id"""

        oErr = ErrHandle()
        try:
            obj = UserSearch.objects.filter(id=search_id).first()
            if obj != None:
                param_list = json.loads(obj.params)
                for param_str in param_list:
                    arParam = param_str.split("=")
                    if len(arParam) == 2:
                        k = arParam[0]
                        v = arParam[1]
                        qd[k] = v
        except:
            msg = oErr.get_error_message()
            oErr.DoError("UserSearch/load_parameters")
        # Return what we found
        return qd


class Address(models.Model):
    """IP addresses that have been blocked"""

    # [1] The IP address itself
    ip = models.CharField("IP address", max_length = MAX_TEXT_LEN)
    # [1] The reason for blocking
    reason = models.TextField("Reason")

    # [0-1] The date when blocked
    created = models.DateTimeField(default=get_current_datetime)

    # [0-1] The path that the user has used
    path = models.TextField("Path", null=True, blank=True)

    # [0-1] The whole body of the request
    body = models.TextField("Body", null=True, blank=True)

    def __str__(self):
        sBack = self.ip
        return sBack

    def add_address(ip, request, reason):
        """Add an IP to the blocked ones"""

        bResult = True
        oErr = ErrHandle()
        try:
            if ip != "127.0.0.1":
                # Check if it is on there already
                obj = Address.objects.filter(ip=ip).first()
                if obj is None:
                    # It is not on there, so continue
                    path = request.path
                    get = request.POST if request.POST else request.GET
                    body = json.dumps(get)
                    obj = Address.objects.create(ip=ip, path=path, body=body, reason=reason)

        except:
            msg = oErr.get_error_message()
            oErr.DoError("Address/add_address")
            bResult = False

        return bResult

    def is_blocked(ip, request):
        """Check if an IP address is blocked or not"""

        bResult = False
        oErr = ErrHandle()
        look_for = [
            ".php", "%3dphp", "win.ini", "/passwd", ".env", "config.ini", ".local", ".zip", "jasperserver"
            ]
        try:
            # Check if it is on there already
            obj = Address.objects.filter(ip=ip).first()
            if obj is None:
                # Double check
                path = request.path.lower()
                if path != "/":
                    # We need to look further
                    for item in look_for:
                        if item in path:
                            # Block it
                            Address.add_address(ip, request, item)
                            bResult = True
                            break
            else:
                # It is already blocked
                bResult = True
        except:
            msg = oErr.get_error_message()
            oErr.DoError("Address/is_blocked")

        return bResult


# =================== Some kind of CMS ===============================


class Cpage(models.Model):
    """A HTML page on which the CMS works"""

    # [1] obligatory name of the page this content element pertains to
    name = models.CharField("Name", max_length=LONG_STRING)

    # [0-1] The name of the page as it occurs in 'urls.py'
    urlname = models.CharField("Name in urls", null=True, blank=True, max_length=LONG_STRING)

    # [1] And a date: the date of saving this manuscript
    created = models.DateTimeField(default=get_current_datetime)
    saved = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        sBack = self.name
        return sBack

    def get_count_locations(self):
        """Get the number of locations attached to this Cpage"""

        count = self.page_locations.count()
        return count

    def get_created(self):
        sCreated = get_crpp_date(self.created, True)
        return sCreated

    def get_saved(self):
        if self.saved is None:
            self.saved = self.created
            self.save()
        sSaved = get_crpp_date(self.saved, True)
        return sSaved

    def get_urlname(self, html=False):
        sBack = "-"
        if not self.urlname is None and self.urlname != "":
            sBack = self.urlname
            if html:
                try:
                    url = reverse(sBack)
                except:
                    url = None
                if url is None:
                    sBack = "<span class='badge signature cl'>{}</span>".format(sBack)
                else:
                    sBack = "<a href='{}'><span class='badge signature cl'>{}</span></a>".format(url, sBack)
        return sBack

    def save(self, force_insert = False, force_update = False, using = None, update_fields = None):

        oErr = ErrHandle()
        try:
            # Adapt the save date
            self.saved = get_current_datetime()
            response = super(Cpage, self).save(force_insert, force_update, using, update_fields)

        except:
            msg = oErr.get_error_message()
            oErr.DoError("Cpage.save")
            response = None

        # Return the response when saving
        return response


class Clocation(models.Model):
    """The location of a content-item on a HTML page"""

    # [1] Name of the location as a descriptive string
    name = models.TextField("Name")
    # [1] obligatory htmlid on the page
    htmlid = models.CharField("Htmlid", blank=True, null=True, max_length=LONG_STRING)

    # [1] Link to the page on which this location holds
    page = models.ForeignKey(Cpage, on_delete=models.CASCADE, related_name="page_locations")

    # [1] And a date: the date of saving this manuscript
    created = models.DateTimeField(default=get_current_datetime)
    saved = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        sBack = "-"
        if not self.page is None:
            sBack = "{}: {}".format(self.page.name, self.name)
        return sBack

    def get_created(self):
        sCreated = get_crpp_date(self.created, True)
        return sCreated

    def get_saved(self):
        if self.saved is None:
            self.saved = self.created
            self.save()
        sSaved = get_crpp_date(self.saved, True)
        return sSaved

    def save(self, force_insert = False, force_update = False, using = None, update_fields = None):

        oErr = ErrHandle()
        try:
            # Adapt the save date
            self.saved = get_current_datetime()
            response = super(Clocation, self).save(force_insert, force_update, using, update_fields)

        except:
            msg = oErr.get_error_message()
            oErr.DoError("Clocation.save")
            response = None

        # Return the response when saving
        return response
    

class Citem(models.Model):
    """A mini variant of a content management system"""

    # [1] Obligatory location of this content item
    clocation = models.ForeignKey(Clocation, on_delete=models.CASCADE, related_name="location_items")

    # [0-1] the markdown contents for the information
    contents = models.TextField("Contents", null=True, blank=True)

    # [0-1] the markdown contents for the ORIGINAL information
    original = models.TextField("Original", null=True, blank=True)

    # [1] Every manuscript has a status - this is *NOT* related to model 'Status'
    stype = models.CharField("Status", choices=build_abbr_list(STATUS_TYPE), max_length=5, default="man")
    # [0-1] Status note
    snote = models.TextField("Status note(s)", default="[]")

    # [1] And a date: the date of saving this manuscript
    created = models.DateTimeField(default=get_current_datetime)
    saved = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        sBack = "-"
        if not self.clocation is None:
            sBack = "{}: {}".format(self.clocation.page.name, self.clocation.name)
        return sBack

    def get_contents(self):
        sBack = "-"
        oErr = ErrHandle()
        try:
            if not self.contents is None:
                sBack = striphtml(self.contents)
        except:
            msg = oErr.get_error_message()
            oErr.DoError("Citem/get_contents")
        return sBack

    def get_contents_markdown(self, stripped=False, retain=False):
        sBack = "-"
        oErr = ErrHandle()
        try:
            # sBack = self.get_contents()
            sBack = "-"
            if stripped:
                if not self.contents is None:
                    sBack = self.contents
                sBack = striphtml(markdown(sBack, safe_mode='escape', extensions=['tables']))
            else:
                sBack = self.get_contents()
                sBack = adapt_markdown(sBack)
                if retain:
                    sBack = sBack.replace("<a ", "<a class='retain' ")
        except:
            msg = oErr.get_error_message()
            oErr.DoError("Citem/get_contents_markdown")
        return sBack

    def get_created(self):
        sCreated = get_crpp_date(self.created, True)
        return sCreated

    def get_htmlid(self):
        """Get the location HTML id"""

        sBack = "-"
        if not self.clocation is None:
            sBack = self.clocation.get_htmlid()
        return sBack

    def get_location(self, bHtml=False):
        """Get the location name"""

        sBack = "-"
        if not self.clocation is None:
            sBack = self.clocation.get_location()
            if bHtml:
                html = []
                url = reverse('clocation_details', kwargs={'pk': self.clocation.id})
                html.append("<span class='badge signature gr'><a href='{}'>{}</a></span>".format(url, sBack))
                sBack = "\n".join(html)
        return sBack

    def get_original(self):
        sBack = "-"
        oErr = ErrHandle()
        try:
            if not self.original is None:
                sBack = striphtml(self.original)
        except:
            msg = oErr.get_error_message()
            oErr.DoError("Citem/get_original")
        return sBack

    def get_original_markdown(self, stripped=False, retain=False):
        sBack = "-"
        oErr = ErrHandle()
        try:
            # sBack = self.get_original()
            sBack = "-"
            if stripped:
                if not self.original is None:
                    sBack = self.original
                sBack = striphtml(markdown(sBack, safe_mode='escape', extensions=['tables']))
            else:
                sBack = self.get_original()
                sBack = adapt_markdown(sBack)
                if retain:
                    sBack = sBack.replace("<a ", "<a class='retain' ")
        except:
            msg = oErr.get_error_message()
            oErr.DoError("Citem/get_original_markdown")
        return sBack

    def get_page(self):
        """Get the name of the page"""

        sBack = "-"
        if not self.clocation is None:
            sBack = self.clocation.get_page()
        return sBack

    def get_saved(self):
        if self.saved is None:
            self.saved = self.created
            self.save()
        sSaved = get_crpp_date(self.saved, True)
        return sSaved

    def save(self, force_insert = False, force_update = False, using = None, update_fields = None):

        oErr = ErrHandle()
        try:
            # Adapt the save date
            self.saved = get_current_datetime()
            response = super(Citem, self).save(force_insert, force_update, using, update_fields)

        except:
            msg = oErr.get_error_message()
            oErr.DoError("Citem.save")
            response = None

        # Return the response when saving
        return response

