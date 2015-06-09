import _import
import textwrap

from pdn.workshops.models import Workshop, User, WorkshopRating

# Dit is een tweede manier om aan een rooster te komen. We gebruiken
# `geheeltallig lineair programmeren'.

def dedent(s):
    first, rest = s.split("\n",1)
    return first + "\n" + textwrap.dedent(rest)

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
    f.write(dedent("""
                # The rounds.  Probably just {1,2} or {1,2,3}.
                set rounds;

                # The participants.  Also contains bogus participants to fill
                # empty slots.
                set users;

                # The slots.  Each workshop has a variable amount.  Here they
                # are thrown together.  Will look like
                #   {workshop1slot1, ..., workshop1slot30, workshop2slot1,
                #    workshop2slot20, ... workshop12slot10}
                set slots;

                # User preference.
                #  Profit[u,s] is the score the user u gave for the workshop
                #  associated to the slot s.
                param profit{users,slots};

                # Set of workshops.
                set workshops;
                
                # slotOfWorkshop[w,s] = 1 if and only if s is a slot
                # of the workshop w.
                param slotOfWorkshop{workshops,slots};

                # The schedule.  x[u,s,r] is 1 if user u is assigned
                # the slot s in round r and 0 otherwise.
                var x{users,slots,rounds} binary;

                # We maximize the obvious thing.
                maximize totalprofit:
                    sum{i in users, j in slots, r in rounds}
                        profit[i,j]*x[i,j,r];

                # But must be sure the schedule makes sense.
                
                # Each participant should be assigned no more slots than
                # there are number of rounds.
                subject to users_contraint{i in users}:
            """))
    f.write("sum{j in slots, r in rounds} x[i,j,r] <= "+str(len(rounds))+";\n")
    f.write(dedent("""
                # Each slot should have at least one participant. (Consequently
                # each slot has at most one participant.)
                subject to workshop_constraint{j in slots, r in rounds}:
                    sum{i in users} x[i,j,r] >= 1;

                # In each round, each participant should be assigned no more
                # than one slot.
                subject to round_constraint1{i in users, r in rounds}:
                    sum{j in slots} x[i,j,r] <= 1;

                # Each participant can take a workshop at most once.
                subject to round_constraint2{i in users, w in workshops}:
                    sum{j in slots, r in rounds}
                        slotOfWorkshop[w,j] * x[i,j,r] <= 1;

                solve;

                display totalprofit;

                data;
                """))
    f.write("set rounds :=\n")
    f.write(" ".join(rounds))
    f.write(";\n")

    f.write("set users :=\n")
    f.write(" ".join(users))
    f.write(";\n")

    f.write("set slots :=\n")
    f.write(" ".join(slots))
    f.write(";\n")

    f.write("set workshops :=\n")
    f.write(" ".join(['workshop%s' % w for w in workshops]))
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

    f.write("param slotOfWorkshop : ")
    f.write(' '.join(slots))
    f.write(' :=\n')
    for w in workshops:
        f.write('workshop%s'%w)
        f.write(' ')
        for s in slots:
            f.write('1 ' if s.startswith('workshop%ss' % w) else '0 ')
        f.write('\n')
    f.write(' ;\n')
    f.write('end;\n')
