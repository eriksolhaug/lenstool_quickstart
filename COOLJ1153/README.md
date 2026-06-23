# Lens Model for COOLJ1153
# -- Using Space-Based Data and Starting from Scratch

### 0. Calculate HST Zeropoint Using Headers

I've created a script that does this using the FITS header keywords. This script is called calc_HST_ZP.py.

E.g. run:

```bash
python ../lenstool_quickstart/calc_HST_ZP.py data/COOL-J1153+0755_F606W_0.03g0.6_crsc1.2_0.7crsn3.5_3.0_drc_sci.fits
```

| Filter | Zeropoint |
|--------|-----------|
| F475W  | 26.0393   |
| F606W  | 26.4831   |
| F814W  | 25.9317   |

Now, when running source extractor, the zero points need to be included into the .sex file in order to produce correct magnitudes.


### 1. Run Source Extractor

<!-- ```bash
python ../lenstool_quickstart/run_sextractor.py \
    --detection-image data/COOL-J1153+0755_F606W_0.03g0.6_crsc1.2_0.7crsn3.5_3.0_drc_sci.fits \
    --measure-image data/COOL-J1153+0755_F814W_0.03g0.6_crsc1.2_0.7crsn3.5_3.0_drc_sci.fits \
    --config config/coolj1153_default.sex \
    --output catalogs/coolj1153_sources.cat
``` -->

Using the default Source Extractor call in `dual image` mode.

```bash
    sex Image1 [Image2] -c configuration-file [-Parameter1 Value1 -Parameter2 Value2 ...]
```

With **F814W** as the detection image, following the convention from Gladders & Yee, 2000 of using producing a CMD (color-magnitude diagram) with the reddest filter for magnitude and both filters for color.

```bash
    mkdir catalogs
    sex data/COOL-J1153+0755_F814W_0.03g0.6_crsc1.2_0.7crsn3.5_3.0_drc_sci.fits data/COOL-J1153+0755_F606W_0.03g0.6_crsc1.2_0.7crsn3.5_3.0_drc_sci.fits -c config/coolj1153_default.sex # Set the zero point in the .sex file!
    mv catalogs/coolj1153_sources.cat catalogs/coolj1153_sources_f606w.cat
    sex data/COOL-J1153+0755_F814W_0.03g0.6_crsc1.2_0.7crsn3.5_3.0_drc_sci.fits data/COOL-J1153+0755_F814W_0.03g0.6_crsc1.2_0.7crsn3.5_3.0_drc_sci.fits -c config/coolj1153_default.sex # Set the zero point in the .sex file!
    mv catalogs/coolj1153_sources.cat catalogs/coolj1153_sources_f814w.cat
```

### 2. Visualize Detections

```bash
python ../lenstool_quickstart/visualize_detections.py \
    --image data/COOL-J1153+0755_F814W_0.03g0.6_crsc1.2_0.7crsn3.5_3.0_drc_sci.fits \
    --catalog catalogs/coolj1153_sources_f814w.cat \
    --output plots/detections.png
```

### 3. Make Color-Magnitude Diagram

We need to select a threshold for what defines a star vs. a galaxy. This is the classic star-galaxy separation. Source Extractor has a built-in CLASS_STAR keyword functionality that produces a number that corresponds to the stellarity (how star-like is it?) of an object.

```bash
python ../lenstool_quickstart/plot_cmd.py \
    --band1-catalog catalogs/coolj1153_sources_f814w.cat \
    --band2-catalog catalogs/coolj1153_sources_f606w.cat \
    --output plots/color_magnitude_diagram.png \
    --class-star-threshold 0.95
```

### 4. Create DS9 Region File

```bash
python ../lenstool_quickstart/star_galaxy_regions.py \
    --band1-catalog catalogs/coolj1153_sources_f606w.cat \
    --band2-catalog catalogs/coolj1153_sources_f814w.cat \
    --output regions/stars_galaxies.reg \
    --class-star-threshold 0.95
```

Opens in DS9 with cyan circles for galaxies and red circles for stars.

### 5. Filter Objects

Edit the `## FILTER` section in the script to set your filtering parameters:

```bash
python ../lenstool_quickstart/filter_objects.py
```

This applies cuts to:
- CLASS_STAR (selects galaxies)
- Magnitude range
- Color range (using both bands)

Outputs `catalogs/coolj1153_filtered.cat`

### 6. Create Region File for Filtered Objects

```bash
python ../lenstool_quickstart/filtered_regions.py \
    --catalog catalogs/coolj1153_filtered.cat \
    --output regions/filtered_objects.reg \
    --radius 1.0
```

Creates DS9 region file with orange circles for all filtered objects.

Outputs `regions/filtered_objects.reg`

### 7. Create Lenstool Catalog

```bash
python ../lenstool_quickstart/make_catalog.py
```

Formats the filtered catalog for lenstool input. Edit the script's `## INPUT/OUTPUT` section to change paths or pixel scale if needed.

Outputs `catalogs/coolj1153_lenstool.cat`


### 8. Build Lenstool Input File

Use `coolj1153_lenstool.cat` as input galaxy catalog for lens model.

```bash
    mkdir -p lenstool/cats
    cp catalogs/coolj1153_lenstool.cat lenstool/cats/.
```

I use the reference coordinate (178.3302680, 7.9325130) which is outputed from Source Extractor for the BCG.

I use outputed Source Extractor coordinates for the arcs/coolj1153.dat file (astrometric input positions/constraints).


Activate conda environment for lenstool v8. I have this installed in `lenstool_env8`.

```bash
    cd lenstool
    conda activate lenstool_env8
    lenstool input.par -n
```

#### v1.1

I start by adding one halo - **potentiel O1** - that is placed on the BCG. Parameters (except positions) are free to vary.

I add the potfile0 using the Source Extractor catalog with the same scaling relations as in Solhaug et al. 2026.

For constraints, I'm using the three brightest images of COOLJ1153A and COOLJ1153B, and the centroid coordinate of the "blue arc" (see Solhaug et al. 2026) outputted from Source Extractor.

#### v1.2

I add **potentiel O2** at the location of the spiral that is at a different redshift [z = REDSHIFT FROM KCWI] than the primary cluster. I fix the position to 178.3303810, 7.9366250 from Source Extractor and use Source Extractor's PA=180-47.96=132.04.

I free potentiel O1's position to vary within a box of 10"x10" around the BCG position.

```bash
    potential O1
        profile       81
        x_centre     0.000000
        y_centre     0.000000
        ellipticity     0.404285
        angle_pos       123.190410
        core_radius_kpc     63.122232
        cut_radius_kpc     1500.000000
        v_disp     981.783599
        z_lens     0.4301
        end

    potfile0
        filein  3 cats/coolj1153_lenstool.cat
        zlens   0.430100
        type    81
        corekpc 0.150000
        mag0    19.530000
        sigma   3 115.176558 4.361758
        cutkpc  3 39.857883 38.878750
        slope   0 4.000000 0.000000
        vdslope 0 4.000000 0.000000
        vdscatter 0 0.000000 0.000000
        rcutscatter 0 0.000000 0.000000
        end
```

**Note:** the catalog was not pushed for this and was later altered in v1.3 to include the correct recalculated zeropoints for the HST images. In previous versions, the zeropoints for each image adopted a zeropoint close to the correct values but not correct (within <2 AB mag). The `coolj1153_lenstool.cat` catalog for v1.1 and v1.2 are therefore lost. The output files for this version reflect the outputs using the former catalog.

#### v1.3

Updated the HST zeropoints to be correct by using the custom script calc_HST_ZP.py.

#### Suggestions:

* Try adding the fourth images of the quasars.