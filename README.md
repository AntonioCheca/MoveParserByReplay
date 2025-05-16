# Move Parser By Replay

Project to get a list of interactions in a Street Fighter 6 game just from the Replay of it.

It assumes the replay comes with Frame Meter and Input Display on for both players, and for now, at 0.5x speed so the
Observers have more data

Frame data information to disambiguate moves in the Replay comes from the people at FAT Frame
Data https://github.com/D4RKONION/FAT

## Features

- Parse Street Fighter 6 replays with input display and frame meter
- Extract input sequences and character states
- Detect moves from replay video
- Outputs structured data for further analysis

## Installation (development)

First install this package with:

``pip install -e .``

And then you have to install the requirements.txt with:

``pip install -r requirements.txt``

You also need to copy paste the data images and font is inside the `data` folder.
You will need access to the images and templates if you want tests to pass and Observers to work properly.
However, for license and space reasons, I do not want to add these images in this repository.

## Tests

They are run with pytest, just doing

```
pytest
```

in the root folder should work.

## Use

Right now we do not have a main.py to run this, we still need the Manager and to standardise the output

## Roadmap

### Core features

- [X] Getting accurate list for Input Display from video
- [X] Getting Characters used from video
- [X] Getting basic list of Frame Meter States (not 100% accurate) from video
- [X] Getting basic list of normal moves from frame meter states
- [ ] Standardise output of Observers to contain timeframe of observations that can be shared between different
  Observers
- [ ] Define Manager that will call Observers, handling errors, outputs and order
- [ ] Define main.py that will call Manager
- [ ] Define validations on video (basic resolution)
- [ ] Use InputDisplay information in the Move In Frame observer to solve ambiguous Frame State sequences
- [ ] Extend moves recognised to cancels and jump-ins
- [ ] Fix issue with Frame Meter State not having the "number" information (this is important for 0 frame gaps, right
  now the program doesn't differentiate a 0-frame gap from a no-gap sequence)
- [ ] Improve accuracy of Frame Meter States from video
- [ ] Improve accuracy of Input Display from video
- [ ] Improve performance of Frame Meter States from video (bottleneck in the flow)
- [ ] Extend moves recognised for any non-static sequence of StateType
- [ ] Improve output to include what parts of the Observers had ambiguity problems, and between what options, for
  transparency and to know blind spots
- [ ] Pre-process the video to normalise resolution and scale if given in different resolution

### Cool-but-unclear features

- [ ] (Maybe hard) Design how to detect Option Selects as "moves"
- [ ] (Hard) Include a class that handles Inputs as the engine does, to improve accuracy when using Input Display to
  solve ambiguity for a move done
- [ ] (Hard) Think about how to get proper spacing information, and if it's possible to do it without Machine learning
  Pose-Estimation algorithm
- [ ] (Hard) Consider using Machine-Learning in the Frame State detection instead of doing estimations via colors
- [ ] (Very hard) Consider using Pose-Estimation Machine Learning instead of simple OpenCV (this would be able to be
  used in other Fighting Games Replays, not just SF6)

### Tech Debt

- [ ] Improve the Move class to standardise the way we give possible Frame Meter Sequences out of it to allow all
  possible moves in the game
- [ ] Improve the way we write the output of all Observers and include two modes, machine-friendly and human-readable
- [ ] Separate functional tests from normal unit tests for performance
- [ ] Standardise metrics of accuracy for each Observer with one full Functional Test that measures all of them (needs
  us to label manually a full match)
- [ ] Extend videos on Functional Tests to have one match for each character, to see blind spots in Moves not supported
  or not accurate yet
- [ ] Include batch-processing of videos instead of one-by-one

### Management

- [ ] Add a Github project to handle Issues that are currently being worked in
- [ ] Add Issues Templating for new bugs found
- [ ] Add a Contributing.md with details on Design requirements