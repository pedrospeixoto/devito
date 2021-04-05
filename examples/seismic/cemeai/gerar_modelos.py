#==============================================================================
# Bibliotecas Python
#==============================================================================
import numpy as np
import time
#==============================================================================

#==============================================================================
# Bibliotecas Devito
#==============================================================================
from examples.seismic import Model, plot_velocity
#==============================================================================

#==============================================================================
def generateRandomModel(teste,vmodelmin,vmodelmax,max_layers):

    shape      = (teste.nptx,teste.nptz)
    spacing    = (teste.hx,teste.hz)
    origin     = (teste.x0,teste.z0)
    sou        = teste.sou
    nbl        = teste.nbl
    v          = np.empty(shape, dtype=np.float32)

    vel_media    = np.sort(np.random.rand(max_layers+1)*int(vmodelmax-vmodelmin) + vmodelmin)
    vel_media[0] = vmodelmin;

    layer_type    = np.rint(np.random.rand(max_layers)).astype(int)
    layer_type[0] = 0;  

    n_layers = np.floor(np.random.rand() * max_layers + 1).astype(int)

    prof    = np.random.rand(n_layers) * np.rint(shape[1]/n_layers);
    prof[0] = np.rint(10)

    for k in range(n_layers):
        
        prof[k] = prof[k] + np.rint(shape[1]/n_layers)*k;
    
    k_vec = np.arange(0,n_layers)
    i_vec = np.arange(0,shape[0])
    j_vec = np.arange(0,shape[1])

    eq_layer = np.zeros((n_layers, shape[0]))
    
    incl = np.random.rand(max_layers) * 0.2 - 0.1; 
    ampl = np.random.rand(max_layers) * 20;
    wlen = np.random.rand(max_layers) * 0.5;
    cent = np.random.rand(max_layers) * shape[0];
    
    for k in range(0,n_layers):
        
        if(layer_type[k]==0):
        
            eq_layer[k,:] = incl[k] * i_vec + prof[k];
        
        else:
        
            eq_layer[k,:] = -ampl[k] * np.exp(-0.05 * wlen[k] * (i_vec-cent[k]) * (i_vec-cent[k])) + prof[k] + incl[k] * i_vec;

    i_vec = np.array([i_vec,]*shape[1]).transpose()
    j_vec = np.array([j_vec,]*shape[0])

    v[:, :] = vel_media[n_layers]
    
    for k in range(n_layers-1, -1, -1):
    
        indices = j_vec < eq_layer[k, i_vec]
        
        v[np.where(indices)] = vel_media[k]

    model = Model(vp=v,origin=origin,shape=shape,spacing=spacing,space_order=sou,nbl=nbl,bcs="damp")

    return model
#==============================================================================

#==============================================================================
def generateRandomModel_linhas(teste,vmodelmin,vmodelmax,max_layers):

    shape      = (teste.nptx,teste.nptz)
    spacing    = (teste.hx,teste.hz)
    origin     = (teste.x0,teste.z0)
    sou        = teste.sou
    nbl        = teste.nbl
    v          = np.empty(shape, dtype=np.float32)

    vel_media    = np.sort(np.random.rand(max_layers+1)*int(vmodelmax-vmodelmin) + vmodelmin)
    vel_media[0] = vmodelmin;

    layer_type    = np.rint(np.random.rand(max_layers)).astype(int)
    layer_type[0] = 0;  

    n_layers = np.floor(np.random.rand() * max_layers + 1).astype(int)

    prof    = np.random.rand(n_layers) * np.rint(shape[1]/n_layers);
    prof[0] = np.rint(10)

    for k in range(n_layers):
        
        prof[k] = prof[k] + np.rint(shape[1]/n_layers)*k;
    
    k_vec = np.arange(0,n_layers)
    i_vec = np.arange(0,shape[0])
    j_vec = np.arange(0,shape[1])

    eq_layer = np.zeros((n_layers, shape[0]))
    
    for k in range(0, n_layers):
        
        if(layer_type[k]==0):
        
            eq_layer[k, :] = prof[k]; 
                        
    i_vec = np.array([i_vec,]*shape[1]).transpose()
    j_vec = np.array([j_vec,]*shape[0])

    v[:,:] = vel_media[n_layers]
    
    for k in range(n_layers-1, -1, -1):
        
        indices = j_vec < eq_layer[k, i_vec]
        
        v[np.where(indices)] = vel_media[k]

    model = Model(vp=v,origin=origin,shape=shape,spacing=spacing,space_order=sou,nbl=nbl,bcs="damp")

    return model
#==============================================================================

#==============================================================================
def generateRandomModel_linha_inclinada(teste,vmodelmin,vmodelmax,max_layers):

    shape      = (teste.nptx,teste.nptz)
    spacing    = (teste.hx,teste.hz)
    origin     = (teste.x0,teste.z0)
    sou        = teste.sou
    nbl        = teste.nbl
    v          = np.empty(shape, dtype=np.float32)
        
    vel_media    = np.sort(np.random.rand(max_layers+1)*int(vmodelmax-vmodelmin) + vmodelmin)
    vel_media[0] = vmodelmin;

    layer_type    = np.rint(np.random.rand(max_layers)).astype(int)
    layer_type[0] = 0;

    n_layers = np.floor(np.random.rand() * max_layers + 1).astype(int)

    prof    = np.random.rand(n_layers) * np.rint(shape[1]/n_layers);
    prof[0] = np.rint(10)

    for k in range(n_layers):
        prof[k] = prof[k] + np.rint(shape[1]/n_layers)*k;

    k_vec = np.arange(0,n_layers)
    i_vec = np.arange(0,shape[0])
    j_vec = np.arange(0,shape[1])

    eq_layer = np.zeros( (n_layers, shape[0]) )

    incl = np.random.rand(max_layers) * 0.2 - 0.1;
    
    for k in range(0,n_layers):
        
        if(layer_type[k]==0):
        
            eq_layer[k,:] = incl[k] * i_vec + prof[k]; 
              
    i_vec = np.array([i_vec,]*shape[1]).transpose()
    j_vec = np.array([j_vec,]*shape[0])

    v[:,:] = vel_media[n_layers]
    
    for k in range(n_layers-1, -1, -1):
    
        indices = j_vec < eq_layer[k, i_vec]
        
        v[np.where(indices)] = vel_media[k]

    model = Model(vp=v,origin=origin,shape=shape,spacing=spacing,space_order=sou,nbl=nbl,bcs="damp")

    return model
#==============================================================================

#==============================================================================
def generateRandomModel_gaussiana(teste,vmodelmin,vmodelmax,max_layers):

    shape      = (teste.nptx,teste.nptz)
    spacing    = (teste.hx,teste.hz)
    origin     = (teste.x0,teste.z0)
    sou        = teste.sou
    nbl        = teste.nbl
    v          = np.empty(shape, dtype=np.float32)
        
    vel_media    = np.sort(np.random.rand(8) * 2 + vmodelmin)
    vel_media[0] = vmodelmin;

    layer_type    = np.rint(np.random.rand(max_layers)).astype(int)
    layer_type[0] = 0;

    n_layers = np.floor(np.random.rand() * max_layers + 1).astype(int)

    prof    = np.random.rand(n_layers) * np.rint(shape[1]/n_layers);
    prof[0] = np.rint(10)

    for k in range(n_layers):
        prof[k] = prof[k] + np.rint(shape[1]/n_layers)*k;

    k_vec = np.arange(0,n_layers)
    i_vec = np.arange(0,shape[0])
    j_vec = np.arange(0,shape[1])

    eq_layer = np.zeros( (n_layers, shape[0]) )

    ampl = np.random.rand(max_layers) * 20;
    wlen = np.random.rand(max_layers) * 0.5;
    cent = np.random.rand(max_layers) * shape[0];

    for k in range(0, n_layers):
        
        if(layer_type[k]== 0):
       
            eq_layer[k, :] = prof[k]; 
              
        else:
            
            eq_layer[k,:] = -ampl[k] * np.exp(-0.05 * wlen[k] * (i_vec-cent[k]) * (i_vec-cent[k])) + prof[k]
            
    i_vec = np.array([i_vec,]*shape[1]).transpose()
    j_vec = np.array([j_vec,]*shape[0])

    v[:,:] = vel_media[n_layers]
    
    for k in range(n_layers-1, -1, -1):
    
        indices = j_vec < eq_layer[k, i_vec]
        
        v[np.where(indices)] = vel_media[k]

    model = Model(vp=v,origin=origin,shape=shape,spacing=spacing,space_order=sou,nbl=nbl,bcs="damp")

    return model
#==============================================================================