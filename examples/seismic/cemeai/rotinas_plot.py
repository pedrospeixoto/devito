#==============================================================================
# -*- encoding: utf-8 -*-
#==============================================================================

#==============================================================================
# Módulos Importados do Python / Devito / Examples
#==============================================================================

#==============================================================================
# Pyhton Modules and Imports
#==============================================================================
import numpy                   as np
import matplotlib.pyplot       as plot
import matplotlib.ticker       as mticker    
from   mpl_toolkits.axes_grid1 import make_axes_locatable
from   matplotlib              import cm
from   matplotlib              import ticker
#==============================================================================

#==============================================================================
# Plot do Deslocamento
#==============================================================================
def graph2d(U,teste,i,k,tmodel):

    x0    = teste.x0
    x1    = teste.x1
    z0    = teste.z0
    z1    = teste.z1
    nptx  = teste.nptx
    nptz  = teste.nptz
    nbl   = teste.nbl
    
    plot.figure(figsize = (14,4))
    fscale =  10**(-3)
    scale = np.amax(U[nbl:-nbl,nbl:-nbl])/50.
    extent = [fscale*x0,fscale*x1, fscale*z1, fscale*z0]
    fig = plot.imshow(np.transpose(U[nbl:-nbl,nbl:-nbl]), vmin=-scale, vmax=scale, cmap=cm.gray, extent=extent)      
    plot.gca().xaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f km'))
    plot.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f km'))
    plot.axis('equal')
    plot.title('Map - Acoustic Problem with Devito - Model %d - Source %d - Tipo %d'%(i,k,tmodel))
    plot.grid()
    ax = plot.gca()
    divider = make_axes_locatable(ax)
    ax.xaxis.set_major_locator(plot.MaxNLocator(4))
    ax.yaxis.set_major_locator(plot.MaxNLocator(4))
    cax = divider.append_axes("right", size="4%", pad=0.025)
    tick_locator = ticker.MaxNLocator(nbins=5)
    cbar = plot.colorbar(fig, cax=cax, format='%.2e')
    cbar.locator = tick_locator
    cbar.update_ticks()
    plot.draw()
    plot.savefig('figures/displacement/displacement_model_%d_source_%d_type_%d.png'%(i,k,tmodel),dpi=100)
    plot.show()
    plot.close()
#==============================================================================

#==============================================================================
# Plot dos Receivers
#==============================================================================
def graph2drec(rec,teste,i,k,tmodel):
      
    x0    = teste.x0
    x1    = teste.x1
    z0    = teste.z0
    z1    = teste.z1
    nptx  = teste.nptx
    nptz  = teste.nptz
    nbl   = teste.nbl
    t0    = teste.t0
    tn    = teste.tn
    
    plot.figure(figsize = (14,4))
    fscale =  10**(-3)
    scale = np.amax(rec[:,nbl:-nbl])/50.
    extent = [fscale*x0,fscale*x1, fscale*tn,fscale*t0]
    fig = plot.imshow(rec[:,nbl:-nbl], vmin=-scale, vmax=scale, cmap=cm.gray, extent=extent)
    plot.gca().xaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f km'))
    plot.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f s'))
    plot.axis('equal')
    if tmodel < 0:
        plot.title('Receivers Signal Profile - Devito - Homogeneous Model - Source %d '%(k))
    else:
        plot.title('Receivers Signal Profile - Devito - Model %d - Source %d - Type %d'%(i,k,tmodel))
    plot.grid()
    ax = plot.gca()
    divider = make_axes_locatable(ax)
    ax.xaxis.set_major_locator(plot.MaxNLocator(4))
    ax.yaxis.set_major_locator(plot.MaxNLocator(4))
    cax = divider.append_axes("right", size="4%", pad=0.025)
    tick_locator = ticker.MaxNLocator(nbins=5)
    cbar = plot.colorbar(fig, cax=cax, format='%.2e')
    cbar.locator = tick_locator
    cbar.update_ticks()
    if tmodel < 0:
        plot.savefig('figures/receivers/receivers_homog_source_%d.png'%(k),dpi=100)
    else:
        plot.savefig('figures/receivers/receivers_model_%d_source_%d_type_%d.png'%(i,k,tmodel),dpi=100)
    plot.show()
    plot.close()
#==============================================================================

#==============================================================================
# Plot Velocidades
#==============================================================================
def graph2dvel(vel,teste,i,tmodel):
    
    x0    = teste.x0
    x1    = teste.x1
    z0    = teste.z0
    z1    = teste.z1
    nptx  = teste.nptx
    nptz  = teste.nptz
    nbl   = teste.nbl
    
    plot.figure(figsize = (14,4))
    fscale =  10**(-3)
    
    scale  = np.amax(vel[nbl:-nbl,nbl:-nbl])
    extent = [fscale*x0,fscale*x1, fscale*z1, fscale*z0]
    fig = plot.imshow(np.transpose(vel[nbl:-nbl,nbl:-nbl]), vmin=np.amin(vel),vmax=scale, cmap=cm.jet, extent=extent)
    plot.gca().xaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f km'))
    plot.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f km'))
    plot.title('Velocity Profile - Model %d - Type %d'%(i,tmodel))
    plot.grid()
    ax = plot.gca()
    divider = make_axes_locatable(ax)
    ax.xaxis.set_major_locator(plot.MaxNLocator(4))
    ax.yaxis.set_major_locator(plot.MaxNLocator(4))
    cax = divider.append_axes("right", size="4%", pad=0.025)
    tick_locator = ticker.MaxNLocator(nbins=3)
    cbar = plot.colorbar(fig, cax=cax, format='%.2e')
    cbar.locator = tick_locator
    cbar.update_ticks()
    cbar.set_label('Velocity [km/s]')
    plot.savefig('figures/vel_model/vel_model_%d_type_%d.png'%(i,tmodel),dpi=100)
    plot.show()
    plot.close()
#==============================================================================