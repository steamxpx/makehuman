import sys
import os
import glob, imp
from os.path import join, basename, splitext

from core import G
import mh
import files3d
import gui3d, font3d, animation3d
import human
import guimodelling, guifiles
from aljabr import centroid
import algos3d
#import posemode
import gui
import language as lang
from camera3d import Camera
import log

class PluginCheckBox(gui.CheckBox):

    def __init__(self, module):

        super(PluginCheckBox, self).__init__(module, module not in gui3d.app.settings['excludePlugins'])
        self.module = module

    def onClicked(self, event):
        if self.selected:
            gui3d.app.settings['excludePlugins'].remove(self.module)
        else:
            gui3d.app.settings['excludePlugins'].append(self.module)

        gui3d.app.saveSettings()

class PluginsTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Plugins')

        self.pluginsBox = self.addWidget(mh.addWidget(mh.Frame.LeftTop, gui.GroupBox('Plugins')))

        for module in gui3d.app.modules:
            check = self.pluginsBox.addWidget(PluginCheckBox(module))

class MHApplication(gui3d.Application, mh.Application):
    def __init__(self):
        if G.app is not None:
            raise RuntimeError('MHApplication is a singleton')
        G.app = self
        gui3d.Application.__init__(self)
        mh.Application.__init__(self)

        self.shortcuts = {
            # Actions
            (mh.Modifiers.CTRL, mh.Keys.z): self.undo,
            (mh.Modifiers.CTRL, mh.Keys.y): self.redo,
            (mh.Modifiers.CTRL, mh.Keys.m): self.goToModelling,
            (mh.Modifiers.CTRL, mh.Keys.s): self.goToSave,
            (mh.Modifiers.CTRL, mh.Keys.l): self.goToLoad,
            (mh.Modifiers.CTRL, mh.Keys.e): self.goToExport,
            (mh.Modifiers.CTRL, mh.Keys.r): self.goToRendering,
            (mh.Modifiers.CTRL, mh.Keys.h): self.goToHelp,
            (mh.Modifiers.CTRL, mh.Keys.q): self.promptAndExit,
            (mh.Modifiers.CTRL, mh.Keys.w): self.toggleStereo,
            (mh.Modifiers.CTRL, mh.Keys.f): self.toggleSolid,
            (mh.Modifiers.ALT, mh.Keys.t): self.saveTarget,
            (mh.Modifiers.ALT, mh.Keys.e): self.quickExport,
            (mh.Modifiers.ALT, mh.Keys.s): self.toggleSubdivision,
            (mh.Modifiers.ALT, mh.Keys.g): self.grabScreen,
            # Camera navigation
            (0, mh.Keys.N2): self.rotateDown,
            (0, mh.Keys.N4): self.rotateLeft,
            (0, mh.Keys.N6): self.rotateRight,
            (0, mh.Keys.N8): self.rotateUp,
            (0, mh.Keys.UP): self.panUp,
            (0, mh.Keys.DOWN): self.panDown,
            (0, mh.Keys.RIGHT): self.panRight,
            (0, mh.Keys.LEFT): self.panLeft,
            (0, mh.Keys.PLUS): self.zoomIn,
            (0, mh.Keys.MINUS): self.zoomOut,
            (0, mh.Keys.N1): self.frontView,
            (0, mh.Keys.N3): self.rightView,
            (0, mh.Keys.N7): self.topView,
            (mh.Modifiers.CTRL, mh.Keys.N1): self.backView,
            (mh.Modifiers.CTRL, mh.Keys.N3): self.leftView,
            (mh.Modifiers.CTRL, mh.Keys.N7): self.bottomView,
            (0, mh.Keys.PERIOD): self.resetView,
            # Version check
            (0, 0x12345678): self._versionSentinel
        }

        self.mouseActions = {
            (0, mh.Buttons.RIGHT_MASK): self.mouseTranslate,
            (0, mh.Buttons.LEFT_MASK): self.mouseRotate,
            (0, mh.Buttons.MIDDLE_MASK): self.mouseZoom
        }

        self.settings = {
            'realtimeUpdates': True,
            'realtimeNormalUpdates': True,
            'cameraAutoZoom': True,
            'shader': None,
            'lowspeed': 1,
            'highspeed': 5,
            'units':'metric',
            'invertMouseWheel':False,
            'font':'arial',
            'language':'english',
            'excludePlugins':[],
            'rtl': False
        }

        self.fonts = {}

        self.loadHandlers = {}
        self.saveHandlers = []

        self.dialog = None
        self.helpIds = set()

        self.modelCamera = Camera(self)

        @self.modelCamera.mhEvent
        def onChanged(event):
            for category in self.categories.itervalues():
                for task in category.tasks:
                    task.callEvent('onCameraChanged', event)

        mh.cameras.append(self.modelCamera.camera)

        self.guiCamera = Camera(self)
        self.guiCamera.fovAngle = 45
        self.guiCamera.eyeZ = 10
        self.guiCamera.projection = 0

        mh.cameras.append(self.guiCamera.camera)

    def _versionSentinel(self):
        # dummy method used for checking the shortcuts.ini version
        pass

    def loadBackground(self):
        self.progressBar.setProgress(0.1)
        mh.setClearColor(0.5, 0.5, 0.5, 1.0)

    def loadHuman(self):

        self.progressBar.setProgress(0.2)
        #hairObj = hair.loadHairsFile(self.scene3d, path="./data/hairs/default", update = False)
        #self.scene3d.clear(hairObj)
        self.selectedHuman = self.addObject(human.Human(files3d.loadMesh("data/3dobjs/base.obj")))

    def loadMainGui(self):

        self.progressBar.setProgress(0.3)

        self.tool = None
        self.selectedGroup = None

        self.undoStack = []
        self.redoStack = []
        self.modified = False

        @self.selectedHuman.mhEvent
        def onMouseDown(event):
          if self.tool:
            self.selectedGroup = self.getSelectedFaceGroup()
            self.tool.callEvent("onMouseDown", event)
          else:
            self.currentTask.callEvent("onMouseDown", event)

        @self.selectedHuman.mhEvent
        def onMouseMoved(event):
          if self.tool:
            self.tool.callEvent("onMouseMoved", event)
          else:
            self.currentTask.callEvent("onMouseMoved", event)

        @self.selectedHuman.mhEvent
        def onMouseDragged(event):
          if self.tool:
            self.tool.callEvent("onMouseDragged", event)
          else:
            self.currentTask.callEvent("onMouseDragged", event)

        @self.selectedHuman.mhEvent
        def onMouseUp(event):
          if self.tool:
            self.tool.callEvent("onMouseUp", event)
          else:
            self.currentTask.callEvent("onMouseUp", event)

        @self.selectedHuman.mhEvent
        def onMouseEntered(event):
          if self.tool:
            self.tool.callEvent("onMouseEntered", event)
          else:
            self.currentTask.callEvent("onMouseEntered", event)

        @self.selectedHuman.mhEvent
        def onMouseExited(event):
          if self.tool:
            self.tool.callEvent("onMouseExited", event)
          else:
            self.currentTask.callEvent("onMouseExited", event)

        @self.selectedHuman.mhEvent
        def onChanging(event):

            for category in self.categories.itervalues():

                for task in category.tasks:

                    task.callEvent('onHumanChanging', event)

        @self.selectedHuman.mhEvent
        def onChanged(event):

            for category in self.categories.itervalues():

                for task in category.tasks:

                    task.callEvent('onHumanChanged', event)

        @self.selectedHuman.mhEvent
        def onTranslated(event):

            for category in self.categories.itervalues():

                for task in category.tasks:

                    task.callEvent('onHumanTranslated', event)

        @self.selectedHuman.mhEvent
        def onRotated(event):

            for category in self.categories.itervalues():

                for task in category.tasks:

                    task.callEvent('onHumanRotated', event)

        @self.selectedHuman.mhEvent
        def onShown(event):

            for category in self.categories.itervalues():

                for task in category.tasks:

                    task.callEvent('onHumanShown', event)

        @self.selectedHuman.mhEvent
        def onHidden(event):

            for category in self.categories.itervalues():

                for task in category.tasks:

                    task.callEvent('onHumanHidden', event)

        # Set up categories and tasks

        self.addCategory(guimodelling.ModellingCategory())
        self.addCategory(guifiles.FilesCategory())

    def loadPlugins(self):

        self.progressBar.setProgress(0.4)

        # Load plugins not starting with _
        self.modules = {}

        self.pluginsToLoad = glob.glob(join("plugins/",'[!_]*.py'))
        self.pluginsToLoad.sort()
        self.pluginsToLoad.reverse()

        while self.pluginsToLoad:
            self.loadNextPlugin()
            yield

    def loadNextPlugin(self):

        alreadyLoaded = len(self.modules)
        stillToLoad = len(self.pluginsToLoad)
        self.progressBar.setProgress(0.4 + (float(alreadyLoaded) / float(alreadyLoaded + stillToLoad)) * 0.4)

        if not stillToLoad:
            return

        path = self.pluginsToLoad.pop()
        try:
            name, ext = splitext(basename(path))
            if name not in self.settings['excludePlugins']:
                log.message('Importing plugin %s', name)
                module = imp.load_source(name, path)
                self.modules[name] = module
                log.message('Imported plugin %s', name)
                log.message('Loading plugin %s', name)
                module.load(self)
                log.message('Loaded plugin %s', name)
            else:
                self.modules[name] = None
        except Exception, e:
            log.warning('Could not load %s', name, exc_info=True)

    def unloadPlugins(self):

        for name, module in self.modules.iteritems():
            try:
                log.message('Unloading plugin %s', name)
                module.unload(self)
                log.message('Unloaded plugin %s', name)
            except Exception, e:
                log.warning('Could not unload %s', name, exc_info=True)

    def loadGui(self):

        self.progressBar.setProgress(0.9)

        category = self.getCategory('Settings')
        category.addTask(PluginsTaskView(category))

        # Exit button
        category = self.addCategory(gui3d.Category(self, "Exit"))
        @category.tab.mhEvent
        def onClicked(event):
            self.promptAndExit()

        self.buttonBox = mh.addWidget(mh.Frame.RightBottom, gui.GroupBox('Edit'))
        self.undoButton  = self.buttonBox.addWidget(gui.Button("Undo"),  0, 0)
        self.redoButton  = self.buttonBox.addWidget(gui.Button("Redo"),  0, 1)
        self.resetButton = self.buttonBox.addWidget(gui.Button("Reset"), 0, 2)

        @self.undoButton.mhEvent
        def onClicked(event):
            gui3d.app.undo()

        @self.redoButton.mhEvent
        def onClicked(event):
            gui3d.app.redo()

        @self.resetButton.mhEvent
        def onClicked(event):
            human = self.selectedHuman
            human.resetMeshValues()
            human.applyAllTargets(self.progress)


            mh.setCaption("MakeHuman r" + os.environ['SVNREVISION'] + " - [Untitled]")

        self.globalButton = self.buttonBox.addWidget(gui.Button("Global cam"), 1, 0, 1, -1)
        self.faceButton = self.buttonBox.addWidget(gui.Button("Face cam"), 2, 0, 1, -1)
        self.imagesButton = self.buttonBox.addWidget(gui.CheckBox("Slider images", gui.Slider.imagesShown()), 3, 0, 1, -1)

        @self.globalButton.mhEvent
        def onClicked(event):
          gui3d.app.setGlobalCamera()

        @self.faceButton.mhEvent
        def onClicked(event):
          gui3d.app.setFaceCamera()

        @self.imagesButton.mhEvent
        def onClicked(event):
            gui.Slider.showImages(self.imagesButton.selected)
            mh.refreshLayout()

        """
        self.poseModeBox = self.buttonBox.addWidget(gui.CheckBox("Pose mode", False))

        @self.poseModeBox.mhEvent
        def onClicked(event):
          print dir(event)
          if self.poseModeBox.selected:
            posemode.exitPoseMode()
          else:
            posemode.enterPoseMode()
        """

        self.switchCategory("Modelling")

        self.progressBar.setProgress(1.0)
        # self.progressBar.hide()

    def loadFinish(self):

        self.selectedHuman.applyAllTargets(gui3d.app.progress)
        self.selectedHuman.callEvent('onChanged', human.HumanEvent(self.selectedHuman, 'reset'))

        self.prompt('Warning', 'This is an alpha release, which means that there are still bugs present and features missing. Use at your own risk.',
            'OK', helpId='alphaWarning')
        # self.splash.hide()

        mh.setCaption("MakeHuman r" + os.environ['SVNREVISION'] + " - [Untitled]")

        #printtree(self)

        mh.updatePickingBuffer();
        self.redraw()

    def startupSequence(self):
        self.splash.setFormat('<br><br><b><font size="48" color="#ff0000">%s</font></b>')
        old_stdout = sys.stdout
        sys.stdout = self.splash
        yield None

        log.message('Loading background')
        self.loadBackground()
        yield None

        log.message('Loading human')
        self.loadHuman()
        yield None

        log.message('Loading main GUI')
        self.loadMainGui()
        yield None

        log.message('Loading plugins')
        for _ in self.loadPlugins():
            yield None
        yield None

        log.message('Loading GUI')
        self.loadGui()
        yield None

        log.message('Loading done')
        self.loadFinish()
        yield None

        log.message('')
        yield None

        sys.stdout = old_stdout
        self.splash.finish(self.mainwin)

    def nextStartupTask(self):
        if not next(self.tasks, True):
            mh.callAsync(self.nextStartupTask)

    # Events
    def onStart(self, event):
        self.tasks = self.startupSequence()
        self.nextStartupTask()

    def onStop(self, event):

        self.saveSettings()
        self.unloadPlugins()
        self.dumpMissingStrings()

    def onQuit(self, event):

        self.promptAndExit()

    def onMouseDragged(self, event):

        if self.selectedHuman.isVisible():

            # Normalize modifiers
            modifiers = mh.getKeyModifiers() & (mh.Modifiers.CTRL | mh.Modifiers.ALT | mh.Modifiers.SHIFT)

            if (modifiers, event.button) in self.mouseActions:
                self.mouseActions[(modifiers, event.button)](event)

    def onMouseWheel(self, event):

        if self.selectedHuman.isVisible():

            zoomOut = event.wheelDelta > 0
            if gui3d.app.settings.get('invertMouseWheel', False):
                zoomOut = not zoomOut

            if zoomOut:
                self.zoomOut()
            else:
                self.zoomIn()

    def onKeyDown(self, event):

        # Normalize modifiers
        modifiers = event.modifiers & (mh.Modifiers.CTRL | mh.Modifiers.ALT)

        if modifiers & mh.Modifiers.CTRL:
            modifiers |= mh.Modifiers.CTRL
        if modifiers & mh.Modifiers.ALT:
            modifiers |= mh.Modifiers.ALT

        # Normalize key
        key = event.key

        if (modifiers, key) in self.shortcuts:
            self.shortcuts[(modifiers, key)]()

    # Undo-redo
    def do(self, action):
        if action.do():
            self.undoStack.append(action)
            del self.redoStack[:]
            self.modified = True
            log.message('do %s', action.name)
            self.redraw()

    def did(self, action):
        self.undoStack.append(action)
        self.modified = True
        del self.redoStack[:]
        log.message('did %s', action.name)
        self.redraw()

    def undo(self):
        if self.undoStack:
            action = self.undoStack.pop()
            log.message('undo %s', action.name)
            action.undo()
            self.redoStack.append(action)
            self.modified = True
            self.redraw()

    def redo(self):
        if self.redoStack:
            action = self.redoStack.pop()
            log.message('redo %s', action.name)
            action.do()
            self.undoStack.append(action)
            self.modified = True
            self.redraw()

    # Settings

    def loadSettings(self):
        try:
            if os.path.isfile(os.path.join(mh.getPath(''), "settings.ini")):
                f = open(os.path.join(mh.getPath(''), "settings.ini"), 'r')
                settings = eval(f.read(), {"__builtins__":None}, {'True':True, 'False':False})
                self.settings.update(settings)
                f.close()
        except:
            log.error('Failed to load settings')

        if 'language' in gui3d.app.settings:
            self.setLanguage(gui3d.app.settings['language'])

        try:
            if os.path.isfile(os.path.join(mh.getPath(''), "shortcuts.ini")):
                shortcuts = self.shortcuts.copy()
                self.shortcuts = {}
                f = open(os.path.join(mh.getPath(''), "shortcuts.ini"), 'r')
                for line in f:
                    modifier, key, method = line.split(' ')
                    #print modifier, key, method[0:-1]
                    if hasattr(self, method[0:-1]):
                        self.shortcuts[(int(modifier), int(key))] = getattr(self, method[0:-1])
                f.close()
                if (0, 0x12345678) not in self.shortcuts:
                    log.warning('shortcuts.ini out of date; ignoring')
                    self.shortcuts = shortcuts
        except:
            log.error('Failed to load shortcut settings')

        try:
            if os.path.isfile(os.path.join(mh.getPath(''), "mouse.ini")):
                self.mouseActions = {}
                f = open(os.path.join(mh.getPath(''), "mouse.ini"), 'r')
                for line in f:
                    modifier, button, method = line.split(' ')
                    #print modifier, button, method[0:-1]
                    if hasattr(self, method[0:-1]):
                        self.mouseActions[(int(modifier), int(button))] = getattr(self, method[0:-1])
                f.close()
        except:
            log.error('Failed to load mouse settings')

        try:
            if os.path.isfile(os.path.join(mh.getPath(''), "help.ini")):
                self.helpIds = set()
                f = open(os.path.join(mh.getPath(''), "help.ini"), 'r')
                for line in f:
                    self.helpIds.add(line[0:-1])
                f.close()
                if self.dialog is not None:
                    self.dialog.helpIds.update(self.helpIds)
        except:
            log.error('Failed to load help settings')

    def saveSettings(self):
        if not os.path.exists(mh.getPath('')):
            os.makedirs(mh.getPath(''))

        f = open(os.path.join(mh.getPath(''), "settings.ini"), 'w')
        f.write(repr(self.settings))
        f.close()

        f = open(os.path.join(mh.getPath(''), "shortcuts.ini"), 'w')
        for shortcut, method in self.shortcuts.iteritems():
            f.write('%d %d %s\n' % (shortcut[0], shortcut[1], method.__name__))
        f.close()

        f = open(os.path.join(mh.getPath(''), "mouse.ini"), 'w')
        for mouseAction, method in self.mouseActions.iteritems():
            f.write('%d %d %s\n' % (mouseAction[0], mouseAction[1], method.__name__))
        f.close()

        if self.dialog is not None:
            self.helpIds.update(self.dialog.helpIds)
        f = open(os.path.join(mh.getPath(''), "help.ini"), 'w')
        for helpId in self.helpIds:
            f.write('%s\n' % helpId)
        f.close()

    # Themes
    def setTheme(self, theme):

        f = open(os.path.join("data/themes/", theme + ".mht"), 'r')

        for data in f.readlines():
            lineData = data.split()

            if len(lineData) > 0:
                if lineData[0] == "version":
                    log.message('Version %s', lineData[1])
                elif lineData[0] == "color":
                    if lineData[1] == "clear":
                        mh.setClearColor(float(lineData[2]), float(lineData[3]), float(lineData[4]), float(lineData[5]))

        self.theme = theme

    def getThemeResource(self, folder, id):
        if '/' in id:
            return id
        path = os.path.join("data/themes/", self.theme, folder, id)
        if os.path.exists(path):
            return path
        else:
            return os.path.join("data/themes/default/", folder, id)

    def setLanguage(self, language):
        lang.language.setLanguage(language)
        self.settings['rtl'] = lang.language.rtl

    def getLanguageString(self, string):
        return lang.language.getLanguageString(string)

    def dumpMissingStrings(self):
        lang.language.dumpMissingStrings()

    # Font resources
    def getFont(self, fontFamily):
        if fontFamily not in self.fonts:
            self.fonts[fontFamily] = font3d.Font("data/fonts/%s.fnt" % fontFamily)

        return self.fonts[fontFamily]

    # Caption
    def setCaption(self, caption):
        mh.setCaption(caption.encode('utf8'))

    # Global status bar
    def status(self, text, permanent=False):
        if self.statusBar is None:
            return
        self.statusBar.showMessage(text, permanent)

    # Global progress bar
    def progress(self, value, text=None):
        if text is not None:
            self.status(text)

        if self.progressBar is None:
            return

        if value >= 1.0:
            self.progressBar.reset()
        else:
            self.progressBar.setProgress(value)

        self.processEvents()

    # Global dialog
    def prompt(self, title, text, button1Label, button2Label=None, button1Action=None, button2Action=None, helpId=None):
        if self.dialog is None:
            self.dialog = gui.Dialog(self.mainwin)
            self.dialog.helpIds.update(self.helpIds)
        self.dialog.prompt(title, text, button1Label, button2Label, button1Action, button2Action, helpId)

    # Camera's
    def setCameraCenterViewDistance(self, center, view='front', distance=10):

        human = self.selectedHuman
        tl = animation3d.Timeline(0.20)
        cam = self.modelCamera
        if view == 'front':
            tl.append(animation3d.CameraAction(self.modelCamera, None,
                [center[0], center[1], distance,
                center[0], center[1], 0,
                0, 1, 0]))
        elif view == 'top':
            tl.append(animation3d.CameraAction(self.modelCamera, None,
                [center[0], center[1] + distance, center[2],
                center[0], center[1], center[2],
                0, 0, -1]))
        elif view == 'left':
            tl.append(animation3d.CameraAction(self.modelCamera, None,
                [center[0] - distance, center[1], center[2],
                center[0], center[1], center[2],
                0, 1, 0]))
        elif view == 'right':
            tl.append(animation3d.CameraAction(self.modelCamera, None,
                [center[0] + distance, center[1], center[2],
                center[0], center[1], center[2],
                0, 1, 0]))
        tl.append(animation3d.PathAction(human, [human.getPosition(), [0.0, 0.0, 0.0]]))
        tl.append(animation3d.RotateAction(human, human.getRotation(), [0.0, 0.0, 0.0]))
        tl.append(animation3d.UpdateAction(self))
        tl.start()

    def setCameraGroupsViewDistance(self, groupNames, view='front', distance=10):

        human = self.selectedHuman
        vertices = human.meshData.getCoords(human.meshData.getVerticesForGroups(groupNames))
        center = centroid(vertices)

        self.setCameraCenterViewDistance(center, view, distance)

    def setGlobalCamera(self):

        human = self.selectedHuman

        tl = animation3d.Timeline(0.20)
        cam = self.modelCamera
        tl.append(animation3d.CameraAction(self.modelCamera, None, [0,0,60, 0,0,0, 0,1,0]))
        tl.append(animation3d.PathAction(human, [human.getPosition(), [0.0, 0.0, 0.0]]))
        tl.append(animation3d.RotateAction(human, human.getRotation(), [0.0, 0.0, 0.0]))
        tl.append(animation3d.UpdateAction(self))
        tl.start()

    def setTargetCamera(self, names, view='front', distance=10):
        human = self.selectedHuman
        groupNames = [group.name
                      for group in human.meshData.faceGroups
                      if any(name in group.name for name in names)]
        self.setCameraGroupsViewDistance(groupNames, view, distance)

    def setFaceCamera(self):
        self.setTargetCamera(("head", "jaw"))

    def setLeftHandFrontCamera(self):
        self.setTargetCamera("l-hand")

    def setLeftHandTopCamera(self):
        self.setTargetCamera("l-hand", 'top')

    def setRightHandFrontCamera(self):
        self.setTargetCamera("r-hand")

    def setRightHandTopCamera(self):
        self.setTargetCamera("r-hand", 'top')

    def setLeftFootFrontCamera(self):
        self.setTargetCamera("l-foot")

    def setLeftFootLeftCamera(self):
        self.setTargetCamera("l-foot", 'left')

    def setRightFootFrontCamera(self):
        self.setTargetCamera("r-foot")

    def setRightFootRightCamera(self):
        self.setTargetCamera("r-foot", 'right')

    def setLeftArmFrontCamera(self):
        self.setTargetCamera(("l-lowerarm", "l-upperarm"), distance=30)

    def setLeftArmTopCamera(self):
        self.setTargetCamera(("l-lowerarm", "l-upperarm"), top, distance=30)

    def setRightArmFrontCamera(self):
        self.setTargetCamera(("r-lowerarm", "r-upperarm"), distance=30)

    def setRightArmTopCamera(self):
        self.setTargetCamera(("r-lowerarm", "r-upperarm"), top, distance=30)

    def setLeftLegFrontCamera(self):
        self.setTargetCamera(("l-lowerleg", "l-upperleg"), distance=30)

    def setLeftLegLeftCamera(self):
        self.setTargetCamera(("l-lowerleg", "l-upperleg"), left, distance=30)

    def setRightLegFrontCamera(self):
        self.setTargetCamera(("r-lowerleg", "r-upperleg"), distance=30)

    def setRightLegRightCamera(self):
        self.setTargetCamera(("r-lowerleg", "r-upperleg"), right, distance=30)

    # Shortcuts
    def setShortcut(self, modifier, key, method):

        shortcut = (modifier, key)

        if shortcut in self.shortcuts:
            self.prompt('Warning', 'This combination is already in use. Change the combination for the action which has reserved this shortcut', 'OK', helpId='shortcutWarning')
            return False

        # Remove old entry
        for s, m in self.shortcuts.iteritems():
            if m == method:
                del self.shortcuts[s]
                break

        self.shortcuts[shortcut] = method

        #for shortcut, m in self.shortcuts.iteritems():
        #    print shortcut, m

        return True

    def getShortcut(self, method):

        for shortcut, m in self.shortcuts.iteritems():
            if m == method:
                return shortcut

    # Mouse actions
    def setMouseAction(self, modifier, key, method):

        mouseAction = (modifier, key)

        if mouseAction in self.mouseActions:
            self.prompt('Warning', 'This combination is already in use. Change the combination for the action which has reserved this mouse action', 'OK', helpId='mouseActionWarning')
            return False

        # Remove old entry
        for s, m in self.mouseActions.iteritems():
            if m == method:
                del self.mouseActions[s]
                break

        self.mouseActions[mouseAction] = method

        #for mouseAction, m in self.mouseActions.iteritems():
        #    print mouseAction, m

        return True

    def getMouseAction(self, method):

        for mouseAction, m in self.mouseActions.iteritems():
            if m == method:
                return mouseAction

    # Load handlers

    def addLoadHandler(self, keyword, handler):
        self.loadHandlers[keyword] = handler

    # Save handlers

    def addSaveHandler(self, handler):
        self.saveHandlers.append(handler)

    # Shortcut methods

    def goToModelling(self):
        self.switchCategory("Modelling")
        self.redraw()

    def goToSave(self):
        self.switchCategory("Files")
        self.switchTask("Save")
        self.redraw()

    def goToLoad(self):
        self.switchCategory("Files")
        self.switchTask("Load")
        self.redraw()

    def goToExport(self):
        self.switchCategory("Files")
        self.switchTask("Export")
        self.redraw()

    def goToRendering(self):
        self.switchCategory("Rendering")
        self.redraw()

    def goToHelp(self):
        self.switchCategory("Help")

    def toggleStereo(self):
        stereoMode = self.modelCamera.stereoMode
        stereoMode += 1
        if stereoMode > 2:
            stereoMode = 0
        self.modelCamera.stereoMode = stereoMode

        # We need a black background for stereo
        if stereoMode:
            mh.setClearColor(0.0, 0.0, 0.0, 1.0)
            self.categories["Modelling"].anaglyphsButton.setSelected(True)
        else:
            mh.setClearColor(0.5, 0.5, 0.5, 1.0)
            self.categories["Modelling"].anaglyphsButton.setSelected(False)

        self.redraw()

    def toggleSolid(self):
        self.selectedHuman.setSolid(not self.selectedHuman.isSolid())
        self.redraw()

    def toggleSubdivision(self):
        self.selectedHuman.setSubdivided(not self.selectedHuman.isSubdivided(), True, self.progress)
        self.redraw()

    def saveTarget(self):
        human = self.selectedHuman
        algos3d.saveTranslationTarget(human.meshData, "full_target.target")
        log.message("Full target exported")

    def quickExport(self):
        exportPath = mh.getPath('exports')
        if not os.path.exists(exportPath):
            os.makedirs(exportPath)
        import mh2obj
        mh2obj.exportObj(self.selectedHuman.meshData, exportPath + '/quick_export.obj')
        import mh2bvh
        mh2bvh.exportSkeleton(self.selectedHuman.meshData, exportPath + '/quick_export.bvh')
        import mh2mhx
        mh2mhx.exportMhx(self.selectedHuman.meshData, exportPath + '/quick_export.mhx')

    def grabScreen(self):
        grabPath = mh.getPath('grab')
        if not os.path.exists(grabPath):
            os.makedirs(grabPath)
        # TODO: use bbox to choose grab region
        mh.grabScreen(180, 80, 440, 440, os.path.join(grabPath, 'grab.bmp'))

    # Camera navigation
    def rotateCamera(self, axis, amount):
        human = self.selectedHuman
        rot = human.getRotation()
        rot[axis] += amount
        human.setRotation(rot)
        self.redraw()

    def panCamera(self, axis, amount):
        human = self.selectedHuman
        trans = human.getPosition()
        trans[axis] += amount
        human.setPosition(trans)
        self.redraw()

    def cameraSpeed(self):
        if mh.getKeyModifiers() & mh.Modifiers.SHIFT:
            return gui3d.app.settings.get('highspeed', 5)
        else:
            return gui3d.app.settings.get('lowspeed', 1)

    def zoomCamera(self, amount):
        self.modelCamera.eyeZ += amount * self.cameraSpeed()
        self.redraw()

    def rotateAction(self, axis):
        return animation3d.RotateAction(self.selectedHuman, self.selectedHuman.getRotation(), axis)

    def axisView(self, axis):
        animation3d.animate(self, 0.20, [self.rotateAction(axis)])

    def rotateDown(self):
        self.rotateCamera(0, 5.0)

    def rotateLeft(self):
        self.rotateCamera(0, -5.0)

    def rotateRight(self):
        self.rotateCamera(1, 5.0)

    def rotateUp(self):
        self.rotateCamera(1, -5.0)

    def panUp(self):
        self.panCamera(1, 0.05)

    def panDown(self):
        self.panCamera(1, -0.05)

    def panRight(self):
        self.panCamera(0, 0.05)

    def panLeft(self):
        self.panCamera(0, -0.05)

    def zoomOut(self):
        self.zoomCamera(0.65)

    def zoomIn(self):
        self.zoomCamera(-0.65)

    def frontView(self):
        self.axisView([0.0, 0.0, 0.0])

    def rightView(self):
        self.axisView([0.0, -90.0, 0.0])

    def topView(self):
        self.axisView([90.0, 0.0, 0.0])

    def backView(self):
        self.axisView([0.0, 180.0, 0.0])

    def leftView(self):
        self.axisView([0.0, 90.0, 0.0])

    def bottomView(self):
        self.axisView([-90.0, 0.0, 0.0])

    def resetView(self):
        cam = self.modelCamera
        animation3d.animate(self, 0.20, [
            self.rotateAction([0.0, 0.0, 0.0]),
            animation3d.CameraAction(cam, None, [cam.eyeX, cam.eyeY, 60.0, cam.focusX, cam.focusY, cam.focusZ, 0, 1, 0])])

    # Mouse actions
    def mouseTranslate(self, event):

        speed = self.cameraSpeed()

        human = self.selectedHuman
        trans = human.getPosition()
        trans = self.modelCamera.convertToScreen(trans[0], trans[1], trans[2])
        trans[0] += event.dx * speed
        trans[1] += event.dy * speed
        trans = self.modelCamera.convertToWorld3D(trans[0], trans[1], trans[2])
        human.setPosition(trans)

    def mouseRotate(self, event):

        speed = self.cameraSpeed()

        human = self.selectedHuman
        rot = human.getRotation()
        rot[0] += 0.5 * event.dy * speed
        rot[1] += 0.5 * event.dx * speed
        human.setRotation(rot)

    def mouseZoom(self, event):

        speed = self.cameraSpeed()

        if gui3d.app.settings.get('invertMouseWheel', False):
            speed *= -1

        self.modelCamera.eyeZ -= 0.05 * event.dy * speed

    def promptAndExit(self):
        if self.modified:
            self.prompt('Exit', 'You have unsaved changes. Are you sure you want to exit the application?', 'Yes', 'No', self.stop)
        else:
            self.stop()

    def OnInit(self):
        mh.Application.OnInit(self)

        self.setTheme("default")
        #self.setTheme("3d")
        self.setLanguage("english")

        self.loadSettings()

        self.splash = gui.SplashScreen(gui3d.app.getThemeResource('images', 'splash.png'))
        self.splash.show()

        # Display the initial splash screen and the progress bar during startup
        # mesh = gui3d.RectangleMesh(800, 600, gui3d.app.getThemeResource('images', 'splash.png'))
        # self.splash = self.addObject(gui3d.Object([0, 0, 9.8], mesh))
        self.statusBar = mh.addWidget(mh.Frame.Bottom, gui.StatusBar())
        self.statusBar.show()
        self.progressBar = mh.addWidget(mh.Frame.Bottom, gui.ProgressBar())

        self.tabs = self.mainwin.tabs

        @self.tabs.mhEvent
        def onTabSelected(tab):
            self.switchCategory(tab.name)

    def run(self):
        self.start()