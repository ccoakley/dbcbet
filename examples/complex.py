"""Complex number example.

This was ported from a JML example illustrating design by
contract. The code is redundant in places, which should not be typical
use. For example, if the specification for a method (postcondition)
looks like the implementation, it shouldn't actually be used. Throw
that postcondition away, as there's no justification for redundant code.
"""


from dbcbet.dbcbet import dbc, pre, post, inv, bet, finitize, finitize_method, throws
from dbcbet.helpers import argument_types
import math
from numbers import Number
#
# Complex number example for design by contract with bounded exhaustive testing
#

# helper alternate
#def approx_equal(a, b, tol):
#    return (abs(a-b) / max(abs(a), abs(b))) < tol
tolerance = 0.005
    
def approx_equal(a, b, tol):
    if a + b == 0:
        return a == b
    return (abs(a-b) / (abs(a)+abs(b))/2) < tol

def real_part_post(self, old, ret):
    return approx_equal(self._magnitude()*math.cos(self._angle()), ret, tolerance)

def imaginary_part_post(self, old, ret):
    return approx_equal(self._magnitude()*math.sin(self._angle()), ret, tolerance)    

def magnitude_post(self, old, ret):
    return approx_equal(math.sqrt(self._real_part()*self._real_part() + self._imaginary_part()*self._imaginary_part()), ret, tolerance)

def angle_post(self, old, ret):
    return approx_equal(math.atan2(self._imaginary_part(), self._real_part()), ret, tolerance)

def arg_not_none(self, b):
    return b is not None

def add_post1(self, old, ret, b):
    return ret is not None

def add_post2(self, old, ret, b):
    return approx_equal(self._real_part() + b._real_part(), ret._real_part(), tolerance)

def add_post3(self, old, ret, b):
    return approx_equal(self._imaginary_part() + b._imaginary_part(), ret._imaginary_part(), tolerance)

def sub_post(self, old, ret, b):
    return ret is not None and approx_equal(self._real_part() - b._real_part(), ret._real_part(), tolerance) and approx_equal(self._imaginary_part() - b._imaginary_part(), ret._imaginary_part(), tolerance)

def mul_post(self, old, ret, b):
    if math.isnan(self._magnitude() * b._magnitude()) or math.isnan(self._angle()) or math.isnan(b._angle()):
        return math.isnan(ret._real_part()) and ret._imaginary_part() == 0.0
    else:
        return (ret is not None 
                and approx_equal(self._magnitude() * b._magnitude(), ret._magnitude(), tolerance) 
                and approx_equal(standardize_angle(self._angle() + b._angle()), ret._angle(), tolerance))

def div_post(self, old, ret, b):
    if math.isnan(self._magnitude() / b._magnitude()) or math.isnan(self._angle()) or math.isnan(b._angle()):
        return math.isnan(ret._real_part()) and ret._imaginary_part() == 0.0
    else:
        return ret is not None and approx_equal(self._magnitude() / b._magnitude(), ret._magnitude(), tolerance) and approx_equal(standardize_angle(self._angle() - b._angle()), ret._angle(), tolerance)
    
def eq_post(self, old, ret, b):
    return ret == isinstance(b, Complex) and self._real_part() == b._real_part() and self._imaginary_part() == b._imaginary_part() and self._magnitude() == b._magnitude() and self._angle() == b._angle()

rectangular_list = []

def polar_invariant(self):
    return True

def rectangular_invariant(self):
    return True

def finitize_polar():
    return {'mag':[-1,0,1],'ang':[-math.pi,0,math.pi/4.0,math.pi/2.0]}

def finitize_rectangular():
    return {'re':xrange(-2,80),'img':[-1,0,1]}

def standardize_angle(rad):
    if math.isnan(rad) or math.isinf(rad):
        raise ValueError()
    rad = math.fmod(rad, 2*math.pi)
    if rad > math.pi:
        return rad - 2*math.pi
    elif rad < -math.pi:
        return rad + 2*math.pi
    else:
        return rad

@dbc
class Complex(object):
    @post(real_part_post)
    def real_part(self):
        pass

    @post(imaginary_part_post)
    def imaginary_part(self):
        pass

    @post(magnitude_post)
    def magnitude(self):
        pass

    @post(angle_post)
    def angle(self):
        pass

@dbc
class ComplexOps(Complex):
    @pre(argument_types(Complex))
    @post(add_post1)
    @post(add_post2)
    @post(add_post3)
    @finitize_method(rectangular_list)
    def add(self, b):
        return Rectangular(self.real_part() + b.real_part(), self.imaginary_part() + b.imaginary_part())

    @post(sub_post)
    def sub(self, b):
        return Rectangular(self.real_part() - b.real_part(), self.imaginary_part() - b.imaginary_part())

    @post(mul_post)
    def mul(self, b):
        try:
            return Polar(self.magnitude() * b.magnitude(), self.angle() + b.angle())
        except ValueError:
            return Rectangular(float('nan'))

    @post(div_post)
    def div(self, b):
        try:
            return Polar(self.magnitude() / b.magnitude(), self.angle() - b.angle())
        except ValueError:
            return Rectangular(float('nan'))

    @post(eq_post)
    def __eq__(self, other):
        if not isinstance(other, Complex):
            return False
        return self.realPart() == other.realPart and self.imaginaryPart() == other.imaginaryPart()

    def __hash__(self):
        return self.realPart() + self.imaginaryPart()

@inv(polar_invariant)
@finitize(finitize_polar)
class Polar(ComplexOps):
    @pre(argument_types(Number, Number))
    @finitize_method([-1,0,1],[-math.pi,0,math.pi/4.0,math.pi/2.0])
    @throws(ValueError)
    def __init__(self, mag, angle):
        if math.isnan(mag):
            raise ValueError()
        if mag < 0:
            mag = -mag;
            angle += math.pi;
        self.mag = mag;
        self.ang = standardize_angle(angle)
        

    @throws(ValueError)
    def standardize_angle(self, rad):
        if math.isnan(rad) or math.isinf(rad):
            raise ValueError()
        rad = math.fmod(rad, 2*math.pi)
        if rad > math.pi:
            return rad - 2*math.pi
        elif rad < -math.pi:
            return rad + 2*math.pi
        else:
            return rad

    def _real_part(self):
        return self.mag * math.cos(self.ang)

    # specification inherited
    real_part = _real_part
        
    def _imaginary_part(self): 
        return self.mag * math.sin(self.ang)

    # specification inherited
    imaginary_part = _imaginary_part
    
    def _magnitude(self):
        return self.mag

    # specification inherited
    magnitude = _magnitude
    
    # specification inherited
    def _angle(self):
        return self.ang

    # specification inherited
    angle = _angle
    
    # specification inherited
    def __str__(self):
        return "(" + self.mag + ", " + self.ang + ")"

@inv(rectangular_invariant)
@finitize(finitize_rectangular)
class Rectangular(ComplexOps):
    @pre(argument_types(Number, Number))
    @finitize_method([None,-1,0,1],[None,-1,0,1])
    def __init__(self, re=None, img=None):
        if re is None:
            self.re = 0.0
        else:
            self.re = re
        if img is None:
            self.img = 0.0
        else:
            self.img = img
        if math.isnan(self.re):
            self.img = 0.0
            
    def _real_part(self):
        return self.re

    # specification inherited
    real_part = _real_part
    
    def _imaginary_part(self):
        return self.img;

    # specification inherited
    imaginary_part = _imaginary_part

    def _magnitude(self):
        return math.sqrt(self.re*self.re + self.img*self.img);

    # specification inherited
    magnitude = _magnitude

    def _angle(self):
        return math.atan2(self.img, self.re)

    # specification inherited
    angle = _angle
 
    # specification inherited
    def __str__(self):
        return  str(self.re) + " + " + str(self.img) + "*i";    

def test_complex():
    rectangular_list.append(Rectangular(0,1))
    rectangular_list.append(Rectangular(1,0))
    rectangular_list.append(Rectangular(1,1))
    bet(Polar).run()
    bet(Rectangular).run()

# this is how python does main, just so you can see the stuff in action
if __name__ == "__main__":
    test_complex()
