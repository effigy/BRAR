import ogre.renderer.OGRE as ogre
import ogre.io.OIS as OIS
import ogre.gui.CEGUI as CEGUI
 
class ExitListener(ogre.FrameListener):
 
    def __init__(self, keyListener, mouseListener):
        ogre.FrameListener.__init__(self)
        self.keyListener = keyListener
        self.mouseListener = mouseListener
 
    def frameStarted(self, evt):
        print "+++++++++  ExitListener.frameStarted"
        if not self.keyListener.keyPressed(evt):
            print "++++++++ keylistener exit"
            return False
        self.mouseListener.mousePressed(evt)
        self.keyListener.keyReleased(evt)
        self.mouseListener.mouseMoved(evt)
        return True
 
    def __del__(self):
        pass
    
######################
##   Key Listener   ##
###################### 
class KeyListener(OIS.KeyListener, ogre.FrameListener):
    
    def __init__(self, keyboard):
        ogre.FrameListener.__init__(self)
        OIS.KeyListener.__init__(self)        
        keyboard.setEventCallback(self)
        self.Keyboard=keyboard    
        
    def keyPressed(self, evt):
        print "++++++++++++ key pressed"
        # Stop Rendering if Escape was pressed.
        if self.Keyboard.isKeyDown(OIS.KC_ESCAPE):
            return False
        # Attach the camera to PitchNode1.
        if self.Keyboard.isKeyDown(OIS.KC_1):
            self.camera.parentSceneNode.detachObject(self.camera)
            self.camNode = self.sceneManager.getSceneNode("CamNode1")
            self.sceneManager.getSceneNode("PitchNode1").attachObject(self.camera)
        # Attach the camera to PitchNode2.
        if self.Keyboard.isKeyDown(OIS.KC_2):
            self.camera.parentSceneNode.detachObject(self.camera)
            self.camNode = self.sceneManager.getSceneNode("CamNode2")
            self.sceneManager.getSceneNode("PitchNode2").attachObject(self.camera)
        # Move Forward.
        if self.Keyboard.isKeyDown(OIS.KC_UP) or self.Keyboard.isKeyDown(OIS.KC_W):
            self.direction.z -= self.move
        # Move Backward.
        if self.Keyboard.isKeyDown(OIS.KC_DOWN) or self.Keyboard.isKeyDown(OIS.KC_S):
            self.direction.z += self.move
        # Strafe Left.
        if self.Keyboard.isKeyDown(OIS.KC_LEFT) or self.Keyboard.isKeyDown(OIS.KC_A):
            self.direction.x -= self.move
        # Strafe Right.
        if self.Keyboard.isKeyDown(OIS.KC_RIGHT) or self.Keyboard.isKeyDown(OIS.KC_D):
            self.direction.x += self.move
        # Move Up.
        if self.Keyboard.isKeyDown(OIS.KC_PGUP) or self.Keyboard.isKeyDown(OIS.KC_Q):
            self.direction.y += self.move
        # Move Down.
        if self.Keyboard.isKeyDown(OIS.KC_PGDOWN) or self.Keyboard.isKeyDown(OIS.KC_E):
            self.direction.y -= self.move
            
        return True
    
    def keyReleased(self, evt):
        # Undo change to the direction vector when the key is released to stop movement.
        if self.Keyboard.isKeyDown(OIS.KC_UP) or self.Keyboard.isKeyDown(OIS.KC_W):
            self.direction.z += self.move
        # Move Backward.
        if self.Keyboard.isKeyDown(OIS.KC_DOWN) or self.Keyboard.isKeyDown(OIS.KC_S):
            self.direction.z -= self.move
        # Strafe Left.
        if self.Keyboard.isKeyDown(OIS.KC_LEFT) or self.Keyboard.isKeyDown(OIS.KC_A):
            self.direction.x += self.move
        # Strafe Right.
        if self.Keyboard.isKeyDown(OIS.KC_RIGHT) or self.Keyboard.isKeyDown(OIS.KC_D):
            self.direction.x -= self.move
        # Move Up.
        if self.Keyboard.isKeyDown(OIS.KC_PGUP) or self.Keyboard.isKeyDown(OIS.KC_Q):
            self.direction.y -= self.move
        # Move Down.
        if self.Keyboard.isKeyDown(OIS.KC_PGDOWN) or self.Keyboard.isKeyDown(OIS.KC_E):
            self.direction.y += self.move
    
#######################
##  Mouse Listener   ##
#######################    
class MouseListener(OIS.MouseListener, ogre.FrameListener):
    
    def __init__(self, mouse):
        ogre.FrameListener.__init__(self)
        OIS.MouseListener.__init__(self)
        mouse.setEventCallback(self)
        self.Mouse = mouse
        
    def mouseMoved(self, evt):
        ms = self.Mouse.getMouseState()
        if ms.buttonDown(OIS.MB_Right):
            self.camNode.yaw(ogre.Degree(-self.rotate
                * ms.X.rel).valueRadians())
            self.camNode.getChild(0).pitch(ogre.Degree(-self.rotate
                * ms.Y.rel).valueRadians())
    
    def mousePressed(self, evt):
        ms = self.Mouse.getMouseState()
        # Toggle the light.
        if ms.buttonDown(OIS.MB_Left):
            light = self.sceneManager.getLight('Light1')
            light.visible = not light.visible
    
    def mouseReleased(self, evt):
        return True
    
#########################
##  Application Class  ##
#########################    
class Application(object):
 
    def go(self):
        self.createRoot()
        self.defineResources()
        self.setupRenderSystem()
        self.createRenderWindow()
        self.initializeResourceGroups()
        self.setupScene()
        self.setupInputSystem()
        self.setupCEGUI()
        self.createFrameListener()
        self.createScene()
        self.startRenderLoop()
        print "+++++++++ out of render loop"
        self.cleanUp()
 
    def createRoot(self):
        self.root = ogre.Root()
 
    def defineResources(self):
        cf = ogre.ConfigFile()
        cf.load("Resources.cfg")
        
        secI = cf.getSectionIterator()
        
        while secI.hasMoreElements():
                secName = secI.peekNextKey()
                settings = secI.getNext()
                for i in settings:
                    ogre.ResourceGroupManager.getSingleton().addResourceLocation(i.value, i.key, secName)
 
    def setupRenderSystem(self):
        if not self.root.restoreConfig() and not self.root.showConfigDialog():
            raise Exception("User canceled config dialog!")
 
    def createRenderWindow(self):
        self.root.initialise(True, "OGRE!!!")
 
    def initializeResourceGroups(self):
        ogre.TextureManager.getSingleton().setDefaultNumMipmaps(5)
        ogre.ResourceGroupManager.getSingleton().initialiseAllResourceGroups()
 
    def setupScene(self):
        self.sceneManager = self.root.createSceneManager(ogre.ST_GENERIC, "Default SceneManager")
        self.camera = self.sceneManager.createCamera('Camera')
        viewport = self.root.getAutoCreatedWindow().addViewport(self.camera)
 
    def setupInputSystem(self):
        rWind = self.root.getAutoCreatedWindow()
        winHandle = rWind.getCustomAttributeInt('WINDOW')
        paramList = [('WINDOW', str(winHandle))]
        self.inputManager = OIS.createPythonInputSystem(paramList)
        
        # Set-Up Mouse and Keyboard objects
        self.Keyboard = self.inputManager.createInputObjectKeyboard(OIS.OISKeyboard, True)
        self.Mouse = self.inputManager.createInputObjectMouse(OIS.OISMouse, True)
        self.mouseListener = MouseListener(self.Mouse)
        self.keyListener = KeyListener(self.Keyboard)
         
    def setupCEGUI(self):
        pass
 
    def createFrameListener(self):
        self.frameListener = ExitListener(self.keyListener, self.mouseListener)
        self.root.addFrameListener(self.frameListener)
 
    def startRenderLoop(self):
        print "+++++++ entering render loop"
        self.root.startRendering()
        
    def createScene(self):
        sceneManager = self.sceneManager
        sceneManager.ambientLight = 0.25, 0.25, 0.25
 
        ent = sceneManager.createEntity("Ninja", "ninja.mesh")
        node = sceneManager.getRootSceneNode().createChildSceneNode("NinjaNode")
        node.attachObject(ent)
 
        light = sceneManager.createLight("Light1")
        light.type = ogre.Light.LT_POINT
        light.position = 250, 150, 250
        light.diffuseColour = 1, 1, 1
        light.specularColour = 1, 1, 1
 
        # create the first camera node/pitch node
        node = sceneManager.getRootSceneNode().createChildSceneNode("CamNode1",
            (-400, 200, 400))
        node.yaw(ogre.Degree(-45))
        node = node.createChildSceneNode("PitchNode1")
        node.attachObject(self.camera)
 
        # create the second camera node/pitch node
        node = sceneManager.getRootSceneNode().createChildSceneNode("CamNode2",
            (0, 200, 400))
        node.createChildSceneNode("PitchNode2")
 
    def cleanUp(self):
        self.inputManager.destroyInputObjectKeyboard(self.Keyboard)
        self.inputManager.destroyInputObjectMouse(self.Mouse)
        OIS.InputManager.destroyInputSystem(self.inputManager)
        self.inputManager = None
    
    def __del__(self):
        del self.renderer
        del self.system
        del self.mouseListener
        del self.keyListener
        del self.frameListener
        del self.root
 
 
if __name__ == '__main__':
    try:
        ta = Application()
        ta.go()
    except ogre.OgreException, e:
        print e