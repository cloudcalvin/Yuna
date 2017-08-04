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
Point(1) = {6500000*ws, 21350000*ws, t2, lc1}; 
Point(2) = {5000000*ws, 21350000*ws, t2, lc1}; 
Point(3) = {5000000*ws, 18650000*ws, t2, lc1}; 
Point(4) = {6500000*ws, 18650000*ws, t2, lc1}; 
Point(5) = {35000000*ws, 21350000*ws, t2, lc1}; 
Point(6) = {33500000*ws, 21350000*ws, t2, lc1}; 
Point(7) = {33500000*ws, 18650000*ws, t2, lc1}; 
Point(8) = {35000000*ws, 18650000*ws, t2, lc1}; 

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
Plane Surface(1) = {1}; 
Plane Surface(2) = {2}; 

// Physical Surface 
Physical Surface("via1") = {1}; 
Physical Surface("via2") = {2}; 

// Extrude 
info1[] = Extrude {0,0,t2} {Surface{1}; Layers{{layers1},{1}};}; 
info2[] = Extrude {0,0,t2} {Surface{2}; Layers{{layers1},{1}};}; 
info3[] = Extrude {0,0,t2} {Surface{3}; Layers{{layers1},{1}};}; 
info4[] = Extrude {0,0,t2} {Surface{4}; Layers{{layers1},{1}};}; 
info5[] = Extrude {0,0,t2} {Surface{5}; Layers{{layers1},{1}};}; 
info6[] = Extrude {0,0,t2} {Surface{6}; Layers{{layers1},{1}};}; 
info7[] = Extrude {0,0,t2} {Surface{7}; Layers{{layers1},{1}};}; 
info8[] = Extrude {0,0,t2} {Surface{8}; Layers{{layers1},{1}};}; 
info9[] = Extrude {0,0,t2} {Surface{9}; Layers{{layers1},{1}};}; 
info10[] = Extrude {0,0,t2} {Surface{10}; Layers{{layers1},{1}};}; 
info11[] = Extrude {0,0,t2} {Surface{11}; Layers{{layers1},{1}};}; 
info12[] = Extrude {0,0,t2} {Surface{12}; Layers{{layers1},{1}};}; 
info13[] = Extrude {0,0,t2} {Surface{13}; Layers{{layers1},{1}};}; 
info14[] = Extrude {0,0,t2} {Surface{14}; Layers{{layers1},{1}};}; 
Mesh.Algorithm = 1; 
Mesh.CharacteristicLengthMin = 100; 
