import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pdn.settings")
import django
django.setup()

from random import shuffle
import json
import threading
import sys

from pdn.workshops.models import Workshop, User, WorkshopRating

workshops = dict()
for ws in Workshop.objects.filter():
	workshops[ws.id] = ws.max

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

best_score_lock = threading.Lock()
best_score = [0]
attempts = [0]

def run_thread():
	while True:
		indeling = make_random()
		score = score_indeling(indeling)
		if score > best_score[0]:
			best_score_lock.acquire()
			if score > best_score[0]:
				best_score[0] = score
				print "Nieuwe beste score: %d!" % score
				save_indeling(indeling, score)
			else:
				print "Ninja'd"
			best_score_lock.release()

def score_indeling(indeling):
	score = 0
	for ronde, rindeling in indeling.items():
		for user, workshop in rindeling.items():
			if users[user][workshop] < 0:
				score -= 50
			score += users[user][workshop]
	return score

def show_indeling(indeling):
	score = dict()
	for i in [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]:
		score[i] = 0
	for ronde, rindeling in indeling.items():
		for user, workshop in rindeling.items():
			score[users[user][workshop]] += 1
	print score

def save_indeling(indeling, score=None):
	if score is None:
		score = score_indeling(indeling)
	fp = open("indelingen/%d.txt" % score, "w")
	fp.write(json.dumps(indeling))
	fp.close()

def make_random():
	while True:
		indeling = {0: dict(), 1: dict()}
		shuffled = users.keys()
		shuffle(shuffled)
		plaatsen = {0: dict(), 1: dict()}
		for ws, max in workshops.items():
			plaatsen[0][ws] = max
			plaatsen[1][ws] = max
		for user in shuffled:
			for workshop in users_ordered[user]:
				if plaatsen[0][workshop] > 0:
					indeling[0][user] = workshop
					plaatsen[0][workshop] -= 1
					break
		shuffled.reverse()
		for user in shuffled:
			for workshop in users_ordered[user]:
				if plaatsen[1][workshop] > 0:
					if workshop == indeling[0][user]:
						continue
					# You are not allowed to workshop 2, 3 and 9 when you've been at workshop 6 first.
					# if indeling[0][user] == 6 and workshop in [2, 3, 9]:
					# 	continue
					indeling[1][user] = workshop
					plaatsen[1][workshop] -= 1
					break
		# Workshops 4 and 8 need an even number
		# if plaatsen[0][4] % 2 == 1 or plaatsen[1][4] % 2 == 1:
		# 	continue
		# if plaatsen[0][8] % 2 == 1 or plaatsen[1][8] % 2 == 1:
		# 	continue
		# Make sure all workshops are at least half full
		for workshop, max in workshops.items():
			if plaatsen[0][workshop] > max/2:
				indeling = False
				break
			if plaatsen[1][workshop] > max/2:
				indeling = False
				break
		if indeling:
			return indeling

indeling = make_random()
print indeling
score = score_indeling(indeling)
print score
print show_indeling(indeling)
save_indeling(indeling, score)

#threads = dict()
#for i in [0, 1, 2]:
#	threads[i] = threading.Thread(target=run_thread)
#	threads[i].start()

run_thread()
