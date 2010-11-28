#
#	Face bone definitions
#

import mhx_rig
from mhx_rig import *

FingerJoints = [
	('l-hand-2',		'j', 'l-hand-2'),
	('l-hand-3',		'j', 'l-hand-3'),
	('r-hand-2',		'j', 'r-hand-2'),
	('r-hand-3',		'j', 'r-hand-3'),
]

FingerHeadsTails = [
	('Finger-1-1_L',		'r-finger-1-1', 'r-finger-1-2'),
	('Finger-1-2_L',		'r-finger-1-2', 'r-finger-1-3'),
	('Finger-1-3_L',		'r-finger-1-3', 'r-finger-1-4'),
	('Finger-2-1_L',		'r-finger-2-1', 'r-finger-2-2'),
	('Finger-2-2_L',		'r-finger-2-2', 'r-finger-2-3'),
	('Finger-2-3_L',		'r-finger-2-3', 'r-finger-2-4'),
	('Finger-3-1_L',		'r-finger-3-1', 'r-finger-3-2'),
	('Finger-3-2_L',		'r-finger-3-2', 'r-finger-3-3'),
	('Finger-3-3_L',		'r-finger-3-3', 'r-finger-3-4'),
	('Finger-4-1_L',		'r-finger-4-1', 'r-finger-4-2'),
	('Finger-4-2_L',		'r-finger-4-2', 'r-finger-4-3'),
	('Finger-4-3_L',		'r-finger-4-3', 'r-finger-4-4'),
	('Finger-5-1_L',		'r-finger-5-1', 'r-finger-5-2'),
	('Finger-5-2_L',		'r-finger-5-2', 'r-finger-5-3'),
	('Finger-5-3_L',		'r-finger-5-3', 'r-finger-5-4'),

	('Finger-1-1_R',		'l-finger-1-1', 'l-finger-1-2'),
	('Finger-1-2_R',		'l-finger-1-2', 'l-finger-1-3'),
	('Finger-1-3_R',		'l-finger-1-3', 'l-finger-1-4'),
	('Finger-2-1_R',		'l-finger-2-1', 'l-finger-2-2'),
	('Finger-2-2_R',		'l-finger-2-2', 'l-finger-2-3'),
	('Finger-2-3_R',		'l-finger-2-3', 'l-finger-2-4'),
	('Finger-3-1_R',		'l-finger-3-1', 'l-finger-3-2'),
	('Finger-3-2_R',		'l-finger-3-2', 'l-finger-3-3'),
	('Finger-3-3_R',		'l-finger-3-3', 'l-finger-3-4'),
	('Finger-4-1_R',		'l-finger-4-1', 'l-finger-4-2'),
	('Finger-4-2_R',		'l-finger-4-2', 'l-finger-4-3'),
	('Finger-4-3_R',		'l-finger-4-3', 'l-finger-4-4'),
	('Finger-5-1_R',		'l-finger-5-1', 'l-finger-5-2'),
	('Finger-5-2_R',		'l-finger-5-2', 'l-finger-5-3'),
	('Finger-5-3_R',		'l-finger-5-3', 'l-finger-5-4'),

	('Finger-1_R',			'l-finger-1-2', 'l-finger-1-4'),
	('Finger-2_R',			'l-finger-2-1', 'l-finger-2-4'),
	('Finger-3_R',			'l-finger-3-1', 'l-finger-3-4'),
	('Finger-4_R',			'l-finger-4-1', 'l-finger-4-4'),
	('Finger-5_R',			'l-finger-5-1', 'l-finger-5-4'),

	('Finger-1_L',			'r-finger-1-2', 'r-finger-1-4'),
	('Finger-2_L',			'r-finger-2-1', 'r-finger-2-4'),
	('Finger-3_L',			'r-finger-3-1', 'r-finger-3-4'),
	('Finger-4_L',			'r-finger-4-1', 'r-finger-4-4'),
	('Finger-5_L',			'r-finger-5-1', 'r-finger-5-4'),
]

'''
	('Wrist-1_L',			'r-hand', 'r-hand-3'),
	('Wrist-2_L',			'r-hand', 'r-hand-2'),
	('Palm-1_L',			'r-hand', 'r-finger-1-1'),
	('Palm-2_L',			'r-hand-3', 'r-finger-2-1'),
	('Palm-3_L',			'r-hand-3', 'r-finger-3-1'),
	('Palm-4_L',			'r-hand-2', 'r-finger-4-1'),
	('Palm-5_L',			'r-hand-2', 'r-finger-5-1'),

	('Wrist-1_R',			'l-hand', 'l-hand-3'),
	('Wrist-2_R',			'l-hand', 'l-hand-2'),
	('Palm-1_R',			'l-hand', 'l-finger-1-1'),
	('Palm-2_R',			'l-hand-3', 'l-finger-2-1'),
	('Palm-3_R',			'l-hand-3', 'l-finger-3-1'),
	('Palm-4_R',			'l-hand-2', 'l-finger-4-1'),
	('Palm-5_R',			'l-hand-2', 'l-finger-5-1'),

	('Wrist-1_L',		0.0, 'Hand_L', F_DEF, L_PALM, (1,1,1) ),
	('Wrist-2_L',		0.0, 'Hand_L', F_DEF, L_PALM, (1,1,1) ),
	('Palm-1_L',		0.0, 'Hand_L', F_DEF, L_PALM, (1,1,1) ),
	('Palm-2_L',		0.0, 'Wrist-1_L', F_DEF, L_PALM, (1,1,1) ),
	('Palm-3_L',		0.0, 'Wrist-1_L', F_DEF, L_PALM, (1,1,1) ),
	('Palm-4_L',		0.0, 'Wrist-2_L', F_DEF, L_PALM, (1,1,1) ),
	('Palm-5_L',		0.0, 'Wrist-2_L', F_DEF, L_PALM, (1,1,1) ),

	('Wrist-1_R',		0.0, 'Hand_R', F_DEF, L_PALM, (1,1,1) ),
	('Wrist-2_R',		0.0, 'Hand_R', F_DEF, L_PALM, (1,1,1) ),
	('Palm-1_R',		0.0, 'Hand_R', F_DEF, L_PALM, (1,1,1) ),
	('Palm-2_R',		0.0, 'Wrist-1_R', F_DEF, L_PALM, (1,1,1) ),
	('Palm-3_R',		0.0, 'Wrist-1_R', F_DEF, L_PALM, (1,1,1) ),
	('Palm-4_R',		0.0, 'Wrist-2_R', F_DEF, L_PALM, (1,1,1) ),
	('Palm-5_R',		0.0, 'Wrist-2_R', F_DEF, L_PALM, (1,1,1) ),

'''

ThumbRoll = 90*deg1

FingerArmature = [
	# Deform
	('Finger-1-1_L',		ThumbRoll, 'Hand_L', F_DEF, L_HANDFK+L_HANDIK, (1,1,1) ),
	('Finger-1-2_L',		ThumbRoll, 'Finger-1-1_L', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-1-3_L',		ThumbRoll, 'Finger-1-2_L', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-2-1_L',		0.0, 'Hand_L', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-2-2_L',		0.0, 'Finger-2-1_L', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-2-3_L',		0.0, 'Finger-2-2_L', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-3-1_L',		0.0, 'Hand_L', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-3-2_L',		0.0, 'Finger-3-1_L', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-3-3_L',		0.0, 'Finger-3-2_L', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-4-1_L',		0.0, 'Hand_L', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-4-2_L',		0.0, 'Finger-4-1_L', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-4-3_L',		0.0, 'Finger-4-2_L', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-5-1_L',		0.0, 'Hand_L', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-5-2_L',		0.0, 'Finger-5-1_L', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-5-3_L',		0.0, 'Finger-5-2_L', F_DEF, L_HANDFK, (1,1,1) ),

	('Finger-1-1_R',		-ThumbRoll, 'Hand_R', F_DEF, L_HANDFK+L_HANDIK, (1,1,1) ),
	('Finger-1-2_R',		-ThumbRoll, 'Finger-1-1_R', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-1-3_R',		-ThumbRoll, 'Finger-1-2_R', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-2-1_R',		0.0, 'Hand_R', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-2-2_R',		0.0, 'Finger-2-1_R', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-2-3_R',		0.0, 'Finger-2-2_R', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-3-1_R',		0.0, 'Hand_R', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-3-2_R',		0.0, 'Finger-3-1_R', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-3-3_R',		0.0, 'Finger-3-2_R', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-4-1_R',		0.0, 'Hand_R', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-4-2_R',		0.0, 'Finger-4-1_R', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-4-3_R',		0.0, 'Finger-4-2_R', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-5-1_R',		0.0, 'Hand_R', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-5-2_R',		0.0, 'Finger-5-1_R', F_DEF, L_HANDFK, (1,1,1) ),
	('Finger-5-3_R',		0.0, 'Finger-5-2_R', F_DEF, L_HANDFK, (1,1,1) ),

	# Finger controls
	('Finger-1_L',		ThumbRoll, 'Finger-1-1_L', F_WIR, L_HANDIK, (1,1,1) ),
	('Finger-2_L',		0.0, 'Hand_L', F_WIR, L_HANDIK, (1,1,1) ),
	('Finger-3_L',		0.0, 'Hand_L', F_WIR, L_HANDIK, (1,1,1) ),
	('Finger-4_L',		0.0, 'Hand_L', F_WIR, L_HANDIK, (1,1,1) ),
	('Finger-5_L',		0.0, 'Hand_L', F_WIR, L_HANDIK, (1,1,1) ),
	
	('Finger-1_R',		-ThumbRoll, 'Finger-1-1_R', F_WIR, L_HANDIK, (1,1,1) ),
	('Finger-2_R',		0.0, 'Hand_R', F_WIR, L_HANDIK, (1,1,1) ),
	('Finger-3_R',		0.0, 'Hand_R', F_WIR, L_HANDIK, (1,1,1) ),
	('Finger-4_R',		0.0, 'Hand_R', F_WIR, L_HANDIK, (1,1,1) ),
	('Finger-5_R',		0.0, 'Hand_R', F_WIR, L_HANDIK, (1,1,1) ),
]

#
#	defineFingerConstraints():
#

limitRotThumb = ('LimitRot', C_OW_LOCAL, 1, ['LimitRot', (-1.37,0.5, 0,0, -deg60,deg60), (1,0,1)]) 
limitRotFingers = ('LimitRot', C_OW_LOCAL, 1, ['LimitRot', (-1.37,0.5, 0,0, -deg30,deg30), (1,0,1)]) 

def defineFingerConstraints():
	fconstraints = {}
	for fnum in range(1,6):
		for suffix in ["_L", "_R"]:
			finger = "Finger-%d%s" % (fnum, suffix)
			for lnum in range(1,4):
				if fnum == 1:
					if lnum == 1:
						cnss = []
					else:
						cnss = [ ('CopyRot', C_OW_LOCAL+C_TG_LOCAL, 1, ['Rot', finger, (1,0,0), (0,0,0), True]) ]
					cnss.append( limitRotThumb )
				else:
					if lnum == 1:
						cnss = [ ('CopyRot', C_OW_LOCAL+C_TG_LOCAL, 1, ['Rot', finger, (1,0,1), (0,0,0), True]) ]
					else:
						cnss = [ ('CopyRot', C_OW_LOCAL+C_TG_LOCAL, 1, ['Rot', finger, (1,0,0), (0,0,0), True]) ]
					cnss.append( limitRotFingers )
				fconstraints["%d-%d%s" % (fnum, lnum, suffix)] = cnss
	return fconstraints
	
fconstraints = defineFingerConstraints()	

#
#	FingerWritePoses(fp):
#

customShape = 'MHCircle05'
customShape = None
		
def FingerWritePoses(fp):
	addPoseBone(fp, 'Finger-1-1_L', customShape, None, (1,1,1), (0,1,0), (1,1,1), (1,0,1), 0, fconstraints["1-1_L"])
	addPoseBone(fp, 'Finger-1-2_L', customShape, None, (1,1,1), (0,1,0), (1,1,1), (0,0,1), 0, fconstraints["1-2_L"])
	addPoseBone(fp, 'Finger-1-3_L', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["1-3_L"])

	addPoseBone(fp, 'Finger-1-1_R', customShape, None, (1,1,1), (0,1,0), (1,1,1), (1,0,1), 0, fconstraints["1-1_R"])
	addPoseBone(fp, 'Finger-1-2_R', customShape, None, (1,1,1), (0,1,0), (1,1,1), (0,0,1), 0, fconstraints["1-2_R"])
	addPoseBone(fp, 'Finger-1-3_R', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["1-3_R"])

	addPoseBone(fp, 'Finger-2-1_L', customShape, None, (1,1,1), (0,1,0), (1,1,1), (1,0,1), 0, fconstraints["2-1_L"])
	addPoseBone(fp, 'Finger-2-2_L', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["2-2_L"])
	addPoseBone(fp, 'Finger-2-3_L', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["2-3_L"])

	addPoseBone(fp, 'Finger-2-1_R', customShape, None, (1,1,1), (0,1,0), (1,1,1), (1,0,1), 0, fconstraints["2-1_R"])
	addPoseBone(fp, 'Finger-2-2_R', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["2-2_R"])
	addPoseBone(fp, 'Finger-2-3_R', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["2-3_R"])

	addPoseBone(fp, 'Finger-3-1_L', customShape, None, (1,1,1), (0,1,0), (1,1,1), (1,0,1), 0, fconstraints["3-1_L"])
	addPoseBone(fp, 'Finger-3-2_L', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["3-2_L"])
	addPoseBone(fp, 'Finger-3-3_L', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["3-3_L"])

	addPoseBone(fp, 'Finger-3-1_R', customShape, None, (1,1,1), (0,1,0), (1,1,1), (1,0,1), 0, fconstraints["3-1_R"])
	addPoseBone(fp, 'Finger-3-2_R', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["3-2_R"])
	addPoseBone(fp, 'Finger-3-3_R', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["3-3_R"])

	addPoseBone(fp, 'Finger-4-1_L', customShape, None, (1,1,1), (0,1,0), (1,1,1), (1,0,1), 0, fconstraints["4-1_L"])
	addPoseBone(fp, 'Finger-4-2_L', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["4-2_L"])
	addPoseBone(fp, 'Finger-4-3_L', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["4-3_L"])

	addPoseBone(fp, 'Finger-4-1_R', customShape, None, (1,1,1), (0,1,0), (1,1,1), (1,0,1), 0, fconstraints["4-1_R"])
	addPoseBone(fp, 'Finger-4-2_R', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["4-2_R"])
	addPoseBone(fp, 'Finger-4-3_R', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["4-3_R"])

	addPoseBone(fp, 'Finger-5-1_L', customShape, None, (1,1,1), (0,1,0), (1,1,1), (1,0,1), 0, fconstraints["5-1_L"])
	addPoseBone(fp, 'Finger-5-2_L', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["5-2_L"])
	addPoseBone(fp, 'Finger-5-3_L', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["5-3_L"])

	addPoseBone(fp, 'Finger-5-1_R', customShape, None, (1,1,1), (0,1,0), (1,0,1), (1,1,1), 0, fconstraints["5-1_R"])
	addPoseBone(fp, 'Finger-5-2_R', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["5-2_R"])
	addPoseBone(fp, 'Finger-5-3_R', customShape, None, (1,1,1), (0,1,1), (1,1,1), (0,0,1), 0, fconstraints["5-3_R"])
	
	# Control fingers
	addPoseBone(fp, 'Finger-1_L', 'MHKnuckle', None, (1,1,1), (0,1,0), (1,0,1), (1,1,1), 0, [limitRotThumb])
	addPoseBone(fp, 'Finger-2_L', 'MHKnuckle', None, (1,1,1), (0,1,0), (1,0,1), (1,1,1), 0, [limitRotFingers])
	addPoseBone(fp, 'Finger-3_L', 'MHKnuckle', None, (1,1,1), (0,1,0), (1,0,1), (1,1,1), 0, [limitRotFingers])
	addPoseBone(fp, 'Finger-4_L', 'MHKnuckle', None, (1,1,1), (0,1,0), (1,0,1), (1,1,1), 0, [limitRotFingers])
	addPoseBone(fp, 'Finger-5_L', 'MHKnuckle', None, (1,1,1), (0,1,0), (1,0,1), (1,1,1), 0, [limitRotFingers])
	
	addPoseBone(fp, 'Finger-1_R', 'MHKnuckle', None, (1,1,1), (0,1,0), (1,0,1), (1,1,1), 0, [limitRotThumb])
	addPoseBone(fp, 'Finger-2_R', 'MHKnuckle', None, (1,1,1), (0,1,0), (1,0,1), (1,1,1), 0, [limitRotFingers])
	addPoseBone(fp, 'Finger-3_R', 'MHKnuckle', None, (1,1,1), (0,1,0), (1,0,1), (1,1,1), 0, [limitRotFingers])
	addPoseBone(fp, 'Finger-4_R', 'MHKnuckle', None, (1,1,1), (0,1,0), (1,0,1), (1,1,1), 0, [limitRotFingers])
	addPoseBone(fp, 'Finger-5_R', 'MHKnuckle', None, (1,1,1), (0,1,0), (1,0,1), (1,1,1), 0, [limitRotFingers])
	return	



