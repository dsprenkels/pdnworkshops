import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pdn.settings")
import django
django.setup()

from workshops.models import Workshop, User, WorkshopRating

# Dit is een tweede manier om aan een rooster te komen. We gebruiken
# `geheeltallig lineair programmeren'.

model = '''
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

workshops = dict()
for ws in Workshop.objects.filter():
	workshops[ws.id] = {"min": 0, "max": ws.max}

prefs = dict()
users = list()
db_users = []
for user in User.objects.filter(deleted=False):
    db_users.append(user.id)
    users.append('u'+str(user.id))
for rating in WorkshopRating.objects.filter(user__in=db_users):
    prefs['u'+str(rating.user_id), 'workshop'
                    +str(rating.workshop_id)] = rating.rating


rounds = ['1', '2']

with open('out3.sol', 'w') as f:
    f.write("%s\n" % model)
    f.write("data;\n")

    f.write("set rounds := %s;\n" % " ".join(rounds))

    f.write("set users :=\n")
    f.write(" ".join(users))
    f.write(";\n")

    f.write("set workshops :=\n")
    f.write(" ".join(['workshop%s' % w for w in workshops]))
    f.write(";\n")
    
    f.write("param : min max :=\n")
    for k, v in workshops.items():
        f.write("workshop%s %d %d\n" % (k, v['min'], v['max']))
    f.write("\n;")

    f.write("param profit : ")
    f.write(' '.join("workshop%d" % w for w in workshops))
    f.write(' :=\n')
    for u in users:
        f.write("%s " % u)
        for w in workshops:
            f.write("%d " % prefs[u, "workshop%d" % w])
        f.write("\n")
    f.write("\n;");

