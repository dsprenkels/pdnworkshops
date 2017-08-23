from collections import OrderedDict
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

DEFAULT_OUTPUT_FILE = 'model.sol'

MODEL = r'''
# vim: set ft=ampl:

# This model calculates the optimal distibution of participants ("users")
# in workshops. It outputs the solution to solution.csv and displays the
# maximized score.
# Note that removing some workshops (if you have enough space) may improve
# the total score, and you should experiment with this.

set rounds;

set users;

set workshops;

param max{workshops, rounds};
param min{workshops, rounds};

param profit{users,workshops};

# The schedule to be calculated
var x{users,workshops,rounds} binary;

maximize totalprofit:
    sum{u in users, w in workshops, r in rounds}
        profit[u,w]*x[u,w,r];


# Each participant should be assigned to a workshop exactly as
# there are number of rounds.
subject to users_constraint{u in users}:
sum{w in workshops, r in rounds} x[u,w,r] = card(rounds);

# Each participant should be assigned exactly one workshop per round
subject to round_constraint{u in users, r in rounds}:
sum{w in workshops} x[u,w,r] = 1;

# Each participant may do a workshop only once
subject to round_constraint2{u in users, w in workshops}:
sum{r in rounds} x[u,w,r] <= 1;

# The amount of participants for is limited per workshop
subject to workshops_max_constraint{w in workshops, r in rounds}:
sum{u in users} x[u,w,r] <= max[w,r];

# The amount of participants must be at least some amount per workshop
subject to workshops_min_constraint{w in workshops, r in rounds}:
sum{u in users} x[u,w,r] >= min[w,r];

solve;

# Output the distribution
printf "Participant, Round, Workshop, Score\n" > "solution.csv";
for {u in users, r in rounds, w in workshops: x[u,w,r] = 1} {
    printf "%s, %s, %s, %d\n", u, r, w, profit[u,w] >> "solution.csv";
}

display totalprofit;
'''.lstrip()

class Command(BaseCommand):
    """
    The `calculate` command reads the database and writes to the output file
    provided on the command line.

    After generating the model, the calculation can be done using gplsol:

    ```shell
    glpsol -m $MODEL_FILE -o solution.txt
    ```
    """

    help = 'Generate a glpsol model from the database'

    @staticmethod
    def _prepare_name(s):
        return "'%s'" % re.sub("[^A-Za-z0-9 ]","", s)

    @staticmethod
    def add_arguments(parser):
        parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT_FILE,
            help='the file the glpsol model will be written to;'
            ' defaults to %s' % DEFAULT_OUTPUT_FILE)

    def handle(self, *args, **options):
        # check the app for problems
        self.check(['workshops'])

        # load workshops
        workshops = OrderedDict()
        for ws in Workshop.objects.filter():
            workshops[self._prepare_name(ws.naam)] = {"min": ws.min, "max": ws.max}

        # load users
        users = []
        db_users = []
        for user in User.objects.filter(deleted=False):
            db_users.append(user.id)
            users.append(self._prepare_name(user.naam))

        # load user preferences
        prefs = OrderedDict()
        for rating in WorkshopRating.objects.filter(user__in=db_users):
            prefs[self._prepare_name(rating.user.naam),
                self._prepare_name(rating.workshop.naam)] = rating.rating

        with open(options['output'], 'w') as f:
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

            f.write("param min : ")
            f.write(' '.join(ROUNDS))
            f.write(' :=\n')
            for workshop, v in workshops.items():
                f.write("%s %s\n" %
                    (workshop, " ".join(str(x) for x in [v['min']]*len(ROUNDS))))
            f.write(";\n");

            f.write("param max : ")
            f.write(' '.join(ROUNDS))
            f.write(' :=\n')
            for workshop, v in workshops.items():
                f.write("%s %s\n" %
                    (workshop, " ".join(str(x) for x in [v['max']]*len(ROUNDS))))
            f.write(";\n");

            f.write("param profit : ")
            f.write(' '.join(workshops))
            f.write(' :=\n')
            for u in users:
                f.write("%s " % u)
                for w in workshops:
                    f.write("%d " % prefs[u, w])
                f.write("\n")
            f.write(";\n");

            f.write("end;\n")
