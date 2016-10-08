#!/usr/bin/env python

from Adafruit_PWM_Servo_Driver import PWM
from Joint import Joint
import time, math

# FL
#	KNEE	servoMin = 170, servoMax = 650, 90 = 400	
# 	FOOT	servoMin = 170, servoMax = 645, 90 = 400
# FR
#	KNEE	servoMin = 170, servoMax = 630, 90 = 400
#	FOOT	servoMin = 170, servoMax = 640, 90 = 400
# BL
#	KNEE	servoMin = 170, servoMax = 645

class Leg:
	FL = 0
	FR = 1
	BL = 2
	BR = 3

	HIP = 0
	KNEE = 1
	FOOT = 2

	state = -1
	hip = None
	knee = None
	foot = None
	pwm = PWM(0x40)
	leg = None
	# notice that this variable is different from the one in Joint.py
	servoSpeed = 0.0523598775598298 # rad/centisecond 3deg/centisecond 300deg/second (1/(joint.servoSpeed))/100
	sineCount = 0
	sineCountMax = 120 # also is set in self.__init__(leg)
	jointBaseline = None
	maxSineJointAng = None
	minSineJointAng = None
	jointAmplitude = None

	# in seconds
	ETA = 1
	
	def __init__(self, leg): # TODO fill out max and min lists
		self.leg = leg
		if leg == self.FL:
			self.hip = Joint(0, "FLHIP")
			self.knee = Joint(1, "FLKNEE")
			self.foot = Joint(2, "FLFOOT")
			# TODO
							#HIP	KNEE	FOOT
			self.maxSineJointAng = 		[70, 	160, 	30]
			self.minSineJointAng = 		[110, 	100, 	100]
			#amplitude 			20	30	35
		elif leg == self.FR:
			self.hip = Joint(3, "FRHIP")
			self.knee = Joint(4, "FRKNEE")
			self.foot = Joint(5, "FRFOOT")
										#HIP	KNEE	FOOT
		#	self.maxSineJointAng = 		[, 		, 		]
		#	self.minSineJointAng = 		[, 		, 		]
		elif leg == self.BR:
			self.hip = Joint(6, "BRHIP")
			self.knee = Joint(7, "BRKNEE")
			self.foot = Joint(8, "BRFOOT")
										#HIP	KNEE	FOOT
		#	self.maxSineJointAng = 		[, 		, 		]
		#	self.minSineJointAng = 		[, 		, 		]
		elif leg == self.BL:
			self.hip = Joint(9, "BLHIP")
			self.knee = Joint(10, "BLKNEE")
			self.foot = Joint(11, "BLFOOT")
										#HIP	KNEE	FOOT
		#	self.maxSineJointAng = 		[, 		, 		]
		#	self.minSineJointAng = 		[, 		, 		]
		self.jointBaseline = [	(self.maxSineJointAng[self.HIP]+self.minSineJointAng[self.HIP])/2.0, 
								(self.maxSineJointAng[self.KNEE]+self.minSineJointAng[self.KNEE])/2.0, 
								(self.maxSineJointAng[self.FOOT]+self.minSineJointAng[self.FOOT])/2.0]
		self.jointAmplitude = [	abs(self.maxSineJointAng[self.HIP]-self.minSineJointAng[self.HIP])/2.0, 
								abs(self.maxSineJointAng[self.KNEE]-self.minSineJointAng[self.KNEE])/2.0, 
								abs(self.maxSineJointAng[self.FOOT]-self.minSineJointAng[self.FOOT])/2.0]
		self.sineCountMax = int((2*math.pi)/self.servoSpeed) 
		self.state = "initialized"

	def getServoAngle(self, joint):
		#		(abs(maxSineJointAng-minSineJointAng)/2.0)*math.sin(self.servoSpeed*self.sineCount)*180/math.pi+jointBaseline
		if self.leg == self.FL or self.leg == self.BR:
			return self.jointAmplitude[joint]*math.sin(self.servoSpeed*self.sineCount)*57.2957795130824+self.jointBaseline[joint]
		else:
			return self.jointAmplitude[joint]*math.sin(self.servoSpeed*self.sineCount+math.pi)*57.2957795130824+self.jointBaseline[joint]

	def sineRun(self):
		for joint in range(0, self.FOOT+1):
			ang = self.getServoAngle(joint)
			print self.jointAmplitude[joint]
			if joint == self.HIP:
				self.hip.moveToAngle(ang)
			elif joint == self.KNEE:
				self.knee.moveToAngle(ang)
			elif joint == self.FOOT:
				self.foot.moveToAngle(ang)
	#		print ang
										   # 120
		print ""
		self.sineCount = (self.sineCount+1)%self.sineCountMax
		print self.sineCount

	def raiseLeg(self):
#		if self.leg == self.FL or self.leg == self.BR:
		self.hip.moveToAngle(90)
#		elif self.leg == self.FR or self.leg == self.BL:
#			self.hip.moveToAngle(60)
		self.ETA = self.hip.ETA
		self.state = "RAISED"

	def lowerLeg(self):
#		if self.leg == self.FL or self.leg == self.BR:
		self.hip.moveToAngle(70)
#		else:
#			self.hip.moveToAngle(120)
		self.ETA = self.hip.ETA
		self.state = "LOWERED"

	def forwardStep(self):
		if self.leg == self.FL or self.leg == self.FR:
			self.knee.moveToAngle(70)
			self.foot.moveToAngle(70)
		else:
			self.knee.moveToAngle(140)
			self.foot.moveToAngle(110)
		self.ETA = self.knee.ETA
		if self.ETA < self.foot.ETA:
			self.ETA = self.foot.ETA
		if("RAISED" in self.state):
			self.state = "RAISED_FORWARD"
		elif("LOWERED" in self.state):
			self.state = "LOWERED_FORWARD"
		else:
			self.state = "FORWARD"
	
	def backwardStep(self):
		if self.leg == self.FL or self.leg == self.FR:
			self.knee.moveToAngle(140)
			self.foot.moveToAngle(110)
		elif self.leg == self.BR or self.leg == self.BL:
			self.knee.moveToAngle(70)
			self.foot.moveToAngle(70)
		self.ETA = self.knee.ETA
		if self.ETA < self.knee.ETA:
			self.ETA = self.knee.ETA
		if("RAISED" in self.state):
			self.state = "RAISED_BACKWARD"
		elif("LOWERED" in self.state):
			self.state = "LOWERED_BACKWARD"
		else:
			self.state = "BACKWARD"

	def tallStand(self):
		self.hip.moveToAngle(70)
		self.knee.moveToAngle(130) #130
		self.foot.moveToAngle(55) #55
		self.ETA = self.hip.ETA
		if self.ETA < self.knee.ETA:
			self.ETA = self.knee.ETA
		if self.ETA < self.foot.ETA:
			self.ETA = self.foot.ETA
		self.state = "TALL_STAND"

	def stand(self):
		self.hip.moveToAngle(70)
		self.knee.moveToAngle(90) #130
		self.foot.moveToAngle(90) #55
		self.ETA = self.hip.ETA
		if self.ETA < self.knee.ETA:
			self.ETA = self.knee.ETA
		if self.ETA < self.foot.ETA:
			self.ETA = self.foot.ETA
		self.state = "STAND"

	def dip(self): 
		if self.leg == self.FL or self.leg == self.FR:
			self.knee.moveToAngle(135)
			self.foot.moveToAngle(70)
		else:
			self.knee.moveToAngle(135)
			self.foot.moveToAngle(70)
		self.ETA = self.hip.ETA
		self.state = "DIP"
	
	def undip(self):
		self.stand()

	def cornerDip(self):
		if self.leg == self.FL or self.leg == self.FR:
			self.hip.moveToAngle(100)
			self.knee.moveToAngle(120)
			self.foot.moveToAngle(70)
		else:
			self.hip.moveToAngle(100)
			self.knee.moveToAngle(120)
			self.foot.moveToAngle(70)
		self.ETA = self.hip.ETA
		self.state = "CORNER_DIP"

	def pullIn(self):
		if self.leg == self.FL or self.leg == self.BR:
			self.knee.moveToAngle(175)
			self.foot.moveToAngle(15)
		else:
			self.knee.moveToAngle(175)
			self.foot.moveToAngle(15)
		self.ETA = self.knee.ETA
		if self.ETA < self.foot.ETA:
			self.ETA = self.foot.ETA
		self.state = "PULLED_IN"

	def pushOut(self):
		if self.leg == self.FR or self.leg == self.BL:
			self.knee.moveToAngle(70)
			self.foot.moveToAngle(90)
		else:
			self.knee.moveToAngle(70)
			self.foot.moveToAngle(90)
		self.ETA = self.knee.ETA
		if self.ETA < self.foot.ETA:
			self.ETA = self.foot.ETA
		self.state = "PUSHED_OUT"

	def tallStand90Hip(self):
		self.hip.moveToAngle(90)
		self.knee.moveToAngle(130) #130
		self.foot.moveToAngle(55) #55
		self.ETA = self.hip.ETA
		if self.ETA < self.knee.ETA:
			self.ETA = self.knee.ETA
		if self.ETA < self.foot.ETA:
			self.ETA = self.foot.ETA
		self.state = "TALL_STAND"
	
	def pullInFront(self):
		if self.leg == self.FL or self.leg == self.BR:
			self.knee.moveToAngle(160)
			self.foot.moveToAngle(60)
		else:
			self.knee.moveToAngle(160)
			self.foot.moveToAngle(60)
		self.ETA = self.knee.ETA
		if self.ETA < self.foot.ETA:
			self.ETA = self.foot.ETA
		self.state = "PULLED_IN"

	def curlIn(self):
		if self.leg == self.FL or self.leg == self.BR:
			self.knee.moveToAngle(160)
			self.foot.moveToAngle(110)
		else:
			self.knee.moveToAngle(160)
			self.foot.moveToAngle(110)
		self.ETA = self.knee.ETA
		if self.ETA < self.foot.ETA:
			self.ETA = self.foot.ETA
		self.state = "CURLED_IN"	

	def tuck(self):
		self.hip.moveToAngle(40)
		self.DTA = self.hip.ETA
		self.state = "tucked"

if __name__ == '__main__':
	l = Leg(0)
	#l.knee.moveToAngle(160)
	#l.foot.moveToAngle(90)
	while True:
		l.sineRun()
		time.sleep(.1)
	#	s = "Next angle?"
	#	i = raw_input(s)
	#	l.foot.moveToAngle(int(i))
