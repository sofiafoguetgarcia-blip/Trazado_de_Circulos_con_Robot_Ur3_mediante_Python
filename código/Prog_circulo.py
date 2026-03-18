# -*- coding: utf-8 -*-
from robodk.robolink import *
from robodk.robomath import *
import math

RDK = Robolink()
RDK.setRunMode(RUNMODE_SIMULATE)

# ----------- PARÁMETROS -----------
RADIO_MM        = 100.0
ALTURA_Z        = 15.0           # “bolígrafo abajo”
ALTURA_SALIDA   = ALTURA_Z + 30  # “bolígrafo arriba”
PUNTOS          = 120            # más puntos → círculo más suave
REDONDEO_MM     = 2.0            # blend para el trazado (no para subir/bajar)

# ----------- OBJETOS -----------
robot = RDK.Item('', ITEM_TYPE_ROBOT)
base  = RDK.Item('UR3e Base', ITEM_TYPE_FRAME)
tool  = robot.getLink(ITEM_TYPE_TOOL)
t1    = RDK.Item('Target 1', ITEM_TYPE_TARGET)

robot.setFrame(base)
robot.setTool(tool)

# ----------- GUARDAR JUNTAS INICIALES -----------
joints_iniciales = robot.Joints()

pose_center = t1.Pose()              # orientación fija del lápiz
xc, yc, _ = pose_center.Pos()

# ----------- PUNTOS DEL CÍRCULO -----------
pts = []
for i in range(PUNTOS):
    ang = math.radians(i * (360.0 / PUNTOS))
    x = xc + RADIO_MM * math.cos(ang)
    y = yc + RADIO_MM * math.sin(ang)
    p = pose_center.copy()
    p.setPos([x, y, ALTURA_Z])       # todos a Z=15 mm
    pts.append(p)

# Punto inicial (para cierre exacto)
p0 = pts[0]

try:
    # 0) Ir al target 1 (config segura)
    robot.MoveJ(t1)

    # 1) Bajar vertical (bolígrafo abajo) SIN blend
    px, py, _ = pose_center.Pos()
    p_down = pose_center.copy()
    p_down.setPos([px, py, ALTURA_Z])
    robot.setRounding(0.0)
    robot.MoveL(p_down)

    # 2) Ir al primer punto SIN blend
    robot.MoveL(p0)

    # 3) Trazar el círculo con blend pequeño
    robot.setRounding(REDONDEO_MM)
    for p in pts[1:]:
        robot.MoveL(p)

    # 4) Cerrar el círculo EXACTO al p0
    robot.setRounding(0.0)
    robot.MoveL(p0)

    # 5) Subir vertical (bolígrafo arriba)
    p_up = pose_center.copy()
    p_up.setPos([px, py, ALTURA_SALIDA])
    robot.MoveL(p_up)

    # 6) VOLVER A LA POSICIÓN INICIAL REAL
    robot.MoveJ(joints_iniciales)

    print("✔ Círculo completado y regreso a la posición inicial.")

except Exception as e:
    print("Error:", e)