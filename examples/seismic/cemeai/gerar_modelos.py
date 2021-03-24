#NBVAL_IGNORE_OUTPUT
from examples.seismic import Model, plot_velocity
import numpy as np
import time


def generateRandomModel(shape, spacing, origin):

    # Define a velocity profile. The velocity is in km/s
    v = np.empty(shape, dtype=np.float32)

    max_layers = 7;
    incl = np.random.rand(7) * 0.2 - 0.1; # numeros aleatorios entre -0.1 e 0.1
    ampl = np.random.rand(7) * 20;
    wlen = np.random.rand(7) * 0.5;
    cent = np.random.rand(7) * shape[0];

    vel_media = np.sort(np.random.rand(8) * 2 + 1.5)
    vel_media[0] = 1.5; ######## restricao

    # sorteio da equacao para cada layer (sin ou reta)
    layer_type = np.rint(np.random.rand(7)).astype(int)
    layer_type[0] = 0;  ######## restricao

    # sorteio do numero de camadas
    n_layers = np.floor(np.random.rand() * 7 + 1).astype(int)


    prof = np.random.rand(n_layers) * np.rint(shape[1]/n_layers);
    prof[0] = np.rint(10) ######## restricao

    for k in range(n_layers):
        prof[k] = prof[k] + np.rint(shape[1]/n_layers)*k;

    
    k_vec = np.arange(0, n_layers)
    i_vec = np.arange(0, shape[0])
    j_vec = np.arange(0, shape[1])

    eq_layer = np.zeros( (n_layers, shape[0]) )
    
    for k in range(0, n_layers):
        if layer_type[k] == 0:
            eq_layer[k, :] = incl[k] * i_vec + prof[k];
        else:
            #eq_layer = ampl[k] * np.sin(wlen[k] * i) + prof[k];
            eq_layer[k, :] = -ampl[k] * np.exp(-0.05 * wlen[k] * (i_vec-cent[k]) * (i_vec-cent[k])) + prof[k] + incl[k] * i_vec;

    i_vec = np.array([i_vec,]*shape[1]).transpose()
    j_vec = np.array([j_vec,]*shape[0])

    v[:, :] = vel_media[n_layers]
    for k in range(n_layers-1, -1, -1):
        indices = j_vec < eq_layer[k, i_vec]
        v[np.where(indices)] = vel_media[k]

    # With the velocity and model size defined, we can create the seismic model that
    # encapsulates this properties. We also define the size of the absorbing layer as 10 grid points
    model = Model(vp=v, origin=origin, shape=shape, spacing=spacing,
                  space_order=2, nbl=10, bcs="damp")

    return model


# Define a physical size
#shape   = (101, 51)  # Number of grid point (nx, nz)
#spacing = (20., 20.)  # Grid spacing in m. The domain size is now 2km by 1km
#origin = (0. , 0.)  # What is the location of the top left corner. This is necessary to define

# Seeding the RNG
#np.random.seed(int(time.time()))
# np.random.seed(0)

# Generates the model
#model = generateRandomModel(shape, spacing, origin)

#plot_velocity(model)