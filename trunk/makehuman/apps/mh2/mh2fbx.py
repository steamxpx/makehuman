#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------
Fbx exporter

"""

import os
import sys
import export_config
import object_collection

fbxpath = "tools/blender26x"
if fbxpath not in sys.path:
    sys.path.append(fbxpath)
    
import io_mh_fbx
# bpy must be imported after io_mh_fbx
import bpy


def exportFbx(human, filepath, options):
    cfg = export_config.exportConfig(human, True)
    cfg.separatefolder = True

    stuffs = object_collection.setupObjects(os.path.splitext(filepath)[0], human,
        helpers=options["helpers"], 
        hidden=options["hidden"], 
        eyebrows=options["eyebrows"], 
        lashes=options["lashes"],
        subdivide=options["subdivide"])
    
    (scale, unit) = options["scale"]   
    outfile = export_config.getOutFileFolder(filepath, cfg)   
    (path, ext) = os.path.splitext(outfile)

    bpy.initialize()
    for stuff in stuffs:
    	bpy.addMesh(stuff.name, stuff, True)
    	
    #name = os.path.splitext(os.path.basename(filepath))[0]
    #bpy.addMesh(name, human.meshData, False)
    
    filename = "%s.fbx" % path
    io_mh_fbx.fbx_export.exportFbxFile(bpy.context, filename)
    return

