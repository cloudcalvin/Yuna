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
Point(1) = {5000000.0*ws, 21400000.0*ws, t2, lc1}; 
Point(2) = {5000000.0*ws, 18600000.0*ws, t2, lc1}; 
Point(3) = {35000000.0*ws, 18600000.0*ws, t2, lc1}; 
Point(4) = {35000000.0*ws, 21400000.0*ws, t2, lc1}; 
Point(5) = {9000000.0*ws, 21350000.0*ws, t2, lc1}; 
Point(6) = {11200000.0*ws, 21350000.0*ws, t2, lc1}; 
Point(7) = {11200000.0*ws, 25590000.0*ws, t2, lc1}; 
Point(8) = {9000000.0*ws, 25590000.0*ws, t2, lc1}; 
Point(9) = {28800000.0*ws, 21350000.0*ws, t2, lc1}; 
Point(10) = {31000000.0*ws, 21350000.0*ws, t2, lc1}; 
Point(11) = {31000000.0*ws, 25600000.0*ws, t2, lc1}; 
Point(12) = {28800000.0*ws, 25600000.0*ws, t2, lc1}; 

// Structure Lines 
Line(1) = {1,2}; 
Line(2) = {2,3}; 
Line(3) = {3,4}; 
Line(4) = {4,1}; 
Line(5) = {5,6}; 
Line(6) = {6,7}; 
Line(7) = {7,8}; 
Line(8) = {8,5}; 
Line(9) = {9,10}; 
Line(10) = {10,11}; 
Line(11) = {11,12}; 
Line(12) = {12,9}; 

// Structure Loop 
Line Loop(1) = {1,2,3,4}; 
Line Loop(2) = {5,6,7,8}; 
Line Loop(3) = {9,10,11,12}; 

// Plane Surface 
Plane Surface(1) = {1}; 
Plane Surface(2) = {2}; 
Plane Surface(3) = {3}; 

// Physical Surface 
Physical Surface(1) = {1}; 
Physical Surface(2) = {2}; 
Physical Surface(3) = {3}; 

// Extrude 
info1[] = Extrude {0,0,t2} {Surface{1}; Layers{{layers1},{1}};}; 
info2[] = Extrude {0,0,t2} {Surface{2}; Layers{{layers1},{1}};}; 
info3[] = Extrude {0,0,t2} {Surface{3}; Layers{{layers1},{1}};}; 
Mesh.Algorithm = 1; 
Mesh.CharacteristicLengthMin = 100; 
