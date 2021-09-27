import math
from math import sin, cos, sqrt, fabs, atan2
from math import pi as PI

# Beijing54 Geodetic coordinate system (Krasovsky reference ellipsoid)
kKRASOVSKY_A = 6378245.0				 # equatorial radius [unit: meter]
kKRASOVSKY_B = 6356863.0187730473  # polar radius
kKRASOVSKY_ECCSQ = 6.6934216229659332e-3  # first eccentricity squared
kKRASOVSKY_ECC2SQ = 6.7385254146834811e-3  # second eccentricity squared
PI = 3.14159265358979323846   # π

kDEG2RAD = PI / 180.0
kRAD2DEG = 180.0 / PI


# /**
#  *  \brief Angle unit transform, degree to radian
#  *
#  *  \param [in] deg: angle in degrees
#  *  \return Returns angle in radians
#  *  \time 15:21:22 2020/06/12
#  */
def Deg2Rad(deg):
    return deg * kDEG2RAD


# /**
#  *  \brief Angle unit transform, radian to degree
#  *
#  *  \param [in] rad: angle in radians
#  *  \return Returns angle in degrees
#  *  \time 15:21:01 2020/06/12
#  */
def Rad2Deg(rad):
    return rad * kRAD2DEG

# /**
#  *  \brief Get geodetic offset used by GCJ-02
#  *
#  *  \param [in] wgs84lon: longitude in WGS84 coordinate system [unit:degree]
#  *  \param [in] wgs84lat: latitude in WGS84 coordinate system [unit:degree]
#  *  \return Returns a pair of geodetic offset used by GCJ-02
#  *  \time 15:28:33 2020/06/12
#  */


def GetGeodeticOffset(wgs84lon, wgs84lat):
    # get geodetic offset relative to 'center china'
    lon0 = wgs84lon - 105.0
    lat0 = wgs84lat - 35.0

    # generate an pair offset roughly in meters
    lon1 = 300.0 + lon0 + 2.0 * lat0 + 0.1 * lon0 * \
        lon0 + 0.1 * lon0 * lat0 + 0.1 * sqrt(fabs(lon0))
    lon1 = lon1 + (20.0 * sin(6.0 * lon0 * PI) + 20.0 *
                   sin(2.0 * lon0 * PI)) * 2.0 / 3.0
    lon1 = lon1 + (20.0 * sin(lon0 * PI) + 40.0 *
                   sin(lon0 / 3.0 * PI)) * 2.0 / 3.0
    lon1 = lon1 + (150.0 * sin(lon0 / 12.0 * PI) + 300.0 *
                   sin(lon0 * PI / 30.0)) * 2.0 / 3.0
    lat1 = -100.0 + 2.0 * lon0 + 3.0 * lat0 + 0.2 * lat0 * \
        lat0 + 0.1 * lon0 * lat0 + 0.2 * sqrt(fabs(lon0))
    lat1 = lat1 + (20.0 * sin(6.0 * lon0 * PI) + 20.0 *
                   sin(2.0 * lon0 * PI)) * 2.0 / 3.0
    lat1 = lat1 + (20.0 * sin(lat0 * PI) + 40.0 *
                   sin(lat0 / 3.0 * PI)) * 2.0 / 3.0
    lat1 = lat1 + (160.0 * sin(lat0 / 12.0 * PI) + 320.0 *
                   sin(lat0 * PI / 30.0)) * 2.0 / 3.0

    # latitude in radian
    B = Deg2Rad(wgs84lat)
    sinB = sin(B)
    cosB = cos(B)
    W = sqrt(1 - kKRASOVSKY_ECCSQ * sinB * sinB)
    N = kKRASOVSKY_A / W

    # geodetic offset used by GCJ-02
    lon2 = Rad2Deg(lon1 / (N * cosB))
    lat2 = Rad2Deg(lat1 * W * W / (N * (1 - kKRASOVSKY_ECCSQ)))
    return lon2, lat2


# /**
#  *  \brief Covert geodetic coordinate in WGS84 coordinate system to geodetic coordinate
#  *         in GCJ-02 coordinate system
#  *
#  *  \param [in] wgs84lon: longitude in WGS84 coordinate system [unit:degree]
#  *  \param [in] wgs84lat: latitude in WGS84 coordinate system [unit:degree]
#  *  \return Returns geodetic coordinate in GCJ-02 coordinate system
#  *  \time 15:47:38 2020/06/12
#  */
def Wgs2Gcj(wgs84lon, wgs84lat):
    dlon, dlat = GetGeodeticOffset(wgs84lon, wgs84lat)
    gcj02lon = wgs84lon + dlon
    gcj02lat = wgs84lat + dlat
    return gcj02lon, gcj02lat

# /**
#  *  \brief Covert geodetic coordinate in GCJ-02 coordinate system to geodetic coordinate
#  *         in WGS84 coordinate system
#  *
#  *  \param [in] gcj02lon: longitude in GCJ-02 coordinate system [unit:degree]
#  *  \param [in] gcj02lat: latitude in GCJ-02 coordinate system [unit:degree]
#  *  \return Returns geodetic coordinate in WGS84 coordinate system
#  *  \remark simple linear iteration
#  *	\detail
#  *  \time 15:51:13 2020/06/12
#  */


def Gcj2Wgs_SimpleIteration(gcj02lon, gcj02lat):
    lon0, lat0 = Wgs2Gcj(gcj02lon, gcj02lat)
    for _ in range(1000):
        lon1, lat1 = Wgs2Gcj(lon0, lat0)
        dlon = lon1 - gcj02lon
        dlat = lat1 - gcj02lat
        lon1 = lon0 - dlon
        lat1 = lat0 - dlat
        # 1.0e-9 degree corresponding to 0.1mm
        if (fabs(dlon) < 1.0e-9 and fabs(dlat) < 1.0e-9):
            break
        lon0 = lon1
        lat0 = lat1
    return lon0, lat0

# /**
#  *  \brief Calculate the partial derivatives with respect to estimated longitude in WGS84
#  *
#  *  \param [in] wgs84lon: estimated longitude in WGS84 coordinate system [unit:degree]
#  *  \param [in] wgs84lat: estimated latitude in WGS84 coordinate system [unit:degree]
#  *  \param [in] dlon: delta longitude (close to zero) in WGS84 coordinate system [unit:degree],
#  *  \return Returns partial derivatives with respect to estimated longitude in WGS84
#  *  \time 20:26:16 2020/06/13
#  */


def GetPartialDerivative_Lon(wgs84lon, wgs84lat, dlon):
    lonBk = wgs84lon + dlon
    lonFw = wgs84lon - dlon
    gcjlonBk, gcjlatBk = Wgs2Gcj(lonBk, wgs84lat)
    gcjlonFw, gcjlatFw = Wgs2Gcj(lonFw, wgs84lat)
    dlongcj_dlonwgs = (gcjlonBk - gcjlonFw) / (dlon * 2.0)
    dlatgcj_dlonwgs = (gcjlatBk - gcjlatFw) / (dlon * 2.0)
    return dlongcj_dlonwgs, dlatgcj_dlonwgs

# /**
#  *  \brief Calculate the partial derivatives with respect to estimated latitude in WGS84
#  *
#  *  \param [in] wgs84lon: estimated longitude in WGS84 coordinate system [unit:degree]
#  *  \param [in] wgs84lat: estimated latitude in WGS84 coordinate system [unit:degree]
#  *  \param [in] dlat: delta latitude (close to zero) in WGS84 coordinate system [unit:degree],
#  *  \return Returns partial derivatives with respect to estimated latitude in WGS84
#  *  \time 20:26:25 2020/06/13
#  */


def GetPartialDerivative_Lat(wgs84lon, wgs84lat, dlat):
    latBk = wgs84lat + dlat
    latFw = wgs84lat - dlat
    gcjlonBk, gcjlatBk = Wgs2Gcj(wgs84lon, latBk)
    gcjlonFw, gcjlatFw = Wgs2Gcj(wgs84lon, latFw)
    dlongcj_dlatwgs = (gcjlonBk - gcjlonFw) / (dlat * 2.0)
    dlatgcj_dlatwgs = (gcjlatBk - gcjlatFw) / (dlat * 2.0)
    return dlongcj_dlatwgs, dlatgcj_dlatwgs

# /**
#  *  \brief Covert geodetic coordinate in GCJ-02 coordinate system to geodetic coordinate
#  *         in WGS84 coordinate system
#  *
#  *  \param [in] gcj02lon: longitude in GCJ-02 coordinate system [unit:degree]
#  *  \param [in] gcj02lat: latitude in GCJ-02 coordinate system [unit:degree]
#  *  \return Returns geodetic coordinate in WGS84 coordinate system
#  *  \remark the encryption formula is unknown but we can covert point in WGS84 to point
#  *          in GCJ-02 with an API,then use the numerical derivation method to solve the
#  *          problem
#  *	\detail Assuming the encryption formula is
#  *
#  *			gcj02lon = Wgs2Gcj(wgs84lon, wgs84lat)
#  *			gcj02lat = Wgs2Gcj(wgs84lon, wgs84lat)
#  *
#  *	 In the rectification process, (wgs84lon, wgs84lat) are unknown items. Obviously,
#  *   this is a system of nonlinear equations.
#  *
#  *   The linear formed error functions of forward intersection come from
#  *   consideration of a Taylor series expansion.
#  *           V = AX - b
#  *    here:
#  *    V: The residuals of the observed values
#  *    A: The jacobian matrix
#  *    X: The modification of the unknown items
#  *    b: The constant terms of the error functions
#  *
#  *    Then the error functions written in vector form are:
#  *    | V_lon | = | dlongcj_dlonwgs  dlongcj_dlatwgs |  | d_lonwgs | - | l_lon |
#  *    | V_lat | = |         0        dlatgcj_dlatwgs |  | d_latwgs | - | l_lat |
#  *    here:
#  *    l_lon = longcj - longcj'                 // the modification of longcj
#  *    l_lat = latgcj - latgcj'                 // the modification of latgcj
#  *    longcj : the observed longitude in GCJ-02
#  *    latgcj : the observed latitude in GCJ-02
#  *    longcj' = Wgs2Gcj(wgs84lon',wgs84lat')    // estimated longitude in GCJ-02
#  *    latgcj' = Wgs2Gcj(wgs84lon',wgs84lat')    // estimated latitude in GCJ-02
#  *    wgs84lon' : estimated longitude in WGS84
#  *    wgs84lat' : estimated latitude in WGS84
#  *    d_lonwgs : unknown items
#  *    d_latwgs : unknown items
#  *    wgs84lon = wgs84lon' + d_lonwgs                           // update
#  *    wgs84lat = wgs84lat' + d_latwgs
#  *
#  *	  let V = [V_lon V_lat]T = 0, then
#  *	  d_latwgs = (l_lon * dlatgcj_dlonwgs - l_lat * dlongcj_dlonwgs) /
#  *			(dlongcj_dlatwgs * dlatgcj_dlonwgs - dlatgcj_dlatwgs * dlongcj_dlonwgs)
#  *	  d_lonwgs = (l_lon - dlongcj_dlatwgs * d_latwgs) / dlongcj_dlonwgs
#  *
#  *    This iterative procedure is repeated until X= [d_lonwgs d_latwgs]T are
#  *    sufficiently small.
#  *  \time 17:42:01 2020/06/12
#  */


def Gcj2Wgs_NumbericDiff(gcj02lon, gcj02lat):
    wgs84lon = gcj02lon
    wgs84lat = gcj02lat
    tol = 1e-9
    for _ in range(1000):
        dlongcj_dlonwgs, dlatgcj_dlonwgs = GetPartialDerivative_Lon(
            wgs84lon, wgs84lat, tol)
        dlongcj_dlatwgs, dlatgcj_dlatwgs = GetPartialDerivative_Lat(
            wgs84lon, wgs84lat, tol)

        gcj02lonEst, gcj02latEst = Wgs2Gcj(wgs84lon, wgs84lat)
        l_lon = gcj02lon - gcj02lonEst
        l_lat = gcj02lat - gcj02latEst
        d_latwgs = (l_lon * dlatgcj_dlonwgs - l_lat * dlongcj_dlonwgs) / \
            (dlongcj_dlatwgs * dlatgcj_dlonwgs - dlatgcj_dlatwgs * dlongcj_dlonwgs)
        d_lonwgs = (l_lon - dlongcj_dlatwgs * d_latwgs) / dlongcj_dlonwgs

        if (fabs(d_latwgs) < tol and fabs(d_lonwgs) < tol):
            break
        wgs84lon = wgs84lon + d_lonwgs
        wgs84lat = wgs84lat + d_latwgs
    return wgs84lon, wgs84lat

# /**
#  *  \brief Covert geodetic coordinate in GCJ-02 coordinate system to geodetic coordinate
#  *         in WGS84 coordinate system
#  *
#  *  \param [in] gcj02lon: longitude in GCJ-02 coordinate system [unit:degree]
#  *  \param [in] gcj02lat: latitude in GCJ-02 coordinate system [unit:degree]
#  *  \return Returns geodetic coordinate in WGS84 coordinate system
#  *  \remark The encryption formula is known,and use the analytical derivation method to
#  *			solve the problem with high precision.
#  *	\detail Assuming the encryption formula is
#  *
#  *			gcj02lon = Wgs2Gcj(wgs84lon, wgs84lat)
#  *			gcj02lat = Wgs2Gcj(wgs84lon, wgs84lat)
#  *
#  *	 In the rectification process, (wgs84lon, wgs84lat) are unknown items. Obviously,
#  *   this is a system of nonlinear equations.
#  *
#  *   The linear formed error functions of forward intersection come from
#  *   consideration of a Taylor series expansion.
#  *           V = AX - b
#  *    here:
#  *    V: The residuals of the observed values
#  *    A: The jacobian matrix
#  *    X: The modification of the unknown items
#  *    b: The constant terms of the error functions
#  *
#  *    Then the error functions written in vector form are:
#  *    | V_lon | = | dlongcj_dlonwgs  dlongcj_dlatwgs |  | d_lonwgs | - | l_lon |
#  *    | V_lat | = | dlatgcj_dlonwgs  dlatgcj_dlatwgs |  | d_latwgs | - | l_lat |
#  *    here:
#  *    l_lon = longcj - longcj'                 // the modification of longcj
#  *    l_lat = latgcj - latgcj'                 // the modification of latgcj
#  *    longcj : the observed longitude in GCJ-02
#  *    latgcj : the observed latitude in GCJ-02
#  *    longcj' = Wgs2Gcj(wgs84lon',wgs84lat')    // estimated longitude in GCJ-02
#  *    latgcj' = Wgs2Gcj(wgs84lon',wgs84lat')    // estimated latitude in GCJ-02
#  *    wgs84lon' : estimated longitude in WGS84
#  *    wgs84lat' : estimated latitude in WGS84
#  *    d_lonwgs : unknown items
#  *    d_latwgs : unknown items
#  *    wgs84lon = wgs84lon' + d_lonwgs                           // update
#  *    wgs84lat = wgs84lat' + d_latwgs
#  *
#  *	  let V = [V_lon V_lat]T = 0, then
#  *	  d_latwgs = (l_lon * dlatgcj_dlonwgs - l_lat * dlongcj_dlonwgs) /
#  *			(dlongcj_dlatwgs * dlatgcj_dlonwgs - dlatgcj_dlatwgs * dlongcj_dlonwgs)
#  *	  d_lonwgs = (l_lon - dlongcj_dlatwgs * d_latwgs) / dlongcj_dlonwgs
#  *
#  *    This iterative procedure is repeated until X= [d_lonwgs d_latwgs]T are
#  *    sufficiently small.
#  *  \time 01:54:46 2020/06/13
#  */


def Gcj2Wgs_AnalyticDiff(gcj02lon, gcj02lat):
    wgs84lon = gcj02lon
    wgs84lat = gcj02lat
    for _ in range(1000):
        # get geodetic offset relative to 'center china'
        lon0 = wgs84lon - 105.0
        lat0 = wgs84lat - 35.0

        # generate an pair offset roughly in meters
        lon1 = 300.0 + lon0 + 2.0 * lat0 + 0.1 * lon0 * \
            lon0 + 0.1 * lon0 * lat0 + 0.1 * sqrt(fabs(lon0))
        lon1 = lon1 + (20.0 * sin(6.0 * lon0 * PI) + 20.0 *
                       sin(2.0 * lon0 * PI)) * 2.0 / 3.0
        lon1 = lon1 + (20.0 * sin(lon0 * PI) + 40.0 *
                       sin(lon0 / 3.0 * PI)) * 2.0 / 3.0
        lon1 = lon1 + (150.0 * sin(lon0 / 12.0 * PI) + 300.0 *
                       sin(lon0 * PI / 30.0)) * 2.0 / 3.0
        lat1 = -100.0 + 2.0 * lon0 + 3.0 * lat0 + 0.2 * lat0 * \
            lat0 + 0.1 * lon0 * lat0 + 0.2 * sqrt(fabs(lon0))
        lat1 = lat1 + (20.0 * sin(6.0 * lon0 * PI) + 20.0 *
                       sin(2.0 * lon0 * PI)) * 2.0 / 3.0
        lat1 = lat1 + (20.0 * sin(lat0 * PI) + 40.0 *
                       sin(lat0 / 3.0 * PI)) * 2.0 / 3.0
        lat1 = lat1 + (160.0 * sin(lat0 / 12.0 * PI) + 320.0 *
                       sin(lat0 * PI / 30.0)) * 2.0 / 3.0

        g_lon0 = 0
        if (lon0 > 0):
            g_lon0 = 0.05 / sqrt(lon0)
        else:
            if (lon0 < 0):
                g_lon0 = -0.05 / sqrt(-lon0)
            else:
                g_lon0 = 0

        PIlon0 = PI * lon0
        PIlat0 = PI * lat0
        dlon1_dlonwgs = 1 + 0.2 * lon0 + 0.1 * lat0 + g_lon0 \
            + ((120 * PI * cos(6 * PIlon0) + 40 * PI * cos(2 * PIlon0))
            + (20 * PI * cos(PIlon0) + 40 * PI / 3.0 * cos(PIlon0 / 3.0))
                + (12.5 * PI * cos(PIlon0 / 12.0) + 10 * PI * cos(PIlon0 / 30.0))) * 2.0 / 3.0
        dlon1_dlatwgs = 2 + 0.1 * lon0

        dlat1_dlonwgs = 2 + 0.1 * lat0 + 2 * g_lon0 \
            + (120 * PI * cos(6 * PIlon0) + 40 * PI * cos(2 * PIlon0)) * 2.0 / 3.0
        dlat1_dlatwgs = 3 + 0.4 * lat0 + 0.1 * lon0 \
            + ((20 * PI * cos(PIlat0) + 40.0 * PI / 3.0 * cos(PIlat0 / 3.0))
            + (40 * PI / 3.0 * cos(PIlat0 / 12.0) + 32.0 * PI / 3.0 * cos(PIlat0 / 30.0))) * 2.0 / 3.0

        # latitude in radian
        B = Deg2Rad(wgs84lat)
        sinB = sin(B)
        cosB = cos(B)
        WSQ = 1 - kKRASOVSKY_ECCSQ * sinB * sinB
        W = sqrt(WSQ)
        N = kKRASOVSKY_A / W

        dW_dlatwgs = -PI * kKRASOVSKY_ECCSQ * sinB * cosB / (180.0 * W)
        dN_dlatwgs = -kKRASOVSKY_A * dW_dlatwgs / WSQ

        PIxNxCosB = PI * N * cosB
        dlongcj_dlonwgs = 1.0 + 180.0 * dlon1_dlonwgs / PIxNxCosB
        dlongcj_dlatwgs = 180 * dlon1_dlatwgs / PIxNxCosB - \
            180 * lon1 * PI * (dN_dlatwgs * cosB - PI * N *
                            sinB / 180.0) / (PIxNxCosB * PIxNxCosB)

        PIxNxSubECCSQ = PI * N * (1 - kKRASOVSKY_ECCSQ)
        dlatgcj_dlonwgs = 180 * WSQ * dlat1_dlonwgs / PIxNxSubECCSQ
        dlatgcj_dlatwgs = 1.0 + 180 * (N * (dlat1_dlatwgs * WSQ + 2.0 * lat1 * W * dW_dlatwgs) - lat1 * WSQ * dN_dlatwgs) / \
            (N * PIxNxSubECCSQ)

        gcj02lonEst, gcj02latEst = Wgs2Gcj(wgs84lon, wgs84lat)
        l_lon = gcj02lon - gcj02lonEst
        l_lat = gcj02lat - gcj02latEst

        d_latwgs = (l_lon * dlatgcj_dlonwgs - l_lat * dlongcj_dlonwgs) / \
            (dlongcj_dlatwgs * dlatgcj_dlonwgs - dlatgcj_dlatwgs * dlongcj_dlonwgs)
        d_lonwgs = (l_lon - dlongcj_dlatwgs * d_latwgs) / dlongcj_dlonwgs

        if (fabs(d_latwgs) < 1.0e-9 and fabs(d_lonwgs) < 1.0e-9):
            break
        wgs84lon = wgs84lon + d_lonwgs
        wgs84lat = wgs84lat + d_latwgs
    return wgs84lon, wgs84lat


if __name__ == '__main__':
    # wgs2gcj
    # coord = (112, 40)
    # trans = WGS2GCJ()
    print(Wgs2Gcj(120.13969, 30.28846))
    print(Gcj2Wgs_SimpleIteration(120.144724, 30.286281))
    print(Gcj2Wgs_NumbericDiff(120.144724, 30.286281))
    print(Gcj2Wgs_AnalyticDiff(120.144724, 30.286281))

    # gcj2wgs
