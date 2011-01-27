""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2009

**Licensing:**         GPL3 (see also http://sites.google.com/site/makehumandocs/licensing)

**Coding Standards:**  See http://sites.google.com/site/makehumandocs/developers-guide

Abstract
--------
Functions shared by all rigs 

Limit angles from http://hippydrome.com/

"""

import aljabr, mhxbones, mh2mhx, math
from aljabr import *

pi = 3.14159
D = pi/180
yunit = [0,1,0]
zunit = [0,0,-1]
ybis = [0,2,0]

unlimited = (-pi,pi, -pi,pi, -pi,pi)
NoBB = (1,1,1)
bbMarg = 0.05

#
#	Bone layers
#

L_MAIN = 	0x0001
L_SPINE =	0x0002
L_ARMIK =	0x0004
L_ARMFK =	0x0008
L_LEGIK =	0x0010
L_LEGFK =	0x0020
L_HANDIK =	0x0040
L_HANDFK =	0x0080

L_PANEL	=	0x0100
L_TORSO =	0x0200
L_TOE =		0x0200
L_HEAD =	0x0400
L_PALM =	0x0800

L_HLPIK	=	0x1000
L_HLPFK	=	0x2000
L_HELP	=	0x4000
L_DEF =		0x8000

#
#	Flags
#


F_CON = 0x0001
F_DEF = 0x0002
F_RES = 0x0004
#F_RES = 0
F_WIR = 0x0008
F_NOSCALE = 0x0010
F_GLOC = 0x0020
F_LOCK = 0x0040
F_HID = 0x0080
F_NOCYC = 0x0100


P_LKROT4 = 0x0001
P_LKROTW = 0x0002
P_IKLIN = 0x0004
P_IKROT = 0x0008
P_STRETCH = 0x0010
P_HID = 0x0020

P_ROTMODE = 0x0f00
P_QUAT = 0x0000
P_XYZ = 0x0100



C_ACT = 0x0004
C_EXP = 0x0008
C_LTRA = 0x0010
C_LOC = 0x0020
C_STRVOL = 0x0040
C_PLANEZ = 0x0080

C_OW_MASK = 0x0300
C_OW_WORLD = 0x0000
C_OW_LOCAL = 0x0100
C_OW_LOCPAR = 0x0200
C_OW_POSE = 0x0300

C_TG_MASK = 0x3000
C_TG_WORLD = 0x0000
C_TG_LOCAL = 0x1000
C_TG_LOCPAR = 0x2000
C_TG_POSE = 0x3000

C_CHILDOF = C_OW_POSE+C_TG_WORLD
C_LOCAL = C_OW_LOCAL+C_TG_LOCAL

rootChildOfConstraints = [
		('ChildOf', C_CHILDOF, 1, ['Floor', 'MasterFloor', (1,1,1), (1,1,1), (1,1,1)]),
		('ChildOf', C_CHILDOF, 0, ['Hips', 'MasterHips', (1,1,1), (1,1,1), (1,1,1)]),
		('ChildOf', C_CHILDOF, 0, ['Neck', 'MasterNeck', (1,1,1), (1,1,1), (1,1,1)])
]

Master = 'MasterFloor'
Master = None

#
#	newSetupJoints (obj, joints, headTails):
#
def newSetupJoints (obj, joints, headTails):
	global rigHead, rigTail, locations
	locations = {}
	for (key, typ, data) in joints:
		if typ == 'j':
			loc = mhxbones.calcJointPos(obj, data)
			locations[key] = loc
			locations[data] = loc
		elif typ == 'v':
			v = int(data)
			locations[key] = obj.verts[v].co
		elif typ == 'x':
			locations[key] = [float(data[0]), float(data[2]), -float(data[1])]

	for (key, typ, data) in joints:
		if typ == 'j':
			pass
		elif typ == 'b':
			locations[key] = locations[data]
		elif typ == 'p':
			x = locations[data[0]]
			y = locations[data[1]]
			z = locations[data[2]]
			locations[key] = [x[0],y[1],z[2]]
		elif typ == 'v':
			pass
		elif typ == 'x':
			pass
		elif typ == 'X':
			r = locations[data[0]]
			(x,y,z) = data[1]
			r1 = [float(x), float(y), float(z)]
			locations[key] = aljabr.vcross(r, r1)
		elif typ == 'l':
			((k1, joint1), (k2, joint2)) = data
			locations[key] = vadd(vmul(locations[joint1], k1), vmul(locations[joint2], k2))
		elif typ == 'o':
			(joint, offsSym) = data
			if type(offsSym) == str:
				offs = locations[offsSym]
			else:
				offs = offsSym
			locations[key] = vadd(locations[joint], offs)
		else:
			raise NameError("Unknown %s" % typ)

	rigHead = {}
	rigTail = {}
	for (bone, head, tail) in headTails:
		rigHead[bone] = findLocation(head)
		rigTail[bone] = findLocation(tail)
	return 

def findLocation(joint):
	try:
		(bone, offs) = joint
	except:
		offs = 0
	if offs:
		return vadd(locations[bone], offs)
	else:
		return locations[joint]

#
#	writeArmature(fp, armature, mhx25):
#	boolString(val):
#	addBone25(bone, roll, parent, flags, layers, bbone, fp):
#	addBone24(bone, roll, parent, flags, layers, bbone, fp):
#

def writeArmature(fp, armature, mhx25):
	global Mhx25
	Mhx25 = mhx25
	if Mhx25:
		for (bone, roll, parent, flags, layers, bbone) in armature:
			addBone25(bone, True, roll, parent, flags, layers, bbone, fp)
	else:
		for (bone, roll, parent, flags, layers, bbone) in armature:
			addBone24(bone, True, roll, parent, flags, layers, bbone, fp)
	return

def boolString(val):
	if val:
		return "True"
	else:
		return "False"

def addBone25(bone, cond, roll, parent, flags, layers, bbone, fp):
	global rigHead, rigTail

	conn = boolString(flags & F_CON)
	deform = boolString(flags & F_DEF)
	restr = boolString(flags & F_RES)
	wire = boolString(flags & F_WIR)
	scale = boolString(flags & F_NOSCALE == 0)
	lloc = boolString(flags & F_GLOC == 0)
	lock = boolString(flags & F_LOCK)
	hide = boolString(flags & F_HID)
	cyc = boolString(flags & F_NOCYC == 0)
	(bin, bout, bseg) = bbone

	fp.write("\n  Bone %s %s\n" % (bone, cond))
	(x, y, z) = rigHead[bone]
	fp.write("    head  %.6g %.6g %.6g  ;\n" % (x,-z,y))
	(x, y, z) = rigTail[bone]
	fp.write("    tail %.6g %.6g %.6g  ;\n" % (x,-z,y))
	if parent:
		fp.write("    parent Refer Bone %s ; \n" % (parent))
	fp.write(
"    roll %.6g ; \n" % (roll)+
"    bbone_in %d ; \n" % (bin) +
"    bbone_out %d ; \n" % (bout) +
"    bbone_segments %d ; \n" % (bseg) +
"    use_connect %s ; \n" % (conn) +
"    use_deform %s ; \n" % (deform)+
"    hide %s ; \n" % hide +
"    show_wire %s ; \n" % (wire) +
"    use_inherit_scale %s ; \n" % (scale) +
"    layers Array ")

	bit = 1
	for n in range(32):
		if layers & bit:
			fp.write("1 ")
		else:
			fp.write("0 ")
		bit = bit << 1

#"    use_cyclic_offset %s ; \n" % cyc +
#"    use_local_location %s ; \n" % lloc +
	fp.write(" ; \n" +
"    lock %s ; \n" % lock +
"    use_envelope_multiply False ; \n"+
"    hide_select %s ; \n" % (restr) +
"  end Bone \n")

def addBone24(bone, cond, roll, parent, flags, layers, bbone, fp):
	global rigHead, rigTail

	flags24 = 0
	if flags & F_CON:
		flags24 += 0x001
	if flags & F_DEF == 0:
		flags24 += 0x004
	if flags & F_NOSCALE:
		flags24 += 0x0e0

	fp.write("\n\tbone %s %s %x %x\n" % (bone, parent, flags24, layers))
	(x, y, z) = rigHead[bone]
	fp.write("    head  %.6g %.6g %.6g  ;\n" % (x,y,z))
	(x, y, z) = rigTail[bone]
	fp.write("    tail %.6g %.6g %.6g  ;\n" % (x,y,z))
	fp.write("    roll %.6g %.6g ; \n" % (roll, roll))
	fp.write("\tend bone\n")
	return

#
#	writeBoneGroups(fp):
#

BoneGroups = [
	('Master', 'THEME13'),
	('Spine', 'THEME05'),
	('FK_L', 'THEME09'),
	('FK_R', 'THEME02'),
	('IK_L', 'THEME03'),
	('IK_R', 'THEME04'),
]

def boneGroupIndex(grp):
	index = 1
	for (name, theme) in BoneGroups:
		if name == grp:
			return index
		index += 1
	raise NameError("Unknown bonegroup %s" % grp)

def writeBoneGroups(fp):
	for (name, theme) in BoneGroups:
		fp.write(
"    BoneGroup %s\n" % name +
"      name '%s' ;\n" % name +
"      color_set '%s' ;\n" % theme +
"    end BoneGroup\n")
	return


#
#	addIkHandle(fp, bone, customShape, limit):
#	addSingleIk(fp, bone, lockRot, target, limit):
#	addDeformLimb(fp, bone, ikBone, ikRot, fkBone, fkRot, cflags, pflags):
#	addDeformYBone(fp, bone, ikBone, fkBone, cflags, pflags):
#	addCSlider(fp, bone, mx):
#	addYSlider(fp, bone, mx):
#	addXSlider(fp, bone, mn, mx):
#

def addIkHandle(fp, bone, customShape, limit):
	if limit:
		cns = [('LimitDist', 0, 1, ['LimitDist', limit])]
	else:
		cns = []
	addPoseBone(fp, bone, customShape, None, (0,0,0), (1,1,1), (1,1,1), (1,1,1), 0, cns)

def addSingleIk(fp, bone, lockRot, target, limit):
	cns = [('IK', 0, 1, ['IK', target, 1, None, (True, False, True), 1.0])]
	if limit:
		cns.append( ('LimitRot', C_OW_LOCAL, 1, ['LimitRot', limit, (True, True, True)]) )
	addPoseBone(fp, bone, None, None, (1,1,1), lockRot, (1,1,1), (1,1,1), 0, cns)

def addDeformYBone(fp, bone, ikBone, fkBone, cflags, pflags):
	space = cflags & (C_OW_MASK + C_TG_MASK)
	constraints = [
		('CopyRot', space, 0, ['RotIKXZ', ikBone, (1,0,1), (0,0,0), False]),
		('CopyRot', space, 0, ['RotIKY', ikBone, (0,1,0), (0,0,0), False]),
		('CopyRot', space, 1, ['RotFKXZ', fkBone, (1,0,1), (0,0,0), False]),
		('CopyRot', space, 1, ['RotFKY', fkBone, (0,1,0), (0,0,0), False])
		]
	if pflags & P_STRETCH:
		constraints += [
		('CopyScale', 0, 0, ['StretchIK', ikBone, (0,1,0), False]),
		('CopyScale', 0, 1, ['StretchFK', fkBone, (0,1,0), False]),
		]		
	addPoseBone(fp, bone, None, None, (1,1,1), (0,0,0), (0,0,0), (1,1,1), 0, constraints)
	return

def addDeformLimb(fp, bone, ikBone, ikRot, fkBone, fkRot, cflags, pflags):
	space = cflags & (C_OW_MASK + C_TG_MASK)
	constraints = [
		('CopyRot', space, 0, ['RotIK', ikBone, ikRot, (0,0,0), False]),
		('CopyRot', space, 1, ['RotFK', fkBone, fkRot, (0,0,0), False])
		]
	if pflags & P_STRETCH:
		constraints += [
		('CopyScale', 0, 0, ['StretchIK', ikBone, (0,1,0), False]),
		('CopyScale', 0, 1, ['StretchFK', fkBone, (0,1,0), False]),
		]		
	(fX,fY,fZ) = fkRot
	addPoseBone(fp, bone, None, None, (1,1,1), (1-fX,1-fY,1-fZ), (0,0,0), (1,1,1), 0, constraints)
	return

def addDeformIK(fp, bone, target, pole):
	addPoseBone(fp, bone, None, None, (1,1,1), (0,0,0), (1,1,1), (1,1,1), 0, 
		[('IK', 0, 1, ['IK', target, 1, pole, (True, False,True)])])

def addDeformIK2(fp, bone, iktar, fktar, ikpole, fkpole):
	addPoseBone(fp, bone, None, None, (1,1,1), (0,0,0), (1,1,1), (1,1,1), 0, 
		[('IK', 0, 1, ['IK', iktar, 1, ikpole, (True, False,True)]),
		 ('IK', 0, 1, ['FK', fktar, 1, fkpole, (True, False,True)])])

def addStretchBone(fp, bone, target, parent):
	addPoseBone(fp, bone, None, None, (1,1,1), (1,1,1), (1,1,1), (1,1,1), P_STRETCH,
		[('StretchTo', 0, 1, ['Stretch', target, 0]),
 		 ('LimitScale', C_OW_LOCAL, 0, ['LimitScale', (0,0, 0,0, 0,0), (0,1,0)])])
	#addPoseBone(fp, target, None, None, (1,1,1), (1,1,1), (1,1,1), (1,1,1), 0,
 	#	[('LimitRot', C_OW_LOCAL, 1, ['LimitRot', (-deg90,deg90, 0,0, -deg90,deg90), (1,1,1)])])
	return

def addCSlider(fp, bone, mx):
	mn = "-"+mx
	addPoseBone(fp, bone, 'MHCube025', None, (0,1,0), (1,1,1), (1,1,1), (1,1,1), 0,
		[('LimitLoc', C_OW_LOCAL+C_LTRA, 1, ['Const', (mn,mx, '0','0', mn,mx), (1,1,1,1,1,1)])])
	
def addYSlider(fp, bone, mx):
	mn = "-"+mx
	addPoseBone(fp, bone, 'MHCube025', None, (1,1,0), (1,1,1), (1,1,1), (1,1,1), 0,
		[('LimitLoc', C_OW_LOCAL+C_LTRA, 1, ['Const', ('0','0', '0','0', mn,mx), (1,1,1,1,1,1)])])
	
def addXSlider(fp, bone, mn, mx, dflt):
	addPoseBone(fp, bone, 'MHCube025', None, ((0,1,1), (dflt,0,0)), (1,1,1), (1,1,1), (1,1,1), 0,
		[('LimitLoc', C_OW_LOCAL+C_LTRA, 1, ['Const', (mn,mx, '0','0', mn,mx), (1,1,1,1,1,1)])])

#
#	addPoseBone(fp, bone, customShape, boneGroup, locArg, lockRot, lockScale, ik_dof, flags, constraints):
#

def addPoseBone(fp, bone, customShape, boneGroup, locArg, lockRot, lockScale, ik_dof, flags, constraints):
	global BoneGroups, Mhx25

	try:
		(lockLoc, location) = locArg
	except:
		lockLoc = locArg
		location = (0,0,0)		
	
	(locX, locY, locZ) = location
	(lockLocX, lockLocY, lockLocZ) = lockLoc
	(lockRotX, lockRotY, lockRotZ) = lockRot
	(lockScaleX, lockScaleY, lockScaleZ) = lockScale
	(ik_dof_x, ik_dof_y, ik_dof_z) = ik_dof
	ikLockX = 1-ik_dof_x
	ikLockY = 1-ik_dof_y
	ikLockZ = 1-ik_dof_z

	ikLin = boolString(flags & P_IKLIN)
	ikRot = boolString(flags & P_IKROT)
	lkRot4 = boolString(flags & P_LKROT4)
	lkRotW = boolString(flags & P_LKROTW)
	hide = boolString(flags & P_HID)

	if Mhx25:
		fp.write("\n  Posebone %s %s \n" % (bone, True))
	else:
		# limitX = flags & 1
		# limitY = (flags >> 1) & 1
		# limitZ = (flags >> 2) & 1
		# lockXRot = (flags >> 3) & 1
		# lockYRot = (flags >> 4) & 1
		# lockZRot = (flags >> 5) & 1
		ikFlags = 8*lockRotX + 16*lockRotY + 32*lockRotZ
		fp.write("\tposebone %s %x \n" % (bone, ikFlags))
		if customShape:
			fp.write("\t\tdisplayObject _object['%s'] ;\n" % customShape)
		
	if boneGroup:
		index = boneGroupIndex(boneGroup)
		fp.write("    bone_group Refer BoneGroup %s ;\n" % boneGroup)

	(usex,usey,usez) = (0,0,0)
	(xmin, ymin, zmin) = (-pi, -pi, -pi)
	(xmax, ymax, zmax) = (pi, pi, pi)

	for (label, cflags, inf, data) in constraints:
		if type(label) == str:
			typ = label
			switch = True
		else:
			(typ, switch) = label

		if typ == 'IK':
			addIkConstraint(fp, switch, cflags, inf, data, lockLoc, lockRot)
		elif typ == 'Action':
			addActionConstraint(fp, switch, cflags, inf, data)
		elif typ == 'CopyLoc':
			addCopyLocConstraint(fp, switch, cflags, inf, data)
		elif typ == 'CopyRot':
			addCopyRotConstraint(fp, switch, cflags, inf, data)
		elif typ == 'CopyScale':
			addCopyScaleConstraint(fp, switch, cflags, inf, data)
		elif typ == 'CopyTrans':
			addCopyTransConstraint(fp, switch, cflags, inf, data)
		elif typ == 'LimitRot':
			addLimitRotConstraint(fp, switch, cflags, inf, data)
			(xmin, xmax, ymin, ymax, zmin, zmax) = data[1]
			(usex,usey,usez) = data[2]			
		elif typ == 'LimitLoc':
			addLimitLocConstraint(fp, switch, cflags, inf, data)
		elif typ == 'LimitScale':
			addLimitScaleConstraint(fp, switch, cflags, inf, data)
		elif typ == 'Transform':
			addTransformConstraint(fp, switch, cflags, inf, data)
		elif typ == 'DampedTrack':
			addDampedTrackConstraint(fp, switch, cflags, inf, data)
		elif typ == 'StretchTo':
			addStretchToConstraint(fp, switch, cflags, inf, data)
		elif typ == 'LimitDist':
			addLimitDistConstraint(fp, switch, cflags, inf, data)
		elif typ == 'ChildOf':
			addChildOfConstraint(fp, switch, cflags, inf, data)
		elif typ == 'SplineIK':
			addSplineIkConstraint(fp, switch, cflags, inf, data)
		else:
			print(label)
			print(typ)
			print(switch)
			raise NameError("Unknown constraint type %s" % typ)

	if not Mhx25:
		fp.write("\tend posebone\n")
		return
	
	fp.write(
"    lock_ik_x %d ;\n" % ikLockX +
"    lock_ik_y %d ;\n" % ikLockY +
"    lock_ik_z %d ;\n" % ikLockZ +
"    use_ik_limit_x %d ;\n" % usex +
"    use_ik_limit_y %d ;\n" % usey +
"    use_ik_limit_z %d ;\n" % usez +
"    ik_stiffness Array 0.0 0.0 0.0  ; \n")
	fp.write(
"    ik_max Array %.4f %.4f %.4f ; \n" % (xmax, ymax, zmax) +
"    ik_min Array %.4f %.4f %.4f ; \n" % (xmin, ymin, zmin))

	if customShape:
		fp.write("    custom_shape Refer Object %s ; \n" % customShape)

	rotMode = flags & P_ROTMODE
	if rotMode == P_XYZ:
		fp.write("  rotation_mode 'XYZ' ;\n")

	fp.write(
"    use_ik_linear_control %s ; \n" % ikLin +
"    ik_linear_weight 0 ; \n"+
"    use_ik_rotation_control %s ; \n" % ikRot +
"    ik_rotation_weight 0 ; \n" +
"    hide %s ; \n" % hide)
	
	if flags & P_STRETCH:
		fp.write(
"#if toggle&T_STRETCH\n" +
"    ik_stretch 0.1 ; \n" +
"#endif\n")
	else:
		fp.write("    ik_stretch 0 ; \n")

	fp.write(
"    location Array %.3f %.3f %.3f ; \n" % (locX, locY, locZ) +
"    lock_location Array %d %d %d ;\n"  % (lockLocX, lockLocY, lockLocZ)+
"    lock_rotation Array %d %d %d ;\n"  % (lockRotX, lockRotY, lockRotZ)+
"    lock_rotation_w %s ; \n" % lkRotW +
"    lock_rotations_4d %s ; \n" % lkRot4 +
"    lock_scale Array %d %d %d  ; \n" % (lockScaleX, lockScaleY, lockScaleZ)+
"  end Posebone \n")
	return

#
#	addIkConstraint(fp, switch, flags, inf, data, lockLoc, lockRot)
#
def addIkConstraint(fp, switch, flags, inf, data, lockLoc, lockRot):
	global Mhx25
	name = data[0]
	subtar = data[1]
	chainlen = data[2]
	pole = data[3]
	(useLoc, useRot, useStretch) = data[4]
	(ownsp, targsp, active, expanded) = constraintFlags(flags)
	(lockLocX, lockLocY, lockLocZ) = lockLoc
	(lockRotX, lockRotY, lockRotZ) = lockRot

	if Mhx25:
		fp.write(
"    Constraint %s IK %s\n" % (name, switch))

		if subtar:
			fp.write(
"      target Refer Object %s ;\n" % mh2mhx.theHuman +
"      subtarget '%s' ;\n" % subtar +
"      target_space '%s' ;\n" % targsp +
"      use_tail True ;\n" +
"      use_target True ;\n")
		else:
			fp.write(
"      use_tail False ;\n" +
"      use_target True ;\n")

		fp.write(
"      pos_lock Array 1 1 1  ;\n" +
"      rot_lock Array 1 1 1  ;\n" +
"      active %s ;\n" % active +
"      show_expanded %s ;\n" % expanded +
"      reference_axis 'BONE' ;\n" +
"      chain_count %d ;\n" % chainlen +
"      ik_type 'COPY_POSE' ;\n" +
"      influence %s ;\n" % inf +
"      iterations 500 ;\n" +
"      limit_mode 'LIMITDIST_INSIDE' ;\n" +
"      orient_weight 1 ;\n" +
"      owner_space '%s' ;\n" % ownsp)

		if pole:
			(angle, ptar) = pole
			fp.write(
"      pole_angle %.6g ;\n" % angle +
"      pole_subtarget '%s' ;\n" % ptar +
"      pole_target Refer Object %s ;\n" % mh2mhx.theHuman)

		fp.write(
"      is_proxy_local False ;\n" +
"      use_location %s ;\n" % useLoc +
"      use_rotation %s ;\n" % useRot +
"      use_stretch %s ;\n" % useStretch +
"      weight 1 ;\n" +
"    end Constraint\n")

	else:
		fp.write("\t\tconstraint IKSOLVER %s 1.0 \n" % name)
		fp.write(
"\t\t\tCHAINLEN	int %d ; \n" % chainlen +
"\t\t\tTARGET	obj Human ; \n" +
"\t\t\tBONE	str %s ; \n" % subtar +
"\t\tend constraint\n")

	return

#
#	addActionConstraint(fp, switch, flags, inf, data):
#
def addActionConstraint(fp, switch, flags, inf, data):
	global Mhx25
	name = data[0]
	action = data[1]
	subtar = data[2]
	channel = data[3]
	(sframe, eframe) = data[4]
	(amin, amax) = data[5]
	inf = data[6]
	(ownsp, targsp, active, expanded) = constraintFlags(flags)

	fp.write(
"    Constraint %s ACTION %s\n" % (name, switch) +
"      target Refer Object %s ; \n" % mh2mhx.theHuman+
"      action Refer Action %s ; \n" % action+
"      active %s ;\n" % active +
"      show_expanded %s ;\n" % expanded +
"      frame_start %s ; \n" % sframe +
"      frame_end %d ; \n" % eframe+
"      influence %s ; \n" % inf)

	if channel[0:3] == 'LOC':
		fp.write(
"      maximum %.4f*theScale ; \n" % amax +
"      minimum %.4f*theScale ; \n" % amin)
	else:
		fp.write(
"      maximum %.4f ; \n" % amax +
"      minimum %.4f ; \n" % amin)
	
	fp.write(
"      owner_space '%s' ; \n" % ownsp +
"      is_proxy_local False ; \n"+
"      subtarget '%s' ; \n" % subtar +
"      target_space '%s' ; \n" % targsp +
"      transform_channel '%s' ;\n" % channel +
"    end Constraint \n")
	return

#
#	addCopyRotConstraint(fp, switch, flags, inf, data):
#
def addCopyRotConstraint(fp, switch, flags, inf, data):
	global Mhx25
	name = data[0]
	subtar = data[1]
	(useX, useY, useZ) = data[2]
	(invertX, invertY, invertZ) = data[3]
	useOffs = data[4]
	(ownsp, targsp, active, expanded) = constraintFlags(flags)

	if Mhx25:
		fp.write(
"    Constraint %s COPY_ROTATION %s\n" % (name, switch) +
"      target Refer Object %s ; \n" % mh2mhx.theHuman+
"      invert Array %d %d %d ; \n" % (invertX, invertY, invertZ)+
"      use Array %d %d %d  ; \n" % (useX, useY, useZ)+
"      active %s ;\n" % active +
"      show_expanded %s ;\n" % expanded +
"      influence %s ; \n" % inf +
"      owner_space '%s' ; \n" % ownsp+
"      is_proxy_local False ; \n"+
"      subtarget '%s' ;\n" % subtar +
"      target_space '%s' ; \n" % targsp+
"      use_offset %s ; \n" % useOffs +
"    end Constraint \n")

	else:
		copy = useX + 2*useY + 4*useZ
		fp.write(
"\t\tconstraint COPYROT %s 1.0 \n" % name +
"\t\t\tTARGET	obj Human ;\n" +
"\t\t\tBONE	str %s ; \n" % subtar +
"\t\t\tCOPY	hex %x ;\n" %  copy +
"\t\tend constraint\n")
	return

#
#	addCopyLocConstraint(fp, switch, flags, inf, data):
#
def addCopyLocConstraint(fp, switch, flags, inf, data):
	global Mhx25
	name = data[0]
	subtar = data[1]
	(useX, useY, useZ) = data[2]
	(invertX, invertY, invertZ) = data[3]
	useOffs = data[4]
	(ownsp, targsp, active, expanded) = constraintFlags(flags)

	if Mhx25:
		fp.write(
"    Constraint %s COPY_LOCATION %s\n" % (name, switch) +
"      target Refer Object %s ; \n" % mh2mhx.theHuman+
"      invert Array %d %d %d ; \n" % (invertX, invertY, invertZ)+
"      use Array %d %d %d  ; \n" % (useX, useY, useZ)+
"      active %s ;\n" % active +
"      show_expanded %s ;\n" % expanded +
"      influence %s ; \n" % inf +
"      owner_space '%s' ; \n" % ownsp +
"      is_proxy_local False ; \n"+
"      subtarget '%s' ;\n" % subtar +
"      target_space '%s' ; \n" % targsp+
"      use_offset %s ; \n" % useOffs +
"    end Constraint \n")

	else:
		fp.write(
"\t\tconstraint COPYLOC %s 1.0 \n" % name +
"\t\t\tTARGET	obj Human ;\n" +
"\t\t\tBONE	str %s ; \n" % subtar +
"\t\tend constraint\n")
	return

#
#	addCopyScaleConstraint(fp, switch, flags, inf, data):
#
def addCopyScaleConstraint(fp, switch, flags, inf, data):
	global Mhx25
	name = data[0]
	subtar = data[1]
	(useX, useY, useZ) = data[2]
	useOffs = data[3]
	(ownsp, targsp, active, expanded) = constraintFlags(flags)

	fp.write(
"    Constraint %s COPY_SCALE %s\n" % (name, switch) +
"      target Refer Object %s ;\n" % mh2mhx.theHuman +
"      use Array %d %d %d  ; \n" % (useX, useY, useZ)+
"      active %s ;\n" % active +
"      show_expanded %s ;\n" % expanded +
"      influence %s ;\n" % inf +
"      owner_space '%s' ;\n" % ownsp +
"      is_proxy_local False ;\n" +
"      subtarget '%s' ;\n" % subtar +
"      target_space '%s' ;\n" % targsp +
"      use_offset %s ;\n" % useOffs +
"    end Constraint\n")
	return

#
#	addCopyTransConstraint(fp, switch, flags, inf, data):
#
def addCopyTransConstraint(fp, switch, flags, inf, data):
	global Mhx25
	name = data[0]
	subtar = data[1]
	inf = data[2]
	(ownsp, targsp, active, expanded) = constraintFlags(flags)
	
	fp.write(
"    Constraint %s COPY_TRANSFORMS\n" % (name, switch) +
"      target Refer Object %s ;\n" % mh2mhx.theHuman +
"      active %s ;\n" % active +
"      show_expanded %s ;\n" % expanded +
"      influence %s ;\n" % inf +
"      owner_space '%s' ;\n" % ownsp +
"      is_proxy_local False ;\n" +
"      subtarget '%s' ;\n" % subtar +
"      target_space '%s' ;\n" % targsp +
"    end Constraint\n")
	return

#
#	addLimitRotConstraint(fp, switch, flags, inf, data):
#
def addLimitRotConstraint(fp, switch, flags, inf, data):
	global Mhx25
	name = data[0]
	(xmin, xmax, ymin, ymax, zmin, zmax) = data[1]
	(usex, usey, usez) = data[2]
	(ownsp, targsp, active, expanded) = constraintFlags(flags)
	ltra = boolString(flags & C_LTRA == 0)
	
	if Mhx25:
		fp.write(	
"    Constraint %s LIMIT_ROTATION %s\n" % (name, switch) +
"      active %s ;\n" % active +
"      show_expanded %s ;\n" % expanded +
"      influence %s ; \n" % inf +
"      use_transform_limit %s ; \n" % ltra+
"      max_x %.6g ;\n" % xmax +
"      max_y %.6g ;\n" % ymax +
"      max_z %.6g ;\n" % zmax +
"      min_x %.6g ;\n" % xmin +
"      min_y %.6g ;\n" % ymin +
"      min_z %.6g ;\n" % zmin +
"      owner_space '%s' ; \n" % ownsp+
"      is_proxy_local False ; \n"+
"      target_space '%s' ; \n" % targsp+
"      use_limit_x %s ; \n" % usex +
"      use_limit_y %s ; \n" % usey +
"      use_limit_z %s ; \n" % usez +
"   end Constraint \n")

	else:
		limit = usex + 2*usey + 4*usez
		fp.write(
"\t\tconstraint LIMITROT Const 1.0 \n" +
"\t\t\tLIMIT	hex %x ;\n" % limit +
"\t\t\tOWNERSPACE       hex 1 ;\n" +
"\t\t\tXMIN       float %g ; \n" % xmin +
"\t\t\tXMAX       float %g ; \n" % xmax +
"\t\t\tYMIN       float %g ; \n" % ymin +
"\t\t\tYMAX       float %g ; \n" % ymax +
"\t\t\tZMIN       float %g ; \n" % zmin +
"\t\t\tZMAX       float %g ; \n" % zmax +
"\t\tend constraint\n")
	return

#
#	addLimitLocConstraint(fp, switch, flags, inf, data):
#
def addLimitLocConstraint(fp, switch, flags, inf, data):
	global Mhx25
	name = data[0]
	(xmin, xmax, ymin, ymax, zmin, zmax) = data[1]
	(useminx, usemaxx, useminy, usemaxy, useminz, usemaxz) = data[2]
	(ownsp, targsp, active, expanded) = constraintFlags(flags)
	
	if Mhx25:
		fp.write(
"    Constraint %s LIMIT_LOCATION %s\n" % (name, switch) +
"      active %s ;\n" % active +
"      show_expanded %s ;\n" % expanded +
"      influence %s ;\n" % inf +
"      use_transform_limit True ;\n" +
"      max_x %s*theScale ;\n" % xmax +
"      max_y %s*theScale ;\n" % ymax +
"      max_z %s*theScale ;\n" % zmax +
"      min_x %s*theScale ;\n" % xmin +
"      min_y %s*theScale ;\n" % ymin +
"      min_z %s*theScale ;\n" % zmin +
"      owner_space '%s' ;\n" % ownsp +
"      is_proxy_local False ;\n" +
"      target_space '%s' ;\n" % targsp +
"      use_max_x %s ;\n" % usemaxx +
"      use_max_y %s ;\n" % usemaxy +
"      use_max_z %s ;\n" % usemaxz +
"      use_min_x %s ;\n" % useminx +
"      use_min_y %s ;\n" % useminy +
"      use_min_z %s ;\n" % useminz +
"    end Constraint\n")

	else:
		limit = useminx + 2*useminy + 4*useminz + 8*usemaxx + 16*usemaxy + 32*usemaxz
		fp.write("\t\tconstraint LIMITLOC Const 1.0 \n")
		fp.write(
"\t\t\tLIMIT	hex %x ;\n" % limit +
"\t\t\tOWNERSPACE       hex 1 ;\n" +
"\t\t\tXMIN       float %g ; \n" % xmin +
"\t\t\tXMAX       float %g ; \n" % xmax +
"\t\t\tYMIN       float %g ; \n" % ymin +
"\t\t\tYMAX       float %g ; \n" % ymax +
"\t\t\tZMIN       float %g ; \n" % zmin +
"\t\t\tZMAX       float %g ; \n" % zmax +
"\t\tend constraint\n")

	return

#
#	addLimitScaleConstraint(fp, switch, flags, inf, data):
#
def addLimitScaleConstraint(fp, switch, flags, inf, data):
	global Mhx25
	name = data[0]
	(xmin, xmax, ymin, ymax, zmin, zmax) = data[1]
	(usex, usey, usez) = data[2]
	(ownsp, targsp, active, expanded) = constraintFlags(flags)
	
	if Mhx25:
		fp.write(
"    Constraint %s LIMIT_SCALE %s\n" % (name, switch) +
"      active %s ;\n" % active +
"      show_expanded %s ;\n" % expanded +
"      influence %s ;\n" % inf +
"      use_transform_limit True ;\n" +
"      max_x %.6g ;\n" % xmax +
"      max_y %.6g ;\n" % ymax +
"      max_z %.6g ;\n" % zmax +
"      min_x %.6g ;\n" % xmin +
"      min_y %.6g ;\n" % ymin +
"      min_z %.6g ;\n" % zmin +
"      owner_space '%s' ;\n" % ownsp +
"      is_proxy_local False ;\n" +
"      target_space '%s' ;\n" % targsp +
"      use_max_x %s ;\n" % usex +
"      use_max_y %s ;\n" % usey +
"      use_max_z %s ;\n" % usez +
"      use_min_x %s ;\n" % usex +
"      use_min_y %s ;\n" % usey +
"      use_min_z %s ;\n" % usez +
"    end Constraint\n")
	return

#
#	addTransformConstraint(fp, switch, flags, inf, data):
#
def addTransformConstraint(fp, switch, flags, inf, data):
	global Mhx25
	name = data[0]
	subtar = data[1]
	map_from = data[2]
	from_min = data[3]
	from_max = data[4]
	map_to_from = data[5]
	map_to = data[6]
	to_min = data[7]
	to_max = data[8]
	(ownsp, targsp, active, expanded) = constraintFlags(flags)

	fp.write(
"    Constraint %s TRANSFORM %s\n" % (name, switch) +
"      target Refer Object %s ;\n" % mh2mhx.theHuman +
"      active %s ;\n" % active +
"      show_expanded %s ;\n" % expanded +
"      influence %s ;\n" % inf +
"      use_motion_extrapolate 0 ;\n" +
"      owner_space '%s' ;\n" % ownsp+
"      is_proxy_local False ;\n" +
"      subtarget '%s' ;\n" % subtar +
"      target_space '%s' ;\n" % targsp+
"      map_from '%s' ;\n" % map_from + 
"      from_min_x %s ;\n" % from_min[0] + 
"      from_min_y %s ;\n" % from_min[1] + 
"      from_min_z %s ;\n" % from_min[2] + 
"      from_max_x %s ;\n" % from_max[0] + 
"      from_max_y %s ;\n" % from_max[1] + 
"      from_max_z %s ;\n" % from_max[2] + 
"      map_to '%s' ;\n" % map_to + 
"      map_to_x_from '%s' ;\n" % map_to_from[0] +
"      map_to_y_from '%s' ;\n" % map_to_from[1] +
"      map_to_z_from '%s' ;\n" % map_to_from[2] +
"      to_min_x %s ;\n" % to_min[0] + 
"      to_min_y %s ;\n" % to_min[1] + 
"      to_min_z %s ;\n" % to_min[2] + 
"      to_max_x %s ;\n" % to_max[0] + 
"      to_max_y %s ;\n" % to_max[1] + 
"      to_max_z %s ;\n" % to_max[2] + 
"    end Constraint\n")
	return

#
#	addDampedTrackConstraint(fp, switch, flags, inf, data):
#
def addDampedTrackConstraint(fp, switch, flags, inf, data):
	global Mhx25
	name = data[0]
	subtar = data[1]
	track = data[2]
	(ownsp, targsp, active, expanded) = constraintFlags(flags)

	fp.write(
"    Constraint %s DAMPED_TRACK %s\n" % (name, switch) +
"      target Refer Object %s ;\n" % mh2mhx.theHuman +
"      active %s ;\n" % active +
"      show_expanded %s ;\n" % expanded +
"      influence %s ;\n" % inf +
"      owner_space '%s' ;\n" % ownsp+
"      is_proxy_local False ;\n" +
"      subtarget '%s' ;\n" % subtar +
"      target_space '%s' ;\n" % targsp+
"      track '%s' ;\n" % track + 
"    end Constraint\n")
	return

#
#	addStretchToConstraint(fp, switch, flags, inf, data):
#
def addStretchToConstraint(fp, switch, flags, inf, data):
	global Mhx25
	name = data[0]
	subtar = data[1]
	head_tail = data[2]
	(ownsp, targsp, active, expanded) = constraintFlags(flags)
	if flags & C_STRVOL:
		volume = 'VOLUME_XZX'
	else:
		volume = 'NO_VOLUME'
	if flags & C_PLANEZ:
		axis = 'PLANE_Z'
	else:
		axis = 'PLANE_X'

	if Mhx25:
		fp.write(
"    Constraint %s STRETCH_TO %s\n" % (name, switch) +
"      target Refer Object %s ;\n" % mh2mhx.theHuman +
"      active %s ;\n" % active +
"      show_expanded %s ;\n" % expanded +
"      bulge 1 ;\n" +
"      head_tail %s ;\n" % head_tail +
"      influence %s ;\n" % inf +
"      keep_axis '%s' ;\n" % axis +
"      owner_space '%s' ;\n" % ownsp+
"      is_proxy_local False ;\n" +
"      subtarget '%s' ;\n" % subtar +
"      target_space '%s' ;\n" % targsp+
"      volume '%s' ;\n" % volume +
"    end Constraint\n")

	else:
		fp.write(
"\t\tconstraint STRETCHTO %s 1.0 \n" % name +
"\t\t\tTARGET	obj Human ;\n" +
"\t\t\tBONE	str %s ;\n" % subtar +
"\t\t\tPLANE	hex 2 ;\n" +
"\t\tend constraint\n")
	return

#
#	addLimitDistConstraint(fp, switch, flags, inf, data):
#
def addLimitDistConstraint(fp, switch, flags, inf, data):
	global Mhx25
	name = data[0]
	subtar = data[1]
	(ownsp, targsp, active, expanded) = constraintFlags(flags)

	if Mhx25:
		fp.write(
"    Constraint %s LIMIT_DISTANCE %s\n" % (name, switch) +
"      target Refer Object %s ;\n" % mh2mhx.theHuman +
"      active %s ;\n" % active +
"      show_expanded %s ;\n" % expanded +
"      influence %s ;\n" % inf +
"      limit_mode 'LIMITDIST_INSIDE' ;\n" +
"      owner_space '%s' ;\n" % ownsp +
"      is_proxy_local False ;\n" +
"      subtarget '%s' ;\n" % subtar +
"      target_space '%s' ;\n" % targsp+
"    end Constraint\n")

	else:
		fp.write(
"\t\tconstraint LIMITDIST %s 1.0 \n" % name +
"\t\t\tTARGET	obj Human ;\n" +
"\t\t\tBONE	str %s ;\n" % subtar +
"\t\tend constraint\n")
	return

#
#	addChildOfConstraint(fp, switch, flags, inf, data):
#
def addChildOfConstraint(fp, switch, flags, inf, data):
	global Mhx25
	# return
	name = data[0]
	subtar = data[1]
	(locx, locy, locz) = data[2]
	(rotx, roty, rotz) = data[3]
	(scalex, scaley, scalez) = data[4]
	(ownsp, targsp, active, expanded) = constraintFlags(flags)

	#ownsp = 'WORLD'
	#targsp = 'WORLD'

	if Mhx25:
		fp.write(
"    Constraint %s CHILD_OF %s\n" % (name, switch) +
"      target Refer Object %s ;\n" % mh2mhx.theHuman +
"      active %s ;\n" % active +
"      show_expanded %s ;\n" % expanded +
"      influence %s ;\n" % inf +
"      owner_space '%s' ;\n" % ownsp +
"      is_proxy_local False ;\n" +
"      subtarget '%s' ;\n" % subtar +
"      target_space '%s' ;\n" % targsp +
"      use_location_x %s ;\n" % locx +
"      use_location_y %s ;\n" % locy +
"      use_location_z %s ;\n" % locz +
"      use_rotation_x %s ;\n" % rotx +
"      use_rotation_y %s ;\n" % roty +
"      use_rotation_z %s ;\n" % rotz +
"      use_scale_x %s ;\n" % scalex +
"      use_scale_y %s ;\n" % scaley +
"      use_scale_z %s ;\n" % scalez +
"    end Constraint\n" +
"    bpyops constraint.childof_set_inverse(constraint='%s',owner='BONE') ;\n" % name)
	return

#
#	addSplineIkConstraint(fp, switch, flags, inf, data):
#
def addSplineIkConstraint(fp, switch, flags, inf, data):
	global Mhx25
	# return
	name = data[0]
	subtar = data[1]
	(locx, locy, locz) = data[2]
	(rotx, roty, rotz) = data[3]
	(scalex, scaley, scalez) = data[4]
	(ownsp, targsp, active, expanded) = constraintFlags(flags)

	fp.write(
"    Constraint %s SPLINE_IK\n" % name +
"      active %s ;\n" % active +
"      chain_count 1 ;\n" +
"      error_location 0 ;\n" +
"      error_rotation 0 ;\n" +
"      influence %s ;\n" % inf +
"      is_proxy_local False ;\n" +
"      is_valid False ;\n" +
"      joint_bindings ['bpy_prop_array'] <bpy_float[0], SplineIKConstraint.joint_bindings> \n" +
"      owner_space '%s' ;\n" % ownsp +
"      show_expanded %s ;\n" % targsp +
"      target_space '%s' ;\n" % tarsp +
"      use_chain_offset False ;\n" +
"      use_curve_radius True ;\n" +
"      use_even_divisions False ;\n" +
"      use_y_stretch True ;\n" +
"      xz_scale_mode 'NONE' ;\n" +
"    end Constraint\n")
	return

#
#	constraintFlags(flags):
#
def constraintFlags(flags):
	ow = flags & C_OW_MASK
	if ow == 0:
		ownsp = 'WORLD'
	elif ow == C_OW_LOCAL:
		ownsp = 'LOCAL'
	elif ow == C_OW_LOCPAR:
		ownsp = 'LOCAL_WITH_PARENT'
	elif ow == C_OW_POSE:
		ownsp = 'POSE'

	tg = flags & C_TG_MASK
	if tg == 0:
		targsp = 'WORLD'
	elif tg == C_TG_LOCAL:
		targsp = 'LOCAL'
	elif tg == C_TG_LOCPAR:
		targsp = 'LOCAL_WITH_PARENT'
	elif tg == C_TG_POSE:
		targsp = 'POSE'

	active = boolString(flags & C_ACT == 0)
	expanded = boolString(flags & C_EXP)
	return (ownsp, targsp, active, expanded)

#
#	writeAction(fp, cond, name, action, lr, ikfk):
#	writeFCurves(fp, name, (x01, y01, z01, w01), (x21, y21, z21, w21)):
#

def writeAction(fp, cond, name, action, lr, ikfk):
	fp.write("Action %s %s\n" % (name,cond))
	if ikfk:
		iklist = ["IK", "FK"]
	else:
		iklist = [""]
	if lr:
		for (bone, quats) in action:
			rquats = []
			for (t,x,y,z,w) in rquats:
				rquats.append((t,x,y,-z,-w))
			for ik in iklist:
				writeFCurves(fp, "%s%s_L" % (bone, ik), quats)
				writeFCurves(fp, "%s%s_R" % (bone, ik), rquats)
	else:
		for (bone, quats) in action:
			for ik in iklist:
				writeFCurves(fp, "%s%s" % (bone, ik), quats)
	fp.write("end Action\n\n")
	return

def writeFCurves(fp, name, quats):
	n = len(quats)
	for index in range(4):
		fp.write("\n" +
"  FCurve pose.bones[\"%s\"].rotation_quaternion %d\n" % (name, index))
		for m in range(n):
			t = quats[m][0]
			x = quats[m][index+1]
			fp.write("    kp %d %.4g ;\n" % (t,x))
		fp.write(
"    extrapolation 'CONSTANT' ;\n" +
"  end FCurve \n")
	return

#
#	writeFkIkSwitch(fp, drivers)
#

def writeFkIkSwitch(fp, drivers):
	for (bone, cond, cnsFK, cnsIK, targ, channel, mx) in drivers:
		cnsData = ("ik", 'TRANSFORMS', [(mh2mhx.theHuman, targ, channel, C_LOC)])
		for cnsName in cnsFK:
			writeDriver(fp, cond, 'AVERAGE', "", "pose.bones[\"%s\"].constraints[\"%s\"].influence" % (bone, cnsName), -1, (mx,-mx), [cnsData])
		for cnsName in cnsIK:
			writeDriver(fp, cond, 'AVERAGE', "", "pose.bones[\"%s\"].constraints[\"%s\"].influence" % (bone, cnsName), -1, (0,mx), [cnsData])

#
#	writeEnumDrivers(fp, drivers):
#

def writeEnumDrivers(fp, drivers):
	for (bone, cns, targ, channel) in drivers:
		drvVars = [("x", 'TRANSFORMS', [(mh2mhx.theHuman, targ, channel, C_LOC)])]
		for n, cnsName in enumerate(cns):
			expr = '(x>%.1f)*(x<%.1f)' % (n-0.5, n+0.5)
			writeDriver(fp, True, ('SCRIPTED', expr), "","pose.bones[\"%s\"].constraints[\"%s\"].influence" % (bone, cnsName), -1, (0,1), drvVars)

#
#	writeProperties(fp, props):
#	writePropDrivers(fp, drivers):
#

def defineProperties(fp, props):
	for (prop, typ, values, options) in props:
		if typ == 'Enum':
			#fp.write("DefineProperty %s Int min=1 max=%d ;\n" % (prop, len(values)))
			#continue
			fp.write("DefineProperty %s Enum " % prop)
			c = 'items=['
			for val in values:
				fp.write("%s('%s','%s','%s')" % (c,val,val,val))
				c = ','
			fp.write("]")
		else:
			fp.write("DefineProperty %s %s" % (prop, typ))
		for option in options:
			fp.write(" %s" % option)
		fp.write(" ;\n")
	return

def writeProperties(fp, props):
	for (prop, typ, values, options) in props:
		if typ == 'Enum':
			#val = values[0]
			#fp.write("  Property %s '%s' ;\n" % (prop, val))
			fp.write("  Property %s 0 ;\n" % (prop))
		else:
			pass
			fp.write("  Property %s %s ;\n" % (prop, values))
	return

def writePropDrivers(fp, drivers):
	for (bone, prop, typ, constraints) in drivers:
		drvVars = [("x", 'SINGLE_PROP', [(mh2mhx.theHuman, prop)])]
		for n, cns in enumerate(constraints):
			if typ == 'Enum':
				expr = '(x==%d)' % n
				#expr = '(x=="%s")*1' % cns
			elif typ == 'Bool':
				expr = 'x'
			writeDriver(fp, True, ('SCRIPTED', expr), "","pose.bones[\"%s\"].constraints[\"%s\"].influence" % (bone, cns), -1, (0,1), drvVars)

#
#	writeTextureDrivers(fp, drivers):
#

def writeTextureDrivers(fp, drivers):
	for (tex, vlist) in drivers.items():
		drvVars = []
		(texnum, targ, channel, coeff) = vlist
		drvVars.append( (targ, 'TRANSFORMS', [(mh2mhx.theHuman, targ, channel, C_LOC)]) )
		writeDriver(fp, 'toggle&T_Face', 'AVERAGE', "", "texture_slots[%d].normal_factor" % (texnum), -1, coeff, drvVars)
	return

#
#	writeShapeDrivers(fp, drivers):
# 'BrowsMidDown' : [('PBrows', 'LOC_Z', (0,K), 0, fullScale)]
#

def writeShapeDrivers(fp, drivers, proxy):
	for (shape, vlist) in drivers.items():
		if mh2mhx.useThisShape(shape, proxy):
			drvVars = []
			(targ, channel, coeff) = vlist
			drvVars.append( (targ, 'TRANSFORMS', [(mh2mhx.theHuman, targ, channel, C_LOC)]) )
			writeDriver(fp, 'toggle&T_Face', 'AVERAGE', "", "keys[\"%s\"].value" % (shape), -1, coeff, drvVars)
	return

#
#	writeDeformDrivers(fp, drivers):
# 	("LegForward_L", "StretchTo", expr, [("f", "UpLegDwn_L", "BendLegForward_L")], [(0,1), (deg30,1), (deg45,0)])
#

def writeDeformDrivers(fp, drivers):
	for (bone, cnsName, expr, targs, keypoints)  in drivers:
		drvVars = []
		if expr:
			drvdata = ('SCRIPTED', expr)
		else:
			drvdata = 'MIN'
		for (var, targ1, targ2) in targs:
			drvVars.append( (var, 'ROTATION_DIFF', [(mh2mhx.theHuman, targ1, C_LOC), (mh2mhx.theHuman, targ2, C_LOC)]) )
		writeDriver(fp, True, drvdata, "","pose.bones[\"%s\"].constraints[\"%s\"].influence" % (bone, cnsName), -1, keypoints, drvVars)
	return


#
#	writeRotDiffDrivers(fp, drivers, proxy):
#

def writeRotDiffDrivers(fp, drivers, proxy):
	for (shape, vlist) in drivers.items():
		if mh2mhx.useThisShape(shape, proxy):
			(targ1, targ2, keypoints) = vlist
			drvVars = [(targ2, 'ROTATION_DIFF', [
			(mh2mhx.theHuman, targ1, C_LOC),
			(mh2mhx.theHuman, targ2, C_LOC)] )]
			writeDriver(fp, True, 'MIN', "", "keys[\"%s\"].value" % (shape), -1, keypoints, drvVars)
	return

#
#	writeDrivers(fp, cond, drivers):
#

def writeDrivers(fp, cond, drivers):
	for drv in drivers:
		(bone, typ, name, index, coeffs, variables) = drv
		if typ == 'INFL':
			writeDriver(fp, cond, 'AVERAGE', "", "pose.bones[\"%s\"].constraints[\"%s\"].influence" % (bone, name), index, coeffs, variables)
		elif typ == 'ROTE':
			writeDriver(fp, cond, 'AVERAGE', "", "pose.bones[\"%s\"].rotation_euler" % bone, index, coeffs, variables)
		elif typ == 'ROTQ':
			writeDriver(fp, cond, 'AVERAGE', "", "pose.bones[\"%s\"].rotation_quaternion" % bone, index, coeffs, variables)
		elif typ == 'LOC':
			writeDriver(fp, cond, 'AVERAGE', "*theScale", "pose.bones[\"%s\"].location" % bone, index, coeffs, variables)
		elif typ == 'SCALE':
			writeDriver(fp, cond, 'AVERAGE', "", "pose.bones[\"%s\"].scale" % bone, index, coeffs, variables)
		else:
			print drv
			raise NameError("Unknown driver type %s" % typ)

#
#	writeDriver(fp, cond, drvdata, extra, channel, index, coeffs, variables):
#

def writeDriver(fp, cond, drvdata, extra, channel, index, coeffs, variables):
	useLoc = False
	useKeypoints = False
	useMod = False
	try:
		(drvtype, expr) = drvdata
	except:
		drvtype = drvdata

	fp.write("\n"+
"    FCurve %s %d %s\n" % (channel, index, cond) +
"      Driver %s\n" % drvtype )

	if drvtype == 'SCRIPTED':
		fp.write("        expression '%s' ;\n" % expr)

	for (var, typ, targets) in variables:
		fp.write("        DriverVariable %s %s\n" % (var,typ))

		if typ == 'TRANSFORMS':
			useMod = True
			for (targ, boneTarg, ttype, flags) in targets:
				if ttype[0:3] == 'LOC':
					useLoc = True
				local = boolString(flags & C_LOC)
				fp.write(
"          Target %s OBJECT\n" % targ +
"            transform_type '%s' ;\n" % ttype +
"            bone_target '%s' ;\n" % boneTarg +
"            use_local_space_transform %s ;\n" % local +
"          end Target\n")

		elif typ == 'ROTATION_DIFF':
			useKeypoints = True
			for (targ, boneTarg, flags) in targets:
				fp.write(
"          Target %s OBJECT\n" % targ +
"            bone_target '%s' ;\n" % boneTarg +
"            use_local_space_transform False ; \n" +
"          end Target\n")

		elif typ == 'SINGLE_PROP':
			useMod = True
			for (targ, boneTarg) in targets:
				fp.write(
"          Target %s OBJECT\n" % targ +
"            data_path '%s' ;\n" % boneTarg +
"          end Target\n")

		else:
			raise NameError("Unknown driver var type %s" % typ)

		fp.write("        end DriverVariable\n")

	fp.write(
"        show_debug_info True ;\n" +
"      end Driver\n")

	if useMod:
		fp.write(
"      FModifier GENERATOR \n" +
"        active False ;\n" +
"        use_additive False ;\n")

		(a0,a1) = coeffs
		if useLoc:
			fp.write("        coefficients Array %s %s*One%s ;\n" % (a0,a1,extra))
		else:
			fp.write("        coefficients Array %s %s%s ;\n" % (a0,a1,extra))

		fp.write(
"        show_expanded True ;\n" +
"        mode 'POLYNOMIAL' ;\n" +
"        mute False ;\n" +
"        poly_order 1 ;\n" +
"      end FModifier\n")

	if useKeypoints:
		for (x,y) in coeffs:
			fp.write("      kp %.4f %.4f ; \n" % (x,y))

	fp.write(
"      extrapolation 'CONSTANT' ;\n" +
"      lock False ;\n" +
"      select False ;\n" +
"    end FCurve\n")

	return

#
#	setupCircle(fp, name, r):
#	setupCube(fp, name, r):
#	setupCircles(fp):
#

def setupCircle(fp, name, r):
	fp.write("\n"+
"Mesh %s %s \n" % (name, name) +
"  Verts\n")
	for n in range(16):
		v = n*pi/8
		fp.write("    v %.3f 0.5 %.3f ;\n" % (r*math.cos(v), r*math.sin(v)))
	fp.write(
"  end Verts\n" +
"  Edges\n")
	for n in range(15):
		fp.write("    e %d %d ;\n" % (n, n+1))
	fp.write("    e 15 0 ;\n")
	fp.write(
"  end Edges\n"+
"end Mesh\n"+
"Object %s MESH %s\n" % (name, name) +
"  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;\n"+
"  parent Refer Object CustomShapes ;\n"+
"end Object\n")
	return

def setupCube(fp, name, r, offs):
	try:
		(rx,ry,rz) = r
	except:
		(rx,ry,rz) = (r,r,r)
	try:
		(dx,dy,dz) = offs
	except:
		(dx,dy,dz) = (0,offs,0)

	fp.write("\n"+
"Mesh %s %s \n" % (name, name) +
"  Verts\n")
	for x in [-rx,rx]:
		for y in [-ry,ry]:
			for z in [-rz,rz]:
				fp.write("    v %.2f %.2f %.2f ;\n" % (x+dx,y+dy,z+dz))
	fp.write(
"  end Verts\n" +
"  Faces\n" +
"    f 0 1 3 2 ;\n" +
"    f 4 6 7 5 ;\n" +
"    f 0 2 6 4 ;\n" +
"    f 1 5 7 3 ;\n" +
"    f 1 0 4 5 ;\n" +
"    f 2 3 7 6 ;\n" +
"  end Faces\n" +
"end Mesh\n" +
"Object %s MESH %s\n" % (name, name) +
"  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;\n" +
"  parent Refer Object CustomShapes ;\n" +
"end Object\n")

def setupCircles(fp):
	setupCircle(fp, "MHCircle01", 0.1)
	setupCircle(fp, "MHCircle025", 0.25)
	setupCircle(fp, "MHCircle05", 0.5)
	setupCircle(fp, "MHCircle10", 1.0)
	setupCircle(fp, "MHCircle15", 1.5)
	setupCircle(fp, "MHCircle20", 2.0)
	setupCube(fp, "MHCube01", 0.1, 0)
	setupCube(fp, "MHCube025", 0.25, 0)
	setupCube(fp, "MHCube05", 0.5, 0)
	setupCube(fp, "MHEndCube01", 0.1, 1)
	setupCube(fp, "MHChest", (0.7,0.25,0.5), (0,0.5,0.35))
	setupCube(fp, "MHRoot", (1.25,0.5,1.0), 1)
	return

#
#	setupRig(obj):
#	writeAllArmatures(fp)	
#	writeAllPoses(fp)	
#	writeAllActions(fp)	
#
import rig_joints_25, rig_body_25, rig_arm_25, rig_finger_25, rig_leg_25, rig_toe_25, rig_face_25, rig_panel_25

def setupRig(obj):
	newSetupJoints(obj, 
		rig_joints_25.DeformJoints +
		rig_body_25.BodyJoints +
		rig_arm_25.ArmJoints +
		rig_finger_25.FingerJoints +
		rig_leg_25.LegJoints +
		#rig_toe_25.ToeJoints +
		rig_face_25.FaceJoints +
		rig_panel_25.PanelJoints,
		
		rig_body_25.BodyHeadsTails +
		rig_arm_25.ArmHeadsTails +
		rig_finger_25.FingerHeadsTails +
		rig_leg_25.LegHeadsTails +
		#rig_toe_25.ToeHeadsTails +
		rig_face_25.FaceHeadsTails +
		rig_panel_25.PanelHeadsTails)
	return
	
def writeAllArmatures(fp):
	writeArmature(fp, 
		rig_body_25.BodyArmature +
		rig_arm_25.ArmArmature +
		rig_finger_25.FingerArmature +
		rig_leg_25.LegArmature +
		#rig_toe_25.ToeArmature +
		rig_face_25.FaceArmature +
		rig_panel_25.PanelArmature, True)
	return

def writeAllPoses(fp):
	writeBoneGroups(fp)
	rig_body_25.BodyWritePoses(fp)
	rig_arm_25.ArmWritePoses(fp)
	rig_finger_25.FingerWritePoses(fp)
	rig_leg_25.LegWritePoses(fp)
	#rig_toe_25.ToeWritePoses(fp)
	rig_face_25.FaceWritePoses(fp)
	rig_panel_25.PanelWritePoses(fp)
	return
	
def writeAllActions(fp):
	#rig_arm_25.ArmWriteActions(fp)
	#rig_leg_25.LegWriteActions(fp)
	#rig_finger_25.FingerWriteActions(fp)
	return

#
#	writeAllDrivers(fp)	
#	writeAllProperties(fp):
#	defineAllProperties(fp):
#

def writeAllDrivers(fp):
	#writeFkIkSwitch(fp, rig_arm_25.ArmFKIKDrivers)
	#writeFkIkSwitch(fp, rig_leg_25.LegFKIKDrivers)
	writeDeformDrivers(fp, rig_arm_25.ArmDeformDrivers)
	writeDeformDrivers(fp, rig_leg_25.LegDeformDrivers)
	#rig_panel_25.FingerWriteDrivers(fp)
	rig_face_25.FaceWriteDrivers(fp)
	#writeEnumDrivers(fp, rig_panel_25.EnumDrivers)

	writePropDrivers(fp,
		rig_body_25.BodyPropDrivers +
		rig_arm_25.ArmPropDrivers +
		rig_finger_25.FingerPropDrivers +
		rig_leg_25.LegPropDrivers +
		rig_face_25.FacePropDrivers)
	return

def writeAllProperties(fp):
	writeProperties(fp,
		rig_body_25.BodyProperties +
		rig_arm_25.ArmProperties +
		rig_finger_25.FingerProperties +
		rig_leg_25.LegProperties +
		rig_face_25.FaceProperties)
	return

def defineAllProperties(fp):
	defineProperties(fp,
		rig_body_25.BodyProperties +
		rig_arm_25.ArmProperties +
		rig_finger_25.FingerProperties +
		rig_leg_25.LegProperties +
		rig_face_25.FaceProperties)
	return

#
#	writeAllProcesses(fp):
#

def writeAllProcesses(fp):
	return
	
	fp.write("  EditMode ;\n")
	parents = rig_arm_25.ArmParents + rig_leg_25.LegParents
	for (bone, parent) in parents:
		fp.write("  Reparent %s %s ;\n" % (bone, parent))

	fp.write("  PoseMode ;\n")
	processes = rig_arm_25.ArmProcess + rig_leg_25.LegProcess
	for (bone, axis, angle) in processes:
		fp.write("  Bend %s %s %.6g ;\n" % (bone, axis, angle))
	fp.write("  EditMode ;\n")
	fp.write("  ObjectMode ;\n")

	fp.write("  Apply ;\n")

	fp.write("  EditMode ;\n")
	snaps = rig_arm_25.ArmSnaps + rig_leg_25.LegSnaps
	for (bone, target, rev) in snaps:
		fp.write("  Snap %s %s %s ;\n" % (bone, target, rev))

	fp.write("  ObjectMode ;\n")
	fp.write("  EditMode ;\n")
	rolls = rig_arm_25.ArmRolls + rig_leg_25.LegRolls
	for (bone, roll) in rolls:
		fp.write("  Roll %s %.4f ;\n" % (bone, roll))
	
	fp.write("  ObjectMode ;\n")

	return

def reapplyArmature(fp, name):
	fp.write("\n" +
"  Object %s  \n" % name +
"    Modifier Armature ARMATURE \n" +
"      show_expanded True ; \n" +
"      object Refer Object %s ; \n" % mh2mhx.theHuman +
"      use_bone_envelopes False ; \n" +
"      use_vertex_groups True ; \n" +
"    end Modifier \n" +
"  end Object\n")




