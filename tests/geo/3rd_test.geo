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
Point(1) = {-17*ws, 7*ws, t2, lc1}; 
Point(2) = {-20*ws, 7*ws, t2, lc1}; 
Point(3) = {-20*ws, 25*ws, t2, lc1}; 
Point(4) = {-25*ws, 25*ws, t2, lc1}; 
Point(5) = {-25*ws, 2*ws, t2, lc1}; 
Point(6) = {-17*ws, 2*ws, t2, lc1}; 
Point(7) = {17*ws, 25*ws, t2, lc1}; 
Point(8) = {12*ws, 25*ws, t2, lc1}; 
Point(9) = {12*ws, 7*ws, t2, lc1}; 
Point(10) = {9*ws, 7*ws, t2, lc1}; 
Point(11) = {9*ws, 2*ws, t2, lc1}; 
Point(12) = {17*ws, 2*ws, t2, lc1}; 
Point(13) = {9*ws, 7*ws, t2, lc1}; 
Point(14) = {-17*ws, 7*ws, t2, lc1}; 
Point(15) = {-17*ws, 2*ws, t2, lc1}; 
Point(16) = {9*ws, 2*ws, t2, lc1}; 

// Structure Lines 
Line(1) = {1,2}; 
Line(2) = {2,3}; 
Line(3) = {3,4}; 
Line(4) = {4,5}; 
Line(5) = {5,6}; 
Line(6) = {6,1}; 
Line(7) = {7,8}; 
Line(8) = {8,9}; 
Line(9) = {9,10}; 
Line(10) = {10,11}; 
Line(11) = {11,12}; 
Line(12) = {12,7}; 
Line(13) = {13,14}; 
Line(14) = {14,15}; 
Line(15) = {15,16}; 
Line(16) = {16,13}; 

// Structure Loop 
Line Loop(1) = {1,2,3,4,5,6}; 
Line Loop(2) = {7,8,9,10,11,12}; 
Line Loop(3) = {13,14,15,16}; 

// Plane Surface 
Plane Surface(1) = {1}; 
Plane Surface(2) = {2}; 
Plane Surface(3) = {3}; 

// Physical Surface 
Physical Surface(1) = {1}; 
Physical Surface(2) = {2}; 
Physical Surface("moat") = {3}; 

// Extrude 
info1[] = Extrude {0,0,t2} {Surface{1}; Layers{{layers1},{1}};}; 
info2[] = Extrude {0,0,t2} {Surface{2}; Layers{{layers1},{1}};}; 
info3[] = Extrude {0,0,t2} {Surface{3}; Layers{{layers1},{1}};}; 
