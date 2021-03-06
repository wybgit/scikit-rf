

'''
.. module:: skrf.media.freespace

========================================
freespace (:mod:`skrf.media.freespace`)
========================================

A plane-wave (TEM Mode) in Freespace.

Represents a plane-wave in a homogeneous freespace, defined by
the space's relative permittivity and relative permeability.

The field properties of space are related to a distributed
circuit transmission line model given in circuit theory by:

===============================  ==============================
Circuit Property                 Field Property
===============================  ==============================
distributed_capacitance          real(ep_0*ep_r)
distributed_resistance           imag(ep_0*ep_r)
distributed_inductance           real(mu_0*mu_r)
distributed_conductance          imag(mu_0*mu_r)
===============================  ==============================

========================  =============  =================  ================================================
               Circuit Property                 Field Property
---------------------------------------  -------------------------------------------------------------------
Variable                  Symbol         Variable           Symbol
========================  =============  =================  ================================================
distributed_capacitance   :math:`C^{'}`  real(ep_0*ep_r)    :math:`\\Re e \{\\epsilon_{0} \\epsilon_{r} \}`
distributed_resistance    :math:`R^{'}`  imag(ep_0*ep_r)    :math:`\\Im m \{\\epsilon_{0} \\epsilon_{r} \}`
distributed_inductance    :math:`L^{'}`  real(mu_0*mu_r)    :math:`\\Re e \{\\mu_{0} \\mu_{r} \}`
distributed_conductance   :math:`G^{'}`  imag(mu_0*mu_r)    :math:`\\Im m \{\\mu_{0} \\mu_{r} \}`
========================  =============  =================  ================================================

'''
from scipy.constants import  epsilon_0, mu_0
from numpy import real, imag, cos
from .distributedCircuit import DistributedCircuit
from .media import Media
from ..data import materials

class Freespace(DistributedCircuit, Media):
    '''
    A plane-wave (TEM Mode) in Freespace.

    Parameters
    -----------
    frequency : :class:`~skrf.frequency.Frequency` object
            frequency band of this transmission line medium
    z0 : number, array-like, or None
        the port impedance for media. Only needed if  its different
        from the characterisitc impedance of the transmission
        line. if z0 is None then will default to Z0
    ep_r : number, array-like
            complex relative permittivity
    mu_r : number, array-like
            possibly complex, relative permeability
    mode_type: ['tem','te','tm']
        the type of mode 
    angle : float
        If mode_type != 'tem', this sets mode the angle (in radians) from 
        the direction the mode is transverse to 
            
    \*args, \*\*kwargs : arguments and keyword arguments

    
    '''
    def __init__(self, frequency=None, z0=None,  ep_r=1+0j, 
                 mu_r=1+0j, rho=None, mode_type='tem', angle=0, 
                 *args, **kwargs):
        
        Media.__init__(self, frequency=frequency,z0=z0)
        self.ep_r  = ep_r
        self.mu_r  = mu_r
        self.mode_type = mode_type.lower()
        self.angle = angle
        self.rho=rho
        
        


    @property
    def R(self):
        return self.frequency.w *imag(mu_0*self.mu_r)
    
    @property
    def L(self):
        return real(mu_0*self.mu_r)
    
    @property
    def C(self):
        return real(epsilon_0*self.ep_r)
    
    @property
    def G(self):
        if self.rho is not None:
            conductivity=1./self.rho
        else:
            conductivity=0
            
        return conductivity+ self.frequency.w *imag(epsilon_0*self.ep_r)
        
    @property
    def Z0(self):
        '''
        Characteristic Impedance, :math:`Z0`

        .. math::
                Z_0 = \\sqrt{ \\frac{Z^{'}}{Y^{'}}}

        Returns
        --------
        Z0 : numpy.ndarray
                Characteristic Impedance in units of ohms
        '''
        Z0 = DistributedCircuit.Z0.fget(self)
        Z0_dict = {'te':Z0/cos(self.angle),
                   'tm':Z0*cos(self.angle),
                   'tem':Z0}
        return Z0_dict[self.mode_type]
    
    @property
    def rho(self):
        '''
        conductivty in ohm*m

        Parameters
        --------------
        val : float, array-like or str
            the conductivity in ohm*m. If array-like must be same length
            as self.frequency. if str, it must be a key in
            `skrf.data.materials`.

        Examples
        ---------
        >>> wg.rho = 2.8e-8
        >>> wg.rho = 2.8e-8 * ones(len(wg.frequency))
        >>> wg.rho = 'al'
        >>> wg.rho = 'aluminum'
        '''
        

        return self._rho
            
    @rho.setter
    def rho(self, val):
        if isinstance(val, str):
            self._rho = materials[val.lower()]['resistivity(ohm*m)']
        else:
            self._rho=val

    @property
    def gamma(self):
        '''
        Propagation Constant, :math:`\\gamma`

        Defined as,

        .. math::
                \\gamma =  \\sqrt{ Z^{'}  Y^{'}}

        Returns
        --------
        gamma : numpy.ndarray
                Propagation Constant,

        Notes
        ---------
        The components of propagation constant are interpreted as follows:

        positive real(gamma) = attenuation
        positive imag(gamma) = forward propagation
        '''
        return  DistributedCircuit.gamma.fget(self)*cos(self.angle)
        
    
    def __str__(self):
        f=self.frequency
        output =  \
                'Freespace  Media.  %i-%i %s.  %i points'%\
                (f.f_scaled[0],f.f_scaled[-1],f.unit, f.npoints)
        return output

    def __repr__(self):
        return self.__str__()
