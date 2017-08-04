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
Point(1) = {18800000*ws, -18000000*ws, t2, lc1}; 
Point(2) = {14700000*ws, -18000000*ws, t2, lc1}; 
Point(3) = {14700000*ws, -31780000*ws, t2, lc1}; 
Point(4) = {18800000*ws, -31780000*ws, t2, lc1}; 
Point(5) = {24245000*ws, -27525000*ws, t2, lc1}; 
Point(6) = {19805000*ws, -27525000*ws, t2, lc1}; 
Point(7) = {19805000*ws, -31965000*ws, t2, lc1}; 
Point(8) = {24245000*ws, -31965000*ws, t2, lc1}; 
Point(9) = {28000000*ws, -38360000*ws, t2, lc1}; 
Point(10) = {24080000*ws, -38360000*ws, t2, lc1}; 
Point(11) = {24080000*ws, -42280000*ws, t2, lc1}; 
Point(12) = {28000000*ws, -42280000*ws, t2, lc1}; 
Point(13) = {11100000*ws, -58400000*ws, t2, lc1}; 
Point(14) = {7400000*ws, -58400000*ws, t2, lc1}; 
Point(15) = {7400000*ws, -62100000*ws, t2, lc1}; 
Point(16) = {11100000*ws, -62100000*ws, t2, lc1}; 

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
Line(13) = {13,14}; 
Line(14) = {14,15}; 
Line(15) = {15,16}; 
Line(16) = {16,13}; 

// Structure Loop 
Line Loop(1) = {1,2,3,4}; 
Line Loop(2) = {5,6,7,8}; 
Line Loop(3) = {9,10,11,12}; 
Line Loop(4) = {13,14,15,16}; 

// Plane Surface 
Plane Surface(1) = {1}; 
Plane Surface(2) = {2}; 
Plane Surface(3) = {3}; 
Plane Surface(4) = {4}; 

// Physical Surface 
Physical Surface("via1") = {1}; 
Physical Surface("via2") = {2}; 
Physical Surface("via3") = {3}; 
Physical Surface("via4") = {4}; 

// Extrude 
info1[] = Extrude {0,0,t2} {Surface{1}; Layers{{layers1},{1}};}; 
info2[] = Extrude {0,0,t2} {Surface{2}; Layers{{layers1},{1}};}; 
info3[] = Extrude {0,0,t2} {Surface{3}; Layers{{layers1},{1}};}; 
info4[] = Extrude {0,0,t2} {Surface{4}; Layers{{layers1},{1}};}; 
Mesh.Algorithm = 1; 
Mesh.CharacteristicLengthMin = 100; 
