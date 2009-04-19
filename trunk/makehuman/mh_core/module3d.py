# You may use, modify and redistribute this module under the terms of the GNU GPL.
"""
Base 3D MakeHuman classes.

===========================  ===============================================================
Project Name:                **MakeHuman**
Module File Location:        mh_core/module3d.py
Product Home Page:           http://www.makehuman.org/
SourceForge Home Page:       http://sourceforge.net/projects/makehuman/
Authors:                     Manuel Bastioni,  Marc Flerackers, Paolo Colombo
Copyright(c):                MakeHuman Team 2001-2009
Licensing:                   GPL3 (see also http://makehuman.wiki.sourceforge.net/Licensing)
Coding Standards:            See http://makehuman.wiki.sourceforge.net/DG_Coding_Standards
===========================  ===============================================================

This module contains all of the base classes needed to manage the 3D MakeHuman
data structures at runtime. This includes the data structures themselves as well
as methods to handle their manipulation in memory. For example, the Vert class
defines the data structures to hold information about mesh vertices objects,
while the Face class defines data structures to hold information about mesh face
objects.

These base classes implement a nested hierarchical structure for the objects
that make up the scene that is shown to the user. For example, a FaceGroup
object contains groups of mesh face objects as defined by the Face class. An
Object3D object contains all of the FaceGroup objects that go to make up a
particular discrete object, such as the humanoid body or one of the GUI
controls. The Scene3D object contains all of the Object3D objects that go
to make up the entire scene.

"""
#.. include:: docs/includes/example1.txt

__docformat__ = 'restructuredtext'


import mh
import aljabr
import time
from types import *
import os

textureCache = {}

class Texture:
        def __init__(self, id, modified):
            self.id = id
            self.modified = modified

class Vert:
    """
    A 3D vertex object. This object records the 3D location and surface normal
    of the vertex and an RGBA color value. It also records references to
    other related data objects.

    Vertex information from this object is passed into the OpenGL 3D
    engine via the C code in *glmodule.c*, which uses the glDrawArray
    OpenGL function to draw objects.

    A single Python Vert object is usually used for all of the faces within a 
    given face group that share that same vertex. The exception to this is 
    where the UV-data used to define the object (as read in from an obj file) 
    used more than one UV-index for the same vertex index, in which case a 
    copy of the vertex exists for each unique UV-index. You can therefore get
    multiple (not usually more than 2) Python Vert objects sharing the same 
    coordinates, but different UV-mapping data, color etc.
    
    However, the OpenGL code considers a vertex shared by multiple faces to
    be multiple vertices. So, a Vert object that appears once on the Python
    vertex list may appear multiple times on the C vertex list.

    For example: Two faces share the edge 'v2-v3'. One face is defined by
    vertices v1, v2 and v3, and the other face is defined by vertices
    v3, v2, and v4. The Python vertex list could contain four vertices:

      [v1,v2,v3,v4]

    However, the C vertex list will repeat vertices that are shared by more
    than one face. So, the C vertex list will be based on the list:

      [v1,v2,v3,v3,v2,v4]

    In addition, the C vertex list is actually an expanded coordinate list,
    containing each coordinate of each vertex (x, y, and z) in one long list
    (stored as a one dimensional array):

      [v1x,v1y,v1z,v2x,v2y,v2z,v3x,v3y,v3z,v3x,v3y,v3z,v2x,v2y,v2z,v4x,v4y,v4z]

    Similarly, the four color components (r, g, b, and a) of each vertex are
    stored in the C vertex color list.

    Each Python Vert object contains a list attribute, *indicesInFullVertArray*,
    listing the various locations where the vertex appears in the C vertex list.
    This allows information held against a single Vert object in Python to be
    copied to multiple locations in the coordinate and color lists in the
    C-based OpenGL world. See the description of the *update* method, below,
    for more detail about how the information in the Python-based Vert class is
    translated to the lists used by OpenGL.

    Basic usage:
    ------------

    ::

        import module3d

        x,y,z = 1,1,1
        v = module3d.Vert([x,y,z])
        v.update()
    """

    def __init__(self, co = [0, 0, 0], idx=0, obIdx=0, sfidx = []):
        """
        This is the constructor method for the Vert class. It initializes the
        following attributes:

        - **self.co**: *float list*. The coordinates of the vertex.
          Default: [coX, coY, coZ]).
        - **self.no**: *float list*. The normal of this vertex (or 0).
          Default: [0, 0, 0].
        - **self.objID**: *int*. The index of the object of which this vertex is a part.
          Default: 0
        - **self.sharedFacesIndices**: *faces list*. The list of faces that share this vertex.
        - **self.sharedFaces**: *faces list*. The list of faces that share this vertex.
        - **self.indicesInFullVertArray**: *Int list*. The list of corresponding vertices in the C OpenGL list.
        - **self.idx**: *Int* The index of this vertex in the vertices list.
        - **self.color**: *float list*. A list of 4 floats [r,g,b,a] used as the vertex color (including an alpha channel).

        Parameters
        ----------

        coX:
            *float*. The x coordinate of the vertex. Default is 0.

        coY:
            *float*. The y coordinate of the vertex. Default is 0.

        coZ:
            *float*. The z coordinate of the vertex. Default is 0.

        idx:
            *int*. The index of this vertex in the vertices list. Default is 0.

        obIdx:
            *int*. The index of the Object3D object that uses this vertex. Default is 0.

        sfidx:
            *int list*. A list of indices of faces that share this vertex. Default is empty.

        """

        self.co = co
        self.no = [0,0,0]
        self.objID = obIdx
        self.sharedFacesIndices = sfidx
        self.sharedFaces = []
        self.indicesInFullVertArray = []
        self.idx = idx
        self.color = [255,255,255,255]


    def update(self,updateNor=1,updateCoo=1,updateCol=None,colorIndexToUpdate=None):
        """
        This method updates the coordinates, normal and/or color of a vertex in the C
        OpenGL world, based upon the values currently held in the Python Vert class.

        The vertex indexing system in the Python code differs from the
        OpenGL vertex indexing system used in the C code, as discussed in the description
        of this *Vert* class (see above).

          - In Python, a single vertex can be shared by multiple faces. In OpenGL, there
            are always multiple copies of any such vertex.
          - Vertex information is expanded, so the x, y and z coordinates
            that are stored for a vertex in the Vert class take up 3 times as many
            positions in the OpenGL coordinate list (and rgba color values
            take 4 times as many index positions).

        Because one Python Vert object can appear multiple times in the C vertex list,
        each Python Vert object has an attribute, *indicesInFullVertArray*, which lists
        the conceptual 'index' in the C lists of coordinates and colors.

        From this 'conceptual' index, we can find where the vertex's coordinates lie in the full C
        coordinate list. Because each vertex has three coordinates (x, y, and z), the
        coordinate list will be three times as long as this 'conceptual' index. So, a vertex
        listed in the *indicesInFullVertArray* at positions 1 and 4 (the second and fifth
        positions) will have its coordinates listed on the C coordinates list at
        positions 3, 4, and 5, and again at positions 12, 13, and 14. Or:

          (n*3), (n*3)+1, (n*3)+2   for both n = 1 and n = 4.

        The C color list is similar to the coordinate list. As each color is defined by
        four components 'red, green, blue, and alpha (transparency)' the C color list is
        four times as long as this 'conceptual' index. So, a vertex listed in the
        *indicesInFullVertArray* at positions 1 and 4 will have its color component values listed in the C
        color list at positions 4, 5, 6, and 7, and again at positions 16, 17, 18, and
        19. Or:

          (n*4), (n*4)+1, (n*4)+2, (n*4)+3   for both n = 1 and n = 4.

        The color passed into this method can originate from various sources, depending upon what the
        color is to represent at this moment in time. Colors can be manipulated to indicate 
        faces or vertices that have been selected, to indicate morph target strengths at different 
        locations on the model or control or to show base colors.
        
        When updating the color information, this method usually sets all vertex colors in the C array
        that were derived from a single Python Vert object to be the same color. 
        **Editorial Note. The colorIndexToUpdate Parameter seems to allow for only a single C vertex
        to be updated, but there don't seem to be any method calls that use this parameter.**

        Parameters
        ----------

        updateNor:
            *int*. If anything other than None, the normal will be updated.

        updateCoo:
            *int*. If anything other than None, the coords will be updated.

        updateCol:
            *int*. If anything other than None, the color will be updated.

        colorIndexToUpdate:
            *int*. If specified, this parameter is used as the index of a color
            in the C array of colors. A vertex can be shared by various faces
            and it's possible to assign it different colors on different faces.
            If this parameter is left to default to 'None' the default color
            index will be calculated based on the index of the vertex.

        """

        if updateCoo:
            for i in self.indicesInFullVertArray:
                mh.setVertCoord(self.objID, i, self.co)
        if updateNor:
            for i in self.indicesInFullVertArray:
                mh.setNormCoord(self.objID, i, self.no)

        if updateCol:
            if colorIndexToUpdate == None:
                for i in self.indicesInFullVertArray:
                    mh.setColorCoord2(self.objID, i, self.color)
            else:
                mh.setColorCoord2(self.objID, colorIndexToUpdate, self.color)


    def calcNorm(self):
        """
        This method calculates the vertex surface normal based upon a mathematical average
        of the physical normals of all faces sharing this vertex. This results in a smooth surface.

        .. image:: ../images/vert_norm.png

        The physical normal of a surface is a direction vector at right angles
        to that surface. Although the triangular mesh consists of a series of flat
        faces, the surface normal calculated for a vertex averages out the
        physical normals of the faces that share that vertex, enabling the
        rendering engine (OpenGL) to shade the object so that the surface looks
        like a single, smooth shape.

        Note for API developers
        -----------------------

        Because the actual 3D engine uses optimized glDrawElements,
        where each vertex can have only one normal, it is impossible
        in MakeHuman to draw the geometry in a "flat" mode.

        MakeHuman is organically oriented, so the benefits of using this optimized technique
        outweigh potential performance costs.

        **Parameters:** This method has no parameters.

        """
        
        no = [0.0, 0.0, 0.0]
        for f in self.sharedFaces:
            no[0] += f.no[0]
            no[1] += f.no[1]
            no[2] += f.no[2]
        self.no = aljabr.vnorm(no)

    def vertsShared(self):
        """
        This method returns a list of the vertices of all faces that share this vertex.

        .. image:: ../images/vert_shared.png

        If processing the vector V in the image above this function would return [v1,v2,v3,v4,v5,v6,v7]

        **Parameters:** This method has no parameters.

        """

        sharedVertices = {}
        for f in self.sharedFaces:
            for v in f.verts:
                sharedVertices[v.idx] = v
        return sharedVertices.values()

    def __str__(self):
        """
        This method returns a string listing the index of the vertex and the
        x, y, and z coordinates of this vertex. This method is called when 
        the vertex object is passed to the 'print' function.

        **Parameters:** This method has no parameters.

        """
        return "vert num %s, coord(%s,%s,%s)"%(self.idx,self.co[0],self.co[1],self.co[2])


class Face:
    """
    A face object. In MakeHuman, all face objects are triangular.

    Basic usage:
    ------------

    ::

        import module3d

        v1 = module3d.Vert([1,0,0])
        v2 = module3d.Vert([0,1,0])
        v3 = module3d.Vert([0,0,1])

        f = module3d.Face(v1,v2,v3)
    """

    def __init__(self,v0,v1,v2):
        """
        This is the constructor method for the Face class.
        It initializes the following attributes:

        - **self.no**: *float list* The physical surface normal of the face (x,y,z). Default: [0, 0, 0].
        - **self.verts**: *verts list* A list of 3 vertices that represent the corners of this face.
        - **self.idx**: *int* The index of this face in the list of faces.
        - **self.group**: *FaceGroup* The face group that is the parent of this face.
        - **self.color**: *list of list of ints*. A list of 3 lists of 4 integers (0-255)
          [[r,g,b,a],[r,g,b,a],[r,g,b,a]] used as the 3 vertex colors (including an alpha channel).
        - **self.colorID**: *list of list of ints*. A list of 3 integers (0-255) [index1,index2,index3]
          used as a 'selection' color.
        - **self.uv**: *list of list of floats*. A list of a 3 lists of 2 floats [[u,v],[u,v],[u,v]]
          holding the UV coordinates for the uv-mapping of textures to this face.

        Parameters
        ----------

        v0:
            *vert*. First vertex of face

        v1:
            *vert*. Second vertex of face

        v2:
            *vert*. Third vertex of face

        """
        self.no = [0.0,0.0,0.0]
        self.verts = [v0,v1,v2]
        self.uv = None
        self.color = None
        self.colorID = [255,255,255]
        self.idx = None
        self.group = None


    def calcNormal(self):
        """
        This method calculates the physical surface normal of the face using the planeNorm function from
        the aljabr.py module. This results in a direction vector at right angles to the
        two edges vt2_vt1 and vt2_vt3.

        **Parameters:** This method has no parameters.

        """
        vt1 = self.verts[0].co
        vt2 = self.verts[1].co
        vt3 = self.verts[2].co
        self.no = aljabr.planeNorm(vt1,vt2,vt3)


    def updateColors(self):
        """
        This method updates the color attributes for each vertex on this face.
        """
        #The position of color index to update in C color array
        #is given by the index of face * 3 * 4
        #because for each face we have 3 verts, and for each vert we have
        #4 floats R,G,B,A.

        for i,v in enumerate(self.verts):
            v.color = self.color[i]
            for index in v.indicesInFullVertArray:
                v.update(0,0,1)
        

    def __str__(self):
        """
        This method returns a string listing the index of the face and the
        indices of the three vertices. This method is called when the face
        object is passed to the 'print' function.

        **Parameters:** This method has no parameters.

        """
        return "face %i: verts: %i, %i, %i" % (self.idx, self.verts[0].idx,
            self.verts[1].idx,self.verts[2].idx)


class FaceGroup:
    """
    A FaceGroup (a group of faces with a unique name).

    Each Face object can be part of one FaceGroup. Each face object has an
    attribute, *group*, storing the FaceGroup it is a member of.

    The FaceGroup object contains a list of the faces in the group and must be
    kept in sync with the FaceGroup references stored by the individual faces.

    """

    def __init__(self,name):
        """
        This is the constructor method for the FaceGroup class.
        It initializes the following attributes:

        - **self.name**: *string*. The name of this FaceGroup.
        - **self.faces**: *faces list*. A list of faces. Default: empty.
        - **self.parent**: *Object3d*. The object3D object that contains this FaceGroup. Default: None.

        Parameters
        ----------

        name:
            *string* The name of this FaceGroup.
        """

        self.name = name
        self.faces = []
        self.parent = None
        self.elementIndex = 0
        self.elementCount = 0

    def __str__(self):
        """
        This method returns a string containing the name of the FaceGroup. This
        method is called when the object is passed to the 'print' function.

        **Parameters:** This method has no parameters.

        """
        return "facegroup %s"%(self.name)




class Object3D:
    """
    A 3D object, made up of faces and vertices (i.e. containing Face objects and Vert objects).
    The humanoid object manipulated by the MakeHuman application is an instance of this
    class, as are all the GUI controls. Multiple 3D objects can be added to the 3D scene.

    This object has a position and orientation of its own, and the positions and
    orientations of faces and vertices that make up this object are defined relative to
    it.

    """

    def __init__(self, objName):
        """
        This is the constructor method for the Object3D class.
        It initializes the following attributes:

        - **self.name**: *string* The name of this Object3D object.
        - **self.idx**: *int* The ID used to identify the object in the OpenGL engine array.
        - **self.x**: *float* The x coordinate of the position of this object in the coordinate space of the scene.
        - **self.y**: *float* The y coordinate of the position of this object in the coordinate space of the scene.
        - **self.z**: *float* The z coordinate of the position of this object in the coordinate space of the scene.
        - **self.rx**: *float* The x rotation component of the orientation of this object within the coordinate space of the scene.
        - **self.ry**: *float* The y rotation component of the orientation of this object within the coordinate space of the scene.
        - **self.rz**: *float* The z rotation component of the orientation of this object within the coordinate space of the scene.
        - **self.sx**: *float* The x scale component of the size of this object within the coordinate space of the scene.
        - **self.sy**: *float* The y scale component of the size of this object within the coordinate space of the scene.
        - **self.sz**: *float* The z scale component of the size of this object within the coordinate space of the scene.
        - **self.r**: *int* The Red channel component of the color ID of this object.
        - **self.g**: *int* The Green channel component of the color ID of this object.
        - **self.b**: *int* The Blue channel component of the color ID of this object.
        - **self.verts**: *verts list* The list of vertices that go to make up this object.
        - **self.faces**: *faces list* The list of faces that go to make up this object.
        - **self.facesGroups**: *facesGroups list* The list of FaceGroups that go to make up this object.
        - **self.cameraMode**: *int flag* A flag to indicate which of the two available perspective camera projections, fixed or movable, is to be used to draw this object.
        - **self.visibility**: *int flag* A flag to indicate whether or not this object is visible.
        - **self.texture**: *string* The path of a TGA file on disk containing the object texture.
        - **self.isSelected**: *int flag* A flag to indicate whether this object is currently selected.
        - **self.faceGroupSelected**: *string* The name of actually selected face group.
        - **self.shadeless**: *int flag* A flag to indicate whether this object is unaffected by variations in lighting (certain GUI elements aren't).
        - **self.lMousePressedCallBack**:
        - **self.rMousePressedCallBack**:
        - **self.lMouseReleasedCallBack**:
        - **self.rMouseReleasedCallBack**:
        - **self.mouseMotionCallBack**:
        - **self.isSubdivided**: *int flag* A flag to indicate whether this object is subdivided or not.
        - **self.indexBuffer**: *faces list* The list of faces as indices to the vertexbuffer.
        - **self.vertexBufferSize**: *int* size in vertices of the vertexbuffer.
        - **self.uvValues**: *uv list* The list of uv values referenced to by the faces.
        - **self.text**: string* A text to be printed near the obj

        Parameters
        ----------

        objName:
            *string* The name of the object. This name is used to reference this object in the scene3D dictionary.

        """

        self.name = objName
        self.idx = None
        self.x = 0
        self.y = 0
        self.z = 0
        self.rx = 0
        self.ry = 0
        self.rz = 0
        self.sx = 1
        self.sy = 1
        self.sz = 1
        self.r = 155
        self.g = 155
        self.b = 155
        self.verts = []
        self.faces = []
        self.facesGroups = []
        self.cameraMode = 1
        self.visibility = 1
        self.texture = None
        #self.colors = []
        self.isSelected = None
        self.faceGroupSelected = None
        self.shadeless = 0
        self.lMousePressedCallBack = None
        self.rMousePressedCallBack = None
        self.lMouseReleasedCallBack = None
        self.rMouseReleasedCallBack = None
        self.mouseWheelUpCallBack = None
        self.mouseWheelDownCallBack = None
        self.mouseMotionCallBack = None
        self.isSubdivided = None
        self.indexBuffer = []
        self.vertexBufferSize = None
        self.uvValues = None
        self.text = ""

    #def runCallback(self):
    #    self.callBack()

    def setLoc(self,locx,locy,locz):
        """
        This method is used to set the location of the object in the 3D coordinate space of the scene.

        Parameters
        ----------

        locx:
            *float*. The x coordinate of the object.
        locy:
            *float*. The y coordinate of the object.
        locz:
            *float*. The z coordinate of the object.
        """
        self.x = locx
        self.y = locy
        self.z = locz
        try:
            mh.setObjLocation(self.idx, self.x, self.y, self.z)
        except IndexError, text:
            print(text)
        #TODO: try-except for all setXxx
        

    def setRot(self,rx,ry,rz):
        """
        This method sets the orientation of the object in the 3D coordinate space of the scene.

        Parameters
        ----------

        rx:
            *float*. Rotation around the x-axis.
        ry:
            *float*. Rotation around the y-axis.
        rz:
            *float*. Rotation around the z-axis.
        """
        self.rx = rx
        self.ry = ry
        self.rz = rz
        mh.setObjRotation(self.idx, self.rx, self.ry, self.rz)

    def setScale(self,sx,sy,sz):
        """
        This method sets the scale of the object in the 3D coordinate space of
        the scene, relative to the initially defined size of the object.

        Parameters
        ----------

        sx:
            *float*. Scale along the x-axis.
        sy:
            *float*. Scale along the y-axis.
        sz:
            *float*. Scale along the z-axis.
        """
        self.sx = sx
        self.sy = sy
        self.sz = sz
        mh.setObjScale(self.idx, self.sx, self.sy, self.sz)

    def setVisibility(self,visib):
        """
        This method sets the visibility of the object.

        Parameters
        ----------

        visib:
            *int flag*. Whether or not the object is visible. 0=Visible, 1=Invisible.
        """
        self.visibility = visib
        try:
            mh.setVisibility(self.idx, visib)
        except IndexError, text:
            print(text)

    def setTexture(self, path):
        """
        This method is used to specify the path of a TGA file on disk containing the object texture.

        Parameters
        ----------

        path:
            *string* The path of a texture TGA file.
        """
        self.texture = path
        print("loading " + path);
        if path in textureCache:
            if os.stat(path).st_mtime != textureCache[path].modified:
                try:
                    mh.LoadTexture(path, textureCache[path].id)
                except RuntimeError, text:
                    print(text)
                    return;
                else:
                    textureCache[path].modified = os.stat(path).st_mtime
            
            try:                
                mh.setObjTexture(self.idx, textureCache[path].id)
            except IndexError, text:
                print(text)
        else:
            texture = None
            try:
                texture = mh.LoadTexture(path, 0)
            except RuntimeError, text:
                print(text)
            else:
                try:
                    textureCache[path] = Texture(texture, os.stat(path).st_mtime)
                    mh.setObjTexture(self.idx, texture)
                except IndexError, text:
                    print(text)
    
            
    def clearTexture(self):
        """
        This method is used to clear an object's texture.

        **Parameters:** This method has no parameters.
        
        """
        self.texture = None
        mh.setObjTexture(self.idx, 0)

    def setShadeless(self,shadeVal):
        """
        This method is used to specify whether or not the object is affected by lights.
        This is used for certain GUI controls to give them a more 2D type
        appearance (predominantly the top bar of GUI controls).

        Parameters
        ----------

        shadeVal:
            *int* Whether or not the object is unaffected by lights. If 0, it is affected by lights; if 0, it is not.

        """
        self.shadeless = shadeVal
        try:                
            mh.setShadeless(self.idx, self.shadeless)
        except IndexError, text:
            print(text)
        

    def setText(self,text):
        """
        Ths method sets the text to print on the object.

        Parameters
        ----------

        text:
            *string* The text to print on the object.

        """
        self.text = text
        try:
            mh.setText(self.idx, self.text)
        except IndexError, text:
            print(text)
        

    def addFaceGroup(self, fg):
        """
        This method adds a FaceGroup to this object.

        Parameters
        ----------

        fg:
            *faceGroups list* The FaceGroup to add.
        """
        fg.parent= self
        self.facesGroups.append(fg)

    def getFaceGroup(self, name):
        """
        This method searches the list of FaceGroups held for this object, and
        returns the FaceGroup with the specified name. If no FaceGroup is found
        for that name, this method returns None.

        Parameters
        ----------

        name:
            *string*  The name of the FaceGroup to retrieve.
        """
        for fg in self.facesGroups:
            if fg.name == name:
                return fg
        return None

    def setCameraProjection(self,mode):
        """
        This method sets the camera mode used to visualize this object (fixed or movable).
        The 3D engine has two camera modes (both perspective modes).
        The first is moved by the mouse, while the second is fixed.
        The first is generally used to model 3D objects (a human, clothes,
        etc.), while the second is used for 3D GUI controls.

        Parameters
        ----------

        mode:
            *int*  The camera mode to be used for this object. 0 = fixed camera; 1 = movable camera
        """
        self.cameraMode = mode        
        try:
            mh.setCameraMode(self.idx,mode)
        except IndexError, text:
            print(text)


    def update(self,indexToUpdate = []):
        """
        This method is used to call the update methods on each of a list of vertices that form part of this object.

        Parameters
        ----------

        indexToUpdate:
            *int list*  The list of vertex indices to update

        """
        for i in indexToUpdate:
            v = self.verts[i]
            v.update()

    def applySelectionColor(self):
        """
        This method applies the 'selection' color to all of the vertices within this object.

        Selection of a vertex is indicated on the screen by increasing
        the Red color component and decreasing the Green and Blue color
        components by a fixed amount (50) and then capping the value so
        that it remains within the bounds of 0-255.

        **Parameters:** This method has no parameters.

        """

        for v in self.verts:
            v.color[0] += 50
            v.color[1] -= 50
            v.color[2] -= 50
            if v.color[0] > 255:
                v.color[0] = 255
            if v.color[1] < 0:
                v.color[1] = 0
            if v.color[2] < 0:
                v.color[2] = 0
            v.update(0,0,1)


    def applyDefaultColor(self):
        """
        This method applies the color white to all of the vertices within this object.

        **Parameters:** This method has no parameters.

        """

        for v in self.verts:
            v.color = [255,255,255,255]
            v.update(0,0,1)


    def calcNormals(self,indexToUpdate = None, facesToRecalcNorm = None, recalcNorms = None):
        """
        This method calls the calcNormal method for a subset of the faces
        in this Object3D object and the calcNorm method on a subset of the
        vertices in this Object3D object.

        If no faces are specified the face normals are not recalculated. If the
        recalcNorms flag is set to None the vertex normals are not recalculated.
        If 'None' is specified for the vertex indices then all vertex indices
        are recalculated (so long as recalcNorms is not set to None).

        The calcNormal method of a face will recalculate the actual physical
        surface normal.
        The calcNorm method of a vertex calculates the vertex's surface normal
        as an average of the  physical surface normals of the faces that share
        that vertex.

        Parameters
        ----------

        indexToUpdate:
            *int list*  The list of indices pointing to the vertices that need to be updated.

        facesToRecalcNorm:
            *int list*  The list of indices pointing to the faces to be updated.

        recalcNorms:
            *flag*  A flag to indicate whether or not the vertex normals should be recalculated.
            If set to anything other than None, the vertex normals are recalculated.
            Otherwise only need the face normals are recalculated.

        """

        if indexToUpdate == None:
            indexToUpdate = range(len(self.verts))

        if facesToRecalcNorm:
            for i in facesToRecalcNorm:
                self.faces[i].calcNormal()
        if recalcNorms:
            for i in indexToUpdate:
                self.verts[i].calcNorm()

    def __str__(self):
        """
        This method returns a string containing the object name, the number of
        vertices, the number of faces, and the location of the object. It is
        called when the object is passed to the 'print' function.

        **Parameters:** This method has no parameters.

        """

        return "object3D named: %s, nverts: %s, nfaces: %s, at |%s,%s,%s|" % \
                (self.name,len(self.verts),len(self.faces),self.x,self.y,self.z)

class Scene3D:
    """
    A 3D object that stores the contents of a scene (made up primarily of
    one or more Object3D objects).
    As a minimum the MakeHuman scene usually consists of a humanoid object
    that can be manipulated by the MakeHuman application, plus a set of 3D GUI
    controls.

    Multiple 3D model objects can theoretically be added to the 3D scene.
    Future versions of MakeHuman are likely to support multiple humanoid
    objects, and potentially separate objects such as clothing and props.

    MakeHuman Selectors
    -------------------

    This object supports the use of a technique called *Selection Using Unique
    Color IDs*, that internally uses color-coding of components within the
    scene to support the selection of objects by the user using the mouse.

    This technique generates a sequence of colors (color IDs), assigning a
    unique color to each uniquely selectable object or component in the scene.
    These colors are not displayed, but are used by MakeHuman to generates an
    unseen image of the various selectable elements. This image uses the same
    camera settings currently being used for the actual, on-screen image.
    When the mouse is clicked, the position of the mouse is used with the
    unseen image to retrieve a color. MakeHuman uses this color as an ID to
    identify which object or component the user clicked with the mouse.

    This technique uses glReadPixels() to read the single pixel at the
    current mouse location, using the unseen, color-coded image.

    For further information on this technique, see:

      - http://www.opengl.org/resources/faq/technical/selection.htm and
      - http://wiki.gamedev.net/index.php/OpenGL_Selection_Using_Unique_Color_IDs

    **Note.** Because the 3D engine uses glDrawElements in a highly opimized
    way and each vertex can have only one color ID, there there is a known
    problem with selecting individual faces with very small FaceGroups using
    this technique. However, this is not a major problem for MakeHuman, which
    doesn't use such low polygon groupings.


    """

    def __init__(self):
        """
        This is the constructor method for the Scene3D class.
        It initializes the following attributes:

        - **self.objects**: *3Dobject list* A list of the 3D objects in the scene.
        - **self.faceGroupColorID**: *Dictionary of colors IDs* A dictionary of the color IDs used for
          selection (see MakeHuman Selectors, above).
        - **self.colorID**: *float list* A progressive color ID.
        - **self.sceneLMousePressedCallBack**: *function* Event handling function. Initially None.
        - **self.sceneRMousePressedCallBack**: *function* Event handling function. Initially None.
        - **self.sceneLMouseReleasedCallBack**: *function* Event handling function. Initially None.
        - **self.sceneRMouseReleasedCallBack**: *function* Event handling function. Initially None.
        - **self.sceneMouseWheelUpCallBack**: *function* Event handling function. Initially None.
        - **self.sceneMouseWheelDownCallBack**: *function* Event handling function. Initially None.
        - **self.sceneMouseMotionCallback**: *function* Event handling function. Initially None.
        - **self.sceneMousePassiveMotionCallback**: *function* Event handling function. Initially None.
        - **self.sceneKeyboardCallback**: *function* Event handling function. Initially None.
        - **self.sceneUpArrowCallback**: *function* Event handling function. Initially None.
        - **self.sceneDownArrowCallback**: *function* Event handling function. Initially None.
        - **self.sceneLeftArrowCallback**: *function* Event handling function. Initially None.
        - **self.sceneRightArrowCallback**: *function* Event handling function. Initially None.
        - **self.sceneLCTRLCallback**: *function* Event handling function. Initially None.
        - **self.sceneRCTRLCallback**: *function* Event handling function. Initially None.
        - **self.sceneLSHIFTCallback**: *function* Event handling function. Initially None.
        - **self.sceneRSHIFTCallback**: *function* Event handling function. Initially None.
        - **self.sceneLALTCallback**: *function* Event handling function. Initially None.
        - **self.sceneTimerCallback**: *function* Event handling function. Initially None.
        - **self.keyboardEventsDict**: *array* Dictionary of keyboard events. Initially empty.
        - **self.keyPressed**: *function* Event handling function. Initially None.
        - **self.characterPressed**: *function* Event handling function. Initially None.
        - **self.mouseState**: *int* The current state of the mouse. Initially 0.
        - **self.mouseX**: *int* Mouse position X value. Initially 0.
        - **self.mouseY**: *int* Mouse position Y value. Initially 0.
        - **self.mouseXRel**: *int* Mouse released position X value. Initially 0.
        - **self.mouseYRel**: *int* Mouse released position Y value. Initially 0.
        - **self.KP0**: *int* Key code 256.
        - **self.KP1**: *int* Key code 257.
        - **self.KP2**: *int* Key code 258.
        - **self.KP3**: *int* Key code 259.
        - **self.KP4**: *int* Key code 260.
        - **self.KP5**: *int* Key code 261.
        - **self.KP6**: *int* Key code 262.
        - **self.KP7**: *int* Key code 263.
        - **self.KP8**: *int* Key code 264.
        - **self.KP9**: *int* Key code 265.
        - **self.KP_PERIOD**: *int* Key code 266.
        - **self.KP_DIVIDE**: *int* Key code 267.
        - **self.KP_MULTIPLY**: *int* Key code 268.
        - **self.KP_MINUS**: *int* Key code 269.
        - **self.KP_PLUS**: *int* Key code 270.
        - **self.KP_ENTER**: *int* Key code 271.
        - **self.KP_EQUALS**: *int* Key code 272.
        - **self.UP_ARROW**: *int* Key code 273.
        - **self.DOWN_ARROW**: *int* Key code 274
        - **self.LEFT_ARROW**: *int* Key code 276.
        - **self.RIGHT_ARROW**: *int* Key code 275.
        - **self.RIGHT_SHIFT**: *int* Key code 303.
        - **self.LEFT_SHIFT**: *int* Key code 304.
        - **self.RIGHT_CTRL**: *int* Key code 305.
        - **self.LEFT_CTRL**: *int* Key code 306.
        - **self.RIGHT_ALT**: *int* Key code 307.
        - **self.LEFT_ALT**: *int* Key code 308.
        
        The attributes *self.colorID* and *self.faceGroupColorID*
        support a technique called *Selection Using Unique Color IDs* to make each
        FaceGroup independently clickable.

        The attribute *self.colorID* stores a progressive color that is incremented for each successive
        FaceGroup added to the scene.
        The *self.faceGroupColorID* attribute contains a list that serves as a directory to map
        each color back to the corresponding FaceGroup by using its color ID.

        **Parameters:** This method has no parameters.

        """
        self.objects = []
        self.faceGroupColorID = {}
        self.colorID = [0,0,0]
        self.sceneLMousePressedCallBack = None
        self.sceneRMousePressedCallBack = None
        self.sceneLMouseReleasedCallBack = None
        self.sceneRMouseReleasedCallBack = None
        self.sceneMouseWheelUpCallBack = None
        self.sceneMouseWheelDownCallBack = None
        self.sceneMouseMotionCallback = None
        self.sceneMousePassiveMotionCallback = None
        self.sceneKeyboardCallback = None
        self.sceneUpArrowCallback = None
        self.sceneDownArrowCallback = None
        self.sceneLeftArrowCallback = None
        self.sceneRightArrowCallback = None
        self.sceneLCTRLCallback = None
        self.sceneRCTRLCallback = None
        self.sceneLSHIFTCallback = None
        self.sceneRSHIFTCallback = None
        self.sceneLALTCallback = None
        self.sceneTimerCallback = None
        self.keyboardEventsDict = {}
        self.keyPressed = None
        self.characterPressed = None
        self.mouseState = 0
        self.mouseX = 0
        self.mouseY = 0
        self.mouseXRel = 0
        self.mouseYRel = 0
        self.KP_RETURN = 13
        self.KP0 = 256
        self.KP1 = 257
        self.KP2 = 258
        self.KP3 = 259
        self.KP4 = 260
        self.KP5 = 261
        self.KP6 = 262
        self.KP7 = 263
        self.KP8 = 264
        self.KP9 = 265
        self.KP_PERIOD = 266
        self.KP_DIVIDE = 267
        self.KP_MULTIPLY = 268
        self.KP_MINUS = 269
        self.KP_PLUS = 270
        self.KP_ENTER = 271
        self.KP_EQUALS = 272
        self.UP_ARROW = 273
        self.DOWN_ARROW = 274
        self.LEFT_ARROW = 276
        self.RIGHT_ARROW = 275
        self.RIGHT_SHIFT = 303
        self.LEFT_SHIFT = 304
        self.RIGHT_CTRL = 305
        self.LEFT_CTRL = 306
        self.RIGHT_ALT = 307
        self.LEFT_ALT= 308
        

    def __str__(self):
        """
        This method is the Print method for a Scene3D object, which returns a string containing the words
        "scene_type".

        **Parameters:** This method has no parameters.

        """
        return "scene_type"

    def update(self):
        """
        This method sends scene data to the OpenGL engine to regenerate the OpenGL scene based on the objects
        currently contained in this Scene3D object.
        This is a very important function, but it is expensive in terms of processing time, so it must be called
        only when absolutely necessary; in particular, when one or more new objects are added to the scene.

        If you only need to *redraw* the scene, use the scene.redraw() method instead.

        **Parameters:** This method has no parameters.

        """
        a = time.time()

        nObjs = len(self.objects)
        self.colorID = [0,0,0]#reset the colors selection ID

        #Free all memory
        mh.init3DScene(nObjs)

        #Re-send all
        for obj in self.objects:
            self.assignSelectionID(obj)
            #print "sending: ", obj.name, obj.idx, len(obj.verts)
            coIdx = 0
            fidx = 0
            uvIdx = 0
            colIdx = 0
            mh.addObj(obj.idx, obj.x, obj.y, obj.z, obj.vertexBufferSize, obj.indexBuffer)  # create an object with vertexBufferSize vertices and len(indexBuffer) / 3 triangles
            mh.setCameraMode(obj.idx,obj.cameraMode)
            mh.setShadeless(obj.idx, obj.shadeless)
            
            for g in obj.facesGroups:
                groupVerts = {};
                for f in g.faces:
                    faceColor = f.color
                    if faceColor == None:
                        faceColor = [[255,255,255,255],[255,255,255,255],[255,255,255,255]]
                    fUV = f.uv
                    if fUV == None:
                        fUV = [-1,-1,-1]
                                
                    i = 0
                    for v in f.verts:
                        if v.idx not in groupVerts:
                            mh.setAllCoord(obj.idx, coIdx, colIdx, v.co, v.no, f.colorID, faceColor[i])
                            groupVerts[v.idx] = set()
                            groupVerts[v.idx].add(fUV[i])
                            
                            coIdx += 1
                            colIdx += 1
                            
                            if obj.uvValues:
                                mh.setUVCoord(obj.idx, uvIdx, obj.uvValues[fUV[i]])
                                uvIdx += 1
                            
                        elif fUV[i] not in groupVerts[v.idx]:
                            mh.setAllCoord(obj.idx, coIdx, colIdx, v.co, v.no, f.colorID, faceColor[i])
                            groupVerts[v.idx].add(fUV[i])
                            
                            coIdx += 1
                            colIdx += 1
                            
                            if obj.uvValues:
                                mh.setUVCoord(obj.idx, uvIdx, obj.uvValues[fUV[i]])
                                uvIdx += 1
                            
                        i += 1
                        
            if obj.texture:
                obj.setTexture(obj.texture)
                
            mh.setObjLocation(obj.idx, obj.x, obj.y, obj.z)
            mh.setVisibility(obj.idx, obj.visibility)
            mh.setCameraMode(obj.idx,obj.cameraMode)
            mh.setText(obj.idx, obj.text)
            #TODO add all obj attributes
            

        print "Regeneration done in" + str(time.time()-a)
        
    def reloadTextures(self):
        print("Reloading textures")
        for path in textureCache:
            try:
                mh.LoadTexture(path, textureCache[path].id)
            except RuntimeError, text:
                    print(text)


    def connect(self,eventName,functionToCall,obj = None):
        """
        This method connects an event handling function for a specific event
        to a specific object in the scene. This can be to one of the Object3D
        objects within the scene, or to this Scene3D object.
        The event is indicated using an event name passed in as a string
        ("LMOUSEP", "RMOUSEP", "LMOUSER", "RMOUSER" or "MOTION"). The name of
        the callback function is assigned to the corresponding callback
        attribute on the object.

        Parameters
        ----------

        eventName:
            *string* The name of the event to connect to a callback function.
        functionToCall:
            *string* The name of the callback function to connect to the event.
        obj:
            *object reference* The object to which to connect the callback function.

        """
        if obj:
            if eventName == "LMOUSEP":
                if obj.lMousePressedCallBack != None:
                    print "Warning, object %s has already LMOUSEP event"%(obj.name)
                    print "function %s not assigned to %s"%(functionToCall,obj.name)
                    return
                else:
                    obj.lMousePressedCallBack = functionToCall
            elif eventName == "RMOUSEP":
                if obj.rMousePressedCallBack != None:
                    print "Warning, object %s has already RMOUSEP event"%(obj.name)
                    print "function %s not assigned to %s"%(functionToCall,obj.name)
                    return
                else:
                    obj.rMousePressedCallBack = functionToCall
            elif eventName == "LMOUSER":
                if obj.lMouseReleasedCallBack != None:
                    print "Warning, object %s has already LMOUSER event"%(obj.name)
                    print "function %s not assigned to %s"%(functionToCall,obj.name)
                    return
                else:
                    obj.lMouseReleasedCallBack = functionToCall
            elif eventName == "RMOUSER":
                if obj.rMouseReleasedCallBack != None:
                    print "Warning, object %s has already RMOUSER event"%(obj.name)
                    print "function %s not assigned to %s"%(functionToCall,obj.name)
                    return
                else:
                    obj.rMouseReleasedCallBack = functionToCall
            elif eventName == "MOUSEWHEELUP":
                if obj.mouseWheelUpCallBack != None:
                    print "Warning, object %s has already MOUSEWHEELUP event"%(obj.name)
                    print "function %s not assigned to %s"%(functionToCall,obj.name)
                    return
                else:
                    obj.mouseWheelUpCallBack = functionToCall
            elif eventName == "MOUSEWHEELDOWN":
                if obj.mouseWheelDownCallBack != None:
                    print "Warning, object %s has already MOUSEWHEELDOWN event"%(obj.name)
                    print "function %s not assigned to %s"%(functionToCall,obj.name)
                    return
                else:
                    obj.mouseWheelDownCallBack = functionToCall
            elif eventName == "MOTION":
                obj.mouseMotionCallBack = functionToCall
        else:
            if eventName == "LMOUSEP":
                if self.sceneLMousePressedCallBack != None:
                    print "Warning, scene has already event LMOUSEP"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneLMousePressedCallBack = functionToCall
            elif eventName == "RMOUSEP":
                if self.sceneRMousePressedCallBack != None:
                    print "Warning, scene has already event RMOUSEP"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneRMousePressedCallBack = functionToCall
            elif eventName == "LMOUSER":
                if self.sceneLMouseReleasedCallBack != None:
                    print "Warning, scene has already event LMOUSER"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneLMouseReleasedCallBack = functionToCall
            elif eventName == "RMOUSER":
                if self.sceneRMouseReleasedCallBack != None:
                    print "Warning, scene has already event RMOUSER"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneRMouseReleasedCallBack = functionToCall
            elif eventName == "MOUSEWHEELUP":
                if self.sceneMouseWheelUpCallBack != None:
                    print "Warning, scene has already event MOUSEWHEELUP"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneMouseWheelUpCallBack = functionToCall
            elif eventName == "MOUSEWHEELDOWN":
                if self.sceneMouseWheelDownCallBack != None:
                    print "Warning, scene has already event MOUSEWHEELDOWN"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneMouseWheelDownCallBack = functionToCall
            elif eventName == "MOTION":
                if self.sceneMouseMotionCallback != None:
                    print "Warning, scene has already event MOTION"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneMouseMotionCallback = functionToCall
            elif eventName == "PMOTION":
                if self.sceneMousePassiveMotionCallback != None:
                    print "Warning, scene has already event PMOTION"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneMousePassiveMotionCallback = functionToCall
            elif eventName == "KEYBOARD":
                if self.sceneKeyboardCallback != None:
                    print "Warning, scene has already event KEYBOARD"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneKeyboardCallback = functionToCall
            elif eventName == "UP_ARROW":
                if self.sceneUpArrowCallback != None:
                    print "Warning, scene has already event UP_ARROW"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneUpArrowCallback = functionToCall
            elif eventName == "DOWN_ARROW":
                if self.sceneDownArrowCallback != None:
                    print "Warning, scene has already event DOWN_ARROW"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneDownArrowCallback = functionToCall
            elif eventName == "LEFT_ARROW":
                if self.sceneLeftArrowCallback != None:
                    print "Warning, scene has already event LEFT_ARROW"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneLeftArrowCallback = functionToCall
            elif eventName == "RIGHT_ARROW":
                if self.sceneRightArrowCallback != None:
                    print "Warning, scene has already event RIGHT_ARROW"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneRightArrowCallback = functionToCall
            elif eventName == "TIMER":
                if self.sceneTimerCallback != None:
                    print "Warning, scene has already event IDLE"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneTimerCallback = functionToCall
            elif eventName == "LEFT_CTRL":
                if self.sceneLCTRLCallback != None:
                    print "Warning, scene has already event LEFT_CTRL"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneLCTRLCallback = functionToCall
            elif eventName == "RIGHT_CTRL":
                if self.sceneRCTRLCallback != None:
                    print "Warning, scene has already event RIGHT_CTRL"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneRCTRLCallback = functionToCall
            elif eventName == "LEFT_SHIFT":
                if self.sceneLSHIFTCallback != None:
                    print "Warning, scene has already event LEFT_SHIFT"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneLSHIFTCallback = functionToCall
            elif eventName == "RIGHT_SHIFT":
                if self.sceneRSHIFTCallback != None:
                    print "Warning, scene has already event RIGHT_SHIFT"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneRSHIFTCallback = functionToCall
            elif eventName == "LEFT_ALT":
                if self.sceneLALTCallback != None:
                    print "Warning, scene has already event LEFT_ALT"
                    print "function %s not assigned to event"%(functionToCall)
                else:
                    self.sceneLALTCallback = functionToCall
                    
            else:
                if type(eventName) is StringType and len(eventName) == 1:
                    eventName = ord(eventName)
                if type(eventName) is IntType:
                    self.keyboardEventsDict[eventName] = functionToCall

    def disconnect(self,eventName,obj = None):
        """
        This method disconnects an event handling function for a specific event
        from a specific object in the scene. This can be from one of the Object3D
        objects within the scene, or from this Scene3D object.
        The event is indicated using an event name passed in as a string
        ("LMOUSEP", "RMOUSEP", "LMOUSER", "RMOUSER" or "MOTION"). The name of
        the callback function for the corresponding callback attribute on the 
        object is set to None.

        Parameters
        ----------

        eventName:
            *string* The name of the event to disconnect from a callback function.
        obj:
            *object reference* The object to which the callback function is connected.

        """
        if obj:
            if eventName == "LMOUSEP":
                obj.lMousePressedCallBack = None
            elif eventName == "RMOUSEP":
                obj.rMousePressedCallBack = None
            elif eventName == "LMOUSER":
                obj.lMouseReleasedCallBack = None
            elif eventName == "RMOUSER":
                obj.rMouseReleasedCallBack = None
            elif eventName == "MOUSEWHEELUP":
                obj.mouseWheelUpCallBack = None
            elif eventName == "MOUSEWHEELDOWN":
                obj.mouseWheelDownCallBack = None
            elif eventName == "MOTION":
                obj.mouseMotionCallBack = None
        else:
            if eventName == "LMOUSEP":
                self.sceneLMousePressedCallBack = None
            elif eventName == "RMOUSEP":
                self.sceneRMousePressedCallBack = None
            elif eventName == "LMOUSER":
                self.sceneLMouseReleasedCallBack = None
            elif eventName == "RMOUSER":
                self.sceneRMouseReleasedCallBack = None
            elif eventName == "MOUSEWHEELUP":
                self.sceneMouseWheelUpCallBack = None
            elif eventName == "MOUSEWHEELDOWN":
                self.sceneMouseWheelDownCallBack = None
            elif eventName == "MOTION":
                self.sceneMouseMotionCallback = None
            elif eventName == "PMOTION":
                self.sceneMousePassiveMotionCallback = None
            elif eventName == "KEYBOARD":
                self.sceneKeyboardCallback = None
            elif eventName == "UP_ARROW":
                self.sceneUpArrowCallback = None
            elif eventName == "DOWN_ARROW":
                self.sceneDownArrowCallback = None
            elif eventName == "LEFT_ARROW":
                self.sceneLeftArrowCallback = None
            elif eventName == "RIGHT_ARROW":
                self.sceneRightArrowCallback = None
            elif eventName == "TIMER":
                self.sceneTimerCallback = None
                
            else:
                if type(eventName) is StringType and len(eventName) == 1:
                    eventName = ord(eventName)
                if type(eventName) is IntType:
                    if eventName in self.keyboardEventsDict:
                        del self.keyboardEventsDict[eventName]

    def setTimeTimer(self, millisecs):
        """
        This method calls the setTimeTimer method on the mh Python class to 
        set the timer in the C code for the timer event.
        
        Parameters
        ----------

        millisecs:
            *int* The number of milliseconds until the next timer event is triggered.

        """       
        mh.setTimeTimer(millisecs)


        
    def timerFunc(self):
        """
        This method calls the 'idle' callback function registered against
        the scene3D object if such a callback function has been defined.

        **Parameters:** This method has no parameters.

        """       
        if self.sceneTimerCallback:
            self.sceneTimerCallback()
            


    def disconnectAllEvents(self):
        """
        This method reinitializes the event callback functions registered
        against the scene3D object to 'None' so that they no longer 
        respond to events.

        **Parameters:** This method has no parameters.

        """
        self.sceneLMousePressedCallBack = None
        self.sceneRMousePressedCallBack = None
        self.sceneLMouseReleasedCallBack = None
        self.sceneRMouseReleasedCallBack = None
        self.sceneMouseWheelUpCallBack = None
        self.sceneMouseWheelDownCallBack = None
        self.sceneMouseMotionCallback = None
        self.sceneMousePassiveMotionCallback = None
        self.sceneKeyboardCallback = None
        self.keyboardEventsDict = {}
        self.sceneUpArrowCallback = None
        self.sceneDownArrowCallback = None
        self.sceneLeftArrowCallback = None
        self.sceneRightArrowCallback = None
        self.sceneLCTRLCallback = None
        self.sceneRCTRLCallback = None
        self.sceneLSHIFTCallback = None
        self.sceneRSHIFTCallback = None
        self.sceneLALTCallback = None

    def getMousePos2D(self):
        """
        This method returns the x and y mouse position in screen 
        coordinates as 2 integer values.
        It calls the getMousePos2D function on the 'mh' module 
        (a module created dynamically at run time by main.c) to retrieve the 
        x and y coordinates of the mouse position from global variables updated 
        before an event was passed up to the Python code. The mouse position is
        returned as two integer values defining the screen coordinates measured 
        from the top-left corner of the screen (the MakeHuman OpenGL viewport).

        **Parameters:** This method has no parameters.

        """
        return [self.mouseX, self.mouseY]
        #return mh.getMousePos2D()

    def getMousePos3D(self):
        """
        This method returns the x, y, z mouse position in scene coordinates as 
        3 float values.
        It calls the getMousePos3D function on the 'mh' module 
        (a module created dynamically at run time by main.c) to retrieve the 
        x, y and z coordinates of the mouse position from global variables updated 
        before an event was passed up to the Python code. The mouse position is
        returned as three float values defining the scene coordinates measured 
        from the OpenGL origin.

        **Parameters:** This method has no parameters.
        """
        return mh.getMousePos3D()

    def getMousePosGUI(self):
        """
        This method returns the x, y, z mouse position in GUI coordinates as 
        3 float values.
        It calls the getMousePosGUI function on the 'mh' module 
        (a module created dynamically at run time by main.c) to retrieve the 
        x, y and z coordinates of the mouse position from global variables updated 
        before an event was passed up to the Python code. The mouse position is
        returned as three float values defining the GUI coordinates measured 
        from the OpenGL origin.

        **Parameters:** This method has no parameters.
        """
        return mh.getMousePosGUI()
        
    def convertToScreen(self, x, y, z, camera = 0):
        """
        This method returns the screen coordinates corresponding to the specified 
        OpenGL 3D world coordinates for the camera type given.  
        
        It calls the convertToScreen function on the 'mh' module 
        (a module created dynamically at run time by main.c) to calculate these  
        coordinates.

        Parameters
        ----------

        x:
            *int* The x-coordinate of the 3D world point.
        y:
            *int* The y-coordinate of the 3D world point.
        z:
            *int* The z-coordinate of the 3D world point.
        camera:
            *int* The camera type.
        """
        return mh.convertToScreen(x, y, z, camera)
        
    def convertToWorld2D(self, x, y, camera = 0):
        """
        This method returns the OpenGL 2D world coordinates corresponding to the 
        specified screen coordinates for the camera type given.  
        
        It calls the convertToWorld2D function on the 'mh' module 
        (a module created dynamically at run time by main.c) to calculate these  
        coordinates.

        Parameters
        ----------

        x:
            *int* The x-coordinate of the screen position.
        y:
            *int* The y-coordinate of the screen position.
        camera:
            *int* The camera type.
        """
        return mh.convertToWorld2D(x, y, camera)
       
    def convertToWorld3D(self, x, y, z, camera = 0):
        """
        This method returns the OpenGL 3D world coordinates corresponding to the 
        specified screen coordinates for the camera type given.  
        
        It calls the convertToWorld3D function on the 'mh' module 
        (a module created dynamically at run time by main.c) to calculate these  
        coordinates.

        Parameters
        ----------

        x:
            *int* The x-coordinate of the screen position.
        y:
            *int* The y-coordinate of the screen position.
        z:
            *int* The z-coordinate of the 3D world point.
        camera:
            *int* The camera type.
        """
        return mh.convertToWorld3D(x, y, z, camera)    

    def getWindowSize(self):
        """
        This method returns the width and height of the drawable area within 
        the MakeHuman window in pixels (the viewport size).
        It calls the getWindowSize function on the 'mh' module 
        (a module created dynamically at run time by main.c) to retrieve the 
        width and height of the window (the OpenGL viewport) from global 
        variables updated before an event was passed up to the Python code. 

        **Parameters:** This method has no parameters.
        """
        return mh.getWindowSize()

    def mouseButtonDown(self, button, x, y):
        """
        This method processes a 'mouseButtonDown' event for this Scene3D
        object.
        If the Scene3D object has a callback function defined for this event
        it is called. Once that callback function finishes this method
        checks whether the mouse click occurred over an object in the scene.
        If it did, and that object has a callback function registered for this
        event, then that object's callback function is also called.

        **Parameters:** This method has no parameters.

        """
        self.mouseX = x
        self.mouseY = y
        
        if button == 1:
            if self.sceneLMousePressedCallBack:
                self.sceneLMousePressedCallBack()
            ob = self.getSelectedObject()
            if ob and ob.lMousePressedCallBack:
                ob.lMousePressedCallBack()
        elif button == 2:
            if self.sceneRMousePressedCallBack:
                self.sceneRMousePressedCallBack()
            ob = self.getSelectedObject()
            if ob and ob.rMousePressedCallBack:
                ob.rMousePressedCallBack()
        elif button == 4:
            if self.sceneMouseWheelUpCallBack:
                self.sceneMouseWheelUpCallBack()
            ob = self.getSelectedObject()
            if ob and ob.mouseWheelUpCallBack:
                ob.mouseWheelUpCallBack()
        elif button == 5:
            if self.sceneMouseWheelDownCallBack:
                self.sceneMouseWheelDownCallBack()
            ob = self.getSelectedObject()
            if ob and ob.mouseWheelDownCallBack:
                ob.mouseWheelDownCallBack()

    def mouseButtonUp(self, button, x, y):
        """
        This method processes a 'mouseButtonUp' event for this Scene3D
        object.
        If the Scene3D object has a callback function defined for this event
        it is called. Once that callback function finishes this method checks
        whether the mouse button release occurred over an object in the scene.
        If it did, and that object has a callback function registered for this
        event, then that objects callback function is also called.

        **Parameters:** This method has no parameters.

        """
        self.mouseX = x
        self.mouseY = y
        
        if button == 1:
            if self.sceneLMouseReleasedCallBack:
                self.sceneLMouseReleasedCallBack()
            ob = self.getSelectedObject()
            if ob and ob.lMouseReleasedCallBack:
                ob.lMouseReleasedCallBack()
        elif button == 2:
            if self.sceneRMouseReleasedCallBack:
                self.sceneRMouseReleasedCallBack()
            ob = self.getSelectedObject()
            if ob and ob.rMouseReleasedCallBack:
                ob.rMouseReleasedCallBack()

    def mouseMotion(self, mouseState, x, y, xRel, yRel):
        """
        This method processes a 'mouseMotion' event for this Scene3D
        object. Depending on the state of the mouse buttons, it is
        translated to a passive or normal motion event.
        If the Scene3D object has a callback function defined for this event
        it is called.

        **Parameters:** This method has no parameters.

        """
        
        self.mouseState = mouseState
        self.mouseX = x
        self.mouseY = y
        self.mouseXRel = xRel
        self.mouseYRel = yRel
        
        if mouseState:
            if self.sceneMouseMotionCallback:
                self.sceneMouseMotionCallback()
        else:
            if self.sceneMousePassiveMotionCallback:
                self.sceneMousePassiveMotionCallback()

    def keyDown(self, key, character):
        """
        This method processes a 'keyDown' event for this Scene3D
        object.
        If the Scene3D object has a callback function defined for this event
        it is called.

        Parameters
        ----------

        key:
            *string* A single character string containing the key pressed.
        x:
            *integer* The distance, in pixels, of the mouse pointer from the
            left edge of the viewport.
        y:
            *integer* The distance, in pixels, of the mouse pointer from the
            top edge of the viewport.

        """
        print(key, character)
        self.keyPressed = key
        self.characterPressed = character
        if self.sceneKeyboardCallback:
            self.sceneKeyboardCallback()
        if key in self.keyboardEventsDict:
            function = self.keyboardEventsDict[key]
            function()
        if self.sceneUpArrowCallback and key == self.UP_ARROW:
            self.sceneUpArrowCallback()
        if self.sceneDownArrowCallback and key == self.DOWN_ARROW:
            self.sceneDownArrowCallback()
        if self.sceneLeftArrowCallback and key == self.LEFT_ARROW:
            self.sceneLeftArrowCallback()
        if self.sceneRightArrowCallback and key == self.RIGHT_ARROW:
            self.sceneRightArrowCallback()        
        if self.sceneLCTRLCallback and key == self.LEFT_CTRL:
            self.sceneLCTRLCallback()
        if self.sceneRCTRLCallback and key == self.RIGHT_CTRL:
            self.sceneRCTRLCallback()
        if self.sceneLSHIFTCallback and key == self.LEFT_SHIFT:
            self.sceneLSHIFTCallback()
        if self.sceneRSHIFTCallback and key == self.RIGHT_SHIFT:
            self.sceneRSHIFTCallback()
        if self.sceneLALTCallback and key == self.LEFT_ALT:
            self.sceneLALTCallback()

    def shutdown(self):
        """
        This method processes a 'shutdown' event for this Scene3D
        object by calling the C shutdown function.

        **Parameters:** This method has no parameters.

        """
        mh.shutDown()

    def getObject(self, name):
        """
        This method searches the list of 3D objects contained within the scene and returns the object with
        the specified name, or None if no object with that name could be found.

        Parameters
        ----------

        name:
            *string*. The name of the object to retrieve.
        """
        objToGet = None
        for obj in self.objects:
            if obj.name == name:
                objToGet = obj
                break
        return objToGet
        #print "Obj %s not found"%(name)

    def getSelectedObject(self):
        """
        This method searches the list of 3D objects contained within the scene and returns
        the currently selected object (the first object with the **isSelected** flag set) or
        None if no object is selected.
        This method assumes that only one object is currently selected.

        **Parameters:** This method has no parameters.

        """        
        objToGet = None
        for obj in self.objects:
            if obj.isSelected:
                objToGet = obj
                break        
        return objToGet

    def deselectAll(self):
        """
        This method resets all **isSelected** attributes, for
        all objects in the scene.

        **Parameters:** This method has no parameters.

        """
        for obj in self.objects:
            if obj.isSelected:
                obj.isSelected = None
                break

    def startWindow(self, useIdle = 0):
        """
        This method opens a Window with a graphical context and is part of the
        application launch sequence.

        Parameters
        ----------

        useIdle:
            *int*. An indicator that determines whether idle time will be used 
            (whether to use timer based events).

        """
        mh.startWindow(useIdle)
        
    def startEventLoop(self):
        """
        This method starts the event loop is part of the
        application launch sequence.

        **Parameters:** This method has no parameters.

        """
        mh.startEventLoop()

    def grabScreen(self, x, y, width, height, filename):
        """
        This method calls the grabScreen method on the 'mh' class which invokes the 
        corresponding C function (mhGrabScreen) to take a rectangular section from 
        the screen and write an image to a bitmap image file on disk containing the 
        pixels currently displayed in that section of screen.

        Parameters
        ----------

        x:
            *int* an int containing the x coordinate of the corner of the area (in pixels).
        y:
            *int* an int containing the y coordinate of the corner of the area (in pixels).
        width:
            *int* an int containing the width of the area in pixels. 
        length:
            *int* an int containing the height of the area in pixels. 
        filename:
            *string* a string containing the full path of the file on disk.

        """
        cursor = self.getObject("cursor.obj")
        cursor.setVisibility(0)
        mh.grabScreen(x, y, width, height, filename)
        cursor.setVisibility(1)

    def newObj(self,name):
        """
        This method creates a newly initialized Object3D instance within this Scene3D object
        and returns it to the calling code ready to be populated.

        Parameters
        ----------

        name:
            *string*. The name for the new Object3D object.

        """

        newObj = Object3D(name)
        newObj.idx = len(self.objects)
        self.objects.append(newObj)
        return newObj

    def instanceObj(self,obj,name):

        """
        This macro creates a reference copy of the Object3D object that is passed in as a parameter.
        It instantiates new FaceGroups which contain the same faces as the original.

        This new object shares the same vertices and faces as the original. Only
        index references are copied, and no new vertices or faces are created.

        The new object is added into the Scene3D object and is returned to the calling code.

        Parameters
        ----------

        obj:
            *object 3D*. The object3D object to be copied.

        name:
            *string*. The name of the new instance.

        """
        newObj = Object3D(name)
        newObj.idx = len(self.objects)
        newObj.x = obj.x
        newObj.y = obj.y
        newObj.z = obj.z
        newObj.rx = obj.rx
        newObj.ry = obj.ry
        newObj.rz = obj.rz
        newObj.r = obj.r
        newObj.g = obj.g
        newObj.b = obj.b
        newObj.verts = obj.verts
        newObj.faces = obj.faces

        for fg in obj.facesGroups:
            newFg = FaceGroup(name+fg.name)
            newFg.faces = fg.faces
            newObj.addFaceGroup(newFg)

        newObj.cameraMode = obj.cameraMode
        newObj.visibility = obj.visibility
        newObj.texture = obj.texture
        newObj.colors = obj.colors
        newObj.cameraMode = obj.cameraMode
        self.objects.append(newObj)
        return newObj


    def deleteObj(self, name):
        """
        This method searches the list of Object3D objects contained within this Scene3D object by name and,
        if found, it deletes that object.
        First, the instance of the object is deleted. Then the index of objects,
        used to identify the object in the OpenGL engine array, is updated and
        renumbered to close the gap.

        Parameters
        ----------

        name:
            *string*. The name of object to delete.
        """
        indexToDelete = None
        for obj in self.objects:
            if obj.name == name:
                indexToDelete = obj.idx
                break
        if indexToDelete:
            del self.objects[indexToDelete]

        #Update the index of objects
        for i,obj in enumerate(self.objects):
                obj.idx = i


    def assignSelectionID(self, obj):
        """
        This method generates a new, unique color ID for each FaceGroup,
        within a particular Object3D object, that forms a part of this scene3D
        object. This color ID can subsequently be used in a non-displayed
        image map to determine the FaceGroup that a mouse click was made in.

        This method loops through the FaceGroups, assigning the next color
        in the sequence to each subsequent FaceGroup. The color value is
        written into a 'dictionary' to serve as a color ID that can be
        translated back into the corresponding FaceGroup name when a mouse
        click is detected.
        This is part of a technique called *Selection Using Unique Color IDs*
        to make each FaceGroup independently clickable.

        (See 'MakeHuman Selectors' above.)

        Parameters
        ----------

        obj:
            *object 3D*. The object3D object for which a color dictionary is to be generated.

        """
        #print "DEBUG COLOR AND GROUPS, obj", obj.name
        #print "---------------------------"
        for g in obj.facesGroups:
            #if len(g.faces) > 0:
            #    print g.name
            # Assign a unique sequential colorID used for selection
            self.colorID[0] += 1
            if self.colorID[0] >= 255:
                self.colorID[0] = 0;
                self.colorID[1] += 1
                if self.colorID[1] >= 255:
                    self.colorID[1] = 0;
                    self.colorID[2] += 1
            idR = self.colorID[0];
            idG = self.colorID[1];
            idB = self.colorID[2];
            for f in g.faces:
                f.colorID = [idR,idG,idB]
            self.faceGroupColorID[str(idR)+str(idG)+str(idB)] = g
            #print "SELECTION DEBUG INFO: facegroup %s of obj %s has the colorID = %s,%s,%s"%(g.name,obj.name,idR,idG,idB)

    def getSelectedFacesGroup(self):
        """
        This method uses a non-displayed image containing color-coded faces
        to return the index of the FaceGroup selected by the user with the mouse.
        This is part of a technique called *Selection Using Unique Color IDs* to make each
        FaceGroup independently clickable.
        (see 'MakeHuman Selectors' above.)

        **Parameters:** This method has no parameters.

        """
        picked = mh.getColorPicked()
        #print "DEBUG COLOR PICKED: %s,%s,%s"%(picked[0],picked[1],picked[2])
        IDkey = str(picked[0])+str(picked[1])+str(picked[2])#TODO convert to string side C

        try:
            groupSelected = self.faceGroupColorID[IDkey]
        except:
            groupSelected = None        
        return groupSelected


    def getMouseDiff(self):
        """
        This method retrieves the difference between the last registered mouse
        position and the current mouse position. This is used during events that
        need to track mouse movements, such as scaling, moving and rotating the
        camera. The mouse movement is returned as a list of 2 integer values
        representing the X and Y displacements of the mouse in pixels.

        **Parameters:** This method has no parameters.

        """
        return [self.mouseXRel, self.mouseYRel]

    def getCameraRotations(self):
        """
        This method retrieves the amount by which a cursor movement has
        rotated the camera, returning the x and y rotations in degrees
        as a list of two floats.
        **Note.** The camera can only rotate around the X and Y axes.

        **Parameters:** This method has no parameters.

        """
        return mh.getCameraRotations()
        
    def setCameraRotations(self, rotX, rotY):
        """
        This method sets the amount by which a cursor movement has
        rotated the camera, passing the x and y rotations in degrees
        as two floats.
        **Note.** The camera can only rotate around the X and Y axes.

        Parameters
        ----------

        rotX:
            *int*. Rotation around the x axis in degrees.
        rotY:
            *int*. Rotation around the y axis in degrees.

        """
        return mh.setCameraRotations(rotX, rotY)

    def getCameraTranslations(self):
        """
        This method retrieves the amount by which a cursor movement has
        translated the camera, returning the x and y displacements as a
        list of two floats. The values returned are 0.05 times the number
        of pixels moved by the cursor.
        **Note.** The camera is only translated in the XY-plane. Movements in
        the Z direction are treated as 'zoom' and can be retrieved using the
        getCameraZoom method.

        **Parameters:** This method has no parameters.

        """
        return mh.getCameraTranslations()
        
    def setCameraTranslations(self, x, y):
        """
        This method sets the amount by which a cursor movement has
        translated the camera, passing the x and y displacements as
        two floats.
        **Note.** The camera is only translated in the XY-plane. Movements in
        the Z direction are treated as 'zoom' and can be set using the
        setCameraZoom method.

        Parameters
        ----------

        x:
            *float*. Translation on the x axis.
        y:
            *float*. Translation on the y axis.

        """
        return mh.setCameraTranslations(x, y)

    def getCameraZoom(self):
        """
        This method retrieves the amount by which a cursor movement has
        zoomed the camera, returning the z displacement as a
        single float value. The value returned is 0.05 times the number
        of pixels moved by the cursor.

        **Parameters:** This method has no parameters.

        """
        return mh.getCameraZoom()
        
    def setCameraZoom(self, zoom):
        """
        This method sets the amount by which a cursor movement has
        zoomed the camera, passing the z displacement as a
        single float value. The value returned is 0.05 times the number
        of pixels moved by the cursor.

        Parameters
        ----------

        zoom:
            *float*. Zoom factor.

        """
        return mh.setCameraZoom(zoom)

    def getCameraSettings(self):
        """
        This method passes the current camera settings through from the
        C core to the Python code. A list of numeric values is returned,
        including the pan, zoom, rotation, field of view angle and the
        viewport dimensions:
        [locX,locY,zoom,rotX,rotY,fovAngle,windowHeight,windowWidth]. 

        **Parameters:** This method has no parameters.

        """
        return mh.getCameraSettings()

    def getKeyModifiers(self):
        """
        This method returns the state of modifiers keys (CTRL, ALT, SHIFT).
        The returned value is:

        - 0 = no modifier pressed
        - 1 = left shift key
        - 2 = right shift key
        - 64 = left ctrl key
        - 128 = right ctrl key
        - 256 = left alt key
        - 512 = right alt key
        - 1024 = left meta key
        - 2048 = right meta key
        - 4096 = num key
        - 8192 = caps key
        - 16384 = mode key

        **Parameters:** This method has no parameters.

        """

        return mh.getKeyModifiers()


    def getPickedObject(self):
        """
        This method determines whether a FaceGroup or a non-selectable zone has been
        clicked with the mouse. It returns a tuple, showing the FaceGroup and the parent
        Object3D object, or None.
        If no object is picked, this method will simply print "no clickable zone."

        **Parameters:** This method has no parameters.

        """
        facegroupPicked = self.getSelectedFacesGroup()
        if facegroupPicked:
            objPicked = facegroupPicked.parent
            return (facegroupPicked,objPicked)
        else:
            print "no clickable zone"
            return None


    def selectObject(self):
        """
        This method first deselects any objects in the scene that are currently
        selected, then, if an object was selected by the current operation, it
        marks that object as selected.

        **Parameters:** None.

        """

        # NOTE: This function supposes that we have only one object
        # selected at a time

        global scene

        #get actual selected obj
        objPicked = self.getSelectedObject()

        #restore his original color (no selected)
        #and then deselect all obj in the scene
        if objPicked:
            #objPicked.applyDefaultColor()
            self.deselectAll()

        #Now get the picked obj to select it
        pickedInfo = self.getPickedObject()
        if pickedInfo:
            pickedObj = pickedInfo[1]
            #pickedObj.applySelectionColor()
            pickedObj.isSelected = 1
            pickedObj.faceGroupSelected = pickedInfo[0]
        self.redraw()



    def redraw(self, async = 1):
        """
        This method redraws the scene. This should be used wherever possible to avoid
        unnecessary calls to the update method, as this method's performance is far better.
        For example, this method should be called to show vertices that have been modified.

        Parameters
        ----------

        name:
            *async*. If 1, draws asynchronous, if 0 draws synchronous.
        """

        mh.redraw(async)

