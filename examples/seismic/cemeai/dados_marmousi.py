#==============================================================================
# Bibliotecas Python
#==============================================================================
import numpy                 as np
import segyio
import sys
from scipy.interpolate       import CubicSpline
from scipy.interpolate       import interp1d  
import matplotlib.pyplot       as plot
import matplotlib.ticker       as mticker    
from   mpl_toolkits.axes_grid1 import make_axes_locatable
from   matplotlib              import cm
from   matplotlib              import ticker  
#==============================================================================

#==============================================================================
# Manipulando Dados do Marmousi
#==============================================================================
with segyio.open('vel_models_file/marmousi_perfil1.segy') as segyfile:
    vel = segyio.tools.cube(segyfile)[0,:,:]
        
nptxvel = vel.shape[0]
nptyvel = vel.shape[1]
x0vel   =      0.        
x1vel   =  17000.     
y0vel   =      0.        
y1vel   =   3500.
hxvel   = (x1vel-x0vel)/(nptxvel-1)
hyvel   = (y1vel-y0vel)/(nptyvel-1)
Xvel    = np.linspace(x0vel,x1vel,nptxvel)
Yvel    = np.linspace(y0vel,y1vel,nptyvel)
fscale  = 10**(-3) 
vel     = fscale*vel
#==============================================================================

#==============================================================================
# Interpolando Dados do Marmousi
#==============================================================================
def inter_marmousi(teste):
        
    nptx      = teste.nptx
    nptz      = teste.nptz
    X0        = teste.X0
    Z0        = teste.Z0
    C0        = np.zeros((nptx,nptz))                     
        
    C0x = np.zeros((nptx,nptyvel))

    for j in range(nptyvel):
        x = Xvel
        y = vel[0:nptxvel,j]
        #cs = interp1d(x,y,kind='linear',fill_value="extrapolate")
        #cs = interp1d(x,y,kind='linear',fill_value="extrapolate")
        cs = interp1d(x,y,kind='nearest',fill_value="extrapolate")
        #cs = interp1d(x,y,kind='previous',fill_value="extrapolate")
        #cs = interp1d(x,y,kind='next',fill_value="extrapolate")
        #cs = CubicSpline(x,y)
        xs = X0
        C0x[0:nptx,j] = cs(xs)

    for i in range(nptx):
        x = Yvel
        y = C0x[i,0:nptyvel]
        #cs = interp1d(x,y,kind='linear',fill_value="extrapolate")
        #cs = interp1d(x,y,kind='linear',fill_value="extrapolate")
        cs = interp1d(x,y,kind='nearest',fill_value="extrapolate")
        #cs = interp1d(x,y,kind='previous',fill_value="extrapolate")
        #cs = interp1d(x,y,kind='next',fill_value="extrapolate")
        #cs = CubicSpline(x,y)
        xs = Z0
        C0[i,0:nptz] = cs(xs)

    return C0
#==============================================================================

#==============================================================================
# Plot Velocidades
#==============================================================================
def graph2dvel(vel,teste):
    
    x0    = teste.x0
    x1    = teste.x1
    z0    = teste.z0
    z1    = teste.z1
    nptx  = teste.nptx
    nptz  = teste.nptz
    
    plot.figure(figsize = (14,4))
    fscale =  10**(-3)
    
    scale  = np.amax(vel)
    extent = [fscale*x0,fscale*x1, fscale*z1, fscale*z0]
    fig = plot.imshow(np.transpose(vel), vmin=np.amin(vel),vmax=scale, cmap=cm.jet, extent=extent)
    plot.gca().xaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f km'))
    plot.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f km'))
    plot.title('Velocity Profile - Marmousi Interpolated')
    plot.grid()
    ax = plot.gca()
    divider = make_axes_locatable(ax)
    ax.xaxis.set_major_locator(plot.MaxNLocator(4))
    ax.yaxis.set_major_locator(plot.MaxNLocator(4))
    cax = divider.append_axes("right", size="4%", pad=0.025)
    tick_locator = ticker.MaxNLocator(nbins=4)
    cbar = plot.colorbar(fig, cax=cax, format='%.2e')
    cbar.locator = tick_locator
    cbar.update_ticks()
    cbar.set_label('Velocity [km/s]')
    plot.savefig('figures/vel_model/marmousi_interpolated.png',dpi=100)
    plot.show()
    plot.close()
#==============================================================================