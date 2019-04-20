import maya.cmds as cmds
import random as rand
import random
import functools


def clear_object(name):
    results = cmds.ls(name)
    if len(results) > 0:
        cmds.delete(results)

def clear_sphere():
    clear_object('center_sphere')

def clear_cylinder():
    clear_object('*cylinder*')
      
def create_sphere():
    result = cmds.sphere(name='center_sphere', p=(0, 0, 0), ax=(0, 1, 0), ssw=0, esw=360, r=2, d=3, ut=0, tol=0.01, s=8, nsp=4, ch=1)
    print 'sphere: %s' % result
    return result

def create_cylinder():
    result = cmds.polyCylinder(name='cylinder', r=1.15, h=0.15, sx=6, sy=1, sz=1, ax=(0, 1, 0), rcp=0, cuv=3, ch=1)
    cmds.polyBevel3(result[0],
                    fraction=0.5,
                    offsetAsFraction=1,
                    autoFit=1,
                    depth=1,
                    mitering=0,
                    miterAlong=0,
                    chamfer=1,
                    segments=1,
                    worldSpace=1,
                    smoothingAngle=30,
                    subdivideNgons=1,
                    mergeVertices=1,
                    mergeVertexTolerance=0.0001,
                    miteringAngle=180,
                    angleTolerance=180,
                    ch=1)
    #print 'result: %s' % result
    return result

def ui_num_cylinder(pWindowTitle, pApplyCallback):
    window_id = 'num_cylinder'
    if cmds.window(window_id, exists=True):
        cmds.deleteUI(window_id)
    cmds.window( window_id, title=pWindowTitle, sizeable=False, resizeToFitChildren=True )
    cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[ (1,75), (2,60), (3,60) ], columnOffset=[ (1,'right',3) ] )
    
    cmds.text( label='Time Range:' )
    startTimeField = cmds.intField( value=cmds.playbackOptions( q=True, minTime=True ) )
    endTimeField = cmds.intField( value=cmds.playbackOptions( q=True, maxTime=True ) )
    
    cmds.text( label='Attribute:' )
    targetAttributeField = cmds.textField( text='rotateY' )
    cmds.separator( h=10, style='none' )
    
    cmds.text( label='Number:')
    numberField = cmds.intField( value=50 )
    cmds.separator( h=10, style='none' )
    
    cmds.separator( h=10, style='none' )
    
    cmds.button( label='Apply', command=functools.partial( pApplyCallback,
                                                  startTimeField,
                                                  endTimeField,
                                                  targetAttributeField,
                                                  numberField ) )
    
    def cancelCallback( *pArgs ):
        if cmds.window( window_id, exists=True ):
            cmds.deleteUI( window_id )
    
    cmds.button( label='Cancel', command=cancelCallback )
    cmds.showWindow()


def create_cylinder_group(num=50):
    result = create_cylinder()
    transformName = result[0]
    instanceGroupName = cmds.group(empty=True, name='group_' + transformName + '_instance')
    
    for i in range(num):
        instanceResult = cmds.instance(transformName, name=transformName+ '_instance#')
        cmds.parent(instanceResult, instanceGroupName)
        
        x = random.uniform(-10, 10)
        y = random.uniform(-10, 10)
        z = random.uniform(-10, 10)
        
        cmds.move(x, y, z, instanceResult)
        
        xRot = random.uniform(0, 360)
        yRot = random.uniform(0, 360)
        zRot = random.uniform(0, 360)
        
        cmds.rotate(xRot, yRot, zRot, instanceResult)

        scalingFactor = random.uniform(0.3, 1.5)
        
        cmds.scale(scalingFactor, scalingFactor, scalingFactor, instanceResult)
        shader=cmds.shadingNode("blinn",asShader=True)
        Colors=[]
        for i in range(3):
            tmp=random.uniform(0.0,1.0) #Uniform function allow me to find a random FLOAT number between a range(not like randint!)
            Colors.append(tmp)  
        cmds.setAttr ( (shader + '.color'), Colors[0],Colors[1],Colors[2], type = 'double3' )
        shading_group= cmds.sets(renderable=True,noSurfaceShader=True,empty=True)
        cmds.connectAttr('%s.outColor' %shader ,'%s.surfaceShader' %shading_group)
        cmds.sets(instanceResult, e=True, forceElement=shading_group)
    
    cmds.hide(transformName)
    cmds.xform(instanceGroupName, centerPivots=True)

    print instanceGroupName
    return instanceGroupName


def aim_at(objectName, targetName):
    results = cmds.ls(objectName)
    for object in results:
        cmds.aimConstraint(targetName, object, aimVector=[0,1,0])


def key_full_rotation(objectName, start_time, end_time, targetAttr):
    cmds.cutKey(objectName, time=(start_time, end_time), attribute=targetAttr)
    cmds.setKeyframe(objectName, time=start_time, attribute=targetAttr, value=0)
    cmds.setKeyframe(objectName, time=end_time, attribute=targetAttr, value=360)
    cmds.selectKey(objectName, time=(start_time, end_time), attribute=targetAttr, keyframe=True)
    cmds.keyTangent(inTangentType='linear', outTangentType='linear')


def rotation_by(objectName, targetAttr):
    results = cmds.ls(objectName, type='transform')
    print 'rotation_by: %s' % results
    start_time = cmds.playbackOptions( query=True, minTime=True )
    end_time = cmds.playbackOptions( query=True, maxTime=True )
    
    for object in results:
        key_full_rotation(object, start_time, end_time, targetAttr)


def expand_at(objectName, targetName):
    locatorGroupName = cmds.group( empty=True, name='group_expansion_locator' )
    maxExpansion = 100    
    newAttributeName = 'expansion'
    
    if not cmds.objExists( '%s.%s' % ( targetName, newAttributeName ) ):
        cmds.select( targetName )
        cmds.addAttr( longName=newAttributeName, shortName='exp',
                      attributeType='double', min=0, max=maxExpansion,
                      defaultValue=maxExpansion, keyable=True )
    
    results = cmds.ls(objectName, type='transform')
    for object in results:
        coords = cmds.getAttr( '%s.translate' % ( object ) )[0]        
        locatorName = cmds.spaceLocator( position=coords, name='%s_loc#' % ( object ) )[0]
        cmds.xform( locatorName, centerPivots=True )
        cmds.parent( locatorName, locatorGroupName )
        pointConstraintName = cmds.pointConstraint( [ targetName, locatorName ], object, name='%s_pointConstraint#' % ( object ) )[0]
       
        cmds.expression( alwaysEvaluate=True, 
                         name='%s_attractWeight' % ( object ),
                         object=pointConstraintName,
                         string='%sW0=%s-%s.%s' % ( targetName, maxExpansion, targetName, newAttributeName ) )        
        cmds.connectAttr( '%s.%s' % ( targetName, newAttributeName ), 
                          '%s.%sW1' % ( pointConstraintName, locatorName ) )  
    cmds.xform( locatorGroupName, centerPivots=True )
    

def apply_callback(field_start_time, field_end_time, field_target_attribute, field_number, *args):
    print field_start_time, field_end_time, field_target_attribute, field_number
    start_time = cmds.intField(field_start_time, query=True, value=True )
    end_time = cmds.intField(field_end_time, query=True, value=True )
    target_attribute = cmds.textField(field_target_attribute, query=True, text=True)

    number = cmds.intField(field_number, query=True, value=True )
    print start_time, end_time, target_attribute, number

    clear_sphere()
    clear_cylinder()
    sphere = create_sphere()
    create_cylinder_group(number)
    aim_at('cylinder_instance*', sphere[0])
    #rotation_by('group_cylinder_instance', 'rotateY')
    expand_at('cylinder_instance*', sphere[0])
    #rotation_by('group_cylinder_instance', 'rotateY')
    rotation_by('group_expansion_locator', 'rotateY')


ui_num_cylinder('Project 06', apply_callback)
