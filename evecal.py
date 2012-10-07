from datetime import datetime, timedelta
from logging import getLogger
from HTMLParser import HTMLParser
from icalendar import Calendar, Event
from eveapi import EVEAPIConnection, Error

api = EVEAPIConnection()


def mask_check(accessmask, bit):
    """Returns a bool indicating if the bit is set in the accessmask"""
    mask = 1 << bit
    return (accessmask & mask) > 0


class EVEEvent(Event):
    """Represents a EVE Event, a subclassed iCal event"""

    @staticmethod
    def from_eveapi(tree):
        event = EVEEvent()
        h = HTMLParser()

        startdate = datetime.fromtimestamp(tree.eventDate)
        if tree.duration > 0:
            enddate = startdate + timedelta(minutes=tree.duration)
        else:
            enddate = None

        event['uid'] = '%s@api.eveonline.com' % tree.eventID
        event.add('summary', tree.eventTitle)
        event.add('description', h.unescape(tree.eventText))
        event.add('dtstart', startdate)
        if enddate:
            event.add('dtend', enddate)
        if tree.duration > 0:
            event.add('duration', timedelta(minutes=tree.duration))
        event.add('organiser', tree.ownerName)

        return event


class EVECal(Calendar):
    """Represents a EVE Calendar from the API"""

    _auth = None
    _calendar = None
    log = getLogger(__name__)

    def __init__(self, keyID, vCode, characterID, **kwargs):
        super(EVECal, self).__init__(self, **kwargs)
        self.add('prodid', '-//EVECalICS//')
        self.add('version', '2.0')
        self._auth = api.auth(keyID=keyID, vCode=vCode)
        self._characterID = characterID

    def _check_access(self):
        """Checks if the provided API key has access to the calendar"""

        if self._auth:
            try:
                doc = self._auth.account.ApiKeyInfo()
            except Error as e:
                self.log.error('Error checking API Key: %s' % e)
                pass
            else:
                return mask_check(doc.key.accessMask, 20)
        return False

    def _generate_calendar(self):

        if not self._check_access():
            self.log.error('Key does not have access to UpcomingCalendarEvents')
            return False

        try:
            doc = self._auth.char.UpcomingCalendarEvents(characterID=self._characterID)
        except Error as e:
            self.log('Error retreiving UpcomingCalendarEvents: %s' % e)
            return False

        for event in doc.upcomingEvents:
            self.add_component(EVEEvent.from_eveapi(event))

    def as_string(self):
        if not len(self.subcomponents):
            self._generate_calendar()
        return super(EVECal, self).as_string()        
