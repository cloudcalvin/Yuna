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
Point(1) = {280*ws, -130*ws, t2, lc1}; 
Point(2) = {230*ws, -130*ws, t2, lc1}; 
Point(3) = {230*ws, -180*ws, t2, lc1}; 
Point(4) = {280*ws, -180*ws, t2, lc1}; 
Point(5) = {50*ws, -130*ws, t2, lc1}; 
Point(6) = {0*ws, -130*ws, t2, lc1}; 
Point(7) = {0*ws, -180*ws, t2, lc1}; 
Point(8) = {50*ws, -180*ws, t2, lc1}; 
Point(9) = {280*ws, 20*ws, t2, lc1}; 
Point(10) = {170*ws, 20*ws, t2, lc1}; 
Point(11) = {170*ws, 170*ws, t2, lc1}; 
Point(12) = {110*ws, 170*ws, t2, lc1}; 
Point(13) = {110*ws, 20*ws, t2, lc1}; 
Point(14) = {50*ws, 20*ws, t2, lc1}; 
Point(15) = {50*ws, 30*ws, t2, lc1}; 
Point(16) = {0*ws, 30*ws, t2, lc1}; 
Point(17) = {0*ws, -130*ws, t2, lc1}; 
Point(18) = {50*ws, -130*ws, t2, lc1}; 
Point(19) = {50*ws, -30*ws, t2, lc1}; 
Point(20) = {230*ws, -30*ws, t2, lc1}; 
Point(21) = {230*ws, -130*ws, t2, lc1}; 
Point(22) = {280*ws, -130*ws, t2, lc1}; 
Point(23) = {170*ws, -330*ws, t2, lc1}; 
Point(24) = {280*ws, -330*ws, t2, lc1}; 
Point(25) = {280*ws, -180*ws, t2, lc1}; 
Point(26) = {230*ws, -180*ws, t2, lc1}; 
Point(27) = {230*ws, -280*ws, t2, lc1}; 
Point(28) = {50*ws, -280*ws, t2, lc1}; 
Point(29) = {50*ws, -180*ws, t2, lc1}; 
Point(30) = {0*ws, -180*ws, t2, lc1}; 
Point(31) = {0*ws, -330*ws, t2, lc1}; 
Point(32) = {110*ws, -330*ws, t2, lc1}; 
Point(33) = {110*ws, -490*ws, t2, lc1}; 
Point(34) = {170*ws, -490*ws, t2, lc1}; 

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
Line(12) = {12,13}; 
Line(13) = {13,14}; 
Line(14) = {14,15}; 
Line(15) = {15,16}; 
Line(16) = {16,17}; 
Line(17) = {17,18}; 
Line(18) = {18,19}; 
Line(19) = {19,20}; 
Line(20) = {20,21}; 
Line(21) = {21,22}; 
Line(22) = {22,9}; 
Line(23) = {23,24}; 
Line(24) = {24,25}; 
Line(25) = {25,26}; 
Line(26) = {26,27}; 
Line(27) = {27,28}; 
Line(28) = {28,29}; 
Line(29) = {29,30}; 
Line(30) = {30,31}; 
Line(31) = {31,32}; 
Line(32) = {32,33}; 
Line(33) = {33,34}; 
Line(34) = {34,23}; 

// Structure Loop 
Line Loop(1) = {1,2,3,4}; 
Line Loop(2) = {5,6,7,8}; 
Line Loop(3) = {9,10,11,12,13,14,15,16,17,18,19,20,21,22}; 
Line Loop(4) = {23,24,25,26,27,28,29,30,31,32,33,34}; 

// Plane Surface 
Plane Surface(1) = {1}; 
Plane Surface(2) = {2}; 
Plane Surface(3) = {3}; 
Plane Surface(4) = {4}; 

// Physical Surface 
Physical Surface("via1") = {1}; 
Physical Surface("via2") = {2}; 
Physical Surface(3) = {3}; 
Physical Surface(4) = {4}; 

// Extrude 
info1[] = Extrude {0,0,t2} {Surface{1}; Layers{{layers1},{1}};}; 
info2[] = Extrude {0,0,t2} {Surface{2}; Layers{{layers1},{1}};}; 
info3[] = Extrude {0,0,t2} {Surface{3}; Layers{{layers1},{1}};}; 
info4[] = Extrude {0,0,t2} {Surface{4}; Layers{{layers1},{1}};}; 
