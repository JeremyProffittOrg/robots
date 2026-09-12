// doorbot door-side parts: the cable anchor and the magnet pod.
// The pod is ONE design printed twice - once for the door's latch edge, once for the jamb
// opposite it - with the magnets loaded so the two pods attract.

include <lib.scad>

// ---------------------------------------------------------------- door anchor
// Screws to the door face. Holds the cable eye anchor_standoff off the face so the cable line
// clears the leaf and the moment arm never collapses. The eye is loaded in double shear with
// its axis flat to the bed, so the tension never tries to peel layers apart.
module door_anchor() {
    eye_z = anchor_standoff;
    difference() {
        union() {
            // base plate
            rbox_corner([anchor_base_l, anchor_base_w, anchor_base_t], r = 4);
            // tapered standoff: a full-width web, thickest at the root
            hull() {
                translate([anchor_base_l / 2 - 13, anchor_base_w / 2 - cable_eye_wall,
                           anchor_base_t - eps])
                    cube([26, 2 * cable_eye_wall, 1]);
                translate([anchor_base_l / 2 - cable_eye_h / 2,
                           anchor_base_w / 2 - cable_eye_wall, eye_z - cable_eye_h / 2])
                    cube([cable_eye_h, 2 * cable_eye_wall, cable_eye_h / 2]);
            }
            // the eye itself
            translate([anchor_base_l / 2, anchor_base_w / 2 - cable_eye_wall,
                       eye_z - cable_eye_h / 2])
                rotate([-90, 0, 0]) cylinder(d = cable_eye_h, h = 2 * cable_eye_wall, $fn = 48);
        }
        // cable bore through the eye, with a generous radius so the cable is not knife-edged
        translate([anchor_base_l / 2, anchor_base_w / 2 + cable_eye_wall + eps,
                   eye_z - cable_eye_h / 2])
            rotate([90, 0, 0]) cyl(cable_eye_d, 2 * cable_eye_wall + 2 * eps);
        // three wood screws, countersunk
        for (i = [-1 : 1])
            translate([anchor_base_l / 2 + i * anchor_screw_pitch, anchor_base_w / 2, 0])
                countersink(anchor_screw_d + 0.6, anchor_base_t, anchor_screw_d * 2.2);
    }
}

// ---------------------------------------------------------------- magnet pod
// Two D84 magnets per pod, each in a pocket closed by three bridged layers. Print, pause at
// the pocket depth, drop both magnets in the same way up, resume: no adhesive, and the magnet
// cannot creep out towards the steel it is pulling on.
module magnet_pod() {
    difference() {
        union() {
            hull() {
                rbox_corner([pod_l, pod_w, pod_t - 1.5], r = 5);
                translate([2, 2, pod_t - 1.5]) rbox_corner([pod_l - 4, pod_w - 4, 1.5], r = 4);
            }
            // a shallow lead-in chamfer so a door that arrives slightly skewed still centres
        }
        // magnet pockets, opening towards the bed so the cap layers bridge over the face
        for (i = [-1, 1])
            translate([pod_l / 2 + i * magnet_pitch / 2, pod_w / 2, 0]) magnet_pocket();
        // two screws, countersunk, between the magnets
        for (i = [-1, 1])
            translate([pod_l / 2 + i * (magnet_pitch / 2 - magnet_pocket_d / 2 - 5.5),
                       pod_w / 2, 0])
                countersink(pod_screw_d + 0.5, pod_t, pod_screw_d * 2.2);
    }
}
