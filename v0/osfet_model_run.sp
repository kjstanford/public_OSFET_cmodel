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
.PARAM W = 60e-9
.PARAM Lch = 60e-9
.PARAM mu_eff = 0.0012
.PARAM Cgch = 0.0124
.PARAM Cpar = "0.0124*60e-9"
.PARAM longVT = 0.43
.PARAM alpha1 = 0.6
.PARAM alpha2 = 0.05
.PARAM meff = 0.3
.PARAM rsd_mode = 1
.PARAM Rs0 = 0.0002
.PARAM Rd0 = 0.0002
.PARAM delta = 0.09
.PARAM rollVT = 0.0
.PARAM n0 = 1.8
.PARAM nd = 0.0
.PARAM type = 1

* .DC vgate LIN 100.0 'vgatel' 'vgateh'
.DC vgate LIN 121 'vgatel' 'vgateh' SWEEP vdrain LIN 2 'vdrainlin' 'vdrainsat'

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    PARHIER=LOCAL
+    PSF=2
+    POST=2

.HDL "osfet_potential_based_compact_model_v0.va"

xos d g s osfet W=W mu_eff=mu_eff Lch=Lch Cgch=Cgch Cpar=Cpar longVT=longVT alpha1=alpha1 alpha2=alpha2 meff=meff
+ rsd_mode=rsd_mode Rs0=Rs0 Rd0=Rd0 delta=delta rollVT=rollVT n0=n0 nd=nd type=type

vd d 0 DC='vdrain'
vg g 0 DC='vgate'
vs s 0 DC=0

.END
