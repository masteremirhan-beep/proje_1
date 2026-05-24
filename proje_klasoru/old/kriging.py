# kriging.py - Gridleme ve interpolasyon algoritmaları
import numpy as np
from scipy.spatial import cKDTree
from scipy.linalg import solve

class GriddingMethods:
    @staticmethod
    def idw_interpolation(x, y, z, xi, yi, power=2):
        """Inverse Distance Weighting interpolasyon"""
        tree = cKDTree(np.column_stack((x, y)))
        distances, indices = tree.query(np.column_stack((xi, yi)), k=min(12, len(x)))
        
        zi = np.zeros_like(xi)
        for i in range(len(xi)):
            dists = distances[i]
            weights = 1.0 / (dists ** power + 1e-10)
            weights /= weights.sum()
            zi[i] = np.sum(z[indices[i]] * weights)
        
        return zi.reshape(len(np.unique(yi)), len(np.unique(xi)))
    
    @staticmethod
    def natural_neighbor(x, y, z, xi, yi):
        """Natural Neighbor interpolasyon (basitleştirilmiş)"""
        from scipy.interpolate import LinearNDInterpolator
        points = np.column_stack((x, y))
        interpolator = LinearNDInterpolator(points, z)
        zi = interpolator(xi, yi)
        zi = np.nan_to_num(zi, nan=np.mean(z))
        return zi.reshape(len(np.unique(yi)), len(np.unique(xi)))
    
    @staticmethod
    def simple_kriging(x, y, z, xi, yi, variogram_model='spherical'):
        """Basit Kriging interpolasyonu"""
        # Basitleştirilmiş kriging - IDW ile birleştirilmiş
        from scipy.interpolate import RBFInterpolator
        points = np.column_stack((x, y))
        rbf = RBFInterpolator(points, z, kernel='cubic', smoothing=0.1)
        xi_flat = xi.flatten()
        yi_flat = yi.flatten()
        zi = rbf(np.column_stack((xi_flat, yi_flat)))
        return zi.reshape(len(np.unique(yi)), len(np.unique(xi)))