/********************************************** 
 * 
 * Gmsh rectangle volume 
 * 
 **********************************************/ 

// Discretization size 
lc1 = 0.1e-4; 

// Ground 
t2 = 350E-9; 
layers1 = 1; 

// units 
ws = 1E-6; 

// Structure 
Point(1) = {26*ws, 0*ws, t2, lc1}; 
Point(2) = {0*ws, 0*ws, t2, lc1}; 
Point(3) = {0*ws, -20*ws, t2, lc1}; 
Point(4) = {26*ws, -20*ws, t2, lc1}; 

// Holes 
Point(5) = {6*ws, -4*ws, t2, lc1}; 
Point(6) = {21.5*ws, -4*ws, t2, lc1}; 
Point(7) = {21.5*ws, -15.5*ws, t2, lc1}; 
Point(8) = {6*ws, -15.5*ws, t2, lc1}; 

// Structure Lines 
Line(1) = {1,2}; 
Line(2) = {2,3}; 
Line(3) = {3,4}; 
Line(4) = {4,1}; 
Line(5) = {5,6}; 
Line(6) = {6,7}; 
Line(7) = {7,8}; 
Line(8) = {8,5}; 

// Structure Loop 
Line Loop(1) = {1,2,3,4}; 
Line Loop(2) = {5,6,7,8}; 

// Plane Surface 
Plane Surface(3) = {1,2}; 
Plane Surface(4) = {2};  

// Extrude 
info1[] = Extrude {0,0,0} {Surface{3}; Layers{{layers1},{1}};}; 
info2[] = Extrude {0,0,0} {Surface{4}; Layers{{layers1},{1}};}; 

// Frequencies (-s = start, -e = end, -n = steps):
Physical Point(".f -s 10E9 -e 10E9 -n 1") = {};

// Volume conductivity (-s) and penetration depth (-l):
Physical Volume(".v1 -s 0.0 -l 270E-9") = {info1[1]};

Physical Point(".h 0") = {};
Physical Surface(".t -p 0") = {info2[2],info2[3],info2[4],info2[5]};

Mesh.Algorithm = 1; 
Mesh.CharacteristicLengthMin = 100; 
