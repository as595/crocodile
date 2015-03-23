# Bojan Nikolic <b.nikolic@mrao.cam.ac.uk>
# 
# Simulate data observed by an interferometer
#
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
#
# USEFUL NOTES
#
# From http://casa.nrao.edu/Memos/CoordConvention.pdf :
#
# UVW is a right-handed coordinate system, with W pointing towards the source, 
# and a baseline convention of ant2 - ant1 where index(ant1) < index(ant2).
# Consider an XYZ Celestial coordinate system centered at the location of the
# interferometer, with X towards the East, Z towards the NCP and Y to complete a 
# right-handed system. The UVW coordinate system is then defined by the hour-angle
# and declination of the phase-reference direction such that (a) when the 
# direction of observation is the NCP (ha=0,dec=90), the UVW coordinates are aligned
# with XYZ, (b) V, W and the NCP are always on a Great circle, (c) when W is
# on the local meridian, U points East (d) when the direction of observation is at 
# zero declination, an hour-angle of -6 hours makes W point due East. The (l,m,n)
# coordinates are parallel to (U,V,W) such that l increases with Right-Ascension 
# (or increasing longitude coordinate), m increases with Declination, and n is towards
# the source. With this convention, images will have Right Ascension increasing 
# from Right to Left, and Declination increasing from Bottom to Top.
#
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# 
# [150323 - AMS]    Correction to rot(), introduced -1 factor in v calculation.
#                   Change to bsl(), to agree with casa convention.
#
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------


import numpy

def rot(ants_xyz, ha, dec):

    """
    Rotate (x,y,z) antenna positions in earth coordinates 
    to (u,v,w) coordinates relative to 
    astronomical source position (ra, dec).

    (see note on co-ordinate systems in header)
    """

    # ants_xyz : (x,y,z) co-ordinates of antennas in array
    # ha : hour angle of source (ha = ra - lst)
    # dec : declination of source

    x,y,z=numpy.hsplit(ants_xyz,3)

    t=x*numpy.cos(ha) - y*numpy.sin(ha)
    u=x*numpy.sin(ha) + y*numpy.cos(ha)
    v=-1.*t*numpy.sin(dec)+ z*numpy.cos(dec)
    w=t*numpy.cos(dec)+ z*numpy.sin(dec)

    ants_uvw = numpy.hstack([u,v,w])

    return ants_uvw


def bls(ants_uvw):

    """
    Compute baselines in uvw co-ordinate system from 
    uvw co-ordinate system station positions
    """

    # ants_uvw : (u,v,w) co-ordinates of antennas in array
    # basel_uvw : delta-(u,v,w) values for baseline
    
    res=[]
    for i in range(ants_uvw.shape[0]):
        for j in range(i+1, ants_uvw.shape[0]):
            res.append(ants_uvw[j]-ants_uvw[i])

    basel_uvw = numpy.array(res)

    return basel_uvw


def genuv(ants_xyz, ha_range, dec):

    """
    Calculate baselines in (u,v,w) co-ordinate system 
    for a range of hour angles (i.e. non-snapshot observation)
    to create a uvw sampling distribution
    """

    # ants_xyz : (x,y,z) co-ordinates of antennas in array
    # ha_range : list of hour angle values for astronomical source as function of time
    # dec : declination of astronomical source [constant, not f(t)]
    # dist_uvw : (u,v,w) distribution of projected baselines

    dist_uvw = numpy.concatenate([bls(rot(ants_xyz,hax,dec)) for hax in ha_range])

    return dist_uvw


def genvis(dist_uvw, l, m):

    """
    Simulate visibilities for unit amplitude point source at 
    angular position (l,m) relative to observed phase centre 
    defined at (ra,dec).

    Note that point source is delta function, therefore
    FT relation ship becomes an exponential, evaluated at 
    (uvw.lmn)
    """

    # dist_uvw : (u,v,w) distribution of projected baselines
    # l : direction cosine relative to phase centre defined at (ra,dec)
    # m : orthogonal directon cosine relative to phase centre defined at (ra,dec)
    # s : (l,m,n) vector direction to source 
    # vis : complex valued visibility data 

    s=numpy.array([l, m , numpy.sqrt(1 - l**2 - m**2)])
    vis = numpy.exp(-2j*numpy.pi* numpy.dot(dist_uvw, s))

    return vis

