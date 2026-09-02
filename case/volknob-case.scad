// -----------------------------------------------------------------------------
// Enclosure for the ESP32 BLE Volume Knob (ESP32-C3 Super Mini + KY-040).
//
// Round desktop puck. The KY-040 is clamped by its own M7 bushing nut against
// the underside of the top face, four ribs keep the board from turning, the
// ESP32-C3 slides into a pair of rails, and a bottom plate closes the case with
// three M3 screws.
//
// Coordinate system: z = 0 is the INNER surface of the top face. The case grows
// upwards to +top_t and downwards to -(cavity_h + floor_t).
//
// Print settings assumed: FDM, 0.4 mm nozzle, 0.2 mm layers.
//   body   - print upside down, top face on the bed. No supports needed.
//   plate  - print flat.
//   knob   - print with the open side down. Optional, most KY-040 kits ship one.
//
// Export a single part with:
//   openscad -D part=\"body\" -o body.stl volknob-case.scad
//
// Every dimension below is nominal. Measure your own parts with calipers and
// print part="fittest" first - it carries the three critical fits and takes a
// few minutes.
// -----------------------------------------------------------------------------

part = "body";   // "body" | "plate" | "knob" | "fittest" | "assembly" | "section"

// --- measured part dimensions ------------------------------------------------
enc_pcb_x     = 19.0;   // KY-040 board, short edge
enc_pcb_y     = 26.0;   // KY-040 board, long edge
enc_pcb_t     = 1.6;    // KY-040 board thickness
enc_body_h    = 6.7;    // encoder body height, board surface to its top face
bushing_d     = 7.0;    // threaded bushing, M7 x 0.75
bushing_h     = 5.0;    // bushing length above the encoder body
nut_t         = 2.2;    // bushing nut thickness
shaft_d       = 6.0;    // shaft diameter
pin_len       = 3.2;    // header pins and solder joints below the board
// MEASURE THIS: distance from the shaft axis to the centre of the KY-040
// board, positive towards the pin header. On most boards the encoder sits at
// one end and the header at the other, so this is NOT zero. The fit test
// cannot catch it - check it before printing the body.
enc_off_y     = 6.0;

esp_pcb_x     = 18.0;   // ESP32-C3 Super Mini, short edge
esp_pcb_y     = 22.5;   // ESP32-C3 Super Mini, long edge
esp_pcb_t     = 1.0;    // board thickness
esp_top_clear = 3.6;    // clearance above the board for components
usb_w         = 9.0;    // USB-C receptacle width
usb_h         = 3.4;    // USB-C receptacle height above the board surface

// --- case --------------------------------------------------------------------
// The outer diameter follows from the boards; set case_d_min to force a larger
// puck. Everything else scales with it.
case_d_min    = 0;      // 0 = derive from the parts
wall          = 2.4;    // side wall
top_t         = 2.4;    // top face; must stay below bushing_h - nut_t
floor_t       = 2.0;    // bottom plate
clr           = 0.3;    // print clearance, per side
fillet        = 2.0;    // rounding of the top edge

screw_d       = 2.5;    // core hole for an M3 self-tapping screw
screw_head_d  = 6.0;    // countersink in the bottom plate
post_d        = 6.0;    // screw post diameter, merges into the side wall
post_h        = 5.0;    // post height above the seam
post_angles   = [90, 210, 330];   // chosen to clear both boards

foot_d        = 8.0;    // recess for a self-adhesive rubber foot
foot_depth    = 0.8;

rib_w         = 2.4;    // anti-rotation rib width

// --- derived stack, measured downwards from the inner top face ---------------
z_enc_pcb_top = -enc_body_h;                        // KY-040 board, top surface
z_enc_pcb_bot = z_enc_pcb_top - enc_pcb_t;
z_enc_pins    = z_enc_pcb_bot - pin_len;            // lowest point of the module
z_esp_top     = z_enc_pins - 1.5;                   // ESP32-C3, top of the board
z_esp_bot     = z_esp_top - esp_pcb_t;
cavity_h      = -z_esp_bot + 2.5;                   // seam sits below the board
total_h       = top_t + cavity_h + floor_t;

z_seam        = -cavity_h;                          // body/plate joint
ledge         = 1.5;                                // shoulder the plate rests on
rib_h         = enc_body_h + enc_pcb_t + 1.5;       // ribs run from the top face down

// Radius needed by each board, taken at its worst corner. The KY-040 usually
// decides, because the shaft is offset from the board centre by enc_off_y.
r_need_enc    = sqrt(pow(enc_pcb_x / 2 + clr + rib_w, 2) +
                     pow(abs(enc_off_y) + enc_pcb_y / 2, 2));
r_need_esp    = sqrt(pow(esp_pcb_x / 2 + clr + 2.4, 2) + pow(esp_pcb_y / 2, 2));

r_cavity      = max(r_need_enc, r_need_esp) + 0.6;
r_inner       = r_cavity + ledge;                   // bottom plate seat
case_d        = max(case_d_min, 2 * (r_inner + wall));

screw_circle  = r_cavity + 0.5;                     // posts merge into the wall
foot_circle   = case_d / 2 - 7.0;
// Push the ESP32-C3 against the wall so the USB-C receptacle reaches the
// opening. The wall is curved, so the usable chord at the board width decides.
esp_y_wall    = -sqrt(r_cavity * r_cavity - pow(esp_pcb_x / 2 + clr, 2));
esp_y_off     = esp_y_wall + esp_pcb_y / 2;

$fn = 96;

echo(str("stack: enc_pcb ", z_enc_pcb_top, "  pins ", z_enc_pins,
         "  esp ", z_esp_top, "  seam ", z_seam, "  total_h ", total_h));
echo(str("case_d ", case_d, "   r_cavity ", r_cavity,
         "   r_need_enc ", r_need_enc, "   r_need_esp ", r_need_esp));
echo(str("esp board y ", esp_y_off - esp_pcb_y / 2, " .. ", esp_y_off + esp_pcb_y / 2,
         "   ky040 board y ", enc_off_y - enc_pcb_y / 2, " .. ", enc_off_y + enc_pcb_y / 2,
         "   cavity r ", r_cavity));

// =============================================================================
// helpers
// =============================================================================

// Puck spanning z = 0..h with the top edge rounded by r.
module puck(d, h, r) {
    hull() {
        cylinder(d = d, h = h - r);
        translate([0, 0, h - r]) rotate_extrude() translate([d / 2 - r, 0])
            circle(r = r);
        translate([0, 0, h - r]) cylinder(d = d - 2 * r, h = r);
    }
}

// =============================================================================
// body
// =============================================================================
// The cavity has to be cut BEFORE the internal features are added, otherwise it
// removes them again.
module body() {
    difference() {
        union() {
            difference() {
                // outer shell
                translate([0, 0, -(cavity_h + floor_t)]) puck(case_d, total_h, fillet);

                // inner cavity; r_cavity leaves a shoulder for the bottom plate
                translate([0, 0, z_seam - 0.01])
                    cylinder(d = 2 * r_cavity, h = cavity_h + 0.02);

                // recess that takes the bottom plate
                translate([0, 0, -(cavity_h + floor_t) - 0.01])
                    cylinder(d = 2 * r_inner, h = floor_t + 0.01);
            }

            // anti-rotation ribs around the KY-040 board, two per long edge
            for (sx = [-1, 1], sy = [-1, 1])
                translate([sx * (enc_pcb_x / 2 + clr + rib_w / 2),
                           enc_off_y + sy * (enc_pcb_y / 4),
                           -rib_h / 2])
                    cube([rib_w, 8, rib_h], center = true);

            // rails for the ESP32-C3: a ledge below plus a lip above the board
            for (s = [-1, 1]) {
                translate([s * (esp_pcb_x / 2 + clr + 0.8), esp_y_off, z_esp_bot - 0.6])
                    cube([1.6, esp_pcb_y, 1.2], center = true);
                translate([s * (esp_pcb_x / 2 + clr + 0.8), esp_y_off, z_esp_top + 0.6])
                    cube([1.6, esp_pcb_y, 1.2], center = true);
            }

            // screw posts, merged into the side wall
            for (a = post_angles) rotate([0, 0, a])
                translate([screw_circle, 0, z_seam])
                    cylinder(d = post_d, h = post_h);
        }

        // ---- cut last, so nothing added above can block these -----------------
        // bushing hole through the top face
        translate([0, 0, -0.01])
            cylinder(d = bushing_d + 2 * clr, h = top_t + 0.02);

        // USB-C opening through the wall at -y
        translate([-(usb_w / 2 + clr), -case_d / 2 - wall, z_esp_top])
            cube([usb_w + 2 * clr, 3 * wall, usb_h + 2 * clr]);

        // screw holes
        for (a = post_angles) rotate([0, 0, a])
            translate([screw_circle, 0, z_seam - 0.01])
                cylinder(d = screw_d, h = post_h + 0.02);
    }
}

// =============================================================================
// bottom plate
// =============================================================================
module plate() {
    difference() {
        cylinder(d = 2 * r_inner - 2 * clr, h = floor_t);

        for (a = post_angles) rotate([0, 0, a]) translate([screw_circle, 0, -0.01]) {
            cylinder(d = screw_d + 0.8, h = floor_t + 0.02);
            cylinder(d1 = screw_head_d, d2 = screw_d + 0.8, h = 1.7);
        }

        for (a = [45, 135, 225, 315]) rotate([0, 0, a])
            translate([foot_circle, 0, -0.01])
                cylinder(d = foot_d, h = foot_depth + 0.01);
    }
}

// =============================================================================
// optional knob
// =============================================================================
knob_d = 32;
knob_h = 14;
module knob() {
    difference() {
        puck(knob_d, knob_h, 2.5);
        // D-bore for the shaft
        translate([0, 0, -0.01]) difference() {
            cylinder(d = shaft_d + 2 * clr, h = knob_h - 3);
            translate([shaft_d / 2 - 1.0 + clr, -shaft_d, -0.01])
                cube([shaft_d, 2 * shaft_d, knob_h]);
        }
        // grip flutes
        for (a = [0 : 15 : 359]) rotate([0, 0, a])
            translate([knob_d / 2, 0, -0.01]) cylinder(d = 2.4, h = knob_h + 0.02);
    }
}

// =============================================================================
// fit test: a 2 mm slice carrying the three critical fits
// =============================================================================
module fittest() {
    difference() {
        translate([-16, -12, 0]) cube([52, 24, 2]);
        translate([0, 0, -0.01]) cylinder(d = bushing_d + 2 * clr, h = 2.02);
        translate([20, 0, 1])
            cube([usb_w + 2 * clr, usb_h + 2 * clr, 2.04], center = true);
        translate([-9, 0, 1])
            cube([esp_pcb_t + 2 * clr, 14, 2.04], center = true);
    }
}

// =============================================================================
module assembly() {
    body();
    translate([0, 0, -(cavity_h + floor_t)]) plate();
    color("silver") translate([0, 0, top_t]) cylinder(d = shaft_d, h = 15);
}

if      (part == "body")     body();
else if (part == "plate")    plate();
else if (part == "knob")     knob();
else if (part == "fittest")  fittest();
else if (part == "assembly") assembly();
else if (part == "section")
    difference() { assembly(); translate([0, 0, -60]) cube([60, 60, 120]); }
