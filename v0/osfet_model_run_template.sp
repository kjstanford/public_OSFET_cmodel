** osfet model test
.PROBE DC
+    V(g)
+    I(vs)
.PRINT DC
+    V(g)
+    I(vs)

.PARAM vdrainlin = @vdrainlin@
.PARAM vdrainsat = @vdrainsat@
.PARAM vdrain = vdrainlin
.PARAM vgateh = @vgateh@
.PARAM vgatel = @vgatel@
.PARAM vgate = vgatel
.PARAM W = @W@
.PARAM Lch = @Lch@
.PARAM mu_eff = @mu_eff@
.PARAM Cgch = @Cgch@
.PARAM Cpar = @Cpar@
.PARAM longVT = @longVT@
.PARAM alpha1 = @alpha1@
.PARAM alpha2 = @alpha2@
.PARAM meff = @meff@
.PARAM rsd_mode = @rsd_mode@
.PARAM Rs0 = @Rs0@
.PARAM Rd0 = @Rd0@
.PARAM delta = @delta@
.PARAM rollVT = @rollVT@
.PARAM n0 = @n0@
.PARAM nd = @nd@
.PARAM type = @type@

* .DC vgate LIN 100.0 'vgatel' 'vgateh'
.DC vgate LIN 121 'vgatel' 'vgateh' SWEEP vdrain LIN 2 'vdrainlin' 'vdrainsat'

.TEMP 25.0
.OPTION
+    ARTIST=2
+    INGOLD=2
+    PARHIER=LOCAL
+    PSF=2
+    POST=2

.HDL @va_model_path@

xos d g s osfet W=W mu_eff=mu_eff Lch=Lch Cgch=Cgch Cpar=Cpar longVT=longVT alpha1=alpha1 alpha2=alpha2 meff=meff
+ rsd_mode=rsd_mode Rs0=Rs0 Rd0=Rd0 delta=delta rollVT=rollVT n0=n0 nd=nd type=type

vd d 0 DC='vdrain'
vg g 0 DC='vgate'
vs s 0 DC=0

.END
