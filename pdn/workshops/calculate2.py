from random import shuffle
import json
import threading
import sys

from pdn.workshops.models import Workshop, User, WorkshopRating

workshops = dict()
for ws in Workshop.objects.filter():
	workshops[ws.id] = ws.max

prefs = dict()
users = list()
_users = []
for user in User.objects.filter(deleted=False):
    _users.append(user.id)
    users.append('u'+str(user.id))
for rating in WorkshopRating.objects.filter(user__in=_users):
    prefs['u'+str(rating.user_id), 'workshop'
                    +str(rating.workshop_id)] = rating.rating


def score_indeling(indeling):
	score = 0
	for ronde, rindeling in indeling.items():
		for user, workshop in rindeling.items():
			if users[user][workshop] < 0:
				score -= 50
			score += users[user][workshop]
	return score

slots = []
for w, c in workshops.iteritems():
    for i in xrange(c):
        slots.append('workshop'+str(w)+'slot'+str(i))

for d in xrange(len(slots) - len(users)):
    p = 'bogus'+str(d)
    users.append(p)
    for w in workshops:
        prefs[p,'workshop'+str(w)] = 0

rounds = ['1', '2']

with open('out.sol', 'w') as f:
    f.write(""" set users;
                set slots;
                set rounds;

                param profit{users,slots};
                var x{users,slots,rounds} binary;

                maximize totalprofit:
                    sum{i in users, j in slots, r in rounds}
                        profit[i,j]*x[i,j,r];

                subject to users_contraint{i in users}:
            """)
    f.write("sum{j in slots, r in rounds} x[i,j,r] <= "+str(len(rounds))+";\n")
    f.write(""" subject to workshop_constraint{j in slots, r in rounds}:
                    sum{i in users} x[i,j,r] >= 1;
                subject to round_constraint1{i in users, r in rounds}:
                    sum{j in slots} x[i,j,r] <= 1;
                subject to round_constraint2{i in users, j in slots}:
                    sum{r in rounds} x[i,j,r] <= 1;

                solve;

                display totalprofit;

                data;
                """)
    f.write("set rounds := ")
    f.write(" ".join(rounds))
    f.write(";\n")

    f.write("set users := ")
    f.write(" ".join(users))
    f.write(";\n")

    f.write("set slots := ")
    f.write(" ".join(slots))
    f.write(";\n")

    f.write("param profit : ")
    f.write(' '.join(slots))
    f.write(' :=\n')
    for p in users:
        f.write(p)
        f.write(' ')
        for s in slots:
            f.write(str(prefs[p, s.rsplit('slot',1)[0]]))
            f.write(' ')
        f.write('\n')
    f.write(' ;\n')
    f.write('end;\n')
