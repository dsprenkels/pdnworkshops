import os
import re

from django.core.management.base import BaseCommand

from workshops.models import Workshop, User, WorkshopRating

"""
Dit is een derde manier om aan een rooster te komen. We gebruiken
hier ook `geheeltallig lineair programmeren'. Deze versie is een
verbeterde versie van `calculate2.py`, geschreven door Bas Westerbaan.
"""

ROUNDS = ['1', '2']

MODEL = r'''
set rounds;

set users;

set workshops;

# in this math model we do not set slots

param max{workshops};
param min{workshops};

param profit{users,workshops};

# the schedule to be calculated
var x{users,workshops,rounds} binary;

maximize totalprofit:
    sum{i in users, j in workshops, r in rounds}
        profit[i,j]*x[i,j,r];


# Each participant should be assigned to a workshop exactly as
# there are number of rounds.
subject to users_constraint{i in users}:
card(rounds) <= sum{j in workshops, r in rounds} x[i,j,r] <= card(rounds);

# Each participant should be assigned exactly one workshop per round
subject to round_constraint{i in users, r in rounds}:
1 <= sum{j in workshops} x[i,j,r] <= 1;

# Each participant may do a workshop only once
subject to round_constraint2{i in users, j in workshops}:
sum{r in rounds} x[i,j,r] <= 1;

# The amount of participants for is limited per workshop
subject to workshops_max_constraint{j in workshops, r in rounds}:
sum{i in users} x[i,j,r] <= max[j];

# The amount of participants must be at least some amount per workshop
subject to workshops_min_constraint{j in workshops, r in rounds}:
sum{i in users} x[i,j,r] >= min[j];

solve;

display totalprofit;
'''.strip()

class Command(BaseCommand):
    can_import_settings = True

    @staticmethod
    def _prepare_name(s):
        return "'%s'" % re.sub("[^A-Za-z ]","", s)

    def handle(self, *args, **options):
        # load workshops
        workshops = dict()
        for ws in Workshop.objects.filter():
            # TODO: implement min
        	workshops["workshop%d" % ws.id] = {"min": 0, "max": ws.max}

        # load users
        users = list()
        db_users = []
        for user in User.objects.filter(deleted=False):
            db_users.append(user.id)
            users.append(self._prepare_name(user.naam))
        
        # load user preferences
        prefs = dict()
        for rating in WorkshopRating.objects.filter(user__in=db_users):
            prefs[self._prepare_name(rating.user.naam), 'workshop'
                            +str(rating.workshop_id)] = rating.rating

        with open('out.sol', 'w') as f:
            # write model section
            f.write("%s\n" % MODEL)

            # write data section
            f.write("data;\n")

            f.write("set rounds := %s;\n" % " ".join(ROUNDS))

            f.write("set users :=\n")
            f.write(" ".join(users))
            f.write(";\n")

            f.write("set workshops :=\n")
            f.write(" ".join(workshops))
            f.write(";\n")
            
            f.write("param : min max :=\n")
            for k, v in workshops.items():
                f.write("%s %d %d\n" % (k, v['min'], v['max']))
            f.write("\n;")

            f.write("param profit : ")
            f.write(' '.join(workshops))
            f.write(' :=\n')
            for u in users:
                f.write("%s " % u)
                for w in workshops:
                    f.write("%d " % prefs[u, w])
                f.write("\n")
            f.write("\n;");

