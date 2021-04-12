#==============================================================================
# Bibliotecas Python
#==============================================================================
import numpy as np
import time
import random
#==============================================================================

#==============================================================================
# Bibliotecas Devito
#==============================================================================
from examples.seismic import Model, plot_velocity
#==============================================================================

#==============================================================================
def generateRandomModel(teste,vmodelmin,vmodelmax,max_layers, layer_profile=[False, False, False]):
    #Layer_profile 
    # Pos1 = horizontal lines
    # Pos2 = inclined lines
    # Pos3 = Gaussian
    # 

    shape      = (teste.nptx,teste.nptz)
    spacing    = (teste.hx,teste.hz)
    origin     = (teste.x0,teste.z0)
    sou        = teste.sou
    nbl        = teste.nbl
    v          = np.empty(shape, dtype=np.float32)

    #vel_media    = np.sort(np.random.rand(max_layers+1)*int(vmodelmax-vmodelmin) + vmodelmin)
    vel_media    = np.random.rand(max_layers+1)*int(vmodelmax-vmodelmin) + vmodelmin
    vel_media[0] = vmodelmin

    nlayer_type = 0
    if layer_profile[0] or layer_profile[1] or layer_profile[2]:
        n_layers = np.floor(np.random.rand() * max_layers+1).astype(int)
        prof    = (0.3 + np.random.rand(n_layers)*0.7) * np.rint(shape[1]/n_layers)
        prof[0] = np.rint(shape[1]/n_layers)*(1-0.8*random.random())
        nlayer_type = 1
    else :
        n_layers = 0 #homogeneous case

    for k in range(1,n_layers):
        prof[k] = prof[k-1] + prof[k]
    
    k_vec = np.arange(0,n_layers)
    i_vec = np.arange(0,shape[0])
    j_vec = np.arange(0,shape[1])

    eq_layer = np.zeros((n_layers, shape[0]))
    
    if layer_profile[1]: #Inclined lines
        nlayer_type = nlayer_type + 1
        incl = np.random.rand(n_layers) * 0.2 - 0.1
    else:
        incl = np.zeros(n_layers) 

    if layer_profile[2]: #Gaussian
        nlayer_type = nlayer_type + 1
        ampl = (np.random.rand(n_layers)*2.0-1.0 )* 100
        wlen = np.random.rand(n_layers) * 0.005
        cent = np.random.rand(n_layers) * shape[0]
    else:
        ampl = np.zeros(n_layers) 
        wlen = np.zeros(n_layers) 
        cent = np.zeros(n_layers)  * shape[0]
    
    #Random choice of layer type
    layer_type    = np.rint(nlayer_type*np.random.rand(n_layers)).astype(int)
    layer_type[0] = 0;  #first layer if a horizontal line
    #print(layer_type, n_layers)
    for k in range(0,n_layers):
        
        if(layer_type[k]==0): #only horizontal lines
            eq_layer[k,:] = prof[k]

        elif (layer_type[k]==1): #inclined lines
            eq_layer[k,:] = incl[k] * i_vec + prof[k]

        elif (layer_type[k]==2): #gaussian only
            eq_layer[k,:] = -ampl[k] * np.exp(-0.05 * wlen[k] * (i_vec-cent[k]) * (i_vec-cent[k])) + prof[k] + incl[k] * i_vec

        else: #Mix everything
        
            eq_layer[k,:] = - ampl[k] * np.exp(-0.05 * wlen[k] * (i_vec-cent[k]) * (i_vec-cent[k])) + prof[k] + incl[k] * i_vec
        #print(k, eq_layer[k,1:5])
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