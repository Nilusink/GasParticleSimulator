"""
physics_calculations.py
3. June 2024

Thermodynamics for the simulator

Author:
Nilusink
"""
import typing as tp
import math as m


if tp.TYPE_CHECKING:
    from particles import Particle


def separate_particles(
        particles: list["Particle"]
) -> tuple[list["Particle"], list["Particle"]]:
    """
    separate particles by mass
    """
    p1s = []
    p2s = []

    # split particles based on mass
    for particle in particles:
        # whatever mass the first particle has is sorted into p1s
        if len(p1s) == 0:
            p1s.append(particle)
            continue

        if particle.mass == p1s[0].mass:
            p1s.append(particle)

        else:
            p2s.append(particle)

    return p1s, p2s


# def pressure_from_particles(
#         particles: list["Particle"],
#         volume: float
# ) -> float:
#     r"""
#     calculate the pressure based off the particles
#
#     $$
#     P = { N \over 3V } * m * \langle v^2 \rangle \newline \ \newline
#     P: \text {Gas pressure} \newline
#     N: \text {Number of molecules} \newline
#     V: \text {Volume} \newline
#     m: \text {mass of a single molecule} \newline
#     \langle v^2 \rangle: \text {mean square velocity} \newline
#     $$
#
#     since we have two different types of molecules, we calculate two pressures
#     and add them together
#
#     :returns: pressure in Pascal
#     """
#     if not particles:
#         return 0
#
#     p1s, p2s = separate_particles(particles)
#
#     # mean square velocities
#     ms1 = sum([p.velocity.length**2 for p in p1s]) / len(p1s) if p1s else 0
#     ms2 = sum([p.velocity.length**2 for p in p2s]) / len(p2s) if p2s else 0
#
#     print(ms1, ms2)
#
#     # pressures
#     p1 = (len(p1s) / 3*volume) * p1s[0].mass * ms1 if p1s else 0
#     p2 = (len(p2s) / 3*volume) * p2s[0].mass * ms2 if p2s else 0
#
#     # add up pressures
#     return p1 + p2
#
#
# def volume_from_pressure(particles: list["Particle"], pressure: float) -> float:
#     r"""
#     calculates the required volume of a space for a certain pressure and
#     particle set
#
#     similar to `pressure_from_particles`
#     """
#     print("recalculating")
#     if not particles:
#         return 0
#
#     p1s, p2s = separate_particles(particles)
#
#     # mean square velocities
#     ms1 = sum([p.velocity.length**2 for p in p1s]) / len(p1s) if p1s else 0
#     ms2 = sum([p.velocity.length**2 for p in p2s]) / len(p2s) if p2s else 0
#
#     print(ms1, ms2)
#
#     volume = 1
#     if p1s:
#         volume *= len(p1s) * p1s[0].mass * ms1
#
#     if p2s:
#         volume *= len(p2s) * p2s[0].mass * ms2
#
#     volume /= 3*pressure
#
#     print(f"{volume=}")
#     return volume

def pressure_from_particles(particles: list["Particle"], volume: float) -> float:
    r"""
    calculate the pressure based off the particles

    $$
    P = { N \over 3V } * m * \langle v^2 \rangle \newline \ \newline
    P: \text {Gas pressure} \newline
    N: \text {Number of molecules} \newline
    V: \text {Volume} \newline
    m: \text {mass of a single molecule} \newline
    \langle v^2 \rangle: \text {mean square velocity} \newline
    $$

    since we have two different types of molecules, we calculate two pressures
    and add them together

    :returns: pressure in Pascal
    """
    if not particles:
        return 0

    p1s, p2s = separate_particles(particles)

    # mean square velocities
    ms1 = sum([p.velocity.length**2 for p in p1s]) / len(p1s) if p1s else 0
    ms2 = sum([p.velocity.length**2 for p in p2s]) / len(p2s) if p2s else 0

    # pressures
    p1 = (len(p1s) / (3 * volume)) * p1s[0].mass * ms1 if p1s else 0
    p2 = (len(p2s) / (3 * volume)) * p2s[0].mass * ms2 if p2s else 0

    # add up pressures
    return p1 + p2


def volume_from_pressure(particles: list["Particle"], pressure: float) -> float:
    """
    calculates the required volume of a space for a certain pressure and
    particle set

    similar to `pressure_from_particles`, but solved for V:

    $$
    P = P_1 + P_2 = { N_1 \over V } * m_1 * \langle v^2 \rangle_1 +
    { N_2 \over V } * m_2 * \langle v^2 \rangle_2 \newline \ \newline
    P*V = N_1 * m_1 * \langle v^2 \rangle_1 + N_2 * m_2 *
    \langle v^2 \rangle_2 \newline \ \newline
    V = { N_1 * m_1 * \langle v^2 \rangle_1 + N_2 * m_2 *
    \langle v^2 \rangle_2 \over P }
    $$

    :returns: volume in m^2
    """
    if not particles:
        return 0

    p1s, p2s = separate_particles(particles)

    # mean square velocities
    ms1 = sum([p.velocity.length**2 for p in p1s]) / len(p1s) if p1s else 0
    ms2 = sum([p.velocity.length**2 for p in p2s]) / len(p2s) if p2s else 0

    N1 = len(p1s)
    N2 = len(p2s)
    m1 = p1s[0].mass if p1s else 0
    m2 = p2s[0].mass if p2s else 0

    # Calculate volume
    volume = (N1 * m1 * ms1 + N2 * m2 * ms2) / (3 * pressure)

    return volume


def calculate_temperature(particles: list["Particle"], volume: float, pressure: float) -> float:
    """
    Calculate the temperature based on the volume, pressure, and number of particles.
    """
    if not particles:
        return 0

    N_total = len(particles)
    Avogadro_constant = 6.022e23  # Avogadro's number in particles/mol
    gas_constant = 8.314  # Ideal gas constant in J/(mol·K)

    # Calculate temperature
    temperature = (pressure * volume * Avogadro_constant) / (N_total * gas_constant)

    return temperature
