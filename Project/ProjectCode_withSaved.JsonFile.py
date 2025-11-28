import json
import math

# LOAD JSON
with open("backup_data.json", "r") as f:
    data = json.load(f)

print(data)

TurretData = data["turrets"]        # dict of turret objects
BallData = data["globes"]           # list of ball objects

numturrets = len(TurretData)
numball = len(BallData)

# Our "own" coordinates (Must fill in these)
ownxcoord = 0
ownycoord = 0

goanglesxy = {}
goanglez = {}

# XY ANGLE CONVERSION
def XYAngleConversion():

    # Turrets
    for tnum, tinfo in TurretData.items():

        r = tinfo["r"]
        theta = tinfo["theta"]

        xcoord = r * math.cos(theta)
        ycoord = r * math.sin(theta)

        goangle = math.degrees(math.atan2((ycoord - ownycoord), (xcoord - ownxcoord)))

        goanglesxy[f"turret_{tnum}"] = round(goangle, 2) 

    # Balls
    for i, binfo in enumerate(BallData, start=1):

        r = binfo["r"]
        theta = binfo["theta"]

        xcoordb = r * math.cos(theta)
        ycoordb = r * math.sin(theta)

        goangleb = math.degrees(math.atan2((ycoordb - ownycoord), (xcoordb - ownxcoord)))
        
        goanglesxy[f"ball_{i}"] = round(goangleb, 2) 


# Z ANGLE CONVERSION
# (elevation angle from XY plane)
def ZAngleConversion():

    for i, binfo in enumerate(BallData, start=1):

        r = binfo["r"]
        theta = binfo["theta"]
        z = binfo["z"]

        # xy projection
        xcoordb = r * math.cos(theta)
        ycoordb = r * math.sin(theta)

        # vector difference
        dx = xcoordb - ownxcoord
        dy = ycoordb - ownycoord
        dz = z

        # elevation angle = atan(dz / horizontal distance)
        horiz = math.sqrt(dx*dx + dy*dy)
        angle_z = math.atan2(dz, horiz)

        goanglez[f"ball_{i}"] = round(angle_z, 2)


# RUN THE CONVERSIONS
XYAngleConversion()
ZAngleConversion()

print('\n')
print("XY Angles:", goanglesxy)
print('\n')
print("Z Angles:", goanglez)
