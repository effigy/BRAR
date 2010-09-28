'''
Created on Sep 28, 2010

@author: jcobb
'''

import ogre.renderer.OGRE as ogre
import SampleFramework as sf
 
class TutorialApplication(sf.Application):
 
    def _createScene(self):
        sceneManager = self.sceneManager
        sceneManager.ambientLight = ogre.ColourValue(1,1,1)
        
        ent1 = sceneManager.createEntity ("Robot", "robot.mesh")
        node1 = sceneManager.getRootSceneNode().createChildSceneNode ("RobotNode")
        node1.attachObject(ent1)
        
        ent2 = sceneManager.createEntity("Robot2", "robot.mesh")
        node2 = sceneManager.getRootSceneNode().createChildSceneNode("RobotNode2", (50,0,0))
        node2.attachObject(ent2)


if __name__ == '__main__':
    ta = TutorialApplication()
    ta.go()