#==============================================================================
# -*- encoding: utf-8 -*-
#==============================================================================

#==============================================================================
# Módulos Importados do Python / Devito / Examples
#==============================================================================

#==============================================================================
# Pyhton Modules and Imports
#==============================================================================
import numpy as np
import math  as mt
#==============================================================================

#==============================================================================
class teste1:
#==============================================================================

#==============================================================================
#Parâmetros de Malha e Tempo
#==============================================================================
    ncamadas   = 4
    N0         = 1
    N1         = 1
    N2         = 1  
    N3         = 1  
    nptx       = 101
    nptz       = 51
    x0         = 0.0
    x1         = 2000
    z0         = 0.0 
    z1         = 1000
    X0         = np.linspace(x0,x1,nptx)
    Z0         = np.linspace(z0,z1,nptz) 
    compx      = x1-x0
    compz      = z1-z0
    hx         = (x1-x0)/(nptx-1)           
    hz         = (z1-z0)/(nptz-1)           
    sou        = 2
    tou        = 2
    nbl        = 10 
    t0         = 0.
    tn         = 1000.
    ntmax      = 401
    CFL        = 0.4
    nfonte     = 1
    f0         = 0.020 
    nxfontpos  = np.array([500.,1000.])   
    nzfontpos  = 20.                        
    nrec       = 51
    nxrecpos   = np.linspace(x0,x1,nrec)   
    nzrecpos   = 20.            
    verbosity  = 1
    sintmodel  = 0
    max_layers = 7                                   
#==============================================================================

#==============================================================================
class teste2:
#==============================================================================

#==============================================================================
#Parâmetros de Malha e Tempo
#==============================================================================
    ncamadas   = 4   #Numero de tipo de esquemas de camadas
    N0         = 40   #numero de amostras do tipo de esquema só horizontal
    N1         = 40   #numero de amostras do tipo de esquema só retas
    N2         = 40   #numero de amostras do tipo de esquema só gaussianas
    N3         = 40   #numero de amostras do tipo de esquema misto de tudo
    nptx       = 901
    nptz       = 321
    x0         = 4000
    x1         = 13000
    z0         = 0 
    z1         = 3200
    X0         = np.linspace(x0,x1,nptx)
    Z0         = np.linspace(z0,z1,nptz) 
    compx      = x1-x0
    compz      = z1-z0
    hx         = (x1-x0)/(nptx-1)           
    hz         = (z1-z0)/(nptz-1)           
    sou        = 4
    tou        = 2
    nbl        = 150 
    t0         = 0.
    tn         = 5000.
    ntmax      = 5000
    CFL        = 0.4
    nfonte     = 1
    f0         = 0.02 
    #nxfontpos  = np.array([4500])
    nxfontpos  = np.array([4500, 5500, 6500, 7500, 8500, 9500, 10500, 11500, 12500])   
    nzfontpos  = 50.                        
    nrec       = nptx
    nxrecpos   = np.linspace(x0,x1,nrec)   
    nzrecpos   = 50.            
    verbosity  = 1
    sintmodel  = 1
    max_layers = 10
#==============================================================================