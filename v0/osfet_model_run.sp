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
.PARAM vgateh = 2
.PARAM vgatel = -1 
.PARAM vgate = vgatel

* .DC vgate LIN 100.0 'vgatel' 'vgateh'
.DC vgate LIN 121 'vgatel' 'vgateh' SWEEP vdrain LIN 2 'vdrainlin' 'vdrainsat'

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    PARHIER=LOCAL
+    PSF=2

.HDL osfet_potential_based_compact_model_v0.va

xos d g s osfet W=2e-6 mu_eff=0.002 Lch=6e-8 Cgch=0.0124 Cpar=0.0124*60e-9 longVT=0.17 alpha1=0.52 alpha2=0.05 meff=0.3
+ rsd_mode=1 Rs0=200.0e-6 Rd0=200.0e-6 delta=0.06 rollVT=0.0 n0=1.4433 nd=0.0 type=1

vd d 0 DC='vdrain'
vg g 0 DC='vgate'
vs s 0 DC=0

.END
