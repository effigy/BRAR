
import ogre.renderer.OGRE as ogre
import ogre.io.OIS as OIS
import ogre.gui.CEGUI as CEGUI
from noise import *
 
 
def sinFunction( tl, br ):
    return 20.0 * ogre.Math.Sin(tl.x - br.y)
  
class LandTile:
    def __init__(self, topLeft, bottomRight, quads=48):
        self.tl = topLeft # the base value
        self.br = bottomRight
 
        self.topLeft = ogre.Vector2(topLeft.x, topLeft.y) # an incremented value
 
        self.numVerts = quads
 
        self.verts = []
        self.uvs = []
        self.normals = []
        self.triangles = []
 
        self.isGenerated = False
        self.edgeDist = self.br.x - self.tl.x
 
        self.heightMapFunction = sinFunction

 
    def getRandom(self, pos):
        rand = 1000.0 * pnoise2( pos.x, pos.y, octaves=6, persistence=.5 )
        print pos.x, pos.y, rand
        return rand
 
    def calcTriangleNormal( self, v1, v2, v3 ):
        return (v2-v1).crossProduct(v3-v1).normalisedCopy()
 
 
    def generate(self):
        incr = float ( (self.br.x - self.tl.x) / self.numVerts )
        mNumVerts = 0
 
        for xv in range( 0, self.numVerts, 4):
            for yv in range(0 , self.numVerts, 4):
                v1 = ( self.topLeft.x + incr, self.getRandom(ogre.Vector2( self.topLeft.x + incr, self.topLeft.y )), self.topLeft.y )
                v2 = ( self.topLeft.x, self.getRandom( ogre.Vector2( self.topLeft.x, self.topLeft.y + incr ) ), self.topLeft.y + incr)
                v3 = ( self.topLeft.x + incr, self.getRandom(self.topLeft + incr), self.topLeft.y + incr)
                v4 = ( self.topLeft.x, self.getRandom(self.topLeft), self.topLeft.y)
 
                self.verts +=  [v1, v2, v3, v4]
 
                tri1 = (mNumVerts+3, mNumVerts+1, mNumVerts)             # [ (0,3,2), (3,2,1) ]
                tri2 = (mNumVerts+1, mNumVerts+2, mNumVerts)
 
                self.triangles += [ tri1, tri2 ]
 
                u0 = (self.topLeft.x - self.tl.x) / self.edgeDist
                v0 = (self.topLeft.y - self.tl.y) / self.edgeDist
                u1 = (self.topLeft.x + incr - self.tl.x) / self.edgeDist
                v1 = (self.topLeft.y + incr - self.tl.y) / self.edgeDist
 
                self.uvs += [ (u1,v0), (u0,v1), (u1,v1), (u0,v0) ]
                self.topLeft.y += incr
                mNumVerts += 4
            self.topLeft.x += incr
            self.topLeft.y = self.tl.y
 
        self.normals = [[0,0,0]] * len(self.verts)
 
        for tri in self.triangles:
            one = self.verts[tri[0]]
            two = self.verts[tri[1]]
            three = self.verts[tri[2]]
 
            v1 = ogre.Vector3(one[0], one[1], one[2])
            v2 = ogre.Vector3(two[0], two[1], two[2])
            v3 = ogre.Vector3(three[0], three[1], three[2])
 
            norm = self.calcTriangleNormal( v1, v2, v3 )
 
            self.normals[ tri[0] ] = [norm.x, norm.y, norm.z]
            self.normals[ tri[1] ] = [norm.x, norm.y, norm.z]
            self.normals[ tri[2] ] = [norm.x, norm.y, norm.z]
 
 
    def buildGeometry(self, msh):
        msh.begin( "Ogre/Skin" )
        for x in range(len(self.verts)):
            msh.position(*self.verts[x])
            if len(self.normals):
                msh.normal(*self.normals[x])
            if len(self.uvs):
                msh.textureCoord(*self.uvs[x])
 
        for x in range(len(self.triangles)):
            msh.triangle(*self.triangles[x])
 
        msh.end() 

class EventListener(ogre.FrameListener, ogre.WindowEventListener, OIS.MouseListener, OIS.KeyListener, OIS.JoyStickListener):
    """
    This class handles all our ogre and OIS events, mouse/keyboard/joystick
    depending on how you initialize this class. All events are handled
    using callbacks (buffered).
    """
 
    mouse = None  
    keyboard = None
    joy = None
 
    def __init__(self, sceneManager, renderWindow, bufferedMouse, bufferedKeys, bufferedJoy):
 
        # Initialize the various listener classes we are a subclass from
        ogre.FrameListener.__init__(self)
        ogre.WindowEventListener.__init__(self)
        OIS.MouseListener.__init__(self)
        OIS.KeyListener.__init__(self)
        OIS.JoyStickListener.__init__(self)
        
        self.sceneManager = sceneManager
        self.camera = self.sceneManager.getCamera("Cam1")
        self.renderWindow = renderWindow
 
        # Create the inputManager using the supplied renderWindow
        windowHnd = self.renderWindow.getCustomAttributeInt("WINDOW")
        self.inputManager = OIS.createPythonInputSystem([("WINDOW",str(windowHnd))])
 
        # Attempt to get the mouse/keyboard input objects,
        # and use this same class for handling the callback functions.
        # These functions are defined later on.
 
        try:
            if bufferedMouse:
                self.mouse = self.inputManager.createInputObjectMouse(OIS.OISMouse, bufferedMouse)
                self.mouse.setEventCallback(self)
 
            if bufferedKeys:
                self.keyboard = self.inputManager.createInputObjectKeyboard(OIS.OISKeyboard, bufferedKeys)
                self.keyboard.setEventCallback(self)
 
            if bufferedJoy:
                self.joy = self.inputManager.createInputObjectJoyStick(OIS.OISJoyStick, bufferedJoy)
                self.joy.setEventCallback(self)
 
        except Exception, e: # Unable to obtain mouse/keyboard/joy input
            raise e
 
        # Set this to True when we get an event to exit the application
        self.quitApplication = False
 
        # Listen for any events directed to the window manager's close button
        ogre.WindowEventUtilities.addWindowEventListener(self.renderWindow, self)
        
        self.rotate = .1
        self.move = 250
        self.direction = ogre.Vector3(0,0,0)
        
    def __del__ (self ):
        # Clean up OIS 
        print "QUITING"
        self.delInputObjects()
 
        OIS.InputManager.destroyInputSystem(self.inputManager)
        self.inputManager = None
 
        ogre.WindowEventUtilities.removeWindowEventListener(self.renderWindow, self)
        self.windowClosed(self.renderWindow)
 
    def delInputObjects(self):
        # Clean up the initialized input objects
        if self.keyboard:
            self.inputManager.destroyInputObjectKeyboard(self.keyboard)
        if self.mouse:
            self.inputManager.destroyInputObjectMouse(self.mouse)
        if self.joy:
            self.inputManager.destroyInputObjectJoyStick(self.joy)
 
    def frameStarted(self, evt):
        """ 
        Called before a frame is displayed, handles events
        (also those via callback functions, as you need to call capture()
        on the input objects)
 
        Returning False here exits the application (render loop stops)
        """
 
        # Capture any buffered events and call any required callback functions
        if self.keyboard:
            self.keyboard.capture()
        if self.mouse:
            self.mouse.capture()
            self.mouseMoved(evt)
        if self.joy:
            self.joy.capture()
 
            # joystick test
            axes_int = self.joy.getJoyStickState().mAxes
            axes = []
            for i in axes_int:
                axes.append(i.abs)            
            print axes
        
        camNode = self.camera.parentSceneNode.parentSceneNode
        camNode.translate(camNode.orientation * self.direction * evt.timeSinceLastFrame)
        # Neatly close our FrameListener if our renderWindow has been shut down
        if(self.renderWindow.isClosed()):
            return False
        
        return not self.quitApplication
 
### Window Event Listener callbacks ###
 
    def windowResized(self, renderWindow):
        pass
 
    def windowClosed(self, renderWindow):
        # Only close for window that created OIS
        if(renderWindow == self.renderWindow):
            del self
 
### Mouse Listener callbacks ###
 
    def mouseMoved(self, evt):
        # Pass the location of the mouse pointer over to CEGUI
        ms = self.mouse.getMouseState()
        if ms.buttonDown(OIS.MB_Left):
            camNode = self.camera.parentSceneNode.parentSceneNode
            camNode.yaw(ogre.Degree(-self.rotate * ms.X.rel).valueRadians())
            camNode.getChild(0).pitch(ogre.Degree(self.rotate * ms.Y.rel).valueRadians())
        return True
 
    def mousePressed(self, evt, id):
        # Handle any CEGUI mouseButton events
        CEGUI.System.getSingleton().injectMouseButtonDown(self.convertButton(id))
        return True
 
    def mouseReleased(self, evt, id):
        # Handle any CEGUI mouseButton events
        CEGUI.System.getSingleton().injectMouseButtonUp(self.convertButton(id))
        return True
 
 
    def convertButton(self,oisID):
        if oisID == OIS.MB_Left:
            return CEGUI.LeftButton
        elif oisID == OIS.MB_Right:
            return CEGUI.RightButton
        elif oisID == OIS.MB_Middle:
            return CEGUI.MiddleButton
        else:
            return CEGUI.LeftButton     
 
### Key Listener callbacks ###
 
    def keyPressed(self, evt):
        # Quit the application if we hit the escape button
        print evt, evt.key
        if evt.key == OIS.KC_ESCAPE:
            self.quitApplication = True
 
        if evt.key == OIS.KC_1:
            print "hello"
        if evt.key == OIS.KC_W or evt.key == OIS.KC_UP:
            self.direction.z += self.move
        if evt.key == OIS.KC_S or evt.key == OIS.KC_DOWN:
            self.direction.z -= self.move
        if evt.key == OIS.KC_A or evt.key == OIS.KC_LEFT:
            self.direction.x += self.move
        if evt.key == OIS.KC_D or evt.key == OIS.KC_RIGHT:
            self.direction.x -= self.move
        if evt.key == OIS.KC_Q or evt.key == OIS.KC_PGUP:
            self.direction.y += self.move
        if evt.key == OIS.KC_E or evt.key == OIS.KC_PGDOWN:
            self.direction.y -= self.move    
        
        return True
 
    def keyReleased(self, evt):
        
        if evt.key == OIS.KC_W or evt.key == OIS.KC_UP:
            self.direction.z -= self.move
        if evt.key == OIS.KC_S or evt.key == OIS.KC_DOWN:
            self.direction.z += self.move
        if evt.key == OIS.KC_A or evt.key == OIS.KC_LEFT:
            self.direction.x -= self.move
        if evt.key == OIS.KC_D or evt.key == OIS.KC_RIGHT:
            self.direction.x += self.move
        if evt.key == OIS.KC_Q or evt.key == OIS.KC_PGUP:
            self.direction.y -= self.move
        if evt.key == OIS.KC_E or evt.key == OIS.KC_PGDOWN:
            self.direction.y += self.move    
        
        return True
 
### Joystick Listener callbacks ###
 
    def buttonPressed(self, evt, id):
        return True
 
    def buttonReleased(self, evt, id):
        return True
 
    def axisMoved(self, evt, id):
        return True
 
class Application(object):
 
    app_title = "MyApplication"
 
    def go(self):
        # See Basic Tutorial 6 for details
        self.createRoot()
        self.defineResources()
        self.setupRenderSystem()
        self.createRenderWindow()
        self.initializeResourceGroups()
        self.setupScene()
        self.createFrameListener()
        self.setupCEGUI()
        self.startRenderLoop()
        #self.cleanUp()
 
    def createRoot(self):
        self.root = ogre.Root()
 
    def defineResources(self):
        # Read the resources.cfg file and add all resource locations in it
        cf = ogre.ConfigFile()
        cf.load("resources.cfg")
        seci = cf.getSectionIterator()
        while seci.hasMoreElements():
            secName = seci.peekNextKey()
            settings = seci.getNext()
 
            for item in settings:
                typeName = item.key
                archName = item.value
                ogre.ResourceGroupManager.getSingleton().addResourceLocation(archName, typeName, secName)
 
 
    def setupRenderSystem(self):
        # Show the config dialog if we don't yet have an ogre.cfg file
        if not self.root.restoreConfig() and not self.root.showConfigDialog():
            raise Exception("User canceled config dialog! (setupRenderSystem)")
 
    def createRenderWindow(self):
        self.root.initialise(True, self.app_title)
 
    def initializeResourceGroups(self):
        ogre.TextureManager.getSingleton().setDefaultNumMipmaps(5)
        ogre.ResourceGroupManager.getSingleton().initialiseAllResourceGroups()
 
    def setupScene(self):
        self.renderWindow = self.root.getAutoCreatedWindow()
        self.sceneManager = self.root.createSceneManager(ogre.ST_GENERIC, "Default SceneManager")
        self.camera = self.sceneManager.createCamera("Cam1")
        viewPort = self.root.getAutoCreatedWindow().addViewport(self.camera)
        
        self.sceneManager.getRootSceneNode().createChildSceneNode("CamNode1", (0, 100, -400)).createChildSceneNode("PitchNode1").attachObject(self.camera)
        self.camera.lookAt(ogre.Vector3(0, 0, 1))
 
 
        self.sceneManager.setAmbientLight(ogre.ColourValue(0.7,0.7,0.7))
        self.sceneManager.setSkyDome(True, 'Examples/CloudySky',4, 8)
        self.sceneManager.setFog( ogre.FOG_EXP, ogre.ColourValue(1,1,1),0.0002)
        self.light = self.sceneManager.createLight( 'lightMain')
        self.light.setPosition ( ogre.Vector3(20, 80, 50) )
 
        self.rn = self.sceneManager.getRootSceneNode()
 
        
        manObj = self.sceneManager.createManualObject("NoisyLand")
 
        test = LandTile( ogre.Vector2( 0,0 ), ogre.Vector2( 50000, 50000 ), 128 )
        test.generate()
        test.buildGeometry( manObj )
 
        node = self.sceneManager.getRootSceneNode().createChildSceneNode()
        node.attachObject( manObj )
 
 
    def createFrameListener(self):
        self.eventListener = EventListener(self.sceneManager, self.renderWindow, True, True, False) # switch the final "False" into "True" to get joystick support
        self.root.addFrameListener(self.eventListener)
 
    def setupCEGUI(self):
        sceneManager = self.sceneManager
        
        # CEGUI setup
        if CEGUI.Version__.startswith("0.6"):
            self.renderer = CEGUI.OgreCEGUIRenderer(renderWindow, ogre.RENDER_QUEUE_OVERLAY, False, 3000, sceneManager)
            self.system = CEGUI.System(self.renderer)
        else:
            self.renderer = CEGUI.OgreRenderer.bootstrapSystem()
            self.system = CEGUI.System.getSingleton()
 
        CEGUI.SchemeManager.getSingleton().create("TaharezLookSkin.scheme")
        self.system.setDefaultMouseCursor("TaharezLook", "MouseArrow")
        self.system.setDefaultFont("BlueHighway-12")
 
        # Uncomment the following to read in a CEGUI sheet (from CELayoutEditor)
        # 
        # self.mainSheet = CEGUI.WindowManager.getSingleton().loadWindowLayout("myapplication.layout")
        # self.system.setGUISheet(self.mainSheet)
 
    def startRenderLoop(self):
        self.root.startRendering()
 
    def cleanUp(self):
        # Clean up CEGUI
        print "CLEANING"
        #del self.renderer
        del self.system
 
        # Clean up Ogre
        #del self.exitListener
        del self.root
 
 
if __name__ == '__main__':
    try:
        ta = Application()
        ta.go()
    except ogre.OgreException, e:
        print e