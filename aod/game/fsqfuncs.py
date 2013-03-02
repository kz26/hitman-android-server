from foursquare import Foursquare
from django.conf import settings

client = Foursquare(client_id=settings.FOURSQUARE_CLIENT_ID, client_secret=settings.FOURSQUARE_CLIENT_SECRET)

def get_nearest_location(latitude, longitude):
    results = client.venues.search(params={"ll": "%s,%s" % (latitude, longitude)})
    if results['venues']:
        return results['venues'][0]['name']
    else:
        return None
