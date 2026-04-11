from dolphin import memory #  type: ignore

def GXBegin(): pass
def GXEnd(): pass
def GXPosition3f32(): pass
    
GXPrimitive = {
    "GX_POINTS": 0xb8,
    "GX_LINES": 0xa8,
    "GX_LINESTRIP": 0xb0,
    "GX_TRIANGLES": 0x90,
    "GX_TRIANGLESTRIP": 0x98,
    "GX_TRIANGLEFAN": 0xa0,
    "GX_QUADS": 0x80,
}

def main(x,y,z):
    VERTS = [[x, y, z],
             [x, y, z],
             [x, y, z],
             [x, y, z]]
    VERT_COUNT = len(VERTS)
    VERT_FORMAT = None
    GX_QUADS = None

    GXBegin(GX_QUADS, VERT_FORMAT, VERT_COUNT)
    for i in range(VERT_COUNT):
        vtx = VERTS[i]
        GXPosition3f32(vtx[0], vtx[1], vtx[2])
    GXEnd()