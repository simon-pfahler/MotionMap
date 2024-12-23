# MotionMap - Generate clean posters of your activities

This project will generate clean images of the streets you ran or cycled, where it maps the GPS data onto real streets to get a cleaned up result without a bunch of overlapping lines.

It is currently a work in progress.

## To do
- [x] `track` object to read in gpx files and allow for basic operations on them
- [x] debugging function to plot a track
- [x] function to load street data for a particular area
- [x] function to plot street data
- [ ] function to map a `track` onto street data
    - [x] function to calculate minimal distance between nodes
    - [x] function to calculate likelihood of edge-point pair
    - [x] function to get probabilities of edges being first edge
    - [ ] clean up street network so there are no duplicate edges or nodes on top of each other
    - [ ] step along in the progression
- [ ] function to import all tracks from garmin export
