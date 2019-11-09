from maya import cmds

def build(task):
    # Create envelope attribute node.
    envelope = task['envelope']
    envelopeAttr = '{0}Envelope'.format(task['title'])
    cmds.addAttr(task.bone, ln=envelopeAttr, at='float', min=envelope.min, max=envelope.max, default=envelope.default)
    envelopeNode = cmds.createNode('multiplyDivide')

    # Create power attribute node.
    envelope = task['power']
    powerAttr = '{0}Power'.format(task['title'])
    cmds.addAttr(task['bone'], ln=powerAttr, at='float', min=power.min, max=power.max, default=power.default)
    powerNode = cmds.createNode('multiplyDivide')

    # Connect node attributes from target to bone.
    task['bone'][powerAttr].connect(powerNode.input1)
    task['target'].scale.connect(powerNode.input2)
    
    task['bone'][envelopeAttr].connect(envelopeNode.input1)
    powerNode.output.connect(envelopeNode.input2)
    
    # Connect envelope to the bone, if the axis is enabled.
    if task['axes']['xAxis']:
        envelopeNode.output.connect(task['bone'].scaleX)

    if task['axes']['yAxis']:
        envelopeNode.output.connect(task['bone'].scaleY)

    if task['axes']['zAxis']:
        envelopeNode.output.connect(task['bone'].scaleZ)
    

    