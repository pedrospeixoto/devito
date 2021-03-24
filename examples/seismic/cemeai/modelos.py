#==============================================================================
# Bibliotecas Python
#==============================================================================
import numpy              as np
import matplotlib.pyplot  as plot
import time               as tm
import time
import sys
#==============================================================================

#==============================================================================
# Bibliotecas Devito
#==============================================================================
from examples.seismic import Model, plot_velocity
from examples.seismic import TimeAxis
from examples.seismic import RickerSource
from examples.seismic import Receiver
from devito import TimeFunction
from devito import Eq, solve
from devito import Operator
from examples.seismic import plot_shotrecord
from devito import configuration
from gerar_modelos import generateRandomModel
configuration['log-level']='ERROR'
#==============================================================================

#==============================================================================
plot.close("all") # fecha todas as janelas
#==============================================================================

#==============================================================================
# Parâmetros do Problema 
#==============================================================================
nmodelos   = 100

nptx       = 101
nptz       = 51
x0         = 0.0
x1         = 2000
z0         = 0.0 
z1         = 1000
compx      = x1-x0
compz      = z1-z0
hx         = (x1-x0)/(nptx-1)           
hz         = (z1-z0)/(nptz-1)           
sou        = 2
tou        = 2
nbl        = 10 
t0         = 0.
tn         = 1000.
CFL        = 0.4
nfonte     = 1
f0         = 0.020 
nxfontpos  = 20.   
nzfontpos  = 20.                        
nrec       = 51
nxrecpos   = np.linspace(x0,x1,nrec)   
nzrecpos   = 20.            

# Number of layers for the model
numberOfLayers = 5

verbosity = 1

#==============================================================================

#==============================================================================
for i in range(0,nmodelos):
#==============================================================================
    print(i)
#==============================================================================
# Parâmetros de Malha
#==============================================================================
    shape   = (nptx,nptz)  
    spacing = (hx,hz)  
    origin  = (x0,z0)  
#==============================================================================

#==============================================================================
# Parâmetros de Velocidade
#==============================================================================
    v = np.empty(shape,dtype=np.float32)
    v[:, :51] = 1.5
    v[:, 51:] = 1.5
#==============================================================================


#==============================================================================
# Construção do Modelo de Velocidade
#==============================================================================
    if i>0:
        # Seeding the RNG
        np.random.seed(int(time.time()))

        # Generates the model
        start = time.time()
        model = generateRandomModel(shape, spacing, origin, numberOfLayers)
        end = time.time()
        print(end - start)
        if verbosity > 0:
            plot_velocity(model)
    
    else: # homogeneous condition, reference
        model = Model(vp=v,origin=origin,shape=shape,spacing=spacing,space_order=sou,nbl=nbl,bcs="damp")
        if verbosity > 0:
            plot_velocity(model)

#==============================================================================
    field = np.transpose(model.vp.data)

    #print(field)
    np.save("data_save/model_data_%d"%i,field)

#==============================================================================
# Construção Parâmetros Temporais
#==============================================================================
    dt         = model.critical_dt 
    print(dt)
    time_range = TimeAxis(start=t0,stop=tn,step=dt)
    
    #vmax  = np.amax(v) 
    #dtmax = (min(hx,hz)*CFL)/(vmax)   
    #ntmax = int((tn-t0)/dtmax)+1
    ntmax = 201
    dt    = (tn-t0)/(ntmax)
    print(dt)
    time_range = TimeAxis(start=t0,stop=tn,step=dt)
#==============================================================================

#==============================================================================
# Construção Fonte de Ricker
#==============================================================================
    src = RickerSource(name='src', grid=model.grid, f0=f0,npoint=nfonte, time_range=time_range)
    src.coordinates.data[:, 0] = nxfontpos
    src.coordinates.data[:, 1] = nzfontpos
#==============================================================================

#==============================================================================
# Construção Receivers
#==============================================================================
    rec = Receiver(name='rec', grid=model.grid, npoint=nrec, time_range=time_range)
    rec.coordinates.data[:, 0] = nxrecpos
    rec.coordinates.data[:, 1] = nzrecpos 
#==============================================================================

#==============================================================================
# Construção dos Campos
#==============================================================================
    u        = TimeFunction(name="u",grid=model.grid, time_order=tou, space_order=sou)
    pde      = model.m * u.dt2 - u.laplace + model.damp * u.dt
    stencil  = Eq(u.forward, solve(pde, u.forward))
    src_term = src.inject(field=u.forward, expr=src * dt**2 / model.m)
    rec_term = rec.interpolate(expr=u.forward)
#==============================================================================

#==============================================================================
# Construção dos Operadores
#==============================================================================
    op = Operator([stencil] + src_term + rec_term, subs=model.spacing_map)
    start = tm.time()
    op(time=time_range.num-1, dt=model.critical_dt)
    end   = tm.time() 
    #print("Elapsed (after compilation) = %s" % (end - start))
#==============================================================================

#==============================================================================
# Manipulando Receivers
#==============================================================================
    np.save("data_save/rec_data_%d"%i,rec.data)
    if verbosity > 0:
        plot_shotrecord(rec.data, model, t0, tn)
#==============================================================================