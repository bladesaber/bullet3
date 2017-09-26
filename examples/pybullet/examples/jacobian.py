import sys
sys.path.append('/Users/bingjeff/Documents/projects/walkman/bullet3/bin/')
import pybullet as p
import numpy as np

def getJointStates(robot):
	joint_states = p.getJointStates(robot, range(p.getNumJoints(robot)))
	joint_positions = [state[0] for state in joint_states]
	joint_velocities = [state[1] for state in joint_states]
	joint_torques = [state[3] for state in joint_states]
	return joint_positions, joint_velocities, joint_torques

def setJointPosition(robot, position, kp=1.0, kv=0.3):
	num_joints = p.getNumJoints(robot)
	zero_vec = [0.0] * num_joints
	if len(position) == num_joints:
		p.setJointMotorControlArray(robot, range(num_joints),
									p.POSITION_CONTROL,
									targetPositions=position,
									targetVelocities=zero_vec,
									positionGains=[kp] * num_joints,
									velocityGains=[kv] * num_joints)
	else:
		print("Not setting torque. "
			  "Expected torque vector of "
			  "length {}, got {}".format(num_joints, len(torque)))

def setJointState(robot, position, velocity=None):
    num_joints = pb.getNumJoints(robot)
    if velocity is None:
        velocity = [0.0] * num_joints
    if len(position) == num_joints and len(velocity) == num_joints:
        for c in range(num_joints):
            pb.resetJointState(robot, c, position[c], velocity[c])
    else:
        print("Not setting state. "
              "Expected vectors of length {}, "
              "got pos={}, vel={}".format(num_joints, len(position), len(velocity)))


clid = p.connect(p.SHARED_MEMORY)
if (clid<0):
	p.connect(p.GUI)
time_step = 0.001
gravity_constant = -9.81
p.resetSimulation()
p.setTimeStep(time_step)
p.setGravity(0.0, 0.0, gravity_constant)
p.loadURDF("plane.urdf",[0,0,-0.3])
kukaId = p.loadURDF("kuka_iiwa/model.urdf",[0,0,0])
p.resetBasePositionAndOrientation(kukaId,[0,0,0],[0,0,0,1])
kukaEndEffectorIndex = 6
numJoints = p.getNumJoints(kukaId)
if (numJoints!=7):
	exit()

setJointPosition(kukaId, [0.1] * p.getNumJoints(kukaId))
p.stepSimulation()

# Get the value of the link and joint state after a simulation step.
result0 = p.getLinkState(kukaId, kukaEndEffectorIndex, computeLinkVelocity=1)
pos, vel, torq = getJointStates(kukaId)

# Now "reset" the simulation to have the same joint state and read the link state.
setJointState(kukaId, pos, vel)
result1 = p.getLinkState(kukaId, kukaEndEffectorIndex, computeLinkVelocity=1)
link_trn, link_rot, com_trn, com_rot, frame_pos, frame_rot, link_vt, link_vr = result1

# Show that the link origin is different for supposedly the same joint state.
print "Link origin - stepSimulation:"
print result0[0]
print "Link origin - resetJointState:"
print result1[0]

# Using the "reset" system the body velocities (should) match.
zero_vec = [0.0] * numJoints
jac_t, jac_r = p.calculateJacobian(kukaId, kukaEndEffectorIndex, com_trn, pos, zero_vec, zero_vec)

print "Link linear velocity of CoM from getLinkState:"
print link_vt
print "Link linear velocity of CoM from linearJacobian * q_dot:"
print np.dot(np.array(jac_t), np.array(vel))
print "Link angular velocity of CoM from getLinkState:"
print link_vr
print "Link angular velocity of CoM from angularJacobian * q_dot:"
print np.dot(np.array(jac_r), np.array(vel))
