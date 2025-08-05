** osfet model test
.PROBE DC
+    V(g)
+    I(vs)
.PRINT DC
+    V(g)
+    I(vs)

.PARAM vdrainlin = 50e-3
.PARAM vdrainsat = 2
.PARAM vdrain = vdrainlin
.PARAM vgateh = 2.5
.PARAM vgatel = -0.5 
.PARAM vgate = vgatel

* .DC vgate LIN 100.0 'vgatel' 'vgateh'
.DC vgate LIN 121 'vgatel' 'vgateh' SWEEP vdrain LIN 2 'vdrainlin' 'vdrainsat'

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    PARHIER=LOCAL
+    PSF=2

.HDL osfet_potential_based_compact_model_v1.va

xos d g s osfet W=120e-9

vd d 0 DC='vdrain'
vg g 0 DC='vgate'
vs s 0 DC=0

.END
