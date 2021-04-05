#==============================================================================
# Bibliotecas Python
#==============================================================================
import numpy              as np
import matplotlib.pyplot  as plot
import segyio
import sys
#==============================================================================

#==============================================================================
# Rotinas Próprias
#==============================================================================
import testes             as tt
import rotinas_plot       as rplot
import gerar_modelos      as gr
import dados_marmousi     as ddmarmou
#==============================================================================

#==============================================================================
# Bibliotecas Devito
#==============================================================================
from examples.seismic import Model, plot_velocity
from examples.seismic import TimeAxis
from examples.seismic import RickerSource
from examples.seismic import Receiver
from examples.seismic import plot_shotrecord
from devito           import TimeFunction
from devito           import Eq, solve
from devito           import Operator
from devito           import configuration
#==============================================================================

#==============================================================================
plot.close("all")
configuration['log-level']='ERROR'
#==============================================================================

#==============================================================================
# Importando Dados do Problema
#==============================================================================
teste     = tt.teste2
sintmodel = teste.sintmodel                                   
#==============================================================================

#==============================================================================
# Capturando Informações do Modelo Sintético
#==============================================================================
if(sintmodel==1):

    C0        = ddmarmou.inter_marmousi(teste)
    V1        = ddmarmou.graph2dvel(C0,teste)
    vmodelmin = np.amin(C0)
    vmodelmax = np.amax(C0)

else:
    
    vmodelmin = 1.5
    vmodelmax = 3.5
#==============================================================================

#==============================================================================
# Parâmetros do Problema 
#==============================================================================
ncamadas    = teste.ncamadas # Número de Tipos de Camadas
N0          = teste.N0       # Número de Camadas aleatórias com retas horizontais
N1          = teste.N1       # Número de Camadas aleatórias com camadas retas inclinadas
N2          = teste.N2       # Número de Camadas aleatórias com camadas Gaussianas
N3          = teste.N3       # Número de Camadas aleatórias com camadas Mistas
nptx        = teste.nptx
nptz        = teste.nptz
x0          = teste.x0
x1          = teste.x1
z0          = teste.z0
z1          = teste.z1
compx       = teste.compx
compz       = teste.compz
hx          = teste.hx           
hz          = teste.hz           
sou         = teste.sou
tou         = teste.tou
nbl         = teste.nbl
t0          = teste.t0
tn          = teste.tn
ntmax       = teste.ntmax
CFL         = teste.CFL
nfonte      = teste.nfonte
f0          = teste.f0
nxfontposv  = teste.nxfontpos
nzfontpos   = teste.nzfontpos            
nrec        = teste.nrec
nxrecpos    = teste.nxrecpos   
nzrecpos    = teste.nzrecpos 
verbosity   = teste.verbosity
max_layers  = teste.max_layers
#==============================================================================

#==============================================================================
# Variáveis Locais
#==============================================================================
number_xfontpos = np.size(nxfontposv)
shape           = (nptx,nptz)  
spacing         = (hx,hz)  
origin          = (x0,z0)  
#==============================================================================

#==============================================================================
# Modelo de Velocidade Hohomogeneo
#==============================================================================
vhomo      = np.empty(shape,dtype=np.float32)
vhomo[:,:] = vmodelmin     
model0     = Model(vp=vhomo,origin=origin,shape=shape,spacing=spacing,space_order=sou,nbl=nbl,bcs="damp")
rec_homo   = np.zeros((number_xfontpos,ntmax+1,nrec))
#==============================================================================

#==============================================================================
# Construção Parâmetros Temporais do Modelo Hohomogeneo
#==============================================================================
dt_ref0 = model0.critical_dt 
dt0     = (tn-t0)/(ntmax)
    
if(dt0>dt_ref0):
    
    print("Warning: dt: ", dt0, " dt_ref: ", dt_ref0)
    
time_range0 = TimeAxis(start=t0,stop=tn,step=dt0)
#==============================================================================

#==============================================================================
# Construção Fonte de Ricker Modelo Homogeneo
#==============================================================================
src0 = RickerSource(name='src0',grid=model0.grid,f0=f0,npoint=nfonte,time_range=time_range0)
src0.coordinates.data[:, 0] = nxfontposv[0]
src0.coordinates.data[:, 1] = nzfontpos
#==============================================================================

#==============================================================================
# Construção Receivers Homogeneo
#==============================================================================
rec0 = Receiver(name='rec0', grid=model0.grid,npoint=nrec,time_range=time_range0)
rec0.coordinates.data[:,0] = nxrecpos
rec0.coordinates.data[:,1] = nzrecpos 
#==============================================================================

#==============================================================================
# Construção dos Campos Modelo Homogêneo
#==============================================================================
u0         = TimeFunction(name="u0",grid=model0.grid,time_order=tou,space_order=sou)
pde0       = model0.m * u0.dt2 - u0.laplace + model0.damp * u0.dt
stencil0   = Eq(u0.forward, solve(pde0, u0.forward))
src_term0  = src0.inject(field=u0.forward, expr=src0* dt0**2 / model0.m)
rec_term0  = rec0.interpolate(expr=u0.forward)
#==============================================================================

#==============================================================================
# Construção e Execução dos Operadores Modelo Homogeneo
#==============================================================================
op0 = Operator([stencil0] + src_term0 + rec_term0, subs=model0.spacing_map)
#op0(time=time_range0.num-1,dt=model0.critical_dt)
#==============================================================================

#==============================================================================
# Salvando Informações dos Receiveris do Modelo Homogeneo
#==============================================================================
rec_homo[0,:,:] = rec0.data[:,:]
#==============================================================================

#==============================================================================
# For para o Número de Fontes
#==============================================================================
print("Homogeneous Problem")
print("dt:", model0.critical_dt, dt0)

for k in range(0,number_xfontpos):    
#==============================================================================
    print("Source:", k)
#==============================================================================
# Atualização da Fonte de Ricker Modelo Homogeneo
#==============================================================================
    src0 = RickerSource(name='src0',grid=model0.grid,f0=f0,npoint=nfonte,time_range=time_range0)
    nxfontpos                   = nxfontposv[k]
    src0.coordinates.data[:, 0] = nxfontpos
    src0.coordinates.data[:, 1] = nzfontpos
#==============================================================================
    
#==============================================================================
# Atualização e Execução dos Operadores Modelo Homogeneo
#==============================================================================
    #op0(time=time_range0.num-1,dt=model0.critical_dt,src0=src0)
    op0(time=time_range0.num-1,dt=dt0,src0=src0)
#==============================================================================

#==============================================================================
# Salvando Informações dos Receiveris do Modelo Homogeneo
#==============================================================================
    rec_homo[k,:,:] = rec0.data[:,:]
    np.save("data_save/rec_data_homog_source_%d"%(k),rec_homo[k, :,nbl:-nbl])

    if(verbosity>0):
    #rplot.graph2d(u.data[0,:,:],teste,i,k,tmodel)
        rplot.graph2drec(rec_homo[k, :, :],teste,0,k,-1)
#==============================================================================

#==============================================================================
# Variando os Tipos de Camadas Aleatórias
#==============================================================================
for tmodel in range(0,ncamadas):
    
    if(tmodel==0): nmodelos = N0
    if(tmodel==1): nmodelos = N1
    if(tmodel==2): nmodelos = N2
    if(tmodel==3): nmodelos = N3
#==============================================================================
    
#==============================================================================
# For para o Número de Modelos
#==============================================================================
    for i in range(0,nmodelos):
#==============================================================================
    
#==============================================================================
# Construção do Modelo de Velocidade
#==============================================================================     
        if(tmodel==0): model = gr.generateRandomModel_linhas(teste,vmodelmin,vmodelmax,max_layers)
        if(tmodel==1): model = gr.generateRandomModel_linha_inclinada(teste,vmodelmin,vmodelmax,max_layers)
        if(tmodel==2): model = gr.generateRandomModel_gaussiana(teste,vmodelmin,vmodelmax,max_layers)
        if(tmodel==3): model = gr.generateRandomModel(teste,vmodelmin,vmodelmax,max_layers)

        if(verbosity>0):
            
            rplot.graph2dvel(model.vp.data,teste,i,tmodel)    
#==============================================================================

#==============================================================================
# Salvando Informacoes de Velocidade
#==============================================================================
        field = np.transpose(model.vp.data[nbl:-nbl,nbl:-nbl])
        np.save("data_save/vel_model_data_%d_type_%d"%(i,tmodel),field)
#==============================================================================

#==============================================================================
# Construção Parâmetros Temporais do Modelo Teste
#==============================================================================
        dt_ref = model.critical_dt 
        dt     = (tn-t0)/(ntmax)
    
        if(dt>dt_ref):
    
            print("Warning: dt: ", dt, " dt_ref: ", dt_ref)
    
        time_range = TimeAxis(start=t0,stop=tn,step=dt)
#==============================================================================

#==============================================================================
# Construção Receivers Modelo Teste
#==============================================================================
        rec = Receiver(name='rec',grid=model.grid,npoint=nrec,time_range=time_range)
        rec.coordinates.data[:,0] = nxrecpos
        rec.coordinates.data[:,1] = nzrecpos 
#==============================================================================

#==============================================================================
# Construção Fonte de Ricker Modelo Teste
#==============================================================================
        src = RickerSource(name='src', grid=model.grid,f0=f0,npoint=nfonte,time_range=time_range)
        src.coordinates.data[:, 0] = nxfontposv[0]
        src.coordinates.data[:, 1] = nzfontpos
#==============================================================================

#==============================================================================
# Construção dos Campos Modelo Teste
#==============================================================================
        u        = TimeFunction(name="u",grid=model.grid, time_order=tou, space_order=sou)
        pde      = model.m * u.dt2 - u.laplace + model.damp * u.dt
        stencil  = Eq(u.forward, solve(pde, u.forward))
        src_term = src.inject(field=u.forward, expr=src * dt**2 / model.m)
        rec_term = rec.interpolate(expr=u.forward)
#==============================================================================

#==============================================================================
# Construção e Execução dos Operadores Modelo Teste
#==============================================================================
        op  = Operator([stencil] + src_term + rec_term, subs=model.spacing_map)        
        op(time=time_range.num-1,dt=model.critical_dt)
#==============================================================================

#==============================================================================
# Manipulando Receivers com Corte da Onda Direta
#============================================================================
        rec_clean = np.zeros((rec.data.shape[0],rec.data.shape[1]))
        rec_clean = rec.data - rec_homo[k,:,:]
                        
        np.save("data_save/rec_data_model_%d_source_%d_type_%d"%(i,k,tmodel),rec_clean[:,nbl:-nbl])
    
        if(verbosity>0):
    
            #rplot.graph2d(u.data[0,:,:],teste,i,k,tmodel)
            rplot.graph2drec(rec_clean,teste,i,k,tmodel)
#==============================================================================

#==============================================================================
# For para o Número de Fontes
#==============================================================================
        for k in range(1,number_xfontpos):    
#==============================================================================

#==============================================================================
# Atualização Fonte de Ricker Modelo Teste
#==============================================================================
            src = RickerSource(name='src', grid=model.grid,f0=f0,npoint=nfonte,time_range=time_range)
            nxfontpos                  = nxfontposv[k]
            src.coordinates.data[:, 0] = nxfontpos
            src.coordinates.data[:, 1] = nzfontpos
#==============================================================================

#==============================================================================
# Atualização e Execução dos Operadores Modelo Teste
#==============================================================================
            op(time=time_range.num-1,dt=model.critical_dt,src=src)
#==============================================================================

#==============================================================================
# Manipulando Receivers com Corte da Onda Direta
#==============================================================================
            rec_clean = np.zeros((rec.data.shape[0],rec.data.shape[1]))
            rec_clean = rec.data - rec_homo[k,:,:]
                        
            np.save("data_save/rec_data_model_%d_source_%d_type_%d"%(i,k,tmodel),rec_clean[:,nbl:-nbl])
    
            if(verbosity>0):
    
                #rplot.graph2d(u.data[0,:,:],teste,i,k,tmodel)
                rplot.graph2drec(rec_clean,teste,i,k,tmodel)
#==============================================================================