import json

with open("data/config.json", "r") as f:
    data = json.load(f)

print(data)

TurretData = {}
BallData = {}
Ownturret = {}
goanglesxy = {}
goanglez = {}

for x in NumTurrets:
	TurretData = {'turretnum': {json.load()}}
	numturrets += 1

for y in NumBall:
	BallData = {'Ballnum': {json.load()}}
	numball += 1

def XYAngleConversion():
	for x in range of numturrets:
		xcoord = r*costheta
		ycoord = r*sintheta
		goangle = arctan((ycoord-ownycoord)/(xcoord-ownxcoord))
		goangles = {'turret + xnum': goangle}
	for y in range of numball:
		xcoordb = rb*costthetab
		ycoordb = rb*sinthetab
		goanglesb = arctan((ycoordb-ownycoord)/(xcoordb-ownxcoord))
		goangles = {'ball + ynum': goanglesb}

def ZAngleConversation():							#Convers
	for z in range of numball:
		goanglesz = arccos((ycoorb-ownycoord)/(z))
		goanglez = {'ball + znum': goanglesz}


# While loop to continously rotate between targets until termination
