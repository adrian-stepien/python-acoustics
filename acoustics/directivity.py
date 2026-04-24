"""
Directivity
===========

The directivity module provides tools to work with directivity.

The following conventions are used within this module:

* The inclination angle :math:`\\theta` has a range :math:`[0, \\pi]`.
* The azimuth angle :math:`\\phi` has a range :math:`[0 , 2 \\pi]`.

"""

import abc

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize
from scipy.interpolate import RegularGridInterpolator
from scipy.special import sph_harm_y


def cardioid(theta, a=1.0, k=1.0):
    """
    A cardioid pattern.

    :param a: a
    :param k: k
    """
    return np.abs(a + a * np.cos(k * theta))


def figure_eight(theta, phi=0.0):
    """
    A figure-of-eight pattern.

    :param theta: angle :math:`\\theta`
    """
    del phi
    # return spherical_harmonic(theta, phi, m=0, n=1)
    return np.abs(np.cos(theta))


def spherical_harmonic(theta, phi, m=0, n=0):
    """Spherical harmonic of order `m` and degree `n`.

    .. note:: The degree `n` is often denoted `l`.

    .. seealso:: :func:`scipy.special.sph_harm_y`

    """
    return sph_harm_y(n, m, theta, phi).real


def spherical_to_cartesian(r, theta, phi):
    """
    Convert spherical coordinates to cartesian coordinates.

    :param r: norm
    :param theta: angle :math:`\\theta`
    :param phi: angle :math:`\\phi`

    .. math:: x = r \\sin{\\theta}\\cos{\\phi}
    .. math:: y = r \\sin{\\theta}\\sin{\\phi}
    .. math:: z = r \\cos{\\theta}
    """
    r = np.asanyarray(r)
    theta = np.asanyarray(theta)
    phi = np.asanyarray(phi)
    return (r * np.sin(theta) * np.cos(phi), r * np.sin(theta) * np.sin(phi), r * np.cos(theta))


def cartesian_to_spherical(x, y, z):
    """
    Convert cartesian coordinates to spherical coordinates.

    :param x: x
    :param y: y
    :param z: z

    .. math:: r = \\sqrt{\\left( x^2 + y^2 + z^2 \\right)}
    .. math:: \\theta = \\arccos{\\frac{z}{r}}
    .. math:: \\phi = \\operatorname{atan2}(y, x)
    """
    x = np.asanyarray(x)
    y = np.asanyarray(y)
    z = np.asanyarray(z)
    r = np.linalg.norm(np.vstack((x, y, z)), axis=0)
    theta = np.zeros_like(r, dtype=float)
    np.divide(z, r, out=theta, where=r != 0.0)
    theta = np.arccos(np.clip(theta, -1.0, 1.0))
    phi = np.mod(np.arctan2(y, x), 2.0 * np.pi)
    return r, theta, phi


class Directivity:
    """
    Abstract directivity class.

    This class defines several methods to be implemented by subclasses.
    """

    def __init__(self, rotation=None):
        if rotation is None:
            rotation = np.zeros(3, dtype=float)
        rotation = np.asarray(rotation, dtype=float)
        if rotation.shape != (3,):
            raise ValueError("rotation must be a three-element vector of X, Y, Z angles.")

        self.rotation = rotation
        """
        Rotation of the directivity pattern.
        """

    @abc.abstractmethod
    def _directivity(self, theta, phi):
        """
        This function should return the directivity as function of :math:`\\theta` and :math:`\\phi`.
        """

    def _undo_rotation(self, theta, phi):
        """
        Undo the configured rotation before sampling the base pattern.
        """
        x, y, z = spherical_to_cartesian(1.0, theta, phi)
        points = np.stack((x, y, z), axis=0)
        shape = points.shape[1:]
        rotated = self._rotation_matrix().T @ points.reshape(3, -1)
        _, theta, phi = cartesian_to_spherical(
            rotated[0].reshape(shape),
            rotated[1].reshape(shape),
            rotated[2].reshape(shape),
        )
        return theta, phi

    def _rotation_matrix(self):
        """Return the rotation matrix for the configured X, Y, Z Euler angles."""
        rx, ry, rz = self.rotation

        cx, sx = np.cos(rx), np.sin(rx)
        cy, sy = np.cos(ry), np.sin(ry)
        cz, sz = np.cos(rz), np.sin(rz)

        rot_x = np.array([[1.0, 0.0, 0.0], [0.0, cx, -sx], [0.0, sx, cx]])
        rot_y = np.array([[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]])
        rot_z = np.array([[cz, -sz, 0.0], [sz, cz, 0.0], [0.0, 0.0, 1.0]])
        return rot_z @ rot_y @ rot_x

    def using_spherical(self, r=None, theta=None, phi=None, include_rotation=True):
        """
        Return the directivity for given spherical coordinates.

        Accepts either ``(theta, phi)`` or ``(r, theta, phi)``.

        :param r: norm or angle :math:`\\theta`
        :param theta: angle :math:`\\theta` or :math:`\\phi`
        :param phi: angle :math:`\\phi`
        :param include_rotation: Apply the configured rotation before sampling.
        """
        if phi is None:
            if r is None or theta is None:
                raise TypeError("using_spherical() requires theta and phi coordinates.")
            theta, phi = r, theta

        if include_rotation and np.any(self.rotation):
            theta, phi = self._undo_rotation(theta, phi)

        return self._directivity(theta, phi)

    def using_cartesian(self, x, y, z, include_rotation=True):
        """
        Return the directivity for given cartesian coordinates.

        :param x: x
        :param y: y
        :param z: z

        """
        _, theta, phi = cartesian_to_spherical(x, y, z)
        return self.using_spherical(theta, phi, include_rotation=include_rotation)

    def plot(self, filename=None, include_rotation=True, sphere=False):
        """
        Directivity plot. Plot to ``filename`` when given.

        :param filename: Filename
        :param include_rotation: Apply the rotation to the directivity.
        :param sphere: Plot the directivity on the surface of a unit sphere.
        """
        fig = plot(self, include_rotation=include_rotation, sphere=sphere)
        if filename:
            fig.savefig(filename)
        return fig


class Omni(Directivity):
    """
    Class to work with omni-directional directivity.
    """

    def _directivity(self, theta, phi):
        """
        Directivity
        """
        return np.ones_like(theta)


class Cardioid(Directivity):
    """
    Cardioid directivity.
    """

    def _directivity(self, theta, phi):
        """
        Directivity
        """
        return cardioid(theta)


class FigureEight(Directivity):
    """Directivity of a figure of eight."""

    def _directivity(self, theta, phi):
        """Directivity"""
        return figure_eight(theta, phi)


class SphericalHarmonic(Directivity):
    """Directivity of a spherical harmonic of degree `n` and order `m`."""

    def __init__(self, rotation=None, m=None, n=None):

        super().__init__(rotation=rotation)
        self.m = m
        """Order `m`.
        """
        self.n = n
        """Degree `n`.
        """

    def _directivity(self, theta, phi):
        """Directivity"""
        return spherical_harmonic(theta, phi, self.m, self.n)


class Custom(Directivity):
    """
    A class to work with directivity.
    """

    def __init__(self, theta=None, phi=None, r=None, rotation=None):
        """
        Constructor.
        """
        super().__init__(rotation=rotation)

        self.theta = theta
        """
        Latitude. 1-D array.
        """
        self.phi = phi
        """
        Longitude. 1-D array.
        """
        self.r = r
        """
        Magnitude or radius. 2-D array.
        """

    def _directivity(self, theta, phi):
        """
        Custom directivity.

        Interpolate the directivity given longitude and latitude vectors.
        ``self.r`` is expected to have shape ``(len(self.theta), len(self.phi))``.
        """
        rgi = RegularGridInterpolator((self.theta, self.phi), self.r, bounds_error=False, fill_value=None)
        theta_arr = np.atleast_1d(theta)
        phi_arr = np.atleast_1d(phi)
        grid_theta, grid_phi = np.meshgrid(theta_arr, phi_arr, indexing='ij')
        return rgi((grid_theta, grid_phi))


def plot(d, sphere=False, include_rotation=True):
    """
    Plot directivity `d`.

    :param d: Directivity
    :type d: :class:`Directivity`

    :returns: Figure
    """
    theta, phi = np.meshgrid(np.linspace(0.0, np.pi, 50), np.linspace(0.0, +2.0 * np.pi, 50))

    # Directivity strength. Real-valued. Can be positive and negative.
    dr = d.using_spherical(theta, phi, include_rotation=include_rotation)

    if sphere:
        x, y, z = spherical_to_cartesian(1.0, theta, phi)

    else:
        x, y, z = spherical_to_cartesian(np.abs(dr), theta, phi)
    # R, theta, phi = cartesian_to_spherical(x, y, z)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # p = ax.plot_surface(x, y, z, cmap=plt.cm.jet, rstride=1, cstride=1, linewidth=0)

    norm = Normalize()
    norm.autoscale(dr)
    colors = cm.jet(norm(dr))
    m = cm.ScalarMappable(cmap=cm.jet, norm=norm)
    m.set_array(dr)
    ax.plot_surface(x, y, z, facecolors=colors, rstride=1, cstride=1, linewidth=0)
    plt.colorbar(m, ax=ax)

    ax.set_xlabel('$x$')
    ax.set_ylabel('$y$')
    ax.set_zlabel('$z$')
    return fig
