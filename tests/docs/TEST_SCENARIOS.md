# Test scenarios

Every scenario of the test suite, grouped by test file. Each group starts with what that part of the
program does and how it is tested; each test then says what it does, what result it expects and why
the scenario matters. The same scenarios are run against the Python program and against the C rewrite
(see [HOW_TESTS_WORK.md](HOW_TESTS_WORK.md)).

**Scenario IDs:** every scenario has an ID such as `GE-12`: a prefix for the area and a number in the
order of the test file. The same ID is written as a comment (`# GE-12`) directly above the test in the
`.py` file, so a scenario can be found in both places. New tests get the next free number of their area.

| Prefix | Area | Test file |
|---|---|---|
| EN | enums (GUI labels) | `test_enums.py` |
| CV | convolution | `test_convolution.py` |
| CO | colour helpers | `test_color_utils.py` |
| GE | geometry helpers | `test_geometry_utils.py` |
| FW | points file | `test_file_writer.py` |
| IO | image loading and saving | `test_image_io.py` |
| DI | point distributions | `test_distributions.py` |
| TE | tessellations | `test_tessellations.py` |
| RE | rendering effects | `test_rendering.py` |
| PI | whole pipeline | `test_pipeline.py` |
| UI | GUI | `test_ui.py` |

**How a result is checked** (shown in brackets after each test name):

* **Exact** – the result must equal a value written in the test.
* **Golden** – the result must equal a reference result saved in `tests/golden/`, produced by the Python program.
* **Property** – the result is random or not unique, so the test checks rules that every correct result
  must follow (counts, bounds, distances, …).
* **Tolerance** – compared with a reference result, allowing a stated small difference.

**Test pictures** in `tests/data/`:

| Name | Size | Content | Why it exists |
|---|---|---|---|
| `blocks` | 64×48 | four single-colour rectangles and a dark disc | few colours and sharp edges, so results are predictable |
| `blocks_large` | 512×384 | the same picture, 8× larger | wide enough for visible grid lines (line width = image width / 500) |
| `halves` | 96×64 | left half one flat colour, right half random noise | shows whether the program puts detail where the picture has detail |
| `photo` | 120×83 | the sample photo `cat.jpg`, shrunk; also as `photo.jpg` | a real photograph that is still fast to process |
| `gradient` | 40×30 | smooth colour gradient | many different colours, no two neighbours equal |

**Seeds:** many parts of the program use random numbers. Tests that need repeatable results first call
`backend.seed(n)`, which seeds the program's random generators. Different seeds must give different
results, the same seed the same result.

In total: 141 test functions and 325 test runs (some functions run once for each listed input).

---

## Enums – `test_enums.py` (EN)

The program offers 4 tessellations, 8 point distributions and 7 effects. Each has a Czech label that the
GUI shows in its menus (`enums/`). The C program must show exactly the same labels in the same order,
and the GUI tests will find menu items by these labels.

* **EN-01 `test_tessellation_labels`** (Exact) – The tessellations and their labels in menu order:
  `Voroného diagram`, `Delaunayho triangulace - Rychlejší`, `Delaunayho triangulace - Lepší barvy`,
  `Kvadrantový strom`.
* **EN-02 `test_distribution_labels`** (Exact) – The 8 point distributions and their labels, e.g. `Rovnoměrné
  rozdělení`, `Laplaceův operátor - Obsah trojúhelníku`, `Mitchellův algoritmus`.
* **EN-03 `test_effect_labels`** (Exact) – The 7 effects and their labels, from `Žádný` (no effect) to `Papír`.

---

## Convolution – `test_convolution.py` (CV)

Convolution slides a small 3×3 matrix (a *kernel*) over an image and combines each pixel with its
neighbours (`util/convolution.py`). The program uses it twice: the **Laplace kernel** finds edges for
the Laplace point distributions, and the **Gaussian kernel** blurs the noise of the paper effect. Before
convolving, the matrix gets a 1-cell border (*padding*) copied from its edges, so the result has the
same size as the image. All results are exact numbers.

* **CV-01 `test_kernels`** (Exact) – The two kernels have exactly the values from the thesis: Laplace
  `[[0,1,0],[1,-4,1],[0,1,0]]`, Gaussian `[[1/16,1/8,1/16],[1/8,1/4,1/8],[1/16,1/8,1/16]]`.
* **CV-02 `test_padding_replicates_edges`** (Exact) – A 2×3 matrix becomes 4×5: each edge row and column is
  copied once more outside, including the corners.
* **CV-03 `test_padding_single_column`** (Exact) – In a one-column matrix the only column is both the leftmost
  and the rightmost one, so it is copied to both sides: `[[7],[8]]` → rows `7 7 7`, `7 7 7`, `8 8 8`,
  `8 8 8`.
* **CV-04 `test_padding_single_row`** (Exact) – A one-row matrix is padded on all four sides.
* **CV-05 `test_convolute_result_is_two_smaller`** (Exact) – Convolution of a padded 5×6 matrix gives 3×4:
  the border is used only as neighbours, it gets no result of its own.
* **CV-06 `test_laplace_of_impulse`** (Exact) – A single 1 in a field of zeros produces the kernel pattern
  itself around it. Checks that the kernel is applied the right way round and at the right position.
* **CV-07 `test_laplace_of_constant_is_zero`** (Exact) – A flat area has no edges, so the result is all zeros.
* **CV-08 `test_laplace_of_linear_ramp_is_zero`** (Exact) – A steady slope also has no edges (the Laplace
  operator reacts to changes of slope only), so again all zeros.
* **CV-09 `test_gaussian_blur_values`** (Exact) – A single value 16 is spread to 4 in its centre (16 × 1/4);
  the numbers 1–9 blur to 5 in the middle, their weighted average.
* **CV-10 `test_separate_color_channels`** (Exact) – A 2×2 image is split into three padded 4×4 matrices,
  one each for red, green and blue, with the right value in every cell.

---

## Colour helpers – `test_color_utils.py` (CO)

These functions decide the colour of every region in the output picture (`util/color_utils.py`):
average colour, most frequent colour, colour differences. Colours are triples of numbers from 0 to 1.
Ties (two colours equally frequent) must be broken exactly like in the original, otherwise the C
program would pick different region colours.

* **CO-01 `test_color_int_to_float`** (Exact) – `(255, 0, 51)` becomes `(1.0, 0.0, 0.2)`: each channel divided
  by 255.
* **CO-02 `test_complementary_color`** (Exact) – The complementary colour of `(0.2, 0.5, 1.0)` is
  `(0.8, 0.5, 0.0)`: each channel subtracted from 1. Used for grid line colours.
* **CO-03 `test_get_point_color_inside_and_outside`** (Exact) – A pixel inside the image returns its colour.
  Points outside – negative coordinates, exactly at the width or height, far away – return black instead
  of failing. This is a safety net: the program's current callers only pass points inside the image
  (the average and most-common-colour functions skip outside points before asking).
* **CO-04 `test_image_mode_color`** (Exact) – The most frequent colour of the whole image. The one-colour grid
  effect uses its complementary colour for all grid lines.
* **CO-05 `test_image_mode_color_tie_prefers_first_seen`** (Exact) – With two colours equally frequent, the
  one that appears first when reading the image row by row wins. Checked both ways round.
* **CO-06 `test_points_average_color`** (Exact) – Average colour of the given pixels; an empty list gives black.
* **CO-07 `test_points_average_color_counts_points_outside_image`** (Exact) – A point outside the image adds no
  colour but still counts when dividing. With one red pixel and one point outside, the average is half
  red `(0.5, 0, 0)`. This is the original behaviour and the C program must reproduce it.
* **CO-08 `test_most_common_colors`** (Exact) – Asking for the 1, 2 or 10 most common colours returns them
  ordered by count, ties by first appearance, and never more colours than exist.
* **CO-09 `test_most_common_colors_ties_follow_point_order`** (Exact) – Three colours appearing once each come
  back in the order of the given points.
* **CO-10 `test_most_common_colors_ignores_points_outside`** (Exact) – Points outside the image are skipped.
  Only outside points, or no points at all, give `[black]`.
* **CO-11 `test_rectangle_average_color_excludes_max_edges`** (Exact) – For the rectangle with corners (0,0)
  and (2,2), only pixels with x and y equal to 0 or 1 are averaged: the right and bottom edge belong to
  the neighbouring rectangle. This keeps quadtree regions from sharing pixels.
* **CO-12 `test_rectangle_average_color_degenerate_uses_first_vertex`** (Exact) – A rectangle of zero width
  contains no pixels; its colour is taken from its first corner.
* **CO-13 `test_rectangle_standard_deviation`** (Exact) – One black and one white pixel: average grey, sample
  standard deviation √0.5 per channel, summed over three channels = 3·√0.5. The quadtree splits a region
  when this value is too high.
* **CO-14 `test_rectangle_standard_deviation_trivial_cases`** (Exact) – A one-colour rectangle gives 0; a
  single pixel gives 0 (a deviation needs at least two values).
* **CO-15 `test_colors_difference`** (Exact) – Difference of two colours = sum of the absolute differences of
  their channels, e.g. `(0.1,0.5,1.0)` vs `(0.3,0.5,0.0)` → 1.2.
* **CO-16 `test_colors_ratio`** (Exact) – Counts how many pixels are closer to the second colour than to the
  first; both counters start at 1. For pixels red, red, blue and colours (red, blue): red 3, blue 2 →
  2/3; with the colours swapped → 3/2. Sets the oval size in the rectangles-with-ovals effect.
* **CO-17 `test_colors_ratio_tie_counts_for_second_color`** (Exact) – A black pixel is equally far from red
  and green and counts for the second colour (ratio 2). With no pixels the ratio is 1/1.

---

## Geometry helpers – `test_geometry_utils.py` (GE)

Small geometric building blocks (`util/geometry_utils.py`, `geometry/point_2d.py`) used by the
distributions, tessellations and effects. Most are exact. Where polygons are compared, the starting
corner and the direction (clockwise or not) do not matter, because Python's geometry library and the C
code may list the same polygon differently.

### Points and rectangles

* **GE-01 `test_euclidean_distance`** (Exact) – Distance (0,0)–(3,4) is 5; a point to itself is 0.
* **GE-02 `test_line_center_truncates_toward_zero`** (Exact) – The midpoint of two points is cut to whole
  numbers toward zero: (1,1)–(4,4) → (2,2), and (−1,0)–(−4,0) → (−2,0), not −3. C rounds differently by
  default, so this must be checked.
* **GE-03 `test_is_point_in_image`** (Exact) – A point is in a 4×3 image if 0 ≤ x < 4 and 0 ≤ y < 3. Points at
  x = 4, y = 3 or negative are outside.
* **GE-04 `test_find_rectangle_points_excludes_max`** (Exact) – For the rectangle (1,2)–(4,5) the pixel columns
  are 1, 2, 3 and rows 2, 3, 4: the maximum is excluded. A zero-size rectangle has none.

### Points inside a polygon

Used to find which pixels lie in a triangle or region, e.g. to choose its colour. The polygon's corners
always come first in the result, followed by the pixels strictly inside (not on the border), in random
order.

* **GE-05 `test_points_in_square`** (Exact) – Square (0,0)–(4,4) in a 10×10 image: its 4 corners, then the 9
  points with x and y from 1 to 3; 13 points, no duplicates.
* **GE-06 `test_points_in_triangle`** (Exact) – Triangle (0,0), (6,0), (0,6): 3 corners plus the 10 integer
  points with x, y ≥ 1 and x + y < 6.
* **GE-07 `test_points_in_polygon_limit`** (Property) – With a limit of 6, exactly 6 points come back: the 4
  corners and 2 of the valid inner points. The fast Delaunay variant uses this limit.
* **GE-08 `test_points_in_polygon_partially_outside_image`** (Exact) – For a square sticking out of the image,
  all corners are kept even outside, but inner points only where they are inside the image.
* **GE-09 `test_points_in_polygon_all_vertices_outside`** (Exact) – If no corner is inside the image, the
  result is empty, even for a polygon that covers the whole image. That is the original behaviour.
* **GE-10 `test_points_in_polygon_random_order_is_seeded`** (Property) – The same seed gives the same order of
  points twice.

### Clipping polygons to the image

Voronoi regions at the border of the picture reach outside it and are clipped to the image rectangle.
Because their corners are rounded to whole pixels, some regions become slightly broken shapes; the
program repairs them.

* **GE-11 `test_crop_partially_outside`** (Exact) – A square from (−5,−5) to (5,5) clipped to the bounds
  (0,0)–(10,10) gives the square (0,0)–(5,5).
* **GE-12 `test_crop_triangle`** (Exact) – A triangle sticking out of the corner is cut into the quadrilateral
  that remains inside.
* **GE-13 `test_crop_fully_inside`** (Exact) – A polygon completely inside the bounds comes back unchanged.
* **GE-14 `test_crop_disjoint_gives_empty`** (Exact) – A polygon completely outside gives an empty result.
* **GE-15 `test_crop_touching_edge_gives_empty`** (Exact) – A square that only touches the bounds along one
  edge has no area inside, so the result is empty.
* **GE-16 `test_crop_self_intersecting_polygon_is_repaired`** (Exact) – A bow-tie (a polygon crossing itself)
  is split into its two triangles; one triangle of area 25, lying inside the bounds, is returned.
* **GE-17 `test_crop_rounded_voronoi_region_with_line_part`** (Exact) – A region taken from a real run of the
  error distribution. Its overlap with the image is a small polygon plus a stray line. The polygon
  (0,46), (2,46), (2,47), (0,48) must come back. Before the fix, the region was returned unclipped and new
  points were placed far outside the image.
* **GE-18 `test_crop_degenerate_self_touching_region`** (Exact) – Another real region, which touches itself
  after rounding (invalid). Its valid part inside the image, the rectangle (82,0)–(83,2), must come back.

### Areas, random points, centroid, longest side

* **GE-19 `test_polygon_area`** (Exact) – Rectangle 4×3 → 12; triangle → 6, whichever direction its corners go.
* **GE-20 `test_random_point_in_polygon_is_strictly_inside`** (Property) – 200 random points in a triangle are
  all whole numbers strictly inside it, never on its border. The error distribution places new points
  this way.
* **GE-21 `test_random_point_in_polygon_without_inner_point`** (Exact) – A thin sliver between x = 94 and
  x = 95 has no whole-number point inside, so the answer is "none" instead of searching forever. In a 2×2
  square only (1,1) is inside; if (1,1) is excluded, the answer is "none".
* **GE-22 `test_random_point_in_polygon_avoids_excluded_point`** (Exact) – In a 3×2 rectangle the inner points
  are (1,1) and (2,1). With (1,1) excluded, 50 draws always give (2,1). The error distribution excludes a
  region's own generator, because a duplicate point would not split the region.
* **GE-23 `test_random_point_in_polygon_uses_whole_polygon`** (Property) – 400 draws in a 4×4 square hit all 9
  inner points, so no part of the polygon is left out.
* **GE-24 `test_centroid`** (Exact) – The centroid is the average of the corners, cut toward zero: (1,1) for
  the triangle (0,0), (3,0), (0,3); (0,0) for an average of 2/3; −1 for an average of −5/3. No corners →
  (−1, −1).
* **GE-25 `test_longest_side`** (Exact) – In the 3-4-5 triangle the longest side is the hypotenuse (5). In a
  square all sides are equal and the first one wins. No corners → no side.

### Splitting a polygon in two

The gradient effect splits each region in two along a line from the middle of its longest side to the
farthest middle of another side, leaving a 2 px gap, and fills the halves with a colour gradient.

* **GE-26 `test_split_square_in_half`** (Exact) – A 20×20 square is cut at x = 10 into two parts spanning
  x = 0–9 and x = 11–20, each of area 180 (±1).
* **GE-27 `test_split_keeps_original_vertices`** (Property) – A pentagon is split in two; every original corner
  ends up in one of the parts, and together the parts are slightly smaller than the pentagon (the gap).
* **GE-28 `test_split_too_small_returns_original`** (Exact) – A triangle too small for a 2 px gap, and an empty
  polygon, come back unchanged as one part.

### Removing points that are too close

Several distributions drop points that are closer than a minimum distance, so the regions are not too
tiny. The first point of each close group is kept and the order stays the same.

* **GE-29 `test_remove_similar_points_keeps_order_and_is_inclusive`** (Exact) – With minimum distance 1, a
  point exactly 1 away counts as too close and is removed; a point √2 ≈ 1.41 away stays.
* **GE-30 `test_remove_similar_points_no_chaining`** (Exact) – Points (0,0), (1,0), (2,0): (1,0) is removed
  because of (0,0). (2,0) is only close to the removed (1,0), not to (0,0), so it stays.
* **GE-31 `test_remove_similar_points_zero_distance_removes_duplicates`** (Exact) – Minimum distance 0 removes
  only exact duplicates.
* **GE-32 `test_remove_similar_points_larger_radius`** (Exact) – Points (0,0), (3,4), (6,8), (2,1), (10,10)
  with minimum distance 5: (0,0) is kept and removes (3,4) (exactly 5 away) and (2,1); (6,8) is kept and
  removes (10,10) (√20 ≈ 4.47 away). Result: `[(0,0), (6,8)]`.

---

## Points file – `test_file_writer.py` (FW)

If the user ticks *Zapsat vygenerované body do souboru*, the generated points are written to a text
file in `points_output/` (`util/file_writer.py`). The file can be used to analyse the distribution.

* **FW-01 `test_points_file_format`** (Exact) – Writing 3 points creates
  `points_output/DD-MM-YYYY_HH-MM-SS.txt`, named after the current time. Its UTF-8 content must be
  exactly: the line `# počet bodů`, the number 3, the line `# souřadnice x;souřadnice y`, and one line
  `x;y` per point in the given order.
* **FW-02 `test_points_file_empty`** (Exact) – With no points the file has the header and the count 0.

---

## Image loading and saving – `test_image_io.py` (IO)

The GUI opens a JPEG, applies the rotation stored in the photo's EXIF data and converts it to RGB; the
result window saves the output as PNG. Every later step depends on the exact pixel values, so the C
program must decode JPEGs to exactly the same pixels as the Python program.

* **IO-01 `test_sample_images_decode_identically`** (Golden, ×14) – Each picture in `img_input/` is loaded and
  compared with the reference: same width and height, and the same SHA-256 fingerprint of all pixels.
* **IO-02 `test_test_photo_decodes_identically`** (Golden) – The same for `tests/data/photo.jpg`, the picture the GUI
  tests will open.
* **IO-03 `test_exif_orientation_is_applied`** (Exact) – `cassie_trava.jpeg` is stored as 4032×3024 with an
  EXIF note "rotate by 90°". It must load as 3024×4032, the way the photo was taken.
* **IO-04 `test_grayscale_jpeg_becomes_rgb`** (Exact) – `audrey_hepburn.jpg` is a black-and-white JPEG. It must
  load as an RGB image with red = green = blue in every pixel.
* **IO-05 `test_save_png_roundtrip`** (Exact) – A 7×5 image with different colours and transparency levels is
  saved as PNG and read back. The file must be a PNG with transparency (RGBA) and contain exactly the
  same values: saving must not convert or adjust them.

---

## Point distributions – `test_distributions.py` (DI)

The first step of the program chooses the starting points for the tessellation
(`point_generator.py`, `distributions/`). All distributions except the Laplace ones are random, so their
tests check properties. Uniform and normal tests use a plain 300×200 image.

Most distributions aim for `round(log((width · height · 100000)², 1.05)) · 2` points, a formula from the
thesis (1846 points for 300×200).

### General

* **DI-01 `test_point_count_formula`** (Exact) – Checks the test's own copy of the formula: 1846 for 300×200,
  1680 for 100×80, 2048 for 1000×700. Other tests rely on it.
* **DI-02 `test_random_distributions_are_seeded`** (Property; uniform, normal, error) – Two runs with seed 7 give
  identical points; seed 8 gives different points.
* **DI-03 `test_points_are_unique_integers`** (Property; uniform, normal, 3× Laplace, error) – All coordinates
  are whole numbers and no point appears twice.

### Uniform distribution

Points spread evenly at random, then points too close together are removed (minimum distance = shorter
image side / 100).

* **DI-04 `test_uniform_bounds_and_count`** (Property) – Every point has 1 ≤ x ≤ width−1 and 1 ≤ y ≤ height−1:
  the program asks for values from 1 up to the width, with the upper end excluded. 70–100 % of the 1846
  requested points remain after removing close ones.
* **DI-05 `test_uniform_respects_given_range`** (Property) – Asking for x in 10–20 and y in 5–8 gives points with
  x from 10 to 19 and y from 5 to 7 only.
* **DI-06 `test_uniform_removes_close_points`** (Property) – Every two points are more than 2 px apart
  (300×200 → minimum distance 2; points exactly 2 apart are removed too).
* **DI-07 `test_uniform_is_spread_evenly`** (Property) – Each quarter of the image holds 21–29 % of the points.

### Normal distribution with the rule of thirds

Points are concentrated around the four "rule of thirds" points (where lines at 1/3 and 2/3 of the
width and height cross), using a normal (bell-curve) distribution.

* **DI-08 `test_normal_bounds_count_and_distance`** (Property) – All points are inside the image, there are
  50–100 % of the requested count (points falling outside are dropped), and every two points are more
  than 2 px apart.
* **DI-09 `test_normal_points_concentrate_around_thirds`** (Property) – Fewer than 20 % of the points lie in
  the outer 10 % frame of the image and more than 17 % in the central third. For comparison, uniform
  points give about 35 % and 11 %. The average point lies near the image centre.

### Mitchell's algorithm

Each new point is the best of several random candidates: the one farthest from all points chosen so
far. This spreads points evenly without clumps. It is the slowest part of the Python program (~80 s
for 1680 points).

* **DI-10 `test_mitchell`** (Property) – On a 100×80 image, exactly 1680 points (the formula), all different,
  all within the allowed range. The smallest distance between two points is at least as large as for
  uniform points: Mitchell's points are spread more evenly.
* **DI-11 `test_mitchell_on_tiny_image_fills_every_position`** (Exact; 20×10 and 40×30) – These images have
  fewer possible positions than the formula asks for (e.g. 40×30: 1131 positions, 1526 requested). Every
  possible position must be used exactly once and the algorithm must finish.

### Laplace operator

Points are placed on edges in the picture: the 5 % of pixels where the Laplace operator gives the
strongest response. They are triangulated, and triangles that are too large (*area* variant), have too
long sides (*length* variant) or too different corner colours (*gradient* variant) get extra points.
Finally, points too close together are removed (minimum distance = shorter side / 65). There is no
randomness, but the result depends on how the triangulation resolves ties, which may differ between the
Python library and the C code.

* **DI-12 `test_laplace_is_deterministic_and_inside_image`** (Property; 3 variants) – Two runs with different
  seeds give the same points, and all points lie inside the image.
* **DI-13 `test_laplace_close_to_reference`** (Tolerance; 3 variants) – On `photo`, the number of points is
  within ±5 % of the Python program's result and at least 85 % of the Python program's points are
  present. Points cannot be required to match exactly: pixels lie on a grid, where a triangulation is
  often not unique, so a correct C program may add some extra points elsewhere.
* **DI-14 `test_laplace_points_lie_on_detail`** (Property; 3 variants) – On `halves`, every point lies in
  the noisy half (x ≥ 47): a flat area has no edges, and extra points are only added inside triangles of
  edge pixels. Column 47 is still flat but next to the noise, so the Laplace operator marks it as an
  edge too.
* **DI-15 `test_laplace_min_distance`** (Property) – On `blocks_large` (minimum distance 384/65 → 5), every two
  points are more than 5 px apart, for all three variants.

### Splitting regions by error

Starts from uniform points, builds a Voronoi diagram and repeatedly adds a random point inside every
region whose colours vary too much (standard deviation above a limit), until no region needs splitting.
Four helper points far outside the image keep the border regions finite and are part of the result.

* **DI-16 `test_error_on_plain_image_is_uniform_plus_far_points`** (Exact) – On a one-colour image no region
  needs splitting, so the result is exactly the uniform distribution's points (same seed) followed by
  the 4 far helper points.
* **DI-17 `test_error_adds_points_where_image_varies`** (Property) – On `halves`, the result starts with the
  uniform points and the 4 helper points, followed by more than 20 added points, at least 90 % of them
  in the noisy half.
* **DI-18 `test_error_adds_points_only_inside_image`** (Property; seeds 0–9) – Apart from the 4 helper points,
  every point lies inside the image.

---

## Tessellations – `test_tessellations.py` (TE)

The second step divides the image into regions from the points (`tessellations/`). The Voronoi diagram
gives each point the area closer to it than to any other point; the Delaunay triangulation connects
the points into triangles; the quadtree splits the image into four rectangles again and again where the
colours vary too much. To make results comparable, the Voronoi and Delaunay tests use fixed points chosen
so that the correct result is unique (no four points on one circle).

### Quadtree

The quadtree starts with the whole image and splits a rectangle into four when its colour standard
deviation is above 0.12 and its area is not too small (image area / 10000). Each region's colour is its
average colour. There is no randomness, so the regions must match the Python program exactly.

* **TE-01 `test_quadtree_distribution_returns_image_corners`** (Exact) – The quadtree "distribution" only
  returns the four image corners in the order NW, NE, SE, SW (top-left, then clockwise).
* **TE-02 `test_quadtree_matches_reference`** (Golden; blocks, blocks_large, photo, gradient) – The same regions
  in the same order, with the same corners and colours, as the Python program produced.
* **TE-03 `test_quadtree_regions_tile_the_image`** (Property; same 4 images) – Every region lists its corners
  NW, NE, SE, SW, and every pixel of the image belongs to exactly one region: no gaps, no overlaps.
* **TE-04 `test_quadtree_region_color_is_average`** (Property) – Each region's colour equals the average colour
  of its pixels.
* **TE-05 `test_quadtree_uniform_image_is_one_region`** (Exact) – A one-colour image needs no splitting: one
  region covering the whole image, in that colour.
* **TE-06 `test_quadtree_split_uses_round_half_to_even`** (Exact; 7×7 and 9×9) – The split position is half the
  width, rounded the way Python rounds: halves go to the even number, so 3.5 → 4 and 4.5 → 4 (C's usual
  rounding would give 5). The picture is black left of x = 4 and white from x = 4, so the correct split
  gives exactly four one-colour regions, listed in the order they leave the program's stack (SW, SE, NE,
  NW). Any other split position cuts through the edge and creates more regions.
* **TE-07 `test_quadtree_finer_where_image_is_detailed`** (Property) – On `halves`, the flat half needs at most 8
  regions while the noisy half has more than 100 times as many.

### Voronoi diagram

Each region's colour is the colour of its point (its *generator*). Regions are clipped to the image.

* **TE-08 `test_voronoi_matches_reference`** (Golden + Tolerance; photo with 60 points, blocks_large with 80) –
  Same regions, generators and colours as the Python program; corner positions may differ by 1 px because
  corners are rounded to whole pixels.
* **TE-09 `test_voronoi_regions_follow_input_order_and_cover_image`** (Property; same inputs) – One region per
  input point, in the order of the points; each colour is the generator's pixel colour; all corners lie
  within the image; the region areas add up to the image area (±1 %).
* **TE-10 `test_voronoi_region_contains_its_generator`** (Property) – Every generator lies inside its own region
  (allowing 1.5 px for rounding).

### Delaunay triangulation

Four image corners are added to the points, so the triangles cover the whole image. The *fast* variant
chooses each triangle's colour as the most frequent colour among a random sample of its pixels; the
*better colours* variant uses all its pixels.

* **TE-11 `test_delaunay_triangles_match_reference`** (Golden; both variants × blocks, blocks_large, photo) –
  The same set of triangles as the Python program (the order of triangles does not matter).
* **TE-12 `test_delaunay_better_colors_match_reference`** (Golden; blocks, blocks_large) – Each triangle has the
  same colour as in the reference. On `photo` the colours are not compared, because many colours are
  equally frequent and the program then picks one at random.
* **TE-13 `test_delaunay_colors_come_from_the_triangle`** (Property; both variants) – Each triangle's colour is
  the colour of some pixel inside the triangle or at its corners.
* **TE-14 `test_delaunay_covers_image_including_corners`** (Property) – The triangles' corners are exactly the
  input points plus the four image corners, and the triangle areas add up to the image area
  ((width − 1) × (height − 1), measured between corner pixels).
* **TE-15 `test_delaunay_fast_is_seeded`** (Property) – The same seed gives the same triangles and colours.
* **TE-16 `test_delaunay_handles_duplicate_and_collinear_points`** (Property) – Input with a duplicate point and
  four points on one line still gives a valid triangulation: no flat triangles, full image covered.

---

## Rendering effects – `test_rendering.py` (RE)

The last step draws the regions with the chosen effect (`visualizer.py`, `geometry/*_region.py`,
`util/image_drawer.py`). Both programs draw with the same graphics library (cairo), so when they get
the same regions, the effects without randomness must produce **identical pixels**. These tests take the
regions from `tests/golden/`, so they test drawing alone, independently of the tessellations.

* **RE-01 `test_render_matches_reference_exactly`** (Golden; 24 cases) – Reference regions drawn with an effect
  must match the reference image pixel for pixel:
  * quadtree regions of `blocks`, `blocks_large` and `photo` with no effect, one-colour grid, multicolour
    grid and rectangles with ovals;
  * Delaunay regions of `blocks` and `blocks_large` with no effect and both grids;
  * Voronoi regions of `photo` and `blocks_large` with no effect and both grids.
* **RE-02 `test_gradients_match_reference`** (Tolerance; quadtree and Delaunay on `blocks_large`) – The gradient
  effect differs from the reference in at most 2 % of pixels. It splits each region (see *Splitting a
  polygon in two*), and the exact cut can differ by a pixel between geometry libraries.
* **RE-03 `test_output_has_image_size_and_is_transparent_without_regions`** (Exact) – With no regions, the
  output has the input's size and is completely transparent.
* **RE-04 `test_basic_fills_region_with_base_color`** (Exact) – A region with colour (1, 0.5, 0) is filled with
  the pixel value (255, 128, 0), fully opaque.
* **RE-05 `test_regions_with_fewer_than_three_vertices_are_not_drawn`** (Exact) – Adding a region with two
  corners and one with none does not change the image, for four effects. Such regions can appear after
  clipping and must be skipped, not cause errors.
* **RE-06 `test_paper_lightens_regions_and_adds_dark_noise`** (Property) – The paper effect lightens every
  region's colour (+0.15 red and green, +0.125 blue, at most 1) and covers the image with random dark
  speckles whose strength is between 10 % and 20 %. The test draws the lightened regions without
  speckles for comparison: every pixel value of the paper image must be 78–100 % of that value, and at
  least 95 % of the values 78–92 % (values below 40 are skipped, where rounding to whole numbers distorts
  the percentage). Transparency must be the same in both images.
* **RE-07 `test_paper_noise_is_random_but_seeded`** (Property) – The same seed gives the same speckles, another
  seed different ones.
* **RE-08 `test_paper_on_tiny_image`** (Property) – On a 9×9 image (81 pixels) the noise particle size,
  `log₁₀₀(width · height)`, would be 0; it must be at least 1 pixel. Every pixel is then covered by noise
  and darkened to 78–92 % of the lightened colour.
* **RE-09 `test_paper_on_images_thinner_than_a_noise_particle`** (Property; 1×1, 10000×1, 1×10000) – For a
  10000×1 image a noise particle is 2 px tall, so not even one row of particles fits; the effect must
  finish and return an image of the right size (the regions are drawn without noise) instead of
  crashing. 1×1 and 1×10000 are the other extreme shapes.
* **RE-10 `test_multiple_shapes`** (Property) – The *different shapes* effect draws each quadtree region at
  random as a rectangle, oval, triangle or rhombus. With the same seed the result repeats; with another
  seed it differs. Because ovals, triangles and rhombi leave parts of their rectangle empty, 15–45 % of
  the pixels are transparent, and at least 90 % of the visible pixels have exactly one of the region
  colours.
* **RE-11 `test_multiple_shapes_small_image_does_not_fail`** (Property) – The quadtree of the small `photo`
  contains regions of zero width or height (the test checks they exist). Drawing them as ovals must not
  fail.
* **RE-12 `test_gradients_on_photo_are_closer_to_input_than_flat_colors`** (Property) – On `photo`, the gradient
  effect follows the original picture more closely than one flat colour per region, because each region
  gets two colours taken from its own two halves.

---

## Whole pipeline – `test_pipeline.py` (PI)

These tests run all three steps – points, regions, drawing – the way the *Generovat* button does
(`Controller.generate`), on `photo`, for every combination the GUI offers. Most combinations involve
randomness, so the result is compared with the Python program's result by three numbers:

* **mean difference** – how much the output's colours differ from the input picture on average (0–255);
* **opaque share** – the share of pixels that are fully non-transparent;
* **number of regions**.

* **PI-01 `test_pipeline`** (Tolerance; 86 combinations) – The combinations are: Voronoi with 4 distributions ×
  5 effects; each of the two Delaunay variants with 6 distributions × 5 effects; quadtree with 6 effects.
  For each:
  * the output has the size of the input;
  * the mean difference is at least 0.5 × reference − 1 and at most 1.3 × reference + 3 (the added
    constants keep small reference values from being judged too strictly) – the picture must be
    stylised about as faithfully as by the Python program, neither much worse nor suspiciously close
    to the original;
  * the opaque share is within ±0.1 of the reference;
  * the number of regions is within ±15 % of the reference (±25 % for the Laplace and error
    distributions, which depend more on details).
* **PI-02 `test_stylize_runs_whole_pipeline`** (Property) – The helper that chains the three steps works: the
  quadtree without effect on `blocks_large` gives a fully opaque picture very close to the input.

---

## GUI – `test_ui.py` (UI)

These tests start the real application window and operate it like a user: they find buttons, labels and
menus by their visible text, click buttons and choose menu items (see the GUI part of
[HOW_TESTS_WORK.md](HOW_TESTS_WORK.md)). The file dialogs are replaced: a test decides which path the next
dialog returns ("" = the user pressed Cancel) and can read what the program asked the dialog for. Message
boxes are replaced too: they are recorded instead of shown, and the tests compare only their icon, title and
text (and that they are plain OK boxes), not other options such as `-parent`. Every test starts a fresh
application in an empty temporary working directory with `logo.png`, `img_input/`, `img_output/` and
`points_output/`, because the program uses these relative paths. The input image is `tests/data/photo.jpg`
(120×83) unless a test says otherwise. All tests have the pytest marker `ui`.

"Shown" means what a user can see: the widget is placed in its window, it is not hidden under another frame
and its window is open. Widgets that the program only hid (it hides old menus instead of deleting them)
do not count. Texts are compared exactly – the C program must show the same Czech texts.

### Main window

* **UI-01 `test_initial_window`** (Exact) – After start, only the main window is open (title empty,
  350×550 pixels) and it shows, top to bottom: the logo, the button `Vybrat obrázek`, the label
  `Vybraný obrázek: X`, the unchecked check box `Zapsat vygenerované body do souboru` and the menu
  `Vybrat teselaci`. There is no distribution or effect menu and no `> Generovat` button yet.
* **UI-02 `test_tessellation_menu_items`** (Exact) – The tessellation menu offers the 4 tessellations in the
  order of EN-01.
* **UI-03 `test_menus_offered_for_tessellation`** (Exact; 4 tessellations) – After choosing a tessellation the
  menu shows its name and below it appear the menu `Vybrat rozdělení bodů`, the menu `Vybrat efekt` and the
  button `> Generovat`, in this order. The menus offer exactly the combinations the program supports:
  * Voronoi: distributions uniform, normal (rule of thirds), error, Mitchell; effects none, grid one-colour,
    grid colourful, gradients, paper;
  * both Delaunay variants: distributions uniform, normal, the three Laplace ones, Mitchell; the same 5 effects;
  * quadtree: **no distribution menu** (the quadtree places its own points); effects none, the two grids,
    gradients, multiple shapes, rectangles with ovals.
* **UI-04 `test_changing_tessellation_replaces_menus`** (Exact) – Choosing another tessellation (Voronoi →
  quadtree → Delaunay) replaces the menus: there is always only one distribution and one effect menu, they
  show the prompts `Vybrat rozdělení bodů` / `Vybrat efekt` again and offer the items for the new tessellation.
* **UI-05 `test_chosen_items_are_shown`** (Exact) – Each menu shows the item chosen last.
* **UI-06 `test_points_checkbox_toggles`** (Exact) – The points-file check box is checked by one click and
  unchecked by the next.

### Choosing the image

* **UI-07 `test_pick_image`** (Exact) – `Vybrat obrázek` opens one file dialog titled `Vybrat obrázek`,
  starting in `img_input/` and offering `*.jpg` and `*.jpeg` files. After choosing `photo.jpg` the label
  reads `Vybraný obrázek: photo.jpg`.
* **UI-08 `test_long_file_name_is_shortened`** (Exact) – A file name longer than 20 characters is shown as its
  first 20 characters followed by `...`, so the narrow window stays readable.
* **UI-09 `test_cancel_keeps_previous_image`** (Exact) – Cancelling the dialog keeps the image chosen before;
  no message appears. The program still has the picture, not only the label: generating then works.
* **UI-10 `test_invalid_image_file`** (Exact; an empty file, a text file, a file that does not exist) – The error
  message (title `Chyba`) `Soubor <path> není validní obrázek.` appears, the label returns to
  `Vybraný obrázek: X`, and the previously chosen picture is forgotten: generating then reports a missing image.

### Missing choices

Clicking `> Generovat` with something missing shows one error message (title `Chyba`) and the window stays as it is.

* **UI-11 `test_missing_image`** (Exact) – No image: `Nebyl vybrán obrázek.`
* **UI-12 `test_missing_tessellation`** (Exact) – Without a tessellation the `> Generovat` button is not offered
  at all, so it cannot be clicked. (The program also has the message `Nebyla vybrána teselace.`, but the GUI
  never lets it appear.)
* **UI-13 `test_missing_distribution`** (Exact; Voronoi and both Delaunay variants) – Image and effect chosen,
  no distribution: `Nebylo vybráno rozdělení bodů.`
* **UI-14 `test_missing_effect`** (Exact; Voronoi, quadtree) – Everything except the effect: `Nebyl vybrán efekt.`
  For the quadtree this also shows that the missing distribution menu is not reported as an error.
* **UI-24 `test_changing_tessellation_forgets_choices`** (Exact; quadtree → Voronoi, Voronoi → Delaunay fast,
  Voronoi → quadtree) – Choosing another tessellation shows the distribution and effect menus with their
  prompts again, so the earlier choices are forgotten: generating then reports the missing distribution
  (or, for the quadtree, the missing effect) instead of running a combination the menus never offered, such
  as a Voronoi diagram from quadtree points or a quadtree with the paper effect.

### Generating

* **UI-15 `test_generate_without_points_file`** (Exact; Voronoi / Delaunay fast / quadtree with different
  effects) – After `> Generovat` the options are replaced by the progress view: `Generování obrázku...`,
  `Body byly vygenerovány.`, `Obrázek byl vygenerován!` and the button `> Zobrazit`. No message appears and no
  points file is written.
* **UI-16 `test_generate_with_points_file`** (Exact, Property) – With the check box checked, exactly one file
  `points_output/DD-MM-YYYY_HH-MM-SS.txt` is written and the progress view says
  `Vygenerované body uloženy do souboru:` followed by that path on the next line. The file has the format of
  FW-01, its point count matches its lines and all points lie inside the picture (x 1–119, y 1–82).

### Result window

* **UI-17 `test_result_window`** (Exact) – `> Zobrazit` opens the window `Vygenerovaný obrázek` (725×725) with
  a canvas and the buttons `Uložit obrázek` and `< Zpět`. The 120×83 result fits, so it is shown unscaled,
  centred on the 650×650 canvas (top-left corner at ((650−120)/2, (650−83)/2) rounded down). The window is
  modal: the main window cannot be used while it is open.
* **UI-18 `test_result_image_scaled_to_fit`** (Exact; 9 sizes) – A picture up to 630×630 is shown unscaled; a
  bigger one is scaled down so that its longer side is 630 and the other side keeps the aspect ratio, rounded
  down (1000×649 → 630×408, not 409); a square one becomes 630×630. It is always centred as in UI-17. The
  sizes include the limit (630) and one pixel over it, landscape and portrait. The inputs are simple
  two-colour JPEGs made by the test, so that big pictures are quick to generate.

### Saving

* **UI-19 `test_save_png`** (Exact, Property) – `Uložit obrázek` opens a save dialog titled `Uložit obrázek`,
  starting in `img_output/`, with default extension `.png` and only `*.png` files offered. After saving, the
  message (title `Success`) `Vygenerovaný obrázek uložen do souboru:` + new line + the path appears. The file
  is a PNG with transparency (RGBA) of the input's size; its fully opaque pixels are exactly the pixels shown
  in the result window, and it still resembles the input (mean colour difference below 40).
* **UI-20 `test_save_cancelled`** (Exact) – Cancelling the save dialog writes nothing, shows no message and
  keeps the result window open.
* **UI-21 `test_save_fails`** (Exact) – Saving into a folder that does not exist shows the error (title `Error`)
  `Nepodařilo se uložit obrázek.`; the result window stays open.

### Going back

* **UI-22 `test_back_resets_window`** (Exact; the `< Zpět` button, the window's close button) – The result
  window closes and the main window is exactly as after start (UI-01), with the check box unchecked. Nothing
  chosen before is remembered: choosing all menus again and generating reports a missing image.
* **UI-23 `test_generate_again_after_back`** (Exact) – After going back, a second picture (of another size)
  can be chosen and generated with other options, and the new result is shown. The points check box was
  checked for the first picture; after going back no points file is written, so the program itself (not
  only the check box) forgot that choice.
