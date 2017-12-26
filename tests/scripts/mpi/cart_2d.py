# coding: utf-8

from pyccel.stdlib.parallel.mpi import mpi_init
from pyccel.stdlib.parallel.mpi import mpi_finalize

from pyccel.stdlib.parallel.mpi_new import Cart

ierr = -1

mpi_init(ierr)

# ...
ntx = 16
nty = 16

# Grid spacing
hx = 1.0/(ntx+1)
hy = 1.0/(nty+1)

# Equation Coefficients
c0 = (0.5*hx*hx*hy*hy)/(hx*hx+hy*hy)
c1 = 1.0/(hx*hx)
c2 = 1.0/(hy*hy)
# ...

mesh = Cart()

# ...
sx = mesh.starts[0]
ex = mesh.ends[0]

sy = mesh.starts[1]
ey = mesh.ends[1]
# ...

# ... grid without ghost cells
r_x  = range(sx, ex)
r_y  = range(sy, ey)

grid = tensor(r_x, r_y)
# ...

# ... extended grid with ghost cells
r_ext_x = range(sx-1, ex+1)
r_ext_y = range(sy-1, ey+1)

grid_ext = tensor(r_ext_x, r_ext_y)
# ...

# ...
u       = zeros(grid_ext, double)
u_new   = zeros(grid_ext, double)
u_exact = zeros(grid_ext, double)
f       = zeros(grid_ext, double)
# ...

# Initialization
x = 0.0
y = 0.0
for i,j in grid:
    x = i*hx
    y = j*hy

    f[i, j] = 2.0*(x*x-x+y*y-y)
    u_exact[i, j] = x*y*(x-1.0)*(y-1.0)
# ...


del mesh

mpi_finalize(ierr)
