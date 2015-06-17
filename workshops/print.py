from random import shuffle
import json
import sys

from pdn.workshops.models import Workshop, User, WorkshopRating

workshops = dict()
for ws in Workshop.objects.all():
	workshops[ws.id] = ws

usernames = dict()
for user in User.objects.filter(deleted=False):
	usernames[user.id] = user.naam

users = dict()
for user in User.objects.filter(deleted=False):
	users[user.id] = dict()
for rating in WorkshopRating.objects.filter(user__in=users.keys()):
	users[rating.user_id][rating.workshop_id] = rating.rating

users_ordered = dict()
for user, rating in users.items():
	bla = rating.items()
	bla.sort(key=lambda x: x[1], reverse=True)
	users_ordered[user] = map(lambda x: x[0], bla)

print users_ordered

assert len(users) == len(users_ordered)

for user, ratings in users.items():
	assert len(ratings) == len(workshops)
print "%d users" % len(users)

def show_indeling(indeling):
	score = dict()
	for i in [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]:
		score[i] = 0
	for ronde, rindeling in indeling.items():
		for user, workshop in rindeling.items():
			score[users[int(user)][workshop]] += 1
	print score

# fp = fopen(sys.argv[1], "r")
# data = fp.read()
# fp.close()
data = json.load(open(sys.argv[1]))
print data

print show_indeling(data)

print "== Alfabetische lijst =="
lines = list()
for user in User.objects.filter(deleted=False):
	lines.append("%-35s %-15s (%d) %-15s (%d)" % (user.naam, workshops[data['0'][str(user.id)]].naam, users[user.id][data['0'][str(user.id)]], workshops[data['1'][str(user.id)]].naam, users[user.id][data['1'][str(user.id)]]))
lines.sort(key=unicode.lower)
for line in lines:
	print line

print "== Per workshop =="
for ws in workshops.values():
	print "%s" % ws.naam
	for ronde in ['0', '1']:
		print " Ronde %d" % (int(ronde)+1)
		for user, workshop in data[ronde].items():
			if(ws.id == workshop):
				print "  %s" % usernames[int(user)]
