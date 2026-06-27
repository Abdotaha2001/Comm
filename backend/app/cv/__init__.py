"""Computer-vision worker package.

`pipeline.analyze_video` runs a pluggable `BallDetector` over a video and derives
structured results (track -> rallies -> shots/events). The default detector is a
classical OpenCV baseline; deep models (TTNet/TrackNet/YOLO — MASTER_SPEC Part 26)
implement the same `BallDetector` interface and drop in for production accuracy.
"""
