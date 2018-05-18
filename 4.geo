// This code was created by pygmsh v4.1.5.
SetFactory("OpenCASCADE");
Mesh.CharacteristicLengthMin = 1;
Mesh.CharacteristicLengthMax = 1;
p0 = newp;
Point(p0) = {-0.20357, -0.05507, 0, 1.0};
p1 = newp;
Point(p1) = {-0.31319, -0.05507, 0, 1.0};
p2 = newp;
Point(p2) = {-0.31319, 0.05527, 0, 1.0};
p3 = newp;
Point(p3) = {-0.20357, 0.05527, 0, 1.0};
p4 = newp;
Point(p4) = {-0.20357, 0.09492, 0, 1.0};
p5 = newp;
Point(p5) = {-0.50479, 0.09492, 0, 1.0};
p6 = newp;
Point(p6) = {-0.50479, -0.09493, 0, 1.0};
p7 = newp;
Point(p7) = {-0.20357, -0.09493, 0, 1.0};
l0 = newl;
Line(l0) = {p0, p1};
l1 = newl;
Line(l1) = {p1, p2};
l2 = newl;
Line(l2) = {p2, p3};
l3 = newl;
Line(l3) = {p3, p4};
l4 = newl;
Line(l4) = {p4, p5};
l5 = newl;
Line(l5) = {p5, p6};
l6 = newl;
Line(l6) = {p6, p7};
l7 = newl;
Line(l7) = {p7, p0};
ll0 = newll;
Line Loop(ll0) = {l0, l1, l2, l3, l4, l5, l6, l7};
s0 = news;
Plane Surface(s0) = {ll0};
Physical Surface("4_0_0") = {s0};
p8 = newp;
Point(p8) = {-0.20357, -0.03802251, 0, 1.0};
p9 = newp;
Point(p9) = {-0.23346, -0.052000000000000005, 0, 1.0};
p10 = newp;
Point(p10) = {-0.23346, 0.052000000000000005, 0, 1.0};
p11 = newp;
Point(p11) = {-0.20357, 0.03802251, 0, 1.0};
p12 = newp;
Point(p12) = {-0.20357, 0.05527, 0, 1.0};
p13 = newp;
Point(p13) = {-0.31319, 0.05527, 0, 1.0};
p14 = newp;
Point(p14) = {-0.31319, -0.05507, 0, 1.0};
p15 = newp;
Point(p15) = {-0.20357, -0.05507, 0, 1.0};
l8 = newl;
Line(l8) = {p8, p9};
l9 = newl;
Line(l9) = {p9, p10};
l10 = newl;
Line(l10) = {p10, p11};
l11 = newl;
Line(l11) = {p11, p12};
l12 = newl;
Line(l12) = {p12, p13};
l13 = newl;
Line(l13) = {p13, p14};
l14 = newl;
Line(l14) = {p14, p15};
l15 = newl;
Line(l15) = {p15, p8};
ll1 = newll;
Line Loop(ll1) = {l8, l9, l10, l11, l12, l13, l14, l15};
s1 = news;
Plane Surface(s1) = {ll1};
Physical Surface("4_1_0") = {s1};
bo1[] = BooleanUnion{ Surface{s0}; Delete; } { Surface{s1}; Delete;};
Mesh.Algorithm = 100;