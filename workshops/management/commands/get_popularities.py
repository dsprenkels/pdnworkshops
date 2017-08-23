from django.core.management.base import BaseCommand

from workshops.models import Workshop, User, WorkshopRating

class Command(BaseCommand):
    help = 'Get workshop populatities'

    def handle(self, *args, **options):
        # check the app for problems
        self.check(['workshops'])

        # load workshops
        workshops = dict()
        for ws in Workshop.objects.filter():
        	workshops[ws.naam] = {'users': 0, 'popularity': 0}

        # load users
        users = list()
        db_users = []
        for user in User.objects.filter(deleted=False):
            db_users.append(user.id)
            users.append(user.naam)

        # load user preferences
        prefs = dict()
        for rating in WorkshopRating.objects.filter(user__in=db_users, rating__gte=4):
            workshops[rating.workshop.naam]['popularity'] += rating.rating
            workshops[rating.workshop.naam]['users'] += 1

        print "Populariteiten:"
        for workshop, rating in sorted(workshops.items(), key=lambda x: x[1]['popularity'], reverse=True):
            print "%s: %d (%d)" % (workshop, rating['popularity'], rating['users'])
