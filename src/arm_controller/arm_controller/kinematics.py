import numpy as np

BASE_H = 0.071
L1     = 0.10
L2     = 0.128
L_end  = 0.18   # L3 + L_EE combined


def fk_from_servos(s1, s2, s3, s4):
    """
    FK directly from servo positions (degrees, 0-180).
    s1=base, s2=shoulder, s3=elbow, s4=wrist
    Returns (x, y, z) in metres.
    
    Convention: servo 90 = neutral/horizontal, 0 = -90deg, 180 = +90deg
    """
    t1 = np.radians(s1 - 90)  # base rotation
    t2 = np.radians(s2 - 90)  # shoulder absolute angle
    t3 = np.radians(s3 - 90)  # elbow relative to shoulder
    t4 = np.radians(s4 - 90)  # wrist relative to elbow

    a2 = t2
    a3 = t2 + t3
    a4 = t2 + t3 + t4

    r = (L1    * np.cos(a2) +
         L2    * np.cos(a3) +
         L_end * np.cos(a4))

    z = BASE_H + (L1    * np.sin(a2) +
                  L2    * np.sin(a3) +
                  L_end * np.sin(a4))

    x = r * np.cos(t1)
    y = r * np.sin(t1)
    return float(x), float(y), float(z)


def forward_kinematics(s1, s2, s3, s4):
    """Alias for fk_from_servos — use this in the action server."""
    return fk_from_servos(s1, s2, s3, s4)


def inverse_kinematics(x_t, y_t, z_t, step=5):
    """
    Brute-force IK in servo space.
    Scans all servo combinations, returns the one closest to target.
    
    Returns (s1, s2, s3, s4) as integer servo degrees, or None if
    best solution is more than 20mm away (target unreachable).
    """
    # Base servo is just the horizontal angle to target
    s1 = int(np.degrees(np.arctan2(y_t, x_t)) + 90)
    s1 = max(0, min(180, s1))

    best_servos = None
    best_dist   = float('inf')

    for s2 in range(0, 181, step):
        for s3 in range(0, 181, step):
            for s4 in range(0, 181, step):
                x, y, z = fk_from_servos(s1, s2, s3, s4)
                dist = np.sqrt((x - x_t)**2 +
                               (y - y_t)**2 +
                               (z - z_t)**2)
                if dist < best_dist:
                    best_dist   = dist
                    best_servos = (s1, s2, s3, s4)

    if best_dist > 0.020:   # 20mm threshold — unreachable
        return None

    return best_servos      # tuple of ints, ready for serial_bridge